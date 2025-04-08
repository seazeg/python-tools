#!/usr/bin/env python3
from typing import Dict, List, Optional, Set, Tuple
import aiohttp
import json
from pathlib import Path
from datetime import datetime
import re
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import asyncio
from urllib.parse import urlparse

# 尝试导入brotli，如果不可用则跳过
try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

# 导入特征签名 (使用相对导入)
from .signatures import (
    TECH_SIGNATURES,
    JS_FRAMEWORKS,
    WEB_FRAMEWORKS,
    UI_FRAMEWORKS,
    STATE_MANAGEMENT,
    WEB_SERVERS,
    CDN_PROVIDERS,
    ANALYTICS
)

console = Console()
async def fetch_url_data(url: str) -> Optional[Dict]:
    """异步获取URL的响应数据"""
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'

    # 添加常见的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': f'gzip, deflate{", br" if HAS_BROTLI else ""}',  # 根据brotli支持情况添加br
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10, allow_redirects=True) as response:
                if response.status == 403:
                    console.print(f'[red]访问被拒绝(403)，尝试使用其他方式访问...[/]')
                    # 尝试使用不同的User-Agent
                    alt_headers = headers.copy()
                    alt_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
                    async with session.get(url, headers=alt_headers, timeout=10) as alt_response:
                        if alt_response.status == 403:
                            console.print('[red]访问仍然被拒绝，建议稍后重试[/]')
                            return None
                        headers = dict(alt_response.headers)
                        content = await alt_response.text()
                elif response.status >= 400:
                    console.print(f'[red]HTTP错误: {response.status} - {response.reason}[/]')
                    return None
                else:
                    headers = dict(response.headers)
                    content = await response.text()

                return {
                    'headers': headers,
                    'content': content,
                    'status': response.status,
                    'host': str(response.url.host),  # 主机名
                    'url': str(response.url),  # 完整URL
                }
    except aiohttp.ClientError as e:
        console.print(f'[red]网络请求错误: {str(e)}[/]')
    except asyncio.TimeoutError:
        console.print('[red]请求超时，请检查网络连接或稍后重试[/]')
    except Exception as e:
        console.print(f'[red]获取URL数据时发生错误: {str(e)}[/]')
    return None

def extract_meta_tags(content: str) -> Dict[str, str]:
    """从HTML内容中提取meta标签信息"""
    meta_tags = {}
    try:
        soup = BeautifulSoup(content, 'html.parser')
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            if name and content:
                meta_tags[name] = content
    except Exception as e:
        console.print(f'[yellow]解析meta标签时出错: {str(e)}[/]')
    return meta_tags

def detect_js_imports(content: str) -> List[str]:
    """检测JavaScript导入语句"""
    import_patterns = [
        r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
        r'require\([\'"]([^\'"]+)[\'"]\)',
    ]
    
    imports = []
    for pattern in import_patterns:
        matches = re.findall(pattern, content)
        imports.extend(matches)
    return list(set(imports))

def detect_package_json(content: str) -> Dict[str, str]:
    """尝试检测package.json内容"""
    try:
        # 查找可能的package.json内容
        match = re.search(r'\{[\s\S]*"dependencies"[\s\S]*\}', content)
        if match:
            package_data = json.loads(match.group(0))
            return package_data.get('dependencies', {})
    except:
        pass
    return {}

def detect_js_resources(content: str) -> List[str]:
    """检测页面中的JavaScript资源路径"""
    js_resources = []
    try:
        soup = BeautifulSoup(content, 'html.parser')
        
        # 检测<script>标签的src属性
        for script in soup.find_all('script', src=True):
            js_resources.append(script['src'])
            
        # 检测动态导入的JavaScript
        dynamic_imports = re.findall(r'import\([\'"]([^\'"]+)[\'"]\)', content)
        js_resources.extend(dynamic_imports)
        
        # 检测require.js的路径
        require_paths = re.findall(r'require\.config\({[^}]*paths:\s*({[^}]+})', content)
        for paths in require_paths:
            try:
                paths_dict = json.loads(paths)
                js_resources.extend(paths_dict.values())
            except:
                pass
                
    except Exception as e:
        console.print(f'[yellow]解析JavaScript资源时出错: {str(e)}[/]')
    
    return list(set(js_resources))

