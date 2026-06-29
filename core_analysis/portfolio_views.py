"""
portfolio_views.py — private, per-user holdings portfolio + risk dashboard.

A logged-in user uploads a Meroshare "My Shares" CSV; we parse it into their
private ``Portfolio`` and render valuation / concentration / sector-exposure /
beta analytics (see ``services.portfolio_analytics``). Everything here is gated
behind login so one user can never see another's positions.
"""
from __future__ import annotations

import csv
import io
import logging
import re

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

DEFAULT_PORTFOLIO_NAME = "My Portfolio"
MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # a holdings CSV is tiny; cap to be safe
_SYMBOL_RE = re.compile(r"^[A-Z0-9]+$")


def _asset_version():
    from core_analysis.insights_views import _asset_version as v

    return v()


# ─────────────────────────────────────────────────────────────────────────────
# CSV parsing (Meroshare "My Shares" export)
# ─────────────────────────────────────────────────────────────────────────────
def _num(value):
    """Parse a number from a CSV cell ('1,065.00', '"100"', '') -> float|None."""
    if value is None:
        return None
    s = str(value).replace(",", "").replace('"', "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _map_columns(header):
    """Locate the columns we need by header name (order-independent).

    The Meroshare export pairs each price with a rupee "Value as of …" column
    whose label *contains* the price label (e.g. "Value as of Last Closing
    Price"), so those value columns are skipped first and the first genuine match
    wins — otherwise the value column would shadow the price column.
    """
    col = {}
    for i, raw in enumerate(header):
        h = (raw or "").strip().lower()
        if not h or h.startswith("value") or "value as of" in h:
            continue  # rupee-value columns, never a price/quantity we want
        if h.startswith("scrip") and "symbol" not in col:
            col["symbol"] = i
        elif ("current balance" in h or h == "balance" or "quantity" in h) and "qty" not in col:
            col["qty"] = i
        elif "last closing price" in h and "close" not in col:
            col["close"] = i
        elif ("last transaction price" in h or h.endswith("(ltp)") or h == "ltp") and "ltp" not in col:
            col["ltp"] = i
    return col


def parse_holdings_csv(text):
    """Parse the Meroshare holdings CSV into rows + a skipped-line count.

    Tolerates the leading header row, the trailing ``Total :`` summary row, blank
    lines, quoted cells and missing decimals. Returns
    ``(rows, skipped)`` where each row is
    ``{symbol, quantity, last_close, ltp}`` and ``skipped`` counts non-position
    lines that were ignored (header/total/blank/invalid).
    """
    rows, skipped, col, seen = [], 0, None, set()
    reader = csv.reader(io.StringIO(text))
    for raw in reader:
        if not raw or all(not (c or "").strip() for c in raw):
            continue
        if col is None:
            if any("scrip" in (c or "").strip().lower() for c in raw):
                col = _map_columns(raw)
                continue
            skipped += 1
            continue
        if "symbol" not in col or col["symbol"] >= len(raw):
            skipped += 1
            continue
        sym = (raw[col["symbol"]] or "").strip().upper()
        if not sym or sym.startswith("TOTAL") or not _SYMBOL_RE.match(sym) or sym in seen:
            skipped += 1
            continue
        qty = _num(raw[col["qty"]]) if "qty" in col and col["qty"] < len(raw) else None
        if not qty:  # drop zero / blank balances
            skipped += 1
            continue
        seen.add(sym)
        rows.append({
            "symbol": sym,
            "quantity": qty,
            "last_close": _num(raw[col["close"]]) if "close" in col and col["close"] < len(raw) else None,
            "ltp": _num(raw[col["ltp"]]) if "ltp" in col and col["ltp"] < len(raw) else None,
        })
    return rows, skipped


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────
def register_view(request):
    """Self-service signup. Logs the new user in and sends them to the portfolio."""
    if request.user.is_authenticated:
        return redirect("portfolio")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Upload your Meroshare CSV to get started.")
            return redirect("portfolio")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


# ─────────────────────────────────────────────────────────────────────────────
# Portfolio page + data
# ─────────────────────────────────────────────────────────────────────────────
def _get_or_create_portfolio(user):
    from core_analysis.models import Portfolio

    portfolio, _ = Portfolio.objects.get_or_create(
        user=user, name=DEFAULT_PORTFOLIO_NAME
    )
    return portfolio


@login_required(login_url="login")
def portfolio_view(request):
    """Render the Risk & Portfolio dashboard shell for the logged-in user."""
    portfolio = _get_or_create_portfolio(request.user)
    return render(
        request,
        "core_analysis/portfolio.html",
        {
            "asset_version": _asset_version(),
            "has_holdings": portfolio.holdings.exists(),
        },
    )


@login_required(login_url="login")
def portfolio_data_api(request):
    """JSON valuation + risk roll-up for the user's portfolio."""
    from core_analysis.services import portfolio_analytics as pa

    portfolio = _get_or_create_portfolio(request.user)
    try:
        return JsonResponse(pa.build_portfolio_payload(portfolio))
    except Exception:  # pragma: no cover - defensive, never 500 the dashboard
        logger.exception("portfolio payload failed for user %s", request.user.id)
        return JsonResponse({"ok": False, "error": "Unable to compute portfolio."}, status=500)


@login_required(login_url="login")
@require_POST
def portfolio_import(request):
    """Replace the user's holdings with the contents of an uploaded CSV."""
    from core_analysis.models import Holding

    upload = request.FILES.get("file")
    if not upload:
        messages.error(request, "Please choose a CSV file to upload.")
        return redirect("portfolio")
    if upload.size and upload.size > MAX_UPLOAD_BYTES:
        messages.error(request, "That file is too large to be a holdings CSV.")
        return redirect("portfolio")

    try:
        text = upload.read().decode("utf-8-sig", errors="replace")
        rows, skipped = parse_holdings_csv(text)
    except Exception:
        logger.exception("CSV parse failed for user %s", request.user.id)
        messages.error(request, "Could not read that file — is it a Meroshare 'My Shares' CSV?")
        return redirect("portfolio")

    if not rows:
        messages.error(request, "No holdings found in that file. Check the format and try again.")
        return redirect("portfolio")

    portfolio = _get_or_create_portfolio(request.user)
    with transaction.atomic():
        portfolio.holdings.all().delete()
        Holding.objects.bulk_create([
            Holding(
                portfolio=portfolio,
                symbol=r["symbol"],
                quantity=r["quantity"],
                last_close=r["last_close"],
                ltp=r["ltp"],
            )
            for r in rows
        ])
        portfolio.save()  # bump updated_at so cached payloads invalidate

    note = f"Imported {len(rows)} holdings."
    if skipped:
        note += f" ({skipped} non-position lines skipped.)"
    messages.success(request, note)
    return redirect("portfolio")


@login_required(login_url="login")
@require_POST
def portfolio_clear(request):
    """Wipe the user's holdings (keeps the empty portfolio)."""
    portfolio = _get_or_create_portfolio(request.user)
    portfolio.holdings.all().delete()
    portfolio.save()
    messages.success(request, "Portfolio cleared.")
    return redirect("portfolio")
