#!/usr/bin/env python3
"""安装HAT工具所需的依赖"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """安装依赖包"""
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("错误: 未找到requirements.txt文件")
        return False
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)])
        print("\n依赖安装完成!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n安装依赖时出错: {e}")
        return False

if __name__ == "__main__":
    print("开始安装HAT工具依赖...")
    if install_requirements():
        print("\n现在可以运行 python hat/main.py 来启动工具了")
    else:
        print("\n安装失败，请检查错误信息并重试") 