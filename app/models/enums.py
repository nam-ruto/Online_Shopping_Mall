from enum import Enum


class Role(str, Enum):
    CUSTOMER = "Customer"
    STAFF = "Staff"
    CEO = "CEO"


class OrderStatus(str, Enum):
    IN_CART = "In Cart"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    REFUNDED = "Refunded"


class PaymentMethod(str, Enum):
    CREDIT = "Credit"
    DEBIT = "Debit"


class ReportType(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


class MessageRole(str, Enum):
    CUSTOMER = "Customer"
    STAFF = "Staff"
    SYSTEM = "System"


