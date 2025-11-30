from __future__ import annotations

from typing import Callable, Dict

from app.models import Role
from app.repositories.item_repository import ItemRepository
from app.services.auth_service import AuthService
from app.cli import ui
from app.cli.customer_cli import customer_portal
from app.cli.staff_cli import staff_portal
from app.cli.ceo_cli import ceo_portal


def _input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def main() -> None:
    auth = AuthService()
    while True:
        ui.clear()
        choice = ui.menu_select("Welcome", "Choose an option", ["Register", "Login", "Exit"])
        if choice == "Register":
            _handle_register(auth)
        elif choice == "Login":
            acc = _handle_login(auth)
            if acc:
                _route_by_role(acc)
                _idle_wait()
                return
        elif choice == "Exit":
            ui.ok("Goodbye!")
            return
        else:
            ui.err("Invalid choice.")
            ui.wait_continue()


def _handle_register(auth: AuthService):
    ui.clear()
    ui.banner("Register", "Create a new account")
    role_choice = ui.select("Which type of account are you registering for?", ["Customer", "Staff", "CEO"])
    role = Role.CUSTOMER if role_choice == "Customer" else Role.STAFF if role_choice == "Staff" else Role.CEO

    # For Staff/CEO, ask for registration code first and abort if invalid
    role_code = None
    if role in (Role.STAFF, Role.CEO):
        role_code = ui.text("Staff/CEO account requires a registration code. Please enter the code first before moving forward:")
        expected = (
            AuthService.STAFF_REG_CODE if role == Role.STAFF else AuthService.CEO_REG_CODE
        )
        if role_code != expected:
            ui.err("Invalid registration code. Please try again!")
            ui.wait_continue()
            return

    user_name = ui.text("Username:")
    password = ui.password("Password:")
    password2 = ui.password("Retype password:")
    if password != password2:
        ui.err("Passwords do not match. Please try again!")
        ui.wait_continue()
        return
    first_name = ui.text("First name:")
    last_name = ui.text("Last name:")
    email = ui.text("Email:")
    result = auth.register(user_name, password, first_name, last_name, email, role, role_code)
    if result.success:
        ui.ok(result.message)
        ui.wait_continue()
    else:
        ui.err(result.message)
        ui.wait_continue()


def _handle_login(auth: AuthService):
    ui.clear()
    ui.banner("Login", "Enter your credentials")
    user_name = ui.text("Username:")
    password = ui.password("Password:")
    result = auth.login(user_name, password)
    if result.success:
        ui.ok(result.message)
    else:
        ui.err(result.message)
        ui.wait_continue()
    return result.account


def _route_by_role(account) -> None:
    if account.role == Role.CUSTOMER:
        customer_portal(account)
    elif account.role == Role.STAFF:
        staff_portal(account)
    elif account.role == Role.CEO:
        ceo_portal(account)
    else:
        ui.err("\n[Unknown role]")

def _idle_wait() -> None:
    while True:
        cmd = ui.text("Type q to quit app: ").strip().lower()
        if cmd == "q":
            ui.ok("Goodbye!")
            return
