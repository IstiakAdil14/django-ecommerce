from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ReviewForm
from .models import Review, Order
# import Product from the app where Product lives. If Product lives in store.models, import that:
from store.models import Product

@login_required
def submit_review(request, product_id):
    """
    Submit or update a review for product identified by product_id.
    Matches URL pattern: submit_review/<int:product_id>/

    Behavior:
      - only POST accepted
      - server-side purchase check (excludes refunded orders)
      - updates existing review if present, otherwise creates one
      - sets verified_purchase True when a qualifying order exists
      - returns JSON for AJAX requests, otherwise redirects back to product detail page
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    product = get_object_or_404(Product, id=product_id)
    user = request.user

    # Server-side purchase check: user must have at least one non-refunded order for this product
    has_purchase = Order.objects.filter(user=user, product=product).exclude(status=Order.STATUS_REFUNDED).exists()
    if not has_purchase:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "Only customers who bought this product can review."}, status=403)
        messages.error(request, "Only customers who bought this product can review.")
        # Redirect to product detail — your product detail URL uses category_slug/product_slug, so try to resolve with product fields
        try:
            return redirect(reverse("store:product_detail_slug", kwargs={
                "category_slug": getattr(product, "category").slug if getattr(product, "category", None) else "",
                "product_slug": getattr(product, "slug", product.id)
            }))
        except Exception:
            return redirect("store:store")

    try:
        with transaction.atomic():
            review, created = Review.objects.get_or_create(
                product=product,
                user=user,
                defaults={
                    "rating": 5,
                    "title": "",
                    "body": "",
                    "verified_purchase": True,
                    "status": Review.STATUS_PENDING,
                },
            )

            form = ReviewForm(request.POST, instance=review)
            if not form.is_valid():
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"success": False, "error": "Validation failed", "errors": form.errors}, status=400)

                # Non-AJAX: re-render product detail with form errors
                # Attempt to reuse your existing store.product_detail view rendering
                # If your store.product_detail expects category_slug & product_slug, redirect back to that view with a message
                messages.error(request, "Please correct the errors in your review form.")
                try:
                    return redirect(reverse("store:product_detail_slug", kwargs={
                        "category_slug": getattr(product, "category").slug if getattr(product, "category", None) else "",
                        "product_slug": getattr(product, "slug", product.id)
                    }))
                except Exception:
                    return redirect("store:store")

            saved = form.save(commit=False)
            # ensure flags set server-side
            saved.verified_purchase = True
            # keep pending by default (moderation); change to APPROVED to auto-publish
            if saved.status not in (Review.STATUS_APPROVED, Review.STATUS_PENDING):
                saved.status = Review.STATUS_PENDING
            saved.save()

    except IntegrityError:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "Database error"}, status=500)
        messages.error(request, "Could not save review, try again.")
        try:
            return redirect(reverse("store:product_detail_slug", kwargs={
                "category_slug": getattr(product, "category").slug if getattr(product, "category", None) else "",
                "product_slug": getattr(product, "slug", product.id)
            }))
        except Exception:
            return redirect("store:store")

    # Success response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        from django.template.loader import render_to_string
        review_html = render_to_string("reviews/_single_review.html", {"r": saved, "request": request})
        count = product.reviews.filter(status=Review.STATUS_APPROVED).count()
        return JsonResponse({"success": True, "id": saved.pk, "html": review_html, "count": count})

    messages.success(request, "Your review has been submitted and is pending approval.")
    try:
        return redirect(reverse("store:product_detail_slug", kwargs={
            "category_slug": getattr(product, "category").slug if getattr(product, "category", None) else "",
            "product_slug": getattr(product, "slug", product.id)
        }))
    except Exception:
        return redirect("store:store")
