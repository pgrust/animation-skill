#!/usr/bin/env python3
"""Render and verify one project through Blender and FFmpeg."""

from __future__ import annotations

import argparse
import json
import math
import os
import py_compile
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from blender_animation.config import ConfigError, ProjectConfig  # noqa: E402


def main() -> None:
    args = parse_args()
    try:
        config = ProjectConfig.load(Path(args.project_dir) / "project.json")
        build_file = config.project_dir / "build.py"
        if not build_file.is_file():
            raise ConfigError(f"Scene builder not found: {build_file}")

        if args.command == "check":
            check_project(config, build_file)
        elif args.command == "preview":
            frames = args.frames or default_preview_frames(config)
            run_blender(config, build_file, "preview", preview_frames=frames)
        elif args.command == "timeline":
            render_timeline(config, build_file)
        elif args.command == "final":
            render_final(config, build_file)
        elif args.command == "verify":
            verify_video(config, config.output_dir / f"{config.name}.mp4", "final")
        elif args.command == "contact-sheet":
            make_contact_sheet(config, args.fps, args.columns)
        else:
            raise RuntimeError(f"Unhandled command: {args.command}")
    except (ConfigError, RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"render failed: {error}") from error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a configured project with headless Blender"
    )
    parser.add_argument("project_dir", help="Directory containing project.json and build.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="Validate configuration, source, and tools")

    preview = subparsers.add_parser("preview", help="Render checkpoint frames")
    preview.add_argument("frames", nargs="*", type=int)

    subparsers.add_parser("timeline", help="Render and encode a low-resolution timeline")
    subparsers.add_parser("final", help="Render frames, encode the master, and verify it")
    subparsers.add_parser("verify", help="Verify the existing master video")

    contact = subparsers.add_parser("contact-sheet", help="Create a master contact sheet")
    contact.add_argument("--fps", type=float, default=1.5)
    contact.add_argument("--columns", type=int, default=6)
    return parser.parse_args()


def check_project(config: ProjectConfig, build_file: Path) -> None:
    blender = require_tool("blender")
    require_tool("ffmpeg")
    require_tool("ffprobe")
    py_compile.compile(str(build_file), doraise=True)
    output = subprocess.run(
        [blender, "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    first_line = output.splitlines()[0] if output else ""
    match = re.fullmatch(r"Blender (\d+)\.(\d+).*", first_line)
    if match is None:
        raise RuntimeError(f"Could not parse Blender version from {first_line!r}")
    actual = (int(match.group(1)), int(match.group(2)))
    if actual != config.blender_version:
        expected = ".".join(str(part) for part in config.blender_version)
        raise RuntimeError(f"Expected Blender {expected}.x, got {first_line}")
    print(json.dumps({"tools": {"blender": first_line}, "project": config.public_summary()}, indent=2))


def default_preview_frames(config: ProjectConfig) -> list[int]:
    timeline = config.timeline
    midpoint = timeline.frame_start + timeline.frame_count // 2
    return sorted({timeline.frame_start, midpoint, timeline.frame_end})


def run_blender(
    config: ProjectConfig,
    build_file: Path,
    quality: str,
    *,
    preview_frames: list[int] | None = None,
    render_all: bool = False,
) -> None:
    blender = require_tool("blender")
    command = [
        blender,
        "--background",
        "--factory-startup",
        "--python-exit-code",
        "1",
        "--python-expr",
        f"import sys; sys.path.insert(0, {str(REPO_ROOT)!r})",
        "--python",
        str(build_file),
        "--",
        "--project-file",
        str(config.path),
        "--quality",
        quality,
    ]
    if preview_frames:
        command.extend(["--preview-frames", *(str(frame) for frame in preview_frames)])
    if render_all:
        command.append("--render-all")
    command.append("--save-blend")

    environment = os.environ.copy()
    old_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        f"{REPO_ROOT}{os.pathsep}{old_pythonpath}" if old_pythonpath else str(REPO_ROOT)
    )
    subprocess.run(command, check=True, cwd=REPO_ROOT, env=environment)


def render_timeline(config: ProjectConfig, build_file: Path) -> None:
    frame_dir = config.output_dir / "preview-frames"
    clean_frame_sequence(config, frame_dir)
    run_blender(config, build_file, "preview", render_all=True)
    verify_frame_sequence(config, frame_dir)
    output = config.output_dir / f"{config.name}-preview.mp4"
    encode_frames(config, frame_dir, output, preset="veryfast", crf=23)
    verify_video(config, output, "preview")


def render_final(config: ProjectConfig, build_file: Path) -> None:
    frame_dir = config.output_dir / "frames"
    clean_frame_sequence(config, frame_dir)
    run_blender(config, build_file, "final", render_all=True)
    verify_frame_sequence(config, frame_dir)
    output = config.output_dir / f"{config.name}.mp4"
    encode_frames(
        config,
        frame_dir,
        output,
        preset=config.video.preset,
        crf=config.video.crf,
    )
    verify_video(config, output, "final")


def clean_frame_sequence(config: ProjectConfig, frame_dir: Path) -> None:
    resolved_output = config.output_dir.resolve()
    resolved_frames = frame_dir.resolve()
    if resolved_frames.parent != resolved_output:
        raise RuntimeError(f"Refusing to clean frame directory outside {resolved_output}")
    frame_dir.mkdir(parents=True, exist_ok=True)
    for path in frame_dir.glob("frame_*.png"):
        path.unlink()


def expected_frame_names(config: ProjectConfig) -> set[str]:
    timeline = config.timeline
    return {
        f"frame_{frame:04d}.png"
        for frame in range(timeline.frame_start, timeline.frame_end + 1)
    }


def verify_frame_sequence(config: ProjectConfig, frame_dir: Path) -> None:
    actual = {path.name for path in frame_dir.glob("frame_*.png")}
    expected = expected_frame_names(config)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing {len(missing)} frame(s), first: {missing[0]}")
        if extra:
            details.append(f"found {len(extra)} extra frame(s), first: {extra[0]}")
        raise RuntimeError("Frame sequence failed completeness check: " + "; ".join(details))
    print(f"FRAME_SEQUENCE={len(actual)} complete frames in {frame_dir}")


def encode_frames(
    config: ProjectConfig,
    frame_dir: Path,
    output: Path,
    *,
    preset: str,
    crf: int,
) -> None:
    ffmpeg = require_tool("ffmpeg")
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-framerate",
            str(config.timeline.fps),
            "-start_number",
            str(config.timeline.frame_start),
            "-i",
            str(frame_dir / "frame_%04d.png"),
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-pix_fmt",
            config.video.pixel_format,
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
    )


def verify_video(config: ProjectConfig, video: Path, quality: str) -> dict[str, object]:
    if not video.is_file():
        raise RuntimeError(f"Video not found: {video}")
    ffprobe = require_tool("ffprobe")
    ffmpeg = require_tool("ffmpeg")
    probe_result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames",
            "-of",
            "json",
            str(video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(probe_result.stdout)
    streams = metadata.get("streams", [])
    if len(streams) != 1:
        raise RuntimeError(f"Expected one video stream, found {len(streams)}")
    stream = streams[0]
    preset = config.preset(quality)
    expected = {
        "codec_name": "h264",
        "width": preset.width,
        "height": preset.height,
        "pix_fmt": config.video.pixel_format,
        "nb_frames": str(config.timeline.frame_count),
    }
    for key, value in expected.items():
        if str(stream.get(key)) != str(value):
            raise RuntimeError(f"Expected {key}={value}, got {stream.get(key)}")
    if Fraction(stream["r_frame_rate"]) != config.timeline.fps:
        raise RuntimeError(
            f"Expected {config.timeline.fps} FPS, got {stream['r_frame_rate']}"
        )
    duration = float(metadata["format"]["duration"])
    tolerance = max(0.05, 1 / config.timeline.fps)
    if abs(duration - config.timeline.duration_seconds) > tolerance:
        raise RuntimeError(
            f"Expected duration {config.timeline.duration_seconds:.3f}, got {duration:.3f}"
        )

    manifest_path = config.output_dir / "scene-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("name") != config.name:
        raise RuntimeError("Manifest project name does not match project.json")
    if manifest.get("frame_count") != config.timeline.frame_count:
        raise RuntimeError("Manifest frame count does not match project.json")

    subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(video), "-f", "null", "-"],
        check=True,
    )
    print("VIDEO_VERIFY=" + json.dumps(metadata, sort_keys=True))
    return metadata


def make_contact_sheet(config: ProjectConfig, fps: float, columns: int) -> None:
    if fps <= 0:
        raise RuntimeError("Contact-sheet FPS must be positive")
    if columns <= 0:
        raise RuntimeError("Contact-sheet columns must be positive")
    video = config.output_dir / f"{config.name}.mp4"
    metadata = verify_video(config, video, "final")
    duration = float(metadata["format"]["duration"])
    frame_count = max(1, math.ceil(duration * fps))
    rows = math.ceil(frame_count / columns)
    output = config.output_dir / "contact-sheet.png"
    ffmpeg = require_tool("ffmpeg")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-i",
            str(video),
            "-vf",
            f"fps={fps},scale=640:-1,tile={columns}x{rows}:padding=4:margin=4",
            "-frames:v",
            "1",
            "-update",
            "1",
            str(output),
        ],
        check=True,
    )
    print(f"CONTACT_SHEET={output} ({columns}x{rows}, {frame_count} samples)")


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"Required command not found: {name}")
    return path


if __name__ == "__main__":
    main()
