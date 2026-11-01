"""Helper UI: clear screen, banner, input, masking, status."""
from __future__ import annotations

import os
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import config

console = Console()


def clear() -> None:
    """Clear layar sebelum pindah menu (sesuai requirement)."""
    os.system("cls" if os.name == "nt" else "clear")


def banner(subtitle: str = "") -> None:
    clear()
    title = Text(f"{config.APP_NAME}  v{config.APP_VERSION}", style="bold cyan")
    if subtitle:
        body = Text(subtitle, style="yellow")
        console.print(Panel.fit(body, title=title, border_style="cyan"))
    else:
        console.print(Panel.fit("AI Analysis • TwelveData • SoSoValue • Groq",
                                title=title, border_style="cyan"))


def hr() -> None:
    console.print("─" * 60, style="dim")


def ask(label: str, default: str = "", allow_empty: bool = True) -> str:
    suffix = f" [dim](default: {default})[/]" if default else ""
    while True:
        val = console.input(f"[bold green]›[/] {label}{suffix}: ").strip()
        if not val:
            val = default
        if val or allow_empty:
            return val
        warn("Input tidak boleh kosong. Coba lagi.")


def ask_int(label: str, default: int | None = None) -> int | None:
    while True:
        raw = ask(label, str(default) if default is not None else "")
        if not raw:
            return default
        try:
            return int(raw)
        except ValueError:
            warn("Harus berupa angka. Coba lagi.")


def press_enter(msg: str = "Tekan [Enter] untuk melanjutkan...") -> None:
    try:
        console.input(f"\n[dim]{msg}[/]")
    except (EOFError, KeyboardInterrupt):
        pass


def mask_secret(value: str) -> str:
    v = value.strip()
    if not v:
        return "[red](belum diisi)[/]"
    if len(v) <= 8:
        return v[:2] + "***"
    return f"{v[:4]}••••••••{v[-4:]}"


def success(msg: str) -> None:
    console.print(f"[bold green]✓[/] {msg}")


def warn(msg: str) -> None:
    console.print(f"[bold yellow]![/] {msg}")


def error(msg: str) -> None:
    console.print(f"[bold red]✗[/] {msg}")


def info(msg: str) -> None:
    console.print(f"[bold blue]i[/] {msg}")


def env_table(rows: list[tuple[str, str, str]]) -> Table:
    t = Table(show_header=True, header_style="bold magenta", expand=True)
    t.add_column("#", style="dim", width=3)
    t.add_column("Variabel", style="cyan", no_wrap=True)
    t.add_column("Nilai", style="green")
    t.add_column("URL / Keterangan", style="dim", overflow="fold")
    for i, (var, val, desc) in enumerate(rows, 1):
        t.add_row(str(i), var, val, desc)
    return t


def settings_table(settings: dict) -> Table:
    method = config.method_by_code(settings["analysis_method"])
    method_label = f"{method['code']} — {method['name']}" if method else settings["analysis_method"]
    t = Table(show_header=True, header_style="bold magenta", expand=True)
    t.add_column("Pengaturan", style="cyan")
    t.add_column("Nilai Saat Ini", style="green")
    t.add_row("Risk : Reward", settings["risk_reward"])
    t.add_row("Metode Analisis", method_label)
    t.add_row("Target Pips", str(settings["target_pips"]))
    return t
