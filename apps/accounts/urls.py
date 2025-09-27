from django.urls import path
from .views import (
    registro_view,
    logout_view,
    RegistroExitosoView,
    CustomLoginView,
    ClientePreRegistroView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("registro/", registro_view, name="registro_opciones"),
    path("registro-exitoso/", RegistroExitosoView.as_view(), name="registro_exitoso"),
    path(
        "pre-registro/<slug:clinica_slug>/",
        ClientePreRegistroView.as_view(),
        name="pre_registro_cliente",
    ),
]
