from django.urls import path
from .views import (
    RegistroOpcionesView,
    CustomLogoutView,
    RegistroExitosoView,
    CustomLoginView,
    ClientePreRegistroView,
    ListaClientesView,
    ListaVeterinariosView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("registro/", RegistroOpcionesView.as_view(), name="registro_opciones"),
    path(
        "registro/cliente/",
        ClientePreRegistroView.as_view(),
        name="pre_registro_cliente",
    ),
    path(
        "registro/cliente/<slug:clinica_slug>/",
        ClientePreRegistroView.as_view(),
        name="pre_registro_cliente",
    ),
    path("registro/exitoso/", RegistroExitosoView.as_view(), name="registro_exitoso"),
    path("clientes/", ListaClientesView.as_view(), name="lista_clientes"),
    path("veterinarios/", ListaVeterinariosView.as_view(), name="lista_veterinarios"),
]
