# ... (目录扫描相关代码) 

import aiohttp
import asyncio
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
from rich.progress import Progress
from rich.table import Table
from rich.console import Console
from rich import box

console = Console()

async def generate_paths() -> list[str]:
    """智能生成目录和文件路径"""
    paths = set()
    
    # 常见目录
    common_dirs = [
        # 管理后台
        'admin', 'administrator', 'manage', 'manager', 'mgr', 'admin123', 'admin_login',
        'admincp', 'adminpanel', 'adminer', 'backoffice', 'backend', 'control', 'cp',
        
        # 用户相关
        'user', 'users', 'member', 'members', 'profile', 'account', 'accounts',
        'register', 'signup', 'login', 'logout', 'password', 'forgot-password',
        
        # 内容管理
        'content', 'posts', 'blog', 'news', 'article', 'articles', 'page', 'pages',
        'category', 'categories', 'tag', 'tags', 'comment', 'comments',
        
        # 系统相关
        'system', 'sys', 'core', 'app', 'api', 'apis', 'service', 'services',
        'include', 'includes', 'inc', 'function', 'functions', 'class', 'classes',
        
        # 资源相关
        'static', 'assets', 'resource', 'resources', 'public', 'uploads', 'upload',
        'files', 'file', 'images', 'img', 'css', 'js', 'javascript', 'media',
        
        # 开发相关
        'dev', 'develop', 'development', 'test', 'testing', 'demo', 'beta', 'debug',
        'tmp', 'temp', 'cache', 'log', 'logs', 'error', 'errors',
        
        # 配置相关
        'config', 'conf', 'setting', 'settings', 'option', 'options', 'preference',
        'preferences', 'setup', 'install', 'configuration',
        
        # 安全相关
        'secure', 'security', 'auth', 'authentication', 'authorize', 'certified',
        'encrypt', 'crypto', 'certificate', 'ssl', 'https',
        
        # 备份相关
        'backup', 'bak', 'old', 'new', '_bak', '_old', '_new', 'copy',
        
        # 其他常见
        'about', 'contact', 'help', 'faq', 'support', 'status', 'privacy', 'terms',
        'search', 'sitemap', 'robots.txt', '.git', '.svn', '.env', '.htaccess'
    ]
    
    # 添加基本路径
    paths.update(common_dirs)
    
    # 添加常见文件后缀
    file_extensions = ['.php', '.asp', '.aspx', '.jsp', '.html', '.htm', '.xml', '.json', '.sql', '.bak', '.old', '.txt']
    for path in list(paths):
        for ext in file_extensions:
            paths.add(f"{path}{ext}")
    
    # 添加备份文件模式
    backup_patterns = ['.bak', '.old', '.backup', '.copy', '~', '_bak', '_old']
    for path in list(paths):
        for pattern in backup_patterns:
            paths.add(f"{path}{pattern}")
    
    # 添加常见配置文件
    config_files = [
        'config.php', 'config.inc.php', 'configuration.php', 'settings.php',
        'database.php', 'db.php', 'conf.php', 'wp-config.php', 'config.xml',
        'web.config', '.env', '.htaccess', 'robots.txt', 'sitemap.xml'
    ]
    paths.update(config_files)
    
    return list(paths)

async def get_page_title(response_text: str) -> str:
    """从HTML响应中提取页面标题"""
    try:
        import re
        title_match = re.search(r'<title[^>]*>(.*?)</title>', response_text, re.I | re.S)
        if title_match:
            return title_match.group(1).strip()
    except:
        pass
    return "No title"

async def check_tech_stack(response_headers: dict, response_text: str) -> dict:
    """检测网站技术栈"""
    tech_stack = {
        'server': response_headers.get('Server', 'Unknown'),
        'framework': 'Unknown',
        'cms': 'Unknown',
        'languages': set(),
        'technologies': set()
    }
    
    # 检测服务器
    if 'nginx' in tech_stack['server'].lower():
        tech_stack['technologies'].add('Nginx')
    elif 'apache' in tech_stack['server'].lower():
        tech_stack['technologies'].add('Apache')
    
    # 检测框架和CMS
    if 'wp-content' in response_text or 'wp-includes' in response_text:
        tech_stack['cms'] = 'WordPress'
    elif 'joomla' in response_text:
        tech_stack['cms'] = 'Joomla'
    elif 'drupal' in response_text:
        tech_stack['cms'] = 'Drupal'
    
    if 'laravel' in response_text:
        tech_stack['framework'] = 'Laravel'
    elif 'django' in response_text:
        tech_stack['framework'] = 'Django'
    elif 'rails' in response_text:
        tech_stack['framework'] = 'Ruby on Rails'
    
    # 检测编程语言
    if '.php' in response_text:
        tech_stack['languages'].add('PHP')
    if '.py' in response_text:
        tech_stack['languages'].add('Python')
    if '.rb' in response_text:
        tech_stack['languages'].add('Ruby')
    if '.js' in response_text:
        tech_stack['languages'].add('JavaScript')
    
    # 检测其他技术
    if 'jquery' in response_text.lower():
        tech_stack['technologies'].add('jQuery')
    if 'bootstrap' in response_text.lower():
        tech_stack['technologies'].add('Bootstrap')
    if 'react' in response_text.lower():
        tech_stack['technologies'].add('React')
    if 'vue' in response_text.lower():
        tech_stack['technologies'].add('Vue.js')
    
    return tech_stack

