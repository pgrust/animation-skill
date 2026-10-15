#!/usr/bin/env python3
"""Opinionated starter for a dense, depth-readable technical pipeline."""

from __future__ import annotations

from typing import Any

import bpy

from blender_animation.runtime import SceneContext, run_scene
from blender_animation.scene import (
    DEFAULT_PALETTE,
    add_attached_label,
    add_box,
    add_cylinder,
    add_curve,
    add_text,
    add_three_point_lighting,
    add_three_quarter_camera,
    follow_orthographic_camera,
    key_camera_pose,
    key_location,
    key_scale,
    key_socket,
    make_material,
    new_collection,
    parent_keep_transform,
    set_interpolation,
    set_visibility,
    srgb_hex,
)


TITLE = "PARALLEL PIPELINE"
TEACHING_SENTENCE = (
    "Persistent work items overlap across three stages while keeping identity."
)

LANES = (-1.65, 0.0, 1.65)
STAGES = (
    {"name": "INGEST", "x": -3.4},
    {"name": "TRANSFORM", "x": 0.0},
    {"name": "COMMIT", "x": 3.4},
)
START_FRAMES = (30, 82, 104, 126, 148, 170, 192, 214)
EVENTS = [
    {
        "item": f"W{index + 1}",
        "lane": index % len(LANES),
        "start": start,
        "stage_1": start + 14,
        "stage_2": start + 32,
        "stage_3": start + 50,
        "finish": start + 68,
    }
    for index, start in enumerate(START_FRAMES)
]


def build_scene(context: SceneContext) -> dict[str, Any]:
    del context
    collections = {
        name: new_collection(name)
        for name in (
            "STRUCTURE",
            "PATHS",
            "WORK",
            "SIGNALS",
            "LABELS",
            "LIGHTS",
            "CAMERAS",
        )
    }
    materials = create_materials()
    create_world()
    camera = create_camera(collections["CAMERAS"])
    create_stage(materials, collections, camera)
    roots = create_work_items(materials, collections, camera)
    add_three_point_lighting(collections["LIGHTS"], focal_point=(0.0, 0.0, 1.0))
    return {"roots": roots, "camera": camera}


def create_world() -> None:
    world = bpy.context.scene.world or bpy.data.worlds.new("WORLD")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = srgb_hex(DEFAULT_PALETTE["world"])
    background.inputs["Strength"].default_value = 0.075


def create_materials() -> dict[str, bpy.types.Material]:
    return {
        "floor": make_material(
            "MAT_FLOOR", DEFAULT_PALETTE["floor"], roughness=0.82
        ),
        "structure": make_material(
            "MAT_STRUCTURE",
            DEFAULT_PALETTE["structure"],
            metallic=0.42,
            roughness=0.34,
        ),
        "edge": make_material(
            "MAT_EDGE",
            DEFAULT_PALETTE["structure_light"],
            metallic=0.68,
            roughness=0.26,
        ),
        "text": make_material(
            "MAT_TEXT", DEFAULT_PALETTE["text"], roughness=0.48
        ),
        "muted": make_material(
            "MAT_MUTED", DEFAULT_PALETTE["muted"], roughness=0.55
        ),
        "active": make_material(
            "MAT_ACTIVE",
            DEFAULT_PALETTE["active"],
            roughness=0.3,
            emission_strength=0.16,
        ),
        "secondary": make_material(
            "MAT_SECONDARY",
            DEFAULT_PALETTE["secondary"],
            roughness=0.32,
            emission_strength=0.12,
        ),
        "accent": make_material(
            "MAT_ACCENT",
            DEFAULT_PALETTE["accent"],
            roughness=0.32,
            emission_strength=0.12,
        ),
        "settled": make_material(
            "MAT_SETTLED",
            DEFAULT_PALETTE["settled"],
            roughness=0.34,
            emission_strength=0.08,
        ),
    }


def create_camera(target: bpy.types.Collection) -> bpy.types.Object:
    camera = add_three_quarter_camera(
        "CAMERA_MAIN",
        target,
        target_point=(0.0, 0.0, 1.25),
        location=(12.5, -18.0, 12.0),
        ortho_scale=19.0,
    )
    key_camera_pose(
        camera,
        1,
        (12.5, -18.0, 12.0),
        (0.0, 0.0, 1.25),
        ortho_scale=19.0,
    )
    key_camera_pose(
        camera,
        28,
        (11.0, -16.0, 10.5),
        (0.0, 0.0, 1.2),
        ortho_scale=17.5,
    )
    key_camera_pose(
        camera,
        282,
        (11.0, -16.0, 10.5),
        (0.0, 0.0, 1.2),
        ortho_scale=17.5,
    )
    key_camera_pose(
        camera,
        310,
        (10.5, -14.5, 9.2),
        (1.0, 0.0, 1.25),
        ortho_scale=16.4,
    )
    set_interpolation(camera, "BEZIER")
    set_interpolation(camera.data, "BEZIER")
    return camera


