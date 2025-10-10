// document.addEventListener('DOMContentLoaded', function() {
//     const especieSelect = document.getElementById('id_especie');
//     const razaSelect = document.getElementById('id_raza');
    
//     if (especieSelect && razaSelect) {
//         especieSelect.addEventListener('change', function() {
//             const especieId = this.value;
            
//             if (!especieId) {
//                 razaSelect.innerHTML = '<option value="">---------</option>';
//                 razaSelect.disabled = true;
//                 return;
//             }
            
//             // Petición AJAX al backend (JSON) ← Aquí estaba mal indentado
//             fetch(`/mascotas/ajax/cargar-razas/?especie_id=${especieId}`)
//                 .then(response => response.json())
//                 .then(data => {
//                     razaSelect.innerHTML = '<option value="">---------</option>';
//                     data.forEach(raza => {
//                         const option = document.createElement('option');
//                         option.value = raza.id;
//                         option.textContent = raza.nombre;
//                         razaSelect.appendChild(option);
//                     });
//                     razaSelect.disabled = false;
//                 })
//                 .catch(error => {
//                     console.error("Error al cargar razas:", error);
//                     razaSelect.innerHTML = '<option value="">Error al cargar razas</option>';
//                 });
//         });
        
//         // Trigger inicial si hay especie seleccionada
//         if (especieSelect.value) {
//             especieSelect.dispatchEvent(new Event('change'));
//         }
//     }
    
//     // Preview de imagen
//     const fotoInput = document.querySelector('input[type="file"][accept="image/*"]');
//     if (fotoInput) {
//         fotoInput.addEventListener('change', function(e) {
//             const file = e.target.files[0];
//             if (file) {
//                 const reader = new FileReader();
//                 reader.onload = function(e) {
//                     let preview = document.getElementById('foto-preview');
//                     if (!preview) {
//                         preview = document.createElement('img');
//                         preview.id = 'foto-preview';
//                         preview.className = 'img-thumbnail mt-2';
//                         preview.style.maxWidth = '200px';
//                         fotoInput.parentNode.appendChild(preview);
//                     }
//                     preview.src = e.target.result;
//                 };
//                 reader.readAsDataURL(file);
//             }
//         });
//     }
// });

document.addEventListener('DOMContentLoaded', function() {
    const especieSelect = document.getElementById('id_especie');
    const razaSelect = document.getElementById('id_raza');
    
    if (especieSelect && razaSelect) {
        const razaOriginalId = razaSelect.value;
        const razaOriginalText = razaSelect.options[razaSelect.selectedIndex]?.text || '';

        console.log('🔍 Valores originales:', {
            especie: especieSelect.value,
            raza: razaOriginalId,
            razaTexto: razaOriginalText
        });

        function cargarRazas(especieId, mantenerSeleccion = true) {
            if (!especieId) {
                razaSelect.innerHTML = '<option value="">---------</option>';
                razaSelect.disabled = true;
                return;
            }

            razaSelect.innerHTML = '<option value="">Cargando razas...</option>';
            razaSelect.disabled = true;

            fetch(`/mascotas/ajax/cargar-razas/?especie_id=${especieId}`)
                .then(response => response.json())
                .then(data => {
                    razaSelect.innerHTML = '<option value="">---------</option>';

                    data.forEach(raza => {
                        const option = document.createElement('option');
                        option.value = raza.id;
                        option.textContent = raza.nombre;

                        if (mantenerSeleccion && String(raza.id) === String(razaOriginalId)) {
                            option.selected = true;
                            console.log('✅ Raza restaurada:', raza.nombre);
                        }

                        razaSelect.appendChild(option);
                    });

                    razaSelect.disabled = false;
                })
                .catch(error => {
                    console.error("Error al cargar razas:", error);
                    razaSelect.innerHTML = '<option value="">Error al cargar razas</option>';
                    razaSelect.disabled = true;
                });
        }

        especieSelect.addEventListener('change', function() {
            cargarRazas(this.value, false);
        });

        // Solo recargar razas si el select está vacío
        if (especieSelect.value && razaSelect.options.length <= 1) {
            cargarRazas(especieSelect.value, true);
        }
    }

    // Preview de imagen
    const fotoInput = document.querySelector('input[type="file"][accept="image/*"]');
    if (fotoInput) {
        fotoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = document.getElementById('foto-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'foto-preview';
                        preview.className = 'img-thumbnail mt-2';
                        preview.style.maxWidth = '200px';
                        fotoInput.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
});