async def check_security_headers(response_headers: dict) -> dict:
    """检查安全相关的HTTP头"""
    security_headers = {
        'X-Frame-Options': response_headers.get('X-Frame-Options', 'Not Set'),
        'X-XSS-Protection': response_headers.get('X-XSS-Protection', 'Not Set'),
        'X-Content-Type-Options': response_headers.get('X-Content-Type-Options', 'Not Set'),
        'Content-Security-Policy': response_headers.get('Content-Security-Policy', 'Not Set'),
        'Strict-Transport-Security': response_headers.get('Strict-Transport-Security', 'Not Set'),
        'Referrer-Policy': response_headers.get('Referrer-Policy', 'Not Set')
    }
    return security_headers

async def smart_scan_url(session: aiohttp.ClientSession, base_url: str, path: str) -> tuple[str, int, dict]:
    """智能扫描单个URL（增强版）"""
    url = urljoin(base_url.rstrip('/') + '/', path)
    info = {
        'status': 0,
        'size': 0,
        'title': 'Unknown',
        'tech_stack': {},
        'security_headers': {},
        'response_time': 0,
        'redirect_url': None
    }
    
    try:
        start_time = datetime.now()
        async with session.get(url, allow_redirects=True) as response:
            response_time = (datetime.now() - start_time).total_seconds()
            content = await response.read()
            text = content.decode('utf-8', errors='ignore')
            
            info.update({
                'status': response.status,
                'size': len(content),
                'title': await get_page_title(text),
                'tech_stack': await check_tech_stack(response.headers, text),
                'security_headers': await check_security_headers(response.headers),
                'response_time': response_time,
                'redirect_url': str(response.url) if str(response.url) != url else None
            })
            
            return path, response.status, info
    except Exception as e:
        return path, 0, info

