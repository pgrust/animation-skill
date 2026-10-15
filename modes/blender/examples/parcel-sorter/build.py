#!/usr/bin/env python3
"""Build a generic parcel-routing animation in Blender 5.2."""

from __future__ import annotations

from typing import Any

import bpy

from blender_animation.runtime import SceneContext, run_scene
from blender_animation.scene import (
    add_area_light,
    add_attached_label,
    add_box,
    add_camera,
    add_curve,
    add_cylinder,
    add_text,
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


TEACHING_SENTENCE = (
    "A parcel keeps its identity while one routing decision changes its destination."
)

EVENTS = [
    {
        "parcel": "P1",
        "route": "A",
        "start": 20,
        "gate": 45,
        "finish": 72,
        "origin": (-5.4, 0.0, 1.15),
        "destination": (4.1, 2.1, 1.15),
    },
    {
        "parcel": "P2",
        "route": "B",
        "start": 54,
        "gate": 80,
        "finish": 108,
        "origin": (-6.5, 0.0, 1.15),
        "destination": (4.1, -2.1, 1.15),
    },
    {
        "parcel": "P3",
        "route": "A",
        "start": 88,
        "gate": 115,
        "finish": 143,
        "origin": (-7.6, 0.0, 1.15),
        "destination": (5.4, 2.1, 1.15),
    },
]

COLORS = {
    "background": "#0b0f14",
    "floor": "#111821",
    "structure": "#202b36",
    "border": "#3d4b59",
    "text": "#eef2f6",
    "muted": "#8f9baa",
    "idle": "#34414f",
    "route_a": "#51c7b7",
    "route_b": "#f09a61",
}


def build_scene(context: SceneContext) -> dict[str, Any]:
    collections = {
        name: new_collection(name)
        for name in ("STRUCTURE", "PATHS", "WORK", "SIGNALS", "LABELS", "LIGHTS", "CAMERAS")
    }
    materials = create_materials()
    create_world()
    camera = create_camera(collections["CAMERAS"])
    create_stage(materials, collections, camera)
    parcel_roots = create_parcels(materials, collections, camera)
    create_lighting(collections["LIGHTS"])
    return {"parcel_roots": parcel_roots}


def create_world() -> None:
    world = bpy.context.scene.world or bpy.data.worlds.new("WORLD")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = srgb_hex(COLORS["background"])
    background.inputs["Strength"].default_value = 0.08


def create_materials() -> dict[str, bpy.types.Material]:
    return {
        "floor": make_material("MAT_FLOOR", COLORS["floor"], roughness=0.84),
        "structure": make_material(
            "MAT_STRUCTURE", COLORS["structure"], metallic=0.45, roughness=0.38
        ),
        "border": make_material(
            "MAT_BORDER", COLORS["border"], metallic=0.7, roughness=0.28
        ),
        "text": make_material("MAT_TEXT", COLORS["text"], roughness=0.5),
        "muted": make_material("MAT_MUTED", COLORS["muted"], roughness=0.55),
        "route_a": make_material(
            "MAT_ROUTE_A", COLORS["route_a"], roughness=0.34, emission_strength=0.08
        ),
        "route_b": make_material(
            "MAT_ROUTE_B", COLORS["route_b"], roughness=0.34, emission_strength=0.08
        ),
    }


def create_camera(target: bpy.types.Collection) -> bpy.types.Object:
    return add_camera(
        "CAMERA_MAIN",
        (11.5, -16.0, 11.0),
        (0.0, 0.0, 1.5),
        target,
        projection="ORTHO",
        ortho_scale=16.0,
    )


def create_stage(
    materials: dict[str, bpy.types.Material],
    collections: dict[str, bpy.types.Collection],
    camera: bpy.types.Object,
) -> None:
    structure = collections["STRUCTURE"]
    paths = collections["PATHS"]
    labels = collections["LABELS"]
    signals = collections["SIGNALS"]

    add_box("FLOOR", (0.0, 0.0, -0.22), (8.4, 5.0, 0.22), materials["floor"], structure)
    infeed = add_box(
        "INFEED",
        (-4.0, 0.0, 0.48),
        (3.8, 0.72, 0.22),
        materials["structure"],
        structure,
    )
    gate = add_box(
        "ROUTING_GATE",
        (0.0, 0.0, 0.68),
        (0.82, 1.05, 0.68),
        materials["border"],
        structure,
    )
    bin_a = add_box(
        "BIN_A",
        (4.65, 2.1, 0.48),
        (2.0, 0.92, 0.22),
        materials["structure"],
        structure,
    )
    bin_b = add_box(
        "BIN_B",
        (4.65, -2.1, 0.48),
        (2.0, 0.92, 0.22),
        materials["structure"],
        structure,
    )

    add_curve(
        "PATH_TO_A",
        [(-3.6, 0.0, 0.78), (0.0, 0.0, 0.78), (2.1, 0.5, 0.78), (4.3, 2.1, 0.78)],
        materials["route_a"],
        paths,
        bevel_depth=0.055,
    )
    add_curve(
        "PATH_TO_B",
        [(-3.6, 0.0, 0.77), (0.0, 0.0, 0.77), (2.1, -0.5, 0.77), (4.3, -2.1, 0.77)],
        materials["route_b"],
        paths,
        bevel_depth=0.055,
    )

    add_text(
        "TITLE",
        "PARCEL SORTER",
        (-1.0, 1.8, 4.55),
        0.62,
        materials["text"],
        labels,
        camera=camera,
    )
    add_text(
        "SUBTITLE",
        "CLASSIFY ONCE  ·  KEEP OBJECT ID",
        (-1.0, 1.75, 3.95),
        0.27,
        materials["muted"],
        labels,
        camera=camera,
    )
    add_attached_label(
        "INFEED_LABEL",
        "UNSORTED INPUT",
        infeed,
        (0.0, -0.74, 0.0),
        0.2,
        materials["muted"],
        labels,
        orientation="FRONT",
    )
    add_attached_label(
        "GATE_LABEL",
        "ROUTE",
        gate,
        (0.0, -1.07, 0.0),
        0.23,
        materials["text"],
        labels,
        orientation="FRONT",
    )
    add_attached_label(
        "BIN_A_LABEL",
        "BIN A",
        bin_a,
        (0.0, -0.94, 0.0),
        0.24,
        materials["route_a"],
        labels,
        orientation="FRONT",
    )
    add_attached_label(
        "BIN_B_LABEL",
        "BIN B",
        bin_b,
        (0.0, -0.94, 0.0),
        0.24,
        materials["route_b"],
        labels,
        orientation="FRONT",
    )

    for event in EVENTS:
        route = event["route"]
        route_material = materials[f"route_{route.lower()}"]
        ring = add_cylinder(
            f"SIGNAL_{event['parcel']}_{route}",
            (0.0, 0.0, 1.43),
            0.6,
            0.035,
            route_material,
            signals,
        )
        set_visibility([ring], [(event["gate"] - 3, event["gate"] + 6)])


def create_parcels(
    materials: dict[str, bpy.types.Material],
    collections: dict[str, bpy.types.Collection],
    camera: bpy.types.Object,
) -> list[bpy.types.Object]:
    parcel_roots: list[bpy.types.Object] = []
    for event in EVENTS:
        parcel = event["parcel"]
        route = event["route"]
        origin = event["origin"]
        destination = event["destination"]
        route_color = COLORS[f"route_{route.lower()}"]

        material = make_material(
            f"MAT_{parcel}",
            COLORS["idle"],
            roughness=0.3,
            emission_color=route_color,
        )
        root = bpy.data.objects.new(f"{parcel}_ROOT", None)
        root.location = origin
        collections["WORK"].objects.link(root)
        body = add_box(
            f"{parcel}_BODY",
            origin,
            (0.58, 0.46, 0.28),
            material,
            collections["WORK"],
            bevel=0.12,
        )
        parent_keep_transform(body, root)
        add_attached_label(
            f"{parcel}_LABEL",
            parcel,
            body,
            (0.0, 0.0, 0.3),
            0.22,
            materials["floor"],
            collections["LABELS"],
            orientation="TOP",
        )

        key_location(root, 1, origin)
        key_location(root, event["start"], origin)
        key_location(root, event["gate"], (0.0, 0.0, 1.15))
        key_location(root, event["finish"], destination)
        key_location(root, 150, destination)
        set_interpolation(root, "BEZIER")

        key_scale(root, event["gate"] - 2, (1.0, 1.0, 1.0))
        key_scale(root, event["gate"] + 2, (1.12, 1.12, 1.12))
        key_scale(root, event["gate"] + 6, (1.0, 1.0, 1.0))
        set_interpolation(root, "BEZIER")

        shader = material.node_tree.nodes["Principled BSDF"]
        key_socket(shader.inputs["Base Color"], 1, srgb_hex(COLORS["idle"]))
        key_socket(
            shader.inputs["Base Color"], event["start"], srgb_hex(route_color)
        )
        key_socket(shader.inputs["Emission Strength"], 1, 0.0)
        key_socket(shader.inputs["Emission Strength"], event["start"], 0.22)
        key_socket(shader.inputs["Emission Strength"], event["finish"] + 5, 0.06)
        parcel_roots.append(root)
    return parcel_roots


def create_lighting(target: bpy.types.Collection) -> None:
    add_area_light("KEY", (-3.0, -6.0, 12.0), 1050, 6.0, "#fff1e7", (0, 0, 1), target)
    add_area_light("FILL", (-6.0, 5.0, 7.0), 420, 7.0, "#b8d7ff", (0, 0, 1), target)
    add_area_light("RIM", (7.0, 4.0, 9.0), 700, 5.0, "#78d7c9", (2, 0, 1), target)


def validate_scene(context: SceneContext, state: dict[str, Any]) -> None:
    roots = state["parcel_roots"]
    if len(roots) != len(EVENTS):
        raise RuntimeError("Every event must create one parcel root")
    if [event["parcel"] for event in EVENTS] != ["P1", "P2", "P3"]:
        raise RuntimeError("Worked example expects parcels P1, P2, and P3")
    if [event["route"] for event in EVENTS] != ["A", "B", "A"]:
        raise RuntimeError("Worked example expects routes A, B, and A")
    if bpy.context.scene.camera.data.type != "ORTHO":
        raise RuntimeError("Worked example requires an orthographic camera")
    if context.config.timeline.frame_end < max(event["finish"] for event in EVENTS):
        raise RuntimeError("Timeline ends before the final parcel arrives")
    semantic_labels = [
        bpy.data.objects[name]
        for name in (
            "INFEED_LABEL",
            "GATE_LABEL",
            "BIN_A_LABEL",
            "BIN_B_LABEL",
            "P1_LABEL",
            "P2_LABEL",
            "P3_LABEL",
        )
    ]
    if any(label.parent is None for label in semantic_labels):
        raise RuntimeError("Every semantic label must be attached to its owner")


def manifest_facts(context: SceneContext, state: dict[str, Any]) -> dict[str, Any]:
    del context, state
    return {
        "teaching_sentence": TEACHING_SENTENCE,
        "events": [
            {
                "parcel": event["parcel"],
                "route": event["route"],
                "start": event["start"],
                "gate": event["gate"],
                "finish": event["finish"],
            }
            for event in EVENTS
        ],
        "final_bins": {"A": ["P1", "P3"], "B": ["P2"]},
    }


if __name__ == "__main__":
    run_scene(
        build_scene,
        validate_scene=validate_scene,
        manifest_facts=manifest_facts,
    )
