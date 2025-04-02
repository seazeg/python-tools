#!/usr/bin/env python3
import typer
import asyncio
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from pathlib import Path
import sys

# 导入各个模块
from modules.port_scanner import scan_ports
from modules.subdomain_scanner import smart_subdomains
from modules.dns_info import dns_info
from modules.lan_scanner import lan_scan, get_local_network
from modules.dir_scanner import smart_dirb

app = typer.Typer(help="黑客工具集 (Hacker's Arsenal of Tools)")
console = Console()

@app.command()
async def menu():
    """交互式菜单"""
    while True:
        console.print("\n[bold cyan]黑客工具集菜单[/]")
        console.print("1. 端口扫描")
        console.print("2. 智能子域名枚举")
        console.print("3. DNS信息收集")
        console.print("4. 局域网扫描")
        console.print("5. 智能目录扫描")
        console.print("0. 退出")
        
        choice = IntPrompt.ask("\n请选择功能", choices=["0", "1", "2", "3", "4", "5"])
        
        try:
            if choice == 0:
                console.print("[yellow]感谢使用，再见！[/]")
                break
            elif choice == 1:
                host = Prompt.ask("请输入目标主机地址")
                start_port = IntPrompt.ask("请输入起始端口", default=1)
                end_port = IntPrompt.ask("请输入结束端口", default=1024)
                await scan_ports(host=host, start_port=start_port, end_port=end_port)
            elif choice == 2:
                domain = Prompt.ask("请输入目标域名")
                await smart_subdomains(domain=domain)
            elif choice == 3:
                domain = Prompt.ask("请输入目标域名")
                await dns_info(domain=domain)
            elif choice == 4:
                network = Prompt.ask("请输入要扫描的网段 (例如: 192.168.1.0/24)", default=get_local_network())
                await lan_scan(network=network)
            elif choice == 5:
                url = Prompt.ask("请输入目标URL")
                await smart_dirb(url=url)
        except Exception as e:
            console.print(f"\n[red]执行出错: {str(e)}[/]")
            console.print("[yellow]按任意键继续...[/]")
            Prompt.ask("")

@app.command()
async def port_scan(
    host: str = typer.Argument(..., help="目标主机地址"),
    start_port: int = typer.Option(1, help="起始端口"),
    end_port: int = typer.Option(1024, help="结束端口")
):
    """扫描目标主机的开放端口"""
    await scan_ports(host=host, start_port=start_port, end_port=end_port)

@app.command()
async def subdomain_scan(
    domain: str = typer.Argument(..., help="目标域名")
):
    """智能子域名枚举"""
    await smart_subdomains(domain=domain)

@app.command()
async def dns_check(
    domain: str = typer.Argument(..., help="目标域名")
):
    """DNS信息收集"""
    await dns_info(domain=domain)

@app.command()
async def network_scan(
    network: str = typer.Argument(None, help="目标网段 (CIDR格式)")
):
    """扫描局域网内的所有活跃主机"""
    if network is None:
        network = get_local_network()
    await lan_scan(network=network)

@app.command()
async def dir_scan(
    url: str = typer.Argument(..., help="目标URL")
):
    """智能目录扫描"""
    await smart_dirb(url=url)

def main():
    """程序入口点"""
    try:
        if len(sys.argv) == 1:
            # 如果没有命令行参数，启动交互式菜单
            asyncio.run(menu())
        else:
            # 否则按照命令行参数执行
            typer.run(app)
    except KeyboardInterrupt:
        console.print("\n[yellow]程序已终止[/]")
    except Exception as e:
        console.print(f"\n[red]程序出错: {str(e)}[/]")

if __name__ == "__main__":
    main()
