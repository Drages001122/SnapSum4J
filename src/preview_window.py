import os
import tkinter as tk
from tkinter import messagebox
from typing import Callable

from PIL import Image

from src.constant import SCALE_FACTOR, TEMP_FILE_NAME
from src.gui_constant import (
    PREVIEW_CONFIRM_WARNING_MESSAGE,
    PREVIEW_CONFIRM_WARNING_TITLE,
    PREVIEW_OUTLINE_COLOR,
    PREVIEW_OUTLINE_WIDTH,
    PREVIEW_RECT_MIN_LENGTH,
    PREVIEW_WARNING_MESSAGE,
    PREVIEW_WARNING_TITLE,
    PREVIEW_WINDOW_RELAX_HEIGHT,
    PREVIEW_WINDOW_TITLE,
)


class PreviewWindow(tk.Toplevel):
    def __init__(
        self,
        root: tk.Tk,
        image_path_var: tk.StringVar,
        recognize_digits: Callable[[], None],
        scaled_size: tuple[int, int],
    ):
        super().__init__(root)
        self.root = root
        self.image_path_var = image_path_var
        self.recognize_digits = recognize_digits
        self.enable_root(False)
        self.create_preview_window(scaled_size)

    def enable_root(self, enabled: bool):
        self.root.attributes(  # pyright: ignore[reportUnknownMemberType]
            "-disabled", not enabled
        )

    def create_preview_window(self, scaled_size: tuple[int, int]):
        self.title(PREVIEW_WINDOW_TITLE)
        self.geometry(
            f"{scaled_size[0]}x{scaled_size[1] + PREVIEW_WINDOW_RELAX_HEIGHT}"
        )
        self.resizable(True, True)

        def on_window_close():
            self.destroy()
            self.enable_root(True)

        self.protocol("WM_DELETE_WINDOW", on_window_close)

    def handle_select_region_events(self, canvas: tk.Canvas, image: Image.Image):
        start_x = None
        start_y = None
        rect = None
        selected_region = None

        def on_mouse_down(event: tk.Event):
            nonlocal start_x, start_y, rect
            start_x = int(canvas.canvasx(event.x))  # type: ignore[reportUnknownMemberType]
            start_y = int(canvas.canvasy(event.y))  # type: ignore[reportUnknownMemberType]
            if rect:
                canvas.delete(rect)
            rect = canvas.create_rectangle(
                start_x,
                start_y,
                start_x,
                start_y,
                outline=PREVIEW_OUTLINE_COLOR,
                width=PREVIEW_OUTLINE_WIDTH,
            )

        def on_mouse_move(event: tk.Event):
            nonlocal start_x, start_y, rect
            if start_x is not None and start_y is not None:
                current_x = int(canvas.canvasx(event.x))  # type: ignore[reportUnknownMemberType]
                current_y = int(canvas.canvasy(event.y))  # type: ignore[reportUnknownMemberType]
                assert (
                    rect is not None
                ), "rect must be initialized before calling on_mouse_move"
                canvas.coords(rect, start_x, start_y, current_x, current_y)

        def on_mouse_up(event: tk.Event):
            nonlocal selected_region, start_x, start_y
            if start_x is not None and start_y is not None:
                end_x = int(canvas.canvasx(event.x))  # type: ignore[reportUnknownMemberType]
                end_y = int(canvas.canvasy(event.y))  # type: ignore[reportUnknownMemberType]
                assert (
                    rect is not None
                ), "rect must be initialized before calling on_mouse_up"
                canvas.coords(rect, start_x, start_y, end_x, end_y)

                x1 = min(start_x, end_x)
                y1 = min(start_y, end_y)
                x2 = max(start_x, end_x)
                y2 = max(start_y, end_y)

                if (
                    x2 - x1 > PREVIEW_RECT_MIN_LENGTH
                    and y2 - y1 > PREVIEW_RECT_MIN_LENGTH
                ):
                    selected_region = (x1, y1, x2, y2)
                else:
                    selected_region = None
                    messagebox.showinfo(
                        PREVIEW_WARNING_TITLE,
                        PREVIEW_WARNING_MESSAGE,
                    )

                start_x = None
                start_y = None

        def on_confirm():
            nonlocal selected_region
            if selected_region:
                original_x1 = int(selected_region[0] / SCALE_FACTOR)
                original_y1 = int(selected_region[1] / SCALE_FACTOR)
                original_x2 = int(selected_region[2] / SCALE_FACTOR)
                original_y2 = int(selected_region[3] / SCALE_FACTOR)
                cropped_image = image.crop(
                    (original_x1, original_y1, original_x2, original_y2)
                )
                temp_file = os.path.join(os.path.abspath("."), TEMP_FILE_NAME)
                cropped_image.save(temp_file)
                self.image_path_var.set(temp_file)
                self.destroy()
                self.enable_root(True)
                self.recognize_digits()
            else:
                messagebox.showinfo(
                    PREVIEW_CONFIRM_WARNING_TITLE,
                    PREVIEW_CONFIRM_WARNING_MESSAGE,
                )

        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        return on_confirm