async def detect_js_content(content: str, response_data: Dict) -> Dict[str, List[str]]:
    """检测JavaScript内容中的技术特征"""
    js_features = {category: [] for category in TECH_SIGNATURES.keys()}
    scripts = []
    
    try:
        soup = BeautifulSoup(content, 'html.parser')
        
        # 收集外部脚本
        for script in soup.find_all('script', src=True):
            src = script['src']
            
            # 格式化脚本URL
            if src.startswith('//'):
                src = 'https:' + src
            elif not src.startswith(('http://', 'https://')):
                # 从当前URL中获取域名和协议
                current_url = response_data.get('url', '')
                if current_url:
                    parsed_url = urlparse(current_url)
                    domain = parsed_url.netloc
                    scheme = parsed_url.scheme or 'https'
                    
                    # 尝试不同的URL组合
                    urls_to_try = [
                        f"{scheme}:{src}" if src.startswith('//') else None,
                        f"{scheme}://{domain}{src if src.startswith('/') else '/' + src}",
                    ]
                    urls_to_try = [url for url in urls_to_try if url is not None]
                else:
                    urls_to_try = []
            
            console.print(f"\n[yellow]检测到外部脚本:[/]")
            console.print(f"  原始URL: [dim]{script['src']}[/]")
            
            success = False
            if src.startswith(('http://', 'https://')):
                urls_to_try = [src]
            
            for url in urls_to_try:
                try:
                    console.print(f"  尝试访问: [dim]{url}[/]")
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, allow_redirects=True, timeout=10) as response:
                            if response.status == 200:
                                script_content = await response.text()
                                scripts.append((f'外部脚本:{url}', script_content))
                                console.print(f"  [green]✓ 成功获取脚本内容[/]")
                                success = True
                                break
                except Exception as e:
                    console.print(f"  [yellow]尝试失败: {str(e)}[/]")
                    continue
            
            if not success:
                console.print(f"  [red]所有URL尝试均失败，将使用原始URL继续分析[/]")
                scripts.append((f'外部脚本:{src}', src))
        
        # 收集内联脚本和页面内容
        for i, script in enumerate(soup.find_all('script', src=False)):
            if script.string:
                scripts.append((f'内联脚本-{i+1}', script.string))
        scripts.append(('页面内容', content))
        
    except Exception as e:
        console.print(f'[yellow]解析script标签时出错: {str(e)}[/]')
        scripts = [('页面内容', content)]

    console.print("\n  [cyan]分析JavaScript特征...[/]")
    
    # 使用统一的TECH_SIGNATURES进行检测
    for category, technologies in TECH_SIGNATURES.items():
        console.print(f"\n    - 检测{category}...")
        for tech_name, tech_info in technologies.items():
            if 'patterns' in tech_info:  # 只处理有patterns的技术
                found_match = False
                for script_name, script_content in scripts:
                    for pattern in tech_info['patterns']:
                        try:
                            match = re.search(pattern, script_content, re.I)
                            if match:
                                js_features[category].append(tech_name)
                                console.print(f"      [green]✓ 在 {script_name} 中检测到 {tech_name}[/]")
                                console.print(f"        模式: {pattern}")
                                console.print(f"        匹配: {match.group(0)}")
                                found_match = True
                                break
                        except Exception as e:
                            console.print(f"      [red]正则匹配出错 ({pattern}): {str(e)}[/]")
                    if found_match:
                        break

    return {k: list(set(v)) for k, v in js_features.items() if v}

