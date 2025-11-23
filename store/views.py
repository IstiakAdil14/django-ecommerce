from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery, Variation, ReviewHelpfulness
from category.models import Category
from carts.models import CartItem
from django.db.models import Q
from django.urls import reverse

from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
# from orders.models import OrderProduct


def store(request, category_slug=None):
    categories = None
    products = None
    links = Category.objects.all()

    # Get filter parameters
    keyword = request.GET.get("keyword")
    sizes = request.GET.getlist("size")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Get available sizes dynamically
    available_sizes = (
        Variation.objects.filter(variation_category="size", is_active=True)
        .values_list("variation_value", flat=True)
        .distinct()
    )

    # Base queryset
    products = Product.objects.filter(is_available=True).order_by("id")

    # Filter by category if provided
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=categories)

    # Filter by keyword
    if keyword:
        products = products.filter(Q(product_name__icontains=keyword))

    # Filter by sizes
    if sizes:
        products = products.filter(
            variation__variation_category="size",
            variation__variation_value__in=sizes,
            variation__is_active=True,
        ).distinct()

    # Filter by price
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Pagination
    paginator = Paginator(products, 3)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    product_count = products.count()

    # Build query params for pagination
    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]
    params = urlencode(query_params)

    context = {
        "products": paged_products,
        "product_count": product_count,
        "links": links,
        "keyword": keyword,
        "sizes": sizes,
        "available_sizes": available_sizes,
        "min_price": min_price,
        "max_price": max_price,
        "params": params,
    }
    return render(request, "store.html", context)


from django.core.paginator import Paginator


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()
    except Product.DoesNotExist:
        # Handle product not found gracefully
        messages.error(request, "Product not found.")
        return redirect("store")
    except Exception as e:
        raise e

    # Check if user has purchased the product
    has_purchased = False
    if request.user.is_authenticated:
        from carts.models import OrderItem

        has_purchased = OrderItem.objects.filter(
            order__user=request.user, product_id=single_product.id, ordered=True
        ).exists()

    # Review sorting parameter
    sort = request.GET.get("sort", "newest")

    reviews_qs = (
        ReviewRating.objects.filter(product_id=single_product.id, status="visible")
        .select_related("user")
        .prefetch_related("media", "helpfulness_votes")
    )

    # Apply sorting
    if sort == "newest":
        reviews_qs = reviews_qs.order_by("-created_at")
    elif sort == "highest":
        reviews_qs = reviews_qs.order_by("-rating", "-created_at")
    elif sort == "lowest":
        reviews_qs = reviews_qs.order_by("rating", "-created_at")
    elif sort == "most_helpful":
        reviews_qs = reviews_qs.order_by("-helpful_votes", "-created_at")
    else:
        reviews_qs = reviews_qs.order_by("-created_at")

    # Pagination
    paginator = Paginator(reviews_qs, 5)  # Show 5 reviews per page
    page_number = request.GET.get("page")
    reviews_page = paginator.get_page(page_number)

    # Calculate review statistics
    total_reviews = reviews_qs.count()
    verified_reviews_count = reviews_qs.filter(is_verified_purchase=True).count()
    percent_verified = 0
    if total_reviews > 0:
        percent_verified = int((verified_reviews_count / total_reviews) * 100)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    # Get variations for color and size
    colors = single_product.variation_set.filter(
        variation_category="color", is_active=True
    )
    sizes = single_product.variation_set.filter(
        variation_category="size", is_active=True
    )

    existing_review = None
    if request.user.is_authenticated:
        existing_review = ReviewRating.objects.filter(
            product_id=single_product.id, user=request.user
        ).first()
    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "has_purchased": has_purchased,
        "reviews": reviews_page,
        "product_gallery": product_gallery,
        "colors": colors,
        "sizes": sizes,
        "sort": sort,
        "total_reviews": total_reviews,
        "percent_verified": percent_verified,
        "page_obj": reviews_page,
        "existing_review": existing_review,
    }
    return render(request, "store/product_detail.html", context)


