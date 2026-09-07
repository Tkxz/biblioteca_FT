import flet as ft
import requests

API_URL = "http://127.0.0.1:8000/api"

PRIMARY = "#1a365d"
BG = "#f1f5f9"
TEXT = "#334155"
SUCCESS = "#10b981"
WARNING = "#f59e0b"
DANGER = "#ef4444"


def main(page: ft.Page):
    page.title = "Sistema de Gestión de Biblioteca"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.bgcolor = BG
    page.padding = 0
    page.window.width = 1150
    page.window.height = 800

    seleccion = {"libro": None, "filtro_estado": "Todos"}

    def snack(mensaje: str, color=None):
        snack_bar = ft.SnackBar(content=ft.Text(mensaje, color="white"), bgcolor=color)
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    def api_get(endpoint, params=None):
        try:
            res = requests.get(f"{API_URL}{endpoint}", params=params, timeout=3)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def ver_detalle_libro(libro):
        seleccion["libro"] = libro
        inv_id.value = f"ID Libro: {libro.get('id', 'N/A')}"
        inv_nombre.value = libro.get("titulo", "Sin título")
        inv_autor.value = f"Autor: {libro.get('autor', 'Desconocido')}"
        inv_isbn.value = f"ISBN: {libro.get('isbn', 'N/A')}"
        inv_genero.value = f"Género: {libro.get('genero', 'General')}"
        inv_anio.value = f"Año: {libro.get('anio_publicacion', 'N/A')}"
        inv_descripcion.value = libro.get("descripcion") or "Sin descripción registrada."
        inv_cantidad.value = f"{libro.get('ejemplares', 0)} ejemplares"
        page.update()

    def seleccionar_para_prestamo(libro):
        seleccion["libro"] = libro
        prestamo_titulo.value = f"Solicitar: {libro.get('titulo')}"
        prestamo_stock_disp.value = str(libro.get("ejemplares", 0))
        page.update()

    # Tablas para mostrar los libros de forma segura
    tabla_libros_inv = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight="bold")),
            ft.DataColumn(ft.Text("Título y Autor", weight="bold")),
            ft.DataColumn(ft.Text("Acción", weight="bold")),
        ],
        rows=[]
    )

    tabla_libros_prestamo = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight="bold")),
            ft.DataColumn(ft.Text("Título y Autor", weight="bold")),
            ft.DataColumn(ft.Text("Acción", weight="bold")),
        ],
        rows=[]
    )

    def actualizar_tablas_libros(filtro=""):
        libros = api_get("/libros")
        filtro_lower = filtro.strip().lower()
        
        items_filtrados = [
            l for l in libros
            if not filtro_lower
            or filtro_lower in str(l.get("titulo", "")).lower()
            or filtro_lower in str(l.get("id", ""))
        ]

        filas_inv = []
        filas_prestamo = []

        for l in items_filtrados:
            info_texto = ft.Column([
                ft.Text(l.get("titulo", ""), weight="bold", color="#0f172a"),
                ft.Text(f"Autor: {l.get('autor', 'N/A')} | ISBN: {l.get('isbn', 'N/A')}", size=12, color="#64748b")
            ], spacing=2)

            # Fila para inventario
            filas_inv.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(l.get("id")))),
                ft.DataCell(info_texto),
                ft.DataCell(ft.ElevatedButton("Ver", bgcolor=PRIMARY, color="white", on_click=lambda e, libro=l: ver_detalle_libro(libro))),
            ]))

            # Fila para préstamos
            filas_prestamo.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(l.get("id")))),
                ft.DataCell(info_texto),
                ft.DataCell(ft.ElevatedButton("Seleccionar", bgcolor=SUCCESS, color="white", on_click=lambda e, libro=l: seleccionar_para_prestamo(libro))),
            ]))

        tabla_libros_inv.rows = filas_inv
        tabla_libros_prestamo.rows = filas_prestamo
        page.update()
    # SECCIÓN 1: VISTA DE TABLA librosDF
    inv_id = ft.Text("ID: -", color=TEXT)
    inv_nombre = ft.Text("Seleccione un libro", size=22, weight="bold", color="#0f172a")
    inv_autor = ft.Text("Autor: -", color=TEXT)
    inv_isbn = ft.Text("ISBN: -", color=TEXT)
    inv_genero = ft.Text("Género: -", color=TEXT)
    inv_anio = ft.Text("Año Publicación: -", color=TEXT)
    inv_descripcion = ft.Text("Seleccione un libro del catálogo para consultar sus detalles.", color=TEXT, italic=True)
    inv_cantidad = ft.Text("-", size=20, weight="bold", color=PRIMARY)

    inv_imagen = ft.Container(
        content=ft.Icon("menu_book", size=50, color="#94a3b8"),
        width=140, height=180, bgcolor="#e2e8f0", border_radius=8,
        alignment=ft.alignment.Alignment(0, 0),
    )

    seccion_inventario = ft.Column([
        ft.Text("Catálogo de Libros (Tabla librosDF)", size=24, weight="bold", color=PRIMARY),
        ft.ResponsiveRow([
            ft.Container(
                col={"sm": 12, "md": 5},
                content=ft.Card(
                    elevation=2,
                    content=ft.Container(
                        bgcolor="white",
                        padding=20,
                        content=ft.Column([
                            ft.Text("Búsqueda en Base de Datos", size=16, weight="bold", color=TEXT),
                            ft.TextField(
                                label="Buscar por título o ID...", prefix_icon="search", dense=True,
                                bgcolor="white",
                                on_change=lambda e: actualizar_tablas_libros(e.control.value)
                            ),
                            ft.Divider(height=1, color="#e2e8f0"),
                            ft.Row([tabla_libros_inv], scroll="auto"),
                        ], spacing=15),
                    )
                ),
            ),
            ft.Container(
                col={"sm": 12, "md": 7},
                content=ft.Card(
                    elevation=2,
                    content=ft.Container(
                        bgcolor="white",
                        padding=24,
                        content=ft.Column([
                            ft.Row([
                                inv_imagen,
                                ft.Column([
                                    inv_id,
                                    inv_nombre,
                                    inv_autor,
                                    inv_isbn,
                                    inv_genero,
                                    inv_anio,
                                ], expand=True, spacing=8),
                            ], vertical_alignment="start", spacing=20),
                            ft.Divider(height=20, color="#e2e8f0"),
                            ft.Text("Descripción / Sinopsis", weight="bold", color=TEXT),
                            inv_descripcion,
                            ft.Divider(height=20, color="#e2e8f0"),
                            ft.Row([
                                ft.Text("Ejemplares Disponibles en BD:", size=16, weight="bold", color=TEXT),
                                inv_cantidad
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ], spacing=10),
                    )
                ),
            ),
        ]),
    ], spacing=20)

    # SECCIÓN 2: PRÉSTAMOS
    prestamo_titulo = ft.Text("Seleccione un libro para solicitar", size=20, weight="bold", color=PRIMARY)
    prestamo_stock_disp = ft.Text("0", size=18, weight="bold", color=TEXT)
    nombre_solicitante = ft.TextField(label="Nombre del Estudiante", bgcolor="white")
    rut_solicitante = ft.TextField(label="RUT (Ej: 20.123.456-7)", bgcolor="white")
    curso_solicitante = ft.TextField(label="Curso (Ej: 3° Medio A)", bgcolor="white")
    cantidad_pedida = ft.TextField(label="Cantidad de Ejemplares", value="1", keyboard_type="number", bgcolor="white")

    def registrar_prestamo(e):
        if not seleccion["libro"]:
            snack("Por favor, seleccione un libro del catálogo.", DANGER)
            return

        if not nombre_solicitante.value or not rut_solicitante.value or not curso_solicitante.value:
            snack("Todos los campos del estudiante son obligatorios.", DANGER)
            return

        payload = {
            "libro_id": seleccion["libro"]["id"],
            "nombre_estudiante": nombre_solicitante.value,
            "rut": rut_solicitante.value,
            "curso": curso_solicitante.value,
            "cantidad": int(cantidad_pedida.value or 1),
        }

        try:
            res = requests.post(f"{API_URL}/prestamos", json=payload)
            if res.status_code == 201:
                snack("¡Préstamo registrado exitosamente en BD!", SUCCESS)
                nombre_solicitante.value = ""
                rut_solicitante.value = ""
                curso_solicitante.value = ""
                cantidad_pedida.value = "1"
                refrescar_todo()
            else:
                detail = res.json().get("detail", "Error al procesar el préstamo.")
                snack(detail, DANGER)
        except Exception as ex:
            snack(f"Error de conexión con el backend: {ex}", DANGER)

    seccion_prestamo = ft.Column([
        ft.Text("Módulo de Préstamos de Libros", size=24, weight="bold", color=PRIMARY),
        ft.ResponsiveRow([
            ft.Container(
                col={"sm": 12, "md": 5},
                content=ft.Card(
                    elevation=2,
                    content=ft.Container(
                        bgcolor="white",
                        padding=20,
                        content=ft.Column([
                            ft.Text("Seleccionar Libro a Solicitar", size=16, weight="bold", color=TEXT),
                            ft.Divider(height=1, color="#e2e8f0"),
                            ft.Row([tabla_libros_prestamo], scroll="auto"),
                        ], spacing=15),
                    )
                ),
            ),
            ft.Container(
                col={"sm": 12, "md": 7},
                content=ft.Card(
                    elevation=2,
                    content=ft.Container(
                        bgcolor="white",
                        padding=24,
                        content=ft.Column([
                            prestamo_titulo,
                            ft.Row([ft.Text("Ejemplares Disponibles:", size=16, weight="bold", color=TEXT), prestamo_stock_disp]),
                            ft.Divider(height=20, color="#e2e8f0"),
                            nombre_solicitante,
                            rut_solicitante,
                            curso_solicitante,
                            cantidad_pedida,
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                "Registrar Préstamo en BD", icon="check_circle_outline",
                                bgcolor=PRIMARY, color="white", on_click=registrar_prestamo,
                                style=ft.ButtonStyle(padding=20)
                            ),
                        ], spacing=12),
                    )
                ),
            ),
        ]),
    ], spacing=20)

    # SECCIÓN 3: HISTORIAL Y TRIGGERS
    tabla_prestamos = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(t, weight="bold")) for t in ["ID", "Fecha", "Estudiante", "RUT", "Curso", "Libro", "Cant.", "Estado", "Acción"]],
        rows=[],
    )

    tabla_triggers = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(t, weight="bold")) for t in ["ID Log", "ID Préstamo", "Estudiante", "Libro", "Cantidad", "Acción Trigger", "Fecha Evento"]],
        rows=[],
    )

    def marcar_como_devuelto(prestamo_id):
        res = requests.put(f"{API_URL}/prestamos/{prestamo_id}/devolver")
        if res.status_code == 200:
            snack("Libro devuelto. Registro de auditoría guardado por Trigger.", SUCCESS)
            refrescar_todo()
        else:
            snack("Error al procesar la devolución.", DANGER)

    def renderizar_tabla_prestamos():
        datos = api_get("/prestamos", params={"estado": seleccion["filtro_estado"]})
        filas = []
        for p in datos:
            es_prestado = p.get("estado") == "Prestado"
            accion = (
                ft.ElevatedButton("Devolver", bgcolor=WARNING, color=TEXT, on_click=lambda e, pid=p["id"]: marcar_como_devuelto(pid))
                if es_prestado else ft.Text("-")
            )
            filas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"#{p.get('id')}")),
                ft.DataCell(ft.Text(str(p.get("fecha", "")))),
                ft.DataCell(ft.Text(p.get("solicitante", ""))),
                ft.DataCell(ft.Text(p.get("rut", ""))),
                ft.DataCell(ft.Text(p.get("curso", ""))),
                ft.DataCell(ft.Text(p.get("herramienta", ""))),
                ft.DataCell(ft.Text(str(p.get("cantidad", 1)))),
                ft.DataCell(ft.Container(
                    content=ft.Text(p.get("estado", ""), color="white", size=12, weight="bold"),
                    bgcolor=WARNING if es_prestado else SUCCESS,
                    padding=8, border_radius=6
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
                    content=ft.Text(log.get("accion", ""), color="white", size=12, weight="bold"),
                    bgcolor=PRIMARY if es_registro else SUCCESS,
                    padding=8, border_radius=6
                )),
                ft.DataCell(ft.Text(str(log.get("fecha_registro", "")))),
            ]))
        tabla_triggers.rows = filas

    def filtrar_estado_prestamos(estado):
        seleccion["filtro_estado"] = estado
        renderizar_tabla_prestamos()
        page.update()

    sub_vista_prestamos = ft.Container(
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

    sub_vista_triggers = ft.Container(
        ft.Column([
            ft.Text("Registros automáticos creados por los Triggers SQL al Insertar/Actualizar:", color="#64748b"),
            ft.Row([tabla_triggers], scroll="auto"),
        ], spacing=12),
        padding=16
    )

    contenedor_subtabs = ft.Container(content=sub_vista_prestamos)

    def cambiar_subvista(idx):
        btn_sub_prestamos.bgcolor = PRIMARY if idx == 0 else "#cbd5e1"
        btn_sub_prestamos.color = "white" if idx == 0 else TEXT
        btn_sub_triggers.bgcolor = PRIMARY if idx == 1 else "#cbd5e1"
        btn_sub_triggers.color = "white" if idx == 1 else TEXT

        contenedor_subtabs.content = sub_vista_prestamos if idx == 0 else sub_vista_triggers
        page.update()

    btn_sub_prestamos = ft.ElevatedButton(
        "Préstamos Activos (prestamosDF)", bgcolor=PRIMARY, color="white",
        on_click=lambda e: cambiar_subvista(0)
    )
    btn_sub_triggers = ft.ElevatedButton(
        "Auditoría de Triggers (historial_prestamosDF)", bgcolor="#cbd5e1", color=TEXT,
        on_click=lambda e: cambiar_subvista(1)
    )

    seccion_historial = ft.Column([
        ft.Text("Historial y Registros Automáticos", size=24, weight="bold", color=PRIMARY),
        ft.Card(
            elevation=2,
            content=ft.Container(
                bgcolor="white",
                padding=20,
                content=ft.Column([
                    ft.Row([btn_sub_prestamos, btn_sub_triggers], spacing=10),
                    ft.Divider(height=1, color="#e2e8f0"),
                    contenedor_subtabs
                ], spacing=15),
            )
        )
    ], spacing=20)

    # CONFIGURACIÓN Y NAVEGACIÓN
    def refrescar_todo():
        actualizar_tablas_libros()
        renderizar_tabla_prestamos()
        renderizar_tabla_triggers()
        page.update()

    contenido_tabs = ft.Container(seccion_inventario, padding=30, expand=True)

    def cambiar_tab(e):
        idx = e.control.data
        for btn in tab_buttons:
            activo = btn.data == idx
            btn.bgcolor = PRIMARY if activo else "white"
            btn.color = "white" if activo else TEXT
            btn.elevation = 2 if activo else 0

        if idx == 0:
            contenido_tabs.content = seccion_inventario
        elif idx == 1:
            contenido_tabs.content = seccion_prestamo
        elif idx == 2:
            contenido_tabs.content = seccion_historial
        page.update()

    tab_buttons = [
        ft.ElevatedButton("📚 Catálogo (librosDF)", data=0, bgcolor=PRIMARY, color="white", elevation=2, on_click=cambiar_tab),
        ft.ElevatedButton("📖 Préstamos", data=1, bgcolor="white", color=TEXT, elevation=0, on_click=cambiar_tab),
        ft.ElevatedButton("📋 Historial y Triggers", data=2, bgcolor="white", color=TEXT, elevation=0, on_click=cambiar_tab),
    ]

    body = ft.Column([
        ft.Container(
            content=ft.Text("Sistema de Biblioteca Conectado a Base de Datos SQL", size=22, weight="bold", color="white"),
            bgcolor=PRIMARY, padding=20, alignment=ft.alignment.Alignment(-1, 0), shadow=ft.BoxShadow(blur_radius=4, color="black12")
        ),
        ft.Container(content=ft.Row(tab_buttons, spacing=15), padding=20),
        contenido_tabs,
    ], expand=True, spacing=0)

    page.add(body)
    refrescar_todo()

if __name__ == "__main__":
    ft.app(target=main)