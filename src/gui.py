import multiprocessing
import os
import time
import tkinter as tk
from multiprocessing.pool import Pool
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from typing import Optional

import pyautogui
from PIL import Image, ImageTk

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
    PREVIEW_WINDOW_RELAX_HEIGHT,
    PREVIEW_WINDOW_TITLE,
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
    TOPMOST_TEXT,
    UPLOAD_BUTTON_PADX,
    UPLOAD_BUTTON_TEXT,
    UPLOAD_FRAME_PADY,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
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
        self.photo: Optional[ImageTk.PhotoImage] = None

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
        topmost_button = tk.Checkbutton(
            self.main_frame,
            text=TOPMOST_TEXT,
            variable=self.topmost_var,
            command=self.toggle_topmost,
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

    def enable_root(self, enabled: bool):
        self.root.attributes(  # pyright: ignore[reportUnknownMemberType]
            "-disabled", not enabled
        )

    def create_preview_window(self, scaled_size: tuple[int, int]):
        preview_window = tk.Toplevel(self.root)
        preview_window.title(PREVIEW_WINDOW_TITLE)
        preview_window.geometry(
            f"{scaled_size[0]}x{scaled_size[1] + PREVIEW_WINDOW_RELAX_HEIGHT}"
        )
        preview_window.resizable(True, True)

        def on_window_close():
            preview_window.destroy()
            self.enable_root(True)

        preview_window.protocol("WM_DELETE_WINDOW", on_window_close)
        return preview_window

    def create_canvas(
        self,
        preview_window: tk.Toplevel,
        scaled_size: tuple[int, int],
    ):
        canvas = tk.Canvas(preview_window, width=scaled_size[0], height=scaled_size[1])
        canvas.pack()
        assert (
            self.photo is not None
        ), "self.photo must be initialized before calling create_canvas"
        canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)  # type: ignore[reportUnknownMemberType]
        return canvas

    def preview_and_select_region(self, image_path: str):
        try:
            image = Image.open(image_path)
            scaled_size = calculate_scaled_size(image)
            self.photo = ImageTk.PhotoImage(image.resize(scaled_size))
            self.enable_root(False)
            preview_window = self.create_preview_window(scaled_size)
            canvas = self.create_canvas(preview_window, scaled_size)

            # 选择区域的变量
            start_x = None
            start_y = None
            rect = None
            selected_region = None  # 存储最终选择的区域

            # 鼠标按下事件
            def on_mouse_down(event):
                nonlocal start_x, start_y, rect
                start_x = canvas.canvasx(event.x)
                start_y = canvas.canvasy(event.y)
                # 创建矩形
                if rect:
                    canvas.delete(rect)
                rect = canvas.create_rectangle(
                    start_x,
                    start_y,
                    start_x,
                    start_y,
                    outline="red",
                    width=2,
                )

            # 鼠标移动事件
            def on_mouse_move(event):
                nonlocal start_x, start_y, rect
                if start_x is not None and start_y is not None:
                    current_x = canvas.canvasx(event.x)
                    current_y = canvas.canvasy(event.y)
                    # 更新矩形
                    canvas.coords(
                        rect, start_x, start_y, current_x, current_y
                    )

            # 鼠标释放事件
            def on_mouse_up(event):
                nonlocal selected_region, start_x, start_y
                if start_x is not None and start_y is not None:
                    end_x = canvas.canvasx(event.x)
                    end_y = canvas.canvasy(event.y)

                    # 确保坐标顺序正确
                    x1 = min(start_x, end_x)
                    y1 = min(start_y, end_y)
                    x2 = max(start_x, end_x)
                    y2 = max(start_y, end_y)

                    # 检查选择区域是否有效
                    if x2 - x1 > 10 and y2 - y1 > 10:
                        # 存储选中的区域
                        selected_region = (x1, y1, x2, y2)
                    else:
                        selected_region = None
                        messagebox.showinfo("提示", "请选择一个更大的区域")

                    # 重置变量
                    start_x = None
                    start_y = None

            # 确认按钮回调函数
            def on_confirm():
                nonlocal selected_region
                if selected_region:
                    # 将放大后的画布坐标转换回原始图片坐标
                    original_x1 = int(selected_region[0] / scale_factor)
                    original_y1 = int(selected_region[1] / scale_factor)
                    original_x2 = int(selected_region[2] / scale_factor)
                    original_y2 = int(selected_region[3] / scale_factor)

                    # 裁剪选中区域
                    cropped_image = Image.open(image_path).crop(
                        (original_x1, original_y1, original_x2, original_y2)
                    )

                    # 保存为临时文件到根目录
                    temp_file = os.path.join(
                        os.path.abspath("."), "selected_region_temp.png"
                    )
                    cropped_image.save(temp_file)

                    # 更新图片路径为选中的区域
                    self.image_path_var.set(temp_file)

                    # 关闭预览窗口
                    preview_window.destroy()

                    # 重新启用主窗口
                    self.root.attributes("-disabled", False)

                    # 开始识别
                    self.recognize_digits()
                else:
                    messagebox.showinfo("提示", "请先选择一个区域")

            # 绑定鼠标事件
            canvas.bind("<Button-1>", on_mouse_down)
            canvas.bind("<B1-Motion>", on_mouse_move)
            canvas.bind("<ButtonRelease-1>", on_mouse_up)

            # 创建按钮框架
            button_frame = tk.Frame(preview_window)
            button_frame.pack(pady=20)

            # 添加确认按钮
            confirm_button = tk.Button(
                button_frame,
                text="确认选择",
                command=on_confirm,
                font=("微软雅黑", 12),
                width=15,
            )
            confirm_button.pack(pady=10)

            # 添加提示标签
            hint_label = tk.Label(
                preview_window,
                text="提示: 按住鼠标左键拖拽选择要识别的区域，可反复选择直到点击确认",
            )
            hint_label.pack(pady=10)

        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            preview_window.destroy()
            # 重新启用主窗口
            self.root.attributes("-disabled", False)

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

    def toggle_topmost(self):
        """切换窗口置顶状态"""
        is_topmost = self.topmost_var.get()
        self.root.attributes("-topmost", is_topmost)
        # 更新状态标签显示置顶状态
        if is_topmost:
            self.status_var.set("窗口已置顶")
        else:
            self.status_var.set("窗口已取消置顶")

    def capture_screen_region(self):
        """截取屏幕区域"""
        # 最小化主窗口
        self.root.iconify()

        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 创建全屏覆盖窗口
        capture_window = tk.Toplevel(self.root)
        capture_window.attributes("-fullscreen", True)
        capture_window.attributes("-alpha", 0.3)  # 设置透明度
        capture_window.attributes("-topmost", True)
        capture_window.config(cursor="cross")

        # 创建画布
        canvas = tk.Canvas(capture_window, width=screen_width, height=screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)

        # 选择区域的变量
        start_x = None
        start_y = None
        rect = None

        # 鼠标按下事件
        def on_mouse_down(event):
            nonlocal start_x, start_y, rect
            start_x = event.x_root
            start_y = event.y_root
            # 创建矩形
            if rect:
                canvas.delete(rect)
            rect = canvas.create_rectangle(
                start_x, start_y, start_x, start_y, outline="red", width=2
            )

        # 鼠标移动事件
        def on_mouse_move(event):
            nonlocal rect
            if start_x is not None and start_y is not None:
                current_x = event.x_root
                current_y = event.y_root
                # 更新矩形
                canvas.coords(rect, start_x, start_y, current_x, current_y)

        # 鼠标释放事件
        def on_mouse_up(event):
            nonlocal start_x, start_y
            if start_x is not None and start_y is not None:
                end_x = event.x_root
                end_y = event.y_root

                # 确保坐标顺序正确
                x1 = min(start_x, end_x)
                y1 = min(start_y, end_y)
                x2 = max(start_x, end_x)
                y2 = max(start_y, end_y)

                # 检查选择区域是否有效
                if x2 - x1 > 10 and y2 - y1 > 10:
                    # 关闭捕获窗口
                    capture_window.destroy()
                    # 截取屏幕区域
                    self.capture_selected_region(x1, y1, x2, y2)
                else:
                    # 关闭捕获窗口
                    capture_window.destroy()
                    # 恢复主窗口
                    self.root.deiconify()
                    messagebox.showinfo("提示", "请选择一个更大的区域")

                # 重置变量
                start_x = None
                start_y = None

        # 绑定鼠标事件
        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        # 点击鼠标右键取消
        def on_right_click(event):
            # 延迟3秒后取消截图
            def cancel_after_delay():
                capture_window.destroy()
                # 恢复主窗口
                self.root.deiconify()

            capture_window.after(100, cancel_after_delay)

        canvas.bind("<Button-3>", on_right_click)

    def capture_selected_region(self, x1, y1, x2, y2):
        """根据坐标截取屏幕区域"""
        try:
            # 截取屏幕区域
            screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

            # 保存为临时文件
            temp_file = os.path.join(os.path.abspath("."), "captured_screen_region.png")
            screenshot.save(temp_file)

            # 恢复主窗口
            self.root.deiconify()

            # 更新图片路径
            self.image_path_var.set(temp_file)
            self.status_var.set(
                f"已截取屏幕区域，保存为: {os.path.basename(temp_file)}"
            )

            # 开始识别
            self.recognize_digits()
        except Exception as e:
            messagebox.showerror("错误", f"截取屏幕失败: {str(e)}")
            self.status_var.set(f"截取屏幕失败: {str(e)}")
