"""VQA prompts and temporal target construction."""

import math

POINT_OUTPUT = (
    "Return only normalized 2D point coordinates in the range [0, 1000]. "
    'Use exactly this JSON format: [{"point_2d":[x,y]}]. Return exactly one point. '
    "Do not output <object>, <area>, <affordance>, <grasp pose>, a bounding box, "
    "labels, or explanations."
)


def presence_question(object_name):
    return (
        f"Point to every visible {object_name}, exactly one point per instance. "
        'If none are visible, output "No object". Otherwise return only JSON in '
        'the format [{"point_2d":[x,y]}], with integer coordinates normalized to [0,1000].'
    )


def short_trajectory(states, context, view):
    future = states[context + 1 : context + 11]
    if len(future) != 10:
        raise ValueError("Short trajectory requires ten future simulator frames")
    segment = states[context : context + 11]
    if any(not math.isclose(b["time"] - a["time"], 0.05, abs_tol=1e-6) for a, b in zip(segment, segment[1:])):
        raise ValueError("Trajectory requires simulator states sampled at 20 Hz")
    positions = [state["eef_2d"][view] for state in future]
    if any(p is None or any(c < 0 or c > 1000 for c in p) for p in positions):
        raise ValueError("Offscreen future end-effector point")
    offsets = [1 + 9 * j / 7 for j in range(8)]
    points = []
    for offset in offsets:
        i = min(int(offset) - 1, 8)
        fraction = offset - 1 - i
        points.append([round((1 - fraction) * positions[i][d] + fraction * positions[i + 1][d], 4) for d in (0, 1)])
    return points, offsets


def trajectory_question(instruction, current):
    return (
        f"You are currently a robot performing robotic manipulation tasks. The task instruction is: {instruction}\n"
        "Use 2D points to trace the immediate short-horizon movement trajectory of the robotic arm end-effector "
        "(not the manipulated object) over the next 10 simulator frames at 20 Hz.\n"
        f"The current gripper position is {current}.\n"
        "Provide the points in trajectory order as 8 evenly sampled waypoints. Do not include the current point.\n"
        'Return only a valid JSON array in exactly this format: [{"point_2d":[x1,y1]},...,{"point_2d":[xN,yN]}].\n'
        "Coordinates are [x,y] values normalized to [0,1000] on both axes. "
        "Do not add labels, bounding boxes, z coordinates, or extra JSON fields."
    )
