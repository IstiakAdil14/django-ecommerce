from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count
from django.utils import timezone

# Create your models here.


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.price < 0:
            raise ValidationError({"price": "Price cannot be negative."})

    def get_url(self):
        return reverse("product_detail_slug", args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(
            average=Avg("rating")
        )
        avg = 0
        if reviews["average"] is not None:
            avg = float(reviews["average"])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(
            count=Count("id")
        )
        count = 0
        if reviews["count"] is not None:
            count = int(reviews["count"])
        return count

    def get_image_url(self):
        """
        Returns the image URL. With CloudinaryStorage configured, 
        this automatically returns Cloudinary CDN URLs.
        Falls back to placeholder if no image is set.
        """
        if self.images and self.images.name:
            # CloudinaryStorage automatically provides full URLs via .url
            return self.images.url
        return "https://via.placeholder.com/300x200?text=No+Image"


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(
            variation_category="color", is_active=True
        )

    def sizes(self):
        return super(VariationManager, self).filter(
            variation_category="size", is_active=True
        )


variation_category_choice = (
    ("color", "color"),
    ("size", "size"),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choice
    )
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    STATUS_CHOICES = (
        ("visible", "Visible"),
        ("hidden", "Hidden"),
        ("pending", "Pending Moderation"),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    total_votes = models.PositiveIntegerField(default=0)
    moderation_reason = models.TextField(blank=True)
    moderated_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_reviews",
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    def helpful_percentage(self):
        if self.total_votes == 0:
            return 0
        return (self.helpful_votes / self.total_votes) * 100

    def is_visible(self):
        return self.status == "visible"

    def mark_as_visible(self, moderator=None):
        self.status = "visible"
        if moderator:
            self.moderated_by = moderator
            self.moderated_at = timezone.now()
        self.save()

    def mark_as_hidden(self, moderator=None, reason=""):
        self.status = "hidden"
        if moderator:
            self.moderated_by = moderator
            self.moderated_at = timezone.now()
        self.moderation_reason = reason
        self.save()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "status", "created_at"]),
            models.Index(fields=["user", "product"]),
        ]


class ReviewHelpfulness(models.Model):
    review = models.ForeignKey(
        ReviewRating, on_delete=models.CASCADE, related_name="helpfulness_votes"
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")

    def __str__(self):
        return f"{self.user.email} - {self.review.subject} - {'Helpful' if self.is_helpful else 'Not Helpful'}"


class ReviewMedia(models.Model):
    review = models.ForeignKey(
        ReviewRating, on_delete=models.CASCADE, related_name="media"
    )
    image = models.ImageField(upload_to="reviews/", max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media for review: {self.review.subject}"


class ReviewAudit(models.Model):
    ACTION_CHOICES = (
        ("hide", "Hidden"),
        ("show", "Shown"),
        ("moderate", "Moderated"),
    )

    review = models.ForeignKey(ReviewRating, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    admin = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.review.subject} by {self.admin.email if self.admin else 'System'}"

    class Meta:
        ordering = ["-timestamp"]


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="store/products", max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = "productgallery"
        verbose_name_plural = "product gallery"
