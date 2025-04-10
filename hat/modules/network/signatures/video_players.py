"""视频播放器特征"""

VIDEO_PLAYERS = {
    'Video.js': {
        'patterns': [
            r'(?:^|/)video(?:-js)?(?:\.min)?\.js$',              # 文件名匹配
            r'(?:^|/)videojs(?:\.min)?\.css$',                   # CSS文件
            r'(?:^|\s)(?:video-js|vjs-(?:big-play-button|control|text-track))(?:\s|$)', # CSS类
            r'data-setup=[\'"]\{[^\}]*?\}[\'"]',                # 配置属性
            r'(?:^|[^\w.])require\([\'"]video\.js[\'"]\)',      # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]video\.js[\'"]', # ES6导入
            r'(?:^|[\'"])@videojs/[a-z-]+(?:[\'"]|$)',         # 插件包
        ]
    },
    'Plyr': {
        'patterns': [
            r'(?:^|/)plyr(?:\.min)?\.js$',                      # 文件名匹配
            r'(?:^|/)plyr(?:\.min)?\.css$',                     # CSS文件
            r'(?:^|[^\w.])new\s+Plyr\s*\(',                     # 实例化
            r'(?:^|\s)plyr(?:__controls|__menu|__progress|__volume)(?:\s|$)', # CSS类
            r'data-plyr-(?:provider|embed-id)=[\'"][^\'"]*[\'"]', # 数据属性
            r'(?:^|[^\w.])require\([\'"]plyr[\'"]\)',          # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]plyr[\'"]', # ES6导入
        ]
    },
    'DPlayer': {
        'patterns': [
            r'(?:^|/)DPlayer(?:\.min)?\.js$',                   # 文件名匹配
            r'(?:^|/)DPlayer(?:\.min)?\.css$',                  # CSS文件
            r'(?:^|[^\w.])new\s+DPlayer\s*\(',                  # 实例化
            r'(?:^|\s)dplayer(?:-mobile)?(?:-(?:danmaku|controller|bezel|loading|icon|menu|notice|setting|subtitle|volume|quality|progress|mask|contextmenu|comment|logo|live))?(?:\s|$)', # CSS类
            r'data-dplayer-(?:video|danmaku|subtitle)=[\'"][^\'"]*[\'"]', # 数据属性
            r'(?:^|[^\w.])require\([\'"]dplayer[\'"]\)',       # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]dplayer[\'"]', # ES6导入
            r'(?:^|/)dplayer/dist/',                           # 目录结构
            r'(?:^|[\'"])@dplayer/[a-z-]+(?:[\'"]|$)',        # npm包
        ]
    },
    'ArtPlayer': {
        'patterns': [
            r'(?:^|/)artplayer(?:\.min)?\.js$',                # 文件名匹配
            r'(?:^|/)artplayer(?:\.min)?\.css$',               # CSS文件
            r'(?:^|[^\w.])new\s+Artplayer\s*\(',               # 实例化
            r'(?:^|\s)art-video-player(?:\s|$)',               # CSS类
            r'data-art-(?:video|subtitle|thumbnail)=[\'"][^\'"]*[\'"]', # 数据属性
            r'(?:^|[^\w.])require\([\'"]artplayer[\'"]\)',    # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]artplayer[\'"]', # ES6导入
        ]
    },
    'Aliplayer': {
        'patterns': [
            r'(?:^|/)aliplayer(?:-(?:h5|flash))?(?:\.min)?\.js$', # 文件名匹配
            r'(?:^|/)aliplayer(?:\.min)?\.css$',                # CSS文件
            r'(?:^|[^\w.])new\s+Aliplayer\s*\(',                # 实例化
            r'(?:^|\s)prism-player(?:\s|$)',                    # CSS类
            r'data-player-(?:type|video|config)=[\'"][^\'"]*[\'"]', # 数据属性
            r'(?:^|[^\w.])alicdn\.com/[^"\']+aliplayer',       # CDN路径
            r'(?:^|[^\w.])Aliplayer\.events\b',                # 事件API
        ]
    },
    'TCPlayer': {
        'patterns': [
            r'(?:^|/)tcplayer(?:-(?:lite|web))?(?:\.min)?\.js$', # 文件名匹配
            r'(?:^|[^\w.])new\s+TCPlayer\s*\(',                 # 实例化
            r'(?:^|\s)vcp-player(?:\s|$)',                      # CSS类
            r'data-tc-(?:player|video)=[\'"][^\'"]*[\'"]',     # 数据属性
            r'(?:^|/)tcplayer\.v\d+\.(?:min\.)?js$',          # 版本文件
            r'(?:^|[^\w.])cloud\.tencent\.com/[^"\']+tcplayer', # CDN路径
            r'(?:^|[^\w.])TCPlayer\.defaults\b',               # 配置API
        ]
    },
    'XGPlayer': {
        'patterns': [
            r'(?:^|/)xgplayer(?:-(?:lite|mp4))?(?:\.min)?\.js$', # 文件名匹配
            r'(?:^|[^\w.])new\s+Player\s*\(',                   # 实例化
            r'(?:^|\s)xgplayer(?:-(?:skin|controls|progress))(?:\s|$)', # CSS类
            r'data-xg-(?:player|video)=[\'"][^\'"]*[\'"]',     # 数据属性
            r'(?:^|/)xgplayer\.v\d+\.(?:min\.)?js$',          # 版本文件
            r'(?:^|[^\w.])require\([\'"]xgplayer[\'"]\)',     # CommonJS引入
            r'(?:^|[^\w.])import\s+[{}\s\w]+\s+from\s+[\'"]xgplayer[\'"]', # ES6导入
        ]
    },
    'Brightcove': {
        'patterns': [
            r'(?:^|/)brightcove(?:-player)?(?:\.min)?\.js$',    # 文件名匹配
            r'(?:^|[^\w.])players\.brightcove\.(?:net|com)',    # CDN域名
            r'(?:^|\s)videojs-bc-player(?:\s|$)',               # 播放器类名
            r'data-video-id=[\'"][0-9]+[\'"]',                 # 视频ID属性
            r'data-account=[\'"][0-9]+[\'"]',                  # 账户ID属性
            r'data-player=[\'"][a-zA-Z0-9_-]+[\'"]',          # 播放器ID属性
            r'data-embed=[\'"]default[\'"]',                   # 嵌入类型
            r'(?:^|/)bc(?:\.min)?\.js$',                       # 核心文件
            r'(?:^|\s)brightcove-(?:player|videojs)(?:\s|$)',  # 相关文件
            r'(?:^|[^\w.])videojs\.getPlayer\([\'"]brightcove', # API调用
            r'(?:^|[^\w.])brightcove\.createExperiences?\(\)', # 旧版API
        ]
    }
} 