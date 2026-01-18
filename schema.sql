DROP TABLE IF EXISTS materias;
CREATE TABLE materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_materia TEXT NOT NULL,
    carrera_id INTEGER, -- Asegúrate que se llame carrera_id
    FOREIGN KEY (carrera_id) REFERENCES carreras_universitarias (id)
);

CREATE TABLE IF NOT EXISTS alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    cedula TEXT UNIQUE NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    clave TEXT NOT NULL,
    id_carrera INTEGER, 
    FOREIGN KEY (id_carrera) REFERENCES carreras_universitarias (id)
);

CREATE TABLE IF NOT EXISTS materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_materia TEXT NOT NULL,
    id_carrera INTEGER,
    FOREIGN KEY (id_carrera) REFERENCES carreras_universitarias (id)
);

CREATE TABLE IF NOT EXISTS inscripciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno INTEGER,
    id_materia INTEGER,
    fecha_inscripcion TEXT,
    FOREIGN KEY (id_alumno) REFERENCES alumnos (id),
    FOREIGN KEY (id_materia) REFERENCES materias (id)
);