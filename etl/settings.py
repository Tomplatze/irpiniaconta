"""Read private command settings without coupling Python jobs to the Node launcher."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def environment_value(name: str, root: Path = ROOT) -> str | None:
    """Prefer process settings and support the project's simple local dotenv assignments."""
    if os.environ.get(name):
        return os.environ[name]
    path = root / '.env'
    if path.is_file():
        for line in path.read_text().splitlines():
            key, separator, value = line.strip().partition('=')
            if separator and key.removeprefix('export ').strip() == name:
                return value.strip().strip('\"\'') or None
    return None
