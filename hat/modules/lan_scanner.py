# ... (局域网扫描相关代码) 

import socket
import struct
import netifaces
import asyncio
from scapy.all import ARP, Ether, srp, ICMP, IP, sr1
import nmap
from pathlib import Path
from datetime import datetime
from rich.progress import Progress
from rich.table import Table
from rich.console import Console
from rich import box
import aiohttp
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

console = Console()

COMMON_PORTS = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3389: "RDP",
    8080: "HTTP-Proxy"
}

DEVICE_SIGNATURES = {
    "printer": ["hp", "epson", "canon", "brother", "printer"],
    "router": ["router", "mikrotik", "cisco", "huawei", "asus"],
    "camera": ["camera", "hikvision", "dahua", "axis"],
    "nas": ["synology", "qnap", "nas"],
    "iot": ["iot", "smart", "xiaomi", "tuya"]
}

CRITICAL_PORTS = {
    21, 22, 23, 25, 53, 80, 443, 445, 1433, 3306, 3389, 5432, 6379, 8080, 27017
}  # 只扫描这些重要端口的漏洞

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
        return "192.168.31.0/24"  # 默认网段

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

async def get_device_type(vendor: str, open_ports: List[dict], hostname: str) -> str:
    """识别设备类型"""
    vendor_lower = vendor.lower()
    hostname_lower = hostname.lower()
    
    # 检查端口特征
    port_services = [p['service'].lower() for p in open_ports]
    
    for device_type, signatures in DEVICE_SIGNATURES.items():
        for sig in signatures:
            if (sig in vendor_lower or sig in hostname_lower or 
                any(sig in service for service in port_services)):
                return device_type.title()
    
    return "Unknown"

async def check_vulnerability(ip: str, port: int, service: str) -> List[dict]:
    """检查常见漏洞"""
    vulns = []
    nm = nmap.PortScanner()
    
    try:
        # 只使用针对性的脚本
        specific_scripts = {
            'http': 'http-vuln*',
            'ssh': 'ssh-vuln*',
            'smb': 'smb-vuln*',
            'ftp': 'ftp-vuln*',
            'mysql': 'mysql-vuln*'
        }
        
        script = specific_scripts.get(service, 'vuln')
        script_args = f"--script {script} -p{port}"
        
        nm.scan(ip, arguments=f"{script_args} -T4")
        
        if ip in nm.all_hosts():
            script_results = nm[ip]['tcp'][port].get('script', {})
            for name, details in script_results.items():
                if 'VULNERABLE' in details.upper():
                    vulns.append({
                        'name': name,
                        'details': details
                    })
    except Exception as e:
        pass
    
    return vulns


async def analyze_network_topology(hosts: List[dict]) -> dict:
    """分析网络拓扑结构"""
    topology = {
        'gateway': None,
        'subnets': {},
        'device_types': {}
    }
    
    # 识别网关
    for host in hosts:
        if any(service['service'] == 'router' for service in host['open_ports']):
            topology['gateway'] = host['ip']
            break
    
    # 按设备类型分类
    for host in hosts:
        device_type = host['device_type']
        if device_type not in topology['device_types']:
            topology['device_types'][device_type] = []
        topology['device_types'][device_type].append(host['ip'])
    
    return topology

async def deep_port_scan(ip: str) -> List[dict]:
    """深度端口扫描"""
    open_ports = []
    nm = nmap.PortScanner()
    
    try:
        # 优化扫描参数
        # -T5: 最快的计时模板
        # -n: 不进行DNS解析
        # --min-rate=2000: 提高最小发包率
        # -Pn: 跳过主机发现
        # --version-intensity 2: 降低版本检测强度
        nm.scan(
            ip,
            arguments='-sS -sV -T5 -n -Pn --min-rate=2000 --max-retries=1 --host-timeout=10s --version-intensity 2'
        )
        
        if ip in nm.all_hosts():
            for proto in nm[ip].all_protocols():
                ports = nm[ip][proto].keys()
                for port in ports:
                    service = nm[ip][proto][port]
                    if service['state'] == 'open':
                        # 只对重要端口进行漏洞扫描
                        vulns = []
                        if port in CRITICAL_PORTS:  # 定义关键端口列表
                            vulns = await check_vulnerability(ip, port, service['name'])
                        
                        open_ports.append({
                            'port': port,
                            'service': service['name'],
                            'version': service.get('version', ''),
                            'vulnerabilities': vulns
                        })
                        
    except Exception as e:
        console.print(f"[yellow]端口扫描出错 ({ip}): {str(e)}[/]")
    
    return open_ports

