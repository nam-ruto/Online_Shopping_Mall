from dataclasses import dataclass
from typing import Optional
import random
import string
from datetime import datetime, timedelta

from app.models import Account, Role
from app.services.account_service import AccountService
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

    # Registration method
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
        if AccountService.get_by_username(user_name):
            return AuthResult(False, "Username already exists")
        if AccountService.get_by_email(email):
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
        AccountService.create_account(account)
        return AuthResult(True, "Registration successful", account)

    # Login method
    def login(self, user_name: str, password: str) -> AuthResult:
        user_name = ensure_non_empty(user_name, "user_name")
        password = ensure_non_empty(password, "password")
        account = AccountService.get_by_username(user_name)
        if account is None:
            return AuthResult(False, "Invalid username or password")
        if not verify_password(password, account.salt, account.password):
            return AuthResult(False, "Invalid username or password")
        return AuthResult(True, "Login successful", account)
    
    # Password reset initiation: send token to email
    def password_reset_initiate(self, email: str) -> AuthResult:
        email = ensure_email(email)
        account = AccountService.get_by_email(email)
        if account is None:
            return AuthResult(False, "Email not found")
        
        token = self._generate_reset_token()
        expiration = self._calculate_token_expiration()
        account.password_reset_token = token
        account.password_reset_token_expiration = expiration
        AccountService.update_account(account)

        # In a real application, send the token via email here
        # For this example, we just return it in the message
        return AuthResult(True, f"Password reset initiated for the account belonging to {email}.\nThe code received will expire in 10 minutes.\n(token: {token})")
    
    # Password reset verification: check token validity
    def password_reset_verify(self, email: str, token: str) -> AuthResult:
        email = ensure_email(email)
        token = ensure_non_empty(token, "token")
        account = AccountService.get_by_email(email)
        if account is None:
            return AuthResult(False, "Email not found")
        if account.password_reset_token != token:
            return AuthResult(False, "Invalid reset token")
        if self._is_token_expired(account.password_reset_token_expiration):
            return AuthResult(False, "Reset token has expired")
        
        # Token is valid
        return AuthResult(True, "Password reset token verified")
    
    # Complete password reset
    def reset_password(self, email: str, new_password: str) -> AuthResult:
        email = ensure_email(email)
        new_password = ensure_non_empty(new_password, "new_password")
        account = AccountService.get_by_email(email)
        if account is None:
            return AuthResult(False, "Email not found")
        
        pwd_hash, salt = make_password_hash(new_password)
        account.password = pwd_hash
        account.salt = salt
        # Clear reset token and expiration
        account.password_reset_token = None
        account.password_reset_token_expiration = None
        AccountService.update_account(account)
        
        return AuthResult(True, "Password has been reset successfully")
    
    # Helper methods for token generation and expiration
    def _generate_reset_token(self) -> str:
        return ''.join(random.choices(string.digits, k=6))  # 6-digit numeric token
    
    def _calculate_token_expiration(self):
        return datetime.utcnow() + timedelta(minutes=10)
    
    def _is_token_expired(self, expiration_time) -> bool:
        return datetime.utcnow() > expiration_time

