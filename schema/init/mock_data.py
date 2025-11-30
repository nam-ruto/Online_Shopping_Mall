#!/usr/bin/env python3
import os
import sys
import csv
from pathlib import Path
from typing import List, Tuple, Dict
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

    data_dir = Path(__file__).parents[1] / "mock_data"
    return {
        "HOST": host,
        "PORT": port,
        "DATABASE": database,
        "USER": user,
        "PASSWORD": password,
        "data_dir": data_dir,
    }


def read_csv_rows(csv_path: Path) -> List[Dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def hex_to_bytes(hex_str: str) -> bytes:
    s = (hex_str or "").strip()
    if s.lower().startswith("0x"):
        s = s[2:]
    if s == "":
        return b""
    return bytes.fromhex(s)


def seed_from_csvs(host: str, port: int, database: str, user: str, password: str, data_dir: Path) -> None:
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
        cursor = connection.cursor()

        # 1) account
        account_rows = read_csv_rows(data_dir / "account.csv")
        account_values: List[Tuple] = []
        for r in account_rows:
            account_values.append((
                r["id"],
                r["user_name"],
                r["password"],
                hex_to_bytes(r["salt"]),
                r["first_name"],
                r["last_name"],
                r["role"],
                r["email"],
                r["country"] or None,
                r["state"] or None,
                r["city"] or None,
                r["address_line"] or None,
                r["zip_code"] or None,
                r["phone"] or None,
            ))
        cursor.executemany(
            "INSERT INTO account (id, user_name, password, salt, first_name, last_name, role, email, country, state, city, address_line, zip_code, phone) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            account_values,
        )

        # 2) item
        item_rows = read_csv_rows(data_dir / "item.csv")
        item_values: List[Tuple] = []
        for r in item_rows:
            item_values.append((
                int(r["id"]),
                r["name"],
                r["description"] or None,
                r["category"] or None,
                float(r["price"]),
                int(r["stock_quantity"]),
                int(r["like_count"]),
            ))
        cursor.executemany(
            "INSERT INTO item (id, name, description, category, price, stock_quantity, like_count) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            item_values,
        )

        # 3) order
        order_rows = read_csv_rows(data_dir / "order.csv")
        order_values: List[Tuple] = []
        for r in order_rows:
            order_values.append((
                int(r["id"]),
                r["customer_id"],
                int(r["transaction_id"]) if r["transaction_id"] else None,
                r["to_state"] or None,
                r["to_city"] or None,
                r["to_address_line"] or None,
                float(r["total_amount"]),
                r["order_date"],
                r["status"],
                r["payment_method"],
            ))
        cursor.executemany(
            "INSERT INTO `order` (id, customer_id, transaction_id, to_state, to_city, to_address_line, total_amount, order_date, status, payment_method) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            order_values,
        )

        # 4) order_item
        order_item_rows = read_csv_rows(data_dir / "order_item.csv")
        order_item_values: List[Tuple] = []
        for r in order_item_rows:
            order_item_values.append((
                int(r["id"]),
                int(r["order_id"]),
                int(r["item_id"]) if r["item_id"] else None,
                r["item_name"],
                r["item_description"] or None,
                r["item_category"] or None,
                int(r["quantity"]),
                float(r["unit_price"]),
                float(r["sub_total"]),
            ))
        cursor.executemany(
            "INSERT INTO order_item (id, order_id, item_id, item_name, item_description, item_category, quantity, unit_price, sub_total) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            order_item_values,
        )

        # 5) conversation
        conversation_rows = read_csv_rows(data_dir / "conversation.csv")
        conversation_values: List[Tuple] = []
        for r in conversation_rows:
            conversation_values.append((
                int(r["id"]),
                r["customer_id"],
                r["subject"],
            ))
        cursor.executemany(
            "INSERT INTO conversation (id, customer_id, subject) "
            "VALUES (%s,%s,%s)",
            conversation_values,
        )

        # 6) message
        message_rows = read_csv_rows(data_dir / "message.csv")
        message_values: List[Tuple] = []
        for r in message_rows:
            message_values.append((
                int(r["id"]),
                int(r["conversation_id"]),
                r["user_id"],
                r["role"],
                r["content"],
                int(r["is_read"]),
            ))
        cursor.executemany(
            "INSERT INTO message (id, conversation_id, user_id, role, content, is_read) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            message_values,
        )

        # 7) report
        report_rows = read_csv_rows(data_dir / "report.csv")
        report_values: List[Tuple] = []
        for r in report_rows:
            report_values.append((
                int(r["id"]),
                r["type"],
                r["start_date"],
                r["end_date"],
                int(r["sold_quantity"]),
                float(r["total_revenue"]),
            ))
        cursor.executemany(
            "INSERT INTO report (id, type, start_date, end_date, sold_quantity, total_revenue) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            report_values,
        )

        # 8) report_content
        rc_rows = read_csv_rows(data_dir / "report_content.csv")
        rc_values: List[Tuple] = []
        for r in rc_rows:
            rc_values.append((
                int(r["id"]),
                int(r["report_id"]),
                int(r["item_id"]),
                int(r["item_sold"]),
                float(r["unit_price"]),
                float(r["sub_total"]),
            ))
        cursor.executemany(
            "INSERT INTO report_content (id, report_id, item_id, item_sold, unit_price, sub_total) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            rc_values,
        )

        connection.commit()
        print("Mock data seeding completed successfully from CSV files.")
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
    print(f"Loading CSVs from: {cfg['data_dir']}")
    seed_from_csvs(cfg["HOST"], cfg["PORT"], cfg["DATABASE"], cfg["USER"], cfg["PASSWORD"], cfg["data_dir"])


if __name__ == "__main__":
    main()

