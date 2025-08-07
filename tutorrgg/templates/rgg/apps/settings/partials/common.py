{% if is_plugin_loaded("minio") or is_plugin_loaded("s3") %}
# S3 common settings
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = "{{ OPENEDX_AWS_ACCESS_KEY }}"
AWS_SECRET_ACCESS_KEY = "{{ OPENEDX_AWS_SECRET_ACCESS_KEY }}"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_QUERYSTRING_AUTH = False
AWS_STORAGE_BUCKET_NAME = "{{ RGG_AWS_STORAGE_BUCKET_NAME }}"
{% endif %}

{% if is_plugin_loaded("minio") %}
# Minio specific settings
AWS_S3_ENDPOINT_URL = "{{ "https" if ENABLE_HTTPS else "http" }}://{{ MINIO_HOST }}"
AWS_S3_REGION_NAME = ""
{% endif %}

{% if is_plugin_loaded("s3") %}
# AWS S3 specific settings
AWS_S3_ENDPOINT_URL = None
AWS_S3_REGION_NAME = "{{ RGG_AWS_S3_REGION_NAME }}"
AWS_DEFAULT_ACL = {% if RGG_AWS_DEFAULT_ACL == "None" %}None{% else %}"{{ RGG_AWS_DEFAULT_ACL }}"{% endif %}
{% endif %}

DEFAULT_FILE_STORAGE = "{{ RGG_DEFAULT_FILE_STORAGE }}"

# Provide additional configuration parameters required by the specified DEFAULT_FILE_STORAGE backend.
DEFAULT_FILE_STORAGE_OPTIONS = "{{ RGG_DEFAULT_FILE_STORAGE_OPTIONS }}"

# hardcoded for gammification dashboard and leaderboard to properly use the media urls
STORE_RELATIVE_URLS = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "{{ RGG_MYSQL_DATABASE }}",
        "USER": "{{ RGG_MYSQL_USERNAME }}",
        "PASSWORD": "{{ RGG_MYSQL_PASSWORD }}",
        "HOST": "{{ MYSQL_HOST }}",
        "PORT": "{{ MYSQL_PORT }}",
        "OPTIONS": {
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": "redis://{% if REDIS_USERNAME and REDIS_PASSWORD %}{{ REDIS_USERNAME }}:{{ REDIS_PASSWORD }}{% endif %}@{{ REDIS_HOST }}:{{ REDIS_PORT }}/{{ RGG_REDIS_DB }}",
        "OPTIONS": {
        },
    }
}

EDX_LMS_BASE_URL = "http://lms:8000"
EDX_API_KEY = "{{ EDX_API_KEY }}"

CELERY_BROKER_URL = "redis://{% if REDIS_USERNAME and REDIS_PASSWORD %}{{ REDIS_USERNAME }}:{{ REDIS_PASSWORD }}{% endif %}@{{ REDIS_HOST }}:{{ REDIS_PORT }}/{{ RGG_REDIS_DB }}"
CELERY_RESULT_BACKEND = "redis://{% if REDIS_USERNAME and REDIS_PASSWORD %}{{ REDIS_USERNAME }}:{{ REDIS_PASSWORD }}{% endif %}@{{ REDIS_HOST }}:{{ REDIS_PORT }}/{{ RGG_REDIS_DB }}"

OAUTH2_PROVIDER_URL = "{{ "https" if ENABLE_HTTPS else "http" }}://{{ LMS_HOST }}/oauth2"
SOCIAL_AUTH_EDX_OAUTH2_KEY = "{{ RGG_OAUTH2_KEY_SSO }}"
SOCIAL_AUTH_EDX_OAUTH2_SECRET = "{{ RGG_OAUTH2_SECRET }}"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "{{ "https" if ENABLE_HTTPS else "http" }}://{{ LMS_HOST }}"
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = "{{ "https" if ENABLE_HTTPS else "http" }}://{{ LMS_HOST }}/logout"

SESSION_COOKIE_SECURE = {{ "True" if ENABLE_HTTPS else "False" }}
CSRF_COOKIE_SECURE = {{ "True" if ENABLE_HTTPS else "False" }}
SESSION_COOKIE_NAME = "gamification_sessionid"

{{ patch("rgg-common-settings") }}
