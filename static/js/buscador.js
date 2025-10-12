document.addEventListener('DOMContentLoaded', function() {
    // 1. Obtener elementos necesarios
    const inputBusqueda = document.getElementById('buscarClinica');
    const listado = document.getElementById('listadoClinicas');
    const mensajeNoEncontrado = document.getElementById('noEncontrado');
    
    // Contenedor que agrupa el título "Veterinarias Disponibles", la lista y la paginación
    const seccionClinicasVisibles = document.getElementById('seccionClinicasVisibles');

    // Solo ejecutar la lógica si los elementos clave existen en la página
    if (inputBusqueda && listado && seccionClinicasVisibles) {
        
        const items = listado.children;
        // Detectar si los ítems son columnas (formato Home) o ítems de lista (formato Opciones)
        const esFormatoColumna = listado.classList.contains('row'); 

        inputBusqueda.addEventListener('keyup', function() {
            const filtro = inputBusqueda.value.toLowerCase();
            let contadorVisible = 0;

            for (let i = 0; i < items.length; i++) {
                const nombreElemento = items[i].querySelector('.nombre-clinica strong');
                
                if (nombreElemento) {
                    const nombreClinica = nombreElemento.textContent.toLowerCase();
                    
                    if (nombreClinica.includes(filtro)) {
                        items[i].style.display = esFormatoColumna ? 'block' : 'flex';
                        contadorVisible++;
                    } else {
                        items[i].style.display = 'none'; 
                    }
                }
            }
            
            // 2. Lógica para mostrar/ocultar el mensaje y la sección principal
            if (contadorVisible === 0) {
                // No se encontraron resultados:
                // Ocultar toda la sección de clínicas
                seccionClinicasVisibles.style.display = 'none';
                
                // Mostrar el mensaje de "No encontrado"
                if (mensajeNoEncontrado) {
                    mensajeNoEncontrado.classList.remove('d-none');
                }
            } else {
                // Se encontraron resultados:
                // Mostrar toda la sección de clínicas
                seccionClinicasVisibles.style.display = 'block';
                
                // Ocultar el mensaje de "No encontrado"
                if (mensajeNoEncontrado) {
                    mensajeNoEncontrado.classList.add('d-none');
                }
            }
        });
    }
});
