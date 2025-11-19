## Online Shopping Mall

## Project layout
```
Add later...
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
  mysql -h "$HOST" -P "$PORT" -u "$USER" -p "$DATABASE" < schema/sql/creation.sql
  ```
- Option B — use the Python helper:
  ```bash
  cd schema/init
  python creation.py
  ```

6) Seed mock data (Python helper)
- Option A - run the SQL directly:
    ```bash
    mysql -h "$HOST" -P "$PORT" -u "$USER" -p "$NAME" < schema/sql/mock_data.sql
    ```
- Option B - use the Python helper:
    ```bash
    cd schema/init
    python mock_data.py
    ```


## Notes
- Account IDs are stored as `CHAR(36)` (UUID). CSVs in `schema/mock_data/` contain compatible values.
- The Python helpers use a buffered cursor and consume results to avoid pending result issues with multi-statement scripts.

