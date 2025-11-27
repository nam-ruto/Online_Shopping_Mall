from __future__ import annotations

from typing import List, Optional

from app.models import Conversation
from . import base


def _row_to_conversation(row: dict) -> Conversation:
    return Conversation(
        id=row["id"],
        customer_id=row["customer_id"],
        subject=row["subject"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class ConversationRepository:
    TABLE = "conversation"

    @staticmethod
    def create(customer_id: str, subject: str) -> int:
        sql = f"INSERT INTO {ConversationRepository.TABLE} (customer_id, subject) VALUES (%s, %s)"
        new_id = base.execute(sql, (customer_id, subject))
        return int(new_id)

    @staticmethod
    def get(conversation_id: int) -> Optional[Conversation]:
        row = base.fetch_one(f"SELECT * FROM {ConversationRepository.TABLE} WHERE id=%s", (conversation_id,))
        return _row_to_conversation(row) if row else None

    @staticmethod
    def list_by_customer(customer_id: str) -> List[Conversation]:
        rows = base.fetch_all(
            f"SELECT * FROM {ConversationRepository.TABLE} WHERE customer_id=%s ORDER BY updated_at DESC",
            (customer_id,),
        )
        return [_row_to_conversation(r) for r in rows]

    @staticmethod
    def list_all() -> List[Conversation]:
        rows = base.fetch_all(
            f"SELECT * FROM {ConversationRepository.TABLE} ORDER BY updated_at DESC",
            (),
        )
        return [_row_to_conversation(r) for r in rows]


