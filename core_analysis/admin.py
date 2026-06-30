from django.contrib import admin, messages
from django.utils import timezone

from .models import AccountApproval


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
