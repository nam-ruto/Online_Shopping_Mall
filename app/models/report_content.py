from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass(slots=True)
class ReportContent:
    # DB: INT AUTO_INCREMENT
    id: Optional[int] = None
    report_id: int = 0
    item_id: int = 0
    item_sold: int = 0
    unit_price: Decimal = field(default_factory=lambda: Decimal("0.00"))
    sub_total: Decimal = field(default_factory=lambda: Decimal("0.00"))

    def __post_init__(self) -> None:
        if self.report_id <= 0:
            raise ValueError("report_id must be a positive integer")
        if self.item_id <= 0:
            raise ValueError("item_id must be a positive integer")
        if self.item_sold < 0:
            raise ValueError("item_sold must be >= 0")
        if isinstance(self.unit_price, (int, float, str)):
            self.unit_price = Decimal(str(self.unit_price))
        if isinstance(self.sub_total, (int, float, str)):
            self.sub_total = Decimal(str(self.sub_total))
        if self.unit_price < Decimal("0"):
            raise ValueError("unit_price must be non-negative")
        if self.sub_total < Decimal("0"):
            raise ValueError("sub_total must be non-negative")


