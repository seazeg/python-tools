"""分析工具特征"""

ANALYTICS = {
    'Google Analytics': {
        'patterns': [
            r'(?:^|/)google-analytics\.com/(?:analytics\.js|ga\.js)',  # GA文件
            r'(?:^|[^\w.])ga\s*\(\s*[\'"]create[\'"]\s*,\s*[\'"]UA-\d{4,}-\d+[\'"]\s*\)', # UA格式
            r'(?:^|[^\w.])gtag\s*\(\s*[\'"]config[\'"]\s*,\s*[\'"]G-[A-Z0-9]+[\'"]\s*\)', # GA4格式
            r'www\.google-analytics\.com/analytics',                   # GA域名
            r'googletagmanager\.com/gtag/js\?id=(?:UA|G|AW|DC)-',    # GTM
            r'google-analytics\.com/collect',                         # 数据收集
            r'window\.ga\s*=\s*window\.ga',                          # GA初始化
            r'gtag\s*\(\s*[\'"]js[\'"]\s*,\s*new\s+Date\(\)\s*\)',  # GTM初始化
            r'analytics\.js|gtag/js|googletagmanager',               # 脚本引用
        ]
    },
    'Baidu Analytics': {
        'patterns': [
            r'hm\.baidu\.com/hm\.js\?[a-f0-9]{32}',                 # 百度统计文件
            r'hm\.baidu\.com/hm\.gif',                              # 数据收集
            r'(?:^|[^\w.])_hmt\.push\s*\(',                         # 百度统计方法
            r'(?:^|[^\w.])var\s+_hmt\s*=\s*_hmt\s*\|\|\s*\[\s*\]', # 初始化
            r'(?:^|[^\w.])_hmt\.id\s*=\s*[\'"][a-f0-9]{32}[\'"]',  # 配置ID
            r'tongji\.baidu\.com',                                   # 统计域名
            r'(?:^|[^\w.])window\._hmt\s*=\s*window\._hmt',         # 全局变量
        ]
    }
} 