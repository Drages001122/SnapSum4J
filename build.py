#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本
用于自动化构建SnapSum4J应用程序
"""

import os
import shutil
import subprocess
import sys


def clean_build():
    """清理之前的构建产物"""
    print("正在清理之前的构建产物...")
    
    # 需要清理的目录和文件
    build_dirs = ['build', 'dist']
    spec_file = 'SnapSum4J.spec'
    
    # 清理目录
    for directory in build_dirs:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print(f"清理目录: {directory}")
            except Exception as e:
                print(f"清理目录 {directory} 失败: {e}")
    
    # 清理spec文件（可选）
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"清理文件: {spec_file}")
        except Exception as e:
            print(f"清理文件 {spec_file} 失败: {e}")
    
    print("清理完成\n")


def generate_spec():
    """生成PyInstaller spec文件"""
    print("正在生成PyInstaller配置文件...")
    
    # 主入口文件
    main_script = 'digit_recognition_app.py'
    
    # 生成spec文件的命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', 'SnapSum4J',
        '--console',  # 使用控制台模式
        main_script
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("生成配置文件成功")
        if result.stdout:
            print("输出:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"生成配置文件失败: {e}")
        print("错误输出:", e.stderr)
        return False
    
    print("生成配置文件完成\n")
    return True


def build_app():
    """构建应用程序"""
    print("正在构建应用程序...")
    
    # 使用生成的spec文件构建
    spec_file = 'SnapSum4J.spec'
    
    if not os.path.exists(spec_file):
        print(f"错误: {spec_file} 文件不存在")
        return False
    
    # 构建命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '-y',  # 自动覆盖输出目录
        spec_file
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建应用程序成功")
        if result.stdout:
            print("输出:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"构建应用程序失败: {e}")
        print("错误输出:", e.stderr)
        return False
    
    print("构建应用程序完成\n")
    return True


def verify_build():
    """验证构建结果"""
    print("正在验证构建结果...")
    
    # 检查构建产物是否存在
    dist_dir = 'dist/SnapSum4J'
    exe_path = os.path.join(dist_dir, 'SnapSum4J.exe')
    
    if os.path.exists(exe_path):
        print(f"✅ 构建成功! 可执行文件位置: {exe_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # 转换为MB
        print(f"可执行文件大小: {file_size:.2f} MB")
        
        return True
    else:
        print(f"❌ 构建失败! 可执行文件不存在: {exe_path}")
        return False


def main():
    """主函数"""
    print("=== SnapSum4J 打包脚本 ===")
    print("开始构建过程...\n")
    
    # 步骤1: 清理
    clean_build()
    
    # 步骤2: 生成spec文件
    if not generate_spec():
        print("生成配置文件失败，构建过程终止")
        return 1
    
    # 步骤3: 构建应用
    if not build_app():
        print("构建应用程序失败，构建过程终止")
        return 1
    
    # 步骤4: 验证构建
    if verify_build():
        # 步骤5: 删除spec文件
        spec_file = 'SnapSum4J.spec'
        if os.path.exists(spec_file):
            try:
                os.remove(spec_file)
                print(f"已删除临时文件: {spec_file}")
            except Exception as e:
                print(f"删除 {spec_file} 失败: {e}")
        print("\n🎉 构建过程完成！")
        return 0
    else:
        print("\n❌ 构建过程失败！")
        return 1


if __name__ == '__main__':
    sys.exit(main())
