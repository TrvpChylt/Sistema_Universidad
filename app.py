from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'mi_llave_secreta_universitaria'

def get_db_connection():
    database_path = '/home/JesusChylt29/database.db'
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row 
    return conn

# --- Rutas ---

@app.route('/')
def index():
    materias = []
    if 'usuario_id' in session:
        conn = get_db_connection()
        query = """
            SELECT m.nombre_materia 
            FROM materias m
            JOIN inscripciones i ON m.id = i.id_materia
            WHERE i.id_alumno = ?
        """
        materias = conn.execute(query, (session['usuario_id'],)).fetchall()
        conn.close()
    
    return render_template('index.html', materias=materias)


@app.route('/registro', methods=['GET'])
def formulario_registro():
    conn = get_db_connection()
    carreras = conn.execute("SELECT * FROM carreras_universitarias").fetchall()
    conn.close()
    return render_template('inscripcion.html', carreras=carreras)

@app.route('/obtener_materias/<int:id_carrera>')
def obtener_materias(id_carrera):
    conn = get_db_connection()
    materias = conn.execute("SELECT id, nombre_materia FROM materias WHERE carrera_id = ?", (id_carrera,)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in materias])



@app.route('/procesar_registro', methods=['POST'])
def registro():
    # 1. Obtención de datos básicos del formulario
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    cedula = request.form.get('cedula')
    correo = request.form.get('correo')
    clave = request.form.get('clave')
    id_carrera = request.form.get('id_carrera')
    
    # 2. Obtener la lista de IDs de las materias (los 3 selects con name="id_materia")
    # request.form.getlist capturará todos los valores de los selects en una lista ['1', '5', '8']
    materias_seleccionadas = request.form.getlist('id_materia')
    
    # 3. Limpieza y validación: eliminamos duplicados y valores vacíos
    # set() elimina duplicados en caso de que el usuario elija la misma materia en dos selects
    materias_unicas = list(set([m for m in materias_seleccionadas if m]))

    if len(materias_unicas) < 3:
        flash("Debes seleccionar al menos 3 materias diferentes.")
        return redirect(url_for('formulario_registro'))

    # 4. Generar el hash de la contraseña por seguridad
    password_hash = generate_password_hash(clave)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 5. Insertar los datos del alumno
        cursor.execute("""
            INSERT INTO alumnos (nombre, apellido, cedula, correo, clave, id_carrera) 
            VALUES (?, ?, ?, ?, ?, ?)""", (nombre, apellido, cedula, correo, password_hash, id_carrera))
        
        id_nuevo_alumno = cursor.lastrowid
        
        # 6. Insertar cada una de las materias en la tabla de inscripciones
        for id_materia in materias_unicas:
            cursor.execute("""
                INSERT INTO inscripciones (id_alumno, id_materia, fecha_inscripcion) 
                VALUES (?, ?, DATE('now'))""", 
                (id_nuevo_alumno, id_materia))
        
        conn.commit()
        flash("Registro exitoso. Ya puedes iniciar sesión.")
        return redirect(url_for('login_page'))

    except sqlite3.IntegrityError:
        conn.rollback()
        flash("Error: La cédula o el correo ya se encuentran registrados.")
        return redirect(url_for('formulario_registro'))
    except Exception as e:
        conn.rollback()
        return f"Error inesperado: {str(e)}"
    finally:
        conn.close()


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

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