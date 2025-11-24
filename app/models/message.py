from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .enums import MessageRole


@dataclass(slots=True)
class Message:
    # DB: INT AUTO_INCREMENT
    id: Optional[int] = None
    conversation_id: int = 0
    user_id: str = ""  # UUID (account.id)
    role: MessageRole = MessageRole.CUSTOMER
    content: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_read: bool = False

    def __post_init__(self) -> None:
        if self.conversation_id <= 0:
            raise ValueError("conversation_id must be a positive integer")
        if not self.user_id:
            raise ValueError("user_id must be provided (account uuid)")
        if not isinstance(self.role, MessageRole):
            raise ValueError("role must be an instance of MessageRole enum")
        if not self.content.strip():
            raise ValueError("content must be non-empty")

    def mark_read(self) -> None:
        if not self.is_read:
            self.is_read = True
            self.updated_at = datetime.utcnow()


