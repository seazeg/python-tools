"""服务端框架检测签名"""
import re

SERVER_FRAMEWORKS = {
    'Django': {
        'headers': {
            'Server': [r'WSGIServer/'],
            'X-Django-Version': [r'.*']
        },
        'cookies': [r'django_', r'csrftoken'],
        'patterns': [
            r'__admin_media_prefix__',
            r'django-\w+',
            r'djangoproject',
            r'csrfmiddlewaretoken',
            r'admin/(?:css|img|js)/',
            r'django\.contrib',
            r'django\.core',
            r'django\.template',
            r'django\.utils'
        ]
    },
    'Flask': {
        'headers': {
            'Server': [r'Werkzeug'],
            'X-Flask-Version': [r'.*']
        },
        'patterns': [
            r'flask\.',
            r'werkzeug\.',
            r'pocoo\.org',
            r'flask_[a-z]+',
            r'Flask(?:Form|Script|Cache|Admin|Login|Upload|RESTful)',
            r'jinja2\.environment'
        ]
    },
    'FastAPI': {
        'headers': {
            'Server': [r'uvicorn'],
            'X-Process-Time': [r'.*']
        },
        'patterns': [
            r'fastapi\.',
            r'uvicorn\.',
            r'starlette\.',
            r'pydantic\.',
            r'/docs(?:#|$)',  # Swagger UI
            r'/redoc(?:#|$)'  # ReDoc
        ]
    },
    'Spring Boot': {
        'headers': {
            'X-Application-Context': [r'.*'],
            'X-Spring-Version': [r'.*']
        },
        'cookies': [r'JSESSIONID'],
        'patterns': [
            r'org\.springframework\.',
            r'spring-boot',
            r'spring-core',
            r'spring-web',
            r'spring-context',
            r'spring-security',
            r'spring-data',
            r'spring-cloud',
            r'spring-test',
            r'spring-boot-starter-\w+'
        ]
    },
    'Laravel': {
        'headers': {
            'Set-Cookie': [r'laravel_session'],
            'X-Laravel-Version': [r'.*']
        },
        'patterns': [
            r'laravel_session',
            r'Illuminate\\',
            r'laravel-\w+',
            r'vendor/laravel/',
            r'artisan',
            r'resources/views/',
            r'storage/framework/',
            r'\.blade\.php'
        ]
    },
    'Express': {
        'headers': {
            'X-Powered-By': [r'Express'],
            'ETag': [r'W/.*']  # Express默认使用弱ETag
        },
        'patterns': [
            r'express\.',
            r'node_modules/express',
            r'app\.(?:get|post|put|delete|use|all|set|engine)',
            r'express-session',
            r'express-validator',
            r'express-middleware',
            r'body-parser',
            r'morgan',
            r'passport'
        ]
    },
    'Nest.js': {
        'headers': {
            'X-Powered-By': [r'NestJS'],
            'X-NestJS-Version': [r'.*']
        },
        'patterns': [
            r'@nestjs/',
            r'nest-\w+',
            r'nestjs',
            r'@Injectable',
            r'@Controller',
            r'@Module',
            r'@Inject',
            r'NestFactory'
        ]
    },
    'Koa': {
        'headers': {
            'X-Powered-By': [r'koa'],
            'koa-version': [r'.*']
        },
        'patterns': [
            r'koa\.',
            r'koa-\w+',
            r'koajs',
            r'app\.use\(async',
            r'ctx\.',
            r'next\(\)'
        ]
    },
    'ThinkPHP': {
        'headers': {
            'X-Powered-By': [r'ThinkPHP'],
            'Server': [r'ThinkPHP']
        },
        'patterns': [
            r'thinkphp',
            r'think-\w+',
            r'topthink',
            r'application/index/',
            r'public/static/',
            r'think\\',
            r'ThinkPHP[\d.]+'
        ]
    }
}

def enhance_framework_detection(headers: dict, content: str) -> list:
    """增强的服务端框架检测"""
    detected_frameworks = []
    
    # 将headers转换为不区分大小写的字典
    headers = {k.lower(): v for k, v in headers.items()}
    
    for framework, signatures in SERVER_FRAMEWORKS.items():
        # 检查headers
        if 'headers' in signatures:
            for header_name, patterns in signatures['headers'].items():
                header_value = headers.get(header_name.lower(), '')
                if header_value:
                    for pattern in patterns:
                        if pattern == r'.*' or any(re.search(pattern, v, re.I) for v in header_value.split(';')):
                            detected_frameworks.append(framework)
                            break
        
        # 检查cookies
        if 'cookies' in signatures:
            cookie_header = headers.get('set-cookie', '')
            if cookie_header:
                for pattern in signatures['cookies']:
                    if re.search(pattern, cookie_header, re.I):
                        detected_frameworks.append(framework)
                        break
        
        # 检查内容模式
        if 'patterns' in signatures and content:
            for pattern in signatures['patterns']:
                if re.search(pattern, content, re.I):
                    detected_frameworks.append(framework)
                    break
    
    return list(set(detected_frameworks)) 