#!/usr/bin/env python3
"""网络抓包模块"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import pyshark
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel

console = Console()

class PacketStats:
    """数据包统计"""
    def __init__(self):
        self.packet_count = 0
        self.protocols: Dict[str, int] = {}
        self.src_ips: Dict[str, int] = {}
        self.dst_ips: Dict[str, int] = {}
        self.src_ports: Dict[int, int] = {}
        self.dst_ports: Dict[int, int] = {}
        self.http_requests: Dict[str, int] = {}  # HTTP请求统计
        self.content_types: Dict[str, int] = {}  # 内容类型统计

    def update(self, packet):
        """更新统计信息"""
        self.packet_count += 1
        
        try:
            # 协议统计
            highest_layer = packet.highest_layer
            self.protocols[highest_layer] = self.protocols.get(highest_layer, 0) + 1
            
            # IP统计
            if hasattr(packet, 'ip'):
                src_ip = packet.ip.src
                dst_ip = packet.ip.dst
                self.src_ips[src_ip] = self.src_ips.get(src_ip, 0) + 1
                self.dst_ips[dst_ip] = self.dst_ips.get(dst_ip, 0) + 1
            
            # 端口统计
            if hasattr(packet, 'tcp'):
                sport, dport = int(packet.tcp.srcport), int(packet.tcp.dstport)
                self.src_ports[sport] = self.src_ports.get(sport, 0) + 1
                self.dst_ports[dport] = self.dst_ports.get(dport, 0) + 1
            elif hasattr(packet, 'udp'):
                sport, dport = int(packet.udp.srcport), int(packet.udp.dstport)
                self.src_ports[sport] = self.src_ports.get(sport, 0) + 1
                self.dst_ports[dport] = self.dst_ports.get(dport, 0) + 1
            
            # HTTP请求统计
            if hasattr(packet, 'http'):
                if hasattr(packet.http, 'request_method'):
                    method = packet.http.request_method
                    uri = packet.http.request_uri if hasattr(packet.http, 'request_uri') else ''
                    req = f"{method} {uri}"
                    self.http_requests[req] = self.http_requests.get(req, 0) + 1
                
                if hasattr(packet.http, 'content_type'):
                    content_type = packet.http.content_type
                    self.content_types[content_type] = self.content_types.get(content_type, 0) + 1
                    
        except Exception as e:
            console.print(f"[red]解析数据包出错: {str(e)}[/]")

def generate_stats_table(stats: PacketStats) -> Table:
    """生成统计表格"""
    table = Table(title="实时网络流量统计")
    
    # 添加列
    table.add_column("类型", style="cyan")
    table.add_column("详细信息", style="green")
    
    # 基本统计
    table.add_row("捕获包数", str(stats.packet_count))
    
    # 协议分布
    proto_str = "\n".join(f"{proto}: {count}" 
                         for proto, count in sorted(stats.protocols.items(), 
                         key=lambda x: x[1], reverse=True)[:5])
    table.add_row("协议分布(Top 5)", proto_str or "暂无数据")
    
    # 源IP分布
    src_ip_str = "\n".join(f"{ip}: {count}" 
                          for ip, count in sorted(stats.src_ips.items(), 
                          key=lambda x: x[1], reverse=True)[:5])
    table.add_row("源IP(Top 5)", src_ip_str or "暂无数据")
    
    # 目标IP分布
    dst_ip_str = "\n".join(f"{ip}: {count}" 
                          for ip, count in sorted(stats.dst_ips.items(), 
                          key=lambda x: x[1], reverse=True)[:5])
    table.add_row("目标IP(Top 5)", dst_ip_str or "暂无数据")
    
    # HTTP请求统计
    if stats.http_requests:
        http_str = "\n".join(f"{req}: {count}" 
                            for req, count in sorted(stats.http_requests.items(), 
                            key=lambda x: x[1], reverse=True)[:5])
        table.add_row("HTTP请求(Top 5)", http_str)
    
    # 内容类型统计
    if stats.content_types:
        content_str = "\n".join(f"{ct}: {count}" 
                               for ct, count in sorted(stats.content_types.items(), 
                               key=lambda x: x[1], reverse=True)[:5])
        table.add_row("内容类型(Top 5)", content_str)
    
    return table

async def packet_capture(
    interface: str,
    filter: str = "",
    count: Optional[int] = None,
    timeout: Optional[int] = None
):
    """网络抓包主函数"""
    
    # 创建保存目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = Path(f"capture_results/capture_{timestamp}")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # 数据包统计对象
    stats = PacketStats()
    
    # 显示抓包信息
    console.print(f"\n[bold blue]开始抓包...[/]")
    console.print(f"接口: [cyan]{interface}[/]")
    if filter:
        console.print(f"过滤器: [cyan]{filter}[/]")
    if count:
        console.print(f"包数限制: [cyan]{count}[/]")
    if timeout:
        console.print(f"时间限制: [cyan]{timeout}秒[/]")
    
    # 创建捕获对象
    capture = pyshark.LiveCapture(
        interface=interface,
        display_filter=filter,
        output_file=str(save_dir / "capture.pcap")
    )
    
    # 设置超时
    if timeout:
        capture.set_debug()
        capture.sniff_timeout = timeout
    
    # 合并进度和统计信息显示
    def get_display():
        """生成显示布局"""
        layout = Layout()
        layout.split_column(
            Layout(Panel(f"[bold cyan]正在抓包... 已捕获 {stats.packet_count} 个数据包[/]", title="状态")),
            Layout(generate_stats_table(stats))
        )
        return layout
    
    # 使用单个Live显示
    with Live(get_display(), refresh_per_second=1) as live:
        try:
            # 开始抓包
            for packet in capture.sniff_continuously(packet_count=count):
                stats.update(packet)
                live.update(get_display())
                
        except KeyboardInterrupt:
            console.print("\n[yellow]抓包被用户中断[/]")
        except Exception as e:
            console.print(f"\n[red]抓包出错: {str(e)}[/]")
            return
        finally:
            capture.close()
    
    # 生成统计报告
    report_file = save_dir / "report.txt"
    with report_file.open("w", encoding="utf-8") as f:
        f.write(f"抓包统计报告\n")
        f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"接口: {interface}\n")
        f.write(f"过滤器: {filter}\n")
        f.write(f"总包数: {stats.packet_count}\n\n")
        
        f.write("协议分布:\n")
        for proto, count in sorted(stats.protocols.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {proto}: {count}\n")
        
        f.write("\n源IP TOP 10:\n")
        for ip, count in sorted(stats.src_ips.items(), key=lambda x: x[1], reverse=True)[:10]:
            f.write(f"  {ip}: {count}\n")
        
        f.write("\n目标IP TOP 10:\n")
        for ip, count in sorted(stats.dst_ips.items(), key=lambda x: x[1], reverse=True)[:10]:
            f.write(f"  {ip}: {count}\n")
        
        if stats.http_requests:
            f.write("\nHTTP请求统计:\n")
            for req, count in sorted(stats.http_requests.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {req}: {count}\n")
        
        if stats.content_types:
            f.write("\n内容类型统计:\n")
            for ct, count in sorted(stats.content_types.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {ct}: {count}\n")
    
    # 显示结果
    console.print(f"\n[green]抓包完成![/]")
    console.print(f"PCAP文件已保存: [cyan]{save_dir / 'capture.pcap'}[/]")
    console.print(f"统计报告已保存: [cyan]{report_file}[/]")
    
    # 显示最终统计
    console.print("\n[bold blue]最终统计:[/]")
    console.print(generate_stats_table(stats)) 