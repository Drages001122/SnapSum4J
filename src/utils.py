import os
import sys

from PIL.ImageFile import ImageFile

from src.constant import SCALE_FACTOR


# 解决打包后路径问题的核心函数：获取资源真实路径
def get_resource_path(relative_path):
    """
    兼容开发环境（源码运行）和打包后环境（exe运行）的路径获取
    """
    if hasattr(sys, "_MEIPASS"):
        # 打包后，临时解压目录（单文件模式）
        base_path = sys._MEIPASS
    else:
        # 开发环境，项目根目录
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def calculate_scaled_size(image: ImageFile):
    img_width, img_height = image.size
    scaled_width = int(img_width * SCALE_FACTOR)
    scaled_height = int(img_height * SCALE_FACTOR)
    return scaled_width, scaled_height
