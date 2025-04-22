from django.template.response import TemplateResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.admin.views.decorators import (
    staff_member_required as _staff_member_required,
)
from .decorators import role_required
from config.user.models import User, AgentPlan, UserLocation, AgentBalanceToday
from config.order.models import Order, OrderPriceChange
from config.client.models import Client
from config.products.models import Currency, ProductionProductInfo, ProductionProduct
from django.urls import reverse
from datetime import datetime
from django.db.models import Count, Sum
from django.utils import timezone
import re
from django.db.models.functions import TruncMonth
import json
from django.core.serializers.json import DjangoJSONEncoder
from .services import get_debtors, get_debtors_count, get_today_production_products_income
from config.dashboard.product.forms import CurrencyForm
from django.core.paginator import Paginator


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def staff_member_required(f):
    return _staff_member_required(f, login_url="dashboard:dashboard-login")


@staff_member_required
@role_required(['seo', 'agent', 'manufacturer', 'accountant', 'zav-sklad', 'driver'])
def dashboard(request):
    if request.user.role.slug == 'agent':
        context = {
            'agent_balance': AgentPlan.objects.filter(agent_id=request.user.id,
                                                      created_at__month=datetime.today().month).first(),
            'client_count': Client.objects.filter(agent_id=request.user.id).count(),
            'clients': Client.objects.filter(agent_id=request.user.id).order_by('-id')[:7],
            'agent_today_price': AgentBalanceToday.objects.filter(agent_id=request.user.id, created_at__date=datetime.today().date()).first()
        }
        if request.user_agent.is_mobile:
            return TemplateResponse(request, "mobile-agent-index.html", context)
        return TemplateResponse(request, "agent-index.html", context)
    elif request.user.role.slug == 'manufacturer':
        return redirect('dashboard:user-worker-list')
    elif request.user.role.slug == 'zav-sklad':
        return redirect('dashboard:production-product-list')
    elif request.user.role.slug == 'driver':
        redirect_url = reverse(f'dashboard:driver-order-list')
        redirect_url += f'?driver={request.user.id}'
        return redirect(redirect_url)
    total_today_amount = OrderPriceChange.objects.filter(created_at__date=timezone.now().date()).values(
        'price').aggregate(total_price=Sum('price'))
    today_order = Order.objects.filter(created_at__date=timezone.now().date()).count()
    last_5_months = Order.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(
        total_orders=Count('id'),
        total_price=Sum('price')
    ).order_by('-month')[:5]
    last_5_months = [
        {
            'month': entry['month'].strftime('%B'),
            'total_orders': entry['total_orders'],
            'total_price': entry['total_price'],
        }
        for entry in last_5_months
    ]
    last_5_months_serialized = json.dumps(last_5_months, cls=DjangoJSONEncoder)
    context = {
        'today_total_price': price_format(total_today_amount['total_price'] or 0),
        'today_order': price_format(today_order or 0),
        'last_5_months': last_5_months_serialized,
        'debtors': get_debtors(),
        'debtors_count': get_debtors_count(),
        'income_price': get_today_production_products_income()
    }
    return TemplateResponse(request, "index.html", context)


def dashboard_login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            founded_user = User.objects.filter(id=user.id).first()
            founded_user.access_time = timezone.now()
            founded_user.save()
            login(request, user)

            return redirect('dashboard:dashboard')
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


@login_required
def dashboard_logout(request):
    auth.logout(request)
    return redirect('dashboard:dashboard-login')


def error_404(request, exception):
    return render(request, "page404.html", status=404)


def price_format(inp):
    price = int(inp)
    res = "{:,}".format(price)
    formated = re.sub(",", " ", res)
    return formated


@staff_member_required
@role_required(['seo'])
def dashboard_setting(request):
    currency = Currency.objects.filter(id=1).first()
    form = CurrencyForm(request.POST or None, instance=currency)
    if request.POST:
        if form.is_valid():
            data = form.save()
            return redirect(f"dashboard:dashboard")
        else:
            print(form.errors)
    context = {
        'form': form
    }
    return TemplateResponse(request, 'setting.html', context)


def update_location(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        user_profile = UserLocation.objects.filter(user=request.user).first()
        if user_profile:
            user_profile.lat = latitude
            user_profile.lon = longitude
            user_profile.save()
        else:
            UserLocation.objects.create(
                user=request.user,
                lat=latitude,
                lon=longitude
            )

        return JsonResponse({'message': 'Location updated successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@staff_member_required
@role_required(['seo'])
def norma(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    products = ProductionProductInfo.objects.all().order_by("-id")
    prepack_item = ProductionProduct.get_records_for_current_month()
    paginator = Paginator(prepack_item, entries)
    prepack_item = paginator.page(page)
    context = {
        'products': products,
        'prepack_item': prepack_item,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
    }
    return TemplateResponse(request, 'norma-list.html', context)