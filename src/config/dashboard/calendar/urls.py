from django.urls import include, path
from . import views


urlpatterns = [
    path("calendar/", views.calendar, name="calendar"),
]