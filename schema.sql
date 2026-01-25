-- 1. Primero eliminamos todo para empezar de cero
DROP TABLE IF EXISTS inscripciones;
DROP TABLE IF EXISTS alumnos;
DROP TABLE IF EXISTS materias;
DROP TABLE IF EXISTS carreras_universitarias;

-- 2. Creamos la tabla de carreras (¡Fundamental!)
CREATE TABLE carreras_universitarias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_carrera TEXT NOT NULL UNIQUE
);

-- 3. Creamos la tabla de materias (Solo una vez)
CREATE TABLE materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_materia TEXT NOT NULL,
    id_carrera INTEGER,
    FOREIGN KEY (id_carrera) REFERENCES carreras_universitarias (id)
);

-- 4. Creamos la tabla de alumnos
CREATE TABLE alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    clave TEXT NOT NULL,
    id_carrera INTEGER, 
    FOREIGN KEY (id_carrera) REFERENCES carreras_universitarias (id)
);

-- 5. Creamos la tabla de inscripciones
CREATE TABLE inscripciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno INTEGER,
    id_materia INTEGER,
    fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_alumno) REFERENCES alumnos (id),
    FOREIGN KEY (id_materia) REFERENCES materias (id)
);

-- 6. Insertar datos iniciales para que no aparezca vacío el select
INSERT INTO carreras_universitarias (nombre_carrera) VALUES 
('Ingeniería en Informática'),
('Licenciatura en Administración'),
('Derecho');