def search(request):
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.order_by("-created_date").filter(
                Q(product_name__icontains=keyword)
            )
            product_count = products.count()

            # Pagination
            paginator = Paginator(products, 3)
            page = request.GET.get("page")
            paged_products = paginator.get_page(page)

            # Build query params for pagination
            query_params = request.GET.copy()
            if "page" in query_params:
                del query_params["page"]
            params = urlencode(query_params)

            context = {
                "products": paged_products,
                "product_count": product_count,
                "keyword": keyword,
                "params": params,
            }
        else:
            context = {
                "products": None,
                "product_count": 0,
                "keyword": keyword,
                "params": "",
            }
    else:
        context = {
            "products": None,
            "product_count": 0,
            "keyword": "",
            "params": "",
        }
    return render(request, "store.html", context)


def submit_review(request, product_id):
    from email_utils import send_email_via_nodemailer
    from .forms import ReviewMediaForm
    import logging
    from django.core.cache import cache
    from django.utils import timezone
    from django.http import JsonResponse
    from django.contrib.auth.decorators import login_required
    from django.contrib.auth import authenticate

    logger = logging.getLogger(__name__)
    url = request.META.get("HTTP_REFERER")
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    logger.info(f"Request headers: {request.headers}")
    logger.info(
        f"submit_review called: user={request.user}, authenticated={request.user.is_authenticated}, is_ajax={is_ajax}, method={request.method}"
    )

    if not request.user.is_authenticated:
        if is_ajax:
            logger.info("Unauthenticated AJAX request to submit_review")
            return JsonResponse(
                {
                    "success": False,
                    "message": "Authentication required. Please log in.",
                },
                status=401,
            )
        else:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())

    if request.method == "POST":
        print("Processing POST data for review submission")
        # Allow any logged-in user to submit review regardless of purchase
        has_purchased = True
        # No purchase check to allow any logged-in user

        # Check if review already exists (one review per user per product)
        existing_review = ReviewRating.objects.filter(
            user=request.user, product_id=product_id
        ).first()

        # Rate limiting: max 5 reviews per day per user
        today = timezone.now().date()
        recent_reviews = ReviewRating.objects.filter(
            user=request.user, created_at__date=today
        ).count()
        print(f"User has submitted {recent_reviews} reviews today")
        if recent_reviews >= 5 and not existing_review:
            print("User reached daily review limit")
            if is_ajax:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "You have reached the daily review limit. Please try again tomorrow.",
                    }
                )
            messages.error(
                request,
                "You have reached the daily review limit. Please try again tomorrow.",
            )
            return redirect(url)

        if existing_review:
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            form = ReviewForm(request.POST)
        media_form = ReviewMediaForm(request.POST, request.FILES)

        if form.is_valid():
            print("ReviewForm is valid")
            if existing_review:
                data = existing_review
            else:
                data = ReviewRating()
            data.subject = form.cleaned_data["subject"]
            data.rating = form.cleaned_data["rating"]
            data.review = form.cleaned_data["review"]
            data.ip = request.META.get("REMOTE_ADDR")
            data.product_id = product_id
            data.user_id = request.user.id
            data.is_verified_purchase = has_purchased

            # Basic spam detection
            if len(data.review.strip()) < 10:
                data.status = "hidden"
                data.moderation_reason = "Review too short - possible spam"
            elif data.rating == 5.0 and len(data.review.strip()) < 20:
                data.status = "pending"  # Flag for moderation
            else:
                data.status = "visible"  # Auto-approve for now

            data.save()

            # Handle media uploads
            if media_form.is_valid() and request.FILES.get("image"):
                media = media_form.save(commit=False)
                media.review = data
                media.save()

            # Update product aggregates
            product = data.product
            product.save()  # Triggers aggregate recalculation

            # Clear product review cache
            cache.delete(f"product_reviews_{product_id}")

            # Log the review submission
            logger.info(
                f"Review submitted by user {request.user.email} for product {product_id}: rating={data.rating}, status={data.status}"
            )
            print(
                f"Review submitted by user {request.user.email} for product {product_id}: rating={data.rating}, status={data.status}"
            )

            # Send confirmation email
            subject = "Review Submitted Successfully"
            html_content = f"""
            <html>
            <body>
                <h2>Thank you for your review!</h2>
                <p>Dear {request.user.first_name},</p>
                <p>Your review for the product has been submitted successfully.</p>
                <p><strong>Rating:</strong> {data.rating} stars</p>
                <p><strong>Subject:</strong> {data.subject}</p>
                <p><strong>Review:</strong> {data.review}</p>
                <p><strong>Status:</strong> {"Visible immediately" if data.status == "visible" else "Under review"}</p>
                <p>You can view your review here: <a href="{request.build_absolute_uri(reverse("product_detail_slug", args=[product.category.slug, product.slug]))}">View Review</a></p>
                <p>Thank you for your feedback!</p>
            </body>
            </html>
            """
            try:
                send_email_via_nodemailer(request.user.email, subject, html_content)
                print(f"Confirmation email sent to {request.user.email}")
            except Exception as e:
                logger.error(f"Failed to send confirmation email: {e}")
                print(f"Failed to send confirmation email: {e}")

            if is_ajax:
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Review posted — confirmation email sent",
                        "review_id": data.id,
                        "status": data.status,
                    }
                )

            messages.success(request, "Review posted — confirmation email sent")
            return redirect(url)

        else:
            logger.error(f"ReviewForm errors: {form.errors.as_json()}")
            print(f"ReviewForm errors: {form.errors.as_json()}")
            if is_ajax:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Please correct the errors in your review.",
                        "errors": form.errors,
                    }
                )
            messages.error(request, "Please correct the errors in your review.")

    if is_ajax:
        return JsonResponse(
            {"success": False, "message": "Invalid request"}, status=400
        )
    else:
        return redirect(url)


