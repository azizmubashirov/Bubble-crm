from django.template.response import TemplateResponse
from config.dashboard.views import staff_member_required
from config.dashboard.decorators import role_required
from config.client.models import Client
from config.order.models import Order
from config.user.models import Notes
from django.core.serializers import serialize
from django.http import JsonResponse
from datetime import datetime

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@staff_member_required
@role_required(['agent', 'seo'])
def calendar(request):
    agent = int(request.GET.get("agent", 0))
    if is_ajax(request=request):
        original_date_string = request.POST.get('date').split()
        date_string = f"{original_date_string[0]} {original_date_string[1]} {original_date_string[2]} {original_date_string[3]}"
        date_object = datetime.strptime(date_string, "%a %b %d %Y")
        formatted_date = date_object.strftime("%Y-%m-%d")
        Notes(
            agent_id = request.user.id,
            description = request.POST.get('title'),
            date = formatted_date
        ).save()
        return JsonResponse({'success': True})
    year = datetime.now().year
    month = datetime.now().month
    if agent:
        clients = Client.objects.filter(created_at__range=(f"{year}-{month}-01", f"{year}-{month}-30"), agent_id=agent)
        orders = Order.objects.filter(created_at__range=(f"{year}-{month}-01", f"{year}-{month}-30"), agent_id=agent)
        notes = Notes.objects.filter(date__range=(f"{year}-{month}-01", f"{year}-{month}-30"), agent_id=agent)
    else:
        clients = Client.objects.filter(created_at__range=(f"{year}-{month}-01", f"{year}-{month}-30"), agent_id=request.user.id)
        orders = Order.objects.filter(created_at__range=(f"{year}-{month}-01", f"{year}-{month}-30"), agent_id=request.user.id)
        notes = Notes.objects.filter(date__range=(f"{year}-{month}-01", f"{year}-{month}-30"), agent_id=request.user.id)
    orders = serialize('json', orders)
    clients = serialize('json', clients)
    notes = serialize('json', notes)
    context = {
        'orders': orders,
        'clients': clients,
        'notes': notes
    }
    return TemplateResponse(request, 'calendar.html', context)


