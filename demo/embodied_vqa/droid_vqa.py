"""Construct DROID family VQA from object, gripper, and camera IR."""

import hashlib
import json
import math
from pathlib import Path

from data_juicer.utils.robot_utils import (
    intersection,
    normalized_center,
    overlap_ratio,
)

from .semantic_labels import SemanticAnnotator
from .task_ir import point_target, target_item
from .vqa_templates import POINT_OUTPUT

OBJECT = [
    "object_reference",
    "PIO|S1 referred-object localization|bbox",
    "PIO|S1 referred-object localization|point",
    "RoboRefIt|referring-expression grounding|bbox",
    "RoboRefIt|referring-expression grounding|point",
]
DESTINATION = [
    "PIO|S2 task-driven pointing|point",
    "PointBench|reasoning|point",
    "RoboSpatial-Home|configuration|bbox",
    "VABench-Point|destination spatial affordance|point",
    "destination_point",
]
CONTACT = [
    "PartAfford|demonstrated contact affordance|point",
    "PointBench|affordable|point",
    "RoboAfford|object affordance recognition|point",
    "demonstrated_contact_affordance",
]
TRAJECTORY = [
    "continuous_trajectory_eval_format/sharerobot_trajectory_variable_point_format",
    "continuous_trajectory_eval_format/vabench_visual_trace_8point_format",
]


def choice_spec(answer, labels):
    return {"type": "choice", "correct_label": answer, "labels": labels}


def point(row, episode, family, image, question, xy, source, root):
    row.append(
        record(
            episode,
            family,
            [image],
            question + " " + POINT_OUTPUT,
            point_target(xy),
            source,
            root,
        )
    )


def ordered_options(episode, family, options):
    """Order choices reproducibly without using the correct answer."""
    return sorted(
        options,
        key=lambda text: hashlib.sha256((episode + "\0" + family + "\0" + text).encode()).digest(),
    )


def choice(row, episode, family, images, question, options, correct, source, root):
    options = ordered_options(episode, family, options)
    labels = [chr(65 + i) for i in range(len(options))]
    answer = labels[options.index(correct)]
    text = question + "\n" + "\n".join(f"({label}) {option}" for label, option in zip(labels, options))
    text += "\nAnswer with the option letter."
    row.append(record(episode, family, images, text, choice_spec(answer, labels), source, root))


def model_choice(rows, episode, family, images, question, options, root, annotator):
    options = ordered_options(episode, family, options)
    correct, evidence = annotator.choose(family, images, question, options)
    choice(
        rows,
        episode,
        family,
        images,
        question,
        options,
        correct,
        "VLM visual semantic annotation",
        root,
    )
    rows[-1]["metadata"]["generation"] = evidence


def resample(points, n):
    if len(points) < 2:
        raise ValueError("Trajectory needs at least two gripper positions")
    out = []
    for j in range(n):
        t = j * (len(points) - 1) / (n - 1)
        i = min(int(t), len(points) - 2)
        a = t - i
        out.append([round((1 - a) * points[i][d] + a * points[i + 1][d], 2) for d in (0, 1)])
    return out


