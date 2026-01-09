# SnapSum4J - 数字识别与求和工具

## 项目简介
SnapSum4J 是一个基于 Python 的数字识别与求和工具，能够识别图片中的所有数字并计算它们的总和。该工具提供了友好的可视化界面，用户可以轻松上传图片、查看识别结果、手动添加数字并计算总和。

## 功能特性

- 🖼️ **图片数字识别**：使用 EasyOCR 库识别图片中的所有数字（支持小数）
- 📝 **可视化界面**：基于 Tkinter 的用户友好界面
- ➕ **手动添加数字**：支持用户手动在文本框中添加数字
- 🧮 **自动求和**：计算所有识别和手动添加数字的总和
- 🔢 **结果展示**：清晰展示识别到的数字和最终求和结果

## 技术栈

- **Python 3.x**：核心编程语言
- **Tkinter**：GUI 界面库
- **EasyOCR**：数字识别库
- **Regular Expressions**：数字提取
- **PyInstaller**：应用打包工具

## 安装步骤

### 方法一：使用打包好的可执行文件

1. 下载项目的打包版本
2. 解压到任意目录
3. 运行 `SnapSum4J.exe` 即可使用

### 方法二：从源码运行

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/SnapSum4J.git
   cd SnapSum4J
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   ```

3. **激活虚拟环境**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **运行应用**
   ```bash
   python digit_recognition_app.py
   ```

## 使用方法

1. **上传图片**：点击"选择图片"按钮，浏览并选择包含数字的图片
2. **识别数字**：点击"识别数字"按钮，系统会自动识别图片中的所有数字
3. **查看结果**：识别到的数字会显示在文本框中，每行一个
4. **手动添加数字**：在文本框中手动添加更多数字（每行一个）
5. **计算总和**：点击"计算总和"按钮，系统会计算所有数字的总和
6. **查看总和**：计算结果会显示在总和输入框中

## 项目结构

```
SnapSum4J/
├── digit_recognition_app.py  # 主应用文件
├── build.py                  # 打包脚本
├── requirements.txt          # 依赖项文件
├── .gitignore                # Git忽略配置
├── 需求.txt                   # 项目需求文档
└── README.md                 # 项目说明文档
```

## 依赖项

主要依赖项包括：
- easyocr==1.7.2
- numpy==2.2.6
- opencv-python-headless==4.12.0.88
- torch==2.9.1+cpu
- transformers==4.33.2

完整依赖项列表请查看 `requirements.txt` 文件。

## 打包应用

如需打包应用为可执行文件，请运行：

```bash
python build.py
```

打包完成后，可执行文件会生成在 `dist/SnapSum4J` 目录中。

## 注意事项

- 图片识别可能会受到图片质量、光照条件等因素的影响
- 识别速度取决于图片大小和计算机性能
- 目前仅支持识别数字


---

**SnapSum4J** - 让数字识别与求和变得简单！