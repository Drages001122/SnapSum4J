import os
import tkinter as tk
from tkinter import filedialog
from typing import Callable

from src.gui_constant import (
    CAPTURE_BUTTON_PADX,
    CAPTURE_BUTTON_TEXT,
    CHOSEN_IMAGE_DESC,
    UPLOAD_BUTTON_PADX,
    UPLOAD_BUTTON_TEXT,
    UPLOAD_FRAME_PADY,
)


class UploadFrame(tk.Frame):
    def __init__(
        self,
        parent: tk.Frame,
        image_path_var: tk.StringVar,
        status_var: tk.StringVar,
        preview_and_select_region: Callable[[str], None],
        capture_screen_region: Callable[[], None],
    ):
        super().__init__(parent)
        self.pack(fill=tk.X, pady=UPLOAD_FRAME_PADY)
        self.image_path_var = image_path_var
        self.status_var = status_var
        self.preview_and_select_region = preview_and_select_region
        self.capture_screen_region = capture_screen_region

    def create_button(self):
        upload_button = tk.Button(
            self, text=UPLOAD_BUTTON_TEXT, command=self.upload_image
        )
        upload_button.pack(side=tk.LEFT, padx=UPLOAD_BUTTON_PADX)
        capture_button = tk.Button(
            self, text=CAPTURE_BUTTON_TEXT, command=self.capture_screen_region
        )
        capture_button.pack(side=tk.LEFT, padx=CAPTURE_BUTTON_PADX)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("所有文件", "*.*"),
            ]
        )
        if file_path:
            self.image_path_var.set(file_path)
            self.status_var.set(f"{CHOSEN_IMAGE_DESC} {os.path.basename(file_path)}")
            self.preview_and_select_region(file_path)
