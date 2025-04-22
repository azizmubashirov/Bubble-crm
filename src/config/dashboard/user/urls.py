from django.urls import include, path
from . import views


urlpatterns = [
    path("user/agent/list/", views.user_agent_list, name="user-agent-list"),
    path("user/driver/list/", views.user_driver_list, name="user-driver-list"),
    path("user/zav-sklad/list/", views.user_sklad_list, name="user-zav-sklad-list"),
    path("user/accountant/list/", views.user_accountant_list, name="user-accountant-list"),
    path("user/manufacturer/list/", views.user_manufacturer_list, name="user-manufacturer-list"),
    path("user/worker/list/", views.user_worker_list, name="user-worker-list"),
    path("user/<int:role_id>/create/", views.user_create, name="user-create"),
    path("user/<int:user_id>/edit/", views.user_edit, name="user-edit"),
    path("user/my-profile/", views.my_profile, name="user-my-profile"),
    path("user/change-password/", views.change_password, name="user-change-password"),
    
    path("agent/add-plan/", views.add_plan, name="agent-add-plan"),
    path("worker/work-time/", views.work_time, name="worker-work-time"),
]