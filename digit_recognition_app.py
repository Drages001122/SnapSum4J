import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import easyocr
import re
import os

# 复用现有的数字识别功能
def recognize_image(image_path):
    """识别图片中的数字并计算总和"""
    try:
        # 初始化EasyOCR（使用英文模型，足够识别数字）
        reader = easyocr.Reader(lang_list=["en"], gpu=False)
        # 识别图片
        result = reader.readtext(image_path)
        # 提取数字（支持小数）
        all_numbers = []
        for detection in result:
            text = detection[1]
            numbers = re.findall(r'\d+(?:\.\d+)?', text)
            if numbers:
                all_numbers.extend(numbers)
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
        
        recognize_button = tk.Button(upload_frame, text="识别数字", command=self.recognize_digits)
        recognize_button.pack(side=tk.LEFT, padx=5)
        
        # 数字显示区域
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        text_label = tk.Label(text_frame, text="识别到的数字（每行一个，可手动添加）:")
        text_label.pack(anchor=tk.W, pady=5)
        
        self.digits_text = ScrolledText(text_frame, height=10, width=60, font=("Courier New", 12))
        self.digits_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # 求和区域
        sum_frame = tk.Frame(main_frame)
        sum_frame.pack(fill=tk.X, pady=10)
        
        sum_button = tk.Button(sum_frame, text="计算总和", command=self.calculate_sum, font=("微软雅黑", 10, "bold"))
        sum_button.pack(side=tk.LEFT, padx=5)
        
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
    
    def recognize_digits(self):
        """识别图片中的数字"""
        image_path = self.image_path_var.get()
        if not image_path:
            messagebox.showerror("错误", "请先选择一张图片")
            return
        
        if not os.path.exists(image_path):
            messagebox.showerror("错误", "选择的图片文件不存在")
            return
        
        self.status_var.set("正在识别数字...")
        self.root.update()
        
        try:
            numbers, total = recognize_image(image_path)
            
            # 清空文本框和上一次的求和结果
            self.digits_text.delete(1.0, tk.END)
            self.sum_result_var.set("")
            for number in numbers:
                self.digits_text.insert(tk.END, f"{number}\n")
            
            self.status_var.set(f"识别完成，找到 {len(numbers)} 个数字")
            messagebox.showinfo("识别完成", f"成功识别到 {len(numbers)} 个数字")
        except Exception as e:
            messagebox.showerror("错误", f"识别失败: {str(e)}")
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
            
            self.status_var.set(f"计算完成，共 {len(numbers)} 个有效数字")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")
            self.status_var.set(f"计算失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitRecognitionApp(root)
    root.mainloop()