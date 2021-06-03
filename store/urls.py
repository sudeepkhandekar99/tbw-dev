from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = "index"),
    path('product/<int:id>', views.product, name = "product"),
    path('shop', views.shop, name = "shop"),
    path('register', views.register, name = "register"),
    path('login', views.auth_login, name = "auth_login"),
    path('cart', views.cart, name = "cart"),
    path('update_item', views.update_item, name = "update_item"),
    path('confirmation', views.confirmation, name = "confirmation"),
    path('checkout', views.checkout, name = "checkout"),
    path('about', views.about, name = "about"),
    path('terms', views.terms, name = "terms"),
    path('cancel', views.cancel, name = "cancel"),
    path('privacy', views.privacy, name = "privacy"),
    path('moreProducts', views.moreProducts, name = "moreProducts"),
    path('process_order', views.process_order, name = "process_order"),
    path('handlerequest', views.handlerequest, name = "handlerequest"),
]
