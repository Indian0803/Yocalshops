from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


class Helper(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


class ShoppingStreet(models.Model):
    name = models.CharField(max_length=200, null=True)
    ward = models.CharField(max_length=200, null=True)
    town = models.CharField(max_length=200, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, null=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    shoppingstreet = models.ForeignKey(
        ShoppingStreet, null=True, on_delete=models.SET_NULL)
    STATUS = (
        ("Pending", "Pending"),
        ("On the way to the store", "On the way to the store"),
        ("On the way", "On the way"),
        ("Delivered", "Delivered")
    )
    status = models.CharField(max_length=200, null=True, choices=STATUS)
    helper = models.ForeignKey(
        Helper, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.customer.name


class Item(models.Model):
    name = models.CharField(max_length=200, null=True)
    store = models.CharField(max_length=200, null=True)
    CATEGORY = (
        ("Meat", "Meat"),
        ("Fish", "Fish"),
        ("Vegetable", "Vegetable"),
        ("Fruits", "Fruits"),
        ("Others", "Others")
    )
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    quantity = models.IntegerField(null=True)
    order = models.ForeignKey(
        Order, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
