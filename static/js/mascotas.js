document.addEventListener('DOMContentLoaded', function() {
    const especieSelect = document.getElementById('id_especie');
    const razaSelect = document.getElementById('id_raza');
    
    if (especieSelect && razaSelect) {
        especieSelect.addEventListener('change', function() {
            const especieId = this.value;
            
            if (!especieId) {
                razaSelect.innerHTML = '<option value="">---------</option>';
                razaSelect.disabled = true;
                return;
            }
            
            // Petición AJAX al backend (JSON) ← Aquí estaba mal indentado
            fetch(`/mascotas/ajax/cargar-razas/?especie_id=${especieId}`)
                .then(response => response.json())
                .then(data => {
                    razaSelect.innerHTML = '<option value="">---------</option>';
                    data.forEach(raza => {
                        const option = document.createElement('option');
                        option.value = raza.id;
                        option.textContent = raza.nombre;
                        razaSelect.appendChild(option);
                    });
                    razaSelect.disabled = false;
                })
                .catch(error => {
                    console.error("Error al cargar razas:", error);
                    razaSelect.innerHTML = '<option value="">Error al cargar razas</option>';
                });
        });
        
        // Trigger inicial si hay especie seleccionada
        if (especieSelect.value) {
            especieSelect.dispatchEvent(new Event('change'));
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

