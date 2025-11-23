from django import forms
from .models import ReviewRating, ReviewMedia


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ["subject", "review", "rating"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].widget.attrs.update(
            {
                "maxlength": "100",
                "placeholder": "Brief title for your review (optional)",
                "class": "form-control",
            }
        )
        self.fields["review"].widget.attrs.update(
            {
                "maxlength": "2000",
                "rows": "4",
                "placeholder": "Share your experience with this product...",
                "class": "form-control",
                "required": True,
            }
        )
        self.fields["rating"].widget.attrs.update(
            {
                "min": "1",
                "max": "5",
                "step": "1",
                "required": True,
                "class": "form-control",
            }
        )

    def clean_review(self):
        review = self.cleaned_data.get("review")
        if len(review.strip()) < 10:
            raise forms.ValidationError("Review must be at least 10 characters long.")
        return review

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if not (1 <= rating <= 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating


class ReviewMediaForm(forms.ModelForm):
    class Meta:
        model = ReviewMedia
        fields = ["image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget.attrs.update(
            {
                "accept": "image/*",
                "class": "form-control-file",
                "multiple": False,
            }
        )

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be less than 5MB.")
            # Check file type
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if (
                hasattr(image, "content_type")
                and image.content_type not in allowed_types
            ):
                raise forms.ValidationError(
                    "Only JPEG, PNG, GIF, and WebP images are allowed."
                )
        return image
