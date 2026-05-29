Created At: 2026-05-26T16:24:06Z
Completed At: 2026-05-26T16:24:09Z
The search for ""flet" "FilePicker" "on_result"" returned the following summary:
In recent versions of Flet (starting from v0.84.0), the `FilePicker` control has been updated to function as a **service** rather than an overlay control[1].

### Key Changes
*   **No `on_result`:** The `on_result` event handler has been removed[1].
*   **Async Methods:** The picker methods (such as `pick_files`, `save_file`, and `get_directory_path`) are now **asynchronous** and return the result directly[1].
*   **Not an Overlay:** You no longer need to add `FilePicker` to `page.overlay`[1].

### How to use it (Current Approach)
Instead of defining a callback function for `on_result`, you now `await` the method call directly in your code[1].

```python
import flet as ft

async def main(page: ft.Page):
    # Initialize the FilePicker service
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker) # Still good practice to keep it available if needed, or simply instantiate
    
    async def pick_files_click(e):
        # Await the result directly
        result = await file_picker.pick_files_async(allow_multiple=True)
        
        if result and result.files:
            for f in result.files:
                print(f"Selected file: {f.name}, Path: {f.path}")
        else:
            print("Dialog cancelled")

    page.add(
        ft.ElevatedButton("Pick Files", on_click=pick_files_click)
    )

ft.app(target=main)
```

### Important Notes
*   **Legacy Code:** If you are following older tutorials or documentation, they will reference `on_result` and `page.overlay`[2][3][4]. These methods will cause errors in newer versions of Flet[1].
*   **Async/Await:** Because the new methods are asynchronous, ensure your event handlers (like `on_click` callbacks) are defined as `async def` and use the `await` keyword[1].

Sources:
[1] [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjJwWCKwRKbVEdnT34azdRDfgBNjPScYOaUA5ogyuXp9RyY0nFuYMvk1_lqX-2Q_OrsSB0KVl_jqqyLKlMt6OwJsGov5xZJjouZiU0RK7PgPfX07GcPQe5GcyIj5Pe4V5d1q4MRgkr)
[2] [flet.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnNmgtsX3UJDHblPz941N4QDNE_rFUymOT-73Dfpa6h-80egd7OgNRioDDRg6On4-Y4rmh0G_TX2ypgc2Ed8mcR6lqz6zfmy8uOyuquCwKMcwUAlrH3o7t-nsTFdXVySIBpH7owPFkj3Q=)
[3] [gemfury.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyPbnvXTv2d8JRmGCeuvm-6QW3KY6Rr6cFYMdC6DZCdgGk50EP5giLT4cY75--Sw-D2037AI9nxaTwbXysrmka_hZXOqKyLIyETG8RYyUwogcNVrVwR8TrQ8s1Yi9MTwDwvqfhbPmfi4W8l_6z0ujbUIN86tItKsgHOlcinYLgmZTbNZhwyJj8PCLNLQ--whNRDQNwpfPAaE9MH6BYJ_w9ZEwWZuv9Rx5w)
[4] [stackoverflow.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtIkdAwtsKD3mkW5aWrAyf9p1bs5fK6WBfSTgTxYC2eMt38n4CkrKBQse8OmhLX-iDwr9N_0LUM1LojybtX_yXwVK6QLsekWVGGn2LsZHgvVXS5VckSa57tXtxR2zZK26hFQTLaKM_rqRJdePU7GgMyoVHnSH86_bCiy_fnE_nBb1nm2adJkmbOzj_5Nzb4wk25nLBugqoYS73NIrRK21qhD4q)