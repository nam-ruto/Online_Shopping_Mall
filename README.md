## Online Shopping Mall

## Project layout
Proposed project layout – changes can be made during development
```
├── app/
│   ├── __init__.py
│   ├── __main__.py                  # allows: python -m app
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py                  # console menu & routing
│   │   ├── customer_cli.py          # customer flows (cart, pay, like, message)
│   │   ├── staff_cli.py             # staff flows (inventory, CRUD items, reply)
│   │   └── ceo_cli.py               # CEO flows (view daily/monthly reports)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # DB URL, email config, report times
│   ├── db/
│   │   ├── __init__.py
│   │   └──connection.py             # DB connection factory
│   ├── models/                      # pure OOP entities (no DB)
│   │   ├── __init__.py
│   │   ├── enums.py                 # Roles, OrderStatus, ReportType, PaymentMethod
│   │   ├── account.py
│   │   ├── item.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── message.py
│   │   ├── report.py
│   │   ├── report_content.py
│   │   └── liked_item.py
│   ├── repositories/                # DB access (CRUD, queries) per aggregate
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── account_repository.py
│   │   ├── item_repository.py
│   │   ├── order_repository.py
│   │   ├── message_repository.py
│   │   ├── report_repository.py
│   │   └── liked_item_repository.py
│   ├── services/                    # business logic/use-cases
│   │   ├── __init__.py
│   │   ├── auth_service.py          # register/login, password hashing+salt
│   │   ├── item_service.py          # list/sort by likes, CRUD (staff)
│   │   ├── cart_service.py          # add/remove; prevent add when stock=0
│   │   ├── order_service.py         # checkout, create order & order_items
│   │   ├── payment_service.py       # simulate credit/debit, produce receipt
│   │   ├── email_service.py         # send receipt (mock)
│   │   ├── messaging_service.py     # customer-staff messages, unread handling
│   │   ├── like_service.py          # like/unlike, maintain like_count
│   │   └── report_service.py        # daily & monthly report generation
│   └── utils/
│       ├── __init__.py
│       ├── hashing.py               # salt + hash helpers
│       ├── validators.py
│       └── scheduling.py            # schedule daily 21:00 and month-end jobs
├── scripts/
│   ├── run_console.sh               # runs python -m app
│   └── init_db.sh                   # apply schema/sql/creation.sql
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   └── test_sample.py
│   └── integration/
│       └── test_end_to_end.py
├── schema/                          # (already exists; keep as source of truth)
│   ├── init/
│   ├── mock_data/
│   └── sql/
│       └── creation.sql
├── .env.example                     # DB creds, EMAIL_FROM, REPORT_TIME=21:00
├── requirements.txt                 # deps (e.g., PyMySQL, passlib, python-dotenv, schedule)
└── README.md
```


## Environment variables
1. Create a `.env` at the repository root (next to `.env.example`). Supported variables:
- `HOST`: Database host (default `127.0.0.1`)
- `PORT`: Database port (default `3306`)
- `DATABASE`: Database name to connect to (must already exist)
- `USER`: Database user (default `root`)
- `PASSWORD`: Database user password

    Notes:
    - The Python scripts read `.env` automatically (via `python-dotenv`).
    - The schema runner connects to the database specified by `DATABASE`. Ensure the database exists.

## Quick start
1) Create and activate a virtual environment
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    ```
    Windows (CMD):
    ```cmd
    python -m venv .venv
    .\.venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    ```
    Windows (PowerShell):
    ```powershell
    python -m venv .venv
    . .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    ```

2) Install required Python packages
    ```bash
    pip install -r requirements.txt
    ```

3) Create and fill your `.env`
    ```bash
    HOST=localhost
    PORT=3306
    DATABASE=shopping_mall
    USER=root
    PASSWORD=your_password
    ```

4) Create the (empty) database in MySQL (if not already created)

5) Create tables (choose ONE method)
- Option A — run the SQL directly:
  ```bash
  mysql -h "$HOST" -P "$PORT" -u "$USER" -D "$DATABASE" -p < schema/sql/creation.sql
  ```
  Windows (CMD):
  ```cmd
  mysql -h "%HOST%" -P "%PORT%" -u "%USER%" -D "%DATABASE%" -p < schema\sql\creation.sql
  ```
  Windows (PowerShell) — using -e with source:
  ```powershell
  mysql -h $env:HOST -P $env:PORT -u $env:USER -D $env:DATABASE -p -e "source schema/sql/creation.sql"
  ```
- Option B — use the Python helper:
  ```bash
  cd schema/init
  python creation.py
  ```

6) Seed mock data
- Option A - run the SQL directly:
    ```bash
    mysql -h "$HOST" -P "$PORT" -u "$USER" -D "$DATABASE" -p < schema/sql/mock_data.sql
    ```
    Windows (CMD):
    ```cmd
    mysql -h "%HOST%" -P "%PORT%" -u "%USER%" -D "%DATABASE%" -p < schema\sql\mock_data.sql
    ```
    Windows (PowerShell) — using -e with source:
    ```powershell
    mysql -h $env:HOST -P $env:PORT -u $env:USER -D $env:DATABASE -p -e "source schema/sql/mock_data.sql"
    ```
- Option B - use the Python helper:
    ```bash
    cd schema/init
    python mock_data.py
    ```


## Notes
- Account IDs are stored as `CHAR(36)` (UUID). CSVs in `schema/mock_data/` contain compatible values.
- The Python helpers use a buffered cursor and consume results to avoid pending result issues with multi-statement scripts.

