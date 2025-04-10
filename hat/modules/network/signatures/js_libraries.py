"""JavaScript库特征"""

JS_LIBRARIES = {
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
    },
    'Boomerang': {
        'patterns': [
            r'(?:^|/)boomerang(?:\.min)?\.js$',                # 文件名匹配
            r'BOOMR(?:\.init|\.[a-z]+)',                       # 全局对象
            r'boomerang/plugins/',                             # 插件目录
            r'(?:^|[^\w.])BOOMR_start\b',                     # 启动变量
            r'(?:^|[^\w.])BOOMR_lstart\b',                    # 加载时间
            r'(?:^|[^\w.])BOOMR\.addVar\s*\(',                # 添加变量
            r'(?:^|[^\w.])BOOMR\.subscribe\s*\(',             # 事件订阅
            r'boomerang-(?:plugin|loader)',                    # 相关文件
            r'boomr/boomerang',                               # npm包
            r'import\s+[{}\s\w]+\s+from\s+[\'"]boomerang[\'"]', # ES6导入
            r'require\([\'"]boomerang[\'"]\)',                # CommonJS引入
            # 性能监控相关
            r'beacon\.(?:min\.)?js',                          # 信标文件
            r'BOOMR\.plugins\.RT\.startTimer\s*\(',           # 计时器
            r'BOOMR\.responseEnd\s*=',                        # 响应时间
            r'BOOMR\.t_(?:start|end|done)',                   # 时间戳
        ]
    }
} 