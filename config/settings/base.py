from pathlib import Path
import os
from datetime import timedelta
import environ
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR/".env")
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4.1-mini")
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG",default=False)


ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "leads",
    "common",
    "clinics",
    "channels",
    "conversations.apps.ConversationsConfig",
    "appointments",
    "core_events",
    "ai.apps.AiConfig",

    "accounts",
    "rest_framework_simplejwt.token_blacklist",


]

MIDDLEWARE = ["django.middleware.security.SecurityMiddleware",
              "django.contrib.sessions.middleware.SessionMiddleware",
              "django.middleware.csrf.CsrfViewMiddleware",
              "corsheaders.middleware.CorsMiddleware",
              "django.middleware.common.CommonMiddleware",
              "django.contrib.auth.middleware.AuthenticationMiddleware",
              "django.contrib.messages.middleware.MessageMiddleware",
              "django.middleware.clickjacking.XFrameOptionsMiddleware",
              ]


ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"




TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),

    }

}
ASGI_APPLICATION = "config.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": "redis://127.0.0.1:6379",
                    "socket_timeout": None,
                }
            ],
        },
    },
}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    )
}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME":timedelta(minutes=30),
              "REFRESH_TOKEN_LIFETIME":timedelta(days=30),
              "ROTATE_REFRESH_TOKENS":True,
              "BLACKLIST_AFTER_ROTATION": True,
              }

CORS_ALLOWED_ORIGINS = ["http://localhost:5173",
    "http://localhost:5174",]
CSRF_TRUSTED_ORIGINS = [
    "https://clinicai-production-2d38.up.railway.app",
]
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

