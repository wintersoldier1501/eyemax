Created At: 2026-05-26T21:43:23Z
Completed At: 2026-05-26T21:43:23Z
File Path: `file:///c:/Users/Accesorizate1/Downloads/Eyemax/original_app_movil.py`
Total Lines: 104
Total Bytes: 4223
Showing lines 1 to 104
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
Created At: 2026-05-26T21:36:47Z
Completed At: 2026-05-26T21:36:48Z
File Path: `file:///c:/Users/Accesorizate1/Downloads/Eyemax/app_movil.py`
Total Lines: 375
Total Bytes: 14677
Showing lines 1 to 150
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import ssl
2: ssl._create_default_https_context = ssl._create_unverified_context
3: 
4: import flet as ft
5: import httpx
6: import os
7: import asyncio
8: import io
9: 
10: SERVER_URL = "http://127.0.0.1:5000"
11: 
12: async def main(page: ft.Page):
13:     # Configuración de ventana para simular una pantalla móvil
14:     page.title = "Eyemax - Scanner de Joyería"
15:     page.window_width = 390
16:     page.window_height = 800
17:     page.window_resizable = False
18:     page.padding = 0
19:     page.bgcolor = "#0F0F1A"
20:     
21:     # Paleta de colores Premium
22:     COLOR_BG_GRADIENT_START = "#14142B"
23:     COLOR_BG_GRADIENT_END = "#0B0B14"
24:     COLOR_GOLD = "#D4AF37"
25:     COLOR_GOLD_LIGHT = "#F3E5AB"
26:     COLOR_DARK_CARD = "#1D1D35"
27:     COLOR_BORDER = "#2E2E54"
28:     COLOR_TEXT_PRIMARY = "#FFFFFF"
29:     COLOR_TEXT_SECONDARY = "#A0A0C0"
30:     COLOR_GREEN = "#00E676"
31:     COLOR_RED = "#FF1744"
32: 
33:     # ---
<truncated 1073 bytes>
               ft.Row(
115:                     controls=[
116:                         ft.Text("PRODUCTO DETECTADO", size=12, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=1.5)),
117:                         res_badge
118:                     ],
119:                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN
120:                 ),
121:                 ft.Divider(color=COLOR_BORDER, height=15),
122:                 ft.Row(
123:                     controls=[res_code, res_price],
124:                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
125:                     vertical_alignment=ft.CrossAxisAlignment.CENTER
126:                 ),
127:                 ft.Container(height=6),
128:                 res_desc,
129:                 ft.Divider(color=COLOR_BORDER, height=15),
130:                 ft.Row(
131:                     controls=[res_mode],
132:                     alignment=ft.MainAxisAlignment.CENTER
133:                 )
134:             ],
135:             spacing=8,
136:             horizontal_alignment=ft.CrossAxisAlignment.CENTER
137:         ),
138:         width=330,
139:         bgcolor="#1C1C3A",
140:         border_radius=20,
141:         padding=20,
142:         border=ft.Border.all(1.5, COLOR_GOLD),
143:         visible=False,
144:         animate=ft.Animation(400, ft.AnimationCurve.DECELERATE)
145:     )
146: 
147:     # --- Lógica de Negocio ---
148:     
149:     async def check_server_status():
150:         """Verifica el estado del servidor de manera asíncrona y segura."""
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

The above content shows the entire, complete file contents of the requested file.