from django.contrib import admin
from config.order import models


admin.site.register(models.Order)
admin.site.register(models.OrderItem)
admin.site.register(models.Payment)
admin.site.register(models.OrderStatus)
admin.site.register(models.OrderPriceChange)
