from __future__ import annotations

import os
from typing import List

from rich.console import Console
from rich.panel import Panel
import questionary


console = Console()


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner(title: str, body: str | None = None) -> None:
    content = body or ""
    console.print(Panel(content, title=f"{title}", border_style="cyan", expand=True))


def info(message: str) -> None:
    console.print(f"[yellow]{message}[/yellow]")


def ok(message: str) -> None:
    console.print(f"[green]{message}[/green]")


def err(message: str) -> None:
    console.print(f"[red]{message}[/red]")


def wait_continue(prompt: str = "Type 'c' to continue: ", key: str = "c") -> None:
    while True:
        ans = questionary.text(prompt).ask()
        if (ans or "").strip().lower() == key.lower():
            return


def select(prompt: str, choices: List[str]) -> str:
    answer = questionary.select(prompt, choices=choices).ask()
    return answer or ""


def menu_select(title: str, prompt: str, choices: List[str]) -> str:
    # Render full-width panel listing choices numerically
    lines = [prompt, ""]
    for idx, label in enumerate(choices, start=1):
        lines.append(f"{idx}. {label}")
    body = "\n".join(lines)
    banner(title, body)
    while True:
        ans = questionary.text(f"Enter choice [1-{len(choices)}]:").ask() or ""
        ans = ans.strip()
        if ans.isdigit():
            n = int(ans)
            if 1 <= n <= len(choices):
                return choices[n - 1]
        err("Invalid choice. Please enter a number in range.")

def text(prompt: str) -> str:
    answer = questionary.text(prompt).ask()
    return answer or ""


def password(prompt: str) -> str:
    answer = questionary.password(prompt).ask()
    return answer or ""


