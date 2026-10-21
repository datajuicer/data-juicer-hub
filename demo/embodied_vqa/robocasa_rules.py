"""State-conditioned rules for supported RoboCasa pick-and-place tasks."""

import re


def task_roles(instruction, objects):
    target, source, destination = [
        re.sub(r"[_\s-]+", " ", objects[key]).strip() for key in ("obj", "obj_container", "container")
    ]
    text = instruction.casefold()
    if not re.search(r"\b(place|put)\b", text):
        raise ValueError("The rule planner supports pick-and-place instructions")
    for name in (target, source, destination):
        if not re.search(r"\b" + re.escape(name.casefold()) + r"\b", text):
            raise ValueError("Instruction does not establish the configured task roles")
    return target, source, destination


def remaining_plan(state, target, destination):
    if state["released_in_destination"]:
        return f"inspect the placement of the {target} in the {destination}"
    if state["secure_grasp"]:
        return f"move the held {target} to the {destination}, and release it"
    if any(state["finger_contact"]):
        return f"securely grasp the {target}, move it to the {destination}, and release it"
    return f"approach and grasp the {target}, move it to the {destination}, and release it"


def phase(state):
    if state["released_in_destination"]:
        return "released"
    if state["secure_grasp"]:
        return "holding"
    if any(state["finger_contact"]):
        return "contact"
    return "approach"


def recorded_task(manifest):
    """Read the task identifier from the recorded dataset location."""
    from pathlib import PurePosixPath

    parts = PurePosixPath(manifest["base"]).parts
    if len(parts) < 3 or parts[-1] != "lerobot" or not re.fullmatch(r"\d{8}", parts[-2]):
        raise ValueError("Expected a dated LeRobot task location in the source manifest")
    return parts[-3]


def absent_class(classes, assets, candidates=("pineapple", "apple", "banana")):
    """Choose a query class absent from recorded objects and all referenced assets."""
    inventory = "\n".join([*classes, *assets]).casefold()
    for candidate in candidates:
        if not re.search(r"(?<![a-z])" + re.escape(candidate.casefold()) + r"(?![a-z])", inventory):
            return candidate
    raise ValueError("No absent query class in the candidate vocabulary")
