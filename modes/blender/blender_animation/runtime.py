"""Blender-side build, validation, preview, and frame rendering runtime."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import bpy

from .config import ProjectConfig


@dataclass(frozen=True)
class SceneContext:
    config: ProjectConfig
    quality: str
    project_dir: Path
    output_dir: Path


BuildScene = Callable[[SceneContext], Any]
ValidateScene = Callable[[SceneContext, Any], None]
ManifestFacts = Callable[[SceneContext, Any], dict[str, Any]]


def run_scene(
    build_scene: BuildScene,
    *,
    validate_scene: ValidateScene | None = None,
    manifest_facts: ManifestFacts | None = None,
) -> None:
    """Run a scene callback through the common headless render lifecycle."""

    started = time.monotonic()
    args = _parse_args()
    config = ProjectConfig.load(args.project_file)
    _require_blender_version(config)
    _clear_scene()
    _configure_scene(config, args.quality)

    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    context = SceneContext(
        config=config,
        quality=args.quality,
        project_dir=config.project_dir,
        output_dir=output_dir,
    )
    state = build_scene(context)
    _validate_common(context)
    if validate_scene is not None:
        validate_scene(context, state)

    facts = manifest_facts(context, state) if manifest_facts is not None else {}
    _write_manifest(context, facts)
    rendered_frames = _render(context, args)
    rendered_summary: list[int] | dict[str, int]
    if len(rendered_frames) <= 20:
        rendered_summary = rendered_frames
    else:
        rendered_summary = {
            "count": len(rendered_frames),
            "first": rendered_frames[0],
            "last": rendered_frames[-1],
        }

    if args.save_blend or args.render_all:
        blend_path = output_dir / f"{config.name}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        print(f"BLEND={blend_path}")

    print(
        "BUILD_SUMMARY="
        + json.dumps(
            {
                **config.public_summary(),
                "quality": args.quality,
                "objects": len(bpy.data.objects),
                "rendered_frames": rendered_summary,
                "elapsed_seconds": round(time.monotonic() - started, 3),
            },
            sort_keys=True,
        )
    )


def _parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-file", required=True)
    parser.add_argument("--quality", choices=("preview", "final"), default="preview")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--preview-frames", nargs="+", type=int)
    output_group.add_argument("--render-all", action="store_true")
    parser.add_argument("--save-blend", action="store_true")
    return parser.parse_args(argv)


def _require_blender_version(config: ProjectConfig) -> None:
    actual = bpy.app.version[:2]
    if actual != config.blender_version:
        expected = ".".join(str(part) for part in config.blender_version)
        raise RuntimeError(f"Expected Blender {expected}.x, got {bpy.app.version_string}")


def _clear_scene() -> None:
    for datablocks in (
        bpy.data.objects,
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            datablocks.remove(datablock, do_unlink=True)


def _configure_scene(config: ProjectConfig, quality: str) -> None:
    scene = bpy.context.scene
    preset = config.preset(quality)
    scene.frame_start = config.timeline.frame_start
    scene.frame_end = config.timeline.frame_end
    scene.render.fps = config.timeline.fps
    scene.render.fps_base = 1
    scene.render.engine = config.render.engine
    scene.render.resolution_x = preset.width
    scene.render.resolution_y = preset.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = config.render.transparent_background
    scene.render.use_file_extension = True
    scene.render.use_overwrite = True
    scene.render.use_placeholder = False
    scene.eevee.taa_render_samples = preset.samples
    scene.view_settings.view_transform = config.render.view_transform
    scene.view_settings.look = config.render.look


def _validate_common(context: SceneContext) -> None:
    scene = bpy.context.scene
    timeline = context.config.timeline
    if scene.camera is None:
        raise RuntimeError("Scene builder must assign bpy.context.scene.camera")
    if (scene.frame_start, scene.frame_end) != (timeline.frame_start, timeline.frame_end):
        raise RuntimeError("Scene builder changed the configured frame range")
    if scene.render.fps != timeline.fps:
        raise RuntimeError("Scene builder changed the configured frame rate")


def _write_manifest(context: SceneContext, facts: dict[str, Any]) -> None:
    manifest = {
        **context.config.public_summary(),
        "blender": bpy.app.version_string,
        "quality": context.quality,
        "object_count": len(bpy.data.objects),
        "facts": facts,
    }
    path = context.output_dir / "scene-manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"MANIFEST={path}")


def _render(context: SceneContext, args: argparse.Namespace) -> list[int]:
    scene = bpy.context.scene
    timeline = context.config.timeline
    if args.preview_frames:
        preview_dir = context.output_dir / "previews"
        preview_dir.mkdir(parents=True, exist_ok=True)
        for frame in args.preview_frames:
            if not timeline.frame_start <= frame <= timeline.frame_end:
                raise ValueError(
                    f"Preview frame must be {timeline.frame_start}..{timeline.frame_end}"
                )
            scene.frame_set(frame)
            scene.render.filepath = str(
                preview_dir / f"{args.quality}-frame-{frame:04d}.png"
            )
            bpy.ops.render.render(write_still=True)
            print(f"PREVIEW={scene.render.filepath}")
        return list(args.preview_frames)

    if args.render_all:
        directory_name = "preview-frames" if args.quality == "preview" else "frames"
        frame_dir = context.output_dir / directory_name
        frame_dir.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(frame_dir / "frame_####")
        bpy.ops.render.render(animation=True)
        print(f"FRAMES={frame_dir}")
        return list(range(timeline.frame_start, timeline.frame_end + 1))

    return []
