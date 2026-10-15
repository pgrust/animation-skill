#!/usr/bin/env python3
"""Create an opinionated parallel-pipeline project in projects/<name>."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "templates" / "parallel-pipeline"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a project from the opinionated parallel-pipeline starter"
    )
    parser.add_argument("name", help="Lowercase project slug")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.name):
        raise SystemExit("name must contain lowercase letters, digits, and hyphens")
    destination = (REPO_ROOT / "projects" / args.name).resolve()
    if destination.exists():
        raise SystemExit(f"destination already exists: {destination}")

    shutil.copytree(
        SOURCE,
        destination,
        ignore=shutil.ignore_patterns("output", "__pycache__", "*.pyc"),
    )
    config_path = destination / "project.json"
    config = json.loads(config_path.read_text())
    config["name"] = args.name
    config_path.write_text(json.dumps(config, indent=2) + "\n")

    display_name = args.name.replace("-", " ").upper()
    for filename in ("build.py", "README.md", "EVAL.md"):
        path = destination / filename
        content = path.read_text()
        content = content.replace("PARALLEL PIPELINE", display_name)
        content = content.replace("projects/parallel-pipeline", f"projects/{args.name}")
        path.write_text(content)
    print(destination)


if __name__ == "__main__":
    main()
