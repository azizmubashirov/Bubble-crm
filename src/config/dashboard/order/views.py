from django.template.response import TemplateResponse
from config.order.models import Order, OrderItem, Payment, OrderStatus, OrderPriceChange
from config.products.models import ProductionProduct, Currency, Categories
from config.user.models import User, AgentPlan, AgentBalanceToday
from config.dashboard.product import services
from django.db.models import Q
from django.core.paginator import Paginator
from config.dashboard.views import staff_member_required
from .forms import OrderForm, PaymentForm
from django.shortcuts import redirect
from django.conf import settings
from config.dashboard.decorators import role_required
from django.http import JsonResponse
from datetime import datetime
from django.urls import reverse


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@staff_member_required
@role_required(['seo', 'agent', 'zav-sklad'])
def order_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    status = int(request.GET.get("status", 0))
    start_date_str = request.GET.get("start_date", "")
    finish_date_str = request.GET.get("finish_date", "")
    agent = int(request.GET.get("agent", 0))
    zav_sklad = int(request.GET.get("zav_sklad", 0))
    
    if start_date_str and finish_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        finish_date = datetime.strptime(finish_date_str, "%Y-%m-%d")
    else:
        start_date = finish_date = None
    
    if agent:
        orders = Order.objects.filter(agent_id=agent).order_by('-id')
    elif zav_sklad:
        orders = Order.objects.filter(zav_sklad_id=zav_sklad, status=5).order_by('-id')
    else:
        orders = Order.objects.all().order_by("-id")
    
    if search:
        orders = orders.filter(Q(id__icontains=search)).order_by('-id')
    # if payment:
    #     orders = orders.filter(payment_id=payment).order_by('-id')
    if status:
        orders = orders.filter(status=status).order_by('-id')
    if start_date and finish_date:
        orders = orders.filter(created_at__range=(start_date, finish_date)).order_by('-id')
    
    payments = Payment.objects.all()
    order_status = OrderStatus.objects.all()
    drivers = User.objects.filter(role__slug='driver')
    orders_count = orders.count()
    paginator = Paginator(orders, entries)
    orders = paginator.page(page)
    context = {
        "orders": orders,
        'orders_count':orders_count,
        'drivers': drivers,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        'payments': payments,
        # 'payment': payment,
        'status': status,
        'status_list': order_status,
        'start_date': start_date_str,
        'finish_date': finish_date_str,
        'zav_sklad_items': User.objects.filter(role__slug='zav-sklad')
    }
    if request.user_agent.is_mobile:
        return TemplateResponse(request, 'order/mobile/list.html', context)
    return TemplateResponse(request, 'order/list.html', context)

@staff_member_required
@role_required(['seo', 'agent', 'zav-sklad'])
def order_create(request):
    products = ProductionProduct.objects.filter(status=3).order_by('-id')
    if request.method == 'POST':
        form = OrderForm(request.POST or None, request.FILES or None,request=request, instance=Order(
            agent_id=request.user.id,
            status_id = 1
        ))
        if form.is_valid():
            model = form.save()       
            count = len(request.POST.getlist('product_value'))
            amount_price = 0
            for i in range(count):
                order_item = OrderItem.objects.filter(product_id=request.POST.getlist('product_value')[i], order_id=model.id).first()
                product = ProductionProduct.objects.filter(id=request.POST.getlist('product_value')[i]).first()
                if product:
                    product.amount -= float(request.POST.getlist('product_option_value')[i])
                    product.save()
                if order_item:
                    order_item.amount += float(request.POST.getlist('product_option_value')[i])
                    order_item.save()
                    amount_price += float(order_item.product.production_product.price[model.price_type]) * int(order_item.amount)
                    
                else:
                    order_item = OrderItem(
                        order = model,
                        product_id = request.POST.getlist('product_value')[i],
                        amount = request.POST.getlist('product_option_value')[i]
                    )
                    order_item.save()
                    amount_price += float(order_item.product.production_product.price[model.price_type]) * int(order_item.amount)
            
            currency_price = Currency.objects.filter(id=1).first()
            if model.discount:
                discount_price = (amount_price * float(currency_price.amount)) * (model.discount / 100)
                model.price = (amount_price * float(currency_price.amount) )- discount_price
            else :
                model.price = amount_price * float(currency_price.amount)
            if model.qqs:
                qss_price = (amount_price * float(currency_price.amount)) * (12 / 100)
                model.qqs_price = qss_price
                model.price = model.price + qss_price
            model.save()
            redirect_url = reverse(f'dashboard:order-list')
            redirect_url += f'?agent={request.user.id}'
            return redirect(redirect_url)
        else:
            print(form.errors)
    if is_ajax(request=request):
        products = ProductionProduct.objects.filter(status=3, production_product__category_id=request.POST.get('category_id')).order_by('-id')
        return TemplateResponse(request, 'order/pro.html', {'products': products})
    else:
        form = OrderForm(instance=Order(), request=request)
        
    context = {
        'products': products,
        'form':form,
        'categories': Categories.objects.all().order_by('-id')
    }
    if request.user_agent.is_mobile:
        return TemplateResponse(request, 'order/mobile/form.html', context)
    return TemplateResponse(request, 'order/form.html', context)


