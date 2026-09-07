"""
Sistema de Gestión de Biblioteca + Panel de Administración
Compatible con Flet 0.86.5+

Ejecutar:
  pip install flet
  flet run app.py
"""

import flet as ft
from logic import SistemaPrestamos, PanelAdmin, ErrorNegocio

# Paleta de colores
PRIMARY = "#1a365d"     # Azul biblioteca
BG = "#f7fafc"
TEXT = "#2d3748"
SUCCESS = "#28a745"
WARNING = "#ffc107"
DANGER = "#dc3545"

ADMIN_PRIMARY = "#2c3e50"
ADMIN_ACCENT = "#3498db"
ADMIN_SUCCESS = "#27ae60"
ADMIN_DANGER = "#e74c3c"


def main(page: ft.Page):
    page.title = "Sistema de Gestión de Biblioteca"
    page.bgcolor = BG
    page.padding = 0
    page.window.width = 1100
    page.window.height = 780

    sistema = SistemaPrestamos()
    admin = PanelAdmin()
    seleccion = {"item": None, "filtro_estado": "Todos"}

    def snack(mensaje: str, color=None):
        page.open(ft.SnackBar(content=ft.Text(mensaje), bgcolor=color))

    # ======================================================================
    # SECCIÓN 1: INVENTARIO DE LIBROS
    # ======================================================================
    inv_nombre = ft.Text("Seleccione un libro", size=20, weight="bold", color=TEXT)
    inv_autor = ft.Text("Autor: -", color=TEXT)
    inv_descripcion = ft.Text(
        "Seleccione un libro del catálogo para consultar sus detalles y disponibilidad.", color=TEXT
    )
    inv_estado = ft.Text("-", color=TEXT)
    inv_cantidad = ft.Text("-", size=18, weight="bold", color=PRIMARY)
    inv_imagen = ft.Container(
        content=ft.Icon("menu_book", size=60, color="#94a3b8"),
        width=180, height=140, bgcolor="#cbd5e1", border_radius=8,
        alignment=ft.Alignment(0, 0),
    )

    def ver_detalle_libro(nombre_key: str):
        item = sistema.inventario.get(nombre_key)
        if not item:
            return
        seleccion["item"] = nombre_key
        libro_id = item.get("id", "N/A")
        inv_nombre.value = f"[{libro_id}] {nombre_key}"
        inv_autor.value = f"Autor: {item.get('autor', 'Desconocido')}"
        inv_descripcion.value = item.get("descripcion", "Sin descripción disponible.")
        inv_estado.value = item.get("estado", "Disponible")
        inv_cantidad.value = f"{item.get('cantidad', 0)} ejemplares"
        page.update()

    def construir_lista_libros(on_click_item, filtro: str = ""):
        filtro_lower = filtro.strip().lower()
        items_filtrados = []
        
        for nombre, datos in sistema.inventario.items():
            libro_id = str(datos.get("id", "")).lower()
            if not filtro_lower or filtro_lower in nombre.lower() or filtro_lower in libro_id:
                items_filtrados.append((nombre, datos))

        return [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon("book", color=PRIMARY),
                        ft.Column(
                            [
                                ft.Text(nombre, weight="bold", overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(
                                    f"ID/ISBN: {datos.get('id', 'N/A')} | Autor: {datos.get('autor', 'N/A')}",
                                    size=12,
                                    color="#64748b",
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=8,
                border_radius=6,
                on_click=lambda e, n=nombre: on_click_item(n),
                ink=True,
            )
            for nombre, datos in items_filtrados
        ]

    lista_libros_inv = ft.ListView(
        controls=construir_lista_libros(ver_detalle_libro),
        height=380,
        spacing=4
    )

    def buscar_libro_change(e):
        lista_libros_inv.controls = construir_lista_libros(ver_detalle_libro, e.control.value)
        page.update()

    seccion_inventario = ft.Column(
        [
            ft.Text("Catálogo General de Libros", size=22, weight="bold", color=TEXT),
            ft.ResponsiveRow(
                [
                    ft.Container(
                        col={"sm": 12, "md": 5},
                        content=ft.Card(content=ft.Container(
                            ft.Column([
                                ft.Text("Búsqueda de Libros", size=16, weight="bold"),
                                ft.TextField(
                                    label="Buscar por título o ID...",
                                    prefix_icon="search",
                                    on_change=buscar_libro_change,
                                    dense=True
                                ),
                                lista_libros_inv,
                            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                            padding=16,
                        )),
                    ),
                    ft.Container(
                        col={"sm": 12, "md": 7},
                        content=ft.Card(content=ft.Container(
                            ft.Row([
                                inv_imagen,
                                ft.Column([
                                    inv_nombre,
                                    inv_autor,
                                    ft.Text("Información del Libro", weight="bold"),
                                    inv_descripcion,
                                    ft.Row([ft.Text("Estado:", weight="bold"), inv_estado]),
                                    ft.Row([ft.Text("Ejemplares Disponibles:", weight="bold"), inv_cantidad]),
                                ], expand=True, spacing=6),
                            ], vertical_alignment="start"),
                            padding=16,
                        )),
                    ),
                ],
            ),
        ],
        spacing=16,
    )

    # ======================================================================
    # SECCIÓN 2: SOLICITAR PRÉSTAMO DE LIBRO
    # ======================================================================
    prestamo_titulo = ft.Text("Seleccione un libro para solicitar", size=18, weight="bold")
    prestamo_stock_disp = ft.Text("0", weight="bold")
    nombre_solicitante = ft.TextField(label="Nombre del Lector / Estudiante", hint_text="Ej. María González")
    curso_solicitante = ft.TextField(label="Curso o RUT del Lector", hint_text="Ej. 2° Medio A / 20.123.456-7")
    cantidad_pedida = ft.TextField(label="Cantidad de Ejemplares", value="1", keyboard_type="number")

    def seleccionar_para_prestamo(nombre_key: str):
        item = sistema.inventario.get(nombre_key)
        if not item:
            return
        seleccion["item"] = nombre_key
        prestamo_titulo.value = f"Solicitar Préstamo: {nombre_key}"
        prestamo_stock_disp.value = str(item.get("cantidad", 0))
        page.update()

    lista_libros_prestamo = ft.ListView(
        controls=construir_lista_libros(seleccionar_para_prestamo),
        height=380,
        spacing=4
    )

    def buscar_prestamo_change(e):
        lista_libros_prestamo.controls = construir_lista_libros(seleccionar_para_prestamo, e.control.value)
        page.update()

    def registrar_prestamo(e):
        try:
            sistema.registrar_prestamo(
                seleccion["item"], nombre_solicitante.value, curso_solicitante.value, cantidad_pedida.value
            )
        except ErrorNegocio as err:
            snack(str(err), DANGER)
            return

        item_nombre = seleccion["item"]
        prestamo_stock_disp.value = str(sistema.inventario[item_nombre]["cantidad"])
        snack("¡Préstamo de libro registrado con éxito!", SUCCESS)

        nombre_solicitante.value = ""
        curso_solicitante.value = ""
        cantidad_pedida.value = "1"

        renderizar_tabla_historial()
        ver_detalle_libro(item_nombre)
        page.update()

    seccion_prestamo = ft.Column(
        [
            ft.Text("Módulo de Préstamos de Biblioteca", size=22, weight="bold", color=TEXT),
            ft.ResponsiveRow(
                [
                    ft.Container(
                        col={"sm": 12, "md": 5},
                        content=ft.Card(content=ft.Container(
                            ft.Column([
                                ft.Text("Seleccionar Libro", size=16, weight="bold"),
                                ft.TextField(label="Buscar por título o ID...", prefix_icon="search",
                                             on_change=buscar_prestamo_change, dense=True),
                                lista_libros_prestamo,
                            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                            padding=16,
                        )),
                    ),
                    ft.Container(
                        col={"sm": 12, "md": 7},
                        content=ft.Card(content=ft.Container(
                            ft.Column([
                                prestamo_titulo,
                                ft.Row([ft.Text("Ejemplares Disponibles:", weight="bold"),
                                        prestamo_stock_disp, ft.Text("unidades")]),
                                nombre_solicitante,
                                curso_solicitante,
                                cantidad_pedida,
                                ft.ElevatedButton("Registrar Préstamo de Libro", icon="check_circle_outline",
                                                   bgcolor=PRIMARY, color="white", on_click=registrar_prestamo),
                            ], spacing=12),
                            padding=16,
                        )),
                    ),
                ],
            ),
        ],
        spacing=16,
    )

    # ======================================================================
    # SECCIÓN 3: HISTORIAL DE PRÉSTAMOS
    # ======================================================================
    tabla_historial = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(t)) for t in
                 ["ID Préstamo", "Fecha/Hora", "Lector / Solicitante", "Curso / Identificación", "Libro", "Cantidad", "Estado", "Acción"]],
        rows=[],
    )
    buscar_historial_field = ft.TextField(label="Buscar por lector, libro o curso...",
                                           prefix_icon="search")

    def marcar_como_devuelto(prestamo_id: int, e=None):
        prestamo = sistema.marcar_como_devuelto(prestamo_id)
        if prestamo:
            renderizar_tabla_historial()
            if seleccion["item"] == prestamo["herramienta"]:
                prestamo_stock_disp.value = str(sistema.inventario[prestamo["herramienta"]]["cantidad"])
            ver_detalle_libro(prestamo["herramienta"])
            page.update()

    def renderizar_tabla_historial():
        filas = []
        for p in sistema.filtrar_historial(seleccion["filtro_estado"], buscar_historial_field.value):
            es_prestado = p["estado"] == "Prestado"
            accion = (
                ft.ElevatedButton("Devolver Libro", bgcolor=WARNING, color=TEXT,
                                  on_click=lambda e, pid=p["id"]: marcar_como_devuelto(pid))
                if es_prestado else ft.Text("-")
            )
            tag_color = WARNING if es_prestado else SUCCESS
            filas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(f'#{str(p["id"]).zfill(4)[-4:]}')),
                ft.DataCell(ft.Text(p["fecha"])),
                ft.DataCell(ft.Text(p["solicitante"])),
                ft.DataCell(ft.Text(p["curso"])),
                ft.DataCell(ft.Text(p["herramienta"])),
                ft.DataCell(ft.Text(str(p["cantidad"]))),
                ft.DataCell(ft.Container(
                    content=ft.Text(p["estado"], color="white", size=12),
                    bgcolor=tag_color, padding=ft.Padding(8, 4, 8, 4), border_radius=12,
                )),
                ft.DataCell(accion),
            ]))
        tabla_historial.rows = filas
        page.update()

    def filtrar_estado(estado: str):
        seleccion["filtro_estado"] = estado
        for b in filtro_botones:
            activo = b.data == estado
            b.bgcolor = PRIMARY if activo else "#e2e8f0"
            b.color = "white" if activo else TEXT
        renderizar_tabla_historial()

    filtro_botones = [
        ft.ElevatedButton("Todos", data="Todos", bgcolor=PRIMARY, color="white",
                           on_click=lambda e: filtrar_estado("Todos")),
        ft.ElevatedButton("En Préstamo", data="Prestado", bgcolor="#e2e8f0", color=TEXT,
                           on_click=lambda e: filtrar_estado("Prestado")),
        ft.ElevatedButton("Devueltos", data="Devuelto", bgcolor="#e2e8f0", color=TEXT,
                           on_click=lambda e: filtrar_estado("Devuelto")),
    ]
    buscar_historial_field.on_change = lambda e: renderizar_tabla_historial()

    seccion_historial = ft.Column(
        [
            ft.Text("Historial de Préstamos de Libros", size=22, weight="bold", color=TEXT),
            ft.Card(content=ft.Container(
                ft.Column([
                    buscar_historial_field,
                    ft.Row(filtro_botones),
                    ft.Row([tabla_historial], scroll="auto"),
                ], spacing=12),
                padding=16,
            )),
        ],
        spacing=16,
    )

    # ======================================================================
    # VISTA "SISTEMA DE BIBLIOTECA"
    # ======================================================================
    contenido_tabs = ft.Container(seccion_inventario, padding=20, expand=True)

    def cambiar_tab_prestamos(e):
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
        ft.ElevatedButton("📚 Catálogo de Libros", data=0, bgcolor=PRIMARY, color="white", on_click=cambiar_tab_prestamos),
        ft.ElevatedButton("📖 Solicitar Préstamo", data=1, bgcolor="#cbd5e1", color=TEXT, on_click=cambiar_tab_prestamos),
        ft.ElevatedButton("📋 Historial de Libros", data=2, bgcolor="#cbd5e1", color=TEXT, on_click=cambiar_tab_prestamos),
    ]

    barra_pestañas = ft.Container(
        content=ft.Row(tab_buttons, spacing=10),
        padding=ft.Padding(left=20, top=16, right=20, bottom=0),
    )

    vista_prestamos = ft.Column(
        [
            ft.Container(content=ft.Text("- Sistema de Biblioteca -", size=20, weight="bold", color="white"),
                         bgcolor=PRIMARY, padding=16),
            barra_pestañas,
            contenido_tabs,
        ],
        expand=True, spacing=0,
    )

    # ======================================================================
    # VISTA "PANEL ADMIN BIBLIOTECA"
    # ======================================================================
    scanner_result = ft.Container(visible=False, padding=12, border_radius=6)
    barcode_input = ft.TextField(label="Escanee o escriba el ISBN / Código del libro (Ej: 978-84-376-0494-7)",
                                  autofocus=True, expand=True)

    def verificar_producto(e):
        ok, mensaje = admin.verificar_codigo(barcode_input.value)
        scanner_result.bgcolor = "#d4edda" if ok else "#f8d7da"
        scanner_result.content = ft.Text(mensaje, color="#155724" if ok else "#721c24")
        scanner_result.visible = True
        barcode_input.value = ""
        page.update()

    tabla_peticiones = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(t)) for t in
                 ["ID Petición", "Usuario / Estudiante", "Libro Solicitado", "Fecha", "Acción"]],
        rows=[],
    )

    def gestionar_peticion(peticion_id: str, aceptar: bool):
        admin.resolver_peticion(peticion_id, aceptar)
        snack(f"Petición {peticion_id} {'aceptada' if aceptar else 'rechazada'}.",
              ADMIN_SUCCESS if aceptar else ADMIN_DANGER)
        render_tabla_peticiones()
        page.update()

    def render_tabla_peticiones():
        tabla_peticiones.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(p["id"])),
                ft.DataCell(ft.Text(p["usuario"])),
                ft.DataCell(ft.Text(p["equipo"])),
                ft.DataCell(ft.Text(p["fecha"])),
                ft.DataCell(ft.Row([
                    ft.ElevatedButton("Aceptar", bgcolor=ADMIN_SUCCESS, color="white",
                                       on_click=lambda e, pid=p["id"]: gestionar_peticion(pid, True)),
                    ft.ElevatedButton("Rechazar", bgcolor=ADMIN_DANGER, color="white",
                                       on_click=lambda e, pid=p["id"]: gestionar_peticion(pid, False)),
                ])),
            ])
            for p in admin.peticiones
        ]

    render_tabla_peticiones()

    vista_admin = ft.Column(
        [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("BibliotecaAdmin", size=22, weight="bold", color="white"),
                        ft.Row([
                            ft.Text("👤 Encargado(a): Damián Fuentes", color="white"),
                            ft.OutlinedButton(content=ft.Text("Cerrar Sesión", color="white")),
                        ]),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=ADMIN_PRIMARY, padding=20,
            ),
            ft.Container(
                ft.Column([
                    ft.Card(content=ft.Container(
                        ft.Column([
                            ft.Text("Peticiones de Préstamo Pendientes", size=18, weight="bold"),
                            ft.Row([tabla_peticiones], scroll="auto"),
                        ], spacing=12),
                        padding=16,
                    )),
                    ft.Card(content=ft.Container(
                        ft.Column([
                            ft.Text("Verificación de Libro Físico por ISBN / Código", size=18, weight="bold"),
                            ft.Text("Conecte el lector y escanee el código de barras del libro para "
                                    "verificarlo antes de la entrega."),
                            ft.Row([
                                barcode_input,
                                ft.ElevatedButton("Verificar Libro", bgcolor=ADMIN_ACCENT, color="white",
                                                  on_click=verificar_producto),
                            ]),
                            scanner_result,
                        ], spacing=12),
                        padding=16,
                    )),
                ], spacing=16),
                padding=20,
            ),
        ],
        expand=True, spacing=0, scroll="auto",
    )

    # ======================================================================
    # NAVEGACIÓN PRINCIPAL
    # ======================================================================
    body = ft.Container(content=vista_prestamos, expand=True)

    def cambiar_vista(e):
        body.content = vista_prestamos if e.control.selected_index == 0 else vista_admin
        page.update()

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type="all",
        min_width=90,
        bgcolor="#e2e8f0",
        destinations=[
            ft.NavigationRailDestination(icon="menu_book", label="Biblioteca"),
            ft.NavigationRailDestination(icon="admin_panel_settings", label="Admin"),
        ],
        on_change=cambiar_vista,
    )

    page.add(ft.Row([nav_rail, ft.VerticalDivider(width=1), body], expand=True))


if __name__ == "__main__":
    ft.app(target=main)