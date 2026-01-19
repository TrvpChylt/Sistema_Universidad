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
    materia_inscrita = None
    if 'usuario_id' in session:
        conn = get_db_connection()
        query = """
            SELECT nombre_materia 
            FROM materias nombre_materia 
            JOIN inscripciones i ON nombre_materia.id = i.id_materia
            WHERE i.id_alumno = ?
            LIMIT 1
        """
        materia_inscrita = conn.execute(query, (session['usuario_id'],)).fetchone()
        conn.close()
    
    return render_template('index.html', materia=materia_inscrita)


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
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    cedula = request.form['cedula']
    correo = request.form['correo']
    password_hash = generate_password_hash(request.form['clave'])
    id_carrera = request.form['id_carrera']
    id_materia = request.form['id_materia']

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alumnos (nombre, apellido, cedula, correo, clave, id_carrera) 
            VALUES (?, ?, ?, ?, ?, ?)""", 
            (nombre, apellido, cedula, correo, password_hash, id_carrera))
        
        id_nuevo_alumno = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO inscripciones (id_alumno, id_materia, fecha_inscripcion) 
            VALUES (?, ?, DATE('now'))""", 
            (id_nuevo_alumno, id_materia))
        
        conn.commit()
        flash("Tus Datos fueron Inscritos Correctamente. Ya puedes iniciar sesión.")
        return redirect(url_for('login_page'))
    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"
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