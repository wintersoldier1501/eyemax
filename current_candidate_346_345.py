Created At: 2026-05-26T16:31:57Z
Completed At: 2026-05-26T16:32:00Z
The search for "flet async "FilePicker" example python" returned the following summary:
In Flet, the `FilePicker` control is used to open native OS dialogs for selecting files or directories[1]. When working in an `async` context, you can directly `await` the methods `pick_files()`, `save_file()`, and `get_directory_path()` to get the result without needing the older `on_result` callback[2][3].

### Async `FilePicker` Example

It is recommended to add the `FilePicker` to `page.overlay` so it does not interfere with your app's layout[1].

```python
import flet as ft

async def main(page: ft.Page):
    # 1. Define the handler to process the selected files
    async def handle_pick_files(e):
        # Open the file picker
        files = await file_picker.pick_files_async(allow_multiple=True)
        
        if files:
            result_text.value = f"Selected: {', '.join([f.name for f in files])}"
        else:
            result_text.value = "No files selected."
        
        await page.update_async()

    # 2. Create the FilePicker control
    file_picker = ft.FilePicker(on_result=None) # on_result is optional for async
    page.overlay.append(file_picker)
    
    result_text = ft.Text("No files selected.")
    pick_button = ft.ElevatedButton(
        "Pick files", 
        on_click=handle_pick_files
    )

    await page.add_async(pick_button, result_text)

ft.app(target=main)
```

### Key Points
*   **Async Methods**: You can use `await file_picker.pick_files_async(...)`, `await file_picker.save_file_async(...)`, or `await file_picker.get_directory_path_async(...)` directly in your async event handlers[2][3].
*   **No `on_result` Needed**: When using the `await` pattern, you do not need to rely on the `on_result` callback to retrieve the selected file data, as the method returns the result directly[2][4].
*   **Overlay**: Always append the `FilePicker` to `page.overlay`[1]. Even though it has no visual footprint (0x0 size), it must be part of the control tree to function correctly[1].
*   **Platform Differences**: On Desktop, `pick_files` returns the absolute path to the files[1]. On the Web, it handles file references for uploading purposes[1].

Sources:
[1] [flet.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGezbt5E24rQw8So0R36QjxqrCQ0WomtgYf0TrN84XGOwqNRoQHwXdjHyvgKbWrZ8LrvoDoE5If7Dsps26yg6BA0f99Igb3epCbXLaWErDUgbloqCp0oYWDVDwxSUOEJKa9rPKBysC9cIw=)
[2] [flet.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFewFjfoTGGJPTAvcjh3Yqe7dLbkEoYVQq_PsoIYwL72nLIxUFuRZxKxmSJ5EhxrdyrmWY3ThTyb90xTu7UF0CFf4R9tyRcGSjsTVfuMlzh3VzknLsbjzrNBDiZ2FwQpWg4GjatTw==)
[3] [gemfury.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRCtsO5_dulbKSETANquhSus8OLPCytl32nSbYqJFf_gDfXNQBrTuvOJ7Mm4khlIoqYs2wNfBjSapSKj-U8tRV8Q4URe9deKcldL3f7OZ8FyTVxJPzNMRbWEHKvnHu7pfT40OVH4sadBOucoaflMTp0kYKS1a7b2-L9D_ilqkQxEHoTueGyTzSJWCiYjVThPT6frBZqTjFRm8Ii5ucBi2CphQLpthN1xOr)
[4] [stackoverflow.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAhL314MsmpCMGgPsILQAltXnZjrGHfZ2jmTMz7aq2TNf5odUpdh7-Edz3PpB0dj6r9wNimSZUdJaxLYZVgrHxLnIFq9UI0xlRcEky0Ycopx_qtk0TyUvpyRsAbECDIXKnRt712LRof8ksywmq0OWYafjDuSZ5sUFg9v8xa873R6CdVJlwLOf6bw==)