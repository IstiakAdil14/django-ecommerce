#!/usr/bin/env python
import os
import django
import sys
import requests

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from store.models import Product, ReviewRating
from carts.models import Order, OrderItem
from django.utils import timezone


def test_ajax_review_submission():
    """Test AJAX review submission manually"""
    client = Client()

    # Get the test user
    try:
        user = get_user_model().objects.get(email="testuser@example.com")
        print(f"Found test user: {user.username}")
    except get_user_model().DoesNotExist:
        print("Test user not found. Run create_test_data.py first")
        return

    # Get product
    try:
        product = Product.objects.get(id=1)
        print(f"Found product: {product.product_name}")
    except Product.DoesNotExist:
        print("Product not found")
        return

    # Login
    login_success = client.login(email=user.email, password="testpass123")
    if not login_success:
        print("Login failed")
        return

    # Test AJAX review submission
    print("Testing AJAX review submission...")
    response = client.post(
        reverse("submit_review", args=[product.id]),
        {
            "subject": "Great product from test!",
            "rating": "5",
            "review": "This is an excellent product. Highly recommend! Tested via script.",
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response data: {data}")
            if data.get("success"):
                print("✓ AJAX review submission successful")
                # Check if review was created
                review = ReviewRating.objects.filter(user=user, product=product).first()
                if review:
                    print(f"✓ Review created: {review.subject}")
                else:
                    print("✗ Review not found in database")
            else:
                print(f"✗ Review submission failed: {data.get('message')}")
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Response content: {response.content}")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
        print(f"Response content: {response.content}")


def test_email_service():
    """Test email service connectivity"""
    print("Testing email service...")
    try:
        response = requests.get("http://localhost:3001/health", timeout=5)
        if response.status_code == 200:
            print("✓ Email service is running")
        else:
            print(f"✗ Email service returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Email service not accessible: {e}")


if __name__ == "__main__":
    test_email_service()
    test_ajax_review_submission()
