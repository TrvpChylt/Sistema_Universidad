import sqlite3

connection = sqlite3.connect('database.db')
with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()
# Insertamos las 3 carreras iniciales
cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Ingeniería en Informática',))
cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Licenciatura en Administración',))
cur.execute("INSERT INTO carreras_universitarias (nombre_carrera) VALUES (?)", ('Derecho',))

connection.commit()
connection.close()
print("Base de datos SQLite lista.")