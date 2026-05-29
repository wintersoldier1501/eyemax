Created At: 2026-05-26T21:36:47Z
Completed At: 2026-05-26T21:36:48Z
File Path: `file:///c:/Users/Accesorizate1/Downloads/Eyemax/app_movil.py`
Total Lines: 375
Total Bytes: 14677
Showing lines 1 to 150
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import flet as ft
import httpx
import os
import asyncio
import io

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

# --- Elementos de UI ---

# Indicador de estado del servidor
status_dot = ft.Container(width=8, height=8, bgcolor=COLOR_RED, border_radius=4)
status_text = ft.Text("Desconectado", size=11, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD)
status_badge = ft.Row(
controls=[status_dot, status_text],
alignment=ft.MainAxisAlignment.END,
spacing=6
)

# Visor de la cámara placeholder
camera_view_content = ft.Column(
controls=[
ft.Icon(ft.Icons.CAMERA_ALT, size=52, color=COLOR_GOLD),
ft.Text(
4
<truncated 2579 bytes>
=10, vertical=4),
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
bgcolor="#1C1C3A",
border_radius=20,
padding=20,
border=ft.Border.all(1.5, COLOR_GOLD),
visible=False,
animate=ft.Animation(400, ft.AnimationCurve.DECELERATE)
)

# --- Lógica de Negocio ---

async def check_server_status():
"""Verifica el estado del servidor de manera asíncrona y segura."""
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.