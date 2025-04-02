# ... (子域名枚举相关代码) 

import asyncio
import socket
import aiohttp
import dns.resolver
import ssl
import OpenSSL.crypto as crypto
from pathlib import Path
from datetime import datetime
from rich.progress import Progress
from rich.table import Table
from rich.console import Console
from rich import box

console = Console()

async def generate_subdomains(domain: str) -> list[str]:
    """智能生成可能的子域名"""
    common_prefixes = [
        # 常见服务
        'www', 'mail', 'email', 'webmail', 'smtp', 'pop', 'imap', 'ftp', 'sftp',
        'ns1', 'ns2', 'dns1', 'dns2', 'mx1', 'mx2', 'pop3', 'smtp', 'admin',
        
        # 开发和测试
        'dev', 'development', 'test', 'testing', 'stage', 'staging', 'beta',
        'demo', 'sandbox', 'api', 'api-dev', 'api-test', 'api-stage',
        
        # 管理和控制
        'admin', 'administrator', 'adminer', 'webadmin', 'manage', 'manager',
        'control', 'panel', 'cp', 'cpanel', 'dashboard', 'portal',
        
        # 应用和服务
        'app', 'apps', 'application', 'web', 'service', 'services', 'cloud',
        'cdn', 'static', 'media', 'assets', 'img', 'images', 'css', 'js', 'image',
        
        # 内容管理
        'blog', 'forum', 'bbs', 'community', 'help', 'support', 'kb',
        'docs', 'documentation', 'wiki', 'news', 'store', 'shop',
        
        # 监控和状态
        'status', 'stats', 'monitor', 'monitoring', 'health', 'report',
        'reports', 'analytics', 'metrics', 'grafana', 'prometheus',
        
        # 安全相关
        'secure', 'security', 'ssl', 'vpn', 'auth', 'login', 'sso',
        'ldap', 'proxy', 'waf', 'firewall',
        
        # 区域和位置
        'eu', 'us', 'asia', 'americas', 'europe', 'local', 'internal',
        'external', 'public', 'private',
        
        # 常见环境
        'prod', 'production', 'uat', 'qa', 'preview', 'preprod',
        'pre-production', 'stg', 'staging',
        
        # 基础设施
        'git', 'svn', 'jenkins', 'build', 'ci', 'cd', 'registry',
        'docker', 'k8s', 'kubernetes', 'cluster',
        
        # 存储和数据
        'db', 'database', 'sql', 'mysql', 'postgres', 'redis', 'cache',
        'storage', 'backup', 'data', 'elasticsearch',
        
        # 其他常见
        'm', 'mobile', 'wap', 'old', 'new', 'temp', 'tmp', 'v1', 'v2',
        'legacy', 'alpha', 'omega', 'test1', 'test2'
    ]
    
    # 生成子域名列表
    subdomains = set()
    
    # 添加基本前缀
    subdomains.update(common_prefixes)
    
    # 添加环境组合
    envs = ['dev', 'test', 'stage', 'prod', 'uat']
    services = ['api', 'admin', 'app', 'portal', 'cdn']
    for env in envs:
        for service in services:
            subdomains.add(f"{env}-{service}")
            subdomains.add(f"{service}-{env}")
    
    # 添加数字组合
    for prefix in ['test', 'dev', 'srv', 'server']:
        for num in range(1, 6):
            subdomains.add(f"{prefix}{num}")
    
    return list(subdomains)

async def check_subdomain(session: aiohttp.ClientSession, domain: str, subdomain: str) -> tuple[str, bool, dict]:
    """检查子域名是否存在"""
    full_domain = f"{subdomain}.{domain}"
    info = {
        'status': 'Unknown',
        'ip': [],
        'cname': [],
        'mx': [],
        'ns': [],
        'txt': [],
        'protocol': 'Unknown',
        'server': 'Unknown',
        'title': 'Unknown',
        'cert_domains': [],
        'is_alive': False,
        'discovery_method': set()
    }
    
    # DNS解析检查
    try:
        # A记录
        ips = socket.gethostbyname_ex(full_domain)[2]
        if ips:
            info['ip'] = ips
            info['is_alive'] = True
            info['discovery_method'].add('DNS-A')
        
        # 其他DNS记录
        resolver = dns.resolver.Resolver()
        
        # CNAME记录
        try:
            answers = resolver.resolve(full_domain, 'CNAME')
            info['cname'] = [str(rdata.target) for rdata in answers]
            info['discovery_method'].add('DNS-CNAME')
        except:
            pass
        
        # MX记录
        try:
            answers = resolver.resolve(full_domain, 'MX')
            info['mx'] = [str(rdata.exchange) for rdata in answers]
            info['discovery_method'].add('DNS-MX')
        except:
            pass
        
        # NS记录
        try:
            answers = resolver.resolve(full_domain, 'NS')
            info['ns'] = [str(rdata) for rdata in answers]
            info['discovery_method'].add('DNS-NS')
        except:
            pass
        
        # TXT记录
        try:
            answers = resolver.resolve(full_domain, 'TXT')
            info['txt'] = [str(rdata) for rdata in answers]
            info['discovery_method'].add('DNS-TXT')
        except:
            pass
            
    except:
        pass
    
    # HTTP(S)检查
    protocols = ['https://', 'http://']
    for protocol in protocols:
        try:
            url = f"{protocol}{full_domain}"
            async with session.get(url, timeout=5, allow_redirects=True) as response:
                if response.status in [200, 301, 302, 401, 403]:
                    info['status'] = response.status
                    info['protocol'] = protocol.rstrip('://')
                    info['server'] = response.headers.get('server', 'Unknown')
                    info['title'] = await extract_title(response)
                    info['is_alive'] = True
                    info['discovery_method'].add('HTTP')
                    
                    # 检查SSL证书中的域名
                    if protocol == 'https://':
                        try:
                            cert = await get_ssl_cert(full_domain)
                            if cert:
                                cert_domains = get_cert_domains(cert)
                                info['cert_domains'] = cert_domains
                                info['discovery_method'].add('SSL')
                        except:
                            pass
                    break
        except:
            continue
    
    # 转换discovery_method为列表以便JSON序列化
    info['discovery_method'] = list(info['discovery_method'])
    
    return full_domain, info['is_alive'], info

