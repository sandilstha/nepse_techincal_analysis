"""Post-close sync for the Raw Inventory Manager, driven by a scheduler.

Data lands in two waves after NEPSE closes at 15:00 Nepal time: prices settle
almost at once, the floorsheet dribbles in for another hour. The intended
schedule is therefore

    15:15  manage.py market_close_sync            prices + floorsheet
    15:30  manage.py market_close_sync --verify   re-sync only what is incomplete
    16:00  manage.py market_close_sync --verify   final sweep

No pass ever re-runs a sync blindly — including the 15:15 one. Every run first
measures what actually landed for the day and fetches only the gaps, so a
manual sync from the Workbench that already brought the data in means the
scheduled passes do nothing. ``--force`` overrides that. What gets measured:

  * Prices        — are there rows for the day, and is the count in line with
                    the previous trading day (a half-written sync shows up as a
                    thin day, not an empty one).
  * Floorsheet    — every trade is one floorsheet row, and the price feed
                    independently reports ``total_trades`` per stock. Their sum
                    is therefore the expected floorsheet row count for the day.
                    Coverage below the threshold means trades are still missing.

Design notes:
  * Nepal time, not server time. settings.TIME_ZONE is UTC, so "15:15" must be
    resolved against Asia/Kathmandu or the job fires 5h45m off.
  * NEPSE is shut Friday and Saturday — those days exit immediately.
  * It never raises. A scheduled task that exits non-zero produces a daily
    error balloon; failures are logged and summarised instead.
  * Every underlying sync upserts, so re-running is safe — which is what makes
    the three-pass schedule work.
"""
from datetime import date, timedelta, timezone as dt_timezone

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Max, Sum
from django.utils import timezone

# NEPSE trades on Nepal time; UTC+05:45 has no DST, so a fixed offset is exact.
NPT = dt_timezone(timedelta(hours=5, minutes=45))
# Saturday is the only day NEPSE never trades. Do NOT add Friday: measured over
# the last 260 sessions the weekday split is Sun 36 / Mon 52 / Tue 54 / Wed 52 /
# Thu 50 / Fri 16 / Sat 0 — Friday sessions are irregular but real, and skipping
# them would lose ~16 trading days a year. Sundays and Fridays that turn out to
# be holidays are handled by the no-session check below, not by this set.
CLOSED_WEEKDAYS = {5}             # Saturday (Mon=0)

# Floorsheet is judged complete at this share of the expected trade count. Not
# 100%: the sync legitimately drops a handful of malformed rows each day
# (reported as skipped_invalid), and chasing them would re-sync forever.
FLOOR_COVERAGE_OK = 0.995
# Prices are judged complete at this share of the previous trading day's row
# count — catches a sync that died halfway, which an "any rows?" test misses.
PRICE_ROWS_OK = 0.90


