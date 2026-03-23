from __future__ import annotations

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# --- 설정값 ---
MARIADB_ENGINE = "django.db.backends.mysql"
MARIADB_CHARSET = "utf8mb4"
DEFAULT_DB_HOST = "127.0.0.1"
DEFAULT_DB_PORT = "3306"
DEFAULT_CONN_MAX_AGE = 60

SERVICE_DB_DEFAULT_NAMES = {
    "default": "autoe_orchestration",
    "vehicle": "autoe_vehicle",
    "zone": "autoe_zone",
    "parking_command": "autoe_parking_command",
    "parking_query": "autoe_parking_query",
}

SERVICE_DB_ENV_PREFIXES = {
    "default": "ORCHESTRATION",
    "vehicle": "VEHICLE",
    "zone": "ZONE",
    "parking_command": "PARKING_COMMAND",
    "parking_query": "PARKING_QUERY",
}

SERVICE_DB_FILENAMES = {
    "default": "orchestration.sqlite3",
    "vehicle": "vehicle.sqlite3",
    "zone": "zone.sqlite3",
    "parking_command": "parking_command.sqlite3",
    "parking_query": "parking_query.sqlite3",
}

# --- 도구 함수 ---

def build_sqlite_database(*, name: str) -> dict:
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": name,
    }

def build_mariadb_database(
    *,
    name: str,
    host: str,
    port: str,
    user: str,
    password: str,
    conn_max_age: int = DEFAULT_CONN_MAX_AGE,
) -> dict:
    return {
        "ENGINE": MARIADB_ENGINE,
        "NAME": name,
        "HOST": host,
        "PORT": str(port),
        "USER": user,
        "PASSWORD": password,
        "CONN_MAX_AGE": conn_max_age,
        "OPTIONS": {"charset": MARIADB_CHARSET},
    }

def build_service_mariadb_database(*, alias: str) -> dict:
    """특정 서비스의 환경변수를 읽어 MariaDB 설정을 반환합니다."""
    default_name = SERVICE_DB_DEFAULT_NAMES[alias]
    env_prefix = SERVICE_DB_ENV_PREFIXES[alias]
    
    # 필수 환경변수 체크
    host = os.getenv(f"{env_prefix}_DB_HOST")
    user = os.getenv(f"{env_prefix}_DB_USER")
    password = os.getenv(f"{env_prefix}_DB_PASSWORD")
    
    if not all([host, user, password]):
        raise ImproperlyConfigured(f"MariaDB env vars missing for {alias} (HOST, USER, or PASSWORD)")

    return build_mariadb_database(
        name=os.getenv(f"{env_prefix}_DB_NAME", default_name),
        host=host,
        port=os.getenv(f"{env_prefix}_DB_PORT", DEFAULT_DB_PORT),
        user=user,
        password=password,
    )

# --- 메인 함수 (이걸 수정했습니다) ---

def build_service_mariadb_databases() -> dict[str, dict]:
    """전체 서비스를 MariaDB로 강제 설정할 때 사용"""
    return {
        alias: build_service_mariadb_database(alias=alias)
        for alias in SERVICE_DB_DEFAULT_NAMES
    }

def build_service_databases(*, base_dir: Path) -> dict[str, dict]:
    """
    K8s 환경변수가 있으면 MariaDB, 없으면 SQLite를 자동으로 선택합니다.
    """
    databases: dict[str, dict] = {}
    
    for alias in SERVICE_DB_DEFAULT_NAMES.keys():
        prefix = SERVICE_DB_ENV_PREFIXES[alias]
        
        # 해당 서비스의 DB_HOST가 설정되어 있는지 확인
        if os.getenv(f"{prefix}_DB_HOST"):
            try:
                databases[alias] = build_service_mariadb_database(alias=alias)
                continue # 성공하면 다음 서비스로
            except ImproperlyConfigured:
                pass # 실패하면 아래 SQLite로 이동
        
        # 환경변수가 없으면 SQLite 사용
        filename = SERVICE_DB_FILENAMES.get(alias, f"{alias}.sqlite3")
        databases[alias] = build_sqlite_database(name=str(base_dir / filename))
        
    return databases
