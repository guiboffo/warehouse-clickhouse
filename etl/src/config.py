import os
from dotenv import load_dotenv

load_dotenv()

def env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v == "":
        raise ValueError(f"Missing env var: {name}")
    return v

def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    return int(v) if v not in (None, "") else default

def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y")

USE_SSH_TUNNEL = env_bool("USE_SSH_TUNNEL", "0")

SSH_HOST = os.getenv("SSH_HOST", "")
SSH_PORT = env_int("SSH_PORT", 22)
SSH_USER = os.getenv("SSH_USER", "")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "")

DB_HOST = env("DB_HOST")
DB_PORT = env_int("DB_PORT", 3306)
DB_USER = env("DB_USER")
DB_PASSWORD = env("DB_PASSWORD")

CH_HOST = env("CH_HOST")
CH_PORT = env_int("CH_PORT", 8123)
CH_USER = env("CH_USER")
CH_PASSWORD = os.getenv("CH_PASSWORD", "")
CH_DB = env("CH_DB")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5000"))
PROJECTS_LAG_MINUTES = int(os.getenv("PROJECTS_LAG_MINUTES", "3"))

# Optional override for testing incremental
FORCE_LAST_RUN_AT = os.getenv("FORCE_LAST_RUN_AT", "").strip() or None
