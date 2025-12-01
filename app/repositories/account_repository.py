from __future__ import annotations

from typing import Optional

from app.models import Account, Role
from . import base


def _row_to_account(row: dict) -> Account:
    return Account(
        id=row["id"],
        user_name=row["user_name"],
        password=row["password"],
        salt=row["salt"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        role=Role(row["role"]),
        email=row["email"],
        country=row.get("country"),
        state=row.get("state"),
        city=row.get("city"),
        address_line=row.get("address_line"),
        zip_code=row.get("zip_code"),
        phone=row.get("phone"),
        password_reset_token=row.get("password_reset_token"),
        password_reset_token_expiration=row.get("password_reset_token_expiration"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class AccountRepository:
    TABLE = "account"

    @staticmethod
    def create(account: Account) -> None:
        # Insert only columns present in schema
        base.insert_from_dataclass(
            AccountRepository.TABLE,
            account,
            include={
                "id",
                "user_name",
                "password",
                "salt",
                "first_name",
                "last_name",
                "role",
                "email",
                "country",
                "state",
                "city",
                "address_line",
                "zip_code",
                "phone",
                "password_reset_token",
                "password_reset_token_expiration",
                "created_at",
                "updated_at",
            },
        )

    @staticmethod
    def get_by_username(user_name: str) -> Optional[Account]:
        row = base.fetch_one(
            f"SELECT * FROM {AccountRepository.TABLE} WHERE user_name=%s",
            (user_name,),
        )
        return _row_to_account(row) if row else None

    @staticmethod
    def get_by_email(email: str) -> Optional[Account]:
        row = base.fetch_one(
            f"SELECT * FROM {AccountRepository.TABLE} WHERE email=%s",
            (email,),
        )
        return _row_to_account(row) if row else None

    @staticmethod
    def get_by_id(acc_id: str) -> Optional[Account]:
        row = base.fetch_one(
            f"SELECT * FROM {AccountRepository.TABLE} WHERE id=%s",
            (acc_id,),
        )
        return _row_to_account(row) if row else None

    @staticmethod
    def get_by_name_or_id(first_name: str | None, last_name: str | None, id: str | None) -> Optional[list[Account]]:
        if first_name is None and last_name is None and id is None:
            return None

        sql = f"SELECT * FROM {AccountRepository.TABLE} WHERE ("

        if first_name is not None:
            sql += f"first_name LIKE '%{first_name}%'"

        if last_name is not None:
            if first_name is not None:
                sql += f" OR last_name LIKE '%{last_name}%'"
            else:
                sql += f"last_name LIKE '%{last_name}%'"

        if id is not None:
            if first_name is not None or last_name is not None:
                sql += f" OR id LIKE '%{id}%'"
            else:
                sql += f"id LIKE '%{id}%'"

        sql += f") AND role = \"Customer\""

        rows = base.fetch_all(sql)
        return [_row_to_account(row) for row in rows] if rows else None

    @staticmethod
    def update_address(
        acc_id: str,
        country: Optional[str],
        state: Optional[str],
        city: Optional[str],
        address_line: Optional[str],
        zip_code: Optional[str],
        phone: Optional[str],
    ) -> None:
        sql = (
            f"UPDATE {AccountRepository.TABLE} SET "
            "country=%s, state=%s, city=%s, address_line=%s, zip_code=%s, phone=%s "
            "WHERE id=%s"
        )
        base.execute(sql, (country, state, city, address_line, zip_code, phone, acc_id))

    @staticmethod
    def update_basic(
        acc_id: str,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
    ) -> None:
        sql = (
            f"UPDATE {AccountRepository.TABLE} SET "
            "first_name=%s, last_name=%s, email=%s "
            "WHERE id=%s"
        )
        base.execute(sql, (first_name, last_name, email, acc_id))

    @staticmethod
    def update(account: Account) -> None:
        sql = (
            f"UPDATE {AccountRepository.TABLE} SET "
            "user_name=%s, password=%s, salt=%s, first_name=%s, last_name=%s, role=%s, "
            "email=%s, country=%s, state=%s, city=%s, address_line=%s, zip_code=%s, phone=%s, "
            "password_reset_token=%s, password_reset_token_expiration=%s "
            "WHERE id=%s"
        )
        base.execute(
            sql,
            (
                account.user_name,
                account.password,
                account.salt,
                account.first_name,
                account.last_name,
                account.role.value,
                account.email,
                account.country,
                account.state,
                account.city,
                account.address_line,
                account.zip_code,
                account.phone,
                account.password_reset_token,
                account.password_reset_token_expiration,
                account.id,
            ),
        )
