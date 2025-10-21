document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'es',
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        events: function(info, successCallback, failureCallback) {
            const veterinarioId = document.getElementById('filtroVeterinario').value;
            const estadoCodigo = document.getElementById('filtroEstado').value;
            
            let url = TURNOS_JSON_URL;
            const params = new URLSearchParams();
            if (veterinarioId) params.append('veterinario', veterinarioId);
            if (estadoCodigo) params.append('estado', estadoCodigo);
            if (params.toString()) url += '?' + params.toString();
            
            fetch(url)
                .then(response => response.json())
                .then(data => successCallback(data))
                .catch(error => failureCallback(error));
        },
        eventClick: function(info) {
            window.location.href = '/mascotas/turno/' + info.event.id + '/detalle-admin/';
        },
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }
    });
    
    calendar.render();
    document.getElementById('btnAplicarFiltros').addEventListener('click', function() {
        calendar.refetchEvents();
    });
});
