from django.template.response import TemplateResponse
from config.user.models import User, Role, AgentInformation, AgentPlan, WorkerTime
from django.db.models import Q
from django.core.paginator import Paginator
from config.dashboard.views import staff_member_required
from .forms import UserForm, UserProfileForm, AgentInformationForm

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.conf import settings
from config.dashboard.decorators import role_required
from datetime import datetime
from django.http import JsonResponse


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@staff_member_required
@role_required(['seo', 'accountant'])
def user_agent_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    role = Role.objects.filter(Q(name__icontains='agent')).first()
    users = User.objects.filter(role_id=role.id, is_superuser=False).order_by("-id")
    paginator = Paginator(users, entries)
    users = paginator.page(page)
    context = {
        "users": users,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        'role_id': role.id,
    }
    if request.user.role.slug == 'accountant':
        return TemplateResponse(request, 'user/agent-balance.html', context)
    return TemplateResponse(request, 'user/list.html', context)

@staff_member_required
@role_required(['seo', 'agent'])
def user_driver_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    role = Role.objects.filter(Q(name__icontains='driver')).first()
    users = User.objects.filter(role_id=role.id, is_superuser=False).order_by("-id")
    paginator = Paginator(users, entries)
    users = paginator.page(page)
    context = {
        "users": users,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        'role_id': role.id
    }
    return TemplateResponse(request, 'user/list.html', context)
@staff_member_required
@role_required(['seo'])
def user_sklad_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    role = Role.objects.filter(Q(name__icontains='zav sklad')).first()
    users = User.objects.filter(role_id=role.id, is_superuser=False).order_by("-id")
    paginator = Paginator(users, entries)
    users = paginator.page(page)
    context = {
        "users": users,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        'role_id': role.id
    }
    return TemplateResponse(request, 'user/list.html', context)

@staff_member_required
@role_required(['seo'])
def user_accountant_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    role = Role.objects.filter(Q(name__icontains='buxgalter')).first()
    users = User.objects.filter(role_id=role.id, is_superuser=False).order_by("-id")
    paginator = Paginator(users, entries)
    users = paginator.page(page)
    context = {
        "users": users,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        'role_id': role.id
    }
    return TemplateResponse(request, 'user/list.html', context)

@staff_member_required
@role_required(['seo'])
def user_manufacturer_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    role = Role.objects.filter(Q(name__icontains='Ishlab chiqaruvchi')).first()
    users = User.objects.filter(role_id=role.id, is_superuser=False).order_by("-id")
    paginator = Paginator(users, entries)
    users = paginator.page(page)
    context = {
        "users": users,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        'role_id': role.id
    }
    return TemplateResponse(request, 'user/list.html', context)

@staff_member_required
@role_required(['seo', 'manufacturer'])
def user_worker_list(request):
    if is_ajax(request=request):
        worker_time = WorkerTime.objects.filter(date=datetime.now().date()).first()
        if worker_time:
            worker_time.hour = request.POST.get('hour')
            worker_time.save()
        else:
            WorkerTime.objects.create(
                worker_id = request.POST.get('worker'),
                hour = request.POST.get('hour')
            )
        return JsonResponse({'success': True})
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    role = Role.objects.filter(Q(name__icontains='Ishchi')).first()
    users = User.objects.filter(role_id=role.id, is_superuser=False).order_by("-id")
    paginator = Paginator(users, entries)
    users = paginator.page(page)
    context = {
        "users": users,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        'role_id': role.id
    }
    return TemplateResponse(request, 'user/list.html', context)

@staff_member_required
@role_required(['seo', 'manufacturer'])
def user_create(request, role_id):
    role = Role.objects.filter(id=role_id).first()
    if role.slug in ['agent', 'worker']:
        form = UserForm(request.POST or None, request.FILES or None, instance=User())
        agent_form = AgentInformationForm(request.POST or None, request.FILES or None, instance=AgentInformation())
        if request.POST:
            image = ""
            if request.FILES:
                path = default_storage.save(f"files/{request.FILES['file']}",
                                            ContentFile(request.FILES["file"].read()))
                image = f"/media/{path}"
            form = UserForm(request.POST or None, request.FILES or None, instance=User(
                role=role,
                image=image
            ))
            if form.is_valid():
                model = form.save()
                agent_form = AgentInformationForm(request.POST or None, request.FILES or None, instance=AgentInformation(
                    agent_id=model.id
                ))
                if agent_form.is_valid():
                    agent_form.save()
                    return redirect(f"dashboard:user-{role.slug}-list")
                else:
                    print(agent_form.errors)
            else:
                print(form.errors)
                
        context = {
            'form': form,
            'agent_form': agent_form,
            'role_id': role_id
        }
        return TemplateResponse(request, 'user/agent_create.html', context)
    else:
        form = UserForm(request.POST or None, request.FILES or None, instance=User())
        if request.POST:
            image = ""
            if request.FILES:
                path = default_storage.save(f"files/{request.FILES['file']}",
                                            ContentFile(request.FILES["file"].read()))
                image = f"/media/{path}"
            form = UserForm(request.POST or None, request.FILES or None, instance=User(
                role=role,
                image=image
            ))
            if form.is_valid():
                form.save()
                return redirect(f"dashboard:user-{role.slug}-list")
            else:
                print(form.errors)
        context = {
            'form': form,
            'role_id': role_id
        }
        return TemplateResponse(request, 'user/create.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer'])
