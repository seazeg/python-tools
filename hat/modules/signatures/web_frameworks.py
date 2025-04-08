"""Web框架特征"""

WEB_FRAMEWORKS = {
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
} 