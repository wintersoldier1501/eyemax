Created At: 2026-05-26T16:33:05Z
Completed At: 2026-05-26T16:33:05Z
The following changes were made by the multi_replace_file_content tool to: c:\Users\Accesorizate1\Downloads\Eyemax\app_movil.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -9,7 +9,7 @@
 
 SERVER_URL = "http://127.0.0.1:5000"
 
-async def main(page: ft.Page):
+def main(page: ft.Page):
     # Configuración de ventana para simular una pantalla móvil
     page.title = "Eyemax - Scanner de Joyería"
     page.window_width = 390
@@ -165,21 +165,13 @@
     # Ejecutar chequeo en hilo secundario
     threading.Thread(target=check_server_status, daemon=True).start()
 
-    file_picker = ft.FilePicker()
-    page.overlay.append(file_picker)
-
     # Callback para procesar la imagen elegida por el FilePicker
-    async def on_scan_click(e):
-        result = await file_picker.pick_files(
-            allow_multiple=False,
-            file_type=ft.FilePickerFileType.IMAGE,
-            dialog_title="Capturar foto de joyería (simulado)"
-        )
-        if not result:
+    def on_file_selected(e: ft.FilePickerResultEvent):
+        nonlocal selected_image_path
+        if not e.files:
             return
             
-        nonlocal selected_image_path
-        selected_image_path = result[0].path
+        selected_image_path = e.files[0].path
         print(f"Imagen seleccionada localmente: {selected_image_path}")
         
         # Actualizar vista previa
@@ -196,6 +196,10 @@
         # Lanzar análisis del backend
         analyze_image()
 
+    file_picker = ft.FilePicker(on_result=on_file_selected)
+    page.overlay.append(file_picker)
+    page.update()  # Enviar el control FilePicker al cliente inmediatamente
+
     def analyze_image():
         nonlocal selected_image_path
         if not selected_image_path or not os.path.exists(selected_image_path):
@@ -331,7 +331,11 @@
                                         icon=ft.Icons.CAMERA_ALT,
                                         icon_size=36,
                                         icon_color="#000000",
-                                        on_click=on_scan_click
+                                        on_click=lambda _: file_picker.pick_files(
+                                            allow_multiple=False,
+                                            file_type=ft.FilePickerFileType.IMAGE,
+                                            dialog_title="Capturar foto de joyería (simulado)"
+                                        )
                                     ),
                                     width=76,
                                     height=76,
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.