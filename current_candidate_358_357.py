Created At: 2026-05-26T16:32:29Z
Completed At: 2026-05-26T16:32:33Z
The search for "flet "Unknown control: filepicker"" returned the following summary:
The error **"Unknown control: FilePicker"** in recent versions of Flet (starting from v0.84.0) occurs because the `FilePicker` control has been redesigned[1][2].

In older versions, `FilePicker` was treated as an overlay control and added to `page.overlay`[3][1]. In newer versions, it has been changed to a **Service** and should no longer be added to `page.overlay`[1][2].

### How to Fix
To resolve this, update your code to use the new service-based approach[1]:

1.  **Do not add it to `page.overlay`**: Removing this line is usually sufficient to stop the "Unknown control" error[1].
2.  **Use it as a service**: The `FilePicker` methods are now asynchronous and return results directly, meaning it no longer uses the `on_result` event handler[1].

#### Example of the Updated Approach
Instead of adding the control to the page, you can now invoke it directly and await the result[1]:

```python
import flet as ft

async def main(page: ft.Page):
    # Initialize the FilePicker
    file_picker = ft.FilePicker()
    
    # Define a function to trigger the picker
    async def pick_files_result(e):
        # Await the result directly
        result = await file_picker.pick_files_async()
        if result and result.files:
            print(f"Selected: {result.files[0].name}")

    # Add a button to trigger it
    page.add(ft.ElevatedButton("Pick files", on_click=pick_files_result))

ft.app(target=main)
```

*Note: If you are using an older version of Flet, this error may also appear if you have not upgraded your Flet library or if your project cache is stale[3][4]. If you have recently upgraded, ensure you are following the patterns in the latest [Flet documentation](https://flet.dev/docs/services/filepicker)[1].*

Sources:
[1] [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhOjwKnQmFwm-QMVtdb2NA3IXfD98pc6KJe1ZrIGf3cXNIFRLd7-u-GjipUHinRwDvbe1DuNHBDDODGxBvrd2WFRXaQzCIHSAqG3M2--oCXL0m6q-L30GLJLMJbZUC7tpkqMOrduDa)
[2] [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG20cQEN02XBY64pxu0NV6xcIc8480R0KcG4egQPoTtfWorAQ4Yw_Q_i_6Hm6rIGGIsPrjHekNMCMFAxi-LzbmR7I_PfhQMG_Q6NljsyxI0KGofiXid9bOjBzQ_YFbh4GRnhD8vWPuR88ijyy8VM2Og-v3Y5k0J0RU=)
[3] [flet.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-o_m9lgLy7YURAqYf-hq_9rGl2md7mkdPlEftajwy4RYDsZ0plVxYrq9qNTwpIezGk0P8sL1-bbwaP4CMONlLWrMGHSOk4uvBEtzu5bTj0Q9o9g4D1RF14bcbFEEsErRjuUc8QISNHnA=)
[4] [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTGIQjXDOUypcBj7D5twy8sIXNpjBHNJAwFY4LW03xoxYro4RzBGeRdDUpHrKOXPs_VwvRnXkBwPhsuA7DcmOWCeqCYTvMCx3y-ij6Q0d42Gl7WgxkdcP2P5s7VMeG0HAmk89vRWMw)