@staff_member_required
@role_required(['seo', 'agent', 'zav-sklad'])
def add_order(request, client_id):
    products = ProductionProduct.objects.filter(status=3).order_by('-id')
    if request.method == 'POST':
        form = OrderForm(request.POST or None, request.FILES or None,request=request, instance=Order(
            agent_id=request.user.id,
            status_id = 1
        ))
        if form.is_valid():
            model = form.save()       
            count = len(request.POST.getlist('product_value'))
            amount_price = 0
            for i in range(count):
                order_item = OrderItem.objects.filter(product_id=request.POST.getlist('product_value')[i], order_id=model.id).first()
                product = ProductionProduct.objects.filter(id=request.POST.getlist('product_value')[i]).first()
                if product:
                    product.amount -= float(request.POST.getlist('product_option_value')[i])
                    product.save()
                if order_item:
                    order_item.amount += float(request.POST.getlist('product_option_value')[i])
                    order_item.save()
                    amount_price += float(order_item.product.production_product.price[model.price_type]) * int(order_item.amount)
                    
                else:
                    order_item = OrderItem(
                        order = model,
                        product_id = request.POST.getlist('product_value')[i],
                        amount = request.POST.getlist('product_option_value')[i]
                    )
                    order_item.save()
                    amount_price += float(order_item.product.production_product.price[model.price_type]) * int(order_item.amount)
            
            currency_price = Currency.objects.filter(id=1).first()
            if model.discount:
                discount_price = (amount_price * float(currency_price.amount)) * (model.discount / 100)
                model.price = (amount_price * float(currency_price.amount) )- discount_price
            else :
                model.price = amount_price * float(currency_price.amount)
            if model.qqs:
                qss_price = (amount_price * float(currency_price.amount)) * (model.qqs / 100)
                model.qqs_price = qss_price
                model.price = (amount_price * float(currency_price.amount) ) + qss_price
            
            model.save()
            redirect_url = reverse(f'dashboard:order-list')
            redirect_url += f'?agent={request.user.id}'
            return redirect(redirect_url)
        else:
            print(form.errors)
    else:
        form = OrderForm(instance=Order(client_id=client_id), request=request)
        
    context = {
        'products': products,
        'form':form,
        'categories': Categories.objects.all().order_by('-id')
    }
    if request.user_agent.is_mobile:
        return TemplateResponse(request, 'order/mobile/form.html', context)
    
    return TemplateResponse(request, 'order/form.html', context)