def build_targets(root, model=None, endpoint=None):
    annotator = SemanticAnnotator(root, model, endpoint)
    ir = json.loads((root / "ir" / "episode_ir.json").read_text())
    episode, instruction = ir["episode_id"], ir["instruction"]
    views = ir["sampled_views"]
    primary = ir["primary_view"]
    other = ir["geometry"]["secondary_view"]
    images = views[primary]["images"]
    second_images = views[other]["images"]
    size = views[primary]["image_size"]
    object_json = json.loads(Path(ir["object_operator_outputs"][0]).read_text())
    object_track = json.loads(Path(ir["object_operator_outputs"][1]).read_text())
    gripper_json = json.loads(Path(ir["gripper_operator_output"]).read_text())
    target = object_json["vlm_target_object"]["target_object"]
    visible_point = [round(x) for x in object_json["vlm_pointing"]["point_1000"]]
    objects = {int(f["frame_index"]): f["bbox_xyxy"] for f in object_track["frames"] if f.get("bbox_xyxy")}
    grippers = {int(f["frame_index"]): f["bbox_xyxy"] for f in gripper_json["tracking"]["frames"] if f.get("bbox_xyxy")}
    joint = sorted(set(objects) & set(grippers) & set(range(len(images))))
    if len(joint) < 3:
        raise ValueError("Need at least three jointly tracked sampled frames")
    contact_i = max(joint, key=lambda i: overlap_ratio(objects[i], grippers[i]))
    contact_overlap = overlap_ratio(objects[contact_i], grippers[contact_i])
    if contact_overlap < 0.05:
        raise ValueError("No geometric contact frame; cannot compile contact families")
    contact_box = intersection(objects[contact_i], grippers[contact_i])
    contact_point = normalized_center(contact_box, size["width"], size["height"])
    first_i, last_i = joint[0], joint[-1]
    final_grounding = ir["geometry"]["final_target_grounding"]
    destination = final_grounding["point"]
    gripper_points = [normalized_center(grippers[i], size["width"], size["height"]) for i in joint]
    rows = []

    object_questions = {
        "object_reference": f'For "{instruction}", point to the visible task-relevant {target}.',
        "PIO|S1 referred-object localization|bbox": f"Locate the visible {target} referred to by the instruction.",
        "PIO|S1 referred-object localization|point": f"Point to the {target} the robot should manipulate.",
        "RoboRefIt|referring-expression grounding|bbox": f'Locate the visible object described as "{target}".',
        "RoboRefIt|referring-expression grounding|point": f'Point to the object referred to by "{target}" in this image.',
    }
    for family in OBJECT:
        point(
            rows,
            episode,
            family,
            images[first_i],
            object_questions[family],
            visible_point,
            "fresh VLM pointing + SAM3 target localization",
            root,
        )
    destination_questions = {
        "PIO|S2 task-driven pointing|point": f'For "{instruction}", point to the final demonstrated destination of the {target}.',
        "PointBench|reasoning|point": f'Where did the {target} end up after "{instruction}"? Point to its final location.',
        "RoboSpatial-Home|configuration|bbox": f"Locate the {target} in the final demonstrated configuration.",
        "VABench-Point|destination spatial affordance|point": f"Point to the region occupied by the {target} after the demonstrated placement.",
        "destination_point": f"Point to the demonstrated final location of the {target}.",
    }
    for family in DESTINATION:
        point(
            rows,
            episode,
            family,
            final_grounding["image"],
            destination_questions[family],
            destination,
            "VLM relocalization in final multi-view images",
            root,
        )
        rows[-1]["metadata"]["generation"]["grounding_trace"] = final_grounding["model_trace"]
    contact_questions = {
        "PartAfford|demonstrated contact affordance|point": f"Point to the region of the {target} intersecting the gripper in this demonstration.",
        "PointBench|affordable|point": f"Locate the demonstrated interaction region used by the gripper on the {target}.",
        "RoboAfford|object affordance recognition|point": f"Point to the demonstrated gripper contact region on the {target}.",
        "demonstrated_contact_affordance": f"Point to the demonstrated gripper interaction with the {target}.",
        "relational_contact_placement": f"Locate the overlap between the visible gripper and the {target}.",
    }
    for family in CONTACT + ["relational_contact_placement"]:
        point(
            rows,
            episode,
            family,
            images[contact_i],
            contact_questions[family],
            contact_point,
            "object/gripper overlap center",
            root,
        )

    choice(
        rows,
        episode,
        "ContactDecide",
        [images[contact_i]],
        f'For "{instruction}", is the gripper visibly contacting the {target}?',
        ["No", "Yes"],
        "Yes" if contact_overlap >= 0.05 else "No",
        f"tracked box overlap={contact_overlap:.3f}",
        root,
    )
    ox, oy = normalized_center(objects[first_i], size["width"], size["height"])
    gx, gy = normalized_center(grippers[first_i], size["width"], size["height"])
    if overlap_ratio(objects[first_i], grippers[first_i]) >= 0.05:
        location = "overlapping the gripper"
    elif abs(ox - gx) >= abs(oy - gy):
        location = "right of the gripper" if ox > gx else "left of the gripper"
    else:
        location = "below the gripper" if oy > gy else "above the gripper"
    choice(
        rows,
        episode,
        "configuration",
        [images[first_i]],
        "Which target/gripper configuration is shown?",
        [
            "left of the gripper",
            "right of the gripper",
            "above the gripper",
            "below the gripper",
            "overlapping the gripper",
        ],
        location,
        "tracked object/gripper box centers",
        root,
    )

    early_i = min((i for i in joint if i < contact_i), default=first_i)
    model_choice(
        rows,
        episode,
        "Q3_secure_grasp_status",
        [images[early_i]],
        f"Is the gripper visibly holding the {target} securely in this observation?",
        ["No", "Yes"],
        root,
        annotator,
    )
    model_choice(
        rows,
        episode,
        "Q4_task_completion_status",
        [images[early_i]],
        f'Based on this observation, has the task "{instruction}" been completed?',
        ["No", "Yes"],
        root,
        annotator,
    )
    model_choice(
        rows,
        episode,
        "Success_Task",
        [images[first_i], images[last_i], final_grounding["image"]],
        f'Based on the first observation and two synchronized final views, was "{instruction}" completed successfully?',
        ["No", "Yes"],
        root,
        annotator,
    )

    actions = [
        "establish contact with the task-relevant object",
        "securely engage the task-relevant object",
        "move the task-relevant object toward the instructed goal",
        "release the object and inspect the result",
    ]
    planning_questions = {
        "future_prediction": f'For "{instruction}", which next action is predicted after these early observations?',
        "immediate_planning": f'Given the visible early execution of "{instruction}", what should the robot do next?',
        "immediate_planning_with_context": f'Using these ordered context frames of "{instruction}", select the next task-relevant action.',
    }
    for family, count in (
        ("future_prediction", 2),
        ("immediate_planning", 2),
        ("immediate_planning_with_context", 3),
    ):
        context = [images[i] for i in joint[:count]]
        model_choice(
            rows,
            episode,
            family,
            context,
            planning_questions[family],
            actions,
            root,
            annotator,
        )

    consequences = [
        f"the robot moved the {target} away from its initial position",
        "the robot left every object unchanged",
        "the robot navigated to another room",
        "the robot opened an unrelated appliance",
    ]
    model_choice(
        rows,
        episode,
        "action_consequence",
        [images[first_i], images[last_i], final_grounding["image"]],
        "Which task-relevant change best describes this demonstration?",
        consequences,
        root,
        annotator,
    )

    distractors = ["Open a drawer", "Turn on a faucet", "Move to another room"]
    instructions = [
        instruction,
        *[x for x in distractors if x.casefold() != instruction.casefold()],
    ]
    instructions = instructions[:4]
    model_choice(
        rows,
        episode,
        "multi_view_reasoning",
        [images[contact_i], second_images[contact_i]],
        "These synchronized camera views show which task?",
        instructions,
        root,
        annotator,
    )
    choice(
        rows,
        episode,
        "multi_view_task_consistency",
        [images[contact_i], second_images[contact_i]],
        "Do these synchronized camera views come from the same task episode?",
        ["No", "Yes"],
        (
            "Yes"
            if primary != other
            and views[primary]["frame_indices"][contact_i] == views[other]["frame_indices"][contact_i]
            else "No"
        ),
        "shared raw episode and source frame index",
        root,
    )
    model_choice(
        rows,
        episode,
        "multi_view_phase_consistency",
        [images[contact_i], second_images[contact_i]],
        f'For "{instruction}", which phase explains both synchronized views?',
        [
            "approaching the object before contact",
            "establishing contact or grasping",
            "transporting the held object",
            "releasing or withdrawing after placement",
        ],
        root,
        annotator,
    )

    trajectory_inputs = [joint[round(j * (len(joint) - 1) / 3)] for j in range(4)]
    for family, n in zip(TRAJECTORY, (10, 8)):
        trajectory = resample(gripper_points, n)
        motion = sum(math.dist(a, b) for a, b in zip(trajectory, trajectory[1:]))
        spec = {
            "type": "traj2d",
            "traj": trajectory,
            "key": "point_2d",
            "n_points": n,
            "gt_motion": round(motion, 2),
        }
        rows.append(
            record(
                episode,
                family,
                [images[i] for i in trajectory_inputs],
                f'Trace the demonstrated gripper motion for "{instruction}" with {n} '
                "normalized 2D points in [0,1000] in chronological order. Trace the robotic arm end-effector, not the manipulated object. "
                'Return only a JSON array in exactly this format: [{"point_2d":[x,y]}]. '
                "Do not add labels, bounding boxes, z coordinates, or extra JSON fields.",
                spec,
                "interpolated tracked gripper centers",
                root,
            )
        )

        rows[-1]["metadata"]["evidence"] = {
            "operator": "gripper_track_centers",
            "sample_indices": joint,
            "input_sample_indices": trajectory_inputs,
            "source_frame_indices": [views[primary]["frame_indices"][i] for i in joint],
            "source_fps": views[primary]["source_fps"],
            "n_points": n,
            "interpolation": "linear over ordered sampled gripper centers",
            "horizon": "observed sampled clip",
            "exclude_current": False,
        }

    return rows


def record(episode, family, images, question, spec, source, output):
    rel_images = [str(Path(p).relative_to(output)) for p in images]
    return target_item(
        f"{episode}__{family}",
        rel_images,
        question,
        spec,
        {
            "episode_id": episode,
            "family": family,
            "source_dataset": "DROID",
            "label_source": source,
            "demo_source": "raw episode and executed IR operators",
            "build_version": "episode-demo-v4",
            "generation": {"generator": "scripted_from_model_ir", "rule": source},
        },
    )
