"""图表工具特征"""

CHART_TOOLS = {
    'ECharts': {
        'patterns': [
            r'(?:^|/)echarts(?:\.min)?\.js$',                   # 文件名匹配
            r'(?:^|[^\w.])echarts(?:\.init|\.connect)\s*\(',    # 初始化方法
            r'(?:^|/)echarts/(?:lib|dist|src)/',                # 目录结构
            r'(?:^|[\'"])@echarts/[a-z-]+(?:[\'"]|$)',         # npm包
            r'(?:^|[\'"])echarts-(?:gl|liquidfill|wordcloud)(?:[\'"]|$)', # 扩展插件
            r'(?:^|/)zrender(?:\.min)?\.js$',                   # 渲染引擎
            r'(?:^|[^\w.])require\([\'"]echarts[\'"]\)',       # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]echarts[\'"]', # ES6导入
            r'(?:^|[^\w.])echartsInstance\.(?:setOption|resize|dispose)\s*\(', # 实例方法
        ]
    },
    'Chart.js': {
        'patterns': [
            r'(?:^|/)chart(?:\.min)?\.js$',                    # 文件名匹配
            r'(?:^|[^\w.])new\s+Chart\s*\(',                   # 实例化
            r'(?:^|[^\w.])Chart\.(?:defaults|register|version)\b', # 全局API
            r'(?:^|[\'"])chartjs-plugin-[a-z-]+(?:[\'"]|$)',  # 插件
            r'(?:^|[^\w.])require\([\'"]chart\.js[\'"]\)',    # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]chart\.js[\'"]', # ES6导入
            r'(?:^|[\'"])@types/chart\.js(?:[\'"]|$)',        # TypeScript类型
            r'data-type=[\'"](?:line|bar|radar|doughnut|pie|polarArea|bubble|scatter)[\'"]', # 图表类型
        ]
    },
    'Highcharts': {
        'patterns': [
            r'(?:^|/)highcharts(?:\.min)?\.js$',              # 文件名匹配
            r'(?:^|[^\w.])Highcharts\.(?:chart|stockChart|mapChart)\s*\(',  # 初始化
            r'(?:^|/)highcharts/(?:modules|themes)/',         # 模块和主题
            r'(?:^|[\'"])highcharts-(?:more|3d|stock|maps)(?:[\'"]|$)', # 扩展包
            r'(?:^|[^\w.])require\([\'"]highcharts[\'"]\)',  # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]highcharts[\'"]', # ES6导入
            r'(?:^|[\'"])@types/highcharts(?:[\'"]|$)',      # TypeScript类型
            r'(?:^|[^\w.])Highcharts\.(?:setOptions|getOptions)\s*\(', # 配置方法
        ]
    },
    'D3.js': {
        'patterns': [
            r'(?:^|/)d3(?:\.min)?\.js$',                      # 文件名匹配
            r'(?:^|[^\w.])d3\.(?:select|selectAll|append|attr|style)\s*\(', # DOM操作
            r'(?:^|[^\w.])d3\.(?:scale|axis|svg|transition|zoom)\b', # 核心功能
            r'(?:^|[\'"])d3-(?:array|axis|brush|chord|color|contour|force|geo|hierarchy|interpolate|path|polygon|quadtree|scale|selection|shape|time|timer|transition|zoom)(?:[\'"]|$)', # 模块
            r'(?:^|[^\w.])require\([\'"]d3[\'"]\)',          # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]d3[\'"]', # ES6导入
            r'(?:^|[\'"])@types/d3(?:[\'"]|$)',              # TypeScript类型
        ]
    },
    'AntV': {
        'patterns': [
            r'(?:^|/)(?:g2|g6|f2|l7|x6)(?:\.min)?\.js$',     # 文件名匹配
            r'(?:^|[\'"])@antv/(?:g2|g6|f2|l7|x6)(?:[\'"]|$)', # npm包
            r'(?:^|[^\w.])(?:G2|G6|F2|L7|X6)\.(?:Chart|Graph|Canvas)\s*\(', # 实例化
            r'(?:^|[\'"])antv-(?:g2|g6|f2|l7|x6)(?:[\'"]|$)', # 相关包
            r'(?:^|[^\w.])require\([\'"]@antv/[^\'"]+[\'"]\)', # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]@antv/[^\'"]+[\'"]', # ES6导入
        ]
    },
    'Three.js': {
        'patterns': [
            r'(?:^|/)three(?:\.min)?\.js$',                   # 文件名匹配
            r'(?:^|[^\w.])THREE\.(?:Scene|Camera|WebGLRenderer)\b', # 核心类
            r'(?:^|[^\w.])THREE\.(?:Mesh|Geometry|Material)\b', # 3D对象
            r'(?:^|/)three/(?:examples|build|src)/',         # 目录结构
            r'(?:^|[^\w.])require\([\'"]three[\'"]\)',      # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]three[\'"]', # ES6导入
            r'(?:^|[\'"])@types/three(?:[\'"]|$)',          # TypeScript类型
            r'(?:^|[\'"])three-[a-z-]+(?:-loader|\.js)(?:[\'"]|$)', # 扩展和加载器
        ]
    }
}
