from __future__ import annotations

from datetime import datetime, date

from app.cli import ui
from app.models import ReportType
from app.services.report_service import ReportService
from app.cli.ui import console
from rich.table import Table


def ceo_portal(account) -> None:
    svc = ReportService()
    while True:
        choice = ui.menu_select(
            "CEO Portal",
            "Choose an option",
            ["View existing reports", "Generate new report", "Logout"],
        )
        if choice == "View existing reports":
            _view_existing_reports(svc)
        elif choice == "Generate new report":
            _generate_new_report(svc)
        elif choice == "Logout":
            ui.ok("Log out successful!")
            return


def _view_existing_reports(svc: ReportService) -> None:
    rows = svc.list_all_reports()
    table = Table(title="Existing Reports", show_lines=True)
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Start")
    table.add_column("End")
    table.add_column("Qty")
    table.add_column("Revenue")
    table.add_column("Created")
    if not rows:
        ui.banner("Existing Reports", "No reports found.")
    else:
        for r in rows:
            table.add_row(
                str(r.id),
                r.type.value,
                r.start_date.strftime("%Y-%m-%d"),
                r.end_date.strftime("%Y-%m-%d"),
                str(r.sold_quantity),
                f"${r.total_revenue}",
                r.created_date.strftime("%Y-%m-%d %H:%M"),
            )
        console.print(table)
    sel = ui.text("Enter report ID to view details (type q to quit):").strip()
    if sel.lower() == "q" or not sel:
        return
    if not sel.isdigit():
        ui.err("Invalid ID")
        ui.wait_continue()
        return
    rid = int(sel)
    gen = svc.get_report(rid)
    if not gen:
        ui.err("Report not found")
        ui.wait_continue()
        return
    _show_report(gen, svc, ask_continue=True)


def _generate_new_report(svc: ReportService) -> None:
    kind = ui.select("Type", ["Daily", "Weekly", "Monthly"])
    ds = ui.text("Enter start date (YYYY-MM-DD):").strip()
    try:
        start_day = datetime.strptime(ds, "%Y-%m-%d").date()
        if kind == "Daily":
            gen = svc.generate_daily(start_day)
        elif kind == "Weekly":
            gen = svc.generate_weekly(start_day)
        else:
            gen = svc.generate_monthly(start_day.year, start_day.month)
        _show_report(gen, svc, ask_continue=False)
        ui.wait_continue()
    except Exception as e:
        ui.err(str(e))
        ui.wait_continue()


def _show_report(gen, svc: ReportService | None = None, ask_continue: bool = False) -> None:
    r = gen.report
    # Summary table
    header = f"Report #{r.id} | {r.type.value} | {r.start_date:%Y-%m-%d} -- {r.end_date:%Y-%m-%d}"
    summary = Table(title=header, show_lines=True)
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Total Sold", str(r.sold_quantity))
    summary.add_row("Total Revenue", f"${r.total_revenue}")
    console.print(summary)

    # Contents table (by item) with item names
    table = Table(title="Report Contents", show_lines=True)
    table.add_column("Item ID")
    table.add_column("Item Name")
    table.add_column("Qty")
    table.add_column("Unit Price")
    table.add_column("Subtotal")
    rows = svc.get_report_details(r.id) if svc is not None else []
    if not rows:
        ui.info("(no sales)")
    else:
        for row in rows:
            table.add_row(
                str(row["item_id"]),
                str(row["item_name"]),
                str(row["item_sold"]),
                f"${row['unit_price']}",
                f"${row['sub_total']}",
            )
        console.print(table)

    if ask_continue:
        ui.wait_continue()


