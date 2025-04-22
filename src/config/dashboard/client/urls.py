from django.urls import include, path
from . import views


urlpatterns = [
    path("client/list/<int:agent_id>/", views.client_list, name="client-list"),
    path("client/create/", views.client_create, name="client-create"),
    path("client/<int:client_id>/edit/", views.client_edit, name="client-edit"),
    path("client/<int:client_id>/view/", views.client_view, name="client-view"),
    path("debtors/list/", views.debtors_list, name="debtors-list"),
]