from __future__ import annotations

from app.models import Role
from app.cli import ui
from app.services.messaging_service import MessagingService


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
        if choice == "Message Support":
            _customer_messaging_portal(account)
        elif choice == "Logout":
            ui.ok("Log out successful!")
            return
        else:
            ui.banner(choice, f"{choice} is in development.")
            ui.wait_continue()


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


