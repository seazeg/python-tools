#!/usr/bin/env python3
"""网站结构爬取模块"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathlib import Path
from datetime import datetime
import json
import random
from rich.console import Console
from rich.tree import Tree
from rich.progress import Progress
import xml.etree.ElementTree as ET
import re
import os
from rich.prompt import Prompt

console = Console()

class SiteMapper:
    """网站结构爬取器"""
    
    def __init__(self, url: str, max_requests: int = None):
        self.start_url = url
        self.domain = urlparse(url).netloc
        self.visited_urls = set()
        self.site_structure = {}
        self.session = None
        self.max_requests = max_requests if max_requests is not None else self.calculate_max_requests()
        self.request_count = 0
        self.progress = None
        self.crawl_task = None
        self.total_urls = 0
        self.current_phase = ""
        self.semaphore = None  # 并发控制
        self.max_concurrent = 10  # 最大并发数
        
        # 防止递归的集合
        self.normalized_urls = set()  # 标准化后的URL集合
        
        # 请求头
        self.headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def calculate_max_requests(self) -> int:
        """智能计算最大请求数"""
        base_limit = 1000  # 基础限制
        
        # 根据域名类型调整
        if any(edu_domain in self.domain for edu_domain in ['.edu.', '.edu.cn', '.ac.']):
            base_limit = 2000  # 教育网站通常内容更多
        elif any(gov_domain in self.domain for gov_domain in ['.gov.', '.gov.cn']):
            base_limit = 1500  # 政府网站
        elif '.org' in self.domain:
            base_limit = 1200  # 组织机构网站
        
        # 可以通过环境变量覆盖
        env_limit = os.getenv('HAT_MAX_REQUESTS')
        if env_limit and env_limit.isdigit():
            return int(env_limit)
        
        return base_limit

    def normalize_url(self, url: str) -> str:
        """标准化URL，移除查询参数和片段，处理路径中的 . 和 .."""
        parsed = urlparse(url)
        path = parsed.path
        
        # 处理路径中的 . 和 ..
        parts = []
        for part in path.split('/'):
            if part == '.' or not part:
                continue
            elif part == '..':
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        
        clean_path = '/' + '/'.join(parts)
        return f"{parsed.scheme}://{parsed.netloc}{clean_path}"

    def should_crawl_url(self, url: str) -> bool:
        """检查URL是否应该被爬取"""
        # 检查是否超过最大请求数
        if self.request_count >= self.max_requests:
            return False
            
        # 标准化URL
        normalized = self.normalize_url(url)
        
        # 检查是否已访问
        if normalized in self.normalized_urls:
            return False
            
        # 检查域名
        if urlparse(url).netloc != self.domain:
            return False
            
        # 检查文件类型
        ignored_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', 
                            '.ico', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar'}
        if any(url.lower().endswith(ext) for ext in ignored_extensions):
            return False
            
        # 检查URL长度
        if len(url) > 255:  # 防止异常长URL
            return False
            
        # 检查循环路径
        path_parts = urlparse(url).path.split('/')
        if len(path_parts) > 10 or len(set(path_parts)) < len(path_parts) / 2:
            return False
            
        return True

    async def check_robots_txt(self):
        """检查robots.txt"""
        self.current_phase = "检查robots.txt"
        self.progress.print(f"[blue]正在{self.current_phase}...")
        
        robots_url = urljoin(self.start_url, '/robots.txt')
        try:
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    text = await response.text()
                    sitemap_urls = []
                    for line in text.split('\n'):
                        if line.lower().startswith('sitemap:'):
                            sitemap_url = line.split(':', 1)[1].strip()
                            sitemap_urls.append(sitemap_url)
                    if sitemap_urls:
                        self.progress.print(f"[green]发现 {len(sitemap_urls)} 个sitemap文件")
                    return sitemap_urls
                else:
                    self.progress.print("[yellow]未找到robots.txt")
        except Exception as e:
            self.progress.print(f"[yellow]获取robots.txt失败: {str(e)}")
        return []
    
    async def parse_sitemap(self, url: str):
        """解析sitemap"""
        self.current_phase = "解析Sitemap"
        self.progress.print(f"[blue]正在解析Sitemap: {url}")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    root = ET.fromstring(text)
                    namespace = {'ns': root.tag.split('}')[0].strip('{')}
                    urls = []
                    
                    if 'sitemapindex' in root.tag:
                        sitemaps = root.findall('.//ns:loc', namespace)
                        self.progress.print(f"[green]发现 {len(sitemaps)} 个子Sitemap")
                        for sitemap in sitemaps:
                            sub_urls = await self.parse_sitemap(sitemap.text)
                            urls.extend(sub_urls)
                    else:
                        url_elements = root.findall('.//ns:loc', namespace)
                        urls = [url_elem.text for url_elem in url_elements]
                        self.progress.print(f"[green]从Sitemap中提取到 {len(urls)} 个URL")
                    return urls
        except Exception as e:
            self.progress.print(f"[yellow]解析sitemap失败 {url}: {str(e)}")
        return []
    
    async def crawl_page(self, url: str):
        """爬取单个页面"""
        if not self.should_crawl_url(url):
            return []
        
        self.request_count += 1
        self.visited_urls.add(url)
        self.normalized_urls.add(self.normalize_url(url))
        
        try:
            async with self.semaphore:  # 使用信号量控制并发
                async with self.session.get(url, headers=self.headers, timeout=30) as response:
                    status = response.status
                    if status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        if 'text/html' not in content_type.lower():
                            self.progress.update(self.crawl_task, advance=1)
                            return []
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 更新结构
                        path_parts = urlparse(url).path.strip('/').split('/')
                        current_dict = self.site_structure
                        for part in path_parts:
                            if part:
                                if part not in current_dict:
                                    current_dict[part] = {
                                        '_info': {
                                            'url': url,
                                            'title': soup.title.string.strip() if soup.title else '',
                                            'status': status,
                                            'content_type': content_type,
                                        },
                                        '_children': {}
                                    }
                                current_dict = current_dict[part]['_children']
                        
                        # 提取链接
                        links = []
                        for a in soup.find_all('a', href=True):
                            link = urljoin(url, a['href'])
                            if urlparse(link).netloc == self.domain:
                                links.append(link)
                        
                        if links:
                            self.progress.print(f"[green]发现 {len(links)} 个新链接 <- {url}")
                        
                        self.progress.update(self.crawl_task, advance=1)
                        return links
                    else:
                        self.progress.print(f"[yellow]状态码 {status} <- {url}")
                        self.progress.update(self.crawl_task, advance=1)
                        
        except Exception as e:
            self.progress.print(f"[yellow]爬取失败 {url}: {str(e)}")
            self.progress.update(self.crawl_task, advance=1)
        
        return []
    
    async def process_url_batch(self, urls: set):
        """并发处理一批URL"""
        tasks = []
        for url in urls:
            if self.should_crawl_url(url):
                tasks.append(self.crawl_page(url))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            new_urls = set()
            for result in results:
                if isinstance(result, list):  # 忽略异常结果
                    new_urls.update(result)
            return new_urls
        return set()

    async def crawl(self):
        """开始爬取"""
        with Progress() as progress:
            self.progress = progress
            self.semaphore = asyncio.Semaphore(self.max_concurrent)
            
            # 添加总进度条
            overall_task = progress.add_task(
                "[bold blue]总进度...", 
                total=None,
                visible=False
            )
            
            # 添加当前阶段进度条
            self.crawl_task = progress.add_task(
                "[cyan]爬取中...",
                total=None,
                visible=False
            )
            
            async with aiohttp.ClientSession() as session:
                self.session = session
                
                # 检查sitemap
                progress.print("[bold blue]阶段1: 检查网站配置")
                sitemap_urls = await self.check_robots_txt()
                urls_to_crawl = set()
                
                if sitemap_urls:
                    progress.print("[bold blue]阶段2: 解析Sitemap")
                    for sitemap_url in sitemap_urls:
                        urls = await self.parse_sitemap(sitemap_url)
                        urls_to_crawl.update(urls)
                
                # 添加起始URL
                urls_to_crawl.add(self.start_url)
                self.total_urls = len(urls_to_crawl)
                
                # 更新进度条
                progress.update(self.crawl_task, 
                              total=self.total_urls,
                              visible=True,
                              description="[cyan]正在爬取页面...")
                
                progress.print(f"[bold blue]阶段3: 开始爬取 ({self.total_urls} 个起始URL)")
                
                # 分批处理URL
                while urls_to_crawl and self.request_count < self.max_requests:
                    # 取出一批URL进行处理
                    batch_size = min(self.max_concurrent * 2, len(urls_to_crawl))
                    current_batch = set()
                    for _ in range(batch_size):
                        if urls_to_crawl:
                            current_batch.add(urls_to_crawl.pop())
                    
                    # 并发处理这批URL
                    new_urls = await self.process_url_batch(current_batch)
                    
                    # 更新待爬取的URL集合
                    valid_new_urls = {url for url in new_urls 
                                    if self.should_crawl_url(url)}
                    urls_to_crawl.update(valid_new_urls)
                    
                    # 更新总进度
                    self.total_urls += len(valid_new_urls)
                    progress.update(self.crawl_task, total=self.total_urls)
                    
                    # 添加小延迟避免请求过快
                    await asyncio.sleep(0.1)
                
                progress.print("[bold green]爬取完成!")

def generate_tree_view(structure, tree=None, prefix=''):
    """生成树形视图"""
    if tree is None:
        tree = Tree("📁 根目录")
    
    for name, data in structure.items():
        if name != '_info' and name != '_children':
            node = tree.add(f"{'📁' if data.get('_children') else '📄'} {name}")
            if '_info' in data:
                info = data['_info']
                node.add(f"🔗 {info['url']}")
                if info['title']:
                    node.add(f"📝 {info['title']}")
            
            if '_children' in data:
                generate_tree_view(data['_children'], node, prefix + '  ')
    
    return tree 

def generate_html_report(url: str, structure: dict, visited_urls: set, timestamp: str, max_requests: int) -> str:
    """生成HTML格式的报告"""
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>网站结构报告 - {url}</title>
        <style>
            :root {{
                --primary-color: #2196F3;
                --success-color: #4CAF50;
                --warning-color: #FFC107;
                --danger-color: #F44336;
                --text-color: #333;
                --border-color: #ddd;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background: #f8f9fa;
                color: var(--text-color);
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid var(--border-color);
            }}
            
            .header h1 {{
                color: var(--primary-color);
                margin-bottom: 10px;
            }}
            
            .stats {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                border: 1px solid var(--border-color);
            }}
            
            .stats h2 {{
                color: var(--primary-color);
                margin-top: 0;
            }}
            
            .tree-container {{
                margin: 30px 0;
                padding: 20px;
                border: 1px solid var(--border-color);
                border-radius: 8px;
            }}
            
            .tree {{
                list-style: none;
                padding-left: 25px;
                margin: 0;
            }}
            
            .tree li {{
                position: relative;
                padding: 8px 0;
                border-left: 1px solid var(--border-color);
            }}
            
            .tree li::before {{
                content: "";
                position: absolute;
                left: -20px;
                top: 15px;
                width: 15px;
                height: 1px;
                background: var(--border-color);
            }}
            
            .tree li:last-child {{
                border-left: none;
            }}
            
            .folder {{
                color: var(--primary-color);
                font-weight: 600;
                cursor: pointer;
            }}
            
            .file {{
                color: var(--success-color);
            }}
            
            .url {{
                color: #666;
                font-size: 0.9em;
                margin-left: 15px;
                text-decoration: none;
                transition: color 0.2s;
            }}
            
            .url:hover {{
                color: var(--primary-color);
                text-decoration: underline;
            }}
            
            .title {{
                color: #9C27B0;
                font-style: italic;
                margin-left: 15px;
            }}
            
            .timestamp {{
                color: #666;
                font-size: 0.9em;
            }}
            
            .visited-urls {{
                margin-top: 30px;
                padding: 20px;
                border: 1px solid var(--border-color);
                border-radius: 8px;
            }}
            
            .visited-urls h2 {{
                color: var(--primary-color);
                margin-top: 0;
            }}
            
            .visited-urls ul {{
                list-style: none;
                padding: 0;
            }}
            
            .visited-urls li {{
                padding: 8px 0;
                border-bottom: 1px solid var(--border-color);
            }}
            
            .visited-urls li:last-child {{
                border-bottom: none;
            }}
            
            .visited-urls a {{
                color: #666;
                text-decoration: none;
                transition: color 0.2s;
            }}
            
            .visited-urls a:hover {{
                color: var(--primary-color);
                text-decoration: underline;
            }}
            
            /* 添加响应式支持 */
            @media (max-width: 768px) {{
                .container {{
                    padding: 15px;
                }}
                
                .tree {{
                    padding-left: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>网站结构报告</h1>
                <p>目标网站: <a href="{url}" target="_blank">{url}</a></p>
                <p class="timestamp">生成时间: {timestamp}</p>
            </div>
            
            <div class="stats">
                <h2>统计信息</h2>
                <p>总计爬取页面数: {total_pages}</p>
                <p>最大请求限制: {max_requests}</p>
            </div>
            
            <div class="tree-container">
                <h2>网站结构</h2>
                {tree_html}
            </div>
            
            <div class="visited-urls">
                <h2>已爬取的URL列表</h2>
                <ul>
                    {urls_list}
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    def generate_tree_html(structure: dict, level: int = 0) -> str:
        """递归生成树形结构的HTML"""
        html = ['<ul class="tree">']
        for name, data in structure.items():
            if name not in ('_info', '_children'):
                info = data.get('_info', {})
                is_folder = bool(data.get('_children'))
                
                item_html = f'<li><span class="{"folder" if is_folder else "file"}">{name}</span>'
                if info:
                    item_html += f'<a href="{info["url"]}" class="url" target="_blank">{info["url"]}</a>'
                    if info.get('title'):
                        item_html += f'<span class="title">{info["title"]}</span>'
                
                if is_folder:
                    item_html += generate_tree_html(data['_children'], level + 1)
                
                item_html += '</li>'
                html.append(item_html)
        
        html.append('</ul>')
        return '\n'.join(html)
    
    # 生成URL列表HTML，添加可点击链接
    urls_list_html = '\n'.join(
        f'<li><a href="{url}" target="_blank">{url}</a></li>' 
        for url in sorted(visited_urls)
    )
    
    # 生成完整的HTML报告
    report_html = html_template.format(
        url=url,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_pages=len(visited_urls),
        max_requests=max_requests,  # 使用传入的参数
        tree_html=generate_tree_html(structure),
        urls_list=urls_list_html
    )
    
    return report_html 

async def crawl_site_structure(url: str):
    """爬取网站结构入口函数"""
    console.print(f"\n[bold blue]开始爬取网站结构: {url}[/]")
    
    # 获取用户输入的最大请求数
    suggested_max = calculate_suggested_max_requests(url)
    console.print(f"[yellow]建议的最大请求数: {suggested_max}[/]")
    
    while True:
        max_requests_input = Prompt.ask(
            "请输入最大请求数",
            default=str(suggested_max),
            show_default=True
        )
        try:
            max_requests = int(max_requests_input)
            if max_requests <= 0:
                console.print("[red]请输入大于0的数字[/]")
                continue
            break
        except ValueError:
            console.print("[red]请输入有效的数字[/]")
    
    mapper = SiteMapper(url, max_requests)
    await mapper.crawl()
    
    # 创建结果目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = Path(f"scan_results/structure_{timestamp}")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存JSON格式的完整结构
    with open(save_dir / "structure.json", "w", encoding="utf-8") as f:
        json.dump(mapper.site_structure, f, indent=2, ensure_ascii=False)
    
    # 生成树形视图
    tree = generate_tree_view(mapper.site_structure)
    
    # 保存文本格式的树形视图
    with open(save_dir / "structure_tree.txt", "w", encoding="utf-8") as f:
        f.write(f"网站结构报告 - {url}\n")
        f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(tree.__str__())
    
    # 生成HTML报告
    html_content = generate_html_report(
        url=url,
        structure=mapper.site_structure,
        visited_urls=mapper.visited_urls,
        timestamp=timestamp,
        max_requests=max_requests  # 传入max_requests参数
    )
    
    with open(save_dir / "report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # 显示树形结构
    console.print("\n[bold cyan]网站结构:[/]")
    console.print(tree)
    
    # 显示统计信息
    total_pages = len(mapper.visited_urls)
    console.print(f"\n[bold]爬取统计:[/]")
    console.print(f"总页面数: {total_pages}")
    console.print(f"完整报告已保存到: {save_dir}")
    console.print(f"[blue]可以在浏览器中打开 {save_dir}/report.html 查看详细报告[/]") 

def calculate_suggested_max_requests(url: str) -> int:
    """计算建议的最大请求数"""
    domain = urlparse(url).netloc
    base_limit = 1000  # 基础限制
    
    # 根据域名类型调整
    if any(edu_domain in domain for edu_domain in ['.edu.', '.edu.cn', '.ac.']):
        base_limit = 2000  # 教育网站通常内容更多
    elif any(gov_domain in domain for gov_domain in ['.gov.', '.gov.cn']):
        base_limit = 1500  # 政府网站
    elif '.org' in domain:
        base_limit = 1200  # 组织机构网站
    
    # 可以通过环境变量覆盖
    env_limit = os.getenv('HAT_MAX_REQUESTS')
    if env_limit and env_limit.isdigit():
        return int(env_limit)
    
    return base_limit 

# 修改wordlists路径
wordlist_path = Path(__file__).parent / 'wordlists' / 'dir_basic.txt' 