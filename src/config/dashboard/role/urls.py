from django.urls import include, path
from . import views


urlpatterns = [
    path("role/list/", views.role_list, name="role-list"),
]