from django.db import models
from config.user.models import BaseModel, User
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta

def default_price():
    return {
        "A": 0,
        "B": 0,
        "C": 0,
    }


class Type(BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=10, blank=False, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Categories(MPTTModel, BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    image = models.URLField(blank=True, null=True, max_length=500)
    type = models.ForeignKey(Type, blank=False, null=True, on_delete=models.SET_NULL)

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['mptt_level']

    def __str__(self):
        return self.name
    
class RawCategories(BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self) -> str:
        return self.name

class Products(BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    category = models.ForeignKey(RawCategories, blank=False, null=True, on_delete=models.SET_NULL)
    images = ArrayField(models.URLField(blank=False, null=False, max_length=500), size=10)
    amount = models.BigIntegerField(blank=True, null=True, default=0)
    defect = models.BigIntegerField(null=True, blank=True, default=0)
    type = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


class QuantityChange(BaseModel):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=10, choices=[('add', 'Add'), ('subtract', 'Вычесть')])
    type = models.CharField(max_length=10, choices=[('amount', 'Количество'), ('defect', 'Дефект')])
    quantity_changed = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user} - {self.change_type} {self.quantity_changed} of {self.product.name}"


class ProductionProductInfo(BaseModel):
    name = models.CharField(max_length=200, null=True, blank=True)
    category = models.ForeignKey(Categories, blank=False, null=True, on_delete=models.SET_NULL)
    images = ArrayField(models.URLField(blank=False, null=False, max_length=500), size=10)
    norm = models.BigIntegerField(blank=True, null=True, default=0, help_text="Norma Product")
    price = models.JSONField(blank=True, null=True, default=default_price)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class ProductionProduct(BaseModel):
    production_product = models.ForeignKey(ProductionProductInfo, on_delete=models.CASCADE, null=True)
    amount = models.BigIntegerField(blank=False, null=False, default=0)
    amount_old = models.BigIntegerField(blank=False, null=False, default=0)
    amount_m = models.BigIntegerField(blank=False, null=False, default=0)
    one_m = models.BigIntegerField(blank=False, null=False, default=0)
    status = models.BigIntegerField(blank=False, null=False, default=1)
    accepted = models.BigIntegerField(default=1)
    stock_products = models.ManyToManyField(Products, through='ProductionProductStockItem')
    worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cost = models.CharField(blank=True, null=True, max_length=200)

    def __str__(self):
        return self.production_product.name
    
    @classmethod
    def get_records_for_current_month(cls, status=1):
        current_date = datetime.now()
        start_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        records = cls.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month, status=status).order_by('-id')
        return records


class ProductionProductStockItem(BaseModel):
    production_product = models.ForeignKey(ProductionProduct, on_delete=models.CASCADE, null=True)
    stock_product = models.ForeignKey(Products, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    defect_amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.production_product.production_product.name} - {self.stock_product.name}"


class UserProduct(BaseModel):
    user = models.ForeignKey(User, blank=False, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(ProductionProduct, blank=False, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.product.name

