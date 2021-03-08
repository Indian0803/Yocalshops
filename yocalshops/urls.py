from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),
    path("customer_home/", views.customer_home, name="customer_home"),
    path("customer_orders/", views.customer_orders, name="customer_orders"),
    path("customer_chat/", views.customer_chat, name="customer_chat"),
    path("customer_settings/", views.customer_settings, name="customer_settings"),
    path("customer_status/", views.customer_status, name="customer_status"),
    path("helper_home/", views.helper_home, name="helper_home"),
    path("helper_chat/", views.helper_chat, name="helper_chat"),
    path("helper_delivery/", views.helper_delivery, name="helper_delivery"),
    path("helper_details/", views.helper_details, name="helper_details"),
    path("helper_orders/", views.helper_orders, name="helper_orders"),
    path("helper_chat/", views.helper_chat, name="helper_chat"),
    path("helper_settings/", views.helper_settings, name="helper_settings")
]