@login_required(login_url="accounts:login")
def vote_helpfulness(request, review_id):
    from django.http import JsonResponse

    if request.method == "POST":
        try:
            review = ReviewRating.objects.get(id=review_id)
            is_helpful = request.POST.get("is_helpful") == "true"

            # Check if user already voted
            existing_vote = ReviewHelpfulness.objects.filter(
                review=review, user=request.user
            ).first()

            if existing_vote:
                if existing_vote.is_helpful == is_helpful:
                    # Remove vote if same
                    existing_vote.delete()
                    action = "removed"
                else:
                    # Update vote
                    existing_vote.is_helpful = is_helpful
                    existing_vote.save()
                    action = "updated"
            else:
                # Create new vote
                ReviewHelpfulness.objects.create(
                    review=review, user=request.user, is_helpful=is_helpful
                )
                action = "added"

            # Update vote counts
            review.helpful_votes = review.helpfulness_votes_set.filter(
                is_helpful=True
            ).count()
            review.total_votes = review.helpfulness_votes_set.count()
            review.save()

            return JsonResponse(
                {
                    "success": True,
                    "action": action,
                    "helpful_votes": review.helpful_votes,
                    "total_votes": review.total_votes,
                    "percentage": review.helpful_percentage(),
                }
            )

        except ReviewRating.DoesNotExist:
            return JsonResponse({"success": False, "message": "Review not found"})

    return JsonResponse({"success": False, "message": "Invalid request"})


@login_required(login_url="accounts:login")
def moderation_queue(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect("store")

    reviews = (
        ReviewRating.objects.filter(status="pending")
        .select_related("user", "product")
        .order_by("-created_at")
    )
    context = {
        "reviews": reviews,
    }
    return render(request, "store/moderation_queue.html", context)
