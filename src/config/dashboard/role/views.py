from django.template.response import TemplateResponse
from config.user.models import Role
from config.dashboard.views import staff_member_required

@staff_member_required
def role_list(request):
    roles = Role.objects.all()
    context = {
        'roles': roles
    }
    return TemplateResponse(request, 'role/list.html', context)