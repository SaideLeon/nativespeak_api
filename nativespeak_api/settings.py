import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'change-me-for-production'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    
    # Unfold admin theme
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Crispy forms for Unfold form templates
    'crispy_forms',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nativespeak_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # include project templates directory so Unfold can override admin templates if needed
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nativespeak_api.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
# allow a local static/ folder for development
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy forms config to use Unfold's template pack (optional)
CRISPY_TEMPLATE_PACK = 'unfold_crispy'
CRISPY_ALLOWED_TEMPLATE_PACKS = ['unfold_crispy']

# Unfold optional defaults will be set after UNFOLD dict is declared further below

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]
}

# Enable automatic OpenAPI schema generation and ensure renderers include
# JSON and the browsable API. AutoSchema will pick up viewsets and @action
# endpoints so they show up in the generated documentation.
REST_FRAMEWORK.setdefault('DEFAULT_SCHEMA_CLASS', 'rest_framework.schemas.openapi.AutoSchema')
REST_FRAMEWORK.setdefault('DEFAULT_RENDERER_CLASSES', [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
])

# Basic Unfold configuration (optional tweaks)
UNFOLD = {
    # Example: set environment label for admin (development, staging, production)
    # 'ENVIRONMENT_LABEL': 'development',
    "SITE_TITLE": "NativeSpeak Admin",
    "SITE_HEADER": "NativeSpeak",
    "SITE_ICON": "material-symbols:school",
    # Outras opções podem ser adicionadas conforme necessário
}

# Ensure some defaults exist if not provided
# SIDEBAR is expected to be a mapping by Unfold internals
UNFOLD.setdefault('SIDEBAR', {'enabled': True})
UNFOLD.setdefault('COMMAND', {'search_models': False})

# Some users may set UNFOLD['SIDEBAR'] to a boolean value; Unfold expects a mapping
# so normalize it here if needed.
if not isinstance(UNFOLD.get('SIDEBAR'), dict):
    sidebar_value = UNFOLD.get('SIDEBAR')
    if isinstance(sidebar_value, bool):
        UNFOLD['SIDEBAR'] = {
            'enabled': sidebar_value,
            'show_search': False,
            'command_search': False,
            'show_all_applications': False,
            'navigation': [],
        }
    else:
        # fallback to defaults
        UNFOLD['SIDEBAR'] = {'enabled': True, 'navigation': []}
