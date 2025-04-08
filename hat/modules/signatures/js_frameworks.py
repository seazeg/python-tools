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
} 