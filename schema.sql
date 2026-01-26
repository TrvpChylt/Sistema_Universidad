DROP TABLE IF EXISTS inscripciones;
DROP TABLE IF EXISTS alumnos;
DROP TABLE IF EXISTS materias;
DROP TABLE IF EXISTS carreras_universitarias;

CREATE TABLE carreras_universitarias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_carrera TEXT NOT NULL UNIQUE
);

CREATE TABLE materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_materia TEXT NOT NULL,
    id_carrera INTEGER,
    FOREIGN KEY (id_carrera) REFERENCES carreras_universitarias (id)
);

CREATE TABLE alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    clave TEXT NOT NULL,
    id_carrera INTEGER, 
    FOREIGN KEY (id_carrera) REFERENCES carreras_universitarias (id)
);

CREATE TABLE inscripciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno INTEGER,
    id_materia INTEGER,
    fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_alumno) REFERENCES alumnos (id),
    FOREIGN KEY (id_materia) REFERENCES materias (id)
);
