Created At: 2026-05-26T21:31:45Z
Completed At: 2026-05-26T21:31:49Z
The search for "flet filepicker pick_files callback parameter" returned the following summary:
In modern versions of Flet, the `FilePicker` API has changed significantly. It no longer uses an `on_result` event callback[1]. Instead, the `pick_files()` method is now an **asynchronous method that returns the result directly**[1][2].

### How to use `pick_files()` (Current Approach)

Because `pick_files()` is now asynchronous, you should `await` it inside an `async` function to receive the selection result immediately[3][2].

```python
import flet as ft

async def main(page: ft.Page):
    # Create the FilePicker service
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    async def handle_pick_files(e):
        # Call pick_files and await the result directly
        result = await file_picker.pick_files_async(
            allow_multiple=True,
            dialog_title="Select files..."
        )
        
        # Process the result
        if result and result.files:
            for f in result.files:
                print(f"Selected file: {f.name}, Path: {f.path}")

    page.add(
        ft.ElevatedButton("Pick files", on_click=handle_pick_files)
    )

ft.app(target=main)
```

### Key Changes
*   **No `on_result` Callback:** You do not need to define an `on_result` handler or pass it to the `FilePicker` constructor anymore[1].
*   **Async/Await:** Use `await file_picker.pick_files_async(...)` to get the list of selected files directly[3][2].
*   **Result Object:** The returned object contains a `.files` property (a list of `FilePickerFile` objects) if files were selected, or `None` if the user cancelled the dialog[4][5].

### Parameters for `pick_files_async`
The `pick_files_async` method accepts the following parameters[3]:
*   **`dialog_title`** (str | None): The title of the dialog window.
*   **`initial_directory`** (str | None): The directory where the dialog should open.
*   **`file_type`**: Restrict selection (e.g., `ft.FilePickerFileType.IMAGE`).
*   **`allow_multiple`** (bool): If `True`, allows selecting multiple files.
*   **`with_data`** (bool): If `True`, reads file contents into memory (useful for web apps)[3].

Sources:
[1] [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI_TGlqklRtgjF4ThgnL7IlD4JLf1-Ag9o8_6Pdh5wdCkqxzZO84fXVgY3Q_9wuNQhnJUy1LmqRM0iMgOOauAng3x65NzO7EJyjG91wPAX8tT27cO66cf7HZOv5GYlL6ooARnB7FE=)
[2] [stackoverflow.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOTV38LNPGkCMccKXEZTlDCGXCrwp_qJShpDFvV7IjEyi_68NM61KazAJaOZ5L13Wrs_5U9uzcN4AoRyc23iXsHr7fwBVEm1Kv1Gx6JRMoSo2VkB2TIKGkdnskrl3eDtuQQ9FQVlbUFrW06VRSpaq0b-8mjSrHLIC0rJIz9TRnklwM_iUXKNsV)
[3] [flet.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZyQH4jp-DKldntZxK-hD8xebT8o53cFcH30ZPUSk1LwF9VjuBpSfFAygEB0cXQoVALY457w-hvcfq0iMEyupHPsvTFFtW6GANVo6zqZrB5SMKkvozaJjkBiMwF01ShtYzT9wS)
[4] [flet.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcVWKMYcdtBU-1-DUefTM2x0C6BMHnV1nIDc5O6DkpQYurfLPunwops_sj3IgOwxPjfpno94p9gCwPNpAWtSUlod_mIOkXStRf5F9IYFEVU0uvlunPEQiSqHpHAIyn-t8nGmh9k5aMjg==)
[5] [gemfury.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKXSvGm_fr4mlAs_C67s-1H8d57JZzTE2DJvxr431mh9uom4SEHznXvP5Iha52pVth3kqKPH-9qxa2nCYWBrt5P9TrLRTkS_JK6xBSrDg6HJNtCx7Q_jmZ9Cidl8XAdXmAofvDCGnKMlRmOQS-j-LraTUQYkT70qSHYNwJ_TYnE70ca5_nIn8BOvAFKNUzu45h8chG24_eKbLaur__KerRWd5lkRd5NdQ=)