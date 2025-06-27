from ..devstack import *

{% if IS_MINIO_ENABLED %}
AWS_S3_ENDPOINT_URL = "http://{{ MINIO_HOST }}:9000"
{% endif %}

{% include "rgg/apps/settings/partials/common.py" %}

EDX_LMS_BASE_URL = "http://{{ LMS_HOST }}:8000"

OAUTH2_PROVIDER_URL = "http://{{ LMS_HOST }}:8000/oauth2"
SOCIAL_AUTH_EDX_OAUTH2_KEY = "{{ RGG_OAUTH2_KEY_SSO_DEV }}"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "http://{{ LMS_HOST }}:8000"
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = "http://{{ LMS_HOST }}:8000/logout"
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

{{ patch("rgg-development-settings") }}
