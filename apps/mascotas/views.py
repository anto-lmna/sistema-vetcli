from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Mascota, Raza
from .forms import (
    MascotaClienteForm,
    MascotaAdminForm,
    InactivarMascotaForm,
    FiltroMascotasForm,
)


# ==================== VISTAS PARA CLIENTES ====================


@login_required
def mis_mascotas(request):
    """Lista las mascotas del cliente autenticado"""

    if request.user.rol != "cliente":
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")

    # Obtener mascotas del usuario
    mascotas = (
        Mascota.objects.filter(dueno=request.user)
        .select_related("especie", "raza")
        .order_by("-activo", "nombre")
    )

    # Aplicar filtros si existen
    form_filtro = FiltroMascotasForm(request.GET)
    if form_filtro.is_valid():
        buscar = form_filtro.cleaned_data.get("buscar")
        especie = form_filtro.cleaned_data.get("especie")
        sexo = form_filtro.cleaned_data.get("sexo")
        estado = form_filtro.cleaned_data.get("estado")

        if buscar:
            mascotas = mascotas.filter(nombre__icontains=buscar)

        if especie:
            mascotas = mascotas.filter(especie=especie)

        if sexo:
            mascotas = mascotas.filter(sexo=sexo)

        if estado == "activo":
            mascotas = mascotas.filter(activo=True)
        elif estado == "inactivo":
            mascotas = mascotas.filter(activo=False)

    context = {
        "mascotas": mascotas,
        "form_filtro": form_filtro,
        "total_mascotas": mascotas.count(),
        "activas": mascotas.filter(activo=True).count(),
        "inactivas": mascotas.filter(activo=False).count(),
    }

    return render(request, "mascotas/mis_mascotas.html", context)


@login_required
def agregar_mascota(request):
    """Permite al cliente agregar una nueva mascota"""

    if request.user.rol != "cliente":
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")

    if request.method == "POST":
        form = MascotaClienteForm(request.POST, request.FILES, usuario=request.user)
        if form.is_valid():
            mascota = form.save()
            messages.success(
                request, f'¡Mascota "{mascota.nombre}" agregada exitosamente!'
            )
            return redirect("mascotas:mis_mascotas")
    else:
        form = MascotaClienteForm(usuario=request.user)

    context = {"form": form, "titulo": "Agregar Nueva Mascota"}

    return render(request, "mascotas/agregar_mascota.html", context)


@login_required
def editar_mascota(request, pk):
    """Permite al cliente editar su mascota"""

    mascota = get_object_or_404(Mascota, pk=pk)

    # Verificar que el usuario sea el dueño
    if request.user != mascota.dueno:
        messages.error(request, "No tienes permiso para editar esta mascota.")
        return redirect("mascotas:mis_mascotas")

    if request.method == "POST":
        form = MascotaClienteForm(
            request.POST, request.FILES, instance=mascota, usuario=request.user
        )
        if form.is_valid():
            mascota = form.save()
            messages.success(
                request, f'Mascota "{mascota.nombre}" actualizada exitosamente.'
            )
            return redirect("mascotas:detalle_mascota", pk=mascota.pk)
    else:
        form = MascotaClienteForm(instance=mascota, usuario=request.user)

    context = {"form": form, "mascota": mascota, "titulo": f"Editar {mascota.nombre}"}

    return render(request, "mascotas/editar_mascota.html", context)


@login_required
def detalle_mascota(request, pk):
    """Muestra los detalles de una mascota"""

    mascota = get_object_or_404(
        Mascota.objects.select_related("especie", "raza", "dueno"), pk=pk
    )

    # Verificar permisos
    if request.user.rol == "cliente":
        if mascota.dueno != request.user:
            messages.error(request, "No tienes permiso para ver esta mascota.")
            return redirect("mascotas:mis_mascotas")
    elif request.user.rol not in ["admin_veterinaria", "veterinario"]:
        return HttpResponseForbidden("No tienes permiso para acceder.")

    context = {
        "mascota": mascota,
    }

    return render(request, "mascotas/detalle_mascota.html", context)


# ==================== VISTAS PARA ADMIN ====================


@login_required
def lista_mascotas_admin(request):
    """Lista todas las mascotas de la clínica (solo admin)"""

    if request.user.rol != "admin_veterinaria":
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")

    # Obtener todas las mascotas de la clínica
    mascotas = (
        Mascota.objects.filter(dueno__clinica=request.user.clinica)
        .select_related("dueno")  # ✅ Corregido: especie y raza no son FK
        .order_by("-fecha_registro")
    )

    # Aplicar filtros
    form_filtro = FiltroMascotasForm(request.GET)
    if form_filtro.is_valid():
        buscar = form_filtro.cleaned_data.get("buscar")
        especie = form_filtro.cleaned_data.get("especie")
        sexo = form_filtro.cleaned_data.get("sexo")
        estado = form_filtro.cleaned_data.get("estado")

        if buscar:
            mascotas = mascotas.filter(
                Q(nombre__icontains=buscar)
                | Q(dueno__first_name__icontains=buscar)  # ✅ Corregido
                | Q(dueno__last_name__icontains=buscar)  # ✅ Corregido
                | Q(dueno__email__icontains=buscar)
            )

        if especie:
            mascotas = mascotas.filter(especie__iexact=especie)  # ✅ Mejor con iexact

        if sexo:
            mascotas = mascotas.filter(sexo=sexo)

        if estado == "activo":
            mascotas = mascotas.filter(activo=True)
        elif estado == "inactivo":
            mascotas = mascotas.filter(activo=False)

    # Paginación
    paginator = Paginator(mascotas, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "form_filtro": form_filtro,
        "total_mascotas": mascotas.count(),
        "activas": Mascota.objects.filter(
            dueno__clinica=request.user.clinica, activo=True
        ).count(),
        "inactivas": Mascota.objects.filter(
            dueno__clinica=request.user.clinica, activo=False
        ).count(),
    }

    return render(request, "mascotas/lista_mascotas_admin.html", context)


