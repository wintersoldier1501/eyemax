The following changes were made by the USER to: c:\Users\Accesorizate1\Downloads\Eyemax\app_movil.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1,3 +1,6 @@
+import ssl
+ssl._create_default_https_context = ssl._create_unverified_context
+
 import flet as ft
 import httpx
 import os
@@ -5,7 +5,7 @@
 
 SERVER_URL = "http://127.0.0.1:5000"
 
-def main(page: ft.Page):
+async def main(page: ft.Page):
     # Configuración de ventana para simular una pantalla móvil
     page.title = "Eyemax - Scanner de Joyería"
     page.window_width = 390
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.