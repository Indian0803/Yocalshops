from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.registerPage, name="register"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("customer_home/", views.customer_home, name="customer_home"),
    path("customer_orders/", views.customer_orders, name="customer_orders"),
    path("customer_status/", views.customer_status, name="customer_status"),
    path("helper_home/", views.helper_home, name="helper_home"),
    path("helper_orders/", views.helper_orders, name="helper_orders"),
    path("helper_details/<int:id>/",
         views.helper_details, name="helper_details"),
    path("helper_delivery/<int:c_id>",
         views.helper_delivery, name="helper_delivery")

]
