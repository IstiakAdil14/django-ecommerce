from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "title", "body")
        widgets = {
            "rating": forms.RadioSelect(choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")], attrs={
                "class": "form-check-input"
            }),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Short summary",
                "maxlength": "150",
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Write your review",
                "rows": 5,
                "maxlength": "2000",
            }),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating is None:
            raise forms.ValidationError("Rating is required.")
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            raise forms.ValidationError("Invalid rating value.")
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        return title

    def clean_body(self):
        body = self.cleaned_data.get("body", "").strip()
        if not body:
            raise forms.ValidationError("Review body is required.")
        if len(body) > 2000:
            raise forms.ValidationError("Review is too long (max 2000 characters).")
        return body
