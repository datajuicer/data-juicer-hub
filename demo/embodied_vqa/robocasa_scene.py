"""Build scene IR and 720p videos from recorded MuJoCo states."""

import gzip
import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from data_juicer.utils.lazy_loader import LazyLoader

from .runtime import write_json

cv2 = LazyLoader("cv2")
mujoco = LazyLoader("mujoco")
np = LazyLoader("numpy")
Image = LazyLoader("PIL.Image", "Pillow")

WIDTH, HEIGHT = 1280, 720
VIEWS = ["robot0_agentview_left", "robot0_agentview_right"]


def load_model(raw, episode):
    meta = json.loads((raw / f"extras/{episode}/ep_meta.json").read_text())
    root = ET.fromstring(gzip.decompress((raw / f"extras/{episode}/model.xml.gz").read_bytes()))
    suite = Path(importlib.util.find_spec("robosuite").origin).parent / "models/assets"
    for e in root.iter():
        file = e.get("file")
        if not file:
            continue
        if "robocasa/models/assets/" in file:
            path = raw / "assets" / file.split("robocasa/models/assets/")[1]
        elif "robosuite/models/assets/" in file:
            path = suite / file.split("robosuite/models/assets/")[1]
        else:
            raise ValueError("Unrecognized asset path: " + file)
        if not path.is_file():
            raise FileNotFoundError(path)
        e.set("file", str(path.resolve()))
    for name in VIEWS:
        cfg = meta["cam_configs"][name]
        parent = next(e for e in root.iter("body") if e.get("name") == cfg["parent_body"])
        ET.SubElement(
            parent,
            "camera",
            name=name,
            pos=" ".join(map(str, cfg["pos"])),
            quat=" ".join(map(str, cfg["quat"])),
            **cfg.get("camera_attribs", {}),
        )
    visual = root.find("visual")
    if visual is None:
        visual = ET.SubElement(root, "visual")
    glob = visual.find("global")
    if glob is None:
        glob = ET.SubElement(visual, "global")
    glob.set("offwidth", str(WIDTH))
    glob.set("offheight", str(HEIGHT))
    return mujoco.MjModel.from_xml_string(ET.tostring(root, encoding="unicode")), meta


def project(model, data, camera, world):
    c = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, camera)
    local = data.cam_xmat[c].reshape(3, 3).T @ (np.asarray(world) - data.cam_xpos[c])
    if local[2] >= 0:
        return None
    f = HEIGHT / 2 / np.tan(np.deg2rad(model.cam_fovy[c]) / 2)
    return [
        round((WIDTH / 2 + f * local[0] / -local[2]) / WIDTH * 1000, 3),
        round((HEIGHT / 2 - f * local[1] / -local[2]) / HEIGHT * 1000, 3),
    ]


def restore_state(model, data, state):
    data.time = state[0]
    data.qpos[:] = state[1 : 1 + model.nq]
    data.qvel[:] = state[1 + model.nq : 1 + model.nq + model.nv]
    if model.na:
        data.act[:] = state[-model.na :]
    mujoco.mj_forward(model, data)


def collect_state_ir(model, data, states, meta):
    body_ids = {
        c["name"]: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, c["name"] + "_main") for c in meta["object_cfgs"]
    }

    def descendants(b):
        ids = {b}
        for i in range(model.nbody):
            if int(model.body_parentid[i]) in ids:
                ids.add(i)
        return ids

    object_bodies = {name: descendants(body) for name, body in body_ids.items()}
    geoms = {
        k: {i for i in range(model.ngeom) if int(model.geom_bodyid[i]) in object_bodies[k]} for k, b in body_ids.items()
    }
    names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, i) or "" for i in range(model.ngeom)]
    fingers = [{i for i, n in enumerate(names) if f"finger{j}" in n and "collision" in n} for j in (1, 2)]
    site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "gripper0_right_grip_site")
    rows = []
    for i, state in enumerate(states):
        restore_state(model, data, state)
        contacts = []
        held = [False, False]
        placed = False
        for con in data.contact[: data.ncon]:
            if con.dist > 0:
                continue
            pair = {int(con.geom1), int(con.geom2)}
            if pair & geoms["obj"]:
                contacts.append(
                    {
                        "geoms": [names[int(con.geom1)], names[int(con.geom2)]],
                        "position": con.pos.tolist(),
                        "distance": float(con.dist),
                    }
                )
                for j in (0, 1):
                    held[j] |= bool(pair & fingers[j])
                placed |= bool(pair & geoms["container"])
        rows.append(
            {
                "index": i,
                "time": float(data.time),
                "objects": {k: data.xpos[b].tolist() for k, b in body_ids.items()},
                "eef": data.site_xpos[site].tolist(),
                "contacts": contacts,
                "contact_2d": {
                    v: [
                        project(model, data, v, c["position"])
                        for c in contacts
                        if any("finger" in n for n in c["geoms"])
                    ]
                    for v in VIEWS
                },
                "finger_contact": held,
                "secure_grasp": all(held),
                "placed_contact": bool(placed),
                "released_in_destination": bool(placed and not any(held)),
                "eef_2d": {v: project(model, data, v, data.site_xpos[site]) for v in VIEWS},
            }
        )
    return rows, geoms


