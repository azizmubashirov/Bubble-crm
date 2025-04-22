from django import template
from config.user.models import User, RoleAccess, Role, AgentPlan, WorkerTime
from config.order.models import OrderItem, Order
from config.products.models import Currency, ProductionProductStockItem, ProductionProduct
from config.client.models import ClientPhoneNumber
from datetime import datetime
import re
from django.db.models import Count, Sum
register = template.Library()


@register.filter
def calculation_role(role_id):
    return User.objects.filter(role_id=role_id).count()

@register.filter
def role_access(role_id):
    return RoleAccess.objects.filter(role_id=role_id)

@register.filter
def role_list():
    return Role.objects.all().order_by('-id')


@register.filter
def role_list():
    return Role.objects.all().order_by('-id')

@register.simple_tag
def total_product_price(qty, price):
    print(qty)
    currency = Currency.objects.filter(id=1).first()
    price = float(qty) * (float(price) * float(currency.amount))
    return price_format(price)


@register.simple_tag
def total_price(order_item, type):
    total = 0
    currency = Currency.objects.filter(id=1).first()
    for item in order_item:
        if type == 'A':
            total += float(item.product.production_product.price['A']) * float(item.amount)
        elif type == 'B':
            total += float(item.product.production_product.price['B']) * float(item.amount)
        elif type == 'C':
            total += float(item.product.production_product.price['C']) * float(item.amount)
    return price_format(total * float(currency.amount) )


@register.simple_tag
def discount_price(order_item, type, discount):
    total = 0
    currency = Currency.objects.filter(id=1).first()
    for item in order_item:
        if type == 'A':
            total += float(item.product.production_product.price['A']) * float(item.amount)
        elif type == 'B':
            total += float(item.product.production_product.price['B']) * float(item.amount)
        elif type == 'C':
            total += float(item.product.production_product.price['C']) * float(item.amount)
            
    discount_price = (total * float(currency.amount)) * (discount / 100)
    return price_format(discount_price)


@register.simple_tag
def total(price, discount, delivery_price):
    total = price
    total += delivery_price
    return price_format(total)

@register.filter
def get_plan(user_id):
    agent = AgentPlan.objects.filter(agent_id=user_id, created_at__month=datetime.today().month).first()
    if agent:
        return price_format(agent.plan)
    else:
        return 0


@register.simple_tag
def get_debtor_price(order_prices, total, delivery_price): 
    price = 0
    for order_price in order_prices:
        price += order_price.price
    return price_format((total+delivery_price) - price)



@register.filter
def price_format(inp):
    try:
        price = int(inp)
        res = "{:,}".format(price)
        formated = re.sub(",", " ", res)
        return formated
    except: 
        return inp


@register.filter
def stock_item(product_id):
    return ProductionProductStockItem.objects.filter(production_product_id=product_id)

@register.filter
def norma_cal(product_id):
    product = ProductionProduct.objects.filter(id=product_id).first()
    norma = product.production_product.norm * product.amount_old
    if  norma == product.amount_m:
        return f"""<span class="badge badge-light-primary fw-semibold me-1">0 м²</span>"""
    elif norma > product.amount_m:
        return f"""<span class="badge badge-light-danger fw-semibold me-1">-{norma-product.amount_m} м²</span>"""
    elif norma < product.amount_m:
        return f"""<span class="badge badge-light-success fw-semibold me-1">+{product.amount_m-norma} м²</span>"""
    

@register.filter
def client_phone_number(client_id):
    client = ClientPhoneNumber.objects.filter(client_id=client_id).last()
    return client
   
   
@register.simple_tag
def work_time_today(user_id, start_date_str=None, finish_date_str=None):
    if start_date_str and finish_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        finish_date = datetime.strptime(finish_date_str, "%Y-%m-%d")
    else:
        start_date = finish_date = None
    
    if start_date and finish_date:
        work_time = WorkerTime.objects.filter(date__range=(start_date, finish_date), worker_id=user_id).values('hour').aggregate(total_hour=Sum('hour'))
        return work_time['total_hour'] if work_time.get('total_hour') else 0
    else:
        work_time = WorkerTime.objects.filter(date=datetime.now().date(), worker_id=user_id).first()
        return work_time.hour if work_time else 0
    

@register.filter
def cal_qqs(order_id):
    order = Order.objects.filter(id=order_id).first()
    if order and order.qqs:
        return order.qqs
    else:
        return 0
