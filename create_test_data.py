#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from accounts.models import Account
from carts.models import Order, OrderItem
from store.models import Product
from django.utils import timezone


def create_test_data():
    # Create a test user if not exists
    try:
        user = Account.objects.get(email="testuser@example.com")
        print("Test user already exists")
    except Account.DoesNotExist:
        user = Account.objects.create(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            username="testuser123",  # Changed to avoid conflict
            phone_number="1234567890",
        )
        user.set_password("testpass123")
        user.is_active = True
        user.save()
        print("Test user created")

    # Get product with id=1
    try:
        product = Product.objects.get(id=1)
        print(f"Product found: {product.product_name}")
    except Product.DoesNotExist:
        print("Product with id=1 not found")
        return

    # Check if user already has an order for this product
    existing_order = OrderItem.objects.filter(
        order__user=user, product=product, ordered=True
    ).exists()

    if existing_order:
        print("User already has purchased this product")
        return

    # Create an order for the user
    order = Order.objects.create(
        user=user,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone_number,
        address_line_1="123 Test St",
        city="Test City",
        state="Test State",
        country="Test Country",
        order_total=100.00,
        tax=10.00,
        status="Delivered",
        payment_status="Paid",
        email_verified=True,
        created_at=timezone.now(),
    )
    order.order_number = f"{order.created_at.strftime('%Y%m%d')}{order.id}"
    order.save()
    print(f"Order created: {order.order_number}")

    # Create OrderItem with ordered=True
    order_item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        product_price=product.price,
        ordered=True,
    )
    print("OrderItem created with ordered=True")


if __name__ == "__main__":
    create_test_data()
