from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from .decorators import unauthenticated_user, allowed_users
from .forms import *
from .models import *
import geocoder

# display the home page


def home(request):
    return render(request, "yocalshops/home.html")


# display the register page and varify user information to save it in the User class


@unauthenticated_user
def registerPage(request):
    # using RegisterForm to create a user if the form is valid
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")

            # checking for the usertype so that either Customer/Helper object can be created
            role = form.cleaned_data.get("user_type")
            group = Group.objects.get(name=role)
            user.groups.add(group)
            address = form.cleaned_data.get("address")

            if role == "customer":
                Customer.objects.create(
                    user=user, name=username, address=address)

            elif role == "helper":
                Helper.objects.create(
                    user=user, name=username)
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
    # Using 2 forms:
    # OrderForm to make the user specify the shopping street, which will be stored in the Customer object
    # ItemFormSet to make the user type in the actual orders, which will be stored in the Item object that will be subject to the customer
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
    # The status of the customer's order is stored in the customer object
    # The status is checked and is passed into the template
    # If the order has been accepted by a helper, the helper object is passed in so that the name and location can be displayed to the customer
    customer = Customer.objects.get(name=request.user.username)
    if customer.status == "Pending":
        status = "Pending"
        context = {"status": status}
    elif customer.status == None:
        status = None
        context = {"status": status}
    else:

        # getting customer's address
        address = customer.address
        g = geocoder.osm(address, timeout=5.0)
        clat = g.latlng[0]
        clng = g.latlng[1]

        status = customer.status
        helper = customer.helper
        context = {"clat": clat, "clng": clng,
                   "status": status, "helper": helper}

    # Helper's address
    return render(request, "yocalshops/customer_status.html", context)

# display the helper home page


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_home(request):
    # checks if the helper has an order at the moment
    # c_id is the id of the customer and it is set to 0 if helper has no order at the moment
    # c_id is passed into the template, which will then be passed into the helper_delivery function
    helper = Helper.objects.get(name=request.user.username)
    c = Customer.objects.filter(helper=helper)
    if not c:
        c_id = 0
    else:
        customer = c[0]
        c_id = customer.id
    context = {"c_id": c_id}
    return render(request, "yocalshops/helper_home.html", context)

# display a list of pending orders by passing in the Customer objects


@allowed_users(allowed_roles=["admin", "helper"])
@login_required(login_url="login")
def helper_orders(request):
    customers = Customer.objects.filter(status="Pending")

    context = {"customers": customers}
    return render(request, "yocalshops/helper_orders.html", context)

# when the helper clicks to see details of the order, show them the details of the order


def helper_details(request, id):
    # When the helper clicks on the order, the id of the customer that created the order will be passed in to this function
    # Information about customer's order will be passed into the template
    customer = Customer.objects.get(id=id)
    items = Item.objects.filter(customer=customer)
    user = Helper.objects.get(name=request.user.username)

    context = {"customer": customer, "items": items, "user": user}
    return render(request, "yocalshops/helper_details.html", context)


# display the order information and map. Allow the helper to change the status of the order
def helper_delivery(request, c_id):
    # Check if the helper has accepted any order, and c_id will be 0 if the helper has not customer
    # information about the order is passed into the template
    if c_id != 0:
        customer = Customer.objects.get(id=c_id)
        helper = Helper.objects.get(name=request.user.username)
        customer.helper = helper
        customer.status = "On The Way"
        customer.save()
        shoppingstreet = customer.shoppingstreet

        items = Item.objects.filter(customer=customer)

        # getting helper's current location and saving it in helper object
        g = geocoder.ip("me", key="AIzaSyDXrOFblUU_XMSP8UEXav0Y25qv2q9Fl10")
        print(g.latlng)
        print(g.latlng[0])
        helper.latitude = g.latlng[0]
        print(helper.latitude)
        helper.longitude = g.latlng[1]
        helper.save()
        # When the user clicks on the button inside the template, the delivering is completed and the order is deleted
        if request.method == "POST":
            customer.status = None
            customer.shoppingstreet = None
            customer.helper = None
            customer.save()
            Item.objects.filter(customer=customer).delete()
            return redirect("helper_home")
        context = {"customer": customer,
                   "items": items, "c_id": c_id, "shoppingstreet": shoppingstreet}
    else:
        context = {"c_id": c_id}
    return render(request, "yocalshops/helper_delivery.html", context)
