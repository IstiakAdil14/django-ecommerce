from django.contrib import admin
from .models import Review, Product

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "verified_purchase", "status", "created_at")
    list_filter = ("verified_purchase", "status", "rating")
    search_fields = ("user__username", "user__email", "product__product_name", "title", "body")
    actions = ("approve_reviews", "mark_pending")

    def approve_reviews(self, request, queryset):
        updated = queryset.update(status=Review.STATUS_APPROVED)
        self.message_user(request, f"{updated} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"

    def mark_pending(self, request, queryset):
        updated = queryset.update(status=Review.STATUS_PENDING)
        self.message_user(request, f"{updated} reviews marked as pending.")
    mark_pending.short_description = "Mark selected reviews as pending"
