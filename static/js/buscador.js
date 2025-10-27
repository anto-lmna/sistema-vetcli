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

$(document).ready(function() {
    // --- Configuración de Selectores ---
    const $password1Input = $('#id_password1');
    const $password2Input = $('#id_password2');

    // Los help_text de Crispy Forms tienen el ID con el sufijo "_helptext"
    const $password1HelpText = $('#id_password1_helptext');
    const $password2HelpText = $('#id_password2_helptext');

    // --- Lógica de Ocultamiento Inicial ---
    // Oculta las reglas de la contraseña 1 y el texto de ayuda de la 2 al cargar
    $password1HelpText.hide();
    $password2HelpText.hide();

    // --- Lógica de Interacción para Contraseña 1 (Reglas de Complejidad) ---

    // Mostrar reglas al enfocar (focus) el campo
    $password1Input.on('focus', function() {
        // Usamos slideDown para una transición suave
        $password1HelpText.slideDown(200);
    });

    // Ocultar reglas al desenfocar (blur) si el campo está vacío
    $password1Input.on('blur', function() {
        if ($(this).val().trim() === '') {
            $password1HelpText.slideUp(200);
        }
    });

    // --- Lógica de Interacción para Contraseña 2 (Confirmación) ---

    // Mostrar mensaje de confirmación cuando el usuario enfoca
    $password2Input.on('focus', function() {
        $password2HelpText.slideDown(200);
    });

    // Ocultar si el campo de confirmación se desenfoca y está vacío
    $password2Input.on('blur', function() {
        if ($(this).val().trim() === '') {
            $password2HelpText.slideUp(200);
        }
    });
});