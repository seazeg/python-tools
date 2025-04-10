#!/usr/bin/env python3
"""HAT - HTTP Analysis Tool 主程序"""

import asyncio
import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

# 导入模块
from modules.tech_detector import analyze_tech_stack
from modules.port_scanner import scan_ports
from modules.dir_scanner import smart_dirb
from modules.subdomain_scanner import smart_subdomains
from modules.dns_info import dns_info
from modules.lan_scanner import lan_scan
from modules.security_scanner import security_scan  # 导入安全检测模块

console = Console()

def show_banner():
    """显示工具横幅"""
    banner = """
    ██╗  ██╗ █████╗ ████████╗
    ██║  ██║██╔══██╗╚══██╔══╝
    ███████║███████║   ██║   
    ██╔══██║██╔══██║   ██║   
    ██║  ██║██║  ██║   ██║   
    ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
    HTTP Analysis Tool v1.0
    """
    console.print(Panel(banner, border_style="blue", title="欢迎使用", subtitle="by HAT Team"))

def show_menu():
    """显示主菜单"""
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("选项", style="cyan", justify="center")
    table.add_column("功能", style="green")
    table.add_column("描述", style="yellow")
    
    table.add_row("1", "技术栈检测", "检测目标网站使用的技术栈")
    table.add_row("2", "端口扫描", "扫描目标主机的开放端口")
    table.add_row("3", "目录扫描", "扫描网站的目录结构")
    table.add_row("4", "子域名枚举", "枚举目标域名的子域名")
    table.add_row("5", "DNS信息收集", "收集域名的DNS记录信息")
    table.add_row("6", "局域网扫描", "扫描局域网内的活跃主机")
    table.add_row("7", "安全检测", "检测网站的安全问题")
    table.add_row("0", "退出", "退出程序")
    
    console.print(table)

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="HAT - HTTP Analysis Tool")
    parser.add_argument("-u", "--url", help="目标URL")
    parser.add_argument("-p", "--port", help="端口扫描范围 (例如: 1-1024)")
    parser.add_argument("-d", "--domain", help="目标域名")
    parser.add_argument("-n", "--network", help="目标网段 (例如: 192.168.1.0/24)")
    parser.add_argument("-m", "--mode", type=int, choices=range(8), help="运行模式: 1=技术栈检测, 2=端口扫描, 3=目录扫描, 4=子域名枚举, 5=DNS信息收集, 6=局域网扫描, 7=安全检测, 0=交互模式")
    
    args = parser.parse_args()
    
    # 如果没有指定模式或模式为0，进入交互模式
    if args.mode is None or args.mode == 0:
        show_banner()
        while True:
            show_menu()
            choice = Prompt.ask("请选择功能", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default="0")
            
            if choice == "0":
                console.print("[bold green]感谢使用HAT工具，再见！[/]")
                break
                
            await execute_function(int(choice), args)
    else:
        # 直接执行指定的功能
        await execute_function(args.mode, args)

async def execute_function(mode, args):
    """执行选定的功能"""
    try:
        if mode == 1:  # 技术栈检测
            url = args.url or Prompt.ask("请输入目标URL", default="https://www.example.com/")
            console.print(f"[bold blue]正在检测 {url} 的技术栈...[/]")
            await analyze_tech_stack(url)
            
        elif mode == 2:  # 端口扫描
            host = args.url or Prompt.ask("请输入目标主机", default="127.0.0.1")
            if host.startswith(("http://", "https://")):
                from urllib.parse import urlparse
                host = urlparse(host).netloc.split(":")[0]
            
            port_range = args.port or Prompt.ask("请输入端口范围 (例如: 1-1024)", default="1-1024")
            start_port, end_port = map(int, port_range.split("-"))
            
            console.print(f"[bold blue]正在扫描 {host} 的端口 ({start_port}-{end_port})...[/]")
            await scan_ports(host, start_port, end_port)
            
        elif mode == 3:  # 目录扫描
            url = args.url or Prompt.ask("请输入目标URL")
            console.print(f"[bold blue]正在扫描 {url} 的目录结构...[/]")
            await smart_dirb(url)
            
        elif mode == 4:  # 子域名枚举
            domain = args.domain or Prompt.ask("请输入目标域名", default="example.com")
            console.print(f"[bold blue]正在枚举 {domain} 的子域名...[/]")
            await smart_subdomains(domain)
            
        elif mode == 5:  # DNS信息收集
            domain = args.domain or Prompt.ask("请输入目标域名", default="example.com")
            console.print(f"[bold blue]正在收集 {domain} 的DNS信息...[/]")
            await dns_info(domain)
            
        elif mode == 6:  # 局域网扫描
            network = args.network or Prompt.ask("请输入目标网段", default="192.168.31.0/24")
            console.print(f"[bold blue]正在扫描网段 {network}...[/]")
            await lan_scan(network)
            
        elif mode == 7:  # 安全检测
            url = args.url or Prompt.ask("请输入目标URL", default="https://www.example.com/")
            console.print(f"[bold blue]正在检测 {url} 的安全问题...[/]")
            await security_scan(url)
            
    except Exception as e:
        console.print(f"[bold red]执行过程中出错: {str(e)}[/]")
    
    # 在交互模式下，等待用户按回车继续
    if args.mode is None or args.mode == 0:
        console.print("\n[bold cyan]按回车键继续...[/]", end="")
        input()
        console.print("\n" + "-" * 80 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]程序被用户中断[/]")
        sys.exit(0)
