#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"

exec python3 "$REPO_ROOT/scripts/render_project.py" "$PROJECT_DIR" "$@"
