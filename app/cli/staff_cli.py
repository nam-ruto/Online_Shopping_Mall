from __future__ import annotations
from decimal import Decimal

from app.cli import ui
from app.models.item import Item
from app.repositories.account_repository import AccountRepository
from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService
from app.services.messaging_service import MessagingService
from app.services.order_service import OrderService


def staff_portal(account) -> None:
    while True:
        choice = ui.menu_select(
            "Staff Portal",
            "Choose an option",
            ["Manage Inventory", "Check Customer Information", "Customer Support", "Logout"],
        )
        if choice == "Manage Inventory":
            _staff_inventory_portal()
        elif choice == "Check Customer Information":
            _staff_customer_info_portal()
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
        elif choice == "Update an existing item":
            _handle_update_item(item_service)
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

def _handle_update_item(item_service: ItemService):
    ui.clear()
    ui.banner("Inventory", "Update an existing item")

    try:
        id = int(ui.text(f"Order ID:"))
    except:
        ui.err("Invalid input: order ID must be a whole number.")
        ui.wait_continue()
        return
    item = ItemRepository.get_by_id(id)
    if not item:
        ui.err("No item exists with that ID.")
        return
    ui.ok(item)

    ui.info("Enter a blank input for fields you do not wish to change.")

    name = ui.text(f"Name [\"{item.name}\"]:")
    description = ui.text(f"Description [{f"\"{item.description}\"" if item.description else "none"}]:")
    category = ui.text(f"Category [{f"\"{item.category}\"" if item.category else "none"}]:")
    try:
        price = Decimal(ui.text(f"Price [{item.price}]:"))
    except:
        ui.err("Invalid input: price must be a real number.")
        ui.wait_continue()
        return
    try:
        stock_quantity = int(ui.text(f"Stock quantity [{item.stock_quantity}]:"))
    except:
        ui.err("Invalid input: stock quantity must be a whole number.")
        ui.wait_continue()
        return

    updated_item = Item(
        id=item.id,
        name=name if name != "" else item.name,
        description=description if description != "" else item.description,
        category=category if category != "" else item.category,
        price=price if price != 0 else item.price,
        stock_quantity=stock_quantity if stock_quantity != 0 else item.stock_quantity,
        like_count=item.like_count,
    )

    result = item_service.update_item(id, updated_item)
    if result.success:
        ui.ok(result.message)
        ui.wait_continue()
    else:
        ui.err(result.message)
        ui.wait_continue()

def _staff_customer_info_portal() -> None:
    while True:
        choice = ui.menu_select(
            "Customer Information",
            "Choose an action",
            ["Search customer", "Search order", "Quit"]
        )
        if choice == "Search customer":
            _handle_search_customer()
        elif choice == "Search order":
            _handle_search_order()
        elif choice == "Quit":
            return
        else:
            ui.banner(choice, f"{choice} is in development.")
            ui.wait_continue()

def _handle_search_customer() -> None:
    first_name = ui.text("(optional) First name:")
    last_name = ui.text("(optional) Last name:")
    id = ui.text(f"(optional) Customer ID:")

    rows = AccountRepository.get_by_name_or_id(first_name if first_name != "" else None, last_name if last_name != "" else None, id if id != "" else None)
    if rows:
        for row in rows:
            ui.ok(row)
    else:
        ui.err("No customers by that criteria were found.")
    ui.wait_continue()
    return

def _handle_search_order() -> None:
    order_service = OrderService()

    try:
        id = int(ui.text(f"Order ID:"))
    except:
        ui.err("Invalid input: order ID must be a whole number.")
        ui.wait_continue()
        return

    order = order_service.get_by_id(id)
    if order:
        ui.ok(order)
    else:
        ui.err("No order exists with that ID.")
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
