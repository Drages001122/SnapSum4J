import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import time
import threading
import pyautogui
from PIL import Image, ImageTk
from .ocr import recognize_image

class DigitRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数字识别与求和工具")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        
        # 创建主框架
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(main_frame, text="数字识别与求和工具", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=10)
        
        # 图片上传区域
        upload_frame = tk.Frame(main_frame)
        upload_frame.pack(fill=tk.X, pady=10)
        
        self.image_path_var = tk.StringVar()
        
        upload_button = tk.Button(upload_frame, text="选择图片", command=self.upload_image)
        upload_button.pack(side=tk.LEFT, padx=5)
        
        # 添加屏幕截取按钮
        capture_button = tk.Button(upload_frame, text="截取屏幕区域", command=self.capture_screen_region)
        capture_button.pack(side=tk.LEFT, padx=5)
        
        # 数字显示区域
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        text_label = tk.Label(text_frame, text="识别到的数字（每行一个，可手动添加）:")
        text_label.pack(anchor=tk.W, pady=5)
        
        self.digits_text = ScrolledText(text_frame, height=10, width=60, font=("Courier New", 12))
        self.digits_text.pack(fill=tk.BOTH, expand=True, padx=5)
        # 绑定文本修改事件，实现自动更新总和
        self.digits_text.bind("<KeyRelease>", self.on_digits_modified)
        
        # 求和区域
        sum_frame = tk.Frame(main_frame)
        sum_frame.pack(fill=tk.X, pady=10)
        
        sum_label = tk.Label(sum_frame, text="总和:", font=("微软雅黑", 10, "bold"))
        sum_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.sum_result_var = tk.StringVar()
        self.sum_result_entry = tk.Entry(sum_frame, textvariable=self.sum_result_var, width=20, font=("Courier New", 12), state="readonly")
        self.sum_result_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 置顶按钮
        self.topmost_var = tk.BooleanVar(value=False)
        self.topmost_button = tk.Checkbutton(main_frame, text="窗口置顶", variable=self.topmost_var, command=self.toggle_topmost)
        self.topmost_button.pack(anchor=tk.W, pady=5)
        
        # 状态标签
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, fg="blue", font=("微软雅黑", 9))
        self.status_label.pack(anchor=tk.W, pady=5)
    
    def upload_image(self):
        """上传图片"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*")]
        )
        if file_path:
            self.image_path_var.set(file_path)
            self.status_var.set(f"已选择图片: {os.path.basename(file_path)}")
            # 显示图片预览并允许用户选择区域
            self.preview_and_select_region(file_path)
    
    def preview_and_select_region(self, image_path):
        """显示图片预览并允许用户选择区域"""
        # 加载图片
        try:
            image = Image.open(image_path)
            img_width, img_height = image.size
            
            # 放大倍数
            scale_factor = 3
            
            # 计算放大后的尺寸
            scaled_width = img_width * scale_factor
            scaled_height = img_height * scale_factor
            
            # 禁用主窗口
            self.root.attributes('-disabled', True)
            
            # 创建预览窗口，大小为图片的3倍
            preview_window = tk.Toplevel(self.root)
            preview_window.title("图片预览 - 请框选要识别的区域")
            # 为了容纳按钮，稍微增加窗口高度
            preview_window.geometry(f"{scaled_width}x{scaled_height + 100}")
            preview_window.resizable(True, True)
            
            # 放大图片
            scaled_image = image.resize((scaled_width, scaled_height))
            
            # 转换为Tkinter可用的图片格式
            photo = ImageTk.PhotoImage(scaled_image)
            
            # 创建画布，大小为图片的3倍
            canvas = tk.Canvas(preview_window, width=scaled_width, height=scaled_height)
            canvas.pack()
            
            # 在画布上显示图片
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo  # 保持引用，防止被垃圾回收
            
            # 选择区域的变量
            self.start_x = None
            self.start_y = None
            self.rect = None
            selected_region = None  # 存储最终选择的区域
            
            # 鼠标按下事件
            def on_mouse_down(event):
                self.start_x = canvas.canvasx(event.x)
                self.start_y = canvas.canvasy(event.y)
                # 创建矩形
                if self.rect:
                    canvas.delete(self.rect)
                self.rect = canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)
            
            # 鼠标移动事件
            def on_mouse_move(event):
                if self.start_x is not None and self.start_y is not None:
                    current_x = canvas.canvasx(event.x)
                    current_y = canvas.canvasy(event.y)
                    # 更新矩形
                    canvas.coords(self.rect, self.start_x, self.start_y, current_x, current_y)
            
            # 鼠标释放事件
            def on_mouse_up(event):
                nonlocal selected_region
                if self.start_x is not None and self.start_y is not None:
                    end_x = canvas.canvasx(event.x)
                    end_y = canvas.canvasy(event.y)
                    
                    # 确保坐标顺序正确
                    x1 = min(self.start_x, end_x)
                    y1 = min(self.start_y, end_y)
                    x2 = max(self.start_x, end_x)
                    y2 = max(self.start_y, end_y)
                    
                    # 检查选择区域是否有效
                    if x2 - x1 > 10 and y2 - y1 > 10:
                        # 存储选中的区域
                        selected_region = (x1, y1, x2, y2)
                    else:
                        selected_region = None
                        messagebox.showinfo("提示", "请选择一个更大的区域")
                    
                    # 重置变量
                    self.start_x = None
                    self.start_y = None
            
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
                    cropped_image = Image.open(image_path).crop((original_x1, original_y1, original_x2, original_y2))
                    
                    # 保存为临时文件到根目录
                    temp_file = os.path.join(os.path.abspath("."), "selected_region_temp.png")
                    cropped_image.save(temp_file)
                    
                    # 更新图片路径为选中的区域
                    self.image_path_var.set(temp_file)
                    
                    # 关闭预览窗口
                    preview_window.destroy()
                    
                    # 重新启用主窗口
                    self.root.attributes('-disabled', False)
                    
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
            confirm_button = tk.Button(button_frame, text="确认选择", command=on_confirm, font=("微软雅黑", 12), width=15)
            confirm_button.pack(pady=10)
            
            # 添加提示标签
            hint_label = tk.Label(preview_window, text="提示: 按住鼠标左键拖拽选择要识别的区域，可反复选择直到点击确认")
            hint_label.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            preview_window.destroy()
            # 重新启用主窗口
            self.root.attributes('-disabled', False)
    
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
        
        # 定义计算完成后的回调（用于更新UI）
        def on_recognition_done(result):
            # 用after()回到UI线程更新界面
            self.root.after(0, lambda: self.update_ui_after_recognition(result))
        
        # 启动后台线程
        def recognition_thread():
            try:
                # 记录开始时间
                start_time = time.time()
                
                numbers, total = recognize_image(image_path)
                
                # 计算识别耗时
                elapsed_time = time.time() - start_time
                
                # 构造识别结果
                result = {
                    "success": True,
                    "numbers": numbers,
                    "total": total,
                    "elapsed_time": elapsed_time
                }
            except Exception as e:
                result = {
                    "success": False,
                    "error": str(e)
                }
            
            # 识别完成后调用回调函数更新UI
            on_recognition_done(result)
        
        # 启动后台线程
        calc_thread = threading.Thread(target=recognition_thread)
        calc_thread.daemon = True  # 守护线程，程序退出时自动结束
        calc_thread.start()
    
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
            self.status_var.set(f"识别完成，耗时: {result['elapsed_time']:.2f} 秒，总和: {result['total']}")
        else:
            # 识别失败时用红字显示错误信息
            self.status_label.config(fg="red")
            self.status_var.set(f"识别失败: {result['error']}")
        
        # 识别完成后删除临时文件
        temp_file = self.image_path_var.get()
        if temp_file and ("selected_region_temp.png" in temp_file or "captured_screen_region.png" in temp_file):
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
            lines = text_content.strip().split('\n')
            
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
    
    def on_digits_modified(self, event):
        """当用户修改数字时自动更新总和"""
        # 调用 calculate_sum 方法更新总和
        self.calculate_sum()
    
    def toggle_topmost(self):
        """切换窗口置顶状态"""
        is_topmost = self.topmost_var.get()
        self.root.attributes('-topmost', is_topmost)
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
        capture_window.attributes('-fullscreen', True)
        capture_window.attributes('-alpha', 0.3)  # 设置透明度
        capture_window.attributes('-topmost', True)
        capture_window.config(cursor='cross')
        
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
            rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)
        
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
            capture_window.destroy()
            # 恢复主窗口
            self.root.deiconify()
        
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
            self.status_var.set(f"已截取屏幕区域，保存为: {os.path.basename(temp_file)}")
            
            # 开始识别
            self.recognize_digits()
        except Exception as e:
            messagebox.showerror("错误", f"截取屏幕失败: {str(e)}")
            self.status_var.set(f"截取屏幕失败: {str(e)}")
