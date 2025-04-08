#!/usr/bin/env python3
from typing import Dict, List, Optional
import aiohttp
import json
from pathlib import Path
from datetime import datetime
import re
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import asyncio

console = Console()

# 定义技术特征
TECH_SIGNATURES = {
    'Web服务器': {
        'Apache': {'headers': ['server', 'x-powered-by'], 'pattern': r'apache'},
        'Nginx': {'headers': ['server'], 'pattern': r'nginx'},
        'IIS': {'headers': ['server'], 'pattern': r'iis|microsoft'},
    },
    'Web框架': {
        'Django': {'headers': ['x-framework'], 'pattern': r'django'},
        'Flask': {'headers': ['server'], 'pattern': r'flask'},
        'Laravel': {'headers': ['x-powered-by'], 'pattern': r'laravel'},
        'Express': {
            'headers': ['x-powered-by'],
            'pattern': r'express',
            'content': r'node_modules|express'
        },
        'Nuxt.js': {
            'content': r'nuxt|__NUXT_|_nuxt/',
            'meta': {'generator': r'nuxt'}
        },
        'Next.js': {
            'content': r'next/|__NEXT_|_next/',
            'headers': ['x-powered-by'],
            'pattern': r'next\.js'
        },
        'Spring Boot': {
            'headers': ['x-application-context'],
            'pattern': r'spring-boot'
        },
        'Ruby on Rails': {
            'headers': ['x-powered-by', 'server'],
            'pattern': r'rails|ruby'
        },
    },
    'JavaScript框架': {
        'React': {
            'content': r'react\.production\.min\.js|react-dom|__REACT_|_react'
        },
        'Vue.js': {
            'content': r'vue\.js|vue\.min\.js|__vue__|_vue'
        },
        'Angular': {
            'content': r'angular\.js|angular\.min\.js|ng-|angular-route'
        },
        'Svelte': {
            'content': r'svelte-|__SVELTE_'
        },
    },
    '数据库': {
        'MySQL': {'headers': ['x-powered-by'], 'pattern': r'mysql'},
        'PostgreSQL': {'headers': ['x-powered-by'], 'pattern': r'postgresql'},
        'MongoDB': {'headers': ['x-powered-by'], 'pattern': r'mongodb'},
        'Redis': {'headers': ['x-powered-by'], 'pattern': r'redis'},
    },
    'CDN服务': {
        'Cloudflare': {'headers': ['cf-ray', 'server'], 'pattern': r'cloudflare'},
        'Akamai': {'headers': ['server'], 'pattern': r'akamai'},
        'Fastly': {'headers': ['fastly-debug-digest'], 'pattern': r'fastly'},
        'Vercel': {'headers': ['x-vercel-id', 'server'], 'pattern': r'vercel'},
        'Netlify': {'headers': ['x-nf-request-id', 'server'], 'pattern': r'netlify'},
    },
    '构建工具': {
        'Webpack': {'content': r'webpack|__webpack_'},
        'Vite': {'content': r'vite|__vite_'},
        'Rollup': {'content': r'rollup|__rollup_'},
    },
    '状态管理': {
        'Redux': {'content': r'redux|__REDUX_'},
        'Vuex': {'content': r'vuex|__VUEX_'},
        'MobX': {'content': r'mobx|__MOBX_'},
    },
    'UI框架': {
        'Ant Design': {'content': r'antd|ant-design'},
        'Material-UI': {'content': r'@material-ui|@mui/'},
        'Tailwind CSS': {'content': r'tailwind|tailwindcss'},
        'Bootstrap': {'content': r'bootstrap\.css|bootstrap\.min\.css'},
        'Element UI': {'content': r'element-ui|element-plus'},
    }
}

async def fetch_url_data(url: str) -> Optional[Dict]:
    """异步获取URL的响应数据"""
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'

    # 添加常见的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
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
                    'host': str(response.url.host)  # 添加主机名
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