async def detect_technologies(response_data: Dict) -> Dict[str, List[str]]:
    """检测网站使用的技术"""
    detected_tech = {category: [] for category in TECH_SIGNATURES.keys()}
    content = response_data['content']
    headers = response_data['headers']
    meta_tags = extract_meta_tags(content)
    
    js_features = await detect_js_content(content, response_data)
    
    # 合并JavaScript特征到检测结果
    for category, techs in js_features.items():
        detected_tech[category].extend(techs)

    # 再进行基础特征检测
    for category, technologies in TECH_SIGNATURES.items():
        for tech_name, signatures in technologies.items():
            # 检查HTTP头
            if 'headers' in signatures:
                for header in signatures['headers']:
                    header_value = headers.get(header, '').lower()
                    if header_value and re.search(signatures['pattern'], header_value, re.I):
                        detected_tech[category].append(tech_name)
                        break

            # 检查页面内容
            if 'content' in signatures:
                if re.search(signatures['content'], content, re.I):
                    detected_tech[category].append(tech_name)

            # 检查meta标签
            if 'meta' in signatures:
                for meta_name, pattern in signatures['meta'].items():
                    meta_value = meta_tags.get(meta_name, '').lower()
                    if meta_value and re.search(pattern, meta_value, re.I):
                        detected_tech[category].append(tech_name)

    # 最后进行JavaScript资源和导入分析
    js_resources = detect_js_resources(content)
    if js_resources:
        console.print("\n[yellow]发现JavaScript资源:[/]")
        framework_keywords = {
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'svelte': 'Svelte',
            'redux': 'Redux',
            'vuex': 'Vuex',
            'mobx': 'MobX',
            'antd': 'Ant Design',
            'element-ui': 'Element UI',
            'material-ui': 'Material-UI',
            'mui': 'Material-UI',
            'jquery': 'jQuery',
            'underscore': 'Underscore.js',
            'lodash': 'Lodash',
            'fingerprintjs': 'FingerprintJS',
            'swiper': 'Swiper',
            'core-js': 'core-js',
            'pinia': 'Pinia',
            'naive-ui': 'Naive UI',
            'vant': 'Vant'
        }
        
        for resource in js_resources:
            # 格式化资源URL
            if resource.startswith('//'):
                resource = 'https:' + resource
            elif not resource.startswith(('http://', 'https://')):
                resource = f"https://{response_data.get('host', '')}{resource if resource.startswith('/') else '/' + resource}"
            
            # 打印资源路径
            console.print(f"  [dim]- {resource}[/]")
            
            # 检查资源路径中的框架关键词
            resource_lower = resource.lower()
            for keyword, framework in framework_keywords.items():
                if keyword in resource_lower:
                    if framework in ['React', 'Vue.js', 'Angular', 'Svelte']:
                        detected_tech['JavaScript框架'].append(framework)
                    elif framework in ['Redux', 'Vuex', 'MobX']:
                        detected_tech['状态管理'].append(framework)
                    elif framework in ['Ant Design', 'Element UI', 'Material-UI']:
                        detected_tech['UI框架'].append(framework)

    # JavaScript导入分析
    js_imports = detect_js_imports(content)
    if js_imports:
        console.print("\n[yellow]发现需要进一步分析的JavaScript模块:[/]")
        for imp in js_imports:
            imp_lower = imp.lower()
            if any(keyword in imp_lower for keyword in framework_keywords.keys()):
                console.print(f"  [dim]- {imp}[/]")
                # 根据导入语句检测框架
                for keyword, framework in framework_keywords.items():
                    if keyword in imp_lower:
                        if framework in ['React', 'Vue.js', 'Angular', 'Svelte']:
                            detected_tech['JavaScript框架'].append(framework)
                        elif framework in ['Redux', 'Vuex', 'MobX']:
                            detected_tech['状态管理'].append(framework)
                        elif framework in ['Ant Design', 'Element UI', 'Material-UI']:
                            detected_tech['UI框架'].append(framework)

    # 依赖项检测
    package_deps = detect_package_json(content)
    for dep_name in package_deps:
        if any(framework.lower() in dep_name.lower() for framework in ['express', 'koa', 'fastify']):
            detected_tech['Web框架'].append('Node.js')
        elif 'nuxt' in dep_name:
            detected_tech['Web框架'].append('Nuxt.js')
        elif 'next' in dep_name:
            detected_tech['Web框架'].append('Next.js')
        elif '@vue' in dep_name:
            detected_tech['JavaScript框架'].append('Vue.js')
        elif 'react' in dep_name:
            detected_tech['JavaScript框架'].append('React')
        elif '@angular' in dep_name:
            detected_tech['JavaScript框架'].append('Angular')

    return {k: list(set(v)) for k, v in detected_tech.items() if v}

def display_results(results: Dict[str, List[str]]) -> None:
    """使用rich表格显示结果"""
    table = Table(title="检测到的技术", show_header=True)
    table.add_column("类别", style="cyan")
    table.add_column("技术", style="green")
    
    for category, techs in results.items():
        if techs:
            table.add_row(category, ", ".join(techs))
    
    console.print(table)

