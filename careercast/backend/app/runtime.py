"""Writable state stays outside installed package/model assets."""
import os
from pathlib import Path

_source = Path(__file__).resolve().parents[1]
_default = _source if (_source / "requirements.txt").exists() else Path.home() / ".careercast"
RUNTIME_DIR = Path(os.getenv("CAREERCAST_DATA_DIR", str(_default))).expanduser().resolve()
