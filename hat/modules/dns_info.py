# ... (DNS信息收集相关代码) 

import dns.resolver
import socket
import ssl
import OpenSSL.crypto as crypto
import whois
from pathlib import Path
from datetime import datetime
from rich.progress import Progress
from rich.table import Table
from rich.console import Console
from rich import box

console = Console()

async def get_dns_records(domain: str) -> dict:
    """获取所有DNS记录"""
    records = {
        'A': [],
        'AAAA': [],
        'CNAME': [],
        'MX': [],
        'NS': [],
        'TXT': [],
        'SOA': [],
        'PTR': [],
        'SRV': [],
        'CAA': [],
    }
    
    resolver = dns.resolver.Resolver()
    
    with Progress() as progress:
        task = progress.add_task("[cyan]正在收集DNS记录...", total=len(records))
        
        for record_type in records.keys():
            try:
                answers = resolver.resolve(domain, record_type)
                if record_type == 'MX':
                    records[record_type] = [(str(r.exchange), r.preference) for r in answers]
                elif record_type == 'SOA':
                    for rdata in answers:
                        records[record_type].append({
                            'mname': str(rdata.mname),
                            'rname': str(rdata.rname),
                            'serial': rdata.serial,
                            'refresh': rdata.refresh,
                            'retry': rdata.retry,
                            'expire': rdata.expire,
                            'minimum': rdata.minimum
                        })
                elif record_type == 'SRV':
                    records[record_type] = [(str(r.target), r.port, r.priority, r.weight) for r in answers]
                else:
                    records[record_type] = [str(r) for r in answers]
            except Exception as e:
                pass
            progress.update(task, advance=1)
    
    return records

async def get_ssl_info(domain: str) -> dict:
    """获取SSL证书信息"""
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain, 443))
            cert = s.getpeercert(binary_form=True)
            cert_pem = ssl.DER_cert_to_PEM_cert(cert)
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
            
            # 获取证书信息
            info = {
                'subject': dict(x509.get_subject().get_components()),
                'issuer': dict(x509.get_issuer().get_components()),
                'version': x509.get_version(),
                'serial_number': x509.get_serial_number(),
                'not_before': x509.get_notBefore(),
                'not_after': x509.get_notAfter(),
                'alt_names': [],
                'signature_algorithm': x509.get_signature_algorithm().decode()
            }
            
            # 获取SAN
            for i in range(x509.get_extension_count()):
                ext = x509.get_extension(i)
                if ext.get_short_name() == b'subjectAltName':
                    san = str(ext)
                    info['alt_names'] = [name.split('DNS:')[1].strip() for name in san.split(',') if 'DNS:' in name]
            
            return info
    except:
        return None

async def get_whois_info(domain: str) -> dict:
    """获取Whois信息"""
    try:
        w = whois.whois(domain)
        return {
            'registrar': w.registrar,
            'creation_date': w.creation_date,
            'expiration_date': w.expiration_date,
            'last_updated': w.updated_date,
            'status': w.status,
            'name_servers': w.name_servers,
            'emails': w.emails
        }
    except:
        return None

