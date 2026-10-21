"""Construct RoboCasa VQA prompts and typed targets from episode IR."""

import hashlib
import json
import math
import random

from .robocasa_rules import (
    absent_class,
    phase,
    remaining_plan,
    task_roles,
)
from .task_ir import point_target, target_item
from .vqa_templates import (
    POINT_OUTPUT,
    presence_question,
    short_trajectory,
    trajectory_question,
)


def build_targets(root):
    ir = json.loads((root / "ir/episode_ir.json").read_text())
    rows = []
    states = ir["states"]
    other, view = ir["views"]
    anchors = ir["anchors"]
    target, source, destination = [ir["objects"][k] for k in ("obj", "obj_container", "container")]
    instruction = ir["instruction"]
    target, source, destination = task_roles(instruction, ir["objects"])

    def best_view(i):
        return max(
            ir["views"],
            key=lambda v: states[i]["views"][v]["objects"].get("obj", {}).get("pixels", 0),
        )

    def frame_image(i, v=None):
        return states[i]["views"][v or best_view(i)]["image"]

    def visible_point(i, obj="obj", v=None):
        v = v or best_view(i)
        instance = states[i]["views"][v]["objects"].get(obj)
        if not instance or instance["pixels"] < 100:
            raise ValueError(f"Insufficient visible evidence: frame {i}, {obj}, {v}")
        return instance["point_2d"]

    def add_record(family, images, question, spec, evidence):
        rows.append(
            target_item(
                ir["episode_id"] + "__" + family,
                images,
                question,
                spec,
                {
                    "family": family,
                    "episode_id": ir["episode_id"],
                    "source_dataset": "RoboCasa",
                    "label_source": "raw simulation state and rendered instance/depth IR",
                    "build_version": "1",
                    "generation": {
                        "generator": "scripted",
                        "rule": evidence["operator"],
                    },
                    "evidence": evidence,
                },
            )
        )

    def add_point(family, i, question, obj="obj", coordinates=None, evidence=None):
        coordinates = visible_point(i, obj) if coordinates is None else coordinates
        if not all(0 <= a <= 1000 for a in coordinates):
            raise ValueError(f"Offscreen point {family}: {coordinates}")
        add_record(
            family,
            [frame_image(i)],
            question + " " + POINT_OUTPUT,
            point_target(coordinates),
            evidence
            or {
                "operator": "visible_instance_point",
                "frame": i,
                "object": obj,
                "view": best_view(i),
            },
        )

    def add_choice(family, indices, question, options, correct, evidence, views=None):
        options = list(options)
        seed = hashlib.sha256((ir["episode_id"] + family).encode()).digest()
        random.Random(int.from_bytes(seed, "big")).shuffle(options)
        labels = [chr(65 + j) for j in range(len(options))]
        answer = labels[options.index(correct)]
        images = [frame_image(i, v) for i, v in zip(indices, views or [best_view(i) for i in indices])]
        add_record(
            family,
            images,
            question
            + "\n"
            + "\n".join(f"({label}) {option}" for label, option in zip(labels, options))
            + "\nAnswer with the option letter.",
            {"type": "choice", "correct_label": answer, "labels": labels},
            evidence,
        )

    first = anchors["initial"]
    last = anchors["final"]
    grasp = max(
        (i for i in ir["sampled_indices"] if states[i]["secure_grasp"]),
        key=lambda i: min(states[i]["views"][v]["objects"].get("obj", {}).get("pixels", 0) for v in ir["views"]),
    )
    for v in ir["views"]:
        visible_point(grasp, v=v)
    contact = anchors["contact"]
    placed = anchors["placed"]
    # These prompts refer to the same visible object.
    objects = {
        "object_reference": f"Point to the visible {target}.",
        "PIO|S1 referred-object localization|bbox": f"Point to the {target} on the {source}.",
        "PIO|S1 referred-object localization|point": f"Point to the {target} that must be picked up.",
        "RoboRefIt|referring-expression grounding|bbox": f"Point to the food resting on the {source} that must go into the {destination}.",
        "RoboRefIt|referring-expression grounding|point": f'Point to the object described by "the {target} on the {source}".',
        "PixMo-Points|present-instance pointing|bbox": f"Point to the visible {target}, one point per instance.",
        "PixMo-Points|present-instance pointing|point": f"Locate the single visible {target}.",
        "PointBench|steerable|point": f"Ignore the {destination}; point to the {target} on the {source}.",
        "PointBench|reasoning|point": f'Which object must move to satisfy "{instruction}"? Point to it.',
    }
    for family, question in objects.items():
        add_point(family, first, question)
    a, b = visible_point(first), visible_point(first, "container")
    relation = (
        ("left of" if a[0] < b[0] else "right of")
        if abs(a[0] - b[0]) > abs(a[1] - b[1])
        else ("above" if a[1] < b[1] else "below")
    )
    for family in ("PointBench|spatial|bbox", "PointBench|spatial|point"):
        add_point(
            family,
            first,
            (
                f"Locate the {target} that appears {relation} the {destination}."
                if family.endswith("|bbox")
                else f"Point to the {target} positioned {relation} the {destination} in this image."
            ),
        )
    add_point(
        "RefSpatial-Bench|location|point",
        first,
        f"Point to the food that starts on the {source} and is {relation} the {destination} in this image.",
    )
    for family, question in {
        "PIO|S2 task-driven pointing|point": f'For "{instruction}", point to the destination receptacle.',
        "VABench-Point|destination spatial affordance|point": f"Point to the receptacle where the {target} should be placed.",
        "destination_point": f"{instruction} Identify the final destination region where the object should be placed. Do not mark the source object.",
        "RoboAfford|spatial affordance localization|point": f"Point to the receiving receptacle for the {target}.",
        "RefSpatial-Bench|placement|point": f"Point to the {destination}, the placement destination for the {target}.",
    }.items():
        add_point(family, first, question, obj="container")
    # Project the recorded finger-object contact into the selected camera.
    contacts = states[contact]["contacts"]
    physical = [c for c in contacts if any("finger" in n for n in c["geoms"])]
    if not physical:
        raise ValueError("Missing physical finger contact")
    coordinates = states[contact]["contact_2d"][best_view(contact)][0]
    contact_questions = {
        "PartAfford|demonstrated contact affordance|point": f"Point to the demonstrated finger contact region used to grasp the {target}.",
        "PointBench|affordable|point": f"Locate the region of the {target} used for the demonstrated grasp.",
        "RoboAfford|object affordance recognition|point": f"Where do the fingers interact with the {target}? Return the demonstrated contact location.",
        "demonstrated_contact_affordance": f'Given the task "{instruction}", point to the demonstrated interaction target.',
        "relational_contact_placement": f"Locate the physical contact between the gripper fingers and the {target}.",
    }
    for family in (
        "PartAfford|demonstrated contact affordance|point",
        "PointBench|affordable|point",
        "RoboAfford|object affordance recognition|point",
        "demonstrated_contact_affordance",
        "relational_contact_placement",
    ):
        add_point(
            family,
            contact,
            contact_questions[family],
            coordinates=coordinates,
            evidence={
                "operator": "physical_contact_projection",
                "frame": contact,
                "contact": physical[0],
                "view": best_view(contact),
            },
        )
    add_point(
        "RoboSpatial-Home|configuration|bbox",
        last,
        f"Point to the {target} after demonstrated placement.",
    )
    gripper = states[first]["eef_2d"][best_view(first)]
    if gripper is None:
        raise ValueError("Configuration needs a projected gripper position")
    target_point = visible_point(first)
    dx, dy = [target_point[d] - gripper[d] for d in (0, 1)]
    configuration = ("right of" if dx > 0 else "left of") if abs(dx) >= abs(dy) else ("below" if dy > 0 else "above")
    add_choice(
        "configuration",
        [first],
        "Which target/gripper configuration is shown?",
        [f"the {target} is {direction} the robot gripper" for direction in ("left of", "right of", "above", "below")],
        f"the {target} is {configuration} the robot gripper",
        {
            "operator": "target_gripper_relation",
            "frame": first,
            "target_point": target_point,
            "gripper_point": gripper,
            "view": best_view(first),
        },
    )
    for family, i, question, flag in [
        (
            "ContactDecide",
            grasp,
            f"Are the fingers contacting the {target}?",
            any(states[grasp]["finger_contact"]),
        ),
        (
            "Q3_secure_grasp_status",
            grasp,
            f"Is the {target} engaged by both opposing fingers?",
            states[grasp]["secure_grasp"],
        ),
        (
            "Q4_task_completion_status",
            last,
            f"Has the {target} been released onto the {destination}?",
            states[last]["released_in_destination"],
        ),
        (
            "Success_Task",
            last,
            f'Based on these frames of one robot execution, was the task "{instruction}" completed successfully?',
            states[last]["released_in_destination"],
        ),
    ]:
        add_choice(
            family,
            [i, i]
            if family in {"ContactDecide", "Q3_secure_grasp_status"}
            else [first, i]
            if family == "Success_Task"
            else [i],
            question,
            ["Yes", "No"],
            "Yes" if flag else "No",
            {
                "operator": "contact_and_release",
                "frame": i,
                "contacts": states[i]["contacts"],
                "finger_contact": states[i]["finger_contact"],
                "criterion": ir["success_criterion"],
            },
            views=ir["views"] if family in {"ContactDecide", "Q3_secure_grasp_status"} else None,
        )
    # Select a negative class absent from both metadata and referenced assets.
    add_record(
        "balanced present-absent localization",
        [frame_image(first)],
        presence_question(target),
        {
            "type": "point_or_no_object",
            "expected_kind": "point",
            "point": visible_point(first),
            "key": "point_2d",
        },
        {"operator": "visible_instance_point", "frame": first, "object": "obj"},
    )
    absent = absent_class(ir["objects"].values(), ir["source_manifest"]["assets"])
    add_record(
        "balanced present-absent localization",
        [frame_image(first)],
        presence_question(absent),
        {
            "type": "point_or_no_object",
            "expected_kind": "no_object",
            "accepted_text": ["No object"],
        },
        {
            "operator": "scene_object_absence",
            "frame": first,
            "queried_class": absent,
            "scene_classes": list(ir["objects"].values()),
            "asset_manifest": "ir/episode_ir.json#source_manifest",
        },
    )
    rows[-1]["id"] += "__absent"
    for family, count in [
        ("immediate_planning", 1),
        ("immediate_planning_with_context", 2),
        ("remaining_long_horizon_planning", 3),
    ]:
        indices = [i for i in ir["sampled_indices"] if i < contact][:count]
        if not indices:
            indices = [first]
        context_state = states[indices[-1]]
        planned = remaining_plan(context_state, target, destination)
        options = [
            planned,
            f"leave the {target} on the {source}",
            f"move the {destination} to the {source}",
            f"open the {destination}",
        ]
        add_choice(
            family,
            indices,
            f'Given "{instruction}", which sequence remains to be performed?',
            options,
            planned,
            {
                "operator": "state_conditioned_pick_place_planner",
                "context_frame": indices[-1],
                "phase": phase(context_state),
                "finger_contact": context_state["finger_contact"],
                "secure_grasp": context_state["secure_grasp"],
                "released_in_destination": context_state["released_in_destination"],
                "frames": indices,
                "instruction": instruction,
                "demonstrated_contact": contact,
                "demonstrated_placement": placed,
            },
        )
    future = f"The {target} will move from the {source} into the {destination}."
    add_choice(
        "future_prediction",
        [first],
        f'If the demonstrated task "{instruction}" succeeds, what will happen?',
        [
            future,
            f"The {target} will stay on the {source}.",
            f"The {destination} will leave the stove.",
            "The robot will open a drawer.",
        ],
        future,
        {"operator": "instruction_conditioned_goal", "instruction": instruction},
    )
    initial_position = states[first]["objects"]["obj"]
    final_position = states[last]["objects"]["obj"]
    if not states[last]["released_in_destination"] or math.dist(initial_position, final_position) <= 1e-6:
        raise ValueError("No supported pick-and-place consequence in simulator IR")
    consequence = f"The {target} moved from the {source} to the {destination}."
    add_choice(
        "action_consequence",
        [first, last],
        "What changed from the first image to the second?",
        [
            consequence,
            f"The {target} stayed on the {source}.",
            f"The {destination} was opened.",
            "The robot left the kitchen.",
        ],
        consequence,
        {
            "operator": "object_displacement_and_destination_contact",
            "initial": states[first]["objects"],
            "final": states[last]["objects"],
            "released_in_destination": states[last]["released_in_destination"],
        },
    )
    pair_first = max(
        (i for i in ir["sampled_indices"] if i < contact),
        key=lambda i: min(states[i]["views"][v]["objects"].get("obj", {}).get("pixels", 0) for v in ir["views"]),
    )
    pair_grasp = max(
        (i for i in ir["sampled_indices"] if states[i]["secure_grasp"]),
        key=lambda i: min(states[i]["views"][v]["objects"].get("obj", {}).get("pixels", 0) for v in ir["views"]),
    )
    for i in (pair_first, pair_grasp):
        for v in ir["views"]:
            visible_point(i, v=v)
    add_choice(
        "multi_view_reasoning",
        [pair_first, pair_first],
        "What task do these synchronized views support?",
        [instruction, "Open a cabinet.", "Turn on the faucet.", "Close a drawer."],
        instruction,
        {
            "operator": "synchronized_views_and_instruction",
            "frames": [pair_first, pair_first],
        },
        [view, other],
    )
    add_choice(
        "multi_view_task_consistency",
        [pair_grasp, pair_grasp],
        f"Are the two views consistent with grasping the same {target}?",
        ["Yes", "No"],
        "Yes" if states[pair_grasp]["secure_grasp"] else "No",
        {"operator": "shared_object_identity_and_contact", "frame": pair_grasp},
        [view, other],
    )
    phase_text = {
        "holding": f"holding the {target} between the fingers",
        "contact": f"establishing contact with the {target}",
        "approach": f"approaching the untouched {target}",
        "released": f"the {target} is released in the {destination}",
    }
    add_choice(
        "multi_view_phase_consistency",
        [pair_grasp, pair_grasp],
        "Which action phase explains both synchronized views?",
        [
            f"holding the {target} between the fingers",
            f"approaching the untouched {target}",
            f"establishing contact with the {target}",
            f"the {target} is released in the {destination}",
            "idle with no object interaction",
        ],
        phase_text[phase(states[pair_grasp])],
        {
            "operator": "simulator_phase_classifier",
            "frame": pair_grasp,
            "phase": phase(states[pair_grasp]),
        },
        [view, other],
    )
    contexts = []
    for index in ir["sampled_indices"]:
        try:
            short_trajectory(states, index, view)
        except ValueError:
            continue
        contexts.append(index)
    if len(contexts) < 2:
        raise ValueError("Need two supported trajectory contexts at 20 Hz")
    for family, context in zip(
        [
            "continuous_trajectory_eval_format/sharerobot_trajectory_variable_point_format",
            "continuous_trajectory_eval_format/vabench_visual_trace_8point_format",
        ],
        contexts[:2],
    ):
        n = 8
        traj, offsets = short_trajectory(states, context, view)
        spec = {
            "type": "traj2d",
            "traj": traj,
            "key": "point_2d",
            "n_points": n,
            "gt_motion": sum((math.dist(a, b) for (a, b) in zip(traj, traj[1:]))),
        }
        add_record(
            family,
            [frame_image(context, view)],
            trajectory_question(instruction, states[context]["eef_2d"][view]),
            spec,
            {
                "operator": "calibrated_eef_projection",
                "context_frame": context,
                "state_indices": list(range(context + 1, context + 11)),
                "waypoint_frame_offsets": offsets,
                "horizon_frames": 10,
                "rate_hz": 20,
                "exclude_current": True,
                "view": view,
            },
        )
    return rows
