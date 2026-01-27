import multiprocessing
import os
import time
import tkinter as tk
from multiprocessing.pool import Pool
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from PIL import Image

from src.capture_window import CaptureScreen
from src.gui_constant import (
    APP_TITLE,
    CAPTURE_BUTTON_PADX,
    CAPTURE_BUTTON_TEXT,
    CHOSEN_IMAGE_DESC,
    DIGITS_DESC,
    DIGITS_DESC_PADY,
    DIGITS_PADY,
    DIGITS_TEXT_FONT,
    DIGITS_TEXT_HEIGHT,
    DIGITS_TEXT_PADX,
    DIGITS_TEXT_WIDTH,
    HEAD,
    HEADER_FONT,
    MAIN_FROM_PADX,
    MAIN_FROM_PADY,
    STATUS_LABEL_FONT,
    STATUS_LABEL_PADY,
    SUM_LABEL_FONT,
    SUM_LABEL_PADX,
    SUM_LABEL_PADY,
    SUM_LABEL_TEXT,
    SUM_PADY,
    SUM_RESULT_ENTRY_PADX,
    SUM_RESULT_FONT,
    SUM_RESULT_WIDTH,
    TITLE_LABEL_PADY,
    TOPMOST_PADY,
    UPLOAD_BUTTON_PADX,
    UPLOAD_BUTTON_TEXT,
    UPLOAD_FRAME_PADY,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.preview_window import PreviewWindow
from src.topmost import TopmostButton
from src.utils import calculate_scaled_size

# 全局变量，用于存储OCR实例（在子进程中初始化）
global_ocr = None


# 进程池初始化函数，确保每个子进程只加载一次模型
def init_worker():
    global global_ocr
    if global_ocr is None:
        from paddleocr import PaddleOCR

        from .utils import get_resource_path

        # 初始化 PaddleOCR 实例
        global_ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            text_detection_model_dir=get_resource_path("models/PP-OCRv5_server_det"),
            text_recognition_model_dir=get_resource_path("models/PP-OCRv5_server_rec"),
        )


# 定义识别函数，用于在子进程中执行
def recognition_process(image_path):
    try:
        # 记录开始时间
        start_time = time.time()

        # 使用全局OCR实例
        global global_ocr
        if global_ocr is None:
            init_worker()

        # 识别图片
        result = global_ocr.predict(input=image_path)
        # 提取数字
        all_numbers = []
        if result:
            rec_texts = []
            # 遍历result中的每个OCRResult对象
            for res in result:
                try:
                    # 检查res对象是否有rec_texts属性
                    if hasattr(res, "rec_texts"):
                        rec_texts.extend(res.rec_texts)
                    # 或者检查是否可以通过字典方式访问
                    elif isinstance(res, dict) and "rec_texts" in res:
                        rec_texts.extend(res["rec_texts"])
                except Exception as e:
                    print(f"Error accessing rec_texts: {e}")

            # 过滤出数字（支持小数）
            for text in rec_texts:
                if text.replace(".", "", 1).isdigit():
                    all_numbers.append(text)
        # 计算总和
        total_sum = sum(float(num) for num in all_numbers)

        # 计算识别耗时
        elapsed_time = time.time() - start_time

        # 构造识别结果
        result = {
            "success": True,
            "numbers": all_numbers,
            "total": total_sum,
            "elapsed_time": elapsed_time,
        }
    except Exception as e:
        result = {"success": False, "error": str(e)}

    return result


class DigitRecognitionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.init_window()
        self.init_attributes()
        self.init_layout()

        self.process_pool: Pool = multiprocessing.Pool(
            processes=1, initializer=init_worker
        )

    def init_window(self):
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(True, True)

    def init_attributes(self):
        self.image_path_var = tk.StringVar()
        self.sum_result_var = tk.StringVar()
        self.topmost_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar()
        self.photo = None

    def init_layout(self):
        self.main_frame = tk.Frame(self.root, padx=MAIN_FROM_PADX, pady=MAIN_FROM_PADY)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.init_title()
        self.init_upload()
        self.init_digits()
        self.init_sum()
        self.init_topmost()
        self.init_status()

    def init_title(self):
        title_label = tk.Label(self.main_frame, text=HEAD, font=HEADER_FONT)
        title_label.pack(pady=TITLE_LABEL_PADY)

    def init_upload(self):
        upload_frame = tk.Frame(self.main_frame)
        upload_frame.pack(fill=tk.X, pady=UPLOAD_FRAME_PADY)
        upload_button = tk.Button(
            upload_frame, text=UPLOAD_BUTTON_TEXT, command=self.upload_image
        )
        upload_button.pack(side=tk.LEFT, padx=UPLOAD_BUTTON_PADX)
        capture_button = tk.Button(
            upload_frame, text=CAPTURE_BUTTON_TEXT, command=self.capture_screen_region
        )
        capture_button.pack(side=tk.LEFT, padx=CAPTURE_BUTTON_PADX)

    def init_digits(self):
        digit_frame = tk.Frame(self.main_frame)
        digit_frame.pack(fill=tk.BOTH, expand=True, pady=DIGITS_PADY)
        desc_label = tk.Label(digit_frame, text=DIGITS_DESC)
        desc_label.pack(anchor=tk.W, pady=DIGITS_DESC_PADY)
        self.digits_text = ScrolledText(
            digit_frame,
            height=DIGITS_TEXT_HEIGHT,
            width=DIGITS_TEXT_WIDTH,
            font=DIGITS_TEXT_FONT,
        )
        self.digits_text.pack(fill=tk.BOTH, expand=True, padx=DIGITS_TEXT_PADX)
        self.digits_text.bind("<KeyRelease>", self.on_digits_modified)

    def init_sum(self):
        sum_frame = tk.Frame(self.main_frame)
        sum_frame.pack(fill=tk.X, pady=SUM_PADY)
        sum_label = tk.Label(sum_frame, text=SUM_LABEL_TEXT, font=SUM_LABEL_FONT)
        sum_label.pack(side=tk.LEFT, padx=SUM_LABEL_PADX, pady=SUM_LABEL_PADY)
        sum_result_entry = tk.Entry(
            sum_frame,
            textvariable=self.sum_result_var,
            width=SUM_RESULT_WIDTH,
            font=SUM_RESULT_FONT,
            state="readonly",
        )
        sum_result_entry.pack(
            side=tk.LEFT, padx=SUM_RESULT_ENTRY_PADX, fill=tk.X, expand=True
        )

    def init_topmost(self):
        topmost_button = TopmostButton(
            self.root,
            self.main_frame,
            self.topmost_var,
            self.status_var,
        )
        topmost_button.pack(anchor=tk.W, pady=TOPMOST_PADY)

    def init_status(self):
        self.status_label = tk.Label(
            self.main_frame,
            textvariable=self.status_var,
            fg="blue",
            font=STATUS_LABEL_FONT,
        )
        self.status_label.pack(anchor=tk.W, pady=STATUS_LABEL_PADY)

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

    def preview_and_select_region(self, image_path: str):
        image = Image.open(image_path)
        scaled_size = calculate_scaled_size(image)
        preview_window = PreviewWindow(
            self.root,
            self.image_path_var,
            self.recognize_digits,
        )
        preview_window.add_image(image, scaled_size)

    def recognize_digits(self):
        """识别图片中的数字"""
        image_path = self.image_path_var.get()
        if not image_path:
            messagebox.showerror("错误", "请先选择一张图片")
            return

        if not os.path.exists(image_path):
            messagebox.showerror("错误", "选择的图片文件不存在")
            return

        # 识别过程中用红字显示正在识别
        self.status_label.config(fg="red")
        self.status_var.set("正在识别数字...")

        # 定义回调函数处理结果
        def handle_result(result):
            # 更新UI
            self.update_ui_after_recognition(result)

        # 使用进程池提交任务
        self.process_pool.apply_async(
            recognition_process, (image_path,), callback=handle_result
        )

    def update_ui_after_recognition(self, result):
        """识别完成后更新UI"""
        if result["success"]:
            # 清空文本框和上一次的求和结果
            self.digits_text.delete(1.0, tk.END)
            self.sum_result_var.set("")
            for number in result["numbers"]:
                self.digits_text.insert(tk.END, f"{number}\n")

            # 自动计算并显示总和
            self.sum_result_var.set(str(result["total"]))

            # 识别结束后用蓝字显示求和结果以及识别耗时
            self.status_label.config(fg="blue")
            # 显示识别耗时和总和，移除弹窗和数字数量
            self.status_var.set(
                f"识别完成，耗时: {result['elapsed_time']:.2f} 秒，总和: {result['total']}"
            )
        else:
            # 识别失败时用红字显示错误信息
            self.status_label.config(fg="red")
            self.status_var.set(f"识别失败: {result['error']}")

        # 识别完成后删除临时文件
        temp_file = self.image_path_var.get()
        if temp_file and (
            "selected_region_temp.png" in temp_file
            or "captured_screen_region.png" in temp_file
        ):
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"删除临时文件失败: {str(e)}")

    def calculate_sum(self):
        """计算文本框中所有数字的总和"""
        try:
            # 获取文本框内容
            text_content = self.digits_text.get(1.0, tk.END)
            lines = text_content.strip().split("\n")

            # 提取所有数字（支持小数）
            numbers = []
            for line in lines:
                line = line.strip()
                if line:
                    # 尝试将每行转换为数字
                    try:
                        number = float(line)
                        numbers.append(number)
                    except ValueError:
                        # 跳过非数字行
                        pass

            # 计算总和
            total_sum = sum(numbers)
            self.sum_result_var.set(str(total_sum))

            # 计算完成后用蓝字显示结果
            self.status_label.config(fg="blue")
            self.status_var.set("计算完成")
        except Exception as e:
            # 计算失败时用红字显示错误信息
            self.status_label.config(fg="red")
            self.status_var.set(f"计算失败: {str(e)}")

    def on_digits_modified(self, event: tk.Event):
        """当用户修改数字时自动更新总和"""
        # 调用 calculate_sum 方法更新总和
        self.calculate_sum()

    def capture_screen_region(self):
        self.root.iconify()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        capture_window = CaptureScreen(
            self.root, self.image_path_var, self.status_var, self.recognize_digits
        )

        canvas = capture_window.create_canvas(screen_width, screen_height)
        capture_window.handle_select_region_events(canvas)
