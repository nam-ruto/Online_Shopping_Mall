from __future__ import annotations

from app.models import Role, PaymentMethod
from app.cli import ui
from app.services.messaging_service import MessagingService
from app.repositories.browse_item_repository import BrowseItemRepository
from app.services.cart_service import CartService
from app.services.like_service import LikeService
from app.services.order_service import OrderService
from app.repositories.account_repository import AccountRepository
from app.utils.validators import ensure_length_max, ensure_non_empty, ensure_email
from rich.table import Table
from app.cli.ui import console
from app.repositories.item_repository import ItemRepository

_cart = CartService()
_likes = LikeService()
_orders = OrderService()


def customer_portal(account) -> None:
    while True:
        choice = ui.menu_select(
            "Customer Portal",
            "Choose an option",
            [
                "Browse Catalog (View Items)",
                "My Shopping Cart",
                "My Order",
                "My Liked Items",
                "Update Profile",
                "Message Support",
                "Logout",
            ],
        )
        if choice == "Browse Catalog (View Items)":
            _browse_catalog(account)
        elif choice == "My Shopping Cart":
            _shopping_cart(account)
        elif choice == "My Order":
            _my_orders(account)
        elif choice == "My Liked Items":
            _my_liked_items(account)
        elif choice == "Update Profile":
            _update_profile(account)
        elif choice == "Message Support":
            _customer_messaging_portal(account)
        elif choice == "Logout":
            ui.ok("Log out successful!")
            return
        else:
            ui.banner(choice, f"{choice} is in development.")
            ui.wait_continue()

def _browse_catalog(account) -> None:
    items = BrowseItemRepository.list_all_popular_first()
    table = Table(title="Catalog", show_lines=True)
    table.add_column("ID"); table.add_column("Name"); table.add_column("Category")
    table.add_column("Price"); table.add_column("Stock"); table.add_column("Likes")
    for it in items:
        table.add_row(str(it.id), it.name or "", it.category or "", f"${it.price}", str(it.stock_quantity), str(it.like_count))
    console.print(table)
    action = ui.select("Choose an action", ["Add items to cart", "Like items", "Back"])
    if action == "Add items to cart":
        while True:
            raw = ui.text("Item ID to add (or /quit):").strip()
            if raw == "/quit" or not raw:
                break
            if not raw.isdigit():
                ui.err("Please enter a valid numeric item ID.")
                continue
            iid = int(raw)
            if ItemRepository.get_by_id(iid) is None:
                ui.err(f"Item {iid} does not exist.")
                continue
            qty_raw = ui.text("Quantity:").strip()
            if not qty_raw.isdigit():
                ui.err("Please enter a valid numeric quantity.")
                continue
            qty = int(qty_raw)
            if qty <= 0:
                ui.err("Quantity must be greater than 0.")
                continue
            if qty > ItemRepository.get_by_id(iid).stock_quantity:
                ui.err(f"Item {iid} does not have enough stock.")
                continue
            _cart.add_item(account.id, iid, qty)
            ui.ok(f"Added item {iid} x{qty} to cart.")
        # ui.wait_continue()
    elif action == "Like items":
        while True:
            raw = ui.text("Item ID to like (or /quit):").strip()
            if raw == "/quit" or not raw:
                break
            if not raw.isdigit():
                ui.err("Please enter a valid numeric item ID.")
                continue
            iid = int(raw)
            if ItemRepository.get_by_id(iid) is None:
                ui.err(f"Item {iid} does not exist.")
                continue
            liked = _likes.like_items(account.id, [iid])
            if liked:
                ui.ok("Item liked.")
            else:
                ui.info("No change.")
        # ui.wait_continue()
    else:
        return

