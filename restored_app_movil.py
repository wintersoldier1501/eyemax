Created At: 2026-05-26T16:30:23Z
Completed At: 2026-05-26T16:30:23Z
File Path: `file:///c:/Users/Accesorizate1/Downloads/Eyemax/app_movil.py`
Total Lines: 368
Total Bytes: 14213
Showing lines 1 to 368
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import flet as ft
import httpx
import os
import threading
import time

SERVER_URL = "http://127.0.0.1:5000"

async def main(page: ft.Page):
# Configuración de ventana para simular una pantalla móvil
page.title = "Eyemax - Scanner de Joyería"
page.window_width = 390
page.window_height = 800
page.window_resizable = False
page.padding = 0
page.bgcolor = "#0F0F1A"

# Paleta de colores Premium
COLOR_BG_GRADIENT_START = "#14142B"
COLOR_BG_GRADIENT_END = "#0B0B14"
COLOR_GOLD = "#D4AF37"
COLOR_GOLD_LIGHT = "#F3E5AB"
COLOR_DARK_CARD = "#1D1D35"
COLOR_BORDER = "#2E2E54"
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#A0A0C0"
COLOR_GREEN = "#00E676"
COLOR_RED = "#FF1744"

# Variable para almacenar la ruta de la imagen seleccionada
selected_image_path = None

# --- Elementos de UI ---

# Indicador de estado del servidor
status_dot = ft.Container(width=8, height=8, bgcolor=COLOR_RED, border_radius=4)
status_text = ft.Text("Desconectado", size=11, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD)
status_badge = ft.Row(
controls=[status_dot, status_text],
alignment=ft.MainAxisAlignment.END,
spacing=6
)

# Contenedor de la previsualización de imagen (visor de la cámara)
camera_v
<truncated 12375 bytes>
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
ft.app(target=main)

The above content shows the entire, complete file contents of the requested file.