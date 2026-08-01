"""Load and expose config.yaml as a plain dict, resolved relative to the
project root so scripts work no matter what directory they're run from."""

from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg


def resolve_path(relative_path: str) -> Path:
    """Turn a config-relative path (e.g. 'data/raw') into an absolute Path."""
    return PROJECT_ROOT / relative_path


CONFIG = load_config()
