"""Endpoints CRUD para Libros, Estudiantes y Préstamos."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.connect import get_conexion

router = APIRouter(prefix="/api", tags=["Biblioteca"])


# --- Schemas ---
class PrestamoRequest(BaseModel):
    libro_id: int
    nombre_estudiante: str
    rut_curso: str
    cantidad: int = 1


# ======================================================================
# ENDPOINTS LIBROS
# ======================================================================

@router.get("/libros")
def listar_libros():
    """Devuelve todos los libros registrados."""
    conexion = get_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id, titulo, autor, isbn, descripcion, ejemplares FROM librosDF ORDER BY id DESC")
            libros = cursor.fetchall()
        return libros
    finally:
        conexion.close()


@router.get("/libros/{libro_id}")
def obtener_libro(libro_id: int):
    """Busca un libro mediante su id."""
    conexion = get_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM librosDF WHERE id = %s", (libro_id,))
            libro = cursor.fetchone()
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return libro
    finally:
        conexion.close()


@router.post("/libros", status_code=201)
async def crear_libro(request: Request):
    """Crea un registro nuevo de libro."""
    datos = await request.json()
    conexion = get_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO librosDF (titulo, autor, isbn, descripcion, genero, anio_publicacion, ejemplares)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    datos.get("titulo"),
                    datos.get("autor"),
                    datos.get("isbn"),
                    datos.get("descripcion"),
                    datos.get("genero"),
                    datos.get("anio_publicacion"),
                    datos.get("ejemplares", 1),
                ),
            )
            conexion.commit()
            nuevo_id = cursor.lastrowid
        return {"id": nuevo_id, **datos}
    finally:
        conexion.close()


# ======================================================================
# ENDPOINTS PRÉSTAMOS
# ======================================================================

@router.post("/prestamos", status_code=201)
def registrar_prestamo(data: PrestamoRequest):
    """Registra un préstamo descontando ejemplares y registrando al estudiante si no existe."""
    conexion = get_conexion()
    try:
        with conexion.cursor() as cursor:
            # 1. Verificar disponibilidad del libro
            cursor.execute("SELECT ejemplares FROM librosDF WHERE id = %s", (data.libro_id,))
            libro = cursor.fetchone()
            if not libro:
                raise HTTPException(status_code=404, detail="Libro no encontrado.")
            
            if libro["ejemplares"] < data.cantidad:
                raise HTTPException(status_code=400, detail="Cantidad de ejemplares insuficientes.")

            # 2. Registrar/Obtener Estudiante
            cursor.execute("SELECT id FROM estudiantesDF WHERE rut_curso = %s", (data.rut_curso,))
            estudiante = cursor.fetchone()
            
            if estudiante:
                estudiante_id = estudiante["id"]
            else:
                cursor.execute(
                    "INSERT INTO estudiantesDF (nombre, rut_curso) VALUES (%s, %s)",
                    (data.nombre_estudiante, data.rut_curso)
                )
                estudiante_id = cursor.lastrowid

            # 3. Crear Préstamo (Trigger creará la entrada en historial_prestamosDF)
            cursor.execute(
                "INSERT INTO prestamosDF (estudiante_id, libro_id, cantidad) VALUES (%s, %s, %s)",
                (estudiante_id, data.libro_id, data.cantidad)
            )
            
            # 4. Actualizar ejemplares
            cursor.execute(
                "UPDATE librosDF SET ejemplares = ejemplares - %s WHERE id = %s",
                (data.cantidad, data.libro_id)
            )

            conexion.commit()
            return {"mensaje": "Préstamo registrado exitosamente."}
    finally:
        conexion.close()


@router.get("/prestamos")
def listar_prestamos(estado: str = "Todos"):
    """Lista todos los préstamos vinculados con libros y estudiantes."""
    conexion = get_conexion()
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT p.id, p.fecha_prestamo AS fecha, e.nombre AS solicitante, 
                       e.rut_curso AS curso, l.titulo AS herramienta, p.cantidad, p.estado
                FROM prestamosDF p
                JOIN estudiantesDF e ON p.estudiante_id = e.id
                JOIN librosDF l ON p.libro_id = l.id
            """
            if estado != "Todos":
                query += " WHERE p.estado = %s"
                cursor.execute(query + " ORDER BY p.id DESC", (estado,))
            else:
                cursor.execute(query + " ORDER BY p.id DESC")
            
            return cursor.fetchall()
    finally:
        conexion.close()


@router.put("/prestamos/{prestamo_id}/devolver")
def devolver_libro(prestamo_id: int):
    """Marca un préstamo como devuelto y reintegra los ejemplares al libro."""
    conexion = get_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT libro_id, cantidad, estado FROM prestamosDF WHERE id = %s", (prestamo_id,))
            prestamo = cursor.fetchone()

            if not prestamo:
                raise HTTPException(status_code=404, detail="Préstamo no encontrado.")
            if prestamo["estado"] == "Devuelto":
                raise HTTPException(status_code=400, detail="El libro ya fue devuelto previamente.")

            # Cambiar estado (Trigger registrará el evento 'DEVUELTO')
            cursor.execute(
                "UPDATE prestamosDF SET estado = 'Devuelto', fecha_devolucion = NOW() WHERE id = %s",
                (prestamo_id,)
            )

            # Reintegrar ejemplares
            cursor.execute(
                "UPDATE librosDF SET ejemplares = ejemplares + %s WHERE id = %s",
                (prestamo["cantidad"], prestamo["libro_id"])
            )

            conexion.commit()
            return {"mensaje": "Libro devuelto exitosamente."}
    finally:
        conexion.close()


@router.get("/historial")
def ver_historial_triggers():
    """Consulta directa a la tabla generada por los triggers."""
    conexion = get_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM historial_prestamosDF ORDER BY id DESC")
            return cursor.fetchall()
    finally:
        conexion.close()