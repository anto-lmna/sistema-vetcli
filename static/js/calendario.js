document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'es',
        initialView: 'dayGridMonth',
        themeSystem: 'standard',
        
        height: 'auto',
        contentHeight: 'auto',
        aspectRatio: 1.8, 
        
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        
        events: TURNOS_JSON_URL,
    
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            
            if (info.event.url) {
                window.location.href = info.event.url;
            } else if (info.event.id) {
                window.location.href = '/turnos/veterinario/detalle/' + info.event.id + '/';
            }
        },
        
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false,
            hour12: false
        },
        displayEventTime: true
    });

    calendar.render();
});