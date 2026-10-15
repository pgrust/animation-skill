"""Small Blender 5.2 helpers for deterministic scene construction."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from math import radians

import bpy
from mathutils import Vector


# Neutral defaults for technical explainers. They are deliberately vivid enough
# to survive feed-size playback without carrying any product's visual identity.
DEFAULT_PALETTE = {
    "world": "#050914",
    "floor": "#0d1626",
    "structure": "#1d2b42",
    "structure_light": "#314866",
    "text": "#f4f8ff",
    "muted": "#9bacc3",
    "active": "#42d9c8",
    "secondary": "#ffb45b",
    "accent": "#9b8cff",
    "settled": "#80df9b",
}


def srgb_hex(value: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    raw = value.removeprefix("#")
    if len(raw) != 6:
        raise ValueError(f"Expected six-digit hex color, got {value!r}")
    channels = [int(raw[index : index + 2], 16) / 255.0 for index in (0, 2, 4)]

    def linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    return tuple(linear(channel) for channel in channels) + (alpha,)


def new_collection(name: str) -> bpy.types.Collection:
    target = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(target)
    return target


def move_to_collection(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    target.objects.link(obj)


def make_material(
    name: str,
    base_color: str,
    *,
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission_color: str | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = srgb_hex(base_color)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader is None:
        raise RuntimeError("Principled BSDF node is missing")
    shader.inputs["Base Color"].default_value = srgb_hex(base_color)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Emission Color"].default_value = srgb_hex(
        emission_color or base_color
    )
    shader.inputs["Emission Strength"].default_value = emission_strength
    return material


def add_box(
    name: str,
    location: Sequence[float],
    scale: Sequence[float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    *,
    bevel: float = 0.08,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel > 0:
        modifier = obj.modifiers.new("BEVEL", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    move_to_collection(obj, target)
    return obj


def add_cylinder(
    name: str,
    location: Sequence[float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    *,
    vertices: int = 48,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    move_to_collection(obj, target)
    return obj


def add_curve(
    name: str,
    points: Sequence[Sequence[float]],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    *,
    bevel_depth: float = 0.035,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinates in zip(spline.bezier_points, points, strict=True):
        point.co = coordinates
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    target.objects.link(obj)
    curve.materials.append(material)
    return obj


def add_text(
    name: str,
    body: str,
    location: Sequence[float],
    size: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    *,
    camera: bpy.types.Object | None = None,
    align_x: str = "CENTER",
    align_y: str = "CENTER",
    extrude: float = 0.005,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.align_x = align_x
    curve.align_y = align_y
    curve.size = size
    curve.extrude = extrude
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    obj.location = location
    target.objects.link(obj)
    if camera is not None:
        face_camera(obj, camera)
    return obj


def add_attached_label(
    name: str,
    body: str,
    parent: bpy.types.Object,
    local_location: Sequence[float],
    size: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    *,
    orientation: str = "TOP",
    camera: bpy.types.Object | None = None,
    max_words: int = 3,
    extrude: float = 0.006,
) -> bpy.types.Object:
    """Attach a short semantic label to an in-scene object.

    ``TOP`` lies on a horizontal top face. ``FRONT`` lies on a vertical face
    whose normal points toward negative Y. ``BILLBOARD`` remains attached to
    the object but copies an orthographic camera's rotation. Global titles and
    captions should use ``add_text`` directly instead.
    """

    if "\n" in body:
        raise ValueError("Attached labels must use one line")
    if len(body.split()) > max_words:
        raise ValueError(
            f"Attached label {body!r} exceeds the {max_words}-word default"
        )
    mode = orientation.upper()
    if mode not in {"TOP", "FRONT", "BILLBOARD"}:
        raise ValueError(f"Unknown attached-label orientation: {orientation!r}")
    if mode == "BILLBOARD" and camera is None:
        raise ValueError("BILLBOARD labels require a camera")

    label = add_text(
        name,
        body,
        (0.0, 0.0, 0.0),
        size,
        material,
        target,
        extrude=extrude,
    )
    label.parent = parent
    label.location = local_location
    if mode == "TOP":
        label.rotation_euler = (0.0, 0.0, 0.0)
    elif mode == "FRONT":
        label.rotation_euler = (radians(90.0), 0.0, 0.0)
    else:
        face_camera(label, camera)
        follow_orthographic_camera(label, camera)
    return label


def add_camera(
    name: str,
    location: Sequence[float],
    target_point: Sequence[float],
    target: bpy.types.Collection,
    *,
    projection: str = "ORTHO",
    ortho_scale: float = 12.0,
    lens: float = 55.0,
) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(name)
    camera_data.type = projection
    camera_data.ortho_scale = ortho_scale
    camera_data.lens = lens
    camera_data.clip_start = 0.05
    camera_data.clip_end = 1000.0
    camera = bpy.data.objects.new(name, camera_data)
    camera.location = location
    target.objects.link(camera)
    look_at(camera, target_point)
    bpy.context.scene.camera = camera
    return camera


def add_three_quarter_camera(
    name: str,
    target: bpy.types.Collection,
    *,
    target_point: Sequence[float] = (0.0, 0.0, 1.2),
    location: Sequence[float] = (11.0, -16.0, 10.5),
    ortho_scale: float = 17.5,
) -> bpy.types.Object:
    """Add the default oblique camera for a wide technical stage.

    The offset in all three axes exposes top, front, and side faces. Adjust
    ``ortho_scale`` to fit the stage; do not flatten ``location`` onto an axis.
    """

    return add_camera(
        name,
        location,
        target_point,
        target,
        projection="ORTHO",
        ortho_scale=ortho_scale,
    )


def add_area_light(
    name: str,
    location: Sequence[float],
    energy: float,
    size: float,
    color: str,
    target_point: Sequence[float],
    target: bpy.types.Collection,
) -> bpy.types.Object:
    light_data = bpy.data.lights.new(name, "AREA")
    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size
    light_data.color = srgb_hex(color)[:3]
    light = bpy.data.objects.new(name, light_data)
    light.location = location
    target.objects.link(light)
    look_at(light, target_point)
    return light


def add_three_point_lighting(
    target: bpy.types.Collection,
    *,
    focal_point: Sequence[float] = (0.0, 0.0, 1.0),
    energy_scale: float = 1.0,
) -> dict[str, bpy.types.Object]:
    """Add a readable warm-key, cool-fill, neutral-rim lighting rig."""

    return {
        "key": add_area_light(
            "KEY_WARM",
            (-5.0, -7.0, 12.0),
            1150 * energy_scale,
            6.0,
            "#fff0df",
            focal_point,
            target,
        ),
        "fill": add_area_light(
            "FILL_COOL",
            (-7.0, 6.0, 8.0),
            460 * energy_scale,
            7.0,
            "#b8d8ff",
            focal_point,
            target,
        ),
        "rim": add_area_light(
            "RIM_NEUTRAL",
            (8.0, 5.0, 10.0),
            780 * energy_scale,
            5.0,
            "#d9e6ff",
            focal_point,
            target,
        ),
    }


def look_at(obj: bpy.types.Object, target: Sequence[float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def face_camera(obj: bpy.types.Object, camera: bpy.types.Object) -> None:
    if camera.data.type == "ORTHO":
        obj.rotation_euler = camera.rotation_euler.copy()
    else:
        look_at(obj, camera.location)


def follow_orthographic_camera(
    obj: bpy.types.Object, camera: bpy.types.Object
) -> bpy.types.Constraint:
    """Rotate an object-anchored billboard with an orthographic camera.

    Do not use this to place semantic labels in the camera plane. The label
    should remain parented to its owning in-scene object so depth and occlusion
    stay truthful.
    """

    constraint = obj.constraints.new("COPY_ROTATION")
    constraint.name = "FACE_CAMERA"
    constraint.target = camera
    return constraint


def key_camera_pose(
    camera: bpy.types.Object,
    frame: int,
    location: Sequence[float],
    target_point: Sequence[float],
    *,
    ortho_scale: float | None = None,
) -> None:
    """Key a semantic camera reframe; use sparingly between story beats."""

    camera.location = location
    look_at(camera, target_point)
    camera.keyframe_insert(data_path="location", frame=frame)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    if ortho_scale is not None:
        camera.data.ortho_scale = ortho_scale
        camera.data.keyframe_insert(data_path="ortho_scale", frame=frame)


def parent_keep_transform(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def key_location(obj: bpy.types.Object, frame: int, value: Sequence[float]) -> None:
    obj.location = value
    obj.keyframe_insert(data_path="location", frame=frame)


def key_scale(obj: bpy.types.Object, frame: int, value: Sequence[float]) -> None:
    obj.scale = value
    obj.keyframe_insert(data_path="scale", frame=frame)


def key_socket(socket: bpy.types.NodeSocket, frame: int, value: object) -> None:
    socket.default_value = value
    socket.keyframe_insert(data_path="default_value", frame=frame)


def set_interpolation(
    obj: bpy.types.Object, interpolation: str = "BEZIER"
) -> None:
    action = obj.animation_data.action if obj.animation_data else None
    if action is None:
        return
    for layer in action.layers:
        for strip in layer.strips:
            if strip.type != "KEYFRAME":
                continue
            for channelbag in strip.channelbags:
                for fcurve in channelbag.fcurves:
                    for key in fcurve.keyframe_points:
                        key.interpolation = interpolation
                        if interpolation == "BEZIER":
                            key.handle_left_type = "AUTO_CLAMPED"
                            key.handle_right_type = "AUTO_CLAMPED"


def set_visibility(
    objects: Iterable[bpy.types.Object], ranges: Sequence[tuple[int, int]]
) -> None:
    for obj in objects:
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_render", frame=0)
        for start, end in ranges:
            obj.hide_render = False
            obj.keyframe_insert(data_path="hide_render", frame=start)
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_render", frame=end + 1)
        set_interpolation(obj, "CONSTANT")
