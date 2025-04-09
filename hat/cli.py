#!/usr/bin/env python3
"""HAT - HTTP Analysis Tool 命令行入口"""

import sys
import os
from pathlib import Path

# 确保可以导入主模块
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# 导入主程序
from main import main
import asyncio

if __name__ == "__main__":
    try:
        # 检查是否有足够的权限运行某些功能
        if os.name != 'nt' and os.geteuid() != 0:
            print("警告: 某些功能(如端口扫描和局域网扫描)可能需要管理员权限才能正常工作。")
            print("建议使用 'sudo python hat/cli.py' 运行。\n")
        
        # 运行主程序
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        sys.exit(1) 