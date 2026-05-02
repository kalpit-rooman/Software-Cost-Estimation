"""
pytest configuration for the backend test suite.

Adds the backend/ directory to sys.path so all imports resolve
without needing an editable install.
"""
from __future__ import annotations

import sys
from pathlib import Path

# backend/ must be the first entry so local packages take priority.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
