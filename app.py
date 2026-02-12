from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'mi_llave_secreta_universitaria'



def get_db_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_dir, 'database.db')
    
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row 
    return conn



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
    materias = conn.execute(
        "SELECT id, nombre_materia FROM materias WHERE id_carrera = ?", 
        (id_carrera,)
    ).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in materias])


@app.route('/procesar_registro', methods=['POST'])
def registro():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    clave = request.form.get('clave')
    id_carrera = request.form.get('id_carrera')
    
    materias_seleccionadas = request.form.getlist('id_materia')
    
    materias_unicas = list(set([m for m in materias_seleccionadas if m]))

    if len(materias_unicas) < 3:
        flash("Debes seleccionar al menos 3 materias diferentes.")
        return redirect(url_for('formulario_registro'))


    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO alumnos (nombre, apellido, correo, clave, id_carrera) 
        VALUES (?, ?, ?, ?, ?) """, (nombre, apellido, correo, clave, id_carrera))
        
        id_nuevo_alumno = cursor.lastrowid
  
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
    
    usuario = conn.execute("SELECT * FROM alumnos WHERE correo = ?", (correo,)).fetchone()
    
    if usuario:
        rol = 'alumno'
    else:
        usuario = conn.execute("SELECT * FROM administradores WHERE correo = ?", (correo,)).fetchone()
        rol = 'admin'

    conn.close()

    if usuario and usuario['clave'] == clave_ingresada:
        session['usuario_id'] = usuario['id']
        session['nombre'] = usuario['nombre']
        session['rol'] = rol
        return redirect(url_for('index'))
    
    flash("Correo o contraseña incorrectos")
    return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/perfil/<int:usuario_id>')
def perfil(usuario_id):
    rol_actual = session.get('rol')
    conn = get_db_connection()

    usuario = None
    materias = []

    if rol_actual == 'alumno':
        query_alumno = """
            Select a.*, cn.nombre_carrera
            From alumnos a
            Left Join carreras_universitarias cn ON a.id_carrera = cn.id
            Where a.id = ?
        """

        usuario = conn.execute(query_alumno, (usuario_id,)).fetchone()

        query_materias = """
            SELECT m.nombre_materia 
            FROM materias m
            JOIN inscripciones i ON m.id = i.id_materia
            WHERE i.id_alumno = ?
        """
        materias = conn.execute(query_materias, (usuario_id,)).fetchall()

    elif rol_actual == 'admin':
        query_admin = "SELECT * FROM administradores WHERE id = ?"
        usuario = conn.execute(query_admin, (usuario_id,)).fetchone()

        conn.close()

    if usuario is None:
        flash("Usuario no encontrado.")
        return redirect(url_for('index'))
    
    return render_template('perfil.html', usuario=usuario, materias=materias)


@app.route('/editar_alumno/<int:alumno_id>', methods=['GET', 'POST'])
def editar_alumno(alumno_id):
    if session.get('rol') != 'admin':
        flash("No tienes permiso para realizar esta acción.")
        return redirect(url_for('index'))

    conn = get_db_connection()

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
    
        query_update = """
            UPDATE alumnos 
            SET nombre = ?, apellido = ?, correo = ?
            WHERE id = ?
        """
        conn.execute(query_update, (nombre, apellido, correo, alumno_id))
        conn.commit()
        conn.close()
        flash("Datos actualizados correctamente.")
        return redirect(url_for('perfil', usuario_id=alumno_id))

    alumno = conn.execute('SELECT * FROM alumnos WHERE id = ?', (alumno_id,)).fetchone()
    conn.close()
    
    return render_template('editar_alumnos.html', alumno=alumno)


@app.route('/editar/<int:usuario_id>', methods=['POST'])
def editar_estudiante(usuario_id):
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form['correo']
    rol = session.get('rol')
    
    conn = get_db_connection()

    if rol == 'alumno':
        conn.execute('UPDATE alumnos SET nombre = ?, apellido = ?, correo = ? WHERE id = ?',
                     (nombre, apellido, correo, usuario_id))
    elif rol == 'admin':
        conn.execute('UPDATE administradores SET nombre = ?, apellido = ?, correo = ? WHERE id = ?',
                     (nombre, apellido, correo, usuario_id))
    conn.commit()
    conn.close()
    
    flash("Perfil actualizado")
    return redirect(url_for('perfil', usuario_id=usuario_id))



@app.route('/admin/alumnos')
def gestion_alumnos():
    if session.get('rol') != 'admin':
        flash("Acceso denegado.")
        return redirect(url_for('index'))

    conn = get_db_connection()
    alumnos = conn.execute('''
        SELECT a.id, a.nombre, a.apellido, a.correo, c.nombre_carrera 
        FROM alumnos a
        LEFT JOIN carreras_universitarias c ON a.id_carrera = c.id
    ''').fetchall()
    conn.close()
    
    return render_template('gestion_alumnos.html', alumnos=alumnos)



@app.route('/admin/eliminar_alumno/<int:id>')
def eliminar_alumno(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('index'))

    conn = get_db_connection()
    
    conn.execute('DELETE FROM inscripciones WHERE id_alumno = ?', (id,))
    conn.execute('DELETE FROM alumnos WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash("Alumno eliminado correctamente.")
    return redirect(url_for('gestion_alumnos'))

if __name__ == '__main__':
    app.run(debug=True)