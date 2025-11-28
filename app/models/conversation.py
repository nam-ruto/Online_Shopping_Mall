from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Conversation:
    # DB: INT AUTO_INCREMENT
    id: Optional[int] = None
    customer_id: str = ""  # UUID (account.id)
    subject: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.customer_id:
            raise ValueError("customer_id must be provided")
        if not self.subject.strip():
            raise ValueError("subject must be non-empty")
        if len(self.subject) > 200:
            raise ValueError("subject must be at most 200 characters")


