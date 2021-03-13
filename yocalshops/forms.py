from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Form
from django.db import models
from django import forms
from .models import *

# Just a default django registering form with additional address field


class RegisterForm(UserCreationForm):
    user_type = forms.fields.ChoiceField(
        choices=(
            ("customer", "Customer"),
            ("helper", "Helper"),
        ),
        required=True,
        widget=forms.widgets.Select)
    address = forms.fields.CharField(max_length=200)

    class Meta:
        model = User
        fields = ["user_type", "username",
                  "password1", "password2", "address"]


class OrderForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["shoppingstreet"]


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ["name", "category", "quantity", "store"]
