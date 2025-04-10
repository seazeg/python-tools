"""构建工具特征"""

BUILD_TOOLS = {
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
            r'/@vite/client',                                  # Vite 客户端导入
            r'/vite/dist/',                                    # Vite 分发目录
            r'vite\.config\.[jt]s',                            # Vite 配置文件
            r'import\.meta\.(?:hot|env\.MODE|url|glob)',       # Vite 特有的导入元属性
            r'__vite_(?:hmr|ssr|base|asset)',                  # Vite 生成的变量
            r'vite-plugin-[a-z-]+',                            # Vite 插件
            r'\.vite/',                                         # Vite 缓存目录
            r'@vitejs/plugin-',                                # Vite 官方插件
            r'/_vite_hmr',                                     # HMR 端点
            r'from\s+[\'"]/@fs/',                              # Vite 文件系统路径
            r'assets/[a-zA-Z0-9]+\.[a-zA-Z0-9]+\.(?:js|css)', # Vite 哈希资源
            r'/@id/',                                          # Vite 模块解析
            r'/@react-refresh',                                # React 刷新支持
            r'data-vite-dev-id',                               # Vite 开发标识符
            r'vite-hmr',                                       # HMR 相关类或属性
            r'vite-error-overlay',                             # 错误覆盖层
            r'import\s+[{}\s\w]+\s+from\s+[\'"]vite[\'"]',    # Vite 导入
            r'require\([\'"]vite[\'"]\)',                      # Vite CommonJS 导入
            r'<script\s+type=[\'"]module[\'"]\s+src=[\'"]/src/[^\'"]+'  # Vite 开发模式脚本
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
    },
    'Babel': {
        'patterns': [
            r'(?:^|/)babel(?:\.min)?\.js$',                     # 文件名匹配
            r'@babel/(?:core|runtime|preset-env|plugin-)',      # Babel包
            r'\.babelrc(?:\.js|\.json)?$',                     # 配置文件
            r'babel\.config\.(?:js|json|cjs|mjs)$',           # 新版配置
            # Babel运行时特征
            r'(?:^|[^\w.])_(?:createClass|classCallCheck|defineProperty|objectSpread|extends|inherits|getPrototypeOf|possibleConstructorReturn|assertThisInitialized|setPrototypeOf)\s*\(',
            # Babel转换后的代码特征
            r'(?:^|[^\w.])require\([\'"]@babel/runtime/[^\'"]+[\'"]\)',
            r'import\s+[{}\s\w]+\s+from\s+[\'"]@babel/runtime/',
            # Babel插件和预设
            r'(?:^|[^\w.])(?:presets|plugins)\s*:\s*\[\s*[\'"]@babel/',
            r'babel-plugin-[a-z-]+',                           # 社区插件
            r'babel-preset-[a-z-]+',                           # 预设包
            # Babel配置选项
            r'(?:^|[^\w.])(?:targets|modules|loose|spec|useBuiltIns|corejs|decorators|classProperties)\s*:\s*(?:true|false|[\'"]\w+[\'"]|\{)',
            # Babel CLI和工具
            r'babel-node',
            r'babel-loader',
            r'@babel/cli',
            # Babel注释指令
            r'@babel/(?:ignore|plugin|preset)',
        ]
    }
} 