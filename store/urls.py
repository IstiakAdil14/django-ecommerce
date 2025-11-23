from django.urls import path
from . import views

urlpatterns = [
    path("", views.store, name="store"),
    path("<slug:category_slug>/", views.store, name="products_by_category"),
    path(
        "<slug:category_slug>/<slug:product_slug>/",
        views.product_detail,
        name="product_detail_slug",
    ),
    path("search/", views.search, name="search"),
    path("submit_review/<int:product_id>/", views.submit_review, name="submit_review"),
    path(
        "vote_helpfulness/<int:review_id>/",
        views.vote_helpfulness,
        name="vote_helpfulness",
    ),
    path("moderation_queue/", views.moderation_queue, name="moderation_queue"),
]
