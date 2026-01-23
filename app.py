from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'mi_llave_secreta_universitaria'

def get_db_connection():
    # Asegúrate de que esta ruta sea correcta en tu PythonAnywhere
    database_path = '/home/JesusChylt29/database.db'
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row 
    return conn

# --- Rutas de Visualización ---

@app.route('/')
def index():
    # Si no hay sesión, simplemente mostramos el index limpio
    if 'usuario_id' not in session:
        return render_template('index.html', nombre=None)
    
    return render_template('index.html', nombre=session.get('nombre'))

@app.route('/registro', methods=['GET'])
def formulario_registro():
    conn = get_db_connection()
    carreras = conn.execute("SELECT * FROM carreras_universitarias").fetchall()
    conn.close()
    return render_template('inscripcion.html', carreras=carreras)

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# --- APIs y Procesamiento ---

@app.route('/obtener_materias/<int:id_carrera>')
def obtener_materias(id_carrera):
    conn = get_db_connection()
    materias = conn.execute("SELECT id, nombre_materia FROM materias WHERE carrera_id = ?", (id_carrera,)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in materias])

@app.route('/api/mis_materias')
def mis_materias():
    """Ruta que consulta las materias inscritas por el usuario actual"""
    if 'usuario_id' not in session:
        return jsonify([])
    
    conn = get_db_connection()
    # Query para traer los nombres de las materias del alumno logueado
    query = """
        SELECT m.nombre_materia 
        FROM materias m
        JOIN inscripciones i ON m.id = i.id_materia
        WHERE i.id_alumno = ?
    """
    materias = conn.execute(query, (session['usuario_id'],)).fetchall()
    conn.close()
    
    return jsonify([{"nombre": m['nombre_materia']} for m in materias])

@app.route('/procesar_registro', methods=['POST'])
def registro():
    # Datos personales
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    cedula = request.form['cedula']
    correo = request.form['correo']
    password_hash = generate_password_hash(request.form['clave'])
    id_carrera = request.form['id_carrera']
    
    # Obtenemos la lista de IDs de materias (los 3 selects del form)
    # Importante: En tu HTML los selects deben tener name="materias_ids"
    materias_seleccionadas = request.form.getlist('materias_ids')

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # 1. Insertar el Alumno
        cursor.execute("""
            INSERT INTO alumnos (nombre, apellido, cedula, correo, clave, id_carrera) 
            VALUES (?, ?, ?, ?, ?, ?)""", 
            (nombre, apellido, cedula, correo, password_hash, id_carrera))
        
        id_nuevo_alumno = cursor.lastrowid
        
        # 2. Insertar las materias seleccionadas (las 3 del registro)
        for id_materia in materias_seleccionadas:
            if id_materia: # Validar que no llegue vacío
                cursor.execute("""
                    INSERT INTO inscripciones (id_alumno, id_materia, fecha_inscripcion) 
                    VALUES (?, ?, DATE('now'))""", 
                    (id_nuevo_alumno, id_materia))
        
        conn.commit()
        flash("Registro e inscripción exitosa. Ya puedes iniciar sesión.")
        return redirect(url_for('login_page'))
    
    except Exception as e:
        conn.rollback()
        print(f"Error en registro: {e}")
        flash("Hubo un error al procesar tu registro.")
        return redirect(url_for('formulario_registro'))
    finally:
        conn.close()

@app.route('/procesar_login', methods=['POST'])
def login():
    correo = request.form['correo']
    clave_ingresada = request.form['clave']

    conn = get_db_connection()
    alumno = conn.execute("SELECT * FROM alumnos WHERE correo = ?", (correo,)).fetchone()
    conn.close()

    if alumno and check_password_hash(alumno['clave'], clave_ingresada):
        session['usuario_id'] = alumno['id']
        session['nombre'] = alumno['nombre']
        return redirect(url_for('index'))
    
    flash("Correo o contraseña incorrectos")
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)