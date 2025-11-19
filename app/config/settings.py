import os
from dataclasses import dataclass
from typing import Dict, Any

from dotenv import load_dotenv


# Load .env from repo root if present; fallback to process env
load_dotenv(override=True)


def _env(key: str, *aliases: str, default: str = "") -> str:
    for k in (key, *aliases):
        v = os.getenv(k)
        if v:
            return v
    return default


@dataclass(frozen=True)
class Settings:
    # Match schema/init/creation.py variable conventions
    db_host: str = _env("DB_HOST", "HOST", default="127.0.0.1")
    db_port: int = int(_env("DB_PORT", "PORT", default="3306"))
    db_user: str = _env("DB_USER", "MYSQL_USER", "USER", default="root")
    db_password: str = _env("DB_PASSWORD", "MYSQL_PASSWORD", "PASSWORD", default="")
    db_name: str = _env("DB_NAME", "DATABASE", default="shopping_mall")

    def mysql_connector_config(self) -> Dict[str, Any]:
        return {
            "host": self.db_host,
            "port": self.db_port,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "autocommit": False,
            "consume_results": True,
            "charset": "utf8mb4",
        }


settings = Settings()


