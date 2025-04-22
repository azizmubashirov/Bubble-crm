from django.db import models
from config.user.models import BaseModel


class Profile(BaseModel):
    company_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.company_name

