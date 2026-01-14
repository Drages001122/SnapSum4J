from paddleocr import PaddleOCR

from .utils import get_resource_path

# 复用现有的数字识别功能
def recognize_image(image_path):
    """识别图片中的数字并计算总和"""
    try:
        # 初始化 PaddleOCR 实例
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            text_detection_model_dir=get_resource_path("models/PP-OCRv5_server_det"),
            text_recognition_model_dir=get_resource_path("models/PP-OCRv5_server_rec"),
        )
        
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

        return all_numbers, total_sum
    except Exception as e:
        print(f"识别失败: {str(e)}")
        return [], 0