def select_frames(rows):
    touch = [r["index"] for r in rows if any(r["finger_contact"])]
    grasp = [r["index"] for r in rows if r["secure_grasp"]]
    placed = [r["index"] for r in rows if r["released_in_destination"]]
    if not touch or not grasp or not placed:
        raise ValueError("Episode lacks demonstrated grasp/placement evidence")
    anchors = {
        "initial": 0,
        "contact": touch[0],
        "grasp": grasp[len(grasp) // 2],
        "placed": placed[-1],
        "final": len(rows) - 1,
    }
    selected = sorted(set(np.linspace(0, len(rows) - 1, 12).astype(int).tolist() + list(anchors.values())))
    return anchors, selected


def visible_instances(segmentation, depth, geoms):
    visible = {}
    for k, ids in geoms.items():
        mask = np.isin(segmentation[:, :, 0], list(ids)) & (segmentation[:, :, 1] == int(mujoco.mjtObj.mjOBJ_GEOM))
        yy, xx = np.where(mask)
        if not len(xx):
            continue
        center = np.array([xx.mean(), yy.mean()])
        j = int(np.argmin((xx - center[0]) ** 2 + (yy - center[1]) ** 2))
        visible[k] = {
            "pixels": len(xx),
            "bbox_xyxy": [
                int(xx.min()),
                int(yy.min()),
                int(xx.max() + 1),
                int(yy.max() + 1),
            ],
            "point_2d": [
                round(xx[j] / WIDTH * 1000),
                round(yy[j] / HEIGHT * 1000),
            ],
            "median_depth_m": float(np.median(depth[mask])),
        }
    return visible


def render_episode(model, data, states, rows, geoms, selected, output):
    option = mujoco.MjvOption()
    option.geomgroup[0] = 0
    option.sitegroup[:] = 0
    renderer = mujoco.Renderer(model, HEIGHT, WIDTH)
    videos = {
        v: cv2.VideoWriter(
            str(output / (v + ".mp4")),
            cv2.VideoWriter_fourcc(*"mp4v"),
            20,
            (WIDTH, HEIGHT),
        )
        for v in VIEWS
    }
    try:
        if not all(w.isOpened() for w in videos.values()):
            raise RuntimeError("Cannot open video encoder")
        for i, state in enumerate(states):
            restore_state(model, data, state)
            if i in selected:
                rows[i]["views"] = {}
            for v in VIEWS:
                renderer.update_scene(data, camera=v, scene_option=option)
                rgb = renderer.render()
                videos[v].write(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
                if i not in selected:
                    continue
                path = Path("frames") / v / f"{i:06d}.jpg"
                (output / path).parent.mkdir(parents=True, exist_ok=True)
                Image.fromarray(rgb).save(output / path, quality=95)
                renderer.enable_segmentation_rendering()
                seg = renderer.render()
                renderer.disable_segmentation_rendering()
                renderer.enable_depth_rendering()
                depth = renderer.render()
                renderer.disable_depth_rendering()
                depths = Path("ir/depth") / v / f"{i:06d}.npz"
                (output / depths).parent.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(output / depths, depth_m=depth)
                visible = visible_instances(seg, depth, geoms)
                rows[i]["views"][v] = {
                    "image": str(path),
                    "objects": visible,
                    "depth": str(depths),
                }
            if i % 30 == 0:
                print(f"Rendered {i + 1}/{len(states)} states at 1280x720", flush=True)
    finally:
        for writer in videos.values():
            writer.release()
        renderer.close()


def extract_scene_ir(raw, output, episode):
    model, meta = load_model(raw, episode)
    data = mujoco.MjData(model)
    with np.load(raw / f"extras/{episode}/states.npz") as archive:
        states = archive["states"]
    expected = 1 + model.nq + model.nv + model.na
    if states.shape[1] != expected:
        raise ValueError(f"State layout mismatch {states.shape[1]} != {expected}")
    output.mkdir(parents=True, exist_ok=True)
    rows, geoms = collect_state_ir(model, data, states, meta)
    anchors, selected = select_frames(rows)
    render_episode(model, data, states, rows, geoms, selected, output)
    from .robocasa_rules import recorded_task

    source_manifest = json.loads((raw / "download_manifest.json").read_text())
    ir = {
        "episode_id": episode,
        "instruction": meta["lang"],
        "task": recorded_task(source_manifest),
        "objects": {c["name"]: c["info"]["cat"] for c in meta["object_cfgs"]},
        "resolution": [WIDTH, HEIGHT],
        "views": VIEWS,
        "anchors": anchors,
        "sampled_indices": selected,
        "states": rows,
        "success_criterion": "object-to-container physical contact and no finger contact (demonstrated placement; not a call to environment._check_success)",
        "operators": [
            "raw_state_replay",
            "camera_calibration",
            "instance_segmentation",
            "visible_point_and_bbox",
            "depth",
            "eef_trajectory",
            "physical_contact",
            "bilateral_finger_grasp",
            "placement_contact",
            "temporal_phase",
            "synchronized_views",
        ],
        "source_manifest": source_manifest,
    }
    write_json(output / "ir/episode_ir.json", ir)
    print("IR ready", anchors, flush=True)
