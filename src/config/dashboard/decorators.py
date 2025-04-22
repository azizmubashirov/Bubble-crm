from functools import wraps
from django.http import HttpResponseForbidden
from config.user.models import Role


def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            role = Role.objects.filter(id=user.role_id).first()
            role = role.slug
            print(role)
            if role in roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You don't have permission to access this page.")

        return _wrapped_view

    return decorator
