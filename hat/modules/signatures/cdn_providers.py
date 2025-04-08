"""CDN提供商特征"""

CDN_PROVIDERS = {
    'Cloudflare': {
        'patterns': [
            r'^https?://[^/]*cloudflare\.com/',                # CDN域名
            r'^https?://[^/]*cdnjs\.cloudflare\.com/',        # CDNJS域名
            r'^https?://[^/]*cloudflare-dns\.com/',           # DNS域名
            r'^https?://[^/]*workers\.dev/',                  # Workers域名
        ],
        'headers': [
            'cf-ray',                                         # 请求ID
            'cf-cache-status',                                # 缓存状态
            'cf-connecting-ip',                               # 客户端IP
            'cf-worker',                                      # Worker标识
            'cf-visitor',                                     # 访客信息
            'cf-ipcountry',                                   # IP国家/地区
        ]
    },
    'Akamai': {
        'patterns': [
            r'^https?://[^/]*\.akamai(?:\.net|\.com|\.co|\.cn|edge\.net)/', # Akamai域名族
            r'^https?://[^/]*\.akamaized\.net/',              # 优化域名
            r'^https?://[^/]*\.akamaihd\.net/',               # 媒体域名
            r'^https?://[^/]*\.edgesuite\.net/',              # 传统域名
            r'^https?://[^/]*\.edgekey\.net/',                # SSL域名
        ],
        'headers': [
            'x-akamai-transformed',                           # 转换标记
            'akamai-origin-hop',                              # 源站跳转
            'x-akamai-request-id',                            # 请求ID
            'x-akamai-cache-',                                # 缓存信息
            'akamai-x-cache-on',                              # 缓存状态
            'akamai-x-get-cache-key',                         # 缓存键
            'akamai-x-check-cacheable',                       # 可缓存检查
            'akamai-x-feo-trace',                             # 前端优化跟踪
            'x-akamai-ssl-client-sid',                        # SSL会话ID
            'x-akamai-edgescape'                              # 地理位置信息
        ]
    },
    'Fastly': {
        'patterns': [
            r'^https?://[^/]*\.fastly\.net/',                 # Fastly域名
            r'^https?://[^/]*\.fastly-edge\.com/',            # 边缘域名
            r'^https?://[^/]*\.fastlylb\.net/',               # 负载均衡域名
        ],
        'headers': [
            'fastly-debug-digest',                            # 调试摘要
            'x-served-by',                                    # 服务节点
            'x-cache-hits',                                   # 缓存命中
            'x-timer',                                        # 计时信息
            'x-fastly-request-id'                             # 请求ID
        ]
    },
    'AWS CloudFront': {
        'patterns': [
            r'^https?://[^/]*\.cloudfront\.net/',             # CloudFront域名
            r'^https?://[^/]*\.amazonaws\.com/',              # AWS域名
        ],
        'headers': [
            'x-amz-cf-id',                                    # CloudFront ID
            'x-amz-cf-pop',                                   # 接入点
            'x-amz-id-2',                                     # 请求ID
            'x-amz-request-id',                               # 请求ID
            'via'                                             # 代理信息
        ]
    },
    '阿里云CDN': {
        'patterns': [
            r'^https?://[^/]*\.alicdn\.com/',                 # 阿里CDN域名
            r'^https?://[^/]*\.aliyuncs\.com/',               # 阿里云域名
            r'^https?://[^/]*\.aliyun-inc\.com/',             # 内部域名
        ],
        'headers': [
            'ali-swift-global-savetime',                      # 全局保存时间
            'x-swift-cachetime',                              # 缓存时间
            'x-oss-request-id',                               # OSS请求ID
            'x-oss-cdn-auth',                                 # CDN认证
            'via'                                             # 代理信息
        ]
    },
    '腾讯云CDN': {
        'patterns': [
            r'^https?://[^/]*\.qcloud\.com/',                 # 腾讯云域名
            r'^https?://[^/]*\.cdntip\.com/',                 # CDN域名
            r'^https?://[^/]*\.tcloudscdn\.com/',             # 新CDN域名
            r'^https?://[^/]*\.myqcloud\.com/',               # 对象存储域名
        ],
        'headers': [
            'x-daa-tunnel',                                   # 隧道信息
            'x-cache-lookup',                                 # 缓存查询
            'x-tencent-acceleration',                         # 加速信息
            'via'                                             # 代理信息
        ]
    },
    '七牛云CDN': {
        'patterns': [
            r'^https?://[^/]*\.qiniucdn\.com/',               # 七牛CDN域名
            r'^https?://[^/]*\.qiniudns\.com/',               # DNS域名
            r'^https?://[^/]*\.qbox\.me/',                    # 存储域名
            r'^https?://[^/]*\.qiniu\.com/',                  # 主域名
        ],
        'headers': [
            'x-qiniu-zone',                                   # 区域信息
            'x-reqid',                                        # 请求ID
            'x-qnm-cache',                                    # 缓存信息
            'via'                                             # 代理信息
        ]
    },
    'Netlify': {
        'patterns': [
            r'^https?://[^/]*\.netlify\.(?:com|app)/',        # Netlify域名
            r'^https?://[^/]*\.netlify\.app/',                # 应用域名
            r'^https?://[^/]*\.netlifyglobalcdn\.com/',       # CDN域名
        ],
        'headers': [
            'x-nf-request-id',                                # 请求ID
            'x-netlify',                                      # Netlify标识
            'x-nf-pop',                                       # POP位置
            'x-nf-count',                                     # 请求计数
            'x-nf-cache-status',                              # 缓存状态
            'x-nf-edge-cache',                                # 边缘缓存
            'x-nf-serve-time',                                # 服务时间
            'via'                                             # 代理信息
        ]
    }
} 