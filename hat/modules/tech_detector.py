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

# 定义统一的技术特征
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
            'patterns': [
                r'express(?:\.min)?\.js',
                r'node_modules/express',
                r'require\([\'"]express[\'"]\)',
                r'app\.(?:get|post|put|delete|use|listen)',
            ]
        },
        'Nuxt.js': {
            'patterns': [
                r'(?:^|/)_nuxt/',                                    # Nuxt资源目录
                r'(?:^|/)__nuxt/',                                   # Nuxt生成目录
                r'(?:^|/)nuxt(?:\.min)?\.js$',                      # Nuxt主文件
                r'window\.__NUXT__',                                # Nuxt状态
                r'<div\s+id="__nuxt"(?:\s|>)',                     # Nuxt根元素
                r'(?:^|[^\w-])@nuxt/[a-z-]+',                      # Nuxt官方包
                r'(?:^|[^\w-])nuxt-(?:link|child|layout|view|loading|error|progress|build|start|generate)', # Nuxt组件和命令
                r'import\s+[{}\s\w]+\s+from\s+[\'"]@nuxt/',        # Nuxt导入
                r'extends:\s*[\'"]@nuxt/',                         # Nuxt配置继承
                r'modules:\s*\[\s*[\'"]@nuxt/',                    # Nuxt模块配置
            ]
        },
        'Next.js': {
            'patterns': [
                r'(?:^|/)_next/',                                   # Next资源目录
                r'(?:^|/)__next/',                                  # Next生成目录
                r'(?:^|/)next(?:\.min)?\.js$',                     # Next主文件
                r'window\.__NEXT_DATA__',                          # Next状态
                r'<div\s+id="__next"(?:\s|>)',                    # Next根元素
                r'(?:^|[^\w-])@next/[a-z-]+',                     # Next官方包
                r'(?:^|[^\w-])next-(?:link|router|head|script|image|auth|seo|sitemap|mdx|transpile-modules)', # Next组件和工具
                r'import\s+[{}\s\w]+\s+from\s+[\'"]next/',        # Next导入
                r'config\s*=\s*{\s*[\'"]next[\'"]',               # Next配置
                r'getStaticProps|getServerSideProps|getInitialProps', # Next数据获取
            ]
        }
    },
    'JavaScript框架': {
        'React': {
            'patterns': [
                r'react(?:\.production)?(?:\.min)?\.js',
                r'react-dom(?:\.production)?(?:\.min)?\.js',
                r'window\.React|ReactDOM\.render',
                r'(?:^|\s)React\.createElement',
                r'(?:^|\s)React\.Component',
                r'_jsx|_jsxs|_jsxDEV',
                r'useState|useEffect|useContext|useRef|useMemo|useCallback',
                r'@react-|react-router|react-redux',
            ]
        },
        'Vue.js': {
            'patterns': [
                r'vue(?:\.runtime)?(?:\.esm)?(?:\.min)?\.js',
                r'window\.Vue|Vue\.createApp',
                r'new\s+Vue\(',
                r'v-(?:if|for|model|bind|on|show|html|text|slot)',
                r'@vue/|vue-router|vuex',
                r'defineComponent|onMounted',
                r'<template>[\s\S]*</template>',
                r'\.vue$|vue-loader',
            ]
        },
        'Angular': {
            'patterns': [
                r'angular(?:\.min)?\.js',
                r'@angular/core',
                r'@Component|@Injectable|@NgModule',
                r'ngOnInit|ngOnDestroy|ngAfterViewInit',
                r'@angular/(?:common|platform-browser|forms)',
                r'ng-(?:controller|app|model|bind|repeat|if|show|hide)',
                r'angular-route(?:\.min)?\.js',
                r'zone\.js|rxjs',
            ]
        }
    },
    '构建工具': {
        'Webpack': {
            'patterns': [
                r'(?:window\.|var\s+)__webpack_(?:require|modules|jsonp)',
                r'webpack(?:\.runtime|\.bundle)?\.js',
                r'webpackChunk|webpackJsonp',
                r'webpack_require\(.+?\)',
                r'webpack-dev-server',
                r'webpack-hot-middleware',
                r'/webpack(?:-[^/]+)?\.js(?:on)?$',
                r'webpack\.config\.[jt]s',
            ]
        },
        'Vite': {
            'patterns': [
                r'/@vite/client',
                r'/vite/dist/',
                r'vite\.config\.[jt]s',
                r'import\.meta\.(?:hot|env\.MODE)',
                r'__vite_(?:hmr|ssr)',
                r'vite-plugin-[a-z-]+',
                r'\.vite/',
                r'@vitejs/plugin-',
            ]
        },
        'Rollup': {
            'patterns': [
                r'rollup(?:\.(?:config|browser))\.js',
                r'__ROLLUP_(?:ASSET|CHUNK)_[A-Z_]+__',
                r'rollup-plugin-[a-z-]+',
                r'\.rollup\.js$',
                r'@rollup/[a-z-]+',
                r'\.rolluprc(?:\.[a-z]+)?$',
                r'import\.meta\.ROLLUP_',
            ]
        }
    },
    'JavaScript库': {
        'jQuery': {
            'patterns': [
                r'jquery(?:\.min)?\.js',
                r'jquery-\d+\.\d+\.\d+',
                r'window\.jQuery',
                r'\$\(document\)',
                r'jquery(?:ui|mobile|validate|form|lightbox|fancybox|slick|datepicker)',
            ]
        },
        'Underscore.js': {
            'patterns': [
                r'(?:^|/)underscore(?:\.min)?\.js',                    # 文件名匹配
                r'(?:^|[^\w.])_\.(?:VERSION|noConflict)\b',           # 特有API
                r'(?:^|[^\w.])_\.templateSettings\b',                  # 模板设置
                r'(?:^|[^\w.])require\([\'"]underscore[\'"]\)',       # CommonJS引入
                r'import\s+[{_}\s]+from\s+[\'"]underscore[\'"]',      # ES6引入
                r'underscore/modules/',                                # 模块化引用
                r'@types/underscore'                                   # TypeScript类型
            ]
        },
        'Lodash': {
            'patterns': [
                r'(?:^|/)lodash(?:\.min)?\.js',                       # 文件名匹配
                r'lodash-es/',                                        # ES模块
                r'@lodash/',                                          # npm包
                r'(?:^|[^\w.])_\.(?:VERSION|runInContext)\b',         # 特有API
                r'(?:^|[^\w.])_\.templateSettings\b',                 # 模板设置
                # 对象操作方法 - 确保是_对象的方法调用
                r'(?:^|[^\w.])_\.(?:get|set|has|hasIn|keys|values|entries|toPairs|fromPairs|invoke|create|clone|cloneDeep)\(',
                # 字符串操作方法
                r'(?:^|[^\w.])_\.(?:camelCase|kebabCase|snakeCase|startCase|capitalize|deburr|endsWith|escape|escapeRegExp|pad|padStart|padEnd|parseInt|repeat|replace|split|startsWith|template|trim|trimStart|trimEnd|truncate|unescape|upperCase|upperFirst)\(',
                # 实用函数
                r'(?:^|[^\w.])_\.(?:defaultTo|range|times|uniqueId|constant|identity|matches|method|noop|nthArg|over|overEvery|overSome|property|propertyOf|stubArray|stubFalse|stubObject|stubString|stubTrue)\(',
                r'(?:^|[^\w.])require\([\'"]lodash[\'"]\)',          # CommonJS引入
                r'import\s+[{_}\s]+from\s+[\'"]lodash[\'"]',         # ES6引入
                r'import\s+[{_}\s]+from\s+[\'"]lodash/\w+[\'"]',     # 子模块引入
                r'lodash/fp',                                         # 函数式编程模块
                r'lodash/core',                                       # 核心模块
                r'@types/lodash'                                      # TypeScript类型
            ]
        },
        'core-js': {
            'patterns': [
                r'core-js(?:\.min)?\.js',
                r'core-js/stable',
                r'core-js/modules/',
                r'core-js/features/',
                r'core-js/proposals/',
                r'core-js/web/',
                r'core-js/library',
                r'__core-js_shared__',
                r'core-js-pure',
                r'core-js-compat',
                r'/core-js@\d',
                r'@babel/runtime-corejs\d',
            ]
        },
        'FingerprintJS': {
            'patterns': [
                r'fingerprint(?:\.min)?\.js',
                r'@fingerprintjs/fingerprintjs',
                r'FingerprintJS',
                r'Fingerprint2',
            ]
        },
        'Swiper': {
            'patterns': [
                r'swiper(?:\.min)?\.js',
                r'/swiper/',
                r'swiper-bundle',
                r'swiper-container',
                r'swiper-slide',
                r'swiper-wrapper',
            ]
        }
    },
    '状态管理': {
        'Redux': {
            'patterns': [
                r'(?:^|/)redux(?:\.min)?\.js',                        # 文件名匹配
                r'@reduxjs/toolkit',                                  # Redux工具包
                r'(?:^|[^\w.])(?:create|configure)Store\s*\(',        # Store创建
                r'(?:^|[^\w.])use(?:Selector|Dispatch)\s*\(',        # Hooks API
                r'(?:^|[^\w.])connect\s*\(\s*(?:\([^)]*\)|[^)])*\)', # connect高阶组件
                r'(?:^|[^\w.])mapStateToProps\s*[=:]\s*',            # 映射函数
                r'(?:^|[^\w.])createSlice\s*\(\s*{',                 # Redux Toolkit
                r'(?:^|[^\w.])createReducer\s*\(\s*',                # Reducer创建
                r'(?:^|[^\w.])combineReducers\s*\(\s*{',            # Reducer组合
                r'(?:^|[^\w.])applyMiddleware\s*\(',                # 中间件应用
                r'redux-(?:thunk|saga|observable)(?:/|$)',          # Redux中间件
                r'import\s+[{}\s\w]+\s+from\s+[\'"]@?redux[\'"]',   # Redux导入
            ]
        },
        'Vuex': {
            'patterns': [
                r'(?:^|/)vuex(?:\.min)?\.js',                       # 文件名匹配
                r'(?:^|[^\w.])new\s+Vuex\.Store\s*\(',             # Store实例化
                r'(?:^|[^\w.])map(?:State|Getters|Actions|Mutations)\s*\(',  # 辅助函数
                # Store配置对象
                r'(?:^|[^\w.])(?:commit|dispatch)\s*\(\s*[\'"][^\'"]+[\'"]\s*(?:,|\))',
                r'(?:^|[^\w.])useStore\s*\(\s*\)',                  # 组合式API
                r'(?:^|[^\w.])createStore\s*\(\s*\{',              # Store创建
                r'@/store/index\.(?:js|ts)',                        # 文件路径
                r'import\s+[{}\s\w]+\s+from\s+[\'"]vuex[\'"]',     # Vuex导入
            ]
        },
        'Pinia': {
            'patterns': [
                r'(?:^|/)pinia(?:\.min)?\.js',                      # 文件名匹配
                r'(?:^|[^\w.])createPinia\s*\(\s*\)',              # Pinia创建
                r'(?:^|[^\w.])defineStore\s*\(\s*[\'"]',           # Store定义
                r'(?:^|[^\w.])usePinia\s*\(\s*\)',                 # Pinia使用
                r'(?:^|[^\w.])storeToRefs\s*\(\s*\w+\s*\)',       # Store引用
                r'@pinia/nuxt',                                     # Nuxt集成
                r'@/stores/\w+\.(?:js|ts)',                        # Store文件
                r'pinia/dist',                                      # 构建文件
                # Store定义结构
                r'defineStore\s*\(\s*[\'"][^\'"]+[\'"]\s*,\s*\{\s*(?:state|actions|getters)\s*:',
                r'import\s+[{}\s\w]+\s+from\s+[\'"]pinia[\'"]',    # Pinia导入
            ]
        },
        'MobX': {
            'patterns': [
                r'(?:^|/)mobx(?:\.min)?\.js',                      # 文件名匹配
                r'(?:^|[^\w.])make(?:Observable|AutoObservable)\s*\(',  # Observable创建
                r'(?:^|[^\w.])observer\s*\(\s*(?:class|function)',  # 观察者包装
                r'(?:^|[^\w.])runInAction\s*\(\s*\(?',             # Action执行
                r'mobx-(?:react|vue)(?:/|$)',                      # 框架集成
                r'(?:^|[^\w.])is(?:Observable|Action)\s*\(',      # 类型检查
                r'(?:^|[^\w.])configure\s*\(\s*\{\s*enforceActions',  # 配置
                r'import\s+[{}\s\w]+\s+from\s+[\'"]mobx[\'"]',    # MobX导入
            ]
        }
    },
    'UI框架': {
        'Ant Design': {
            'patterns': [
                r'antd(?:\.min)?\.js',
                r'@ant-design/icons',
                r'@antd/',
                r'(?:^|[^-])(ant-(?:btn|input|form|layout|menu|modal|table|select|checkbox|radio|switch|slider|date|time|calendar|tooltip|popover|drawer|message|notification|spin|icon|tabs|steps|progress|upload|avatar|badge|card|list|tree|tag|alert|skeleton|space|divider|grid|row|col))',
                r'anticon(?:-[a-z]+)?',
                r'ant-design-vue',
                r'antd/lib',
                r'antd/es',
            ]
        },
        'Element UI': {
            'patterns': [
                r'element-ui(?:\.min)?\.js',
                r'element-plus',
                r'(?:^|\s)el-(?:button|input|form|dialog|menu|table|select|radio|checkbox|switch|slider|date-picker|time-picker|upload|progress|badge|tag|alert|message|notification|tabs|card)(?:\s|>|$)',
                r'ElementPlus',
                r'@element-plus/',
                r'/element-ui/',
                r'(?:^|\s)(?:ElMessage|ElNotification|ElMessageBox)\s*[,}]',
                r'installElementPlus',
            ]
        },
        'Naive UI': {
            'patterns': [
                r'naive-ui(?:\.min)?\.js',
                r'@naive-ui/',
                r'(?:^|\s)n-(?:button|input|form|modal|menu|table|select|radio|checkbox|switch|slider|date-picker|time-picker|upload|progress|badge|tag|alert|message|notification|tabs|card)(?:\s|>|$)',
                r'(?:^|\s)(?:useMessage|useDialog|useNotification)\s*\(',
                r'(?:^|\s)createDiscreteApi\s*\(',
                r'/naive-ui/',
                r'(?:^|\s)(?:NButton|NInput|NForm|NModal)\s*[,}]',
                r'naive-ui/es',
            ]
        },
        'Vant': {
            'patterns': [
                r'vant(?:\.min)?\.js',
                r'@vant/use',
                r'@vant/weapp',
                r'(?:^|\s)van-(?:button|field|cell|popup|dialog|toast|notify|tabbar|nav-bar|image|swipe|list|grid|form|radio|checkbox|switch|uploader|picker|datetime-picker|rate|slider|search|steps|tabs|collapse|action-sheet|sidebar|skeleton|tag|badge|divider)(?:\s|>|$)',
                r'Vant\.use\(',
                r'/vant/',
                r'vant/lib',
                r'vant/es',
                r'(?:^|\s)(?:showToast|showDialog|showNotify)\s*\(',
            ]
        },
        'Material-UI': {
            'patterns': [
                r'@material-ui/core',                                # 旧版本包名
                r'@mui/material',                                    # 新版本包名
                r'@mui/icons-material',                             # 图标包
                r'(?:^|[^\w.])(?:make|create|with)Styles\s*\(',    # 样式API
                r'(?:^|[^\w.])styled\s*\(\s*(?:[A-Z][a-zA-Z]*|[\'"]\w+[\'"]\s*\))', # styled API
                r'(?:^|[^\w.])(?:Mui|Material)(?:Theme)?Provider',  # 主题提供者
                r'(?:^|[^\w.])create(?:Mui|Material)Theme\s*\(',    # 主题创建
                r'mui-[a-z](?:[a-z-]*[a-z])?',                     # CSS类名
                r'/material-ui/',                                   # 资源路径
                r'@emotion/(?:react|styled)',                       # 依赖包
                r'import\s+[{}\s\w]+\s+from\s+[\'"]@mui/[^\'"]+'   # MUI导入
            ]
        },
        'Tailwind CSS': {
            'patterns': [
                r'tailwind(?:\.min)?\.css',
                r'@tailwindcss/forms',
                r'@tailwindcss/typography',
                r'@tailwindcss/aspect-ratio',
                r'tailwind\.config\.js',
                r'@apply\s+[^;]+;',
                r'theme\([\'"][^\'"]+[\'"]\)',
            ]
        },
        'Bootstrap': {
            'patterns': [
                r'bootstrap(?:\.min)?\.(?:css|js)',
                r'@popperjs/core',
                r'navbar-(?:brand|nav|toggler)',
                r'btn-(?:primary|secondary|success|danger|warning|info|light|dark)',
                r'modal-(?:dialog|content|header|body|footer)',
                r'data-bs-(?:toggle|target|dismiss)',
                r'bootstrap/dist',
            ]
        }
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
    js_features = {category: [] for category in TECH_SIGNATURES.keys()}
    
    try:
        soup = BeautifulSoup(content, 'html.parser')
        scripts = []
        
        # 收集脚本内容
        for script in soup.find_all('script', src=True):
            src = script['src']
            if src.startswith('//'):
                src = 'https:' + src
            elif not src.startswith(('http://', 'https://')):
                src = f"/script/{src}" if not src.startswith('/') else src
            
            console.print(f"\n[yellow]检测到外部脚本:[/]")
            console.print(f"  原始URL: [dim]{script['src']}[/]")
            console.print(f"  格式化URL: [dim]{src}[/]")
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(src, allow_redirects=True) as response:
                        if response.status == 200:
                            script_content = await response.text()
                            scripts.append((f'外部脚本:{src}', script_content))
                        else:
                            scripts.append((f'外部脚本:{src}', src))
            except Exception as e:
                console.print(f"  [red]访问脚本出错: {str(e)}[/]")
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
    test_url = "https://www.mgtv.com/"
    asyncio.run(analyze_tech_stack(test_url))
