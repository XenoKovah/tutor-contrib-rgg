{% if IS_MINIO_ENABLED %}
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = "{{ OPENEDX_AWS_ACCESS_KEY }}"
AWS_SECRET_ACCESS_KEY = "{{ OPENEDX_AWS_SECRET_ACCESS_KEY }}"
AWS_STORAGE_BUCKET_NAME = "{{ RGG_AWS_STORAGE_BUCKET_NAME }}"
AWS_S3_ENDPOINT_URL = "{{ RGG_AWS_S3_ENDPOINT_URL }}"
AWS_S3_REGION_NAME = "{{ RGG_AWS_S3_REGION_NAME }}"
# hardcoded for gammification dashboard and leaderbord to properly use the media urls
STORE_RELATIVE_URLS = False
{% endif %}  # TODO: add s3 support
