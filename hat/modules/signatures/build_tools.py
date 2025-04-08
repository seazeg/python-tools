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