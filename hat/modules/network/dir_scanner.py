#!/usr/bin/env python3
"""Web目录扫描模块"""

import aiohttp
import asyncio
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
from rich.progress import Progress
from rich.table import Table
from rich.console import Console
from rich import box
from typing import List, Dict, Set, Optional
import json

console = Console()

class DirScanner:
    """目录扫描器"""
    def __init__(self, url: str, concurrency: int = 50):
        self.base_url = url.rstrip('/')
        self.concurrency = concurrency
        self.results = []
        self.session = None
        self.sem = None
        # 添加模块路径
        self.module_dir = Path(__file__).parent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.retry_count = 3
        
    async def generate_wordlist(self) -> Set[str]:
        """生成智能字典"""
        paths = set()
        
        # 1. 基础目录
        wordlist_path = self.module_dir / 'wordlists' / 'dir_basic.txt'
        try:
            with open(wordlist_path) as f:
                # 过滤掉注释和空行
                paths.update(
                    line.strip() 
                    for line in f.readlines() 
                    if line.strip() and not line.startswith('#')
                )
        except FileNotFoundError:
            console.print(f"[yellow]警告: 未找到字典文件 {wordlist_path}[/]")
            # 使用内置的基础字典作为备选
            paths.update([
                'admin', 'login', 'wp-admin', 'config',
                'backup', 'test', 'upload', 'api'
            ])
            
        # 2. 敏感文件
        sensitive_files = {
            # 配置文件
            '.env', 'config.php', 'wp-config.php', 'config.yml',
            'application.properties', 'settings.py', 'database.yml',
            
            # 备份文件
            'backup.sql', 'dump.sql', 'website.bak', 'www.zip',
            '1.txt', 'test.txt', 'readme.md', 'README.md',
            
            # 日志文件
            'error.log', 'access.log', 'debug.log', 'web.log',
            
            # 版本控制
            '.git/HEAD', '.svn/entries', '.hg/store/data',
            
            # 开发文件
            'phpinfo.php', 'test.php', 'info.php', 'dev.php',
            
            # 其他敏感文件
            'robots.txt', 'sitemap.xml', 'crossdomain.xml',
            'admin.php', 'login.php', 'shell.php', 'upload.php'
        }
        paths.update(sensitive_files)
        
        # 3. 常见后缀
        extensions = ['.php', '.asp', '.aspx', '.jsp', '.html', '.bak', '.old', '.backup', '~']
        base_paths = paths.copy()
        for path in base_paths:
            for ext in extensions:
                paths.add(f"{path}{ext}")
        
        return paths

    async def check_url(self, path: str) -> Optional[Dict]:
        """增强的URL检查"""
        url = urljoin(self.base_url, path)
        for attempt in range(self.retry_count):
            try:
                async with self.sem:
                    async with self.session.get(
                        url,
                        allow_redirects=True,
                        headers=self.headers,
                        timeout=self.timeout
                    ) as resp:
                        if resp.status in [200, 201, 301, 302, 401, 403]:
                            content = await resp.read()
                            size = len(content)
                            content_type = resp.headers.get('Content-Type', '')
                            
                            # 检查是否是敏感内容
                            is_sensitive = await self.check_sensitive_content(
                                path, content, content_type, resp.headers
                            )
                            
                            return {
                                'path': path,
                                'url': url,
                                'status': resp.status,
                                'size': size,
                                'content_type': content_type,
                                'is_sensitive': is_sensitive,
                                'headers': dict(resp.headers),
                                'title': await self.extract_title(content),
                                'server': resp.headers.get('Server', ''),
                                'powered_by': resp.headers.get('X-Powered-By', '')
                            }
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if attempt == self.retry_count - 1:
                    console.print(f"[yellow]检查 {path} 时出错: {str(e)}[/]")
                break
        return None

    async def check_sensitive_content(
        self, path: str, content: bytes, 
        content_type: str, headers: dict
    ) -> bool:
        """检查是否包含敏感内容"""
        # 路径关键词检查
        sensitive_keywords = {
            'admin', 'config', 'backup', 'password', 'log',
            'secret', 'private', 'test', 'dev', 'sql', 'db',
            'phpinfo', 'shell', 'hack', 'root', 'manager'
        }
        
        if any(keyword in path.lower() for keyword in sensitive_keywords):
            return True
            
        # 内容类型检查
        sensitive_types = {
            'sql', 'backup', 'config', 'log', 'shell', 'private'
        }
        
        if any(t in content_type.lower() for t in sensitive_types):
            return True
            
        # 文件内容检查
        try:
            text = content.decode('utf-8', 'ignore').lower()
            sensitive_content = {
                'password', 'username', 'secret', 'admin',
                'root', 'mysql', 'database', 'config', 'error'
            }
            
            if any(s in text for s in sensitive_content):
                return True
        except:
            pass
            
        return False

    async def extract_title(self, content: bytes) -> str:
        """提取页面标题"""
        try:
            text = content.decode('utf-8', 'ignore')
            import re
            match = re.search(r'<title[^>]*>(.*?)</title>', text, re.I|re.S)
            if match:
                return match.group(1).strip()
        except:
            pass
        return ''

    async def scan(self) -> List[Dict]:
        """执行扫描"""
        try:
            paths = await self.generate_wordlist()
            total = len(paths)
            
            async with aiohttp.ClientSession() as session:
                self.session = session
                self.sem = asyncio.Semaphore(self.concurrency)
                
                with Progress() as progress:
                    task = progress.add_task("[cyan]扫描中...", total=total)
                    
                    async def scan_path(path: str):
                        result = await self.check_url(path)
                        progress.update(task, advance=1)
                        if result:
                            self.results.append(result)
                            # 只打印非403状态码的发现
                            if result['status'] != 403:
                                if result['is_sensitive']:
                                    progress.print(f"[red]发现敏感路径: {path} ({result['status']})[/]")
                                else:
                                    progress.print(f"[green]发现: {path} ({result['status']})[/]")
                    
                    tasks = [scan_path(path) for path in paths]
                    await asyncio.gather(*tasks)
            
            return self.results
            
        except Exception as e:
            console.print(f"[red]扫描出错: {str(e)}[/]")
            return []

    def save_results(self, results: List[Dict]):
        """保存扫描结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = Path(f"scan_results/dirb_{timestamp}")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存JSON格式
        with open(save_dir / "results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # 保存可读格式
        with open(save_dir / "results.txt", "w") as f:
            f.write(f"目录扫描结果 - {self.base_url}\n")
            f.write(f"扫描时间: {datetime.now()}\n")
            f.write("-" * 60 + "\n\n")
            
            # 敏感文件部分
            f.write("发现的敏感文件:\n")
            for r in results:
                if r['is_sensitive']:
                    f.write(f"- {r['path']} ({r['status']})\n")
                    f.write(f"  URL: {r['url']}\n")
                    f.write(f"  大小: {r['size']} bytes\n")
                    f.write(f"  类型: {r['content_type']}\n\n")
            
            # 其他文件部分
            f.write("\n其他发现的路径:\n")
            for r in results:
                if not r['is_sensitive']:
                    f.write(f"- {r['path']} ({r['status']})\n")

async def smart_dirb(url: str):
    """智能目录扫描入口函数"""
    console.print(f"\n[bold blue]开始扫描 {url} 的目录结构...[/]")
    
    scanner = DirScanner(url)
    results = await scanner.scan()
    
    # 只过滤状态码为200的结果
    results_200 = [r for r in results if r['status'] == 200]
    
    if results_200:
        # 显示结果表格
        table = Table(
            title=f"目录扫描结果 ({url}) - 仅显示200状态码",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        table.add_column("路径", style="cyan")
        table.add_column("大小", style="yellow", justify="right")
        table.add_column("类型", style="blue")
        table.add_column("敏感", style="red", justify="center")
        
        for r in sorted(results_200, key=lambda x: x['is_sensitive'], reverse=True):
            table.add_row(
                r['path'],
                f"{r['size']} bytes",
                r['content_type'].split(';')[0],
                "✓" if r['is_sensitive'] else ""
            )
        
        console.print(table)
        
        # 保存结果
        scanner.save_results(results_200)  # 只保存200状态码的结果
        console.print(f"\n[green]扫描完成! 发现 {len(results_200)} 个可访问路径[/]")
        console.print(f"[blue]结果已保存到: scan_results/dirb_*[/]")
    else:
        console.print("[yellow]未发现任何可直接访问的路径[/]") 