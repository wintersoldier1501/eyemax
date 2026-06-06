import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import flet as ft
import httpx
import os
import asyncio
import io



SERVER_URL = "http://192.168.100.78:8080"

async def main(page: ft.Page):
    # Configuración de ventana para simular una pantalla móvil
    page.title = "Eyemax - Scanner de Joyería"
    page.window_width = 390
    page.window_height = 800
    page.window_resizable = False
    page.padding = 0
    page.bgcolor = "#0F0F10"

    # Función para abrir selector de archivos nativo usando Tkinter
    def select_file_native():
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(
                title="Seleccionar foto de joyería",
                filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png;*.webp;*.gif")]
            )
            root.destroy()
            return file_path
        except Exception:
            return None

    # Función para procesar y enviar la imagen al servidor
    async def process_and_upload(file_name, file_bytes, file_path=None):
        # Restablecer visor para una nueva captura y mostrar spinner
        camera_card.content = camera_view_content
        result_card.visible = False
        loading_container.visible = True
        page.update()
        
        try:
            if not file_bytes:
                raise Exception("No se encontraron bytes válidos en el archivo seleccionado.")
                
            # Determinar tipo MIME de la imagen
            mime_type = "image/jpeg"
            if file_name.lower().endswith(".png"):
                mime_type = "image/png"
            elif file_name.lower().endswith(".webp"):
                mime_type = "image/webp"
                
            files = {'image': (file_name, file_bytes, mime_type)}
            print(f"Enviando imagen real '{file_name}' ({len(file_bytes)} bytes) al servidor...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SERVER_URL}/api/recognize",
                    files=files,
                    timeout=120.0
                )
                
            if response.status_code == 200:
                data = response.json()
                print(f"Respuesta exitosa recibida: {data}")
                
                # Rellenar datos en la UI
                res_code.value = str(data.get("CODIGO", "N/A"))
                
                # Tratar descripción
                desc_val = data.get("DESCRIPCION", "-")
                res_desc.value = str(desc_val) if desc_val else "Sin descripción disponible"
                
                # Tratar material
                res_material.value = str(data.get("MATERIAL", "N/A")).upper()
                
                # Tratar precio
                price_val = data.get("PRECIO venta publico", 0.0)
                try:
                    price_float = float(price_val)
                except (ValueError, TypeError):
                    price_float = 0.0
                res_price.value = f"${price_float:,.2f} MXN"
                
                # Tratar modo de respuesta (Real vs Simulación)
                mode_val = data.get("mode", "UNKNOWN")
                res_mode.value = f"Reconocimiento: {str(mode_val)}"
                
                # Mostrar tarjeta de resultados
                loading_container.visible = False
                result_card.visible = True
                show_toast("Pieza identificada con éxito", is_error=False)
            else:
                error_msg = response.json().get("error", "Error desconocido")
                raise Exception(error_msg)
                
        except Exception as ex:
            print(f"Error durante el procesamiento del archivo seleccionado: {ex}")
            loading_container.visible = False
            show_toast(f"Error al analizar imagen: {str(ex)}", is_error=True)
            
        page.update()

    # Callback al presionar "SELECCIONAR FOTO" en PC (diálogo nativo)
    async def on_select_photo_click(e):
        select_photo_btn.disabled = True
        page.update()
        
        file_path = await asyncio.to_thread(select_file_native)
        
        select_photo_btn.disabled = False
        page.update()
        
        if not file_path:
            return
            
        try:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            await process_and_upload(file_name, file_bytes, file_path)
        except Exception as ex:
            show_toast(f"Error al leer archivo: {str(ex)}", is_error=True)

    # Callback del FilePicker al seleccionar imagen real en Android/iOS
    async def on_file_selected(e):
        if not e.files:
            return
        try:
            picked_file = e.files[0]
            file_name = picked_file.name
            
            # Leer los bytes reales de la imagen seleccionada
            file_bytes = None
            if picked_file.path:
                with open(picked_file.path, "rb") as f:
                    file_bytes = f.read()
            elif picked_file.bytes:
                file_bytes = picked_file.bytes
                
            await process_and_upload(file_name, file_bytes, picked_file.path)
        except Exception as ex:
            show_toast(f"Error al leer archivo: {str(ex)}", is_error=True)
    
    # Paleta de colores Premium (Slate Gray #646267)
    COLOR_BG_GRADIENT_START = "#1B1B1D"
    COLOR_BG_GRADIENT_END = "#0C0C0E"
    COLOR_GOLD = "#D4AF37"
    COLOR_GOLD_LIGHT = "#F3E5AB"
    COLOR_DARK_CARD = "#232325"
    COLOR_BORDER = "#646267"
    COLOR_TEXT_PRIMARY = "#FFFFFF"
    COLOR_TEXT_SECONDARY = "#9C9CA0"
    COLOR_GREEN = "#00E676"
    COLOR_RED = "#FF1744"

    # --- Elementos de UI ---
    
    # Indicador de estado del servidor
    status_dot = ft.Container(width=8, height=8, bgcolor=COLOR_RED, border_radius=4)
    status_text = ft.Text("Desconectado", size=11, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD)
    status_badge = ft.Row(
        controls=[status_dot, status_text],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=6
    )

    # Input para simular la foto
    code_input = ft.TextField(
        label="código de barra / foto",
        value="AX1362",
        border_color=COLOR_GOLD,
        focused_border_color=COLOR_GOLD_LIGHT,
        color=COLOR_TEXT_PRIMARY,
        text_align=ft.TextAlign.CENTER,
        width=280,
        height=50,
        text_size=14,
        label_style=ft.TextStyle(color=COLOR_TEXT_SECONDARY, size=11)
    )

    # Detectar si estamos en un dispositivo móvil
    is_mobile = page.platform in ["android", "ios"]
    
    file_picker = None
    if is_mobile:
        file_picker = ft.FilePicker()
        file_picker.on_result = on_file_selected
        page.overlay.append(file_picker)
        
    def on_button_click(e):
        try:
            if is_mobile and file_picker:
                file_picker.pick_files(allow_multiple=False)
            else:
                page.run_task(on_select_photo_click, e)
        except Exception as ex:
            show_toast(f"Error al abrir selector: {str(ex)}", is_error=True)

    # Botón Seleccionar Foto
    select_photo_btn = ft.Button(
        content=ft.Text("SELECCIONAR FOTO", color="#0F0F1A", weight=ft.FontWeight.BOLD),
        bgcolor=COLOR_GOLD,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        width=280,
        height=45,
        on_click=on_button_click
    )

    # Visor de la cámara placeholder (Simulador de Captura)
    camera_view_content = ft.Column(
        controls=[
            ft.Icon(ft.Icons.CAMERA_ALT, size=46, color=COLOR_TEXT_SECONDARY),
            ft.Text(
                "Scanner Accesorizate",
                size=16,
                color=COLOR_TEXT_PRIMARY,
                weight=ft.FontWeight.BOLD
            ),
            ft.Text(
                "Escribe un código o nombre de foto para el reconocimiento:",
                size=11,
                color=COLOR_TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=5),
            code_input,
            select_photo_btn,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    
    camera_card = ft.Container(
        content=camera_view_content,
        width=330,
        height=330,
        bgcolor=COLOR_DARK_CARD,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=24,
        alignment=ft.alignment.Alignment.CENTER,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    )

    # Spinner de carga
    loading_spinner = ft.ProgressRing(width=30, height=30, color=COLOR_GOLD)
    loading_text = ft.Text("Analizando pieza...", size=13, color=COLOR_TEXT_PRIMARY, italic=True)
    loading_container = ft.Column(
        controls=[loading_spinner, loading_text],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        visible=False
    )

    # Tarjeta de resultados (Diseño Premium Glassmorphic)
    res_code = ft.Text("-", size=24, color=COLOR_GOLD, weight=ft.FontWeight.BOLD)
    res_price = ft.Text("$0.00 MXN", size=26, color=COLOR_GOLD_LIGHT, weight=ft.FontWeight.W_900)
    res_desc = ft.Text("-", size=13, color=COLOR_TEXT_PRIMARY, text_align=ft.TextAlign.CENTER)
    res_material = ft.Text("-", size=11, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD)
    res_badge = ft.Container(
        content=res_material,
        bgcolor="#2C2C2E",
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border=ft.Border.all(1, COLOR_BORDER)
    )
    res_mode = ft.Text("Modo: -", size=10, color=COLOR_TEXT_SECONDARY, italic=True)

    result_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("PRODUCTO DETECTADO", size=12, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=1.5)),
                        res_badge
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color=COLOR_BORDER, height=15),
                ft.Row(
                    controls=[res_code, res_price],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(height=6),
                res_desc,
                ft.Divider(color=COLOR_BORDER, height=15),
                ft.Row(
                    controls=[res_mode],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        width=330,
        bgcolor="#252528",
        border_radius=20,
        padding=20,
        border=ft.Border.all(1.5, COLOR_GOLD),
        visible=False,
        animate=ft.Animation(400, ft.AnimationCurve.DECELERATE)
    )

    # --- Lógica de Negocio ---
    
    async def check_server_status():
        """Verifica el estado del servidor de manera asíncrona y segura."""
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{SERVER_URL}/api/status", timeout=2.0)
                if response.status_code == 200:
                    status_dot.bgcolor = COLOR_GREEN
                    status_text.value = "Conectado"
                    status_text.color = COLOR_GREEN
                else:
                    raise Exception("Offline")
            except Exception:
                status_dot.bgcolor = COLOR_RED
                status_text.value = "Offline (Servidor Apagado)"
                status_text.color = COLOR_RED
            try:
                page.update()
            except Exception:
                break # Evitar excepciones al cerrar la ventana
            await asyncio.sleep(3)

    # Iniciar la tarea asíncrona de fondo
    page.run_task(check_server_status)

    # Callback al presionar el disparador central
    async def on_scan_click(e):
        # Restablecer visor para una nueva captura
        camera_card.content = camera_view_content
        result_card.visible = False
        loading_container.visible = False
        page.update()
        
        try:
            file_name = code_input.value.strip()
            if not file_name:
                show_toast("Por favor escribe un código para simular la foto", is_error=True)
                return
                
            # Si no tiene extensión, le agregamos .jpg para que el servidor lo procese como simulación de imagen
            if not '.' in file_name:
                file_name_with_ext = f"{file_name}.jpg"
            else:
                file_name_with_ext = file_name
                
            # Mostrar el spinner de carga
            loading_container.visible = True
            page.update()
            
            # Enviar bytes simulados
            file_bytes = b"simulated image data"
            files = {'image': (file_name_with_ext, file_bytes, 'image/jpeg')}
            print(f"Enviando solicitud simulada para '{file_name_with_ext}' al servidor...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SERVER_URL}/api/recognize",
                    files=files,
                    timeout=120.0
                )
                
            if response.status_code == 200:
                data = response.json()
                print(f"Respuesta exitosa recibida: {data}")
                
                try:
                    # Rellenar datos en la UI
                    res_code.value = str(data.get("CODIGO", "N/A"))
                    
                    # Tratar descripción
                    desc_val = data.get("DESCRIPCION", "-")
                    res_desc.value = str(desc_val) if desc_val else "Sin descripción disponible"
                    
                    # Tratar material
                    res_material.value = str(data.get("MATERIAL", "N/A")).upper()
                    
                    # Tratar precio
                    price_val = data.get("PRECIO venta publico", 0.0)
                    try:
                        price_float = float(price_val)
                    except (ValueError, TypeError):
                        price_float = 0.0
                    res_price.value = f"${price_float:,.2f} MXN"
                    
                    # Tratar modo de respuesta (Real vs Simulación)
                    mode_val = data.get("mode", "UNKNOWN")
                    res_mode.value = f"Reconocimiento: {str(mode_val)}"
                    
                    # Mostrar tarjeta de resultados
                    loading_container.visible = False
                    result_card.visible = True
                    show_toast("Pieza identificada con éxito", is_error=False)
                except Exception as render_ex:
                    import traceback
                    with open("app_crash.log", "w", encoding="utf-8") as crash_f:
                        traceback.print_exc(file=crash_f)
                    print(f"Error durante el renderizado en la UI: {render_ex}")
                    raise render_ex
            else:
                error_msg = response.json().get("error", "Error desconocido")
                raise Exception(error_msg)
                
        except Exception as ex:
            print(f"Error durante el análisis del archivo real: {ex}")
            loading_container.visible = False
            # Revertir visor si hay error
            camera_card.content = camera_view_content
            show_toast(f"Error al analizar imagen: {str(ex)}", is_error=True)
            
        page.update()


    def show_toast(message, is_error=False):
        """Muestra una barra de notificación (SnackBar) simple."""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=COLOR_RED if is_error else COLOR_GREEN
        )
        page.snack_bar.open = True
        page.update()

    # --- Maquetación Principal de la App Móvil ---
    
    # Contenedor principal que envuelve todo el contenido móvil simulado
    app_layout = ft.Container(
        gradient=ft.LinearGradient(
            colors=[COLOR_BG_GRADIENT_START, COLOR_BG_GRADIENT_END],
            begin=ft.alignment.Alignment.TOP_CENTER,
            end=ft.alignment.Alignment.BOTTOM_CENTER
        ),
        width=390,
        height=800,
        padding=ft.Padding.only(left=20, right=20, top=40, bottom=30),
        content=ft.Column(
            controls=[
                # Barra superior con Logotipo centrado
                ft.Row(
                    controls=[
                        ft.Image(
                            src="/logo.png",
                            width=220,
                            height=78,
                            fit="contain"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                # Estado del servidor centrado
                status_badge,
                ft.Container(height=5),
                
                # Tarjeta del Visor / Cámara
                ft.Row(controls=[camera_card], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=15),
                
                # Contenedor dinámico (Spinner o Tarjeta de Resultados)
                ft.Row(
                    controls=[
                        loading_container,
                        result_card
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
                ft.Container(expand=True), # Empujar el disparador hacia abajo
                
                # Disparador central de Cámara / Captura
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Container(
                                    content=ft.IconButton(
                                        icon=ft.Icons.CAMERA_ALT,
                                        icon_size=36,
                                        icon_color="#000000",
                                        on_click=on_scan_click
                                    ),
                                    width=76,
                                    height=76,
                                    bgcolor=COLOR_GOLD,
                                    border_radius=38,
                                    alignment=ft.alignment.Alignment.CENTER,
                                    shadow=ft.BoxShadow(
                                        spread_radius=1,
                                        blur_radius=15,
                                        color="#D4AF3740",
                                        offset=ft.Offset(0, 5)
                                    )
                                ),
                                ft.Text("ESCANEAR PIEZA", size=10, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=1.2))
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    )

    page.add(app_layout)


if __name__ == '__main__':
    ft.app(target=main, assets_dir="assets")
