CREATE TABLE IF NOT EXISTS estudiantesDF (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    rut VARCHAR(20) UNIQUE NOT NULL,
    curso VARCHAR(50) NOT NULL
);

-- 2. Tabla de Libros
CREATE TABLE IF NOT EXISTS librosDF (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(150) NOT NULL,
    isbn VARCHAR(50) UNIQUE,
    descripcion TEXT,
    genero VARCHAR(100),
    anio_publicacion INT,
    ejemplares INT NOT NULL DEFAULT 1
);

-- 3. Tabla de Préstamos Activos y Registro Principal
CREATE TABLE IF NOT EXISTS prestamosDF (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estudiante_id INT NOT NULL,
    libro_id INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    fecha_prestamo DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_devolucion DATETIME NULL,
    estado ENUM('Prestado', 'Devuelto') DEFAULT 'Prestado',
    FOREIGN KEY (estudiante_id) REFERENCES estudiantesDF(id) ON DELETE CASCADE,
    FOREIGN KEY (libro_id) REFERENCES librosDF(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS historial_prestamosDF (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prestamo_id INT NOT NULL,
    estudiante_nombre VARCHAR(150),
    libro_titulo VARCHAR(200),
    cantidad INT,
    accion VARCHAR(50), -- 'REGISTRADO' o 'DEVUELTO'
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_despues_insertar_prestamo
AFTER INSERT ON prestamosDF
FOR EACH ROW
BEGIN
    DECLARE v_estudiante_nombre VARCHAR(200);
    DECLARE v_libro_titulo VARCHAR(200);

    SELECT CONCAT(nombre, ' (RUT: ', rut, ' | Curso: ', curso, ')') 
    INTO v_estudiante_nombre 
    FROM estudiantesDF WHERE id = NEW.estudiante_id;

    SELECT titulo INTO v_libro_titulo FROM librosDF WHERE id = NEW.libro_id;

    INSERT INTO historial_prestamosDF (prestamo_id, estudiante_nombre, libro_titulo, cantidad, accion)
    VALUES (NEW.id, v_estudiante_nombre, v_libro_titulo, NEW.cantidad, 'REGISTRADO');
END;

CREATE TRIGGER trg_despues_actualizar_prestamo
AFTER UPDATE ON prestamosDF
FOR EACH ROW
BEGIN
    DECLARE v_estudiante_nombre VARCHAR(200);
    DECLARE v_libro_titulo VARCHAR(200);

    IF OLD.estado = 'Prestado' AND NEW.estado = 'Devuelto' THEN
        SELECT CONCAT(nombre, ' (RUT: ', rut, ' | Curso: ', curso, ')') 
        INTO v_estudiante_nombre 
        FROM estudiantesDF WHERE id = NEW.estudiante_id;

        SELECT titulo INTO v_libro_titulo FROM librosDF WHERE id = NEW.libro_id;

        INSERT INTO historial_prestamosDF (prestamo_id, estudiante_nombre, libro_titulo, cantidad, accion)
        VALUES (NEW.id, v_estudiante_nombre, v_libro_titulo, NEW.cantidad, 'DEVUELTO');
    END IF;
END;