def user_edit(request, user_id):
    model = User.objects.get(pk=user_id)
    if model.role.slug in ['agent', 'worker']:
        form = UserForm(request.POST or None, request.FILES or None, instance=model)
        agent_model = AgentInformation.objects.filter(agent_id=model.id).first()
        agent_form = AgentInformationForm(request.POST or None, request.FILES or None, instance=agent_model)
        if request.POST:
            if request.FILES:
                path = default_storage.save(f"files/{request.FILES['file']}",
                                            ContentFile(request.FILES["file"].read()))
                model.image = f"/media/{path}"
            if form.is_valid():
                model = form.save()
                if agent_form.is_valid():
                    agent_form.save()
                    return redirect(f"dashboard:user-{model.role.slug}-list")
                else:
                    print(agent_form.errors)
            else:
                print(form.errors)
                
        context = {
            'form': form,
            'agent_form': agent_form,
            'model': model,
            'MEDIA_URL': settings.MEDIA_HOST,
        }
        return TemplateResponse(request, 'user/agent_edit.html', context)
    else:
        form = UserForm(request.POST or None, request.FILES or None, instance=model)
        if request.POST:
            if request.FILES:
                path = default_storage.save(f"files/{request.FILES['file']}",
                                            ContentFile(request.FILES["file"].read()))
                model.image = f"/media/{path}"
            if form.is_valid():
                user = form.save()
                return redirect(f"dashboard:user-{user.role.slug}-list")
            else:
                print(form.errors)
        context = {
            'form': form,
            'model': model,
            'MEDIA_URL': settings.MEDIA_HOST,
        }
        return TemplateResponse(request, 'user/edit.html', context)

@staff_member_required
def my_profile(request):
    model = User.objects.get(pk=request.user.id)
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST:
        if request.FILES:
            path = default_storage.save(f"files/{request.FILES['file']}",
                                        ContentFile(request.FILES["file"].read()))
            model.image = f"/media/{path}"
        if form.is_valid():
            form.save()
            return redirect(f"dashboard:dashboard")
        else:
            print(form.errors)
    context = {
        'form': form,
        'model': model,
        'MEDIA_URL': settings.MEDIA_HOST,
        'role_list': Role.objects.all()
    }
    return TemplateResponse(request, 'user/profile_edit.html', context)

@role_required(['seo', 'accountant'])
@staff_member_required
def work_time(request):
    start_date_str = request.GET.get("start_date", "")
    finish_date_str = request.GET.get("finish_date", "")
    if start_date_str and finish_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        finish_date = datetime.strptime(finish_date_str, "%Y-%m-%d")
    else:
        start_date = finish_date = None
    role = Role.objects.filter(Q(name__icontains='Ishchi')).first()
    users = User.objects.filter(role_id=role.id, is_superuser=False).order_by("-id")
    context = {
        "users": users,
        "MEDIA_URL": settings.MEDIA_HOST,
        'start_date': start_date_str,
        'finish_date': finish_date_str,
    }
    return TemplateResponse(request, 'user/work-time-list.html', context)

@staff_member_required
def change_password(request):
    if request.POST:
        user = User.objects.filter(id=request.user.id).first()
        pass1 = request.POST.get('newpassword')
        pass2 = request.POST.get('confirmpassword')
        if pass1 == pass2:
            user.set_password(pass1)
            user.save()
            return redirect('dashboard:dashboard')
        
        

def add_plan(request):
    if is_ajax(request=request):
        price = request.POST.get('plan_price')
        agent_id = request.POST.get('agent_id')
        agent_plan = AgentPlan.objects.filter(agent_id=agent_id, created_at__month=datetime.today().month).first()
        if agent_plan:
            agent_plan.plan = price
            agent_plan.save()
        else:
            AgentPlan(
                agent_id = agent_id,
                plan = price
            ).save()
        return JsonResponse({'success': True})
