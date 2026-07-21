from django.urls import path

from apps.audit import views

urlpatterns = [path("", views.event_list, name="audit-event-list")]
