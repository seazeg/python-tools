# ... (局域网扫描相关代码) 

import socket
import struct
import netifaces
from scapy.all import ARP, Ether, srp
import nmap
from pathlib import Path
from datetime import datetime
from rich.progress import Progress
from rich.table import Table
from rich.console import Console
from rich import box

console = Console()

def get_local_network() -> str:
    """获取本地网段"""
    try:
        # 获取默认网关接口
        default_gateway = netifaces.gateways()['default'][netifaces.AF_INET][1]
        # 获取接口地址信息
        interface_info = netifaces.ifaddresses(default_gateway)[netifaces.AF_INET][0]
        ip = interface_info['addr']
        netmask = interface_info['netmask']
        
        # 计算网段
        ip_int = struct.unpack('!I', socket.inet_aton(ip))[0]
        netmask_int = struct.unpack('!I', socket.inet_aton(netmask))[0]
        network_int = ip_int & netmask_int
        network = socket.inet_ntoa(struct.pack('!I', network_int))
        
        # 计算CIDR
        cidr = bin(netmask_int).count('1')
        return f"{network}/{cidr}"
    except:
        return "192.168.1.0/24"  # 默认网段

async def get_mac_vendor(mac: str) -> str:
    """获取MAC地址对应的制造商信息"""
    try:
        import requests
        mac = mac.replace(':', '').upper()[:6]
        url = f"https://api.macvendors.com/{mac}"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    return "Unknown"

async def get_os_info(ip: str) -> str:
    """获取操作系统信息"""
    try:
        nm = nmap.PortScanner()
        nm.scan(ip, arguments='-O')
        if 'osmatch' in nm[ip]:
            matches = nm[ip]['osmatch']
            if matches:
                return matches[0]['name']
    except:
        pass
    return "Unknown"

async def get_open_ports(ip: str) -> list[dict]:
    """获取开放端口信息"""
    try:
        nm = nmap.PortScanner()
        nm.scan(ip, arguments='-sV --version-intensity 5')
        open_ports = []
        for proto in nm[ip].all_protocols():
            ports = nm[ip][proto].keys()
            for port in ports:
                service = nm[ip][proto][port]
                if service['state'] == 'open':
                    open_ports.append({
                        'port': port,
                        'service': service['name'],
                        'version': service['version']
                    })
        return open_ports
    except:
        return []

async def lan_scan(network: str):
    """扫描局域网内的所有活跃主机"""
    console.print(f"\n[bold blue]正在扫描网段 {network}...[/]")
    
    try:
        with Progress() as progress:
            # 第一阶段：ARP扫描
            task1 = progress.add_task("[cyan]ARP扫描中...", total=1)
            arp = ARP(pdst=network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            result = srp(packet, timeout=3, verbose=0)[0]
            progress.update(task1, completed=1)
            
            # 提取活跃主机IP
            alive_hosts = [received.psrc for sent, received in result]
            
            if not alive_hosts:
                console.print("\n[yellow]未发现活跃主机[/]")
                return
            
            console.print(f"\n[green]发现 {len(alive_hosts)} 个活跃主机[/]")
            
            # 第二阶段：详细信息收集
            task2 = progress.add_task(
                f"[cyan]正在收集主机详细信息 (0/{len(alive_hosts)})...", 
                total=len(alive_hosts)
            )
            
            host_details = []
            for i, (sent, received) in enumerate(result):
                ip = received.psrc
                mac = received.hwsrc
                
                # 获取主机名
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    hostname = "Unknown"
                
                # 获取制造商信息
                vendor = await get_mac_vendor(mac)
                
                # 获取操作系统信息
                os_info = await get_os_info(ip)
                
                # 获取开放端口
                open_ports = await get_open_ports(ip)
                
                host_details.append({
                    'ip': ip,
                    'mac': mac,
                    'hostname': hostname,
                    'vendor': vendor,
                    'os': os_info,
                    'open_ports': open_ports
                })
                
                progress.update(task2, advance=1)
                progress.print(f"[green]发现主机: {ip} ({hostname})[/]")
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = Path(f"scan_results/lanscan_{timestamp}.txt")
            result_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(result_file, "w", encoding="utf-8") as f:
                f.write(f"局域网扫描结果 ({network})\n")
                f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 60 + "\n\n")
                
                for host in host_details:
                    f.write(f"IP地址: {host['ip']}\n")
                    f.write(f"MAC地址: {host['mac']}\n")
                    f.write(f"主机名: {host['hostname']}\n")
                    f.write(f"制造商: {host['vendor']}\n")
                    f.write(f"操作系统: {host['os']}\n")
                    
                    if host['open_ports']:
                        f.write("开放端口:\n")
                        for port in host['open_ports']:
                            f.write(f"  {port['port']}/{port['service']}")
                            if port['version']:
                                f.write(f" ({port['version']})")
                            f.write("\n")
                    else:
                        f.write("开放端口: 无\n")
                    
                    f.write("-" * 40 + "\n")
            
            # 显示表格
            table = Table(
                title=f"局域网扫描结果 ({network})",
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                box=box.SQUARE
            )
            
            table.add_column("IP地址", style="cyan", justify="center")
            table.add_column("主机名", style="blue", justify="center")
            table.add_column("MAC地址", style="magenta", justify="center")
            table.add_column("制造商", style="yellow", justify="center")
            table.add_column("操作系统", style="red", justify="center", width=30)
            table.add_column("开放端口", style="cyan", justify="left", width=40)
            
            for host in host_details:
                ports_str = "\n".join([
                    f"• {p['port']}/{p['service']}" + 
                    (f"\n  └─ {p['version']}" if p['version'] else "")
                    for p in host['open_ports']
                ]) or "None"
                
                table.add_row(
                    host['ip'],
                    host['hostname'],
                    host['mac'],
                    host['vendor'],
                    host['os'],
                    ports_str
                )
            
            console.print("\n")
            console.print(table)
            console.print(f"\n[green]扫描完成！发现 {len(host_details)} 个活跃主机[/]")
            console.print(f"[blue]结果已保存到: {result_file}[/]")
        
    except Exception as e:
        console.print(f"[red]扫描出错: {str(e)}[/]") 