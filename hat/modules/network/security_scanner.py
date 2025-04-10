#!/usr/bin/env python3
"""安全检测模块 - 检测网站常见安全问题"""

from typing import Dict, List, Optional, Tuple
import aiohttp
import asyncio
import re
import json
from urllib.parse import urljoin, urlparse
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich import box
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

console = Console()

# 安全检测项目
SECURITY_CHECKS = {
    "安全头信息": [
        {"name": "X-Frame-Options", "description": "防止点击劫持攻击", "expected": ["DENY", "SAMEORIGIN"]},
        {"name": "X-XSS-Protection", "description": "防止跨站脚本攻击", "expected": ["1", "1; mode=block"]},
        {"name": "X-Content-Type-Options", "description": "防止MIME类型嗅探", "expected": ["nosniff"]},
        {"name": "Content-Security-Policy", "description": "内容安全策略", "expected": None},
        {"name": "Strict-Transport-Security", "description": "强制使用HTTPS", "expected": None},
        {"name": "Referrer-Policy", "description": "控制Referer头信息", "expected": None},
        {"name": "Permissions-Policy", "description": "控制浏览器功能", "expected": None},
    ],
    "信息泄露": [
        {"name": "Server", "description": "服务器信息泄露", "expected": None, "check": "server_info"},
        {"name": "X-Powered-By", "description": "技术栈信息泄露", "expected": None, "check": "tech_info"},
    ],
    "Cookie安全": [
        {"name": "HttpOnly", "description": "防止客户端脚本访问Cookie", "expected": True},
        {"name": "Secure", "description": "仅通过HTTPS传输Cookie", "expected": True},
        {"name": "SameSite", "description": "防止跨站请求伪造", "expected": ["Strict", "Lax"]},
    ]
}

