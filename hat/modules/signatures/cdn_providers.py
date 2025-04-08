"""CDN提供商特征"""

CDN_PROVIDERS = {
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
    'Cloudflare': {
        'patterns': [
            r'\.cloudflare\.com/',
            r'cdnjs\.cloudflare\.com/',
            r'cloudflare-static/',
            r'cloudflare-ipfs\.com/',
        ],
        'headers': [
            'cf-ray',
            'cf-cache-status',
            'cf-request-id',
            'cf-connecting-ip',
            'cf-ipcountry',
            'cf-visitor',
        ]
    }
} 