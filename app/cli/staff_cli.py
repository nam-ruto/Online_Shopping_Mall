from __future__ import annotations
from decimal import Decimal

from app.cli import ui
from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService
from app.services.messaging_service import MessagingService


def staff_portal(account) -> None:
    while True:
        choice = ui.menu_select(
            "Staff Portal",
            "Choose an option",
            ["Manage Inventory", "Check Customer Information", "Customer Support", "Logout"],
        )
        if choice == "Manage Inventory":
            _staff_inventory_portal()
        elif choice == "Customer Support":
            _staff_messaging_portal(account)
        elif choice == "Logout":
            ui.ok("Log out successful!")
            return
        else:
            ui.banner(choice, f"{choice} is in development.")
            ui.wait_continue()

def _staff_inventory_portal() -> None:
    item_service = ItemService()
    while True:
        choice = ui.menu_select(
            "Inventory Portal",
            "Choose an action",
            ["List all items", "Add a new item", "Delete an existing item", "Update an existing item", "Quit"]
        )
        if choice == "List all items":
            items = ItemRepository.list()
            if not items:
                ui.err("Could not load item list, or there are no items in the list.")
            else:
                for item in items:
                    ui.ok(item)
            ui.wait_continue()
        elif choice == "Add a new item":
            _handle_new_item(item_service)
        elif choice == "Delete an existing item":
            _handle_delete_item(item_service)
        elif choice == "Quit":
            return
        else:
            ui.banner(choice, f"{choice} is in development.")
            ui.wait_continue()

def _handle_new_item(item_service: ItemService):
    ui.clear()
    ui.banner("Inventory", "Create a new item")

    name = ui.text("Name:")
    description = ui.text("(optional) Description:")
    category = ui.text("(optional) Category:")
    try:
        price = Decimal(ui.text("Price:"))
    except:
        ui.err("Invalid input: price must be a real number.")
        ui.wait_continue()
        return
    try:
        stock_quantity = int(ui.text("Stock quantity:"))
    except:
        ui.err("Invalid input: stock quantity must be a whole number.")
        ui.wait_continue()
        return

    result = item_service.create_item(name, price, stock_quantity, description, category)
    if result.success:
        ui.ok(result.message)
        ui.wait_continue()
    else:
        ui.err(result.message)
        ui.wait_continue()

def _handle_delete_item(item_service: ItemService):
    ui.clear()
    ui.banner("Inventory", "Delete an existing item")

    id = int(ui.text("Item ID:"))
    item = ItemRepository.get_by_id(id)
    if not item:
        ui.err("No item exists with that ID.")
        return

    ui.ok(item)

    cmd = ui.text("Are you sure you want to delete this item? Type 'confirm' to confirm.").strip().lower()
    if cmd != "confirm":
        ui.info("Not confirmed. Backing out.")
        return

    result = item_service.delete_item(id)
    if result.success:
        ui.ok(result.message)
        ui.wait_continue()
    else:
        ui.err(result.message)
        ui.wait_continue()


def _staff_messaging_portal(account) -> None:
    svc = MessagingService()
    while True:
        choice = ui.menu_select(
            "Staff Messaging",
            "Choose an action",
            ["Check unread messages", "View all conversations", "Quit"],
        )
        if choice == "Check unread messages":
            rows = svc.list_unread_conversation_summaries()
            if not rows:
                ui.banner("Unread", "No unread conversations.")
                ui.wait_continue()
            else:
                body = "\n".join([f"{r['id']} - {r['subject']}" for r in rows])
                ui.banner("Unread", body)
                cid_str = ui.text("Enter conversation ID to open (or blank to cancel):").strip()
                if cid_str and cid_str.isdigit():
                    cid = int(cid_str)
                    conv = svc.get_conversation(cid)
                    if conv is None:
                        ui.err("Conversation not found")
                        ui.wait_continue()
                    else:
                        _chat_repl(svc, account, cid, as_staff=True)
        elif choice == "View all conversations":
            convs = svc.list_all_conversations()
            if not convs:
                ui.banner("All Conversations", "No conversations.")
                ui.wait_continue()
            else:
                body = "\n".join([f"{c.id} - {c.subject}" for c in convs])
                ui.banner("All Conversations", body)
                cid_str = ui.text("Enter conversation ID to open (or blank to cancel):").strip()
                if cid_str and cid_str.isdigit():
                    cid = int(cid_str)
                    conv = svc.get_conversation(cid)
                    if conv is None:
                        ui.err("Conversation not found")
                        ui.wait_continue()
                    else:
                        _chat_repl(svc, account, cid, as_staff=True)
        elif choice == "Quit":
            return


def _chat_repl(svc: MessagingService, account, conversation_id: int, as_staff: bool) -> None:
    import threading
    import time

    state = {"watch": True, "interval": 1.0, "last_id": 0}

    def render_full():
        conv = svc.get_conversation(conversation_id)
        if conv is None:
            ui.err("Conversation not found")
            return False
        msgs = svc.get_conversation_messages(conversation_id)
        state["last_id"] = max((m.id or 0) for m in msgs) if msgs else 0
        lines = [f"Subject: {conv.subject}", ""]
        for m in msgs:
            who = "You" if m.user_id == account.id else m.role.value
            lines.append(f"[{who}] {m.content}")
        ui.banner(f"Conversation #{conversation_id}", "\n".join(lines))
        return True

    def watcher():
        while state["watch"]:
            try:
                new_msgs = svc.get_since(conversation_id, state["last_id"])
                if new_msgs:
                    for m in new_msgs:
                        state["last_id"] = max(state["last_id"], m.id or state["last_id"])
                    render_full()
                time.sleep(state["interval"])
            except Exception as e:
                ui.err(str(e))
                time.sleep(state["interval"])

    if not render_full():
        ui.wait_continue()
        return

    t = threading.Thread(target=watcher, daemon=True)
    t.start()

    while True:
        txt = ui.text("Type a message (/quit):").strip()
        if txt == "/quit":
            state["watch"] = False
            return
        if not txt:
            continue
        try:
            svc.staff_reply(account.id, conversation_id, txt)
            render_full()
        except Exception as e:
            ui.err(str(e))
            ui.wait_continue()
