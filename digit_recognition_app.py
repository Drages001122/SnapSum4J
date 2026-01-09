import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import time
from paddleocr import PaddleOCR

# 初始化 PaddleOCR 实例
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

# 复用现有的数字识别功能
def recognize_image(image_path):
    """识别图片中的数字并计算总和"""
    try:
        # 识别图片
        result = ocr.predict(input=image_path)
        # 提取数字
        all_numbers = []
        if result:
            rec_texts = []
            # 遍历result中的每个OCRResult对象
            for res in result:
                try:
                    # 检查res对象是否有rec_texts属性
                    if hasattr(res, 'rec_texts'):
                        rec_texts.extend(res.rec_texts)
                    # 或者检查是否可以通过字典方式访问
                    elif isinstance(res, dict) and 'rec_texts' in res:
                        rec_texts.extend(res['rec_texts'])
                except Exception as e:
                    print(f"Error accessing rec_texts: {e}")
            
            # 过滤出数字（支持小数）
            for text in rec_texts:
                if text.replace('.', '', 1).isdigit():
                    all_numbers.append(text)
        # 计算总和
        total_sum = sum(float(num) for num in all_numbers)
        
        return all_numbers, total_sum
    except Exception as e:
        print(f"识别失败: {str(e)}")
        return [], 0

class DigitRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数字识别与求和工具")
        self.root.geometry("600x500")
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
        self.image_path_entry = tk.Entry(upload_frame, textvariable=self.image_path_var, width=50)
        self.image_path_entry.pack(side=tk.LEFT, padx=5)
        
        upload_button = tk.Button(upload_frame, text="选择图片", command=self.upload_image)
        upload_button.pack(side=tk.LEFT, padx=5)
        
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
            # 自动识别图片
            self.recognize_digits()
    
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
        self.root.update()
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            numbers, total = recognize_image(image_path)
            
            # 计算识别耗时
            elapsed_time = time.time() - start_time
            
            # 清空文本框和上一次的求和结果
            self.digits_text.delete(1.0, tk.END)
            self.sum_result_var.set("")
            for number in numbers:
                self.digits_text.insert(tk.END, f"{number}\n")
            
            # 自动计算并显示总和
            self.sum_result_var.set(str(total))
            
            # 识别结束后用蓝字显示求和结果以及识别耗时
            self.status_label.config(fg="blue")
            # 显示识别耗时和总和，移除弹窗和数字数量
            self.status_var.set(f"识别完成，耗时: {elapsed_time:.2f} 秒，总和: {total}")
        except Exception as e:
            # 识别失败时用红字显示错误信息
            self.status_label.config(fg="red")
            self.status_var.set(f"识别失败: {str(e)}")
    
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

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitRecognitionApp(root)
    root.mainloop()