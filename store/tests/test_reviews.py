from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from store.models import Product, ReviewRating, ReviewHelpfulness, Account
from category.models import Category
from django.utils import timezone

User = get_user_model()


class ReviewRatingModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name="Test Category", slug="test-category"
        )
        self.product = Product.objects.create(
            product_name="Test Product",
            slug="test-product",
            price=100,
            category=self.category,
        )
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password123",
            first_name="Test",
            last_name="User",
            username="testuser",
        )

    def test_create_review_rating(self):
        review = ReviewRating.objects.create(
            product=self.product,
            user=self.user,
            subject="Good product",
            review="This product is really good",
            rating=4.5,
            ip="127.0.0.1",
            status="visible",
            is_verified_purchase=True,
        )
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.subject, "Good product")
        self.assertEqual(review.rating, 4.5)
        self.assertTrue(review.is_visible())


class ReviewViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            category_name="Test Category", slug="test-category"
        )
        self.product = Product.objects.create(
            product_name="Test Product",
            slug="test-product",
            price=100,
            category=self.category,
            stock=10,
        )
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password123",
            first_name="Test",
            last_name="User",
            username="testuser",
        )
        self.client.login(email="user@test.com", password="password123")

    def test_product_detail_reviews_pagination(self):
        # Create multiple reviews for pagination
        for i in range(10):
            ReviewRating.objects.create(
                product=self.product,
                user=self.user,
                subject=f"Subject {i}",
                review=f"Review text {i}",
                rating=4.0,
                status="visible",
            )

        url = reverse(
            "product_detail_slug", args=[self.category.slug, self.product.slug]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("reviews" in response.context)
        self.assertTrue(response.context["reviews"].paginator.num_pages >= 2)

    def test_submit_review_post(self):
        url = reverse("submit_review", args=[self.product.id])
        post_data = {
            "subject": "Test Review",
            "review": "This is a test review text with more than ten characters",
            "rating": 5,
        }
        response = self.client.post(
            url, post_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))

    def test_vote_helpfulness(self):
        review = ReviewRating.objects.create(
            product=self.product,
            user=self.user,
            subject="Helpful review",
            review="This is helpful",
            rating=5,
            status="visible",
        )

        url = reverse("vote_helpfulness", args=[review.id])
        post_data = {"is_helpful": "true"}
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(ReviewHelpfulness.objects.filter(review=review).count(), 1)


class ReviewModerationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            category_name="Test Category", slug="test-category"
        )
        self.product = Product.objects.create(
            product_name="Test Product",
            slug="test-product",
            price=100,
            category=self.category,
            stock=10,
            images="photos/products/default.jpg",
        )
        self.user = User.objects.create_user(
            email="user@test.com", 
            password="password123", 
            first_name="Test", 
            last_name="User", 
            username="testuser"
        )
        self.staff_user = User.objects.create_user(
            email="staff@test.com", password="password123", is_staff=True
        )
        self.review = ReviewRating.objects.create(
            product=self.product,
            user=self.user,
            subject="Pending review",
            review="Needs moderation",
            rating=3,
            status="pending",
        )

    def test_moderation_queue_access(self):
        url = reverse("moderation_queue")
        # Anonymous user should be redirected
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Non staff user redirected or denied
        self.client.login(email="user@test.com", password="password123")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

        # Staff user can access moderation queue
        self.client.login(email="staff@test.com", password="password123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.review, response.context["reviews"])
