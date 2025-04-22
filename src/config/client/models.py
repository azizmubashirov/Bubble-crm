from django.db import models
from config.user.models import BaseModel, User


def default_location():
    return {
        "latitude": 0,
        "longitude": 0,
    }
 

class Client(BaseModel):
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    firstname = models.CharField(max_length=200, help_text="First name")
    lastname = models.CharField(max_length=200, help_text="Last name")
    company_name = models.CharField(max_length=200, help_text="Company name")
    inn = models.CharField(max_length=200, help_text="Inn", blank=True, null=True)
    address = models.CharField(max_length=250, help_text="Address")
    location = models.JSONField(blank=False, null=False, default=default_location)
    location_link = models.URLField(blank=True, null=True, max_length=500)

    def __str__(self):
        return f"{self.firstname} - {self.lastname} {self.company_name} {self.inn}"


class ClientPhoneNumber(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.phone_number


