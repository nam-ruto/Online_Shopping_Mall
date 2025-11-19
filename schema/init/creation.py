#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from mysql.connector import errorcode, connect, Error
from dotenv import load_dotenv


def load_env_config() -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    env_path = repo_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)

    host = os.getenv("DB_HOST") or os.getenv("HOST") or "127.0.0.1"
    port_str = os.getenv("DB_PORT") or os.getenv("PORT") or "3306"
    try:
        port = int(port_str)
    except ValueError:
        port = 3306
    database = os.getenv("DB_NAME") or os.getenv("DATABASE") or ""
    user = os.getenv("DB_USER") or os.getenv("MYSQL_USER") or os.getenv("USER") or "root"
    password = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD") or os.getenv("PASSWORD") or ""

    creation_file = Path(__file__).parents[1] / "sql" / "creation.sql"
    return {
        "HOST": host,
        "PORT": port,
        "DATABASE": database,
        "USER": user,
        "PASSWORD": password,
        "creation_file": creation_file,
    }


def load_sql_file(sql_file_path: str) -> str:
    sql_path = Path(sql_file_path).expanduser().resolve()
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    return sql_path.read_text(encoding="utf-8")


def execute_sql_script(
    host: str, port: int, database: str, user: str, password: str, sql_script: str
) -> None:
    connection = None
    cursor = None
    try:
        connection = connect(
            host=host,
            port=port,
            user=user,
            database=database,
            password=password,
            autocommit=False,
            consume_results=True,
        )
        # Use buffered cursor to ensure all results are consumed immediately
        cursor = connection.cursor(buffered=True)

        statement_buffer = []
        in_block_comment = False
        for raw_line in sql_script.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if in_block_comment:
                if "*/" in line:
                    in_block_comment = False
                continue
            if line.startswith("/*"):
                if "*/" not in line:
                    in_block_comment = True
                continue
            if line.startswith("--") or line.startswith("#"):
                continue
            statement_buffer.append(raw_line)
            if line.endswith(";"):
                stmt = "\n".join(statement_buffer).rstrip().rstrip(";")
                if stmt:
                    cursor.execute(stmt)
                    if getattr(cursor, "with_rows", False):
                        try:
                            cursor.fetchall()
                        except Exception:
                            pass
                statement_buffer = []

        trailing = "\n".join(statement_buffer).strip()
        if trailing:
            cursor.execute(trailing)
            if getattr(cursor, "with_rows", False):
                try:
                    cursor.fetchall()
                except Exception:
                    pass

        try:
            cursor.close()
        except Exception:
            pass
        cursor = None

        # Ensure any pending results on the connection are consumed
        try:
            connection.consume_results()
        except Exception:
            pass

        connection.commit()
        print("Schema creation completed successfully.")
    except Error as err:
        if connection:
            try:
                connection.rollback()
            except Exception:
                pass
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            sys.stderr.write(f"Access denied: {err}\n")
        else:
            sys.stderr.write(f"MySQL error: {err}\n")
        sys.exit(2)
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if connection:
            try:
                connection.close()
            except Exception:
                pass


def main() -> None:
    cfg = load_env_config()
    creation_sql = load_sql_file(cfg["creation_file"])
    print(f"Executing creation SQL from: {cfg['creation_file']}")
    execute_sql_script(cfg["HOST"], cfg["PORT"], cfg["DATABASE"], cfg["USER"], cfg["PASSWORD"], creation_sql)


if __name__ == "__main__":
    main()


