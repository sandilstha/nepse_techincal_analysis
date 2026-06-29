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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST

from core_analysis.forms import EmailRegistrationForm
from core_analysis.models import EmailActivation

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
def _mask_email(email):
    local, _, domain = (email or "").partition("@")
    if not domain:
        return email
    if len(local) <= 2:
        masked = f"{local[:1]}*"
    else:
        masked = f"{local[:1]}{'*' * max(2, len(local) - 2)}{local[-1:]}"
    return f"{masked}@{domain}"


def _activation_sent_url(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return "activation_sent", uidb64


def _activation_link(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse("activate_email", kwargs={"uidb64": uidb64, "token": token})
    return request.build_absolute_uri(path)


def _activation_from_uid(uidb64):
    UserModel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
        return user, user.email_activation
    except (
        TypeError,
        ValueError,
        OverflowError,
        UserModel.DoesNotExist,
        EmailActivation.DoesNotExist,
    ):
        return None, None


def _send_activation_email(request, user, activation):
    link = _activation_link(request, user)
    subject = "Activate your Risk & Portfolio Desk account"
    message = (
        f"Hello {user.get_username()},\n\n"
        "Activate your Risk & Portfolio Desk account using this link:\n"
        f"{link}\n\n"
        "If you did not create this account, you can ignore this email."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [activation.email], fail_silently=False)
    activation.mark_sent()
    activation.save(update_fields=["sent_at"])


def register_view(request):
    """Self-service signup with email activation."""
    if request.user.is_authenticated:
        return redirect("portfolio")
    if request.method == "POST":
        form = EmailRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                activation = EmailActivation.objects.create(
                    user=user, email=form.cleaned_data["email"]
                )
            try:
                _send_activation_email(request, user, activation)
                messages.success(request, f"Activation email sent to {_mask_email(activation.email)}.")
            except Exception:
                logger.exception("activation email failed for user %s", user.pk)
                messages.error(request, "Account created, but the activation email could not be sent. Check SMTP settings and resend it.")
            route, uidb64 = _activation_sent_url(user)
            return redirect(route, uidb64=uidb64)
    else:
        form = EmailRegistrationForm()
    return render(
        request,
        "registration/register.html",
        {"form": form, "asset_version": _asset_version()},
    )


def activation_sent_view(request, uidb64):
    user, activation = _activation_from_uid(uidb64)
    if not user or not activation:
        return render(
            request,
            "registration/email_activation_sent.html",
            {"invalid_link": True, "asset_version": _asset_version()},
            status=404,
        )

    if user.is_active and activation.is_activated:
        if request.user.is_authenticated and request.user.pk == user.pk:
            return redirect("portfolio")
        messages.info(request, "This account is already active. Sign in to continue.")
        return redirect("login")

    if request.method == "POST":
        try:
            _send_activation_email(request, user, activation)
            messages.success(request, f"Activation email sent to {_mask_email(activation.email)}.")
        except Exception:
            logger.exception("activation resend failed for user %s", user.pk)
            messages.error(request, "Could not send the activation email. Check SMTP settings and try again.")
        return redirect("activation_sent", uidb64=uidb64)

    return render(
        request,
        "registration/email_activation_sent.html",
        {
            "masked_email": _mask_email(activation.email),
            "sent_at": activation.sent_at,
            "asset_version": _asset_version(),
        },
    )


def activate_email_view(request, uidb64, token):
    user, activation = _activation_from_uid(uidb64)
    if not user or not activation:
        return render(
            request,
            "registration/email_activation_sent.html",
            {"invalid_link": True, "asset_version": _asset_version()},
            status=404,
        )

    if user.is_active and activation.is_activated:
        messages.info(request, "This account is already active. Sign in to continue.")
        return redirect("login")

    if not default_token_generator.check_token(user, token):
        return render(
            request,
            "registration/email_activation_sent.html",
            {"invalid_link": True, "asset_version": _asset_version()},
            status=400,
        )

    user.is_active = True
    user.save(update_fields=["is_active"])
    activation.activated_at = timezone.now()
    activation.save(update_fields=["activated_at"])
    login(request, user)
    messages.success(request, "Account activated. Upload your Meroshare CSV to get started.")
    return redirect("portfolio")


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
