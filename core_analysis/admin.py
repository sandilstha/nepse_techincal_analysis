from django.contrib import admin, messages
from django.db.models import Count
from django.utils import timezone

from .models import AccountApproval, Holding, HoldingCost, Portfolio


@admin.action(description="Approve selected account requests")
def approve_requests(modeladmin, request, queryset):
    count = 0
    for approval in queryset.select_related("user"):
        if approval.status != AccountApproval.APPROVED:
            approval.approve(reviewer=request.user)
            count += 1
    modeladmin.message_user(
        request,
        f"Approved {count} account request(s).",
        messages.SUCCESS,
    )


@admin.action(description="Reject selected account requests")
def reject_requests(modeladmin, request, queryset):
    count = 0
    for approval in queryset.select_related("user"):
        if approval.status != AccountApproval.REJECTED:
            approval.reject(reviewer=request.user)
            count += 1
    modeladmin.message_user(
        request,
        f"Rejected {count} account request(s).",
        messages.WARNING,
    )


@admin.register(AccountApproval)
class AccountApprovalAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "contact_email",
        "status",
        "created_at",
        "reviewed_by",
        "reviewed_at",
    )
    list_filter = ("status", "created_at", "reviewed_at")
    search_fields = ("user__username", "user__email", "contact_email")
    readonly_fields = ("created_at", "reviewed_by", "reviewed_at")
    actions = (approve_requests, reject_requests)
    fieldsets = (
        (None, {"fields": ("user", "contact_email", "status", "review_note")}),
        ("Review", {"fields": ("created_at", "reviewed_by", "reviewed_at")}),
    )

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and obj.pk:
            old_status = AccountApproval.objects.only("status").get(pk=obj.pk).status

        status_changed = old_status != obj.status
        if status_changed and obj.status in (AccountApproval.APPROVED, AccountApproval.REJECTED):
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
            obj.user.is_active = obj.status == AccountApproval.APPROVED
            obj.user.save(update_fields=["is_active"])
        elif status_changed and obj.status == AccountApproval.PENDING:
            obj.reviewed_by = None
            obj.reviewed_at = None
            obj.user.is_active = False
            obj.user.save(update_fields=["is_active"])

        super().save_model(request, obj, form, change)


# ── Portfolio uploads: who imported holdings / cost basis, and what ────────────
class HoldingInline(admin.TabularInline):
    """The uploaded positions (from the Meroshare 'My Shares' CSV)."""
    model = Holding
    extra = 0
    fields = ("symbol", "quantity", "last_close", "ltp", "updated_at")
    readonly_fields = ("updated_at",)


class HoldingCostInline(admin.TabularInline):
    """The uploaded cost basis (from the broker 'My WACC' report)."""
    model = HoldingCost
    extra = 0
    fields = ("symbol", "wacc_rate", "quantity", "total_cost", "modified", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Every user's uploaded portfolio — the answer to 'who uploaded a portfolio'.

    The changelist lists one row per uploaded portfolio with its owner and how
    many holdings / cost rows it carries; drill in to see the actual positions.
    """
    list_display = ("name", "user", "holdings_count", "costs_count", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username", "user__email", "name", "holdings__symbol")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "updated_at"
    ordering = ("-updated_at",)
    inlines = (HoldingInline, HoldingCostInline)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("user")
        return qs.annotate(_holdings=Count("holdings", distinct=True),
                           _costs=Count("costs", distinct=True))

    @admin.display(description="Holdings", ordering="_holdings")
    def holdings_count(self, obj):
        return obj._holdings

    @admin.display(description="Cost rows", ordering="_costs")
    def costs_count(self, obj):
        return obj._costs


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    """Flat, searchable view of every uploaded position across all users."""
    list_display = ("symbol", "quantity", "portfolio", "owner", "updated_at")
    list_filter = ("updated_at",)
    search_fields = ("symbol", "portfolio__user__username", "portfolio__name")
    readonly_fields = ("updated_at",)
    ordering = ("-updated_at",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("portfolio__user")

    @admin.display(description="User", ordering="portfolio__user__username")
    def owner(self, obj):
        return obj.portfolio.user
