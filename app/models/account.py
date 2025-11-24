from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

from .enums import Role


@dataclass(slots=True)
class Account:
    # DB: CHAR(36) UUID
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_name: str = ""
    password: str = ""  # expected to store a hashed password
    salt: bytes = b""
    first_name: str = ""
    last_name: str = ""
    role: Role = Role.CUSTOMER
    email: str = ""
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address_line: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.user_name.strip():
            raise ValueError("user_name must be non-empty")
        if not self.password:
            raise ValueError("password must be provided (store hashed value)")
        if not isinstance(self.salt, (bytes, bytearray)):
            raise ValueError("salt must be bytes")
        if not self.first_name.strip():
            raise ValueError("first_name must be non-empty")
        if not self.last_name.strip():
            raise ValueError("last_name must be non-empty")
        if "@" not in self.email or not self.email.strip():
            raise ValueError("email must be a valid, non-empty address")
        if not isinstance(self.role, Role):
            raise ValueError("role must be an instance of Role enum")