async def get_hostname(ip: str) -> str:
    """异步获取主机名"""
    try:
        # 首先尝试DNS反向查询
        loop = asyncio.get_event_loop()
        hostname = await loop.run_in_executor(
            None,
            lambda: socket.gethostbyaddr(ip)[0]
        )
        return hostname
    except:
        # DNS反向查询失败,尝试使用nmap的NBT扫描
        try:
            nm = nmap.PortScanner()
            nm.scan(ip, arguments='-sU -p137 --script nbstat')
            if (ip in nm.all_hosts() and 
                'hostscript' in nm[ip] and 
                len(nm[ip]['hostscript']) > 0):
                for script in nm[ip]['hostscript']:
                    if script['id'] == 'nbstat':
                        # 解析NBT扫描结果
                        if 'Computer Name' in script['output']:
                            return script['output'].split('Computer Name:')[1].split('\n')[0].strip()
        except:
            pass
        return "Unknown"

async def scan_with_timeout(coro, timeout=10):
    """带超时的扫描包装器"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return None
    except Exception as e:
        return None

async def lan_scan(network: str):
    """增强版局域网扫描"""
    try:
        async def scan_process():
            console.print(f"\n[bold blue]正在执行深度网络扫描 {network}...[/]")
            
            with Progress() as progress:
                # ARP扫描
                task1 = progress.add_task("[cyan]ARP扫描中...", total=1)
                arp = ARP(pdst=network)
                ether = Ether(dst="ff:ff:ff:ff:ff:ff")
                packet = ether/arp
                result = srp(packet, timeout=2, verbose=0)[0]
                progress.update(task1, completed=1)
                
                if not result:
                    console.print("\n[yellow]未发现活跃主机[/]")
                    return
                
                total_hosts = len(result)
                progress.print(f"[green]发现 {total_hosts} 个活跃主机[/]")
                
                # 创建任务组
                main_task = progress.add_task("[cyan]扫描进度", total=total_hosts * 5)
                
                async def scan_step(ip: str, step: str) -> tuple[str, any]:
                    """执行单个扫描步骤"""
                    try:
                        # 设置不同步骤的超时时间
                        timeouts = {
                            "hostname": 5,  # 主机名解析超时5秒
                            "os": 10,       # 操作系统检测超时10秒
                            "ports": 30     # 端口扫描超时30秒
                        }
                        
                        if step == "hostname":
                            result = await scan_with_timeout(
                                get_hostname(ip), 
                                timeout=timeouts["hostname"]
                            )
                        elif step == "os":
                            result = await scan_with_timeout(
                                get_os_info(ip), 
                                timeout=timeouts["os"]
                            )
                        elif step == "ports":
                            result = await scan_with_timeout(
                                deep_port_scan(ip), 
                                timeout=timeouts["ports"]
                            )
                            
                        if result is None:
                            progress.print(f"[yellow]{step}扫描超时 ({ip})[/]")
                            result = "Unknown" if step != "ports" else []
                            
                        progress.update(main_task, advance=1)
                        return step, result
                    except Exception as e:
                        progress.print(f"[yellow]{step}扫描出错 ({ip}): {str(e)}[/]")
                        progress.update(main_task, advance=1)
                        # 返回默认值而不是None
                        return step, "Unknown" if step != "ports" else []

                # 并发扫描所有主机
                host_details = []
                for sent, received in result:
                    ip, mac = received.psrc, received.hwsrc
                    progress.print(f"\n[blue]扫描主机: {ip}[/]")
                    
                    # 获取厂商信息（这个比较快，可以同步执行）
                    vendor = await scan_with_timeout(get_mac_vendor(mac), timeout=2)
                    vendor = vendor or "Unknown"
                    progress.update(main_task, advance=1)
                    
                    # 创建该主机的所有扫描任务
                    tasks = [
                        scan_step(ip, "hostname"),
                        scan_step(ip, "os"),
                        scan_step(ip, "ports")
                    ]
                    
                    # 并发执行该主机的所有扫描任务
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # 整理扫描结果，处理可能的异常
                    scan_results = {}
                    for result in results:
                        if isinstance(result, tuple):  # 正常结果
                            step, value = result
                            scan_results[step] = value
                        else:  # 发生异常
                            continue
                    
                    # 识别设备类型
                    device_type = await scan_with_timeout(
                        get_device_type(
                            vendor, 
                            scan_results.get("ports", []),
                            scan_results.get("hostname", "Unknown")
                        ),
                        timeout=5
                    ) or "Unknown"
                    progress.update(main_task, advance=1)
                    
                    host_details.append({
                        'ip': ip,
                        'mac': mac,
                        'hostname': scan_results.get("hostname", "Unknown"),
                        'vendor': vendor,
                        'os': scan_results.get("os", "Unknown"),
                        'device_type': device_type,
                        'open_ports': scan_results.get("ports", [])
                    })
                
                # 分析网络拓扑
                progress.print("\n[cyan]正在分析网络拓扑...[/]")
                topology = await scan_with_timeout(
                    analyze_network_topology(host_details),
                    timeout=10
                ) or {'gateway': None, 'device_types': {}}
                
                # 生成报告
                progress.print("[cyan]正在生成报告...[/]")
                await generate_report(network, host_details, topology)
                await display_results(host_details, topology)
                await display_summary(network, host_details, topology)
        
        await scan_process()
            
    except Exception as e:
        console.print(f"[red]扫描过程中出错: {str(e)}[/]")

async def generate_report(network: str, hosts: List[dict], topology: dict):
    """生成详细的扫描报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(f"scan_results/lanscan_{timestamp}")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成HTML报告
    html_report = report_dir / "report.html"
    await generate_html_report(html_report, network, hosts, topology)
    
    # 生成JSON报告
    json_report = report_dir / "report.json"
    await generate_json_report(json_report, network, hosts, topology)
    
    console.print(f"\n[green]报告已生成在: {report_dir}[/]")
    
    # 显示摘要
    await display_summary(network, hosts, topology)

