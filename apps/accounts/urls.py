from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "accounts"

urlpatterns = [
    # Autenticación
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Registro
    path("registro/", views.registro_view, name="registro_opciones"),
    path(
        "registro/cliente/",
        views.ClientePreRegistroView.as_view(),
        name="registro_cliente",
    ),
]
