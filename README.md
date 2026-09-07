# biblioteca_FT

Sistema de gestión de préstamos para una biblioteca escolar. Backend en **FastAPI** + MySQL y una interfaz de escritorio en **Flet** que consume la API.

## Stack

- **Backend:** FastAPI + PyMySQL
- **Base de datos:** MySQL (con triggers de auditoría)
- **Frontend:** Flet (app de escritorio en Python)
- **Config:** python-dotenv

## Estructura

```
biblioteca_FT/
├── backend/
│   ├── main.py            # App FastAPI, monta el router y el endpoint de estado
│   ├── connect.py         # Conexión a MySQL (lee variables de entorno)
│   └── rutas/
│       └── libros.py       # Endpoints: libros, préstamos, historial
├── frontend/
│   └── frontend.py         # Interfaz Flet (catálogo, préstamos, historial)
├── schema.sql               # DDL: tablas + triggers de auditoría
├── requirements.txt
└── .env.example
```

## Modelo de datos

- `librosDF` — catálogo de libros (título, autor, ISBN, género, año, ejemplares disponibles).
- `estudiantesDF` — estudiantes identificados por RUT único.
- `prestamosDF` — préstamos activos/devueltos, vinculados a libro y estudiante.
- `historial_prestamosDF` — bitácora generada automáticamente por triggers al **registrar** o **devolver** un préstamo.

## Configuración
1. Copiar `.env.example` a `.env` y ajustar credenciales:
   ```bash
   cp .env.example .env
   ```
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASS=
   DB_NAME=biblioteca_db
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

**Backend** (desde la raíz del proyecto, para que los imports `backend.*` resuelvan):
```bash
uvicorn backend.main:app --reload
```
API disponible en `http://127.0.0.1:8000` (estado en `/`, endpoints bajo `/api`).

**Frontend** (con el backend ya corriendo):
```bash
python frontend/frontend.py
```

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/libros` | Lista todos los libros |
| GET | `/api/libros/{id}` | Detalle de un libro |
| POST | `/api/libros` | Crea un libro |
| POST | `/api/prestamos` | Registra un préstamo (valida stock, crea/actualiza estudiante) |
| GET | `/api/prestamos?estado=Todos\|Prestado\|Devuelto` | Lista préstamos, con filtro opcional |
| PUT | `/api/prestamos/{id}/devolver` | Marca un préstamo como devuelto y repone stock |
| GET | `/api/historial` | Bitácora de auditoría (generada por triggers)