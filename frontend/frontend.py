"""
Sistema de Gestión de Biblioteca + Panel de Administración
Interfaz Flet adaptada a Base de Datos (FastAPI Backend)
"""

import flet as ft
import requests

# URL de la API creada en FastAPI
API_URL = "http://127.0.0.1:8000/api"

# Paleta de Colores UI
PRIMARY = "#1a365d"
BG = "#f7fafc"
TEXT = "#2d3748"
SUCCESS = "#28a745"
WARNING = "#ffc107"
DANGER = "#dc3545"


def main(page: ft.Page):
    page.title = "Sistema de Gestión de Biblioteca"
    page.bgcolor = BG
    page.padding = 0
    page.window.width = 1150
    page.window.height = 800

    seleccion = {"libro": None, "filtro_estado": "Todos"}

    # --- Notificaciones tipo Toast ---
    def snack(mensaje: str, color=None):
        page.open(ft.SnackBar(content=ft.Text(mensaje), bgcolor=color))

    # --- Consumo Helper GET ---
    def api_get(endpoint, params=None):
        try:
            res = requests.get(f"{API_URL}{endpoint}", params=params)
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []

    # ======================================================================
    # SECCIÓN 1: VISTA DE TABLA librosDF (Catálogo e Información)
    # ======================================================================
    inv_id = ft.Text("ID: -", color=TEXT)
    inv_nombre = ft.Text("Seleccione un libro", size=20, weight="bold", color=TEXT)
    inv_autor = ft.Text("Autor: -", color=TEXT)
    inv_isbn = ft.Text("ISBN: -", color=TEXT)
    inv_genero = ft.Text("Género: -", color=TEXT)
    inv_anio = ft.Text("Año Publicación: -", color=TEXT)
    inv_descripcion = ft.Text("Seleccione un libro del catálogo para consultar sus detalles.", color=TEXT)
    inv_cantidad = ft.Text("-", size=18, weight="bold", color=PRIMARY)

    inv_imagen = ft.Container(
        content=ft.Icon("menu_book", size=60, color="#94a3b8"),
        width=160, height=140, bgcolor="#cbd5e1", border_radius=8,
        alignment=ft.Alignment(0, 0),
    )

    def ver_detalle_libro(libro):
        seleccion["libro"] = libro
        inv_id.value = f"ID Libro: {libro.get('id', 'N/A')}"
        inv_nombre.value = libro.get("titulo", "Sin título")
        inv_autor.value = f"Autor: {libro.get('autor', 'Desconocido')}"
        inv_isbn.value = f"ISBN: {libro.get('isbn', 'N/A')}"
        inv_genero.value = f"Género: {libro.get('genero', 'General')}"
        inv_anio.value = f"Año: {libro.get('anio_publicacion', 'N/A')}"
        inv_descripcion.value = libro.get("descripcion") or "Sin descripción registrada en la base de datos."
        inv_cantidad.value = f"{libro.get('ejemplares', 0)} ejemplares"
        page.update()

    def construir_lista_libros(on_click_item, filtro=""):
        libros = api_get("/libros")
        filtro_lower = filtro.strip().lower()

        items_filtrados = [
            l for l in libros
            if not filtro_lower
            or filtro_lower in str(l.get("titulo", "")).lower()
            or filtro_lower in str(l.get("id", ""))
            or filtro_lower in str(l.get("isbn", "")).lower()
        ]

        return [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon("book", color=PRIMARY),
                        ft.Column(
                            [
                                ft.Text(l.get("titulo", ""), weight="bold", overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(
                                    f"ID: {l.get('id')} | Autor: {l.get('autor', 'N/A')} | ISBN: {l.get('isbn', 'N/A')}",
                                    size=12, color="#64748b", overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            expand=True, spacing=2,
                        ),
                    ]
                ),
                padding=8,
                border_radius=6,
                on_click=lambda e, libro=l: on_click_item(libro),
                ink=True,
            )
            for l in items_filtrados
        ]

    lista_libros_inv = ft.ListView(height=400, spacing=4)

    seccion_inventario = ft.Column([
        ft.Text("Catálogo de Libros (Tabla librosDF)", size=22, weight="bold", color=TEXT),
        ft.ResponsiveRow([
            ft.Container(
                col={"sm": 12, "md": 5},
                content=ft.Card(content=ft.Container(
                    ft.Column([
                        ft.Text("Búsqueda en Base de Datos", size=16, weight="bold"),
                        ft.TextField(
                            label="Buscar por título, ID o ISBN...", prefix_icon="search", dense=True,
                            on_change=lambda e: setattr(
                                lista_libros_inv, 'controls', construir_lista_libros(ver_detalle_libro, e.control.value)
                            ) or page.update()
                        ),
                        lista_libros_inv,
                    ], spacing=10),
                    padding=16,
                )),
            ),
            ft.Container(
                col={"sm": 12, "md": 7},
                content=ft.Card(content=ft.Container(
                    ft.Column([
                        ft.Row([
                            inv_imagen,
                            ft.Column([
                                inv_id,
                                inv_nombre,
                                inv_autor,
                                inv_isbn,
                                inv_genero,
                                inv_anio,
                            ], expand=True, spacing=4),
                        ], vertical_alignment="start"),
                        ft.Divider(),
                        ft.Text("Descripción / Sinopsis", weight="bold"),
                        inv_descripcion,
                        ft.Row([
                            ft.Text("Ejemplares Disponibles en BD:", weight="bold"),
                            inv_cantidad
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=10),
                    padding=16,
                )),
            ),
        ]),
    ], spacing=16)

    # ======================================================================
    # SECCIÓN 2: REGISTRO DE PRÉSTAMOS (prestamosDF + estudiantesDF)
    # ======================================================================
    prestamo_titulo = ft.Text("Seleccione un libro para solicitar", size=18, weight="bold")
    prestamo_stock_disp = ft.Text("0", weight="bold")
    nombre_solicitante = ft.TextField(label="Nombre del Estudiante (estudiantesDF)")
    curso_solicitante = ft.TextField(label="RUT o Curso (Único en estudiantesDF)")
    cantidad_pedida = ft.TextField(label="Cantidad de Ejemplares", value="1", keyboard_type="number")

    def seleccionar_para_prestamo(libro):
        seleccion["libro"] = libro
        prestamo_titulo.value = f"Solicitar: {libro.get('titulo')}"
        prestamo_stock_disp.value = str(libro.get("ejemplares", 0))
        page.update()

    lista_libros_prestamo = ft.ListView(height=380, spacing=4)

    def registrar_prestamo(e):
        if not seleccion["libro"]:
            snack("Por favor, seleccione un libro del catálogo.", DANGER)
            return

        payload = {
            "libro_id": seleccion["libro"]["id"],
            "nombre_estudiante": nombre_solicitante.value,
            "rut_curso": curso_solicitante.value,
            "cantidad": int(cantidad_pedida.value or 1),
        }

        try:
            res = requests.post(f"{API_URL}/prestamos", json=payload)
            if res.status_code == 201:
                snack("¡Préstamo registrado e insertado en la BD!", SUCCESS)
                nombre_solicitante.value = ""
                curso_solicitante.value = ""
                cantidad_pedida.value = "1"
                refrescar_todo()
            else:
                detail = res.json().get("detail", "Error al procesar el préstamo.")
                snack(detail, DANGER)
        except Exception as ex:
            snack(f"Error de conexión con el backend: {ex}", DANGER)

    seccion_prestamo = ft.Column([
        ft.Text("Módulo de Préstamos de Libros", size=22, weight="bold", color=TEXT),
        ft.ResponsiveRow([
            ft.Container(
                col={"sm": 12, "md": 5},
                content=ft.Card(content=ft.Container(
                    ft.Column([
                        ft.Text("Seleccionar Libro a Solicitar", size=16, weight="bold"),
                        lista_libros_prestamo,
                    ], spacing=10),
                    padding=16,
                )),
            ),
            ft.Container(
                col={"sm": 12, "md": 7},
                content=ft.Card(content=ft.Container(
                    ft.Column([
                        prestamo_titulo,
                        ft.Row([ft.Text("Ejemplares Disponibles:", weight="bold"), prestamo_stock_disp]),
                        nombre_solicitante,
                        curso_solicitante,
                        cantidad_pedida,
                        ft.ElevatedButton(
                            "Registrar Préstamo en BD", icon="check_circle_outline",
                            bgcolor=PRIMARY, color="white", on_click=registrar_prestamo
                        ),
                    ], spacing=12),
                    padding=16,
                )),
            ),
        ]),
    ], spacing=16)

    # ======================================================================
    # SECCIÓN 3: TABLA prestamosDF E historial_prestamosDF (TRIGGERS)
    # ======================================================================
    tabla_prestamos = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(t)) for t in ["ID", "Fecha", "Estudiante", "RUT/Curso", "Libro", "Cant.", "Estado", "Acción"]],
        rows=[],
    )

    tabla_triggers = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(t)) for t in ["ID Log", "ID Préstamo", "Estudiante (Copia)", "Libro (Copia)", "Cantidad", "Acción Trigger", "Fecha Evento"]],
        rows=[],
    )

    def marcar_como_devuelto(prestamo_id):
        res = requests.put(f"{API_URL}/prestamos/{prestamo_id}/devolver")
        if res.status_code == 200:
            snack("Libro devuelto. El trigger ha guardado la acción en el historial.", SUCCESS)
            refrescar_todo()
        else:
            snack("Error al procesar la devolución.", DANGER)

    def renderizar_tabla_prestamos():
        datos = api_get("/prestamos", params={"estado": seleccion["filtro_estado"]})
        filas = []
        for p in datos:
            es_prestado = p.get("estado") == "Prestado"
            accion = (
                ft.ElevatedButton("Devolver Libro", bgcolor=WARNING, color=TEXT, on_click=lambda e, pid=p["id"]: marcar_como_devuelto(pid))
                if es_prestado else ft.Text("-")
            )
            filas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"#{p.get('id')}")),
                ft.DataCell(ft.Text(str(p.get("fecha", "")))),
                ft.DataCell(ft.Text(p.get("solicitante", ""))),
                ft.DataCell(ft.Text(p.get("curso", ""))),
                ft.DataCell(ft.Text(p.get("herramienta", ""))),
                ft.DataCell(ft.Text(str(p.get("cantidad", 1)))),
                ft.DataCell(ft.Container(
                    content=ft.Text(p.get("estado", ""), color="white", size=11),
                    bgcolor=WARNING if es_prestado else SUCCESS,
                    padding=ft.Padding(6, 2, 6, 2), border_radius=8
                )),
                ft.DataCell(accion),
            ]))
        tabla_prestamos.rows = filas

    def renderizar_tabla_triggers():
        logs = api_get("/historial")
        filas = []
        for log in logs:
            es_registro = log.get("accion") == "REGISTRADO"
            filas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"#{log.get('id')}")),
                ft.DataCell(ft.Text(f"Préstamo #{log.get('prestamo_id')}")),
                ft.DataCell(ft.Text(log.get("estudiante_nombre", ""))),
                ft.DataCell(ft.Text(log.get("libro_titulo", ""))),
                ft.DataCell(ft.Text(str(log.get("cantidad", 0)))),
                ft.DataCell(ft.Container(
                    content=ft.Text(log.get("accion", ""), color="white", size=11),
                    bgcolor=PRIMARY if es_registro else SUCCESS,
                    padding=ft.Padding(6, 2, 6, 2), border_radius=8
                )),
                ft.DataCell(ft.Text(str(log.get("fecha_registro", "")))),
            ]))
        tabla_triggers.rows = filas

    def filtrar_estado_prestamos(estado):
        seleccion["filtro_estado"] = estado
        renderizar_tabla_prestamos()
        page.update()

    seccion_historial = ft.Column([
        ft.Text("Historial y Registros Automáticos", size=22, weight="bold", color=TEXT),
        ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Préstamos Activos (prestamosDF)",
                    content=ft.Container(
                        ft.Column([
                            ft.Row([
                                ft.ElevatedButton("Todos", on_click=lambda e: filtrar_estado_prestamos("Todos")),
                                ft.ElevatedButton("En Préstamo", on_click=lambda e: filtrar_estado_prestamos("Prestado")),
                                ft.ElevatedButton("Devueltos", on_click=lambda e: filtrar_estado_prestamos("Devuelto")),
                            ], spacing=10),
                            ft.Row([tabla_prestamos], scroll="auto"),
                        ], spacing=12),
                        padding=16
                    )
                ),
                ft.Tab(
                    text="Auditoría de Triggers (historial_prestamosDF)",
                    content=ft.Container(
                        ft.Column([
                            ft.Text("Registros automáticos creados por los Triggers SQL al Insertar/Actualizar:", color="#64748b"),
                            ft.Row([tabla_triggers], scroll="auto"),
                        ], spacing=12),
                        padding=16
                    )
                )
            ]
        )
    ], spacing=16)

    # ======================================================================
    # REFRESCADO Y CONFIGURACIÓN GLOBAL DE NAVEGACIÓN
    # ======================================================================
    def refrescar_todo():
        lista_libros_inv.controls = construir_lista_libros(ver_detalle_libro)
        lista_libros_prestamo.controls = construir_lista_libros(seleccionar_para_prestamo)
        renderizar_tabla_prestamos()
        renderizar_tabla_triggers()
        page.update()

    contenido_tabs = ft.Container(seccion_inventario, padding=20, expand=True)

    def cambiar_tab(e):
        idx = e.control.data
        for btn in tab_buttons:
            activo = btn.data == idx
            btn.bgcolor = PRIMARY if activo else "#cbd5e1"
            btn.color = "white" if activo else TEXT

        if idx == 0:
            contenido_tabs.content = seccion_inventario
        elif idx == 1:
            contenido_tabs.content = seccion_prestamo
        elif idx == 2:
            contenido_tabs.content = seccion_historial
        page.update()

    tab_buttons = [
        ft.ElevatedButton("📚 Catálogo (librosDF)", data=0, bgcolor=PRIMARY, color="white", on_click=cambiar_tab),
        ft.ElevatedButton("📖 Préstamos", data=1, bgcolor="#cbd5e1", color=TEXT, on_click=cambiar_tab),
        ft.ElevatedButton("📋 Historial y Triggers", data=2, bgcolor="#cbd5e1", color=TEXT, on_click=cambiar_tab),
    ]

    body = ft.Column([
        ft.Container(
            content=ft.Text("Sistema de Biblioteca Conectado a Base de Datos SQL", size=20, weight="bold", color="white"),
            bgcolor=PRIMARY, padding=16
        ),
        ft.Container(content=ft.Row(tab_buttons, spacing=10), padding=ft.Padding(20, 10, 20, 0)),
        contenido_tabs,
    ], expand=True, spacing=0)

    page.add(body)

    # Carga inicial de datos
    refrescar_todo()


if __name__ == "__main__":
    ft.app(target=main)