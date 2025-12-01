from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.models import Conversation, Message, MessageRole
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.utils.validators import ensure_length_max, ensure_non_empty


@dataclass
class ConversationSummary:
    id: int
    subject: str


class MessagingService:
    def start_conversation(self, customer_id: str, subject: str, content: str) -> int:
        customer_id = ensure_non_empty(customer_id, "customer_id")
        subject = ensure_length_max(ensure_non_empty(subject, "subject"), "subject", 200)
        content = ensure_non_empty(content, "content")
        conv_id = ConversationService().create(customer_id, subject)
        MessageService().create(conv_id, customer_id, MessageRole.CUSTOMER, content)
        return conv_id

    def customer_reply(self, customer_id: str, conversation_id: int, content: str) -> None:
        content = ensure_non_empty(content, "content")
        conv = ConversationService().get(conversation_id)
        if conv is None or conv.customer_id != customer_id:
            raise ValueError("Conversation not found or not owned by customer")
        MessageService().create(conversation_id, customer_id, MessageRole.CUSTOMER, content)

    def staff_reply(self, staff_id: str, conversation_id: int, content: str) -> None:
        content = ensure_non_empty(content, "content")
        conv = ConversationService().get(conversation_id)
        if conv is None:
            raise ValueError("Conversation not found")
        MessageService().create(conversation_id, staff_id, MessageRole.STAFF, content)
        # Mark customer messages as read upon staff reply
        MessageService().mark_conversation_read(conversation_id)

    def list_customer_conversations(self, customer_id: str) -> List[ConversationSummary]:
        convs = ConversationService().list_by_customer(customer_id)
        return [ConversationSummary(id=int(c.id or 0), subject=c.subject) for c in convs]

    def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        return MessageService().list_by_conversation(conversation_id)

    def list_unread_conversation_summaries(self) -> list[dict]:
        return MessageService().list_unread_conversation_summaries()

    def mark_conversation_read(self, conversation_id: int) -> None:
        MessageService().mark_conversation_read(conversation_id)

    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        return ConversationService().get(conversation_id)

    def list_all_conversations(self) -> List[ConversationSummary]:
        convs = ConversationService().list_all()
        return [ConversationSummary(id=int(c.id or 0), subject=c.subject) for c in convs]

    def get_since(self, conversation_id: int, after_id: int) -> List[Message]:
        return MessageService().list_since(conversation_id, after_id)


