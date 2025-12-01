import os
import sys
from typing import cast
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "")
APP_VERSION = cast(int, os.getenv("APP_VERSION"))
PROJECT_URL = os.getenv("PROJECT_URL", "") or ""
PROJECT_DIR = Path(__file__).parent.parent.parent
SECRETS_DIR = PROJECT_DIR / "secrets"

SECRET_KEY = os.getenv("SECRET_KEY")

# DB secrets
DB_URL = os.getenv("DB_URL")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_SYNC_URL = ("postgresql+psycopg2://"
               f"{DB_USERNAME}:{DB_PASSWORD}"
               "@"
               f"{DB_HOST}/{DB_NAME}")

# DB_SETTINGS
naming_convention = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


# JWT SETTINGS
ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_ALGORITHM = "RS256"

PRIVATE_KEY_PATH = SECRETS_DIR / "private.pem"
PUBLIC_KEY_PATH = SECRETS_DIR / "public.pem"


def load_key(path: Path, key_name: str) -> str:
    if not path.exists():
        print(f"ERROR: {key_name} not found at {path}")
        print("Please make sure your secrets are "
              "in place before running the app.")
        sys.exit(1)
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"ERROR: Failed to read {key_name} "
              f"at {path}: {e}")
        sys.exit(1)


PRIVATE_KEY = load_key(PRIVATE_KEY_PATH, "Private key")
PUBLIC_KEY = load_key(PUBLIC_KEY_PATH, "Public key")

BROKER_URL = os.getenv("BROKER_URL")
BROKER_MAX_CONNECTIONS = int(os.getenv("BROKER_MAX_CONNECTIONS", 1))

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")


MEDIA_DIR = PROJECT_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

MEDIA_PRODUCTS = MEDIA_DIR / "products"
MEDIA_PRODUCTS.mkdir(parents=True, exist_ok=True)