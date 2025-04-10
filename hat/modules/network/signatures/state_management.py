"""状态管理工具特征"""

STATE_MANAGEMENT = {
    'Redux': {
        'patterns': [
            r'(?:^|/)redux(?:\.min)?\.js',                        # 文件名匹配
            r'@reduxjs/toolkit',                                  # Redux工具包
            r'(?:^|[^\w.])(?:create|configure)Store\s*\(',        # Store创建
            r'(?:^|[^\w.])use(?:Selector|Dispatch)\s*\(',        # Hooks API
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
    },
    'Recoil': {
        'patterns': [
            r'recoil(?:\.min)?\.js',                            # 文件名匹配
            r'(?:^|[^\w.])atom\s*\(',                           # 创建atom
            r'(?:^|[^\w.])useRecoilState\s*\(',                 # 状态hook
            r'(?:^|[^\w.])useRecoilValue\s*\(',                 # 值hook
            r'(?:^|[^\w.])useSetRecoilState\s*\(',              # 设置hook
            r'(?:^|[^\w.])RecoilRoot',                          # Root组件
            r'atomFamily|selectorFamily',                        # 参数化状态
        ]
    },
    'Jotai': {
        'patterns': [
            r'jotai(?:\.min)?\.js',                             # 文件名匹配
            r'(?:^|[^\w.])atom\s*\(',                           # 创建atom
            r'(?:^|[^\w.])useAtom\s*\(',                        # 使用atom
            r'(?:^|[^\w.])useAtomValue\s*\(',                   # 读取值
            r'(?:^|[^\w.])useSetAtom\s*\(',                     # 设置值
            r'atomWithStorage|atomWithReducer',                  # 特殊atom
        ]
    },
    'Zustand': {
        'patterns': [
            r'zustand(?:\.min)?\.js',                           # 文件名匹配
            r'zustand/middleware',                              # 中间件
        ]
    }
} 