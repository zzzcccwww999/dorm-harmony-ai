"""加载项目根目录环境变量，保证本地启动和测试入口行为一致。"""

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


def load_project_env() -> bool:
    """只补充未设置的环境变量，避免覆盖 shell 中显式传入的配置。"""
    return load_dotenv(DEFAULT_ENV_FILE, override=False)
