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

async def smart_scan_url(session: aiohttp.ClientSession, base_url: str, path: str) -> tuple[str, int, str]:
    """智能扫描单个URL"""
    url = urljoin(base_url.rstrip('/') + '/', path)
    try:
        async with session.get(url, allow_redirects=True) as response:
            size = len(await response.read())
            return path, response.status, size
    except:
        return path, 0, 0

async def smart_dirb(url: str):
    """智能目录扫描（无需字典）"""
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
                            progress.print(f"[green]发现: {path} ({result[1]})[/]")
                        return result
                
                tasks = [bounded_scan(path) for path in paths]
                results = await asyncio.gather(*tasks)
                
                # 过滤有效结果
                valid_results = [r for r in results if r[1] in [200, 201, 301, 302, 401, 403]]
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = Path(f"scan_results/dirb_{timestamp}.txt")
            result_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(result_file, "w", encoding="utf-8") as f:
                f.write(f"目录扫描结果 - {url}\n")
                f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 60 + "\n\n")
                
                for path, status, size in valid_results:
                    f.write(f"路径: {path}\n")
                    f.write(f"状态: {status}\n")
                    f.write(f"大小: {size} bytes\n")
                    f.write(f"完整URL: {urljoin(url, path)}\n")
                    f.write("-" * 40 + "\n")
            
            # 显示表格
            table = Table(
                title=f"目录扫描结果 ({url})",
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                box=box.SQUARE
            )
            
            table.add_column("路径", style="cyan", justify="left")
            table.add_column("状态码", style="green", justify="center")
            table.add_column("大小", style="yellow", justify="right")
            
            for path, status, size in valid_results:
                status_style = {
                    200: "green",
                    201: "green",
                    301: "yellow",
                    302: "yellow",
                    401: "red",
                    403: "red"
                }.get(status, "white")
                
                table.add_row(
                    path,
                    f"[{status_style}]{status}[/]",
                    f"{size} bytes"
                )
            
            console.print("\n")
            console.print(table)
            console.print(f"\n[green]扫描完成！发现 {len(valid_results)} 个有效路径[/]")
            console.print(f"[blue]结果已保存到: {result_file}[/]")
        
    except Exception as e:
        console.print(f"[red]扫描出错: {str(e)}[/]") 