def _shopping_cart(account) -> None:
    while True:
        items = _cart.list_items(account.id)
        if not items:
            ui.banner("My Shopping Cart", "Your shopping cart is empty. Please browse the catalog and add some!")
            ui.wait_continue()
            return
        table = Table(title="My Shopping Cart", show_lines=True)
        table.add_column("ID"); table.add_column("Name"); table.add_column("Price"); table.add_column("Stock"); table.add_column("Qty")
        for it, qty in items:
            table.add_row(str(it.id), it.name or "", f"${it.price}", str(it.stock_quantity), str(qty))
        console.print(table)
        choice = ui.select("Choose an action", ["Remove item from cart", "Adjust item quantity", "Place an order", "Back"])
        if choice == "Remove item from cart":
            ids = _parse_ids(ui.text("Enter item ids to remove (e.g., 7,12):"))
            if not ids:
                ui.info("No items specified.")
            else:
                for iid in ids:
                    if ItemRepository.get_by_id(iid) is None:
                        ui.err(f"Item {iid} does not exist.")
                        continue
                    if iid not in _cart.get_quantities(account.id):
                        ui.err(f"Item {iid} is not currently in your cart.")
                        continue
                    if _cart.get_quantities(account.id).get(iid, 0) <= 0:
                        ui.err(f"Item {iid} is not in your cart.")
                        continue
                removed = _cart.remove_items(account.id, ids)
                ui.ok(f"Removed {removed} item(s) from cart.")
            # ui.wait_continue()
        elif choice == "Adjust item quantity":
            while True:
                raw = ui.text("Item ID to adjust (or /quit):").strip()
                if raw == "/quit" or not raw:
                    break
                if not raw.isdigit():
                    ui.err("Please enter a valid numeric item ID.")
                    continue
                iid = int(raw)
                if ItemRepository.get_by_id(iid) is None:
                    ui.err(f"Item {iid} does not exist.")
                    continue
                if iid not in _cart.get_quantities(account.id):
                    ui.err(f"Item {iid} is not currently in your cart.")
                    continue
                if _cart.get_quantities(account.id).get(iid, 0) <= 0:
                    ui.err(f"Item {iid} is not in your cart.")
                    continue
                qty_raw = ui.text("New quantity (0 to remove):").strip()
                if not qty_raw.isdigit():
                    ui.err("Please enter a valid non-negative quantity.")
                    continue
                qty = int(qty_raw)
                _cart.set_quantity(account.id, iid, qty)
                ui.ok("Quantity updated.")
            # ui.wait_continue()
        elif choice == "Place an order":
            ids = _parse_ids(ui.text("Which items do you want to place an order? (e.g., 7,12):"))
            if not ids:
                ui.err("No items selected")
                ui.wait_continue()
                continue
            # Build id->quantity map from cart for selected ids
            quantities = _cart.get_quantities(account.id)
            item_id_to_qty = {iid: quantities.get(iid, 0) for iid in ids if quantities.get(iid, 0) > 0}
            if not item_id_to_qty:
                ui.err("Selected items not found in cart.")
                ui.wait_continue()
                continue
            # Address confirmation/update
            acc = AccountRepository.get_by_id(account.id) or account
            _show_address(acc)
            # Check if any address exists
            has_any = any([acc.country, acc.state, acc.city, acc.address_line, acc.zip_code, acc.phone])
            if has_any:
                yn = ui.text("Modify shipping address? (Y/N):").strip().lower()
                if yn == "y":
                    acc = _prompt_address_update(acc)
            else:
                ui.info("You have not added your address yet, please enter yours:")
                acc = _prompt_address_update(acc)
            # Payment method
            method = ui.select("Payment method", ["Credit", "Debit"])
            card = ui.text("Enter card number (mock):")
            name = ui.text("Name on card:")
            confirm = ui.text("Confirm payment? (Y/N):").strip().lower()
            if confirm != "y":
                ui.info("Order cancelled.")
                ui.wait_continue()
                continue
            try:
                order_id = _orders.place_order(
                    customer_id=account.id,
                    item_id_to_quantity=item_id_to_qty,
                    to_state=acc.state,
                    to_city=acc.city,
                    to_address_line=acc.address_line,
                    payment_method=PaymentMethod.CREDIT if method == "Credit" else PaymentMethod.DEBIT,
                )
                _cart.clear_selected(account.id, ids)
                ui.ok(f"Order #{order_id} placed successfully.")
            except Exception as e:
                ui.err(str(e))
            ui.wait_continue()
        else:
            return