@login_required
def crear_mascota_admin(request):
    """Permite al admin crear una mascota para un cliente"""

    if request.user.rol != "admin_veterinaria":
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")

    if request.method == "POST":
        form = MascotaAdminForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save()
            messages.success(
                request,
                f'Mascota "{mascota.nombre}" creada exitosamente para {mascota.dueno.get_full_name}.',
            )
            return redirect("mascotas:lista_mascotas_admin")
    else:
        form = MascotaAdminForm()

    context = {"form": form, "titulo": "Crear Nueva Mascota"}

    return render(request, "mascotas/crear_mascota_admin.html", context)


@login_required
def editar_mascota_admin(request, pk):
    """Permite al admin editar cualquier mascota"""

    if request.user.rol != "admin_veterinaria":
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")

    mascota = get_object_or_404(Mascota, pk=pk)

    # Verificar que la mascota pertenezca a la clínica del admin
    if mascota.dueno.clinica != request.user.clinica:
        messages.error(request, "Esta mascota no pertenece a tu clínica.")
        return redirect("mascotas:lista_mascotas_admin")

    if request.method == "POST":
        form = MascotaAdminForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            mascota = form.save()
            messages.success(
                request, f'Mascota "{mascota.nombre}" actualizada exitosamente.'
            )
            return redirect("mascotas:detalle_mascota", pk=mascota.pk)
    else:
        form = MascotaAdminForm(instance=mascota)

    context = {"form": form, "mascota": mascota, "titulo": f"Editar {mascota.nombre}"}

    return render(request, "mascotas/editar_mascota_admin.html", context)


@login_required
def inactivar_mascota(request, pk):
    """Permite al admin inactivar una mascota"""

    if request.user.rol != "admin_veterinaria":
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect("core:dashboard")

    mascota = get_object_or_404(Mascota, pk=pk)

    # Verificar que la mascota pertenezca a la clínica del admin
    if mascota.dueno.clinica != request.user.clinica:
        messages.error(request, "Esta mascota no pertenece a tu clínica.")
        return redirect("mascotas:lista_mascotas_admin")

    if request.method == "POST":
        form = InactivarMascotaForm(request.POST)
        if form.is_valid():
            fecha_fallecimiento = form.cleaned_data.get("fecha_fallecimiento")
            mascota.inactivar(fecha_fallecimiento)

            mensaje = f'Mascota "{mascota.nombre}" inactivada exitosamente.'
            if fecha_fallecimiento:
                mensaje += f' Fecha de fallecimiento: {fecha_fallecimiento.strftime("%d/%m/%Y")}'

            messages.success(request, mensaje)
            return redirect("mascotas:lista_mascotas_admin")
    else:
        form = InactivarMascotaForm()

    context = {"form": form, "mascota": mascota}

    return render(request, "mascotas/inactivar_mascota.html", context)


@login_required
def activar_mascota(request, pk):
    """Permite al admin reactivar una mascota"""

    if request.user.rol != "admin_veterinaria":
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect("core:dashboard")

    mascota = get_object_or_404(Mascota, pk=pk)

    # Verificar que la mascota pertenezca a la clínica del admin
    if mascota.dueno.clinica != request.user.clinica:
        messages.error(request, "Esta mascota no pertenece a tu clínica.")
        return redirect("mascotas:lista_mascotas_admin")

    if request.method == "POST":
        mascota.activar()
        messages.success(
            request, f'Mascota "{mascota.nombre}" reactivada exitosamente.'
        )
        return redirect("mascotas:detalle_mascota", pk=mascota.pk)

    context = {"mascota": mascota}

    return render(request, "mascotas/activar_mascota.html", context)


# ==================== VISTAS PARA VETERINARIOS ====================


@login_required
def lista_mascotas_veterinario(request):
    """Lista las mascotas de la clínica (para veterinarios)"""

    if request.user.rol != "veterinario":
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")

    # Obtener mascotas activas de la clínica
    mascotas = (
        Mascota.objects.filter(dueno__clinica=request.user.clinica)
        .select_related("dueno")  # ✅ Corregido: especie y raza no son FK
        .order_by("-fecha_registro")
    )

    # Aplicar filtros
    form_filtro = FiltroMascotasForm(request.GET)
    if form_filtro.is_valid():
        buscar = form_filtro.cleaned_data.get("buscar")
        especie = form_filtro.cleaned_data.get("especie")
        sexo = form_filtro.cleaned_data.get("sexo")

        if buscar:
            mascotas = mascotas.filter(
                Q(nombre__icontains=buscar)
                | Q(dueno__first_name__icontains=buscar)
                | Q(dueno__last_name__icontains=buscar)
                | Q(dueno__email__icontains=buscar)
            )

        if especie:
            mascotas = mascotas.filter(especie=especie)

        if sexo:
            mascotas = mascotas.filter(sexo=sexo)

    # Paginación
    paginator = Paginator(mascotas, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "form_filtro": form_filtro,
        "total_mascotas": mascotas.count(),
    }

    return render(request, "mascotas/lista_mascotas_veterinario.html", context)


# ==================== AJAX / API VIEWS ====================


@login_required
def cargar_razas(request):
    """Devuelve las razas en formato JSON según la especie seleccionada"""
    especie_id = request.GET.get("especie_id")

    if especie_id:
        razas = (
            Raza.objects.filter(especie_id=especie_id, activo=True)
            .values("id", "nombre")
            .order_by("nombre")
        )
        return JsonResponse(list(razas), safe=False)

    return JsonResponse([], safe=False)
