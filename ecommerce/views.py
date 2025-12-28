from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from store.models import Product
from store.views import store as store_view
from category.models import Category

def home(request):
    products = Product.objects.filter(is_available=True).order_by('-created_date')[:8]  # Get last 8 added products for popular section
    links = Category.objects.all()
    return render(request, "home.html", {'products': products, 'links': links})

def store(request):
    return store_view(request)

def cart(request):
    return render(request, "cart.html")

def product_detail(request, product_id):
    return render(request, "product_detail.html", {'product_id': product_id})

