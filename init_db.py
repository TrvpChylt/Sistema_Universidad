import sqlite3

connection = sqlite3.connect('database.db')

# 1. Ejecuta el esquema (solo creación de tablas)
with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# 2. Insertar Carreras
cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Ingeniería en Informática',))
id_informatica = cur.lastrowid 

cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Licenciatura en Administración',))
id_administracion = cur.lastrowid 

cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Derecho',))
id_derecho = cur.lastrowid

materias = [
    # Ingeniería en Informática
    ('Programación I', id_informatica),
    ('Inglés Técnico', id_informatica),
    ('Proyecto de Software', id_informatica),
    ('Base de Datos', id_informatica),
    ('Análisis Matemático', id_informatica),
    
    # Licenciatura en Administración
    ('Contabilidad I', id_administracion),
    ('Microeconomía', id_administracion),
    ('Administración de Empresas', id_administracion),
    ('Marketing Digital', id_administracion),
    ('Recursos Humanos', id_administracion),
    
    # Derecho
    ('Derecho Civil I', id_derecho),
    ('Introducción al Derecho', id_derecho),
    ('Derecho Penal', id_derecho),
    ('Derecho Constitucional', id_derecho),
    ('Filosofía del Derecho', id_derecho)
]

# 4. Insertar Materias (Cambiado carrera_id por id_carrera para que coincida con tu SQL)
cur.executemany("INSERT INTO materias (nombre_materia, id_carrera) VALUES (?, ?)", materias)

connection.commit()
connection.close()
print("¡Base de datos creada y poblada con éxito!")