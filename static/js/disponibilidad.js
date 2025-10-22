// Preview de turnos generados
// document.addEventListener('DOMContentLoaded', function() {
//     const horaInicio = document.getElementById('{{ form.hora_inicio.id_for_label }}');
//     const horaFin = document.getElementById('{{ form.hora_fin.id_for_label }}');
//     const duracion = document.getElementById('{{ form.duracion_turno.id_for_label }}');
//     const preview = document.getElementById('preview-turnos');
//     const previewText = document.getElementById('preview-text');

//     function calcularTurnos() {
//         if (!horaInicio.value || !horaFin.value || !duracion.value) return;

//         const inicio = horaInicio.value.split(':');
//         const fin = horaFin.value.split(':');
//         const minutosInicio = parseInt(inicio[0]) * 60 + parseInt(inicio[1]);
//         const minutosFin = parseInt(fin[0]) * 60 + parseInt(fin[1]);
//         const durMin = parseInt(duracion.value);

//         if (minutosFin <= minutosInicio) {
//             preview.style.display = 'none';
//             return;
//         }

//         const totalMinutos = minutosFin - minutosInicio;
//         const cantidadTurnos = Math.floor(totalMinutos / durMin);

//         previewText.innerHTML = `
//             Se generarán <strong>${cantidadTurnos} turnos</strong> de ${durMin} minutos cada uno.<br>
//             <small class="text-muted">
//                 Los clientes podrán reservar cualquiera de estos turnos para sus mascotas.
//             </small>
//         `;
//         preview.style.display = 'block';
//     }

//     horaInicio.addEventListener('change', calcularTurnos);
//     horaFin.addEventListener('change', calcularTurnos);
//     duracion.addEventListener('change', calcularTurnos);
// });

document.addEventListener("DOMContentLoaded", function () {
    const fechaInicio = document.querySelector("[name='fecha_inicio']");
    const fechaFin = document.querySelector("[name='fecha_fin']");
    const horaInicio = document.querySelector("[name='hora_inicio']");
    const horaFin = document.querySelector("[name='hora_fin']");
    const duracion = document.querySelector("[name='duracion_turno']");
    const preview = document.getElementById("preview-turnos");
    const previewText = document.getElementById("preview-text");

    function actualizarVistaPrevia() {
        const f1 = new Date(fechaInicio.value);
        const f2 = new Date(fechaFin.value);
        const h1 = horaInicio.value;
        const h2 = horaFin.value;
        const d = parseInt(duracion.value);
        if (!f1 || !f2 || !h1 || !h2 || !d) {
            preview.style.display = "none";
            return;
        }

        const diffDays = Math.floor((f2 - f1) / (1000 * 60 * 60 * 24)) + 1;
        const diffHours = (new Date(`1970-01-01T${h2}:00`) - new Date(`1970-01-01T${h1}:00`)) / (1000 * 60 * 60);
        const turnosPorDia = Math.floor((diffHours * 60) / d);
        const totalTurnos = diffDays * turnosPorDia;

        previewText.textContent = `Se crearán aproximadamente ${totalTurnos} turnos (${turnosPorDia} por día, durante ${diffDays} día${diffDays>1?"s":""}).`;
        preview.style.display = "block";
    }

    [fechaInicio, fechaFin, horaInicio, horaFin, duracion].forEach(el => {
        el.addEventListener("change", actualizarVistaPrevia);
    });
});