async def analyze_tech_stack(url: str) -> Dict[str, Set[str]]:
    """分析网站技术栈"""
    tech_stack = {
        'js_frameworks': set(),
        'web_frameworks': set(),
        'ui_frameworks': set(), 
        'state_management': set(),
        'web_servers': set(),
        'cdn_providers': set(),
        'analytics': set(),
        'languages': set(),
        'databases': set(),
        'security': set()
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                # 获取响应内容
                content = await response.text()
                headers = dict(response.headers)
                
                # 1. 检测Web服务器
                tech_stack['web_servers'].update(
                    enhance_server_detection(headers, content)
                )
                
                # 2. 检测编程语言
                tech_stack['languages'].update(
                    detect_languages(headers, content)
                )
                
                # 3. 检测数据库
                tech_stack['databases'].update(
                    detect_databases(content, headers)
                )
                
                # 4. 检测安全特征
                tech_stack['security'].update(
                    detect_security_features(headers)
                )
                
                # 5. 检测CDN
                tech_stack['cdn_providers'].update(
                    detect_cdn_providers(headers, content)
                )
                
                # 6. 检测分析工具
                tech_stack['analytics'].update(
                    detect_analytics_tools(content)
                )
                
                # 7. 检测前端框架(保持原有逻辑)
                soup = BeautifulSoup(content, 'html.parser')
                scripts = extract_scripts(soup)
                
                for framework, patterns in JS_FRAMEWORKS.items():
                    if any(re.search(pattern, content) for pattern in patterns.get('patterns', [])):
                        tech_stack['js_frameworks'].add(framework)
                
                for framework, patterns in WEB_FRAMEWORKS.items():
                    if any(re.search(pattern, content) for pattern in patterns.get('patterns', [])):
                        tech_stack['web_frameworks'].add(framework)
                        
                for framework, patterns in UI_FRAMEWORKS.items():
                    if any(re.search(pattern, content) for pattern in patterns.get('patterns', [])):
                        tech_stack['ui_frameworks'].add(framework)
                        
                for framework, patterns in STATE_MANAGEMENT.items():
                    if any(re.search(pattern, content) for pattern in patterns.get('patterns', [])):
                        tech_stack['state_management'].add(framework)

        except Exception as e:
            print(f"Error analyzing {url}: {str(e)}")
            
    return tech_stack

def detect_languages(headers: Dict, content: str) -> Set[str]:
    """检测编程语言"""
    languages = set()
    
    # PHP
    if any([
        'X-Powered-By' in headers and 'php' in headers['X-Powered-By'].lower(),
        re.search(r'\.php[3-7]?$', content),
        'PHPSESSID' in headers.get('Set-Cookie', ''),
    ]):
        languages.add('PHP')
        
    # Python
    if any([
        'X-Powered-By' in headers and 'python' in headers['X-Powered-By'].lower(),
        'wsgi' in headers.get('Server', '').lower(),
        'django' in content.lower(),
        'flask' in content.lower(),
        'fastapi' in content.lower(),
    ]):
        languages.add('Python')
        
    # Java
    if any([
        'X-Powered-By' in headers and 'jsp' in headers['X-Powered-By'].lower(),
        'jsessionid' in headers.get('Set-Cookie', '').lower(),
        re.search(r'\.jsp$', content),
        'spring' in content.lower(),
    ]):
        languages.add('Java')
        
    # Node.js
    if any([
        'X-Powered-By' in headers and 'nodejs' in headers['X-Powered-By'].lower(),
        'express' in content.lower(),
        'node_modules' in content,
    ]):
        languages.add('Node.js')
        
    return languages

def detect_databases(content: str, headers: Dict) -> Set[str]:
    """检测数据库技术"""
    databases = set()
    
    # MySQL
    if any([
        'mysql' in content.lower(),
        'mysqli' in content.lower(),
        'pdo_mysql' in content.lower(),
    ]):
        databases.add('MySQL')
        
    # PostgreSQL
    if any([
        'postgresql' in content.lower(),
        'pgsql' in content.lower(),
        'postgres' in content.lower(),
    ]):
        databases.add('PostgreSQL')
        
    # MongoDB
    if any([
        'mongodb' in content.lower(),
        'mongoose' in content.lower(),
    ]):
        databases.add('MongoDB')
        
    # Redis
    if any([
        'redis' in content.lower(),
        'X-Redis-Version' in headers,
    ]):
        databases.add('Redis')
        
    return databases

def detect_security_features(headers: Dict) -> Set[str]:
    """检测安全特征"""
    security = set()
    
    # HTTPS/SSL
    if headers.get('Strict-Transport-Security'):
        security.add('HSTS')
        
    # XSS Protection
    if headers.get('X-XSS-Protection'):
        security.add('XSS Protection')
        
    # Content Security Policy
    if headers.get('Content-Security-Policy'):
        security.add('CSP')
        
    # CORS
    if headers.get('Access-Control-Allow-Origin'):
        security.add('CORS')
        
    # Frame Options
    if headers.get('X-Frame-Options'):
        security.add('Frame Protection')
        
    return security

def detect_cdn_providers(headers: Dict, content: str) -> Set[str]:
    """检测CDN提供商"""
    cdn_providers = set()
    
    for provider, signatures in CDN_PROVIDERS.items():
        # 检查头部特征
        for header, patterns in signatures.get('headers', {}).items():
            header_value = headers.get(header, '')
            if header_value and any(re.search(pattern, header_value, re.I) for pattern in patterns):
                cdn_providers.add(provider)
                break
                
        # 检查内容特征
        for pattern in signatures.get('patterns', []):
            if re.search(pattern, content, re.I):
                cdn_providers.add(provider)
                break
                
    return cdn_providers

def detect_analytics_tools(content: str) -> Set[str]:
    """检测分析工具"""
    analytics = set()
    
    for tool, patterns in ANALYTICS.items():
        if any(re.search(pattern, content, re.I) for pattern in patterns.get('patterns', [])):
            analytics.add(tool)
            
    return analytics

def extract_scripts(soup: BeautifulSoup) -> List[str]:
    """提取页面中的脚本内容"""
    scripts = []
    
    # 内联脚本
    for script in soup.find_all('script'):
        if script.string:
            scripts.append(script.string)
            
    # 外部脚本
    for script in soup.find_all('script', src=True):
        scripts.append(script['src'])
        
    return scripts

async def analyze_tech_stack(url: str) -> None:
    """分析网站技术栈的主函数"""
    console.print(f"\n[bold cyan]开始分析 {url} 的技术栈...[/]")
    
    # 获取页面数据
    console.print("[yellow]正在获取页面数据...[/]")
    response_data = await fetch_url_data(url)
    if not response_data:
        console.print("[red]获取页面数据失败，分析终止[/]")
        return
    console.print("[green]✓ 页面数据获取成功[/]")
    
    # 分析过程
    console.print("\n[yellow]开始技术检测...[/]")
    
    # 1. 检测HTTP头
    console.print("  [cyan]1. 分析HTTP响应头...[/]")
    headers = response_data['headers']
    console.print(f"    - 发现 {len(headers)} 个HTTP头")
    for key in headers.keys():
        console.print(f"    - 检测到头部: [dim]{key}[/]")
    
    # 2. 提取Meta标签
    console.print("\n  [cyan]2. 分析Meta标签...[/]")
    meta_tags = extract_meta_tags(response_data['content'])
    console.print(f"    - 发现 {len(meta_tags)} 个Meta标签")
    for name in meta_tags.keys():
        console.print(f"    - 检测到Meta标签: [dim]{name}[/]")
    
    # 3. 分析JavaScript
    console.print("\n  [cyan]3. 分析JavaScript内容...[/]")
    js_imports = detect_js_imports(response_data['content'])
    console.print(f"    - 发现 {len(js_imports)} 个JavaScript导入")
    if js_imports:
        console.print("    - 部分导入示例:")
        for imp in js_imports[:3]:  # 只显示前3个
            console.print(f"      [dim]{imp}[/]")
    
    # 4. 分析package.json
    console.print("\n  [cyan]4. 检测package.json...[/]")
    package_deps = detect_package_json(response_data['content'])
    if package_deps:
        console.print(f"    - 发现 {len(package_deps)} 个依赖项")
        console.print("    - 部分依赖示例:")
        for dep in list(package_deps.keys())[:3]:  # 只显示前3个
            console.print(f"      [dim]{dep}[/]")
    else:
        console.print("    - 未发现package.json内容")
    
    # 执行技术检测
    console.print("\n[yellow]正在整合检测结果...[/]")
    results = await detect_technologies(response_data)
    
    # 显示最终结果
    console.print("\n[bold green]检测完成![/]")
    if results:
        console.print("\n[cyan]检测结果:[/]")
        display_results(results)
        
        # 显示检测到的技术数量统计
        total_techs = sum(len(techs) for techs in results.values())
        console.print(f"\n[green]共检测到 {total_techs} 项技术，涉及 {len(results)} 个类别[/]")
    else:
        console.print("[yellow]未检测到已知的技术特征[/]")