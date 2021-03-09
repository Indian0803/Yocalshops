from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from .forms import RegisterForm, OrderForm, ItemForm
from .models import *
# Create your views here.


def home(request):
    return render(request, "yocalshops/home.html")


@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            l = request.user.groups.values_list(
                'name', flat=True)  # QuerySet Object
            l_as_list = list(l)
            if "customer" in l_as_list:
                return redirect("customer_home")
            elif "helper" in l_as_list:
                return redirect("helper_home")

        else:
            messages.info(request, "Username OR Password is incorrect")
    context = {}
    return render(request, "yocalshops/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


@unauthenticated_user
def registerPage(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")

            role = form.cleaned_data.get("user_type")
            group = Group.objects.get(name=role)
            user.groups.add(group)

            address = form.cleaned_data.get("address")
            if role == "customer":
                Customer.objects.create(
                    user=user, name=username, address=address)

            elif role == "helper":
                Helper.objects.create(user=user, name=username)
            return redirect("login")
    else:
        form = RegisterForm()
    context = {"form": form}
    return render(request, "yocalshops/register.html", context)


@allowed_users(allowed_roles=["admin", "customer"])
@login_required(login_url="login")
def customer_home(request):
    context = {}
    return render(request, "yocalshops/customer_home.html", context)


@allowed_users(allowed_roles=["admin", "customer"])
@login_required(login_url="login")
def customer_chat(request):
    context = {}
    return render(request, "yocalshops/customer_chat.html", context)


@allowed_users(allowed_roles=["admin", "customer"])
@login_required(login_url="login")
def customer_orders(request):
    if request.method == "POST":
        oform = OrderForm(request.POST)
        iform = ItemForm(request.POST)
        if oform.is_valid() and iform.is_valid():
            order = oform.save()
            item = iform.save()

            c = Customer.objects.get(name=request.user.username)

            order.customer = c
            order.status = "Pending"
            item.order = order

            order.save()
            item.save()
            return redirect("customer_home")
    else:
        oform = OrderForm()
        iform = ItemForm()

    context = {"oform": oform, "iform": iform}
    return render(request, "yocalshops/customer_orders.html", context)


@allowed_users(allowed_roles=["admin", "customer"])
@login_required(login_url="login")
def customer_settings(request):
    context = {}
    return render(request, "yocalshops/customer_settings.html", context)


@allowed_users(allowed_roles=["admin", "customer"])
@login_required(login_url="login")
def customer_status(request):
    yes = "yes"
    context = {"yes": yes}
    return render(request, "yocalshops/customer_status.html", context)


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_home(request):
    context = {}
    return render(request, "yocalshops/helper_home.html", context)


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_chat(request):
    context = {}
    return render(request, "yocalshops/helper_chat.html", context)


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_delivery(request):
    context = {}
    return render(request, "yocalshops/helper_delivery.html", context)


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_details(request):
    context = {}
    return render(request, "yocalshops/helper_details.html", context)


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_orders(request):
    context = {}
    return render(request, "yocalshops/helper_orders.html", context)


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_settings(request):
    context = {}
    return render(request, "yocalshops/helper_settings.html", context)
