from django.template.response import TemplateResponse
from config.client.models import Client, ClientPhoneNumber
from django.db.models import Q
from django.core.paginator import Paginator
from config.dashboard.views import staff_member_required
from .forms import ClientForm
from django.shortcuts import redirect
from django.conf import settings
from config.dashboard.decorators import role_required
from config.dashboard.services import get_debtors


@staff_member_required
@role_required(['seo', 'agent'])
def client_list(request, agent_id):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    clients = Client.objects.filter(agent_id=agent_id).order_by("-id")
    if search:
        clients = clients.filter(Q(firstname__icontains=search) | Q(lastname__icontains=search) | Q(company_name__icontains=search) | Q(inn__icontains=search) | Q(email__icontains=search))
    
    paginator = Paginator(clients, entries)
    clients = paginator.page(page)
    context = {
        "clients": clients,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
    }
    if request.user_agent.is_mobile:
        return TemplateResponse(request, 'client/mobile-list.html', context)
    return TemplateResponse(request, 'client/list.html', context)



@staff_member_required
@role_required(['seo', 'agent'])
def client_create(request):
    form = ClientForm(request.POST or None, request.FILES or None, instance=Client())
    if request.POST:
        if form.is_valid():
            model = form.save()
            model.agent_id = request.user.id
            model.save()
            for value in request.POST.getlist('value'):
                ClientPhoneNumber(
                    phone_number = value,
                    client_id = model.id
                ).save()
            return redirect(f"dashboard:client-list", agent_id=request.user.id)
        else:
            print(form.errors)
    context = {
        'form': form,
    }
    # if request.user.role.slug == 'seo':
    #     return TemplateResponse(request, 'client/seo_form.html', context)
    # else:
    if request.user_agent.is_mobile:
        return TemplateResponse(request, 'client/mobile-form.html', context)
    return TemplateResponse(request, 'client/form.html', context)


@staff_member_required
@role_required(['seo', 'agent'])
def client_edit(request, client_id):
    model = Client.objects.get(pk=client_id)
    form = ClientForm(request.POST or None, request.FILES or None, instance=model)
    values = ClientPhoneNumber.objects.filter(client_id=model.id)
    if request.POST:
        if form.is_valid():
            model.agent_id = request.user.id
            model = form.save()
            for value in request.POST.getlist(f'value'):
                ClientPhoneNumber(
                    phone_number = value,
                    client_id = model.id
                ).save()
            return redirect(f"dashboard:client-list", agent_id=request.user.id)
        else:
            print(form.errors)
    context = {
        'form': form,
        'model': model,
        'MEDIA_URL': settings.MEDIA_HOST,
        'values':values
    }
    if request.user_agent.is_mobile:
        return TemplateResponse(request, 'client/mobile-edit.html', context)
    return TemplateResponse(request, 'client/edit.html', context)

@staff_member_required
@role_required(['accountant'])
def debtors_list(request):
    context = {
        'debtors': get_debtors()
    }
    return TemplateResponse(request, "debtor/list.html", context)


@staff_member_required
@role_required(['seo', 'agent'])
def client_view(request, client_id):
    model = Client.objects.filter(id=client_id).first()
    phone_numbers = ClientPhoneNumber.objects.filter(client_id=model.id)
    context = {
        'model': model,
        'phone_numbers': phone_numbers
    }
    return TemplateResponse(request, 'client/view.html', context)