async def display_results(hosts: List[dict], topology: dict):
    """显示扫描结果"""
    # 主机表格
    table = Table(
        title="局域网扫描详细结果",
        show_header=True,
        header_style="bold magenta",
        box=box.SQUARE
    )
    
    # 添加更多列以显示设备信息
    table.add_column("IP地址", style="cyan")
    table.add_column("MAC地址", style="blue")
    table.add_column("主机名", style="green")
    table.add_column("设备厂商", style="yellow")
    table.add_column("设备类型", style="magenta")
    table.add_column("操作系统", style="cyan")
    table.add_column("开放端口", style="red")
    table.add_column("漏洞", style="red")
    
    for host in hosts:
        vulns = sum(len(port['vulnerabilities']) for port in host['open_ports'])
        ports_str = "\n".join([
            f"• {p['port']}/{p['service']} ({p['version']})"
            for p in host['open_ports']
        ])
        
        table.add_row(
            host['ip'],
            host['mac'],
            host['hostname'] or "未知",
            host['vendor'] or "未知",
            host['device_type'],
            host['os'] or "未知",
            ports_str or "无",
            f"发现 {vulns} 个漏洞" if vulns else "无"
        )
    
    console.print(table)
    
    # 显示拓扑信息
    console.print("\n[bold blue]网络拓扑分析[/]")
    console.print(f"网关: [cyan]{topology['gateway']}[/]")
    
    # 按设备类型分组显示
    for device_type, ips in topology['device_types'].items():
        console.print(f"\n[bold green]{device_type}:[/] ({len(ips)}台)")
        for ip in ips:
            # 查找对应主机的详细信息
            host = next((h for h in hosts if h['ip'] == ip), None)
            if host:
                console.print(
                    f"  • {host['ip']} - "
                    f"MAC: {host['mac']} - "
                    f"厂商: {host['vendor'] or '未知'} - "
                    f"主机名: {host['hostname'] or '未知'}"
                )

