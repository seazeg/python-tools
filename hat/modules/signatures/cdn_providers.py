"""CDN提供商特征"""

CDN_PROVIDERS = {
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
    },
    'Netlify': {
        'patterns': [
            r'\.netlify\.(?:com|app)/',                    # Netlify域名
            r'netlify-(?:cdn|builds)',                     # 资源标识
            r'netlify\.com/(?:sites|api)',                # API路径
            r'netlify-plugin-[a-z-]+',                    # Netlify插件
            r'netlify\.toml',                             # 配置文件
            r'_redirects|_headers',                        # Netlify配置文件
            r'deploy-preview-\d+--[a-z0-9-]+\.netlify\.app', # 预览环境
            r'app\.netlify\.com/sites/[a-z0-9-]+',        # 管理界面
        ],
        'headers': [
            'x-nf-request-id',                            # 请求ID
            'x-netlify',                                  # Netlify标识
            'x-nf-pop',                                   # POP位置
            'x-nf-count',                                 # 请求计数
            'x-nf-cache-status',                         # 缓存状态
            'x-nf-edge-cache',                           # 边缘缓存
            'x-nf-serve-time',                           # 服务时间
        ]
    }
} 