def _my_orders(account) -> None:
    rows = _orders.list_orders(account.id)
    if not rows:
        ui.banner("My Orders", "You have no orders yet.")
        ui.wait_continue()
        return
    table = Table(title="My Orders", show_lines=True)
    table.add_column("ID"); table.add_column("Date"); table.add_column("Total"); table.add_column("Status")
    for r in rows:
        table.add_row(str(r["id"]), r["order_date"].strftime("%Y-%m-%d %H:%M"), f"${r['total_amount']}", str(r["status"]))
    console.print(table)
    ui.wait_continue()

def _my_liked_items(account) -> None:
    rows = _likes.list_liked(account.id)
    if not rows:
        ui.banner("My Liked Items", "You have no liked items. Try liking some items from the catalog!")
        ui.wait_continue()
        return
    table = Table(title="My Liked Items", show_lines=True)
    table.add_column("Item ID"); table.add_column("Name"); table.add_column("Category"); table.add_column("Price")
    for r in rows:
        table.add_row(str(r["item_id"]), r["name"] or "", r["category"] or "", f"${r['price']}")
    console.print(table)
    ui.banner("Instructions", "Use '/remove' command to remove liked items. Example: /remove 2,23")
    cmd = ui.text("Enter command (or blank to go back):").strip()
    if not cmd:
        return
    if cmd.startswith("/remove"):
        ids = _parse_ids(cmd[len("/remove"):])
        for iid in ids:
            if ItemRepository.get_by_id(iid) is None:
                ui.err(f"Item {iid} does not exist.")
                continue
        removed = _likes.unlike_items(account.id, ids)
        if removed:
            ui.ok(f"Removed {removed} liked items.")
        else:
            ui.info("No change.")
        ui.wait_continue()
    else:
        ui.err("Unknown command")
        ui.wait_continue()

def _update_profile(account) -> None:
    # Display current info
    acc = AccountRepository.get_by_id(account.id) or account
    fields = [
        ("First Name", "first_name", acc.first_name),
        ("Last Name", "last_name", acc.last_name),
        ("Email", "email", acc.email),
        ("Country", "country", acc.country),
        ("State", "state", acc.state),
        ("City", "city", acc.city),
        ("Address Line", "address_line", acc.address_line),
        ("Zip Code", "zip_code", acc.zip_code),
        ("Phone", "phone", acc.phone),
    ]
    _print_profile_table(fields)
    while True:
        choices = [f[0] for f in fields] + ["Done"]
        choice = ui.select("Select a field to update", choices)
        if choice == "Done":
            return
        # find field key
        for label, key, value in fields:
            if label == choice:
                new_val = ui.text(f"Enter new value for {label}:")
                # apply update if address-related
                if key in {"country", "state", "city", "address_line", "zip_code", "phone"}:
                    AccountRepository.update_address(
                        acc.id,
                        country=new_val if key == "country" else acc.country,
                        state=new_val if key == "state" else acc.state,
                        city=new_val if key == "city" else acc.city,
                        address_line=new_val if key == "address_line" else acc.address_line,
                        zip_code=new_val if key == "zip_code" else acc.zip_code,
                        phone=new_val if key == "phone" else acc.phone,
                    )
                    # refresh
                    acc = AccountRepository.get_by_id(acc.id) or acc
                    fields = [
                        ("First Name", "first_name", acc.first_name),
                        ("Last Name", "last_name", acc.last_name),
                        ("Email", "email", acc.email),
                        ("Country", "country", acc.country),
                        ("State", "state", acc.state),
                        ("City", "city", acc.city),
                        ("Address Line", "address_line", acc.address_line),
                        ("Zip Code", "zip_code", acc.zip_code),
                        ("Phone", "phone", acc.phone),
                    ]
                    _print_profile_table(fields)
                elif key in {"first_name", "last_name", "email"}:
                    try:
                        if key == "email":
                            validated = ensure_email(new_val)
                            AccountRepository.update_basic(
                                acc.id,
                                first_name=acc.first_name,
                                last_name=acc.last_name,
                                email=validated,
                            )
                        else:
                            validated = ensure_length_max(ensure_non_empty(new_val, key), key, 50)
                            AccountRepository.update_basic(
                                acc.id,
                                first_name=validated if key == "first_name" else acc.first_name,
                                last_name=validated if key == "last_name" else acc.last_name,
                                email=acc.email,
                            )
                        acc = AccountRepository.get_by_id(acc.id) or acc
                        fields = [
                            ("First Name", "first_name", acc.first_name),
                            ("Last Name", "last_name", acc.last_name),
                            ("Email", "email", acc.email),
                            ("Country", "country", acc.country),
                            ("State", "state", acc.state),
                            ("City", "city", acc.city),
                            ("Address Line", "address_line", acc.address_line),
                            ("Zip Code", "zip_code", acc.zip_code),
                            ("Phone", "phone", acc.phone),
                        ]
                        _print_profile_table(fields)
                        ui.ok("Profile updated.")
                    except Exception as e:
                        ui.err(str(e))
                        ui.wait_continue()
                else:
                    ui.info("Updating that field is not supported yet.")
                    ui.wait_continue()
                break

