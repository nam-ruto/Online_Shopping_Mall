from dataclasses import dataclass
from typing import Optional

from app.models import Account, Role
from app.repositories.account_repository import AccountRepository
from app.utils.hashing import make_password_hash, verify_password
from app.utils.validators import ensure_email, ensure_length_max, ensure_non_empty


@dataclass
class AuthResult:
    success: bool
    message: str
    account: Optional[Account] = None


class AuthService:
    # Hard-coded registration codes for privileged roles
    STAFF_REG_CODE = "STAFF_123"
    CEO_REG_CODE = "CEO_123"

    def register(
        self,
        user_name: str,
        password: str,
        first_name: str,
        last_name: str,
        email: str,
        role: Role = Role.CUSTOMER,
        role_code: Optional[str] = None,
    ) -> AuthResult:
        # Validate inputs
        user_name = ensure_length_max(ensure_non_empty(user_name, "user_name"), "user_name", 30)
        first_name = ensure_length_max(ensure_non_empty(first_name, "first_name"), "first_name", 50)
        last_name = ensure_length_max(ensure_non_empty(last_name, "last_name"), "last_name", 50)
        email = ensure_email(email)

        # Role gate for privileged registrations
        if role == Role.STAFF:
            if role_code != self.STAFF_REG_CODE:
                return AuthResult(False, "Invalid staff registration code")
        if role == Role.CEO:
            if role_code != self.CEO_REG_CODE:
                return AuthResult(False, "Invalid CEO registration code")

        # Uniqueness checks
        if AccountRepository.get_by_username(user_name):
            return AuthResult(False, "Username already exists")
        if AccountRepository.get_by_email(email):
            return AuthResult(False, "Email already exists")

        pwd_hash, salt = make_password_hash(password)

        account = Account(
            user_name=user_name,
            password=pwd_hash,
            salt=salt,
            first_name=first_name,
            last_name=last_name,
            role=role,
            email=email,
        )
        AccountRepository.create(account)
        return AuthResult(True, "Registration successful", account)

    def login(self, user_name: str, password: str) -> AuthResult:
        user_name = ensure_non_empty(user_name, "user_name")
        password = ensure_non_empty(password, "password")
        account = AccountRepository.get_by_username(user_name)
        if account is None:
            return AuthResult(False, "Invalid username or password")
        if not verify_password(password, account.salt, account.password):
            return AuthResult(False, "Invalid username or password")
        return AuthResult(True, "Login successful", account)


