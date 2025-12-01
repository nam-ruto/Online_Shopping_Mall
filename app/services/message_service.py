from __future__ import annotations

from typing import List

from app.models import Message, MessageRole
from app.repositories.message_repository import MessageRepository


class MessageService:
    def create(self, conversation_id: int, user_id: str, role: MessageRole, content: str) -> int:
        return MessageRepository.create(conversation_id, user_id, role, content)

    def list_by_conversation(self, conversation_id: int) -> List[Message]:
        return MessageRepository.list_by_conversation(conversation_id)

    def list_since(self, conversation_id: int, after_id: int) -> List[Message]:
        return MessageRepository.list_since(conversation_id, after_id)

    def list_unread_conversation_summaries(self) -> list[dict]:
        return MessageRepository.list_unread_conversation_summaries()

    def mark_conversation_read(self, conversation_id: int) -> None:
        MessageRepository.mark_conversation_read(conversation_id)

    def update_partial(self, msg_id: int, data: dict) -> None:
        MessageRepository.update_partial(msg_id, data)
