import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Ingeniería en Informática',))
id_informatica = cur.lastrowid 

cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Licenciatura en Administración',))
id_administracion = cur.lastrowid 

cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Derecho',))
id_derecho = cur.lastrowid

materias = [
    ('Programación I', id_informatica),
    ('Base de Datos', id_informatica),
    ('Análisis Matemático', id_informatica),
    ('Contabilidad I', id_administracion),
    ('Microeconomía', id_administracion),
    ('Derecho Civil I', id_derecho),
    ('Introducción al Derecho', id_derecho)
]

cur.executemany("INSERT INTO materias (nombre_materia, carrera_id) VALUES (?, ?)", materias)

connection.commit()
connection.close()
