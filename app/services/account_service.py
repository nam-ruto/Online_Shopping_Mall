from __future__ import annotations

from typing import Optional

from app.models import Account
from app.repositories.account_repository import AccountRepository


class AccountService:
    @staticmethod
    def get_by_id(acc_id: str) -> Optional[Account]:
        return AccountRepository.get_by_id(acc_id)

    @staticmethod
    def get_by_name_or_id(first_name: str | None, last_name: str | None, id: str | None) -> Optional[list[Account]]:
        return AccountRepository.get_by_name_or_id(first_name, last_name, id)

    @staticmethod
    def get_by_username(user_name: str) -> Optional[Account]:
        return AccountRepository.get_by_username(user_name)

    @staticmethod
    def get_by_email(email: str) -> Optional[Account]:
        return AccountRepository.get_by_email(email)

    @staticmethod
    def create_account(account: Account) -> None:
        """Create a new account record in the database.

        AuthService remains responsible for hashing and security-related data,
        but AccountService centralizes persistence operations.
        """
        AccountRepository.create(account)

    @staticmethod
    def update_account(account: Account) -> None:
        AccountRepository.update(account)

    @staticmethod
    def update_partial(acc_id: str, data: dict | None = None, **kwargs) -> None:
        """Update only the provided non-None fields for an account record.

        Accepts either a single dict via `data` or keyword args. Keyword args will
        override keys in `data` if present. This is ergonomic for callers who want
        to update a single field (e.g. update_partial(acc_id, email='a@b.com')).
        """
        merged: dict = {}
        if data:
            merged.update(data)
        if kwargs:
            merged.update(kwargs)
        if not merged:
            return
        AccountRepository.update_partial(acc_id, merged)
