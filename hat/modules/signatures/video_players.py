"""视频播放器特征"""

VIDEO_PLAYERS = {
    'Video.js': {
        'patterns': [
            r'(?:^|/)video(?:-js)?(?:\.min)?\.js$',              # 文件名匹配
            r'videojs(?:\.min)?\.css',                           # CSS文件
            r'(?:^|[^\w.])videojs\s*\(',                         # 实例化
            r'video-js|vjs-(?:big-play-button|control|text-track)', # CSS类
            r'data-setup=[\'"]\{[^\}]*?\}[\'"]',                # 配置属性
            r'(?:^|[^\w.])require\([\'"]video\.js[\'"]\)',      # CommonJS引入
            r'import\s+[{}\s\w]+\s+from\s+[\'"]video\.js[\'"]', # ES6导入
            r'@videojs/[a-z-]+',                                # 插件包
        ]
    },
    'Plyr': {
        'patterns': [
            r'(?:^|/)plyr(?:\.min)?\.js$',                      # 文件名匹配
            r'plyr(?:\.min)?\.css',                             # CSS文件
            r'(?:^|[^\w.])new\s+Plyr\s*\(',                     # 实例化
            r'plyr(?:__controls|__menu|__progress|__volume)',   # CSS类
            r'data-plyr-(?:provider|embed-id)',                 # 数据属性
            r'(?:^|[^\w.])require\([\'"]plyr[\'"]\)',          # CommonJS引入
            r'import\s+[{}\s\w]+\s+from\s+[\'"]plyr[\'"]',     # ES6导入
        ]
    },
    'DPlayer': {
        'patterns': [
            r'(?:^|/)DPlayer(?:\.min)?\.js$',                   # 文件名匹配
            r'DPlayer(?:\.min)?\.css',                          # CSS文件
            r'(?:^|[^\w.])new\s+DPlayer\s*\(',                  # 实例化
            r'dplayer(?:-mobile)?(?:-[a-z-]+)?',               # CSS类
            r'data-dplayer-(?:video|danmaku|subtitle)',        # 数据属性
            r'(?:^|[^\w.])require\([\'"]dplayer[\'"]\)',       # CommonJS引入
            r'import\s+[{}\s\w]+\s+from\s+[\'"]dplayer[\'"]',  # ES6导入
        ]
    },
    'ArtPlayer': {
        'patterns': [
            r'(?:^|/)artplayer(?:\.min)?\.js$',                # 文件名匹配
            r'artplayer(?:\.min)?\.css',                       # CSS文件
            r'(?:^|[^\w.])new\s+Artplayer\s*\(',               # 实例化
            r'art-video-player',                               # CSS类
            r'data-art-(?:video|subtitle|thumbnail)',          # 数据属性
            r'(?:^|[^\w.])require\([\'"]artplayer[\'"]\)',    # CommonJS引入
            r'import\s+[{}\s\w]+\s+from\s+[\'"]artplayer[\'"]', # ES6导入
        ]
    },
    'Aliplayer': {
        'patterns': [
            r'(?:^|/)aliplayer(?:-(?:h5|flash))?(?:\.min)?\.js$', # 文件名匹配
            r'aliplayer(?:\.min)?\.css',                        # CSS文件
            r'(?:^|[^\w.])new\s+Aliplayer\s*\(',                # 实例化
            r'prism-player',                                    # CSS类
            r'data-player-(?:type|video|config)',              # 数据属性
            r'alicdn\.com/[^"\']+aliplayer',                   # CDN路径
            r'Aliplayer\.events',                              # 事件API
        ]
    },
    'TCPlayer': {
        'patterns': [
            r'(?:^|/)tcplayer(?:-(?:lite|web))?(?:\.min)?\.js$', # 文件名匹配
            r'(?:^|[^\w.])new\s+TCPlayer\s*\(',                 # 实例化
            r'vcp-player',                                      # CSS类
            r'data-tc-(?:player|video)',                       # 数据属性
            r'tcplayer\.v\d+\.(?:min\.)?js',                   # 版本文件
            r'cloud\.tencent\.com/[^"\']+tcplayer',           # CDN路径
            r'TCPlayer\.defaults',                             # 配置API
        ]
    },
    'XGPlayer': {
        'patterns': [
            r'(?:^|/)xgplayer(?:-(?:lite|mp4))?(?:\.min)?\.js$', # 文件名匹配
            r'(?:^|[^\w.])new\s+Player\s*\(',                   # 实例化
            r'xgplayer(?:-(?:skin|controls|progress))',        # CSS类
            r'data-xg-(?:player|video)',                       # 数据属性
            r'xgplayer\.v\d+\.(?:min\.)?js',                  # 版本文件
            r'(?:^|[^\w.])require\([\'"]xgplayer[\'"]\)',     # CommonJS引入
            r'import\s+[{}\s\w]+\s+from\s+[\'"]xgplayer[\'"]', # ES6导入
        ]
    }
} 