def _print_profile_table(fields: list[tuple[str, str, str | None]]) -> None:
    table = Table(title="My Profile", show_lines=True)
    table.add_column("Field"); table.add_column("Value")
    for label, _, value in fields:
        table.add_row(label, str(value or ""))
    console.print(table)

def _show_address(acc) -> None:
    table = Table(title="Confirm Your Shipping Address", show_lines=True)
    table.add_column("Field"); table.add_column("Value")
    for label, val in [
        ("Country", acc.country),
        ("State", acc.state),
        ("City", acc.city),
        ("Address Line", acc.address_line),
        ("Zip Code", acc.zip_code),
        ("Phone", acc.phone),
    ]:
        table.add_row(label, str(val or ""))
    console.print(table)

def _prompt_address_update(acc):
    country = ui.text(f"Country [{acc.country or ''}]:") or acc.country
    state = ui.text(f"State [{acc.state or ''}]:") or acc.state
    city = ui.text(f"City [{acc.city or ''}]:") or acc.city
    address_line = ui.text(f"Address Line [{acc.address_line or ''}]:") or acc.address_line
    zip_code = ui.text(f"Zip Code [{acc.zip_code or ''}]:") or acc.zip_code
    phone = ui.text(f"Phone [{acc.phone or ''}]:") or acc.phone
    AccountRepository.update_address(acc.id, country, state, city, address_line, zip_code, phone)
    return AccountRepository.get_by_id(acc.id) or acc

def _parse_ids(text: str) -> list[int]:
    raw = text.replace(",", " ").split()
    out: list[int] = []
    for tok in raw:
        if tok.isdigit():
            out.append(int(tok))
    return out

def _customer_messaging_portal(account) -> None:
    svc = MessagingService()
    while True:
        choice = ui.menu_select(
            "Message Support",
            "Choose an action",
            ["Start a new conversation", "View my conversations", "Quit"],
        )
        if choice == "Start a new conversation":
            subject = ui.text("Subject:")
            content = ui.text("Message:")
            try:
                conv_id = svc.start_conversation(account.id, subject, content)
                _chat_repl(svc, account, conv_id, as_staff=False)
            except Exception as e:
                ui.err(str(e))
                ui.wait_continue()
        elif choice == "View my conversations":
            convs = svc.list_customer_conversations(account.id)
            if not convs:
                ui.banner("My Conversations", "No conversations yet.")
                ui.wait_continue()
            else:
                body = "\n".join([f"{c.id} - {c.subject}" for c in convs])
                ui.banner("My Conversations", body)
                cid_str = ui.text("Enter conversation ID to open (or blank to cancel):").strip()
                if cid_str and cid_str.isdigit():
                    cid = int(cid_str)
                    conv = svc.get_conversation(cid)
                    if conv and conv.customer_id == account.id:
                        _chat_repl(svc, account, cid, as_staff=False)
                    else:
                        ui.err("Conversation not found")
                        ui.wait_continue()
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
            svc.customer_reply(account.id, conversation_id, txt)
            render_full()
        except Exception as e:
            ui.err(str(e))
            ui.wait_continue()


