from __future__ import annotations

from typing import List, Optional

from app.models import Conversation
from app.repositories.conversation_repository import ConversationRepository


class ConversationService:
    def create(self, customer_id: str, subject: str) -> int:
        return ConversationRepository.create(customer_id, subject)

    def get(self, conversation_id: int) -> Optional[Conversation]:
        return ConversationRepository.get(conversation_id)

    def list_by_customer(self, customer_id: str) -> List[Conversation]:
        return ConversationRepository.list_by_customer(customer_id)

    def list_all(self) -> List[Conversation]:
        return ConversationRepository.list_all()

    def update_partial(self, conv_id: int, data: dict) -> None:
        ConversationRepository.update_partial(conv_id, data)
