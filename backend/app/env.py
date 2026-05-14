from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


def load_project_env() -> bool:
    return load_dotenv(DEFAULT_ENV_FILE, override=False)
