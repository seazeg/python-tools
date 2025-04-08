#!/usr/bin/env python3
"""HAT - HTTP Analysis Tool 主程序"""

import asyncio
from modules.tech_detector import analyze_tech_stack

def main():
    """主函数"""
    test_url = "https://www.samsung.com.cn/"
    asyncio.run(analyze_tech_stack(test_url))

if __name__ == "__main__":
    main()
