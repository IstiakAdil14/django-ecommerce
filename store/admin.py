from django.contrib import admin
from .models import (
    Product,
    Variation,
    ReviewRating,
    ReviewHelpfulness,
    ReviewMedia,
    ReviewAudit,
)
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Q


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "price",
        "stock",
        "category",
        "modified_date",
        "is_available",
    )
    prepopulated_fields = {"slug": ("product_name",)}
    inlines = [VariationInline]


class ReviewMediaInline(admin.TabularInline):
    model = ReviewMedia
    extra = 0
    readonly_fields = ("image", "uploaded_at")


class ReviewHelpfulnessInline(admin.TabularInline):
    model = ReviewHelpfulness
    extra = 0
    readonly_fields = ("user", "is_helpful", "created_at")


class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "user",
        "product",
        "rating",
        "status",
        "is_verified_purchase",
        "helpful_percentage",
        "created_at",
    )
    list_filter = ("status", "rating", "is_verified_purchase", "created_at")
    search_fields = ("subject", "review", "user__email", "product__product_name")
    readonly_fields = ("created_at", "updated_at", "helpful_votes", "total_votes")
    inlines = [ReviewMediaInline, ReviewHelpfulnessInline]
    actions = ["mark_as_visible", "mark_as_hidden", "mark_as_pending"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "product", "moderated_by")
        )

    def mark_as_visible(self, request, queryset):
        updated = queryset.update(status="visible")
        for review in queryset:
            ReviewAudit.objects.create(
                review=review,
                action="show",
                admin=request.user,
                reason="Bulk moderation: marked as visible",
            )
        self.message_user(request, f"{updated} reviews marked as visible.")

    mark_as_visible.short_description = "Mark selected reviews as visible"

    def mark_as_hidden(self, request, queryset):
        updated = queryset.update(status="hidden")
        for review in queryset:
            ReviewAudit.objects.create(
                review=review,
                action="hide",
                admin=request.user,
                reason="Bulk moderation: marked as hidden",
            )
        self.message_user(request, f"{updated} reviews marked as hidden.")

    mark_as_hidden.short_description = "Mark selected reviews as hidden"

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status="pending")
        self.message_user(request, f"{updated} reviews marked as pending moderation.")

    mark_as_pending.short_description = "Mark selected reviews as pending"


class ReviewAuditAdmin(admin.ModelAdmin):
    list_display = ("review", "action", "admin", "timestamp")
    list_filter = ("action", "timestamp", "admin")
    search_fields = ("review__subject", "admin__email", "reason")
    readonly_fields = ("review", "action", "admin", "reason", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReviewHelpfulnessAdmin(admin.ModelAdmin):
    list_display = ("review", "user", "is_helpful", "created_at")
    list_filter = ("is_helpful", "created_at")
    search_fields = ("review__subject", "user__email")
    readonly_fields = ("review", "user", "is_helpful", "created_at")

    def has_add_permission(self, request):
        return False


class ReviewMediaAdmin(admin.ModelAdmin):
    list_display = ("review", "image", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("review__subject", "review__user__email")
    readonly_fields = ("review", "image", "uploaded_at")

    def has_add_permission(self, request):
        return False


# Moderation Queue View
class ModerationQueueAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "user",
        "product",
        "rating",
        "created_at",
        "moderation_actions",
    )
    list_filter = ("rating", "created_at", "product__category")
    search_fields = ("subject", "review", "user__email", "product__product_name")
    readonly_fields = (
        "subject",
        "review",
        "rating",
        "user",
        "product",
        "created_at",
        "ip",
        "is_verified_purchase",
    )
    actions = ["bulk_approve", "bulk_hide"]

    def get_queryset(self, request):
        return ReviewRating.objects.filter(status="pending").select_related(
            "user", "product"
        )

    def moderation_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Approve</a> '
            '<a class="button" href="{}">Hide</a>',
            reverse("admin:store_reviewrating_change", args=[obj.pk])
            + "?action=approve",
            reverse("admin:store_reviewrating_change", args=[obj.pk]) + "?action=hide",
        )

    moderation_actions.short_description = "Actions"

    def bulk_approve(self, request, queryset):
        updated = queryset.update(status="visible")
        for review in queryset:
            ReviewAudit.objects.create(
                review=review,
                action="show",
                admin=request.user,
                reason="Bulk approval from moderation queue",
            )
        self.message_user(request, f"{updated} reviews approved.")

    bulk_approve.short_description = "Approve selected reviews"

    def bulk_hide(self, request, queryset):
        updated = queryset.update(status="hidden")
        for review in queryset:
            ReviewAudit.objects.create(
                review=review,
                action="hide",
                admin=request.user,
                reason="Bulk hide from moderation queue",
            )
        self.message_user(request, f"{updated} reviews hidden.")

    bulk_hide.short_description = "Hide selected reviews"


admin.site.register(Product, ProductAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)
admin.site.register(ReviewAudit, ReviewAuditAdmin)
admin.site.register(ReviewHelpfulness, ReviewHelpfulnessAdmin)
admin.site.register(ReviewMedia, ReviewMediaAdmin)
# admin.site.register(ReviewRating, ModerationQueueAdmin)  # Commented out to avoid duplicate registration