@staff_member_required
@role_required(['seo', 'agent', 'driver', 'accountant', 'zav-sklad'])
def order_view(request, order_id):
    model = Order.objects.get(pk=order_id)
    order_item = OrderItem.objects.filter(order_id=model.id)
    order_prices = OrderPriceChange.objects.filter(order_id=model.id)
    payments = Payment.objects.all()
    context = {
        'model': model,
        'order_prices': order_prices,
        'payments': payments,
        'MEDIA_URL': settings.MEDIA_HOST,
        'order_item':order_item
    }
    if request.user_agent.is_mobile:
        return TemplateResponse(request, 'order/mobile/view.html', context)
    return TemplateResponse(request, 'order/view.html', context)


# @staff_member_required
# @role_required(['seo', 'agent', 'driver', 'zav-sklad', 'accountant'])
def order_invoice_chek(request, order_id):
    model = Order.objects.get(pk=order_id)
    order_item = OrderItem.objects.filter(order_id=model.id)
    context = {
        'model': model,
        'MEDIA_URL': settings.MEDIA_HOST,
        'order_item':order_item
    }
    return TemplateResponse(request, 'order/invoice-chek.html', context)

@staff_member_required
@role_required(['seo', 'agent', 'driver', 'accountant', 'zav-sklad'])
def complate_order(request, order_id):
    if is_ajax(request=request):
        model = Order.objects.get(pk=order_id)
        model.signature = request.POST.get('sign')
        OrderPriceChange(
            order_id = order_id,
            payment_id= request.POST.get('payment_type'),
            price = int(request.POST.get('price'))
        ).save()
        order_price = OrderPriceChange.objects.filter(order_id=order_id)
        total_price = 0
        for price in order_price:
            total_price += price.price
        if total_price >= model.price + model.delivery_price:
            model.status_id = 3
            order_items = OrderItem.objects.filter(order_id=order_id)
            agent_salary = 0
            for order_item in order_items:
                agent_salary += int(order_item.product.production_product.price[model.price_type]) * (int(order_item.product.production_product.price[f'percentage_{model.price_type}']) / 100) * int(order_item.amount)    
            agent_plan = AgentPlan.objects.filter(agent_id=model.agent_id, created_at__month=datetime.today().month).first()
            agent_balace = AgentBalanceToday.objects.filter(agent_id=model.agent_id, created_at__date=datetime.today().date()).first()
            if agent_balace:
                agent_balace.balance += agent_salary
                agent_balace.save()
            else:
                AgentBalanceToday(
                    balance = agent_salary,
                    agent_id =  model.agent_id,
                ).save()
            if agent_plan:
                agent_plan.balance += agent_salary
                agent_plan.save()
            else:
                AgentPlan(
                    agent_id = model.agent_id,
                    balance = agent_salary
                ).save()
        else:
            model.status_id = 4
        model.save()
        
    return redirect('dashboard:order-view', order_id=order_id)

@staff_member_required
@role_required(['seo', 'agent', 'driver', 'accountant']) 
def order_change_price(request, order_id):
    if is_ajax(request=request):
        model = Order.objects.get(pk=order_id)
        OrderPriceChange(
            order_id = order_id,
            payment_id= request.POST.get('payment_type'),
            price = int(request.POST.get('price'))
        ).save()
        order_price = OrderPriceChange.objects.filter(order_id=order_id)
        total_price = 0
        for price in order_price:
            total_price += price.price
        
        if total_price >= model.price + model.delivery_price:
            model.status_id = 3
            order_items = OrderItem.objects.filter(order_id=order_id)
            agent_salary = 0
            for order_item in order_items:
                agent_salary += int(order_item.product.production_product.price[model.price_type]) * (int(order_item.product.production_product.price[f'percentage_{model.price_type}']) / 100) * int(order_item.amount)    
            agent_plan = AgentPlan.objects.filter(agent_id=model.agent_id, created_at__month=datetime.today().month).first()
            if agent_plan:
                agent_plan.balance += agent_salary
                agent_plan.save()
            else:
                AgentPlan(
                    agent_id = model.agent_id,
                    balance = agent_salary
                ).save()
        else:
            model.status_id = 4
        model.save()
        
    return redirect('dashboard:order-view', order_id=order_id)