# 常见漏洞检测正则表达式
VULNERABILITY_PATTERNS = {
    "SQL注入点": [
        r"id=\d+",
        r"page=\d+",
        r"category=\d+",
        r"article=\d+",
        r"user=\d+",
    ],
    "敏感文件": [
        r"\.git/",
        r"\.svn/",
        r"\.env",
        r"\.htaccess",
        r"config\.php",
        r"wp-config\.php",
        r"phpinfo\.php",
        r"config\.json",
        r"backup\.",
        r"\.bak$",
        r"\.old$",
        r"\.swp$",
    ],
    "敏感信息": [
        r"password",
        r"username",
        r"admin",
        r"root",
        r"email",
        r"phone",
        r"mobile",
        r"address",
        r"credit",
        r"token",
        r"api[_-]?key",
        r"secret",
    ]
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
                content = await response.text()
                return {
                    'url': str(response.url),
                    'status': response.status,
                    'headers': dict(response.headers),
                    'content': content,
                    'cookies': dict(response.cookies)
                }
    except Exception as e:
        console.print(f"[red]获取URL数据时出错: {str(e)}[/]")
        return None

async def check_security_headers(response_data: Dict) -> Dict[str, Dict]:
    """检查安全相关的HTTP头"""
    results = {}
    headers = response_data.get('headers', {})
    
    # 检查安全头信息
    for category, checks in SECURITY_CHECKS.items():
        if category == "安全头信息":
            for check in checks:
                header_name = check["name"]
                header_value = headers.get(header_name, "")
                
                if not header_value:
                    results[f"{header_name}"] = {
                        "status": "未设置",
                        "value": "未设置",
                        "description": f"{check['description']} - 建议设置此头部"
                    }
                elif check["expected"] is not None:
                    if isinstance(check["expected"], list):
                        if not any(exp.lower() in header_value.lower() for exp in check["expected"]):
                            results[f"{header_name}"] = {
                                "status": "警告",
                                "value": header_value,
                                "description": f"{check['description']} - 当前值不符合推荐设置 ({', '.join(check['expected'])})"
                            }
                        else:
                            results[f"{header_name}"] = {
                                "status": "通过",
                                "value": header_value,
                                "description": f"{check['description']} - 设置正确"
                            }
                    else:
                        if str(check["expected"]).lower() != header_value.lower():
                            results[f"{header_name}"] = {
                                "status": "警告",
                                "value": header_value,
                                "description": f"{check['description']} - 当前值不符合推荐设置 ({check['expected']})"
                            }
                        else:
                            results[f"{header_name}"] = {
                                "status": "通过",
                                "value": header_value,
                                "description": f"{check['description']} - 设置正确"
                            }
                else:
                    results[f"{header_name}"] = {
                        "status": "信息",
                        "value": header_value,
                        "description": f"{check['description']} - 已设置"
                    }
        
        elif category == "信息泄露":
            for check in checks:
                header_name = check["name"]
                header_value = headers.get(header_name, "")
                
                if header_value:
                    if "check" in check and check["check"] == "server_info":
                        if len(header_value) > 10 or re.search(r"\d+\.\d+\.\d+", header_value):
                            results[f"服务器信息泄露"] = {
                                "status": "警告",
                                "value": header_value,
                                "description": "服务器版本信息泄露可能被攻击者利用 - 建议隐藏或简化"
                            }
                        else:
                            results[f"服务器信息泄露"] = {
                                "status": "信息",
                                "value": header_value,
                                "description": "服务器信息已简化，风险较低"
                            }
                    elif "check" in check and check["check"] == "tech_info":
                        results[f"技术栈信息泄露"] = {
                            "status": "警告",
                            "value": header_value,
                            "description": "技术栈信息泄露可能被攻击者利用 - 建议移除此头部"
                        }
                else:
                    if "check" in check and (check["check"] == "server_info" or check["check"] == "tech_info"):
                        results[f"{check['description']}"] = {
                            "status": "通过",
                            "value": "未泄露",
                            "description": f"{check['description']} - 未发现信息泄露"
                        }
    
    # 检查Cookie安全
    cookies = response_data.get('cookies', {})
    if cookies:
        for check in SECURITY_CHECKS.get("Cookie安全", []):
            cookie_secure = all('secure' in str(cookie).lower() for cookie in cookies.values())
            cookie_httponly = all('httponly' in str(cookie).lower() for cookie in cookies.values())
            cookie_samesite = []
            
            for cookie in cookies.values():
                cookie_str = str(cookie).lower()
                if 'samesite=strict' in cookie_str:
                    cookie_samesite.append('Strict')
                elif 'samesite=lax' in cookie_str:
                    cookie_samesite.append('Lax')
                elif 'samesite=none' in cookie_str:
                    cookie_samesite.append('None')
            
            if check["name"] == "Secure":
                if cookie_secure:
                    results["Cookie Secure"] = {
                        "status": "通过",
                        "value": "已设置",
                        "description": "Cookie设置了Secure属性，只能通过HTTPS传输"
                    }
                else:
                    results["Cookie Secure"] = {
                        "status": "警告",
                        "value": "未设置",
                        "description": "Cookie未设置Secure属性，可能通过HTTP传输，存在被窃取风险"
                    }
            
            elif check["name"] == "HttpOnly":
                if cookie_httponly:
                    results["Cookie HttpOnly"] = {
                        "status": "通过",
                        "value": "已设置",
                        "description": "Cookie设置了HttpOnly属性，客户端脚本无法访问"
                    }
                else:
                    results["Cookie HttpOnly"] = {
                        "status": "警告",
                        "value": "未设置",
                        "description": "Cookie未设置HttpOnly属性，客户端脚本可以访问，存在XSS风险"
                    }
            
            elif check["name"] == "SameSite":
                if cookie_samesite:
                    if all(site in check["expected"] for site in cookie_samesite):
                        results["Cookie SameSite"] = {
                            "status": "通过",
                            "value": ", ".join(cookie_samesite),
                            "description": "Cookie设置了安全的SameSite属性，可以防止CSRF攻击"
                        }
                    else:
                        results["Cookie SameSite"] = {
                            "status": "警告",
                            "value": ", ".join(cookie_samesite),
                            "description": f"Cookie的SameSite属性不安全，建议设置为 {', '.join(check['expected'])}"
                        }
                else:
                    results["Cookie SameSite"] = {
                        "status": "警告",
                        "value": "未设置",
                        "description": "Cookie未设置SameSite属性，存在CSRF风险"
                    }
    
    return results

async def check_ssl_security(url: str) -> Dict[str, Dict]:
    """检查SSL/TLS安全配置"""
    results = {}
    parsed_url = urlparse(url)
    
    if parsed_url.scheme != 'https':
        results["HTTPS支持"] = {
            "status": "警告",
            "value": "未使用HTTPS",
            "description": "网站未使用HTTPS加密传输，存在信息泄露和中间人攻击风险"
        }
        return results
    
    results["HTTPS支持"] = {
        "status": "通过",
        "value": "已启用",
        "description": "网站使用HTTPS加密传输，基本安全"
    }
    
    # 这里可以添加更多SSL/TLS检查，如证书有效性、协议版本等
    # 但这需要更复杂的SSL库支持，此处简化处理
    
    return results

async def check_content_security(response_data: Dict) -> Dict[str, Dict]:
    """检查内容安全问题"""
    results = {}
    content = response_data.get('content', '')
    url = response_data.get('url', '')
    
    # 检查是否有明文密码字段
    if re.search(r'<input[^>]*type=[\'"]password[\'"][^>]*>', content, re.I):
        form_with_password = re.search(r'<form[^>]*>.*?<input[^>]*type=[\'"]password[\'"][^>]*>.*?</form>', content, re.I | re.S)
        if form_with_password:
            form_html = form_with_password.group(0)
            if 'https:' not in url and not re.search(r'action=[\'"]https:', form_html, re.I):
                results["密码表单安全"] = {
                    "status": "警告",
                    "value": "HTTP明文传输",
                    "description": "发现密码表单在非HTTPS页面，密码可能以明文形式传输"
                }
            else:
                results["密码表单安全"] = {
                    "status": "通过",
                    "value": "HTTPS加密传输",
                    "description": "密码表单使用HTTPS加密传输"
                }
    
    # 检查是否有内联脚本
    inline_scripts = re.findall(r'<script[^>]*>.*?</script>', content, re.I | re.S)
    if inline_scripts:
        results["内联脚本"] = {
            "status": "信息",
            "value": f"发现{len(inline_scripts)}个内联脚本",
            "description": "内联脚本可能增加XSS风险，建议使用外部脚本并配合CSP"
        }
    
    # 检查是否有潜在的XSS漏洞点
    xss_patterns = {
        'DOM-XSS插值': r'<input[^>]*value=[\'"][^"\']*\$\{.*?\}[^"\']*[\'"]',
        '事件处理XSS': r'<[^>]*on(?:click|load|mouseover|error|keyup|change)[^=]*=[\'"][^"\']*\$\{.*?\}[^"\']*[\'"]',
        '不安全的DOM操作': r'document\.write\s*\(',
        '危险的eval': r'eval\s*\(',
        '不安全的定时器': r'setTimeout\s*\(\s*[\'"]',
        '不安全的定时器': r'setInterval\s*\(\s*[\'"]',
        '不安全的HTML插入': r'innerHTML\s*=',
        '不安全的HTML插入': r'outerHTML\s*='
    }
    
    xss_findings = {}
    for xss_type, pattern in xss_patterns.items():
        matches = re.finditer(pattern, content, re.I)
        for match in matches:
            if xss_type not in xss_findings:
                xss_findings[xss_type] = []
            # 获取匹配位置的上下文（前后20个字符）
            start = max(0, match.start() - 20)
            end = min(len(content), match.end() + 20)
            context = content[start:end].strip()
            xss_findings[xss_type].append({
                'code': match.group(0),
                'context': context,
                'position': match.start()
            })
    
    # 检查XSS风险
    if xss_findings:
        # 简化的表格显示
        details = []
        for xss_type, findings in xss_findings.items():
            details.append(f"\n{xss_type}:")
            for finding in findings:
                # 简化显示的代码片段，最多显示50个字符
                code = finding['code']
                if len(code) > 50:
                    code = code[:47] + "..."
                details.append(f"- 行 {finding['position']}: {code}")
        
        results["潜在XSS风险"] = {
            "status": "警告",
            "value": f"发现{sum(len(f) for f in xss_findings.values())}个风险点",
            "description": "发现以下XSS风险：\n" + "\n".join(details),
            "raw_findings": xss_findings  # 保存原始数据用于写入文件
        }

    # 检查敏感信息
    sensitive_patterns = {
        '密码字段': r'password\s*[=:]\s*[\'"][^\'"]+[\'"]',
        '用户名字段': r'username\s*[=:]\s*[\'"][^\'"]+[\'"]',
        'API密钥': r'api[_-]?key\s*[=:]\s*[\'"][^\'"]+[\'"]',
        '数据库连接': r'(?:mysql|postgresql|mongodb|redis)://[^\s<>"\']+',
        '邮箱地址': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        '手机号码': r'1[3-9]\d{9}',
        '身份证号': r'[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
        'IP地址': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        '内部路径': r'[\'"/][a-zA-Z0-9_-]+/(?:[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_-]+\.[a-zA-Z]{2,4}[\'"]'
    }
    
    sensitive_findings = {}
    for info_type, pattern in sensitive_patterns.items():
        matches = re.finditer(pattern, content, re.I)
        for match in matches:
            if info_type not in sensitive_findings:
                sensitive_findings[info_type] = []
            # 获取匹配位置的上下文（前后30个字符）
            start = max(0, match.start() - 30)
            end = min(len(content), match.end() + 30)
            context = content[start:end].strip()
            sensitive_findings[info_type].append({
                'value': match.group(0),  # 直接使用原始值，不进行打码
                'context': context,
                'position': match.start()
            })
    
    # 检查敏感信息
    if sensitive_findings:
        details = []
        for info_type, findings in sensitive_findings.items():
            details.append(f"\n{info_type}:")
            for finding in findings:
                # 显示原始值和位置
                details.append(f"- 行 {finding['position']}: {finding['value']}")
        
        results["敏感信息泄露"] = {
            "status": "警告",
            "value": f"发现{sum(len(f) for f in sensitive_findings.values())}处敏感信息",
            "description": "发现以下敏感信息：\n" + "\n".join(details),
            "raw_findings": sensitive_findings
        }
    
    return results

async def security_scan(url: str) -> None:
    """执行网站安全扫描"""
    console.print(f"[bold cyan]开始对 {url} 进行安全扫描...[/]")
    
    with Progress() as progress:
        task1 = progress.add_task("[cyan]获取网站数据...", total=1)
        task2 = progress.add_task("[green]检查安全头信息...", total=1)
        task3 = progress.add_task("[yellow]检查SSL/TLS安全...", total=1)
        task4 = progress.add_task("[magenta]检查内容安全...", total=1)
        
        # 获取网站数据
        response_data = await fetch_url_data(url)
        progress.update(task1, completed=1)
        
        if not response_data:
            console.print("[bold red]无法获取网站数据，扫描终止[/]")
            return
        
        # 检查安全头信息
        header_results = await check_security_headers(response_data)
        progress.update(task2, completed=1)
        
        # 检查SSL/TLS安全
        ssl_results = await check_ssl_security(url)
        progress.update(task3, completed=1)
        
        # 检查内容安全
        content_results = await check_content_security(response_data)
        progress.update(task4, completed=1)
    
    # 合并所有结果
    all_results = {**header_results, **ssl_results, **content_results}
    
    # 显示结果表格
    table = Table(
        title=f"安全扫描结果 - {url}",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
        box=box.SQUARE
    )
    
    table.add_column("检查项", style="cyan", justify="left")
    table.add_column("状态", style="yellow", justify="center")
    table.add_column("值", style="green", justify="left")
    table.add_column("说明", style="magenta", justify="left")
    
    # 按状态排序：警告 > 未设置 > 信息 > 通过
    def sort_key(item):
        check_name, result = item
        status = result["status"]
        if status == "警告":
            return 0
        elif status == "未设置":
            return 1
        elif status == "信息":
            return 2
        else:  # 通过
            return 3
    
    sorted_results = sorted(all_results.items(), key=sort_key)
    
    for check_name, result in sorted_results:
        status = result["status"]
        status_style = {
            "警告": "[bold red]警告[/]",
            "未设置": "[bold yellow]未设置[/]",
            "信息": "[bold blue]信息[/]",
            "通过": "[bold green]通过[/]"
        }.get(status, status)
        
        table.add_row(
            check_name,
            status_style,
            result["value"],
            result["description"]
        )
    
    console.print("\n")
    console.print(table)
    
    # 统计结果
    warning_count = sum(1 for _, result in all_results.items() if result["status"] == "警告")
    unset_count = sum(1 for _, result in all_results.items() if result["status"] == "未设置")
    info_count = sum(1 for _, result in all_results.items() if result["status"] == "信息")
    pass_count = sum(1 for _, result in all_results.items() if result["status"] == "通过")
    
    console.print(f"\n[bold]扫描统计:[/] 共 {len(all_results)} 项检查")
    console.print(f"[bold red]警告:[/] {warning_count} 项")
    console.print(f"[bold yellow]未设置:[/] {unset_count} 项")
    console.print(f"[bold blue]信息:[/] {info_count} 项")
    console.print(f"[bold green]通过:[/] {pass_count} 项")
    
    # 安全评分
    total_score = 100
    deductions = warning_count * 10 + unset_count * 5
    final_score = max(0, total_score - deductions)
    
    console.print(f"\n[bold]安全评分:[/] {final_score}/100")
    
    # 根据评分给出安全等级
    if final_score >= 90:
        security_level = "[bold green]优秀[/]"
    elif final_score >= 70:
        security_level = "[bold blue]良好[/]"
    elif final_score >= 50:
        security_level = "[bold yellow]一般[/]"
    else:
        security_level = "[bold red]较差[/]"
    
    console.print(f"[bold]安全等级:[/] {security_level}")
    
    # 保存扫描结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = Path(f"scan_results/security_{timestamp}")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存详细报告
    with open(save_dir / "detailed_report.txt", "w", encoding="utf-8") as f:
        f.write(f"安全扫描详细报告 - {url}\n")
        f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # 按类别保存结果
        categories = {
            "安全头信息": {},
            "SSL/TLS安全": {},
            "内容安全": {},
            "敏感信息": {},
            "其他问题": {}
        }
        
        for check_name, result in all_results.items():
            if "头" in check_name:
                categories["安全头信息"][check_name] = result
            elif "SSL" in check_name or "TLS" in check_name:
                categories["SSL/TLS安全"][check_name] = result
            elif "XSS" in check_name or "注入" in check_name:
                categories["内容安全"][check_name] = result
            elif "敏感" in check_name or "信息泄露" in check_name:
                categories["敏感信息"][check_name] = result
            else:
                categories["其他问题"][check_name] = result
        
        # 写入分类结果
        for category, items in categories.items():
            if items:
                f.write(f"\n{category}\n")
                f.write("-" * 40 + "\n")
                for check_name, result in items.items():
                    f.write(f"\n检查项: {check_name}\n")
                    f.write(f"状态: {result['status']}\n")
                    f.write(f"值: {result['value']}\n")
                    f.write(f"说明: {result['description']}\n")
                    
                    # 如果有原始发现数据，保存详细信息
                    if 'raw_findings' in result:
                        f.write("\n详细发现:\n")
                        for type_name, findings in result['raw_findings'].items():
                            f.write(f"\n  {type_name}:\n")
                            for finding in findings:
                                f.write(f"    位置: {finding['position']}\n")
                                if 'code' in finding:
                                    f.write(f"    代码: {finding['code']}\n")
                                if 'value' in finding:
                                    f.write(f"    值: {finding['value']}\n")
                                f.write(f"    上下文: {finding['context']}\n")
                                f.write("    " + "-" * 30 + "\n")
                    f.write("\n")
    
    # 保存JSON格式结果
    with open(save_dir / "scan_results.json", "w", encoding="utf-8") as f:
        # 移除raw_findings以避免JSON中包含过多重复数据
        clean_results = {}
        for check_name, result in all_results.items():
            clean_results[check_name] = {
                k: v for k, v in result.items() 
                if k != 'raw_findings'
            }
        json.dump(clean_results, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[blue]完整报告已保存到: {save_dir}[/]") 