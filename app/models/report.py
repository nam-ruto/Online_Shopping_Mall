from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from .enums import ReportType
from .report_content import ReportContent


@dataclass(slots=True)
class Report:
    # DB: INT AUTO_INCREMENT
    id: Optional[int] = None
    type: ReportType = ReportType.DAILY
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = field(default_factory=datetime.utcnow)
    created_date: datetime = field(default_factory=datetime.utcnow)
    sold_quantity: int = 0
    total_revenue: Decimal = field(default_factory=lambda: Decimal("0.00"))

    # Domain convenience (not required by DB schema)
    contents: List[ReportContent] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.type, ReportType):
            raise ValueError("type must be an instance of ReportType enum")
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be earlier than start_date")
        if isinstance(self.total_revenue, (int, float, str)):
            self.total_revenue = Decimal(str(self.total_revenue))
        if self.total_revenue < Decimal("0"):
            raise ValueError("total_revenue must be non-negative")
        if self.sold_quantity < 0:
            raise ValueError("sold_quantity must be >= 0")

    def add_content(self, content: ReportContent) -> None:
        self.contents.append(content)
        self.sold_quantity += content.item_sold
        self.total_revenue = (self.total_revenue + content.sub_total).quantize(Decimal("0.01"))


