"""Web框架特征"""

WEB_FRAMEWORKS = {
    'Express': {
        'patterns': [
            r'(?:^|/)express(?:\.min)?\.js$',                   # 主文件
            r'(?:^|/)node_modules/express/',                    # 模块目录
            r'(?:^|[^\w.])require\([\'"]express[\'"]\)',       # CommonJS引入
            r'(?:^|[^\w.])app\.(?:get|post|put|delete|use|listen)\s*\(', # API方法
            r'(?:^|[\'"])express-(?:session|validator|jwt)(?:[\'"]|$)', # 中间件
        ]
    },
    'Nuxt.js': {
        'patterns': [
            r'(?:^|/)_nuxt/',                                    # Nuxt资源目录
            r'(?:^|/)__nuxt/',                                   # Nuxt生成目录
            r'(?:^|/)nuxt(?:\.min)?\.js$',                      # Nuxt主文件
            r'(?:^|[^\w.])window\.__NUXT__',                    # Nuxt状态
            r'(?:^|\s)<div\s+id="__nuxt"(?:\s|>)',             # Nuxt根元素
            r'(?:^|[\'"])@nuxt/[a-z-]+(?:[\'"]|$)',            # Nuxt官方包
            r'(?:^|[\'"])nuxt-(?:link|child|layout|view|loading|error|progress|build|start|generate)(?:[\'"]|$)', # Nuxt组件和命令
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]@nuxt/', # Nuxt导入
            r'(?:^|[^\w.])extends:\s*[\'"]@nuxt/',             # Nuxt配置继承
            r'(?:^|[^\w.])modules:\s*\[\s*[\'"]@nuxt/',        # Nuxt模块配置
        ]
    },
    'Next.js': {
        'patterns': [
            r'(?:^|/)_next/',                                   # Next资源目录
            r'(?:^|/)__next/',                                  # Next生成目录
            r'(?:^|/)next(?:\.min)?\.js$',                     # Next主文件
            r'(?:^|[^\w.])window\.__NEXT_DATA__',              # Next状态
            r'(?:^|\s)<div\s+id="__next"(?:\s|>)',            # Next根元素
            r'(?:^|[\'"])@next/[a-z-]+(?:[\'"]|$)',           # Next官方包
            r'(?:^|[\'"])next-(?:link|router|head|script|image|auth|seo|sitemap|mdx|transpile-modules)(?:[\'"]|$)', # Next组件和工具
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]next/', # Next导入
            r'(?:^|[^\w.])config\s*=\s*{\s*[\'"]next[\'"]',    # Next配置
        ]
    },
    'Django': {
        'patterns': [
            r'(?:^|[\'"])django\.contrib\.[a-z]+(?:[\'"]|$)',  # Django贡献包
            r'(?:^|\s){% [a-z_]+ %}',                          # Django模板标签
            r'(?:^|\s){{ [^}]+ }}',                            # Django模板变量
            r'(?:^|/)django/(?:contrib|core|db|template)/',    # Django目录结构
            r'(?:^|[^\w.])DJANGO_SETTINGS_MODULE\b',           # Django设置
            r'(?:^|[^\w.])INSTALLED_APPS\s*=',                 # Django应用配置
            r'(?:^|[^\w.])MIDDLEWARE\s*=',                     # Django中间件
        ]
    },
    'Flask': {
        'patterns': [
            r'(?:^|[^\w.])Flask\s*\(',                         # Flask实例化
            r'(?:^|[^\w.])@app\.route\s*\(',                   # Flask路由装饰器
            r'(?:^|[\'"])flask[._](?:request|session|g|current_app)(?:[\'"]|$)', # Flask上下文
            r'(?:^|[\'"])flask_(?:sqlalchemy|login|admin|migrate)(?:[\'"]|$)', # Flask扩展
            r'(?:^|[^\w.])render_template\s*\(',               # Flask模板渲染
            r'(?:^|[^\w.])jsonify\s*\(',                       # Flask JSON响应
        ]
    }
} 