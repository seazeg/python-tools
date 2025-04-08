"""UI框架特征"""

UI_FRAMEWORKS = {
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
} 