async def generate_html_report(report_file: Path, network: str, hosts: List[dict], topology: dict):
    """生成HTML格式的扫描报告"""
    # 生成主机表格行
    host_rows = []
    for host in hosts:
        ports_str = '<br>'.join(f"{p['port']}/{p['service']} ({p['version']})" for p in host['open_ports'])
        vulns_str = '<br>'.join(f"{v['name']}: {v['details']}" for p in host['open_ports'] for v in p['vulnerabilities'])
        
        host_row = f"""
            <tr>
                <td>{host['ip']}</td>
                <td>{host['mac']}</td>
                <td>{host['hostname']}</td>
                <td>{host['device_type']}</td>
                <td>{host['os']}</td>
                <td>{ports_str}</td>
                <td class="vulnerability">{vulns_str}</td>
            </tr>
        """
        host_rows.append(host_row)
    
    # 生成设备类型分布列表
    device_type_items = ''.join(
        f'<li>{device_type}: {len(ips)}台设备</li>' 
        for device_type, ips in topology['device_types'].items()
    )
    
    html_content = f"""
    <html>
    <head>
        <title>局域网扫描报告 - {network}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .vulnerability {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>局域网扫描报告</h1>
        <p>扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>目标网段: {network}</p>
        
        <h2>网络拓扑</h2>
        <p>网关: {topology['gateway']}</p>
        <h3>设备类型分布:</h3>
        <ul>
            {device_type_items}
        </ul>
        
        <h2>主机详情</h2>
        <table>
            <tr>
                <th>IP地址</th>
                <th>MAC地址</th>
                <th>主机名</th>
                <th>设备类型</th>
                <th>操作系统</th>
                <th>开放端口</th>
                <th>漏洞信息</th>
            </tr>
            {''.join(host_rows)}
        </table>
    </body>
    </html>
    """
    
    report_file.write_text(html_content)

async def generate_json_report(report_file: Path, network: str, hosts: List[dict], topology: dict):
    """生成JSON格式的扫描报告"""
    import json
    
    report_data = {
        'scan_time': datetime.now().isoformat(),
        'network': network,
        'topology': topology,
        'hosts': hosts
    }
    
    report_file.write_text(json.dumps(report_data, indent=2, ensure_ascii=False))

async def display_summary(network: str, hosts: List[dict], topology: dict):
    """在命令行显示扫描结果摘要"""
    console.print("\n[bold blue]===== 扫描结果摘要 =====[/]")
    
    # 显示基本信息
    console.print(f"\n[cyan]目标网段:[/] {network}")
    console.print(f"[cyan]扫描时间:[/] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"[cyan]发现主机数:[/] {len(hosts)}")
    
    # 显示网关信息
    gateway_host = next((h for h in hosts if h['ip'] == topology['gateway']), None)
    if gateway_host:
        console.print(f"\n[bold green]网关设备:[/]")
        console.print(f"  IP: {gateway_host['ip']}")
        console.print(f"  MAC: {gateway_host['mac']}")
        console.print(f"  厂商: {gateway_host['vendor'] or '未知'}")
        console.print(f"  设备类型: {gateway_host['device_type']}")
    
    # 显示设备类型统计
    console.print("\n[bold green]设备类型分布:[/]")
    for device_type, ips in topology['device_types'].items():
        console.print(f"  • {device_type}: {len(ips)}台")
        # 显示每种类型的第一个设备作为示例
        if ips:
            example_host = next((h for h in hosts if h['ip'] == ips[0]), None)
            if example_host:
                console.print(f"    示例: {example_host['ip']} ({example_host['vendor'] or '未知厂商'})")
    
    # 显示漏洞统计
    total_vulns = sum(len(port['vulnerabilities']) 
                     for host in hosts 
                     for port in host['open_ports'])
    console.print(f"\n[bold red]发现漏洞总数:[/] {total_vulns}")
    
    # 显示高危主机
    high_risk_hosts = [host for host in hosts 
                      if sum(len(port['vulnerabilities']) 
                      for port in host['open_ports']) > 0]
    
    if high_risk_hosts:
        console.print("\n[bold red]存在漏洞的主机:[/]")
        for host in high_risk_hosts:
            vuln_count = sum(len(port['vulnerabilities']) 
                           for port in host['open_ports'])
            console.print(
                f"  • {host['ip']} - "
                f"MAC: {host['mac']} - "
                f"厂商: {host['vendor'] or '未知'} - "
                f"{vuln_count}个漏洞"
            )
    
    console.print("\n[bold blue]========================[/]") 