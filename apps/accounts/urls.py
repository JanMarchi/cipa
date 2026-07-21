from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("convites/<str:token>/", views.accept_invitation_view, name="invitation-accept"),
    path("usuarios/", views.user_list, name="user-list"),
]
