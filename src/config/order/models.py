from django.db import models
from config.user.models import BaseModel, User
from config.products.models import Products, ProductionProduct, ProductionProductInfo
from config.client.models import Client

class Payment(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

class OrderStatus(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Order(BaseModel):
    agent = models.ForeignKey(User,related_name="order_agent", on_delete=models.SET_NULL, blank=True, null=True)
    client = models.ForeignKey(Client, related_name="order_client", on_delete=models.SET_NULL, blank=True, null=True)
    discount = models.BigIntegerField(default=0)
    price_type = models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], max_length=10)
    driver = models.ForeignKey(User, related_name="order_driver", on_delete=models.SET_NULL, blank=True, null=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, blank=True, null=True)
    delivery_price = models.BigIntegerField(default=0, blank=True, null=True)
    signature = models.URLField(blank=True, null=True, max_length=10000000)
    price = models.BigIntegerField(default=0, blank=True, null=True)
    qqs = models.BooleanField(default=False)
    qqs_price = models.BigIntegerField(default=0, blank=True, null=True)
    zav_sklad = models.ForeignKey(User,related_name="order_zav_sklad", on_delete=models.SET_NULL, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.agent} - {self.client}"
    

class OrderPriceChange(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.BigIntegerField(default=0, blank=True, null=True)



class OrderItem(BaseModel):
    product = models.ForeignKey(ProductionProduct, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.product}"