def global_caption(
    name: str,
    body: str,
    location: tuple[float, float, float],
    size: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    camera: bpy.types.Object,
) -> bpy.types.Object:
    """Add title/caption text; semantic labels use add_attached_label."""

    label = add_text(name, body, location, size, material, target, camera=camera)
    follow_orthographic_camera(label, camera)
    return label


def create_stage(
    materials: dict[str, bpy.types.Material],
    collections: dict[str, bpy.types.Collection],
    camera: bpy.types.Object,
) -> None:
    structure = collections["STRUCTURE"]
    paths = collections["PATHS"]
    signals = collections["SIGNALS"]
    labels = collections["LABELS"]

    add_box(
        "FLOOR",
        (0.0, 0.0, -0.28),
        (9.4, 5.2, 0.28),
        materials["floor"],
        structure,
        bevel=0.16,
    )
    add_box(
        "BACK_RISER",
        (0.0, 4.35, 1.05),
        (8.7, 0.22, 1.05),
        materials["structure"],
        structure,
        bevel=0.12,
    )

    lane_materials = (
        materials["active"],
        materials["secondary"],
        materials["accent"],
    )
    for lane_index, lane_y in enumerate(LANES):
        add_curve(
            f"LANE_{lane_index + 1}_PATH",
            [
                (-8.0, lane_y, 0.58),
                (-3.4, lane_y, 0.58),
                (0.0, lane_y, 0.58),
                (3.4, lane_y, 0.58),
                (8.0, lane_y, 0.58),
            ],
            lane_materials[lane_index],
            paths,
            bevel_depth=0.045,
        )

    for stage_index, stage in enumerate(STAGES):
        x = stage["x"]
        stage_base = add_box(
            f"STAGE_{stage_index + 1}_BASE",
            (x, 0.0, 0.36),
            (1.12, 2.72, 0.36),
            materials["structure"],
            structure,
            bevel=0.16,
        )
        add_box(
            f"STAGE_{stage_index + 1}_CAP",
            (x, 0.0, 0.78),
            (0.82, 2.45, 0.08),
            materials["edge"],
            structure,
            bevel=0.06,
        )
        for lane_index, lane_y in enumerate(LANES):
            add_cylinder(
                f"STAGE_{stage_index + 1}_LANE_{lane_index + 1}_SOCKET",
                (x, lane_y, 0.94),
                0.58,
                0.08,
                materials["edge"],
                structure,
            )
        add_attached_label(
            f"STAGE_{stage_index + 1}_LABEL",
            stage["name"],
            stage_base,
            (0.0, -2.75, 0.0),
            0.29,
            materials["text"],
            labels,
            orientation="FRONT",
        )

    title = global_caption(
        "TITLE",
        TITLE,
        (-0.5, 3.05, 4.85),
        0.62,
        materials["text"],
        labels,
        camera,
    )
    subtitle = global_caption(
        "SUBTITLE",
        "ONE COMPLETE PASS  ·  THEN OVERLAPPED WORK",
        (-0.5, 3.02, 4.32),
        0.25,
        materials["muted"],
        labels,
        camera,
    )
    set_visibility([title, subtitle], [(1, 282)])

    final_label = global_caption(
        "FINAL_LABEL",
        "8 ITEMS  ·  3 LANES  ·  IDENTITY PRESERVED",
        (1.0, 3.0, 4.15),
        0.3,
        materials["settled"],
        labels,
        camera,
    )
    set_visibility([final_label], [(284, 330)])

    pulse_materials = (
        materials["active"],
        materials["secondary"],
        materials["accent"],
    )
    for event in EVENTS:
        lane_index = event["lane"]
        lane_y = LANES[lane_index]
        for stage_index, frame_key in enumerate(("stage_1", "stage_2", "stage_3")):
            pulse = add_cylinder(
                f"PULSE_{event['item']}_{stage_index + 1}",
                (STAGES[stage_index]["x"], lane_y, 1.01),
                0.72,
                0.055,
                pulse_materials[lane_index],
                signals,
            )
            arrival = event[frame_key]
            set_visibility([pulse], [(arrival - 2, arrival + 5)])


