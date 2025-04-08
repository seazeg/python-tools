"""JavaScript库特征"""

JS_LIBRARIES = {
    'jQuery': {
        'patterns': [
            r'(?:^|/)jquery(?:\.min)?\.js$',                    # 文件名匹配
            r'(?:^|[^\w.])(?:window\.)?jQuery(?:\.fn|\$)',      # 全局对象
            r'(?:^|[^\w.])(?:\$|jQuery)\s*\(',                  # 函数调用
            r'jquery(?:-\d+\.\d+\.\d+)?(?:\.min)?\.js',        # 版本文件
            r'jquery-ui(?:\.min)?\.js',                        # UI库
            r'jquery\.(?:ajax|get|post)\s*\(',                 # Ajax方法
            r'(?:^|[^\w.])require\([\'"]jquery[\'"]\)',        # CommonJS引入
            r'import\s+[{}\s\w]+\s+from\s+[\'"]jquery[\'"]',   # ES6导入
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
    'Lodash': {
        'patterns': [
            r'(?:^|/)lodash(?:\.min)?\.js$',                    # 文件名匹配
            r'(?:^|[^\w.])_\.(?:map|filter|reduce|find|each)',  # 核心方法
            r'(?:^|[^\w.])require\([\'"]lodash[\'"]\)',        # CommonJS引入
            r'import\s+[{}\s\w]+\s+from\s+[\'"]lodash[\'"]',   # ES6导入
            r'@types/lodash',                                  # TypeScript类型
            r'lodash/(?:fp|core)',                             # 子模块
            r'lodash-es',                                      # ES模块版本
        ]
    }
} 