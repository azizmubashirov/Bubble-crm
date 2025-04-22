from django.contrib import admin
from config.products import models

admin.site.register(models.Products)
admin.site.register(models.Type)
admin.site.register(models.Categories)
admin.site.register(models.UserProduct)
admin.site.register(models.ProductionProductInfo)
admin.site.register(models.ProductionProduct)
admin.site.register(models.ProductionProductStockItem)
admin.site.register(models.Currency)
admin.site.register(models.RawCategories)