def create_work_items(
    materials: dict[str, bpy.types.Material],
    collections: dict[str, bpy.types.Collection],
    camera: bpy.types.Object,
) -> list[bpy.types.Object]:
    roots: list[bpy.types.Object] = []
    lane_colors = (
        DEFAULT_PALETTE["active"],
        DEFAULT_PALETTE["secondary"],
        DEFAULT_PALETTE["accent"],
    )
    for index, event in enumerate(EVENTS):
        lane_index = event["lane"]
        lane_y = LANES[lane_index]
        queue_x = -7.1 - 0.5 * (index // len(LANES))
        output_x = 6.7 + 0.85 * (index // len(LANES))
        origin = (queue_x, lane_y, 1.1)
        destination = (output_x, lane_y, 1.1)
        active_color = lane_colors[lane_index]

        material = make_material(
            f"MAT_{event['item']}",
            DEFAULT_PALETTE["structure_light"],
            metallic=0.24,
            roughness=0.28,
            emission_color=active_color,
        )
        root = bpy.data.objects.new(f"{event['item']}_ROOT", None)
        root.location = origin
        collections["WORK"].objects.link(root)
        body = add_box(
            f"{event['item']}_BODY",
            origin,
            (0.54, 0.44, 0.28),
            material,
            collections["WORK"],
            bevel=0.13,
        )
        stripe = add_box(
            f"{event['item']}_STRIPE",
            (origin[0], origin[1], origin[2] + 0.31),
            (0.42, 0.32, 0.035),
            materials[("active", "secondary", "accent")[lane_index]],
            collections["WORK"],
            bevel=0.035,
        )
        for child in (body, stripe):
            parent_keep_transform(child, root)
        add_attached_label(
            f"{event['item']}_LABEL",
            event["item"],
            stripe,
            (0.0, 0.0, 0.042),
            0.18,
            materials["floor"],
            collections["LABELS"],
            orientation="TOP",
        )

        key_location(root, 1, origin)
        key_location(root, event["start"], origin)
        key_location(root, event["stage_1"], (STAGES[0]["x"], lane_y, 1.1))
        key_location(root, event["stage_2"], (STAGES[1]["x"], lane_y, 1.1))
        key_location(root, event["stage_3"], (STAGES[2]["x"], lane_y, 1.1))
        key_location(root, event["finish"], destination)
        key_location(root, 330, destination)

        for arrival in (event["stage_1"], event["stage_2"], event["stage_3"]):
            key_scale(root, arrival - 2, (1.0, 1.0, 1.0))
            key_scale(root, arrival + 2, (1.12, 1.12, 1.12))
            key_scale(root, arrival + 6, (1.0, 1.0, 1.0))
        set_interpolation(root, "BEZIER")

        shader = material.node_tree.nodes["Principled BSDF"]
        key_socket(
            shader.inputs["Base Color"],
            1,
            srgb_hex(DEFAULT_PALETTE["structure_light"]),
        )
        key_socket(shader.inputs["Base Color"], event["start"], srgb_hex(active_color))
        key_socket(
            shader.inputs["Base Color"],
            event["finish"],
            srgb_hex(DEFAULT_PALETTE["settled"]),
        )
        key_socket(shader.inputs["Emission Strength"], 1, 0.0)
        key_socket(shader.inputs["Emission Strength"], event["start"], 0.24)
        key_socket(shader.inputs["Emission Strength"], event["finish"] + 6, 0.05)

        roots.append(root)
    return roots


def validate_scene(context: SceneContext, state: dict[str, Any]) -> None:
    roots = state["roots"]
    if len(roots) != len(EVENTS):
        raise RuntimeError("Every event must create one persistent work item")
    if len(EVENTS) < 6:
        raise RuntimeError("Starter density requires at least six work items")
    if len({event["lane"] for event in EVENTS}) != 3:
        raise RuntimeError("Starter must use all three depth lanes")
    if any(EVENTS[index]["start"] >= EVENTS[index + 1]["start"] for index in range(7)):
        raise RuntimeError("Work-item start order must be strictly increasing")
    if context.config.timeline.frame_end - EVENTS[-1]["finish"] < 45:
        raise RuntimeError("Final state must hold for at least 1.5 seconds")
    camera = state["camera"]
    if camera.data.type != "ORTHO":
        raise RuntimeError("Starter expects an orthographic three-quarter camera")
    if min(abs(value) for value in camera.location) < 2.0:
        raise RuntimeError("Camera must remain offset on all axes to expose depth")
    semantic_labels = [
        bpy.data.objects[f"STAGE_{index}_LABEL"] for index in range(1, 4)
    ] + [bpy.data.objects[f"W{index}_LABEL"] for index in range(1, 9)]
    if any(label.parent is None for label in semantic_labels):
        raise RuntimeError("Every semantic label must be attached to its owner")
    if any(label.constraints.get("FACE_CAMERA") for label in semantic_labels):
        raise RuntimeError("Starter semantic labels must be surface-aligned, not HUD text")


def manifest_facts(context: SceneContext, state: dict[str, Any]) -> dict[str, Any]:
    del context, state
    return {
        "teaching_sentence": TEACHING_SENTENCE,
        "archetype": "parallel-pipeline",
        "label_policy": "semantic labels are surface-attached scene objects",
        "stages": [stage["name"] for stage in STAGES],
        "events": EVENTS,
        "final_items": [event["item"] for event in EVENTS],
        "illustrative": [
            "lane count",
            "frame timing",
            "geometry",
            "camera choreography",
            "colors",
        ],
    }


if __name__ == "__main__":
    run_scene(
        build_scene,
        validate_scene=validate_scene,
        manifest_facts=manifest_facts,
    )
