
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
                r'(?:^|/)react(?:\.production)?(?:\.min)?\.js$',     # React主文件
                r'(?:^|/)react-dom(?:\.production)?(?:\.min)?\.js$', # ReactDOM文件
                # React全局对象和方法调用
                r'(?:^|[^\w.])(?:window\.)?React(?:\.createElement|\.Component|\.Fragment|\.createContext|\.lazy|\.memo)\s*\(',
                r'(?:^|[^\w.])ReactDOM\.(?:render|hydrate|createRoot)\s*\(',
                # JSX转换函数 - 确保是函数调用
                r'(?:^|[^\w.])_jsx(?:DEV|s)?\s*\(',
                # React Hooks - 确保是函数调用
                r'(?:^|[^\w.])use(?:State|Effect|Context|Ref|Memo|Callback|Reducer|ImperativeHandle|LayoutEffect|DebugValue|DeferredValue|Transition|Id)\s*\(',
                # React相关包
                r'(?:^|[^\w-])(?:@react-|react-router|react-redux|react-query|react-hook-form)',
                # React导入语句
                r'import\s+[{}\s\w]+\s+from\s+[\'"]react(?:/[^\'"]+)?[\'"]',
                r'import\s+[{}\s\w]+\s+from\s+[\'"]@react',
                # React配置文件
                r'(?:^|/)\.react(?:rc|\.config)\.[jt]s',
            ]
        },
        'Vue.js': {
            'patterns': [
                r'(?:^|/)vue(?:\.runtime)?(?:\.esm)?(?:\.min)?\.js$',    # Vue主文件
                # Vue全局对象和实例化
                r'(?:^|[^\w.])(?:window\.)?Vue(?:\.createApp|\.use|\.component|\.directive|\.filter|\.mixin|\.extend)\s*\(',
                r'(?:^|[^\w.])new\s+Vue\s*\(',
                # Vue指令 - 更精确的HTML属性匹配
                r'(?:^|\s+)v-(?:if|else-if|else|for|model|bind|on|show|html|text|slot|cloak|once|pre)="[^"]*"',
                r'(?:^|\s+)v-bind:[\w-]+="[^"]*"',
                r'(?:^|\s+)v-on:[\w-]+="[^"]*"',
                # Vue事件和属性绑定简写
                r'(?:^|\s+)@(?:click|change|input|submit|keyup|keydown|focus|blur)="[^"]*"',
                r'(?:^|\s+):(?:class|style|src|href|alt|title|placeholder|value|type|disabled|required)="[^"]*"',
                # Vue相关包
                r'(?:^|[^\w-])(?:@vue/|vue-router|vuex|@vitejs/plugin-vue)',
                # Vue组件和API
                r'(?:^|[^\w.])(?:defineComponent|onMounted|onUnmounted|onUpdated|ref|reactive|computed|watch)\s*\(',
                # Vue文件和模板
                r'<template>[\s\S]*?</template>',
                r'\.vue$',
                # Vue导入语句
                r'import\s+[{}\s\w]+\s+from\s+[\'"]vue(?:/[^\'"]+)?[\'"]',
                r'import\s+[{}\s\w]+\s+from\s+[\'"]@vue',
                # Vue配置文件
                r'(?:^|/)vue\.config\.[jt]s',
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
        },
        'crypto-js': {
            'patterns': [
                r'(?:^|/)crypto-js(?:\.min)?\.js$',                  # 文件名匹配
                r'CryptoJS\.(?:AES|DES|TripleDES|Rabbit|RC4)',      # 加密算法
                r'(?:^|[^\w.])CryptoJS\.(?:enc|format|lib|mode|pad)', # 工具类
                r'(?:^|[^\w.])CryptoJS\.(?:MD5|SHA[1-3]|RIPEMD160|HMAC)\(', # 哈希函数
                r'(?:^|[^\w.])require\([\'"]crypto-js(?:/[^\'"]+)?[\'"]\)',  # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]crypto-js(?:/[^\'"]+)?[\'"]', # ES6导入
                r'@types/crypto-js',                                 # TypeScript类型
                r'/crypto-js@\d',                                    # 版本标识
            ]
        },
        'Clipboard.js': {
            'patterns': [
                r'(?:^|/)clipboard(?:\.min)?\.js$',                  # 文件名匹配
                r'(?:^|[^\w.])new\s+ClipboardJS\s*\(',              # 实例化
                r'(?:^|[^\w.])clipboard\.js(?:/|$)',                # 包引用
                r'data-clipboard-(?:text|target|action)',           # 数据属性
                r'(?:^|[^\w.])ClipboardJS\.isSupported\s*\(',      # 方法调用
                r'(?:^|[^\w.])require\([\'"]clipboard[\'"]\)',      # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]clipboard[\'"]', # ES6导入
                r'@types/clipboard',                                # TypeScript类型
            ]
        },
        'Axios': {
            'patterns': [
                r'(?:^|/)axios(?:\.min)?\.js$',                     # 文件名匹配
                # Axios方法调用
                r'(?:^|[^\w.])axios\.(?:get|post|put|delete|patch|head|options)\s*\(',
                r'(?:^|[^\w.])axios\.(?:request|create)\s*\(',      # 实例方法
                r'(?:^|[^\w.])axios\.(?:interceptors|defaults)',    # 配置属性
                # Axios实例和配置
                r'(?:^|[^\w.])axios\.create\s*\(\s*\{[^}]*baseURL',
                r'(?:^|[^\w.])axios\.defaults\.(?:headers|timeout|baseURL)',
                # 导入语句
                r'(?:^|[^\w.])require\([\'"]axios[\'"]\)',         # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]axios[\'"]',    # ES6导入
                r'@types/axios',                                    # TypeScript类型
                # 响应和拦截器
                r'(?:^|[^\w.])axios(?:Response|Error|Cancel)',
                r'(?:^|[^\w.])CancelToken\.source\s*\(',
            ]
        },
        'Moment.js': {
            'patterns': [
                r'(?:^|/)moment(?:\.min)?\.js$',                    # 文件名匹配
                r'(?:^|/)moment-with-locales(?:\.min)?\.js$',      # 带本地化文件
                # Moment方法调用
                r'(?:^|[^\w.])moment\s*\([^\)]*\)\.(?:format|fromNow|calendar|diff|valueOf|unix|utc|local|tz)\s*\(',
                # Moment配置和本地化
                r'(?:^|[^\w.])moment\.(?:locale|duration|tz|unix)\s*\(',
                r'(?:^|[^\w.])moment\.(?:updateLocale|defineLocale|locales)\s*\(',
                # 导入语句
                r'(?:^|[^\w.])require\([\'"]moment(?:/[^\'"]+)?[\'"]\)',  # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]moment(?:/[^\'"]+)?[\'"]', # ES6导入
                r'@types/moment',                                   # TypeScript类型
                # 插件和扩展
                r'moment-timezone',
                r'moment/locale/',
                r'moment-range',
                r'moment-duration-format',
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
                r'data-bs-(?:toggle|target|dismiss)',
                r'bootstrap/dist',
            ]
        }
    },
    '分析': {
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
        },
        'Google Tag Manager': {
            'patterns': [
                r'googletagmanager\.com/gtm\.js\?id=GTM-[A-Z0-9]+',     # GTM文件
                r'(?:^|[^\w.])dataLayer\s*=\s*\[\s*\{',                 # 数据层初始化
                r'(?:^|[^\w.])dataLayer\.push\s*\(',                    # 数据推送
                r'<iframe[^>]+googletagmanager\.com/ns\.html\?id=GTM-', # GTM iframe
                r'<!-- Google Tag Manager -->',                          # GTM注释
                r'gtm\.start\s*=\s*new\s+Date',                         # GTM时间戳
                r'gtm\.js\?id=GTM-[A-Z0-9]+',                          # GTM ID
            ]
        },
        'CNZZ': {
            'patterns': [
                r'(?:^|/)cnzz\.com/(?:z_stat\.php|stat\.php)',         # CNZZ文件
                r'(?:^|[^\w.])cnzz_protocol',                          # CNZZ协议
                r'(?:^|[^\w.])var\s+cnzz_s_tag\s*=',                  # CNZZ变量
                r'https?://[^/]*cnzz\.(?:com|net)/',                   # CNZZ域名
                r'id="cnzz_stat_icon_\d+"',                           # CNZZ图标
                r'src="[^"]*cnzz\.com/[^"]+?\?id=\d+"',              # CNZZ脚本
            ]
        },
        'Sensors Analytics': {
            'patterns': [
                r'(?:^|[^\w.])sensorsdata\.min\.js',                   # 神策文件
                r'(?:^|[^\w.])sensors\.track\s*\(',                    # 事件跟踪
                r'(?:^|[^\w.])sensorsdata_js_sdk',                     # SDK标识
                r'(?:^|[^\w.])sa\.track\s*\(',                         # 简写API
                r'(?:^|[^\w.])sensors\.quick\s*\(',                    # 快速API
                r'sensorsdata\.cn/sa\.js',                             # 服务域名
                r'(?:^|[^\w.])sensors\.init\s*\(',                     # 初始化
            ]
        }
    },
    'CDN': {
        'Cloudflare': {
            'patterns': [
                r'cloudflare\.com/cdn-cgi/',                        # CDN路径
                r'cloudflare-static/',                              # 静态资源
                r'__cf_email__',                                    # 邮箱保护
                r'cf-(?:ray|request-id|cache-status)',              # CF头部
                r'cloudflare\.com/ajax/libs',                       # CDNJS
                r'cdnjs\.cloudflare\.com',                         # CDNJS域名
                r'cloudflare\.com/web-analytics',                   # 分析服务
                r'cloudflare-beacon\.com',                         # 信标服务
            ],
            'headers': ['cf-ray', 'cf-cache-status', 'cf-connecting-ip']
        },
        'Akamai': {
            'patterns': [
                r'\.akamai(?:\.net|\.com|\.co|\.cn|edge\.net)/',    # Akamai域名族
                r'\.akamaized\.net/',                               # 优化域名
                r'\.akamaihd\.net/',                               # 媒体域名
                r'\.edgesuite\.net/',                              # 传统域名
                r'\.edgekey\.net/',                                # SSL域名
                r'akamai-(?:static|dynamic|streaming)',             # 资源标识
                r'akamai\.com/clear/[a-f0-9]+',                    # 缓存清理
                r'akamai\.com/(?:web|media|image)/',               # 服务路径
            ],
            'headers': [
                'x-akamai-transformed',                            # 转换标记
                'akamai-origin-hop',                               # 源站跳转
                'x-akamai-request-id',                             # 请求ID
                'x-akamai-cache-',                                 # 缓存信息
                'akamai-x-cache-on',                               # 缓存状态
                'akamai-x-get-cache-key',                          # 缓存键
                'akamai-x-check-cacheable',                        # 可缓存检查
                'akamai-x-feo-trace',                             # 前端优化跟踪
                'x-akamai-ssl-client-sid',                        # SSL会话ID
                'x-akamai-edgescape'                              # 地理位置信息
            ]
        },
        'Fastly': {
            'patterns': [
                r'\.fastly\.net/',                                # Fastly域名
                r'fastly-(?:cdn|ssl|debug)',                      # 服务标识
                r'fastly\.com/products/',                         # 产品路径
            ],
            'headers': ['fastly-debug-digest', 'x-served-by', 'x-cache-hits']
        },
        'AWS CloudFront': {
            'patterns': [
                r'\.cloudfront\.net/',                            # CloudFront域名
                r'aws-cloudfront/',                               # AWS标识
                r'x-amz-cf-',                                     # CF头部前缀
            ],
            'headers': ['x-amz-cf-id', 'x-amz-cf-pop']
        },
        '阿里云CDN': {
            'patterns': [
                r'\.alicdn\.com/',                               # 阿里CDN域名
                r'\.aliyuncs\.com/',                            # 阿里云域名
                r'aliyun-(?:cdn|oss)',                          # 服务标识
            ],
            'headers': ['ali-swift-global-savetime', 'x-swift-cachetime']
        },
        '腾讯云CDN': {
            'patterns': [
                r'\.qcloud\.com/',                              # 腾讯云域名
                r'\.cdntip\.com/',                             # CDN域名
                r'\.tcloudscdn\.com/',                         # 新CDN域名
                r'tencent-cloud-cdn',                          # 服务标识
            ],
            'headers': ['x-daa-tunnel', 'x-cache-lookup']
        },
        '七牛云CDN': {
            'patterns': [
                r'\.qiniucdn\.com/',                           # 七牛CDN域名
                r'\.qiniudns\.com/',                          # DNS域名
                r'\.qbox\.me/',                               # 存储域名
                r'qiniu-(?:cdn|rtc)',                         # 服务标识
            ],
            'headers': ['x-qiniu-zone', 'x-reqid']
        }
    },
    '视频播放器': {
        'Video.js': {
            'patterns': [
                r'(?:^|/)video(?:-js)?(?:\.min)?\.js$',              # 文件名匹配
                r'videojs(?:\.min)?\.css',                           # CSS文件
                r'(?:^|[^\w.])videojs\s*\(',                         # 实例化
                r'video-js|vjs-(?:big-play-button|control|text-track)', # CSS类
                r'data-setup=[\'"]\{[^\}]*?\}[\'"]',                # 配置属性
                r'(?:^|[^\w.])require\([\'"]video\.js[\'"]\)',      # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]video\.js[\'"]', # ES6导入
                r'@videojs/[a-z-]+',                                # 插件包
            ]
        },
        'Plyr': {
            'patterns': [
                r'(?:^|/)plyr(?:\.min)?\.js$',                      # 文件名匹配
                r'plyr(?:\.min)?\.css',                             # CSS文件
                r'(?:^|[^\w.])new\s+Plyr\s*\(',                     # 实例化
                r'plyr(?:__controls|__menu|__progress|__volume)',   # CSS类
                r'data-plyr-(?:provider|embed-id)',                 # 数据属性
                r'(?:^|[^\w.])require\([\'"]plyr[\'"]\)',          # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]plyr[\'"]',     # ES6导入
            ]
        },
        'DPlayer': {
            'patterns': [
                r'(?:^|/)DPlayer(?:\.min)?\.js$',                   # 文件名匹配
                r'DPlayer(?:\.min)?\.css',                          # CSS文件
                r'(?:^|[^\w.])new\s+DPlayer\s*\(',                  # 实例化
                r'dplayer(?:-mobile)?(?:-[a-z-]+)?',               # CSS类
                r'data-dplayer-(?:video|danmaku|subtitle)',        # 数据属性
                r'(?:^|[^\w.])require\([\'"]dplayer[\'"]\)',       # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]dplayer[\'"]',  # ES6导入
            ]
        },
        'ArtPlayer': {
            'patterns': [
                r'(?:^|/)artplayer(?:\.min)?\.js$',                # 文件名匹配
                r'artplayer(?:\.min)?\.css',                       # CSS文件
                r'(?:^|[^\w.])new\s+Artplayer\s*\(',               # 实例化
                r'art-video-player',                               # CSS类
                r'data-art-(?:video|subtitle|thumbnail)',          # 数据属性
                r'(?:^|[^\w.])require\([\'"]artplayer[\'"]\)',    # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]artplayer[\'"]', # ES6导入
            ]
        },
        'Aliplayer': {
            'patterns': [
                r'(?:^|/)aliplayer(?:-(?:h5|flash))?(?:\.min)?\.js$', # 文件名匹配
                r'aliplayer(?:\.min)?\.css',                        # CSS文件
                r'(?:^|[^\w.])new\s+Aliplayer\s*\(',                # 实例化
                r'prism-player',                                    # CSS类
                r'data-player-(?:type|video|config)',              # 数据属性
                r'alicdn\.com/[^"\']+aliplayer',                   # CDN路径
                r'Aliplayer\.events',                              # 事件API
            ]
        },
        'TCPlayer': {
            'patterns': [
                r'(?:^|/)tcplayer(?:-(?:lite|web))?(?:\.min)?\.js$', # 文件名匹配
                r'(?:^|[^\w.])new\s+TCPlayer\s*\(',                 # 实例化
                r'vcp-player',                                      # CSS类
                r'data-tc-(?:player|video)',                       # 数据属性
                r'tcplayer\.v\d+\.(?:min\.)?js',                   # 版本文件
                r'cloud\.tencent\.com/[^"\']+tcplayer',           # CDN路径
                r'TCPlayer\.defaults',                             # 配置API
            ]
        },
        'XGPlayer': {
            'patterns': [
                r'(?:^|/)xgplayer(?:-(?:lite|mp4))?(?:\.min)?\.js$', # 文件名匹配
                r'(?:^|[^\w.])new\s+Player\s*\(',                   # 实例化
                r'xgplayer(?:-(?:skin|controls|progress))',        # CSS类
                r'data-xg-(?:player|video)',                       # 数据属性
                r'xgplayer\.v\d+\.(?:min\.)?js',                  # 版本文件
                r'(?:^|[^\w.])require\([\'"]xgplayer[\'"]\)',     # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]xgplayer[\'"]', # ES6导入
            ]
        }
    },
    '图表工具': {
        'ECharts': {
            'patterns': [
                r'(?:^|/)echarts(?:\.min)?\.js$',                   # 文件名匹配
                r'(?:^|[^\w.])echarts(?:\.init|\.connect)\s*\(',    # 初始化方法
                r'echarts/(?:lib|dist|src)/',                       # 目录结构
                r'@echarts/',                                       # npm包
                r'echarts-(?:gl|liquidfill|wordcloud)',            # 扩展插件
                r'zrender(?:\.min)?\.js',                          # 渲染引擎
                r'(?:^|[^\w.])require\([\'"]echarts[\'"]\)',       # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]echarts[\'"]',  # ES6导入
                r'echartsInstance\.(?:setOption|resize|dispose)',   # 实例方法
            ]
        },
        'Chart.js': {
            'patterns': [
                r'(?:^|/)chart(?:\.min)?\.js$',                    # 文件名匹配
                r'(?:^|[^\w.])new\s+Chart\s*\(',                   # 实例化
                r'Chart\.(?:defaults|register|version)',           # 全局API
                r'chartjs-plugin-[a-z-]+',                        # 插件
                r'(?:^|[^\w.])require\([\'"]chart\.js[\'"]\)',    # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]chart\.js[\'"]', # ES6导入
                r'@types/chart\.js',                              # TypeScript类型
                r'data-type=[\'"](?:line|bar|radar|doughnut|pie|polarArea|bubble|scatter)[\'"]', # 图表类型
            ]
        },
        'Highcharts': {
            'patterns': [
                r'(?:^|/)highcharts(?:\.min)?\.js$',              # 文件名匹配
                r'(?:^|[^\w.])Highcharts\.(?:chart|stockChart|mapChart)\s*\(',  # 初始化
                r'highcharts/(?:modules|themes)/',                # 模块和主题
                r'highcharts-(?:more|3d|stock|maps)',            # 扩展包
                r'(?:^|[^\w.])require\([\'"]highcharts[\'"]\)',  # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]highcharts[\'"]', # ES6导入
                r'@types/highcharts',                            # TypeScript类型
                r'Highcharts\.(?:setOptions|getOptions)',        # 配置方法
            ]
        },
        'D3.js': {
            'patterns': [
                r'(?:^|/)d3(?:\.min)?\.js$',                      # 文件名匹配
                r'd3\.(?:select|selectAll|append|attr|style)',    # DOM操作
                r'd3\.(?:scale|axis|svg|transition|zoom)',        # 核心功能
                r'd3-(?:array|axis|brush|chord|color|contour|force|geo|hierarchy|interpolate|path|polygon|quadtree|scale|selection|shape|time|timer|transition|zoom)', # 模块
                r'(?:^|[^\w.])require\([\'"]d3[\'"]\)',          # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]d3[\'"]',     # ES6导入
                r'@types/d3',                                    # TypeScript类型
            ]
        },
        'AntV': {
            'patterns': [
                r'(?:^|/)(?:g2|g6|f2|l7|x6)(?:\.min)?\.js$',     # 文件名匹配
                r'@antv/(?:g2|g6|f2|l7|x6)',                     # npm包
                r'(?:^|[^\w.])(?:G2|G6|F2|L7|X6)\.(?:Chart|Graph|Canvas)\s*\(', # 实例化
                r'antv-(?:g2|g6|f2|l7|x6)',                      # 相关包
                r'(?:^|[^\w.])require\([\'"]@antv/[^\'"]+[\'"]\)', # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]@antv/[^\'"]+[\'"]', # ES6导入
            ]
        },
        'Three.js': {
            'patterns': [
                r'(?:^|/)three(?:\.min)?\.js$',                   # 文件名匹配
                r'THREE\.(?:Scene|Camera|WebGLRenderer)',         # 核心类
                r'THREE\.(?:Mesh|Geometry|Material)',            # 3D对象
                r'three/(?:examples|build|src)/',                # 目录结构
                r'(?:^|[^\w.])require\([\'"]three[\'"]\)',      # CommonJS引入
                r'import\s+[{}\s\w]+\s+from\s+[\'"]three[\'"]', # ES6导入
                r'@types/three',                                # TypeScript类型
                r'three-[a-z-]+(?:-loader|\.js)',              # 扩展和加载器
            ]
        }
    }
}