from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from blender_animation.config import ConfigError, ProjectConfig
from scripts.render_project import default_preview_frames, expected_frame_names


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = REPO_ROOT / "examples" / "parcel-sorter" / "project.json"


class ProjectConfigTests(unittest.TestCase):
    def test_example_has_config_derived_frame_count(self) -> None:
        config = ProjectConfig.load(EXAMPLE_CONFIG)

        self.assertEqual(config.timeline.frame_count, 150)
        self.assertEqual(config.timeline.duration_seconds, 5.0)
        self.assertEqual(default_preview_frames(config), [1, 76, 150])
        names = expected_frame_names(config)
        self.assertEqual(len(names), 150)
        self.assertIn("frame_0001.png", names)
        self.assertIn("frame_0150.png", names)

    def test_odd_dimensions_are_rejected_for_yuv420p(self) -> None:
        data = json.loads(EXAMPLE_CONFIG.read_text())
        data["render"]["final"]["width"] = 1279

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "project.json"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ConfigError, "must be even"):
                ProjectConfig.load(path)

    def test_unknown_engine_is_rejected_instead_of_silently_misconfigured(self) -> None:
        data = json.loads(EXAMPLE_CONFIG.read_text())
        data["render"]["engine"] = "CYCLES"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "project.json"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ConfigError, "only BLENDER_EEVEE"):
                ProjectConfig.load(path)


if __name__ == "__main__":
    unittest.main()
