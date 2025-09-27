from django.urls import path
from .views import ClinicaDetailView
from apps.accounts.views import ClientePreRegistroView

app_name = "clinicas"

urlpatterns = [
    path("<slug:slug>/", ClinicaDetailView.as_view(), name="detalle"),
    path(
        "<slug:slug>/registro/cliente/",
        ClientePreRegistroView.as_view(),
        name="pre_registro",
    ),
]