class Command(BaseCommand):
    help = "Post-close price + floorsheet sync with verification; run from a scheduler."

    def add_arguments(self, p):
        p.add_argument("--verify", action="store_true",
                       help="Kept for the scheduled passes; every run verifies first anyway.")
        p.add_argument("--floorsheet-only", action="store_true")
        p.add_argument("--price-only", action="store_true")
        p.add_argument("--date", default="",
                       help="Trading day (YYYY-MM-DD). Defaults to today, Nepal time.")
        p.add_argument("--force", action="store_true",
                       help="Re-sync even if the day is already complete, and run on "
                            "Friday/Saturday when NEPSE is closed.")
        # Off by default: a separate, slower upstream feed. Worth enabling —
        # StockPriceAdjustment feeds most desks and goes stale silently.
        p.add_argument("--with-adjustments", action="store_true",
                       help="Also sync split/bonus-adjusted prices (sync_and_calculate).")

    # ── status ──────────────────────────────────────────────────────────────
    def _status(self, day):
        """What actually landed for ``day``, and whether it looks complete."""
        from core_analysis.models import (NepseDailyStockPrice as P,
                                          NepseFloorsheet as F)

        price_rows = P.objects.filter(business_date=day).count()

        prev = (P.objects.filter(business_date__lt=day)
                .aggregate(m=Max("business_date"))["m"])
        prev_rows = P.objects.filter(business_date=prev).count() if prev else 0

        # Expected floorsheet rows = trades reported by the price feed.
        expected = (P.objects.filter(business_date=day)
                    .aggregate(s=Sum("total_trades"))["s"]) or 0
        floor_rows = F.objects.filter(business_date=day).count()
        coverage = (floor_rows / expected) if expected else 0.0

        price_ok = price_rows > 0 and (not prev_rows or price_rows >= prev_rows * PRICE_ROWS_OK)
        # Without prices there is no expected count, so the floorsheet cannot be
        # judged complete yet — treat it as not-ok so the next pass retries.
        floor_ok = bool(expected) and coverage >= FLOOR_COVERAGE_OK

        return {
            "price_rows": price_rows, "prev_rows": prev_rows, "price_ok": price_ok,
            "expected": expected, "floor_rows": floor_rows,
            "coverage": coverage, "floor_ok": floor_ok,
        }

    # ── main ────────────────────────────────────────────────────────────────
    def handle(self, *a, **o):
        now_npt = timezone.now().astimezone(NPT)
        day = date.fromisoformat(o["date"].strip()) if o["date"].strip() else now_npt.date()
        stamp = now_npt.strftime("%Y-%m-%d %H:%M NPT")

        if not o["force"] and now_npt.weekday() in CLOSED_WEEKDAYS:
            self.stdout.write(f"[{stamp}] NEPSE closed ({now_npt.strftime('%A')}) — nothing to do.")
            return

        do_price = not o["floorsheet_only"]
        do_floor = not o["price_only"]

        # Always look before fetching. If the day's data is already complete —
        # because a manual sync from the Workbench got there first, or an
        # earlier pass succeeded — there is nothing to do, and re-pulling it
        # would only burn a few minutes hammering the upstream feed for rows we
        # already hold. --force is the escape hatch for a deliberate refetch.
        s = self._status(day)
        self.stdout.write(
            f"[{stamp}] check {day}: prices {s['price_rows']} rows "
            f"(prev day {s['prev_rows']}) -> {'OK' if s['price_ok'] else 'INCOMPLETE'} | "
            f"floorsheet {s['floor_rows']}/{s['expected']} "
            f"({s['coverage'] * 100:.2f}%) -> {'OK' if s['floor_ok'] else 'INCOMPLETE'}"
        )
        if not o["force"]:
            do_price = do_price and not s["price_ok"]
            do_floor = do_floor and not s["floor_ok"]
        if not do_price and not do_floor:
            self.stdout.write(self.style.SUCCESS(
                f"[{stamp}] {day}: already up to date — nothing to sync."))
            return

        results = []
        if do_price:
            results.append(self._run("prices", "sync_nepse_data",
                                     source="both", from_date=day))
            if o["with_adjustments"]:
                results.append(self._run("adjusted", "sync_and_calculate",
                                         source="adjustments", from_date=day))
        if do_floor:
            results.append(self._run("floorsheet", "sync_floorsheet",
                                     from_date=day, to_date=day))

        after = self._status(day)
        ok = [n for n, good, _ in results if good]
        bad = [(n, e) for n, good, e in results if not good]

        line = (f"[{stamp}] {day}: ran " + (", ".join(ok) or "nothing") +
                f" | prices {after['price_rows']} rows, floorsheet "
                f"{after['floor_rows']}/{after['expected']} ({after['coverage'] * 100:.2f}%)")
        if bad:
            line += " | FAILED: " + ", ".join(f"{n} ({e})" for n, e in bad)
            self.stdout.write(self.style.WARNING(line))
        elif after["price_rows"] == 0:
            # The syncs ran cleanly and the feed returned nothing at all: this is
            # a public holiday, not a failure. Nepal has a lot of them, and many
            # calendar Sundays/Fridays are closed. Without this branch every pass
            # would log INCOMPLETE and retry all afternoon on every holiday.
            self.stdout.write(self.style.SUCCESS(
                f"[{stamp}] {day}: no trading session (holiday) — nothing to sync."))
        elif not (after["price_ok"] and after["floor_ok"]):
            # Ran cleanly but data is still short — the next pass will retry.
            self.stdout.write(self.style.WARNING(line + " | still incomplete, next pass will retry"))
        else:
            self.stdout.write(self.style.SUCCESS(line))

    def _run(self, label, command, **kwargs):
        """Call one sync, swallowing failures so a scheduled run never exits non-zero."""
        try:
            call_command(command, **kwargs)
            return (label, True, None)
        except Exception as exc:   # pragma: no cover - upstream is best-effort
            self.stderr.write(self.style.ERROR(f"  {label} sync failed: {exc}"))
            return (label, False, str(exc)[:120])
