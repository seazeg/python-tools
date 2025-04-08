"""CDN提供商特征"""

CDN_PROVIDERS = {
    'Cloudflare': {
        'headers': {
            'server': [r'(?i)cloudflare'],
            'cf-ray': [r'.*'],
            'cf-cache-status': [r'.*'],
            '__cfduid': [r'.*'],
            'x-fetch-attempts': [r'.*']
        },
        'patterns': [
            r'(?i)cloudflare\.com/cdn-cgi/',
            r'(?i)cdnjs\.cloudflare\.com',
            r'(?i)\.cloudflare\.net/',
            r'(?i)\.cloudflare\.com/',
            r'(?i)cloudflare-nginx',
            r'(?i)\/cdn-cgi\/'
        ]
    },
    'Akamai': {
        'headers': {
            'x-akamai-transformed': [r'.*'],
            'akamai-origin-hop': [r'.*'],
            'x-akamai-ssl-client-sid': [r'.*']
        },
        'patterns': [
            r'(?i)\.akamaihd\.net',
            r'(?i)\.akamai\.net',
            r'(?i)\.akamaized\.net',
            r'(?i)\.edgesuite\.net'
        ]
    },
    'Fastly': {
        'headers': {
            'fastly-debug-digest': [r'.*'],
            'x-fastly-request-id': [r'.*'],
            'x-served-by': [r'(?i)cache-.*-fastly']
        },
        'patterns': [
            r'(?i)\.fastly\.net',
            r'(?i)\.fastlylb\.net',
            r'(?i)\.fastly-edge\.com'
        ]
    },
    'AWS CloudFront': {
        'headers': {
            'x-amz-cf-id': [r'.*'],
            'x-amz-cf-pop': [r'.*'],
            'via': [r'(?i)cloudfront']
        },
        'patterns': [
            r'(?i)\.cloudfront\.net',
            r'(?i)\.amazonaws\.com',
            r'(?i)aws-cloudfront',
            r'(?i)\.awsstatic\.com'
        ]
    },
    '阿里云CDN': {
        'headers': {
            'server': [r'(?i)tengine', r'(?i)aliyun'],
            'via': [r'(?i)ali(?:yun)?cdn'],
            'x-swift-cachetime': [r'.*'],
            'ali-swift-global-savetime': [r'.*'],
            'x-oss-cdn-auth': [r'.*']
        },
        'patterns': [
            r'(?i)\.alicdn\.com',
            r'(?i)\.aliyuncs\.com',
            r'(?i)\.aliyun-inc\.com',
            r'(?i)\.alikunlun\.com',
            r'(?i)\.aliyuncdn\.com'
        ]
    },
    '腾讯云CDN': {
        'headers': {
            'server': [r'(?i)tencent', r'(?i)qcloud'],
            'x-daa-tunnel': [r'.*'],
            'x-cache-lookup': [r'.*'],
            'x-tc-cache': [r'.*']
        },
        'patterns': [
            r'(?i)\.qcloud\.com',
            r'(?i)\.myqcloud\.com',
            r'(?i)\.tencent-cloud\.net',
            r'(?i)\.qcloudcdn\.com',
            r'(?i)\.tencentcdn\.net'
        ]
    },
    '七牛云CDN': {
        'headers': {
            'x-qiniu-zone': [r'.*'],
            'x-qnm-cache': [r'.*'],
            'x-qiniu': [r'.*']
        },
        'patterns': [
            r'(?i)\.qiniucdn\.com',
            r'(?i)\.qiniudns\.com',
            r'(?i)\.qiniup\.com',
            r'(?i)\.qbox\.me',
            r'(?i)\.clouddn\.com'
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

def enhance_cdn_detection(headers: dict, content: str, js_resources: list) -> list:
    """增强的CDN检测"""
    detected_cdns = []
    
    # 检查响应头
    for cdn_name, signatures in CDN_PROVIDERS.items():
        # 检查头部特征
        if 'headers' in signatures:
            for header, patterns in signatures['headers'].items():
                header_value = headers.get(header, '').lower()
                if header_value:
                    for pattern in patterns:
                        if re.search(pattern, header_value, re.I):
                            detected_cdns.append(cdn_name)
                            break
        
        # 检查内容模式
        if 'patterns' in signatures:
            # 检查页面内容
            for pattern in signatures['patterns']:
                if re.search(pattern, content, re.I):
                    detected_cdns.append(cdn_name)
                    break
                    
            # 检查JavaScript资源URL
            for resource in js_resources:
                for pattern in signatures['patterns']:
                    if re.search(pattern, resource, re.I):
                        detected_cdns.append(cdn_name)
                        break

    # 移除重复项
    return list(set(detected_cdns)) 