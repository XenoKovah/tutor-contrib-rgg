from ..devstack import *

{% include "rgg/apps/settings/partials/common.py" %}

{% if IS_MINIO_ENABLED %}
AWS_S3_ENDPOINT_URL = "http://{{ MINIO_HOST }}:9000"
{% endif %}

EDX_LMS_BASE_URL = "http://{{ LMS_HOST }}:8000"

{{ patch("rgg-development-settings") }}
