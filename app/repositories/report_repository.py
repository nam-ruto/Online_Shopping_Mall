from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from app.models import Report, ReportType, ReportContent
from . import base


def _row_to_report(row: dict) -> Report:
    return Report(
        id=row["id"],
        type=ReportType(row["type"]),
        start_date=row["start_date"],
        end_date=row["end_date"],
        created_date=row["created_date"],
        sold_quantity=row["sold_quantity"],
        total_revenue=row["total_revenue"],
    )


def _row_to_content(row: dict) -> ReportContent:
    return ReportContent(
        id=row["id"],
        report_id=row["report_id"],
        item_id=row["item_id"],
        item_sold=row["item_sold"],
        unit_price=row["unit_price"],
        sub_total=row["sub_total"],
    )


class ReportRepository:
    REPORT_TABLE = "report"
    CONTENT_TABLE = "report_content"

    @staticmethod
    def create_report(report: Report) -> int:
        sql = (
            f"INSERT INTO {ReportRepository.REPORT_TABLE} "
            "(type, start_date, end_date, created_date, sold_quantity, total_revenue) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        new_id = base.execute(
            sql,
            (
                report.type.value,
                report.start_date,
                report.end_date,
                report.created_date,
                report.sold_quantity,
                report.total_revenue,
            ),
        )
        return int(new_id)

    @staticmethod
    def add_content(content: ReportContent) -> int:
        sql = (
            f"INSERT INTO {ReportRepository.CONTENT_TABLE} "
            "(report_id, item_id, item_sold, unit_price, sub_total) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        new_id = base.execute(
            sql,
            (content.report_id, content.item_id, content.item_sold, content.unit_price, content.sub_total),
        )
        return int(new_id)

    @staticmethod
    def get_report(report_id: int) -> Optional[Report]:
        row = base.fetch_one(f"SELECT * FROM {ReportRepository.REPORT_TABLE} WHERE id=%s", (report_id,))
        return _row_to_report(row) if row else None

    @staticmethod
    def get_contents(report_id: int) -> List[ReportContent]:
        rows = base.fetch_all(
            f"SELECT * FROM {ReportRepository.CONTENT_TABLE} WHERE report_id=%s ORDER BY id ASC",
            (report_id,),
        )
        return [_row_to_content(r) for r in rows]

    @staticmethod
    def list_reports_by_type_between(rtype: ReportType, start: datetime, end: datetime) -> List[Report]:
        rows = base.fetch_all(
            f"SELECT * FROM {ReportRepository.REPORT_TABLE} "
            "WHERE type=%s AND start_date>= %s AND end_date<= %s ORDER BY created_date DESC",
            (rtype.value, start, end),
        )
        return [_row_to_report(r) for r in rows]

    @staticmethod
    def aggregate_sales(start: datetime, end: datetime) -> list[dict]:
        # Aggregate item sales from order/order_item between dates
        sql = (
            "SELECT oi.item_id AS item_id, "
            "SUM(oi.quantity) AS item_sold, "
            "ROUND(SUM(oi.sub_total) / NULLIF(SUM(oi.quantity),0), 2) AS unit_price, "
            "SUM(oi.sub_total) AS sub_total "
            "FROM order_item oi "
            "JOIN `order` o ON o.id = oi.order_id "
            "WHERE o.order_date BETWEEN %s AND %s "
            "GROUP BY oi.item_id "
            "ORDER BY oi.item_id"
        )
        return base.fetch_all(sql, (start, end))

    @staticmethod
    def list_all_reports() -> List[Report]:
        rows = base.fetch_all(
            f"SELECT * FROM {ReportRepository.REPORT_TABLE} ORDER BY created_date DESC",
            (),
        )
        return [_row_to_report(r) for r in rows]

    @staticmethod
    def get_detailed_contents(report_id: int) -> list[dict]:
        sql = (
            "SELECT rc.id, rc.report_id, rc.item_id, i.name AS item_name, "
            "rc.item_sold, rc.unit_price, rc.sub_total "
            f"FROM {ReportRepository.CONTENT_TABLE} rc "
            "JOIN item i ON i.id = rc.item_id "
            "WHERE rc.report_id = %s "
            "ORDER BY rc.id ASC"
        )
        return base.fetch_all(sql, (report_id,))


