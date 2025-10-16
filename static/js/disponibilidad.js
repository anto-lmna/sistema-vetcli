// Preview de turnos generados
document.addEventListener('DOMContentLoaded', function() {
    const horaInicio = document.getElementById('{{ form.hora_inicio.id_for_label }}');
    const horaFin = document.getElementById('{{ form.hora_fin.id_for_label }}');
    const duracion = document.getElementById('{{ form.duracion_turno.id_for_label }}');
    const preview = document.getElementById('preview-turnos');
    const previewText = document.getElementById('preview-text');

    function calcularTurnos() {
        if (!horaInicio.value || !horaFin.value || !duracion.value) return;

        const inicio = horaInicio.value.split(':');
        const fin = horaFin.value.split(':');
        const minutosInicio = parseInt(inicio[0]) * 60 + parseInt(inicio[1]);
        const minutosFin = parseInt(fin[0]) * 60 + parseInt(fin[1]);
        const durMin = parseInt(duracion.value);

        if (minutosFin <= minutosInicio) {
            preview.style.display = 'none';
            return;
        }

        const totalMinutos = minutosFin - minutosInicio;
        const cantidadTurnos = Math.floor(totalMinutos / durMin);

        previewText.innerHTML = `
            Se generarán <strong>${cantidadTurnos} turnos</strong> de ${durMin} minutos cada uno.<br>
            <small class="text-muted">
                Los clientes podrán reservar cualquiera de estos turnos para sus mascotas.
            </small>
        `;
        preview.style.display = 'block';
    }

    horaInicio.addEventListener('change', calcularTurnos);
    horaFin.addEventListener('change', calcularTurnos);
    duracion.addEventListener('change', calcularTurnos);
});