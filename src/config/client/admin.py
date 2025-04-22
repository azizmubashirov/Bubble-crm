from django.contrib import admin
from config.client import models


admin.site.register(models.Client)
admin.site.register(models.ClientPhoneNumber)
