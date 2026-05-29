Created At: 2026-05-26T16:21:01Z
Completed At: 2026-05-26T16:21:01Z
File Path: `file:///c:/Users/Accesorizate1/Downloads/Eyemax/app_movil.py`
Total Lines: 364
Total Bytes: 14186
Showing lines 1 to 364
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import flet as ft
2: import httpx
3: import os
4: import threading
5: import time
6: 
7: SERVER_URL = "http://127.0.0.1:5000"
8: 
9: def main(page: ft.Page):
10:     # Configuración de ventana para simular una pantalla móvil
11:     page.title = "Eyemax - Scanner de Joyería"
12:     page.window_width = 390
13:     page.window_height = 800
14:     page.window_resizable = False
15:     page.padding = 0
16:     page.bgcolor = "#0F0F1A"
17:     
18:     # Paleta de colores Premium
19:     COLOR_BG_GRADIENT_START = "#14142B"
20:     COLOR_BG_GRADIENT_END = "#0B0B14"
21:     COLOR_GOLD = "#D4AF37"
22:     COLOR_GOLD_LIGHT = "#F3E5AB"
23:     COLOR_DARK_CARD = "#1D1D35"
24:     COLOR_BORDER = "#2E2E54"
25:     COLOR_TEXT_PRIMARY = "#FFFFFF"
26:     COLOR_TEXT_SECONDARY = "#A0A0C0"
27:     COLOR_GREEN = "#00E676"
28:     COLOR_RED = "#FF1744"
29: 
30:     # Variable para almacenar la ruta de la imagen seleccionada
31:     selected_image_path = None
32: 
33:     # --- Elementos de UI ---
34:     
35:     # Indicador de estado del servidor
36:     status_dot = ft.Container(width=8, height=8, bgcolor=COLOR_RED, border_radius=4)
37:     status_text = ft.Text("Desconectado", size=11, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD)
38:     status_badge = ft.Row(
39:         controls=[status_dot, status_text],
40:         alignment=ft.MainAxisAlignment.END,
41:         spacing=6
42:     )
43: 
44:     # Contenedor de la previsualización de imagen (visor de la cámara)
45:     camera_view_content = ft.Column(
46:         controls=[
47:             ft.Icon(ft.icons.CAMERA_ALT, size
<truncated 12328 bytes>
        icon=ft.icons.CAMERA_ALT,
327:                                         icon_size=36,
328:                                         icon_color="#000000",
329:                                         on_click=lambda _: file_picker.pick_files(
330:                                             allow_multiple=False,
331:                                             file_type=ft.FilePickerFileType.IMAGE,
332:                                             dialog_title="Capturar foto de joyería (simulado)"
333:                                         )
334:                                     ),
335:                                     width=76,
336:                                     height=76,
337:                                     bgcolor=COLOR_GOLD,
338:                                     border_radius=38,
339:                                     alignment=ft.alignment.center,
340:                                     shadow=ft.BoxShadow(
341:                                         spread_radius=1,
342:                                         blur_radius=15,
343:                                         color="#D4AF3740",
344:                                         offset=ft.Offset(0, 5)
345:                                     )
346:                                 ),
347:                                 ft.Text("ESCANEAR PIEZA", size=10, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.BOLD, letter_spacing=1.2)
348:                             ],
349:                             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
350:                             spacing=6
351:                         )
352:                     ],
353:                     alignment=ft.MainAxisAlignment.CENTER
354:                 )
355:             ],
356:             alignment=ft.MainAxisAlignment.SPACE_BETWEEN
357:         )
358:     )
359: 
360:     page.add(app_layout)
361: 
362: if __name__ == '__main__':
363:     ft.app(target=main)
364: 
The above content shows the entire, complete file contents of the requested file.
