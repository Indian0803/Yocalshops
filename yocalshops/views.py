from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from .decorators import unauthenticated_user, allowed_users
from .forms import *
from .models import *
# Create your views here.

# display the home page


def home(request):
    return render(request, "yocalshops/home.html")


# display the register page and varify user information to save it in the User class


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

# display the login page and varify the user
# redirect them to the customer page or helper page according to the usertype


@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        # checking the form submitted by the user and using django authenticate function to authentica user
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        # checking for the user type and redirect them according to the user type
        if user is not None:
            login(request, user)
            l = request.user.groups.values_list(
                'name', flat=True)
            l_as_list = list(l)
            if "customer" in l_as_list:
                return redirect("customer_home")
            elif "helper" in l_as_list:
                return redirect("helper_home")

        else:
            messages.info(request, "Username OR Password is incorrect")
    context = {}
    return render(request, "yocalshops/login.html", context)

# logout the user


def logoutUser(request):
    logout(request)
    return redirect("login")

# display the customer home page


@allowed_users(allowed_roles=["admin", "customer"])
@login_required(login_url="login")
def customer_home(request):
    context = {}
    return render(request, "yocalshops/customer_home.html", context)

# allow the user to make orders from the customer_orders page


@allowed_users(allowed_roles=["admin", "customer"])
@login_required(login_url="login")
def customer_orders(request):
    ItemFormSet = inlineformset_factory(
        Customer, Item, fields=["name", "category", "quantity", "store"], extra=10)
    customer = Customer.objects.get(name=request.user.username)
    formset = ItemFormSet(instance=customer)

    if request.method == "POST":
        oform = OrderForm(request.POST)
        formset = ItemFormSet(request.POST, instance=customer)
        if oform.is_valid() and formset.is_valid():
            formset.save()

            customer.shoppingstreet = oform.cleaned_data.get("shoppingstreet")
            customer.status = "Pending"
            customer.save()
            return redirect("customer_home")
    else:
        oform = OrderForm()
        iform = ItemForm()

    context = {"oform": oform, "formset": formset}
    return render(request, "yocalshops/customer_orders.html", context)

# Display the status of the customer's request, and if a helper accepted the request, display the map


@allowed_users(allowed_roles=["admin", "customer"])
@login_required(login_url="login")
def customer_status(request):
    customer = Customer.objects.get(name=request.user.username)
    if customer.status == "Pending":
        status = "Pending"
        context = {"status": status}
    elif customer.status == None:
        status = None
        context = {"status": status}
    else:
        status = customer.status
        helper = customer.helper
        context = {"status": status, "helper": helper}

    # Helper's address
    return render(request, "yocalshops/customer_status.html", context)

# display the helper home page


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_home(request):
    helper = Helper.objects.get(name=request.user.username)
    c = Customer.objects.filter(helper=helper)
    if not c:
        c_id = 0
    else:
        customer = c[0]
        c_id = customer.id
    context = {"c_id": c_id}
    return render(request, "yocalshops/helper_home.html", context)

# display a list of pending orders


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_orders(request):
    customers = Customer.objects.filter(status="Pending")

    context = {"customers": customers}
    return render(request, "yocalshops/helper_orders.html", context)

# when the helper clicks to see details of the order, show them the details of the order


def helper_details(request, id):
    print(id)
    customer = Customer.objects.get(id=id)
    items = Item.objects.filter(customer=customer)
    user = Helper.objects.get(name=request.user.username)

    context = {"customer": customer, "items": items, "user": user}
    return render(request, "yocalshops/helper_details.html", context)


# display the order information and map. Allow the helper to change the status of the order
def helper_delivery(request, c_id):
    if c_id != 0:
        customer = Customer.objects.get(id=c_id)
        helper = Helper.objects.get(name=request.user.username)
        customer.helper = helper
        customer.status = "On the way to the store"
        customer.save()
        shoppingstreet = customer.shoppingstreet

        items = Item.objects.filter(customer=customer)

        form = Status()
        if request.method == "POST":
            form = Status(request.POST)

            if form.is_valid():
                customer.status = form.cleaned_data.get("status")
                if customer.status == "Delivered":
                    customer.status = None
                    customer.shoppingstreet = None
                    customer.helper = None
                    customer.save()
                    Item.objects.filter(customer=customer).delete()
                    return redirect("helper_home")
        context = {"customer": customer,
                   "items": items, "c_id": c_id, "form": form, "shoppingstreet": shoppingstreet}
    else:
        context = {"c_id": c_id}
    return render(request, "yocalshops/helper_delivery.html", context)
