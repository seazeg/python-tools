"""技术特征签名模块"""

from .web_servers import WEB_SERVERS
from .web_frameworks import WEB_FRAMEWORKS
from .js_frameworks import JS_FRAMEWORKS
from .build_tools import BUILD_TOOLS
from .js_libraries import JS_LIBRARIES
from .video_players import VIDEO_PLAYERS
from .chart_tools import CHART_TOOLS
from .cdn_providers import CDN_PROVIDERS
from .analytics import ANALYTICS

# 合并所有特征签名
TECH_SIGNATURES = {
    'Web服务器': WEB_SERVERS,
    'Web框架': WEB_FRAMEWORKS,
    'JavaScript框架': JS_FRAMEWORKS,
    '构建工具': BUILD_TOOLS,
    'JavaScript库': JS_LIBRARIES,
    '视频播放器': VIDEO_PLAYERS,
    '图表工具': CHART_TOOLS,
    'CDN': CDN_PROVIDERS,
    '分析': ANALYTICS
} 