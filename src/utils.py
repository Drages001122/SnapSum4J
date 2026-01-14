import os
import sys

# 解决打包后路径问题的核心函数：获取资源真实路径
def get_resource_path(relative_path):
    """
    兼容开发环境（源码运行）和打包后环境（exe运行）的路径获取
    """
    if hasattr(sys, '_MEIPASS'):
        # 打包后，临时解压目录（单文件模式）
        base_path = sys._MEIPASS
    else:
        # 开发环境，项目根目录
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
