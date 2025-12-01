from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Optional

from app.models import Report, ReportContent, ReportType
from app.repositories.report_repository import ReportRepository


@dataclass
class GeneratedReport:
    report: Report
    contents: List[ReportContent]


class ReportService:
    def generate_report(self, rtype: ReportType, start: datetime, end: datetime) -> GeneratedReport:
        # Aggregate sales
        rows = ReportRepository.aggregate_sales(start, end)
        total_qty = 0
        total_rev = Decimal("0.00")
        # Defer ReportContent instantiation until report_id is known
        pending_rows: List[dict] = []
        for r in rows:
            qty = int(r["item_sold"] or 0)
            rev = Decimal(str(r["sub_total"] or "0.00"))
            unit = Decimal(str(r["unit_price"] or "0.00"))
            total_qty += qty
            total_rev += rev
            pending_rows.append(
                {
                    "item_id": int(r["item_id"]),
                    "item_sold": qty,
                    "unit_price": unit,
                    "sub_total": rev,
                }
            )
        total_rev = total_rev.quantize(Decimal("0.01"))

        report = Report(
            id=None,
            type=rtype,
            start_date=start,
            end_date=end,
            created_date=datetime.utcnow(),
            sold_quantity=total_qty,
            total_revenue=total_rev,
        )
        report_id = ReportRepository.create_report(report)

        # Now create and persist contents with a valid report_id
        for pr in pending_rows:
            rc = ReportContent(
                id=None,
                report_id=report_id,
                item_id=pr["item_id"],
                item_sold=pr["item_sold"],
                unit_price=pr["unit_price"],
                sub_total=pr["sub_total"],
            )
            ReportRepository.add_content(rc)

        # reload final report
        final_report = ReportRepository.get_report(report_id)
        final_contents = ReportRepository.get_contents(report_id)
        assert final_report is not None
        return GeneratedReport(final_report, final_contents)

    def generate_daily(self, day: date) -> GeneratedReport:
        start = datetime.combine(day, datetime.min.time())
        end = datetime.combine(day, datetime.max.time())
        return self.generate_report(ReportType.DAILY, start, end)

    def generate_weekly(self, start_day: date) -> GeneratedReport:
        start = datetime.combine(start_day, datetime.min.time())
        end_day = start_day + timedelta(days=6)
        end = datetime.combine(end_day, datetime.max.time())
        return self.generate_report(ReportType.WEEKLY, start, end)

    def generate_monthly(self, year: int, month: int) -> GeneratedReport:
        start = datetime(year=year, month=month, day=1)
        if month == 12:
            end = datetime(year=year, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            next_month = datetime(year=year, month=month + 1, day=1)
            end = next_month - timedelta(microseconds=1)
        return self.generate_report(ReportType.MONTHLY, start, end)

    def get_report(self, report_id: int) -> Optional[GeneratedReport]:
        rp = ReportRepository.get_report(report_id)
        if rp is None:
            return None
        contents = ReportRepository.get_contents(report_id)
        return GeneratedReport(rp, contents)

    def list_reports(self, rtype: ReportType, start: datetime, end: datetime) -> List[Report]:
        return ReportRepository.list_reports_by_type_between(rtype, start, end)

    def list_all_reports(self) -> List[Report]:
        return ReportRepository.list_all_reports()

    def get_report_details(self, report_id: int) -> list[dict]:
        return ReportRepository.get_detailed_contents(report_id)


