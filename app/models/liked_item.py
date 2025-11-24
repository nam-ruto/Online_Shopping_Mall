from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class LikedItem:
    # DB: INT AUTO_INCREMENT
    id: Optional[int] = None
    customer_id: str = ""  # UUID (account.id)
    item_id: int = 0       # item.id

    def __post_init__(self) -> None:
        if not self.customer_id:
            raise ValueError("customer_id must be provided")
        if self.item_id <= 0:
            raise ValueError("item_id must be a positive integer")


