"""Load and validate an animation project's JSON configuration."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when project.json does not satisfy the supported schema."""


@dataclass(frozen=True)
class RenderPreset:
    width: int
    height: int
    samples: int


@dataclass(frozen=True)
class Timeline:
    frame_start: int
    frame_end: int
    fps: int

    @property
    def frame_count(self) -> int:
        return self.frame_end - self.frame_start + 1

    @property
    def duration_seconds(self) -> float:
        return self.frame_count / self.fps


@dataclass(frozen=True)
class RenderSettings:
    engine: str
    view_transform: str
    look: str
    transparent_background: bool
    preview: RenderPreset
    final: RenderPreset


@dataclass(frozen=True)
class VideoSettings:
    crf: int
    preset: str
    pixel_format: str


@dataclass(frozen=True)
class ProjectConfig:
    schema_version: int
    name: str
    blender_version: tuple[int, int]
    timeline: Timeline
    render: RenderSettings
    video: VideoSettings
    path: Path

    @classmethod
    def load(cls, path: str | Path) -> "ProjectConfig":
        config_path = Path(path).resolve()
        try:
            data = json.loads(config_path.read_text())
        except FileNotFoundError as error:
            raise ConfigError(f"Project file not found: {config_path}") from error
        except json.JSONDecodeError as error:
            raise ConfigError(f"Invalid JSON in {config_path}: {error}") from error

        if not isinstance(data, dict):
            raise ConfigError("Project configuration must be a JSON object")

        schema_version = _integer(data, "schema_version")
        if schema_version != 1:
            raise ConfigError(f"Unsupported schema_version {schema_version}; expected 1")

        name = _string(data, "name")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ConfigError("name must contain lowercase letters, digits, and hyphens")

        version_value = data.get("blender_version")
        if (
            not isinstance(version_value, list)
            or len(version_value) != 2
            or any(type(part) is not int for part in version_value)
        ):
            raise ConfigError("blender_version must be [major, minor]")
        blender_version = (version_value[0], version_value[1])

        timeline_data = _object(data, "timeline")
        timeline = Timeline(
            frame_start=_integer(timeline_data, "frame_start"),
            frame_end=_integer(timeline_data, "frame_end"),
            fps=_integer(timeline_data, "fps"),
        )
        if timeline.frame_start < 0:
            raise ConfigError("timeline.frame_start must be nonnegative")
        if timeline.frame_end < timeline.frame_start:
            raise ConfigError("timeline.frame_end must be at least frame_start")
        if timeline.fps <= 0:
            raise ConfigError("timeline.fps must be positive")

        render_data = _object(data, "render")
        engine = _string(render_data, "engine")
        if engine != "BLENDER_EEVEE":
            raise ConfigError("render.engine currently supports only BLENDER_EEVEE")
        render = RenderSettings(
            engine=engine,
            view_transform=_string(render_data, "view_transform"),
            look=_string(render_data, "look"),
            transparent_background=_boolean(render_data, "transparent_background"),
            preview=_preset(render_data, "preview"),
            final=_preset(render_data, "final"),
        )

        video_data = _object(data, "video")
        video = VideoSettings(
            crf=_integer(video_data, "crf"),
            preset=_string(video_data, "preset"),
            pixel_format=_string(video_data, "pixel_format"),
        )
        if not 0 <= video.crf <= 51:
            raise ConfigError("video.crf must be between 0 and 51")
        if video.pixel_format != "yuv420p":
            raise ConfigError("video.pixel_format currently supports only yuv420p")

        return cls(
            schema_version=schema_version,
            name=name,
            blender_version=blender_version,
            timeline=timeline,
            render=render,
            video=video,
            path=config_path,
        )

    @property
    def project_dir(self) -> Path:
        return self.path.parent

    @property
    def output_dir(self) -> Path:
        return self.project_dir / "output"

    def preset(self, quality: str) -> RenderPreset:
        if quality == "preview":
            return self.render.preview
        if quality == "final":
            return self.render.final
        raise ConfigError(f"Unknown quality: {quality}")

    def public_summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "blender_version": list(self.blender_version),
            "engine": self.render.engine,
            "fps": self.timeline.fps,
            "frame_start": self.timeline.frame_start,
            "frame_end": self.timeline.frame_end,
            "frame_count": self.timeline.frame_count,
            "duration_seconds": self.timeline.duration_seconds,
            "preview": self.render.preview.__dict__,
            "final": self.render.final.__dict__,
        }


def _object(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be a JSON object")
    return value


def _string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{key} must be a nonempty string")
    return value


def _integer(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if type(value) is not int:
        raise ConfigError(f"{key} must be an integer")
    return value


def _boolean(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    if type(value) is not bool:
        raise ConfigError(f"{key} must be true or false")
    return value


def _preset(data: dict[str, Any], key: str) -> RenderPreset:
    preset_data = _object(data, key)
    preset = RenderPreset(
        width=_integer(preset_data, "width"),
        height=_integer(preset_data, "height"),
        samples=_integer(preset_data, "samples"),
    )
    if preset.width <= 0 or preset.height <= 0 or preset.samples <= 0:
        raise ConfigError(f"render.{key} dimensions and samples must be positive")
    if preset.width % 2 or preset.height % 2:
        raise ConfigError(f"render.{key} width and height must be even for yuv420p")
    return preset
