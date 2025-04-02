from typing import List, Tuple
import asyncio
from pathlib import Path
from datetime import datetime
from rich.progress import Progress
from rich.table import Table
from rich.console import Console
from rich import box

console = Console()

async def scan_port(host: str, port: int) -> tuple[int, bool]:
    """扫描单个端口"""
    try:
        _, writer = await asyncio.open_connection(host, port)
        writer.close()
        await writer.wait_closed()
        return port, True
    except:
        return port, False

async def port_scanner(host: str, start_port: int = 1, end_port: int = 1024) -> list[int]:
    """端口扫描器"""
    tasks = [scan_port(host, port) for port in range(start_port, end_port + 1)]
    results = await asyncio.gather(*tasks)
    return [port for port, is_open in results if is_open]

# 常见端口服务对照
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP Proxy"
}

async def scan_ports(host: str, start_port: int = 1, end_port: int = 1024):
    """执行端口扫描并显示结果"""
    try:
        with Progress() as progress:
            task = progress.add_task(
                "[cyan]端口扫描中...", 
                total=end_port - start_port + 1
            )
            
            open_ports = []
            for port in range(start_port, end_port + 1):
                result = await scan_port(host, port)
                if result[1]:  # 如果端口开放
                    open_ports.append(result[0])
                progress.update(task, advance=1)
            
            # 显示结果
            table = Table(
                title=f"{host} 的开放端口",
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                box=box.SQUARE
            )
            
            table.add_column("端口", style="cyan", justify="center")
            table.add_column("状态", style="green", justify="center")
            table.add_column("可能的服务", style="yellow", justify="left")
            
            for port in open_ports:
                service = COMMON_PORTS.get(port, "未知服务")
                table.add_row(str(port), "[green]开放[/]", service)
            
            console.print("\n")
            console.print(table)
            
            # 添加统计信息
            total_ports = end_port - start_port + 1
            console.print(f"\n[green]扫描完成！[/]")
            console.print(f"[blue]扫描端口范围: [/]{start_port}-{end_port} ({total_ports} 个端口)")
            console.print(f"[blue]发现开放端口: [/]{len(open_ports)} 个")
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = Path(f"scan_results/portscan_{timestamp}.txt")
            result_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(result_file, "w", encoding="utf-8") as f:
                f.write(f"端口扫描结果 - {host}\n")
                f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"扫描范围: {start_port}-{end_port}\n")
                f.write("-" * 60 + "\n\n")
                
                for port in open_ports:
                    service = COMMON_PORTS.get(port, "未知服务")
                    f.write(f"端口: {port}\n")
                    f.write(f"状态: 开放\n")
                    f.write(f"服务: {service}\n")
                    f.write("-" * 40 + "\n")
            
            console.print(f"[blue]结果已保存到: {result_file}[/]")
            
    except Exception as e:
        console.print(f"\n[red]扫描出错: {str(e)}[/]") 