async def detect_js_content(content: str) -> Dict[str, List[str]]:
    """通过分析JavaScript内容检测技术特征"""
    js_features = {
        'Web框架': [],
        'JavaScript框架': [],
        '状态管理': [],
        'UI框架': [],
        '构建工具': []
    }
    
    # 简化的特征检测模式
    tech_patterns = {
        'JavaScript框架': {
            'React': [
                r'react\.development\.js',
                r'react\.production\.min\.js',
                r'react-dom',
                r'/react/',
                r'window\.React',
                r'ReactDOM',
            ],
            'Vue.js': [
                r'vue\.js',
                r'vue\.min\.js',
                r'vue\.runtime\.js',
                r'vue@',
                r'window\.Vue',
                r'/vue/',
            ],
            'Angular': [
                r'angular\.js',
                r'angular\.min\.js',
                r'/angular/',
                r'ng-app',
                r'ng-controller',
            ]
        },
        '状态管理': {
            'Redux': [
                r'redux\.js',
                r'redux\.min\.js',
                r'/redux/',
                r'redux-toolkit',
            ],
            'Vuex': [
                r'vuex\.js',
                r'vuex\.min\.js',
                r'/vuex/',
                r'Vuex\.Store',
            ],
            'MobX': [
                r'mobx\.js',
                r'mobx\.min\.js',
                r'/mobx/',
                r'mobx-react',
            ]
        },
        'UI框架': {
            'Ant Design': [
                r'antd\.js',
                r'antd\.min\.js',
                r'/antd/',
                r'ant-design',
                r'(?:^|[^-])(ant-(?:btn|input|form|layout|menu|modal|table|select|checkbox|radio|switch|slider|date|time|calendar|tooltip|popover|drawer|message|notification|spin|icon|tabs|steps|progress|upload|avatar|badge|card|list|tree|tag|alert|skeleton|space|divider|grid|row|col))',
                r'anticon(?:-[a-z]+)?',
                r'@ant-design/icons',
                r'@antd/',
            ],
            'Element UI': [
                r'element-ui',
                r'element-plus',
                r'/element/',
                r'el-button',
                r'el-input',
            ],
            'Material-UI': [
                r'@material-ui',
                r'@mui/',
                r'material-ui',
                r'/mui/',
            ]
        },
        '构建工具': {
            'Webpack': [
                r'webpack',
                r'__webpack_require__',
                r'webpackJsonp',
            ],
            'Vite': [
                r'vite',
                r'/@vite/',
                r'import\.meta\.hot',
            ],
            'Rollup': [
                r'rollup',
                r'__ROLLUP__',
                r'/rollup/',
            ]
        }
    }

    # 提取所有script标签和它们的src属性
    try:
        soup = BeautifulSoup(content, 'html.parser')
        scripts = []
        
        # 收集所有script标签的src
        for script in soup.find_all('script', src=True):
            src = script['src']
            # 格式化资源URL
            if src.startswith('//'):
                src = 'https:' + src
            elif not src.startswith(('http://', 'https://')):
                src = f"/script/{src}" if not src.startswith('/') else src
            
            # 打印原始和格式化后的URL，用于调试
            console.print(f"\n[yellow]检测到外部脚本:[/]")
            console.print(f"  原始URL: [dim]{script['src']}[/]")
            console.print(f"  格式化URL: [dim]{src}[/]")
            
            # 检查URL是否可访问
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(src, allow_redirects=True) as response:
                        if response.status == 200:
                            console.print(f"  [green]✓ 可以访问[/]")
                            if response.history:
                                console.print(f"  [yellow]发生重定向: {' -> '.join(str(r.url) for r in response.history)}[/]")
                            script_content = await response.text()
                            scripts.append((f'外部脚本:{src}', script_content))
                        else:
                            console.print(f"  [red]访问失败: HTTP {response.status}[/]")
                            scripts.append((f'外部脚本:{src}', src))
            except Exception as e:
                console.print(f"  [red]访问脚本出错: {str(e)}[/]")
                scripts.append((f'外部脚本:{src}', src))
        
        # 收集所有内联脚本内容
        for i, script in enumerate(soup.find_all('script', src=False)):
            if script.string:
                scripts.append((f'内联脚本-{i+1}', script.string))
                
        # 将页面内容也加入检查范围
        scripts.append(('页面内容', content))
        
    except Exception as e:
        console.print(f'[yellow]解析script标签时出错: {str(e)}[/]')
        scripts = [('页面内容', content)]

    console.print("\n  [cyan]分析JavaScript特征...[/]")
    
    # 对每个类别进行检测
    for category, technologies in tech_patterns.items():
        console.print(f"\n    - 检测{category}...")
        for tech_name, patterns in technologies.items():
            found_match = False
            for script_name, script_content in scripts:
                for pattern in patterns:
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
                    break  # 如果已经检测到这个技术，就跳过剩余的脚本检查

    return {k: list(set(v)) for k, v in js_features.items() if v}

async def detect_technologies(response_data: Dict) -> Dict[str, List[str]]:
    """检测网站使用的技术"""
    detected_tech = {category: [] for category in TECH_SIGNATURES.keys()}
    
    headers = response_data['headers']
    content = response_data['content']
    meta_tags = extract_meta_tags(content)

    # 先进行JavaScript内容分析
    js_techs = await detect_js_content(content)
    for category, techs in js_techs.items():
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
            'mui': 'Material-UI'
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

if __name__ == "__main__":
    # 测试代码
    test_url = "https://www.vmall.com/"
    asyncio.run(analyze_tech_stack(test_url))
