"""Web服务器特征"""

WEB_SERVERS = {
    'Apache': {'headers': ['server', 'x-powered-by'], 'pattern': r'apache'},
    'Nginx': {'headers': ['server'], 'pattern': r'nginx'},
    'IIS': {'headers': ['server'], 'pattern': r'iis|microsoft'},
} 