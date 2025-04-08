"""Web服务器特征"""
import re  # 添加这一行导入re模块

WEB_SERVERS = {
    'Apache': {
        'headers': {
            'server': [
                r'(?i)apache/?[\d.]*',                         # 标准Server头
                r'(?i)apache[\s-]coyote/?[\d.]*',             # Tomcat的Apache实现
            ],
            'x-powered-by': [
                r'(?i)apache/?[\d.]*',                        # 扩展信息
                r'(?i)mod_(?:perl|python|php|ruby|ssl)',      # Apache模块
            ],
            'x-mod-pagespeed': [r'.*'],                      # PageSpeed模块
            'x-apache': [r'.*'],                             # Apache特有头
        },
        'patterns': [
            r'(?i)/etc/apache\d?/',                          # 配置路径
            r'(?i)/usr/local/apache\d?/',                    # 安装路径
            r'(?i)\.htaccess',                              # 配置文件
            r'(?i)mod_(?:rewrite|ssl|perl|python|php)',     # 模块标识
        ]
    },
    'Nginx': {
        'headers': {
            'server': [
                r'(?i)nginx/?[\d.]*',                        # 标准Server头
                r'(?i)openresty/?[\d.]*',                    # OpenResty变种
            ],
            'x-fastcgi-cache': [r'.*'],                     # FastCGI缓存
            'x-proxy-cache': [r'.*'],                       # 代理缓存
            'x-powered-by': [r'(?i)nginx'],                 # 扩展信息
        },
        'patterns': [
            r'(?i)/etc/nginx/',                             # 配置路径
            r'(?i)/usr/local/nginx/',                       # 安装路径
            r'(?i)\.conf$',                                 # 配置文件
            r'(?i)nginx\.conf',                             # 主配置文件
        ]
    },
    'IIS': {
        'headers': {
            'server': [
                r'(?i)microsoft-iis/?[\d.]*',               # 标准Server头
                r'(?i)iis/?[\d.]*',                         # 简化版Server头
            ],
            'x-powered-by': [
                r'(?i)asp\.net',                            # ASP.NET支持
                r'(?i)iis/?[\d.]*',                         # IIS版本
            ],
            'x-aspnet-version': [r'[\d.]+'],               # ASP.NET版本
            'x-aspnetmvc-version': [r'[\d.]+'],            # MVC版本
        },
        'patterns': [
            r'(?i)\\inetpub\\',                            # 默认站点路径
            r'(?i)\.asp$',                                  # ASP文件
            r'(?i)web\.config$',                           # 配置文件
            r'(?i)microsoft-server-apache',                # 混合模式
        ]
    },
    'Tomcat': {
        'headers': {
            'server': [
                r'(?i)apache-coyote/?[\d.]*',              # Coyote服务器
                r'(?i)apache-tomcat/?[\d.]*',              # Tomcat标识
            ],
            'x-powered-by': [r'(?i)tomcat'],              # Tomcat支持
            'jsessionid': [r'.*'],                        # 会话ID
        },
        'patterns': [
            r'(?i)/tomcat/',                              # 安装路径
            r'(?i)\.jsp$',                                # JSP文件
            r'(?i)catalina\.jar',                        # 核心JAR
            r'(?i)tomcat-users\.xml',                    # 用户配置
        ]
    },
    'LiteSpeed': {
        'headers': {
            'server': [
                r'(?i)litespeed/?[\d.]*',                 # 标准Server头
                r'(?i)openlitespeed/?[\d.]*',            # 开源版本
            ],
            'x-powered-by': [r'(?i)litespeed'],         # 扩展信息
            'x-lsadc-cache': [r'.*'],                   # 缓存标识
        },
        'patterns': [
            r'(?i)/usr/local/lsws/',                    # 安装路径
            r'(?i)\.htaccess',                          # 兼容配置
            r'(?i)lsphp\d+',                           # PHP处理器
        ]
    },
    'Caddy': {
        'headers': {
            'server': [r'(?i)caddy/?[\d.]*'],          # 标准Server头
            'x-powered-by': [r'(?i)caddy'],           # 扩展信息
        },
        'patterns': [
            r'(?i)Caddyfile',                         # 配置文件
            r'(?i)/etc/caddy/',                       # 配置路径
        ]
    },
    'Tengine': {
        'headers': {
            'server': [
                r'(?i)tengine/?[\d.]*',                    # 标准Server头
                r'(?i)tengine/[\d.]+',                     # 精确版本
            ],
            'x-powered-by': [
                r'(?i)tengine',                           # 扩展信息
                r'(?i)alibaba',                           # 阿里巴巴标识
            ],
            'via': [
                r'(?i)tengine',                           # 代理信息
            ],
            'x-tengine-error': [r'.*'],                  # Tengine错误信息
            'eagleeye-traceid': [r'.*'],                 # 阿里云追踪ID
            'x-tengine-version': [r'[\d.]+'],            # Tengine版本
        },
        'patterns': [
            r'(?i)/tengine/',                            # 安装路径
            r'(?i)\.tengine\.conf$',                     # 配置文件
            r'(?i)tengine\.taobao\.com',                 # 官方域名
            r'(?i)powered[\s-]by[\s-]tengine',           # 页面标识
        ]
    }
}

# 通用的错误页面特征
ERROR_PAGES = {
    'Apache': [
        r'<title>Apache HTTP Server Test Page powered by CentOS</title>',
        r'<address>Apache/[\d.]+ \([^)]+\) Server',
        r'Apache is functioning normally',
    ],
    'Nginx': [
        r'<title>Welcome to nginx!</title>',
        r'<hr><center>nginx/[\d.]+</center>',
        r'<title>404 Not Found</title>\s*<center>nginx/[\d.]+',
    ],
    'IIS': [
        r'<title>IIS \d+\.\d+ Detailed Error',
        r'<a href="http://go\.microsoft\.com/fwlink',
        r'<hr width=100% size=1 color=silver>',
    ]
}

# 添加 Tengine 的错误页面特征
ERROR_PAGES.update({
    'Tengine': [
        r'<title>Welcome to tengine!</title>',
        r'<hr><center>tengine/[\d.]+</center>',
        r'<title>404 Not Found</title>\s*<center>tengine/[\d.]+',
        r'<center>tengine/[\d.]+ \([^)]+\)</center>',
    ]
})

def enhance_server_detection(headers: dict, content: str) -> list:
    """增强的服务器检测"""
    detected_servers = []
    
    # 1. 检查标准Server头
    server_header = headers.get('server', '').lower()
    
    # 2. 检查所有相关头部
    for server, signatures in WEB_SERVERS.items():
        # 检查每个头部的模式
        for header, patterns in signatures.get('headers', {}).items():
            header_value = headers.get(header, '').lower()
            if header_value:
                for pattern in patterns:
                    if re.search(pattern, header_value, re.I):
                        detected_servers.append(server)
                        break
        
        # 检查内容模式
        for pattern in signatures.get('patterns', []):
            if re.search(pattern, content, re.I):
                detected_servers.append(server)
                break
                
        # 检查错误页面特征
        if server in ERROR_PAGES:
            for pattern in ERROR_PAGES[server]:
                if re.search(pattern, content, re.I):
                    detected_servers.append(server)
                    break
    
    # 3. 特殊情况处理
    if 'apache' in server_header and 'nginx' in server_header:
        # Apache作为后端，Nginx作为前端的情况
        detected_servers.extend(['Apache', 'Nginx'])
    
    # 4. 移除重复项并返回
    return list(set(detected_servers)) 