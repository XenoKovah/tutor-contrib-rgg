{% if IS_MINIO_ENABLED %}
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = "{{ OPENEDX_AWS_ACCESS_KEY }}"
AWS_SECRET_ACCESS_KEY = "{{ OPENEDX_AWS_SECRET_ACCESS_KEY }}"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_QUERYSTRING_AUTH = False
AWS_STORAGE_BUCKET_NAME = "{{ RGG_AWS_STORAGE_BUCKET_NAME }}"
AWS_S3_ENDPOINT_URL = "{{ "https" if ENABLE_HTTPS else "http" }}://{{ MINIO_HOST }}"
AWS_S3_REGION_NAME = ""
{% endif %}

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

MONGO_URL = "mongodb://mongodb:27017/"
MONGO_DATABASE = "gamma_data"

EDX_LMS_BASE_URL = "http://lms:8000"
EDX_API_KEY = "{{ EDX_API_KEY }}"

CELERY_BROKER_URL = "redis://redis:6379/2"

{{ patch("rgg-common-settings") }}
