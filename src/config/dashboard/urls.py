from django.urls import include, path
from config.dashboard import views
from config.dashboard.user import urls as user_urls
from config.dashboard.role import urls as role_urls
from config.dashboard.product import urls as product_urls
from config.dashboard.calendar import urls as calendar_urls
from config.dashboard.client import urls as client_urls
from config.dashboard.order import urls as order_urls

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.dashboard_login, name="dashboard-login"),
    path("logout/", views.dashboard_logout, name="dashboard-logout"),
    path("setting/", views.dashboard_setting, name="setting"),
    path("norma/", views.norma, name="norma"),
    path("update-location/", views.update_location, name="update-location"),
    path("", include(user_urls)),
    path("", include(role_urls)),
    path("", include(calendar_urls)),
    path("", include(client_urls)),
    path("", include(order_urls)),
    path("product/", include(product_urls)),
]