async def smart_dirb(url: str):
    """智能目录扫描（增强版）"""
    console.print(f"\n[bold blue]正在智能扫描 {url} 的目录结构...[/]")
    
    try:
        with Progress() as progress:
            # 第一阶段：生成路径列表
            task1 = progress.add_task("[cyan]生成扫描路径...", total=1)
            paths = await generate_paths()
            total_paths = len(paths)
            progress.update(task1, completed=1)
            
            # 第二阶段：扫描路径
            task2 = progress.add_task(
                f"[cyan]正在扫描 {total_paths} 个路径...", 
                total=total_paths
            )
            
            valid_results = []
            async with aiohttp.ClientSession() as session:
                sem = asyncio.Semaphore(10)  # 限制并发请求数
                
                async def bounded_scan(path):
                    async with sem:
                        result = await smart_scan_url(session, url, path)
                        progress.update(task2, advance=1)
                        if result[1] in [200, 201, 301, 302, 401, 403]:
                            progress.print(f"[green]发现: {result[0]} ({result[1]})[/]")
                        return result
                
                tasks = [bounded_scan(path) for path in paths]
                results = await asyncio.gather(*tasks)
                
                # 过滤200状态码的结果
                valid_results = [r for r in results if r[1] == 200]
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = Path(f"scan_results/dirb_{timestamp}.txt")
            result_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(result_file, "w", encoding="utf-8") as f:
                f.write(f"目录扫描结果 - {url}\n")
                f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 60 + "\n\n")
                
                # 基本信息部分
                f.write("发现的路径:\n")
                f.write("-" * 20 + "\n")
                for path, status, info in valid_results:
                    f.write(f"路径: {path}\n")
                    f.write(f"状态: {status}\n")
                    f.write(f"大小: {info['size']} bytes\n")
                    f.write(f"响应时间: {info['response_time']:.2f}s\n")
                    f.write(f"标题: {info['title']}\n")
                    f.write(f"完整URL: {urljoin(url, path)}\n")
                    f.write("-" * 40 + "\n")
                
                # 技术栈信息部分
                f.write("\n网站技术栈信息:\n")
                f.write("-" * 20 + "\n")
                tech_info = {}
                for path, _, info in valid_results:
                    if info['tech_stack']:
                        tech = info['tech_stack']
                        # 合并所有路径的技术信息
                        tech_info['servers'] = tech_info.get('servers', set()) | {tech['server']} if tech['server'] != 'Unknown' else tech_info.get('servers', set())
                        tech_info['frameworks'] = tech_info.get('frameworks', set()) | {tech['framework']} if tech['framework'] != 'Unknown' else tech_info.get('frameworks', set())
                        tech_info['cms'] = tech_info.get('cms', set()) | {tech['cms']} if tech['cms'] != 'Unknown' else tech_info.get('cms', set())
                        tech_info['languages'] = tech_info.get('languages', set()) | tech['languages']
                        tech_info['technologies'] = tech_info.get('technologies', set()) | tech['technologies']
                
                if tech_info:
                    if tech_info.get('servers'):
                        f.write("Web服务器:\n")
                        for server in tech_info['servers']:
                            f.write(f"  - {server}\n")
                    
                    if tech_info.get('frameworks'):
                        f.write("\n框架:\n")
                        for framework in tech_info['frameworks']:
                            f.write(f"  - {framework}\n")
                    
                    if tech_info.get('cms'):
                        f.write("\nCMS系统:\n")
                        for cms in tech_info['cms']:
                            f.write(f"  - {cms}\n")
                    
                    if tech_info.get('languages'):
                        f.write("\n编程语言:\n")
                        for lang in tech_info['languages']:
                            f.write(f"  - {lang}\n")
                    
                    if tech_info.get('technologies'):
                        f.write("\n其他技术:\n")
                        for tech in tech_info['technologies']:
                            f.write(f"  - {tech}\n")
                else:
                    f.write("未检测到明确的技术栈信息\n")
                
                # 安全头信息部分
                f.write("\n安全头信息:\n")
                f.write("-" * 20 + "\n")
                for path, _, info in valid_results:
                    if info['security_headers']:
                        headers = info['security_headers']
                        f.write(f"路径: {path}\n")
                        for header, value in headers.items():
                            f.write(f"  {header}: {value}\n")
                        f.write("-" * 40 + "\n")
            
            # 显示表格
            tables = []
            
            # 基本信息表格
            basic_table = Table(
                title=f"目录扫描结果 ({url}) - 仅显示200状态码",
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                box=box.SQUARE
            )
            
            basic_table.add_column("路径", style="cyan", justify="left")
            basic_table.add_column("状态码", style="green", justify="center")
            basic_table.add_column("大小", style="yellow", justify="right")
            basic_table.add_column("响应时间", style="blue", justify="right")
            basic_table.add_column("标题", style="magenta", justify="left")
            
            for path, status, info in valid_results:
                status_style = {
                    200: "green",
                    201: "green",
                    301: "yellow",
                    302: "yellow",
                    401: "red",
                    403: "red"
                }.get(status, "white")
                
                basic_table.add_row(
                    path,
                    f"[{status_style}]{status}[/]",
                    f"{info['size']} bytes",
                    f"{info['response_time']:.2f}s",
                    info['title'][:50] + ('...' if len(info['title']) > 50 else '')
                )
            
            tables.append(basic_table)
            
            # 技术栈表格
            tech_table = Table(
                title="检测到的技术栈",
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                box=box.SQUARE
            )
            
            tech_table.add_column("路径", style="cyan", justify="left")
            tech_table.add_column("服务器", style="yellow", justify="center")
            tech_table.add_column("框架/CMS", style="green", justify="center")
            tech_table.add_column("编程语言", style="blue", justify="center")
            tech_table.add_column("其他技术", style="magenta", justify="left")
            
            for path, _, info in valid_results:
                if info['tech_stack']:
                    tech = info['tech_stack']
                    tech_table.add_row(
                        path,
                        tech['server'],
                        f"{tech['framework']}\n{tech['cms']}",
                        '\n'.join(tech['languages']),
                        '\n'.join(tech['technologies'])
                    )
            
            tables.append(tech_table)
            
            # 安全头信息表格
            security_table = Table(
                title="安全头信息",
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                box=box.SQUARE
            )
            
            security_table.add_column("路径", style="cyan", justify="left")
            security_table.add_column("X-Frame-Options", style="yellow", justify="center")
            security_table.add_column("XSS Protection", style="green", justify="center")
            security_table.add_column("CSP", style="blue", justify="center")
            security_table.add_column("HSTS", style="magenta", justify="center")
            
            for path, _, info in valid_results:
                if info['security_headers']:
                    headers = info['security_headers']
                    security_table.add_row(
                        path,
                        headers['X-Frame-Options'],
                        headers['X-XSS-Protection'],
                        'Set' if headers['Content-Security-Policy'] != 'Not Set' else 'Not Set',
                        'Set' if headers['Strict-Transport-Security'] != 'Not Set' else 'Not Set'
                    )
            
            tables.append(security_table)
            
            # 显示所有表格
            console.print("\n")
            for table in tables:
                console.print(table)
                console.print("\n")
            
            console.print(f"\n[green]扫描完成！发现 {len(valid_results)} 个可访问路径[/]")
            console.print(f"[blue]结果已保存到: {result_file}[/]")
        
    except Exception as e:
        console.print(f"[red]扫描出错: {str(e)}[/]") 