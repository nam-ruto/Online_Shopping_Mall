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
