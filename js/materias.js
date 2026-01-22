let materiasInscritas = [];
const maxMaterias = 3;

// 1. Inicializar el primer botón de agregar
function renderizarBotones() {
    const container = document.getElementById('materias-container');
    container.innerHTML = ''; // Limpiar

    // Dibujar las materias ya inscritas
    materiasInscritas.forEach(materia => {
        container.innerHTML += `
            <div style="background:#e74c3c; color:white; padding:20px; border-radius:15px; width:250px; text-align:center;">
                <span style="display:block">📚</span>
                <strong>${materia}</strong><br>
                <small>Estado: Inscrita correctamente</small>
            </div>`;
    });

    // Mostrar botón de "Agregar" solo si hay menos de 3
    if (materiasInscritas.length < maxMaterias) {
        container.innerHTML += `
            <div onclick="abrirModal()" style="background:#e74c3c; color:white; padding:20px; border-radius:15px; width:250px; text-align:center; cursor:pointer; opacity:0.9;">
                <span style="display:block">➕</span>
                <strong>Agregar materia</strong><br>
                <small>Estado: Disponible</small>
            </div>`;
    }
}

// 2. Abrir el popup y cargar datos de la BD
async function abrirModal() {
    document.getElementById('modal-materia').style.display = 'flex';
    
    // Aquí harías el fetch a tu base de datos (PHP, Node, etc.)
    // Ejemplo: const res = await fetch('get_materias.php');
    const select = document.getElementById('select-materias');
    select.innerHTML = '<option value="Matemáticas II">Matemáticas II</option><option value="Física I">Física I</option>'; 
}

function cerrarModal() {
    document.getElementById('modal-materia').style.display = 'none';
}

// 3. Confirmar selección
function confirmarMateria() {
    const select = document.getElementById('select-materias');
    const materiaSeleccionada = select.value;

    if (materiaSeleccionada) {
        materiasInscritas.push(materiaSeleccionada);
        cerrarModal();
        renderizarBotones(); // Se actualiza y crea el nuevo botón al lado
    }
}

// Ejecutar al cargar
renderizarBotones();