def take_driver(request):
    if is_ajax(request=request):
        order_list = request.POST.getlist('order_list[]')
        for order in order_list:
            order = Order.objects.filter(id=order).first()
            order.driver_id = request.POST.get('driver')
            order.delivery_price = request.POST.get('driver_price')
            order.status_id = 2
            order.save()
        return JsonResponse({'status': True})

def give_zav_sklad(request):
    if is_ajax(request=request):
        order_list = request.POST.getlist('order_list[]')
        for order in order_list:
            order = Order.objects.filter(id=order).first()
            order.zav_sklad_id = request.POST.get('zav_sklad')
            order.status_id = 5
            order.save()
        return JsonResponse({'status': True})
    
@staff_member_required
@role_required(['seo'])  
def payment_list(request):
    payments = Payment.objects.all().order_by('-id')
    context = {
        'payments': payments
    }
    return TemplateResponse(request, 'payment/list.html', context)

@staff_member_required
@role_required(['seo'])
def payment_create(request):
    form = PaymentForm(request.POST or None, instance=Payment())
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect('dashboard:payment-list')
        else:
            print(form.errors)
    context = {
        'form': form
    }
    return TemplateResponse(request, 'payment/form.html', context)

@staff_member_required
@role_required(['seo'])
def payment_edit(request, payment_id):
    model = Payment.objects.filter(id=payment_id).first()
    form = PaymentForm(request.POST or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect('dashboard:payment-list')
        else:
            print(form.errors)
    context = {
        'form': form
    }
    return TemplateResponse(request, 'payment/form.html', context)


@staff_member_required
@role_required(['seo', 'agent', 'driver', 'zav-sklad'])
def driver_order_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    status = int(request.GET.get("status", 0))
    start_date_str = request.GET.get("start_date", "")
    finish_date_str = request.GET.get("finish_date", "")
    agent = int(request.GET.get("agent", 0))
    driver = int(request.GET.get("driver", 0))
    
    if start_date_str and finish_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        finish_date = datetime.strptime(finish_date_str, "%Y-%m-%d")
    else:
        start_date = finish_date = None
        
    if agent:
        orders = Order.objects.filter(agent_id=agent, status_id=2).order_by('-id')
    elif driver:
        orders = Order.objects.filter(driver_id=driver, status_id=2).order_by('-id')
    else:
        orders = Order.objects.filter(status_id=2).order_by("-id")
    
    if search:
        orders = orders.filter(Q(id__icontains=search, status_id=2)).order_by('-id')
    if status:
        orders = orders.filter(status=status).order_by('-id')
    if start_date and finish_date:
        orders = orders.filter(created_at__range=(start_date, finish_date)).order_by('-id')
    
    payments = Payment.objects.all()
    order_status = OrderStatus.objects.all()
    drivers = User.objects.filter(role__slug='driver')
    paginator = Paginator(orders, entries)
    orders = paginator.page(page)
    context = {
        "orders": orders,
        'drivers': drivers,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        'payments': payments,
        # 'payment': payment,
        'status': status,
        'status_list': order_status,
        'start_date': start_date_str,
        'finish_date': finish_date_str,
        'order_type': 2,
    }
    if request.user.role.slug in ['agent', 'zav-sklad']:
        if request.user_agent.is_mobile:
            return TemplateResponse(request, 'driver/mobile/driver-list.html', context)
        return TemplateResponse(request, 'driver/driver-list.html', context)
    else:
        if request.user_agent.is_mobile:
            return TemplateResponse(request, 'driver/mobile/list.html', context)
        return TemplateResponse(request, 'driver/list.html', context)

@staff_member_required
@role_required(['seo', 'accountant'])
def order_payment_history(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    items = OrderPriceChange.objects.filter(order__isnull=False)
    paginator = Paginator(items, entries)
    items = paginator.page(page)
    context = {
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        'items':items
    }
    return TemplateResponse(request, 'order/payment-history.html', context)


