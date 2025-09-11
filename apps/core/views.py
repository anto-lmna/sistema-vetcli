# apps/core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home_view(request):
    """Página de inicio - redirige según el estado del usuario"""
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/home.html")


@login_required
def dashboard_view(request):
    """Dashboard genérico - redirige según el rol del usuario"""
    user = request.user
    if user.is_admin_veterinaria:
        return redirect("core:dashboard_admin")
    elif user.is_veterinario:
        return redirect("core:dashboard_veterinario")
    elif user.is_cliente:
        return redirect("core:dashboard_cliente")
    return render(request, "core/dashboard.html")


@login_required
def dashboard_admin_view(request):
    """Dashboard para administradores de veterinaria"""
    if not request.user.is_admin_veterinaria:
        return redirect("core:dashboard")

    return render(
        request,
        "core/dashboard_admin.html",
        {
            "user": request.user,
        },
    )


@login_required
def dashboard_veterinario_view(request):
    """Dashboard para veterinarios"""
    if not request.user.is_veterinario:
        return redirect("core:dashboard")

    return render(
        request,
        "core/dashboard_veterinario.html",
        {
            "user": request.user,
        },
    )


@login_required
def dashboard_cliente_view(request):
    """Dashboard para clientes"""
    if not request.user.is_cliente:
        return redirect("core:dashboard")

    return render(
        request,
        "core/dashboard_cliente.html",
        {
            "user": request.user,
        },
    )
