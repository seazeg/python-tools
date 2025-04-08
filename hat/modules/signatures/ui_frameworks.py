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
    },
    'Animate.css': {
        'patterns': [
            r'(?:^|/)animate(?:\.min)?\.css$',                  # 主文件
            # 动画类名 - 入场动画
            r'(?:^|\s)animate__(?:bounce|flash|pulse|rubberBand|shakeX|shakeY|headShake|swing|tada|wobble|jello|heartBeat)(?:\s|$)',
            # 淡入动画
            r'(?:^|\s)animate__fade(?:In|InDown|InDownBig|InLeft|InLeftBig|InRight|InRightBig|InUp|InUpBig)(?:\s|$)',
            # 淡出动画
            r'(?:^|\s)animate__fade(?:Out|OutDown|OutDownBig|OutLeft|OutLeftBig|OutRight|OutRightBig|OutUp|OutUpBig)(?:\s|$)',
            # 滑动动画
            r'(?:^|\s)animate__slide(?:InDown|InLeft|InRight|InUp|OutDown|OutLeft|OutRight|OutUp)(?:\s|$)',
            # 缩放动画
            r'(?:^|\s)animate__(?:zoom|flip)(?:In|InDown|InLeft|InRight|InUp|Out|OutDown|OutLeft|OutRight|OutUp)(?:\s|$)',
            # 特殊动画
            r'(?:^|\s)animate__(?:lightSpeedIn|lightSpeedOut|rotateIn|rotateOut|hinge|jackInTheBox|rollIn|rollOut)(?:\s|$)',
            # 基础类和修饰符
            r'(?:^|\s)animate__animated(?:\s|$)',               # 基础类
            r'(?:^|\s)animate__(?:infinite|delay-[1-5]s|slow|slower|fast|faster)(?:\s|$)', # 修饰符
            # CDN引用
            r'(?:^|[\'"])https?://cdnjs\.cloudflare\.com/ajax/libs/animate\.css/[^\'"]*/animate\.(?:min\.)?css(?:[\'"]|$)',
            r'(?:^|[\'"])https?://cdn\.jsdelivr\.net/npm/animate\.css@[^\'"]*/animate\.(?:min\.)?css(?:[\'"]|$)',
            # npm包引用
            r'(?:^|[\'"])animate\.css(?:[\'"]|$)',
            # 导入语句
            r'(?:^|[^\w.])import\s+[\'"]animate\.css[\'"]',
            r'(?:^|[^\w.])require\([\'"]animate\.css[\'"]\)',
        ]
    }
} 