from __future__ import annotations

from typing import List

from app.models import Message, MessageRole
from . import base


def _row_to_message(row: dict) -> Message:
    return Message(
        id=row["id"],
        conversation_id=row["conversation_id"],
        user_id=row["user_id"],
        role=MessageRole(row["role"]),
        content=row["content"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        is_read=bool(row["is_read"]),
    )


class MessageRepository:
    TABLE = "message"

    @staticmethod
    def create(conversation_id: int, user_id: str, role: MessageRole, content: str) -> int:
        sql = f"INSERT INTO {MessageRepository.TABLE} (conversation_id, user_id, role, content) VALUES (%s, %s, %s, %s)"
        new_id = base.execute(sql, (conversation_id, user_id, role.value, content))
        return int(new_id)

    @staticmethod
    def list_by_conversation(conversation_id: int) -> List[Message]:
        rows = base.fetch_all(
            f"SELECT * FROM {MessageRepository.TABLE} WHERE conversation_id=%s ORDER BY created_at ASC",
            (conversation_id,),
        )
        return [_row_to_message(r) for r in rows]

    @staticmethod
    def list_since(conversation_id: int, after_id: int) -> List[Message]:
        rows = base.fetch_all(
            f"SELECT * FROM {MessageRepository.TABLE} WHERE conversation_id=%s AND id>%s ORDER BY id ASC",
            (conversation_id, after_id),
        )
        return [_row_to_message(r) for r in rows]

    @staticmethod
    def list_unread_conversation_summaries() -> list[dict]:
        sql = (
            "SELECT DISTINCT c.id AS id, c.subject AS subject "
            "FROM message m "
            "JOIN conversation c ON c.id = m.conversation_id "
            "WHERE m.role=%s AND m.is_read=FALSE "
            "ORDER BY c.id ASC"
        )
        rows = base.fetch_all(sql, (MessageRole.CUSTOMER.value,))
        return rows

    @staticmethod
    def mark_conversation_read(conversation_id: int) -> None:
        sql = (
            f"UPDATE {MessageRepository.TABLE} "
            "SET is_read=TRUE "
            "WHERE conversation_id=%s AND role=%s AND is_read=FALSE"
        )
        base.execute(sql, (conversation_id, MessageRole.CUSTOMER.value))

    @staticmethod
    def update_partial(msg_id: int, data: dict) -> None:
        """Update only the provided non-None fields for a message record."""
        base.update(MessageRepository.TABLE, msg_id, data)