async def dns_info(domain: str):
    """收集域名的DNS信息"""
    console.print(f"\n[bold blue]正在收集 {domain} 的DNS信息...[/]")
    
    try:
        with Progress() as progress:
            # 第一阶段：DNS记录
            task1 = progress.add_task("[cyan]收集DNS记录...", total=1)
            dns_records = await get_dns_records(domain)
            progress.update(task1, completed=1)
            
            # 第二阶段：SSL证书
            task2 = progress.add_task("[cyan]获取SSL证书信息...", total=1)
            ssl_info = await get_ssl_info(domain)
            progress.update(task2, completed=1)
            
            # 第三阶段：Whois信息
            task3 = progress.add_task("[cyan]获取Whois信息...", total=1)
            whois_info = await get_whois_info(domain)
            progress.update(task3, completed=1)
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = Path(f"scan_results/dns_info_{timestamp}.txt")
            result_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(result_file, "w", encoding="utf-8") as f:
                f.write(f"DNS信息收集结果 - {domain}\n")
                f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 60 + "\n\n")
                
                # DNS记录
                f.write("DNS记录:\n")
                f.write("-" * 20 + "\n")
                for record_type, records in dns_records.items():
                    if records:
                        f.write(f"{record_type} 记录:\n")
                        for record in records:
                            if isinstance(record, dict):
                                for k, v in record.items():
                                    f.write(f"  {k}: {v}\n")
                            elif isinstance(record, tuple):
                                f.write(f"  {' '.join(map(str, record))}\n")
                            else:
                                f.write(f"  {record}\n")
                        f.write("\n")
                
                # SSL证书信息
                if ssl_info:
                    f.write("\nSSL证书信息:\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"版本: {ssl_info['version']}\n")
                    f.write(f"序列号: {ssl_info['serial_number']}\n")
                    f.write(f"签名算法: {ssl_info['signature_algorithm']}\n")
                    f.write(f"生效时间: {ssl_info['not_before']}\n")
                    f.write(f"过期时间: {ssl_info['not_after']}\n")
                    f.write("主体信息:\n")
                    for k, v in ssl_info['subject'].items():
                        f.write(f"  {k.decode()}: {v.decode()}\n")
                    f.write("颁发者信息:\n")
                    for k, v in ssl_info['issuer'].items():
                        f.write(f"  {k.decode()}: {v.decode()}\n")
                    if ssl_info['alt_names']:
                        f.write("备用名称:\n")
                        for name in ssl_info['alt_names']:
                            f.write(f"  {name}\n")
                
                # Whois信息
                if whois_info:
                    f.write("\nWhois信息:\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"注册商: {whois_info['registrar']}\n")
                    f.write(f"创建时间: {whois_info['creation_date']}\n")
                    f.write(f"过期时间: {whois_info['expiration_date']}\n")
                    f.write(f"最后更新: {whois_info['last_updated']}\n")
                    f.write("状态:\n")
                    if isinstance(whois_info['status'], list):
                        for status in whois_info['status']:
                            f.write(f"  {status}\n")
                    else:
                        f.write(f"  {whois_info['status']}\n")
                    f.write("名称服务器:\n")
                    for ns in whois_info['name_servers']:
                        f.write(f"  {ns}\n")
                    if whois_info['emails']:
                        f.write("联系邮箱:\n")
                        for email in whois_info['emails']:
                            f.write(f"  {email}\n")
            
            # 显示表格
            tables = []
            
            # DNS记录表格
            dns_table = Table(
                title="DNS记录",
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                box=box.SQUARE
            )
            
            dns_table.add_column("记录类型", style="cyan", justify="center")
            dns_table.add_column("值", style="yellow", justify="left")
            
            for record_type, records in dns_records.items():
                if records:
                    for record in records:
                        if isinstance(record, dict):
                            value = "\n".join([f"{k}: {v}" for k, v in record.items()])
                        elif isinstance(record, tuple):
                            value = " ".join(map(str, record))
                        else:
                            value = str(record)
                        dns_table.add_row(record_type, value)
            
            tables.append(dns_table)
            
            # SSL证书表格
            if ssl_info:
                ssl_table = Table(
                    title="SSL证书信息",
                    show_header=True,
                    header_style="bold magenta",
                    show_lines=True,
                    box=box.SQUARE
                )
                
                ssl_table.add_column("项目", style="cyan", justify="left")
                ssl_table.add_column("值", style="yellow", justify="left")
                
                ssl_table.add_row("版本", str(ssl_info['version']))
                ssl_table.add_row("序列号", str(ssl_info['serial_number']))
                ssl_table.add_row("签名算法", ssl_info['signature_algorithm'])
                ssl_table.add_row("生效时间", ssl_info['not_before'].decode())
                ssl_table.add_row("过期时间", ssl_info['not_after'].decode())
                ssl_table.add_row(
                    "主体信息",
                    "\n".join([f"{k.decode()}: {v.decode()}" for k, v in ssl_info['subject'].items()])
                )
                ssl_table.add_row(
                    "颁发者",
                    "\n".join([f"{k.decode()}: {v.decode()}" for k, v in ssl_info['issuer'].items()])
                )
                if ssl_info['alt_names']:
                    ssl_table.add_row("备用名称", "\n".join(ssl_info['alt_names']))
                
                tables.append(ssl_table)
            
            # Whois表格
            if whois_info:
                whois_table = Table(
                    title="Whois信息",
                    show_header=True,
                    header_style="bold magenta",
                    show_lines=True,
                    box=box.SQUARE
                )
                
                whois_table.add_column("项目", style="cyan", justify="left")
                whois_table.add_column("值", style="yellow", justify="left")
                
                whois_table.add_row("注册商", str(whois_info['registrar']))
                whois_table.add_row("创建时间", str(whois_info['creation_date']))
                whois_table.add_row("过期时间", str(whois_info['expiration_date']))
                whois_table.add_row("最后更新", str(whois_info['last_updated']))
                whois_table.add_row(
                    "状态",
                    "\n".join(whois_info['status']) if isinstance(whois_info['status'], list)
                    else str(whois_info['status'])
                )
                whois_table.add_row("名称服务器", "\n".join(whois_info['name_servers']))
                if whois_info['emails']:
                    whois_table.add_row("联系邮箱", "\n".join(whois_info['emails']))
                
                tables.append(whois_table)
            
            # 显示所有表格
            console.print("\n")
            for table in tables:
                console.print(table)
                console.print("\n")
            
            console.print(f"[green]信息收集完成！[/]")
            console.print(f"[blue]结果已保存到: {result_file}[/]")
        
    except Exception as e:
        console.print(f"[red]信息收集出错: {str(e)}[/]") 