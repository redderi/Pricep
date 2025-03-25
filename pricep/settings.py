from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env()  # Чтение .env файла, убедитесь, что он существует

API_KEY = env("API_KEY", default="11111111")
DEBUG = env.bool("DEBUG", default=False)  # Изменил значение по умолчанию на False, для продакшн
SECRET_KEY = env("SECRET_KEY", default="22222222")


# Убедитесь, что DEBUG установлен в False в продакшн-среде
DEBUG = False

ALLOWED_HOSTS = ['*']  # Здесь укажите ваш домен или IP-адрес, например: ['yourdomain.com', 'localhost']

# Настройка безопасности
SECURE_SSL_REDIRECT = False  # Перенаправление HTTP на HTTPS
SECURE_HSTS_SECONDS = 31536000  # Включение HSTS для принудительного использования HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Включение HSTS для поддоменов
SECURE_HSTS_PRELOAD = True  # Рекомендуется использовать для обеспечения полной защиты HSTS

# Настройки для работы с HTTPS
CSRF_COOKIE_SECURE = False  # Защищенные cookies при HTTPS
SESSION_COOKIE_SECURE = False  # Защищенные сессии при HTTPS

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pricep.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'pricep.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Не отключать встроенные логгеры
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)-8s %(asctime)s %(name)s: %(message)s',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
        'simple': {
            'format': '%(levelname)-8s %(asctime)s %(message)s',
        },
        'verbose': {
            'format': '%(levelname)-8s %(asctime)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',  # Используем цветной формат
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',  # Используем расширенный формат для файлов
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],  # Отправляем логи в консоль и файл
            'level': 'WARNING',  # Минимальный уровень логирования
            'propagate': True,  # Передаём логи родительским логгерам
        },
        'pricep': {  
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
