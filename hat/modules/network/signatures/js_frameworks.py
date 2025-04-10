"""JavaScript框架特征"""

JS_FRAMEWORKS = {
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
            r'(?:^|[\'"])(?:@react-|react-router|react-redux|react-query|react-hook-form|react-dom)(?:[\'"]|$)',
            # React导入语句
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]react(?:/[^\'"]+)?[\'"]',
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]@react',
            # React配置文件
            r'(?:^|/)\.react(?:rc|\.config)\.[jt]s$',
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
            r'(?:^|\s+):(?:class|style|src|href|alt|title|placeholder|value|type|disabled|required)="[^"]*"',
            # Vue相关包
            r'(?:^|[\'"])(?:@vue/|vue-router|vuex|@vitejs/plugin-vue)(?:[\'"]|$)',
            # Vue组件和API
            r'(?:^|[^\w.])(?:defineComponent|onMounted|onUnmounted|onUpdated|ref|reactive|computed|watch)\s*\(',
            # Vue文件和模板
            r'<template>[\s\S]*?</template>',
            r'\.vue$',
            # Vue导入语句
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]vue(?:/[^\'"]+)?[\'"]',
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]@vue',
            # Vue配置文件
            r'(?:^|/)vue\.config\.[jt]s$',
        ]
    },
    'Angular': {
        'patterns': [
            r'(?:^|/)angular(?:\.min)?\.js$',                    # Angular主文件
            r'(?:^|[\'"])@angular/(?:core|common|platform-browser|forms)(?:[\'"]|$)', # Angular包
            r'(?:^|[^\w.])@(?:Component|Injectable|NgModule)\s*\(', # 装饰器
            r'(?:^|[^\w.])(?:ngOnInit|ngOnDestroy|ngAfterViewInit)\b', # 生命周期
            r'(?:^|\s)ng-(?:controller|app|model|bind|repeat|if|show|hide)(?:\s|$)', # 指令
            r'(?:^|/)angular-route(?:\.min)?\.js$',             # 路由
            r'(?:^|[\'"])(?:zone\.js|rxjs)(?:[\'"]|$)',        # 依赖
        ]
    }
} 