from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from places.fields import PlacesField

from EmployeeList.country import Country


class PrivateInvestigator(models.Model):
    countryObj = Country()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    available = models.BooleanField()
    country = models.CharField(max_length=100, default="US")
    zip_code = models.CharField(max_length=50)
    address = PlacesField()

    def __str__(self):
        return self.user.get_full_name()


class Client(models.Model):
    countryObj = Country()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    reason_for_service = models.TextField()
    country = models.CharField(max_length=100, default="US")
    zip_code = models.CharField(max_length=50)
    address = PlacesField()

    def __str__(self):
        return self.user.get_full_name()


class Customer(models.Model):
    countryObj = Country()
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="US")
    zip_code = models.CharField(max_length=50)
    address = PlacesField()
    added_by = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name.title()


class BookedInvestigator(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    investigator = models.ForeignKey(PrivateInvestigator, on_delete=models.CASCADE)
    booked_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer.full_name + ' => ' + self.investigator.user.get_full_name()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_receiver")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_sender")
    type = models.CharField(max_length=200)
    notify_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    text = models.TextField()
    message_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return self.sender.username


class InvestigatorBlockEvent(models.Model):
    investigator = models.ForeignKey(PrivateInvestigator, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='Blocked')
    date = models.DateField()

    def __str__(self):
        return self.investigator.user.username