async def extract_title(response) -> str:
    """从响应中提取网页标题"""
    try:
        if 'text/html' in response.headers.get('content-type', ''):
            content = await response.text()
            if '<title>' in content.lower():
                title = content.lower().split('<title>')[1].split('</title>')[0]
                return title.strip()
    except:
        pass
    return 'No title'

async def get_ssl_cert(domain: str) -> str:
    """获取域名的SSL证书"""
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain, 443))
            cert = s.getpeercert(binary_form=True)
            return ssl.DER_cert_to_PEM_cert(cert)
    except:
        return None

def get_cert_domains(cert_pem: str) -> list[str]:
    """从SSL证书中提取所有域名"""
    try:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
        domains = []
        
        # 获取主域名
        subject = cert.get_subject()
        if hasattr(subject, 'CN'):
            domains.append(subject.CN)
        
        # 获取SAN扩展中的域名
        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            if ext.get_short_name() == b'subjectAltName':
                san = str(ext)
                for domain in san.split(','):
                    if 'DNS:' in domain:
                        domains.append(domain.split('DNS:')[1].strip())
        
        return list(set(domains))
    except:
        return []

async def smart_subdomains(domain: str):
    """智能子域名枚举（无需字典）"""
    console.print(f"\n[bold blue]正在智能枚举 {domain} 的子域名...[/]")
    
    try:
        with Progress() as progress:
            # 第一阶段：生成子域名列表
            task1 = progress.add_task("[cyan]生成子域名列表...", total=1)
            subdomains = await generate_subdomains(domain)
            progress.update(task1, completed=1)
            
            # 第二阶段：检查子域名
            total = len(subdomains)
            task2 = progress.add_task(
                f"[cyan]正在检查 {total} 个子域名...", 
                total=total
            )
            
            async with aiohttp.ClientSession() as session:
                sem = asyncio.Semaphore(10)
                async def bounded_check(subdomain):
                    async with sem:
                        result = await check_subdomain(session, domain, subdomain)
                        progress.update(task2, advance=1)
                        if result[1]:  # 如果发现有效子域名
                            methods = ', '.join(result[2]['discovery_method'])
                            progress.print(f"[green]发现: {result[0]} ({methods})[/]")
                        return result
                
                tasks = [bounded_check(subdomain) for subdomain in subdomains]
                results = await asyncio.gather(*tasks)
            
            # 过滤有效结果
            valid_results = [(domain, info) for domain, exists, info in results if exists]
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = Path(f"scan_results/subdomains_{timestamp}.txt")
            result_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(result_file, "w", encoding="utf-8") as f:
                f.write(f"子域名枚举结果 - {domain}\n")
                f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 60 + "\n\n")
                
                for subdomain, info in valid_results:
                    f.write(f"子域名: {subdomain}\n")
                    f.write(f"发现方式: {', '.join(info['discovery_method'])}\n")
                    
                    if info['ip']:
                        f.write(f"IP地址: {', '.join(info['ip'])}\n")
                    if info['protocol'] != 'Unknown':
                        f.write(f"协议: {info['protocol']}\n")
                        f.write(f"状态码: {info['status']}\n")
                        f.write(f"服务器: {info['server']}\n")
                        f.write(f"网页标题: {info['title']}\n")
                    if info['cname']:
                        f.write(f"CNAME记录: {', '.join(info['cname'])}\n")
                    if info['mx']:
                        f.write(f"MX记录: {', '.join(info['mx'])}\n")
                    if info['ns']:
                        f.write(f"NS记录: {', '.join(info['ns'])}\n")
                    if info['txt']:
                        f.write(f"TXT记录: {', '.join(info['txt'])}\n")
                    if info['cert_domains']:
                        f.write(f"证书中的域名: {', '.join(info['cert_domains'])}\n")
                    
                    f.write("-" * 40 + "\n")
            
            # 显示表格
            table = Table(
                title=f"子域名枚举结果 ({domain})",
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                box=box.SQUARE
            )
            
            table.add_column("子域名", style="cyan", justify="left", width=40)
            table.add_column("发现方式", style="green", justify="center")
            table.add_column("IP地址", style="yellow", justify="left", width=30)
            table.add_column("其他信息", style="magenta", justify="left", width=40)
            
            for subdomain, info in valid_results:
                other_info = []
                if info['protocol'] != 'Unknown':
                    other_info.append(f"{info['protocol']}://{subdomain}")
                if info['server'] != 'Unknown':
                    other_info.append(f"Server: {info['server']}")
                if info['title'] != 'Unknown':
                    other_info.append(f"Title: {info['title']}")
                
                table.add_row(
                    subdomain,
                    ', '.join(info['discovery_method']),
                    ', '.join(info['ip']) if info['ip'] else 'N/A',
                    '\n'.join(other_info) if other_info else 'N/A'
                )
            
            console.print("\n")
            console.print(table)
            console.print(f"\n[green]枚举完成！发现 {len(valid_results)} 个子域名[/]")
            console.print(f"[blue]结果已保存到: {result_file}[/]")
        
    except Exception as e:
        console.print(f"[red]枚举出错: {str(e)}[/]") 