"""Web框架特征"""

WEB_FRAMEWORKS = {
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
    }
} 