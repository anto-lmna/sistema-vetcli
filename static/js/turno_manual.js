document.addEventListener('DOMContentLoaded', function() {
    const buscarInput = document.getElementById('buscar-cliente');
    const resultadosDiv = document.getElementById('busqueda-resultados');
    const clienteSeleccionadoDiv = document.getElementById('cliente-seleccionado');
    const seccionMascotas = document.getElementById('seccion-mascotas');
    const listaMascotas = document.getElementById('lista-mascotas');
    const seccionFormulario = document.getElementById('seccion-formulario');
    
    let clienteActual = null;
    let mascotaActual = null;
    let timeoutBusqueda = null;

    // Buscar clientes mientras escribe
    buscarInput.addEventListener('input', function() {
        clearTimeout(timeoutBusqueda);
        const query = this.value.trim();
        
        if (query.length < 2) {
            resultadosDiv.innerHTML = '';
            return;
        }
        
        resultadosDiv.innerHTML = '<div class="loading"><i class="bi bi-hourglass-split"></i> Buscando...</div>';
        
        timeoutBusqueda = setTimeout(() => {
            fetch(`${BUSCAR_CLIENTES_URL}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    mostrarResultadosClientes(data.clientes);
                })
                .catch(error => {
                    resultadosDiv.innerHTML = '<div class="alert alert-danger">Error al buscar clientes</div>';
                });
        }, 300);
    });

    // Mostrar resultados de búsqueda
    function mostrarResultadosClientes(clientes) {
        if (clientes.length === 0) {
            resultadosDiv.innerHTML = '<div class="alert alert-warning">No se encontraron clientes</div>';
            return;
        }
        
        let html = '<div class="list-group">';
        clientes.forEach(cliente => {
            const numMascotas = cliente.mascotas.length;
            html += `
                <div class="list-group-item list-group-item-action cliente-card" data-cliente='${JSON.stringify(cliente)}'>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${cliente.nombre_completo}</h6>
                            <p class="mb-1 small text-muted">
                                <i class="bi bi-envelope"></i> ${cliente.email} | 
                                <i class="bi bi-telephone"></i> ${cliente.telefono}
                            </p>
                            <p class="mb-0 small">
                                <span class="badge bg-info">${numMascotas} mascota${numMascotas !== 1 ? 's' : ''}</span>
                            </p>
                        </div>
                        <i class="bi bi-chevron-right"></i>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        resultadosDiv.innerHTML = html;
        
        // Agregar eventos de click
        document.querySelectorAll('.cliente-card').forEach(card => {
            card.addEventListener('click', function() {
                const cliente = JSON.parse(this.dataset.cliente);
                seleccionarCliente(cliente);
            });
        });
    }

    // Seleccionar cliente
    function seleccionarCliente(cliente) {
        clienteActual = cliente;
        
        // Mostrar cliente seleccionado
        document.getElementById('cliente-nombre').textContent = cliente.nombre_completo;
        document.getElementById('cliente-email').textContent = cliente.email;
        document.getElementById('cliente-telefono').textContent = cliente.telefono;
        document.getElementById('cliente_id').value = cliente.id;
        
        // Ocultar búsqueda y mostrar seleccionado
        buscarInput.value = '';
        resultadosDiv.innerHTML = '';
        clienteSeleccionadoDiv.classList.remove('d-none');
        
        // Mostrar mascotas
        mostrarMascotas(cliente.mascotas);
    }

    // Mostrar mascotas del cliente
    function mostrarMascotas(mascotas) {
        if (mascotas.length === 0) {
            listaMascotas.innerHTML = '<div class="col-12"><div class="alert alert-warning">Este cliente no tiene mascotas registradas</div></div>';
            seccionMascotas.classList.remove('d-none');
            return;
        }
        
        let html = '';
        mascotas.forEach(mascota => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="mascota-option" data-mascota-id="${mascota.id}">
                        <div class="d-flex align-items-center">
                            <div class="fs-2 me-3">🐾</div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1">${mascota.nombre}</h6>
                                <p class="mb-0 small text-muted">
                                    ${mascota.especie} ${mascota.raza ? `- ${mascota.raza}` : ''}
                                </p>
                            </div>
                            <i class="bi bi-check-circle-fill text-success d-none"></i>
                        </div>
                    </div>
                </div>
            `;
        });
        
        listaMascotas.innerHTML = html;
        seccionMascotas.classList.remove('d-none');
        
        // Eventos de click en mascotas
        document.querySelectorAll('.mascota-option').forEach(option => {
            option.addEventListener('click', function() {
                // Deseleccionar otras
                document.querySelectorAll('.mascota-option').forEach(opt => {
                    opt.classList.remove('selected');
                    opt.querySelector('.bi-check-circle-fill').classList.add('d-none');
                });
                
                // Seleccionar esta
                this.classList.add('selected');
                this.querySelector('.bi-check-circle-fill').classList.remove('d-none');
                
                // Guardar ID
                mascotaActual = this.dataset.mascotaId;
                document.getElementById('mascota_id').value = mascotaActual;
                
                // Mostrar formulario
                seccionFormulario.classList.remove('d-none');
                seccionFormulario.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    }

    // Botón cambiar cliente
    document.getElementById('btn-cambiar-cliente').addEventListener('click', function() {
        clienteSeleccionadoDiv.classList.add('d-none');
        seccionMascotas.classList.add('d-none');
        seccionFormulario.classList.add('d-none');
        buscarInput.value = '';
        buscarInput.focus();
        clienteActual = null;
        mascotaActual = null;
    });

    // Limpiar búsqueda
    document.getElementById('btn-limpiar-busqueda').addEventListener('click', function() {
        buscarInput.value = '';
        resultadosDiv.innerHTML = '';
        buscarInput.focus();
    });
});