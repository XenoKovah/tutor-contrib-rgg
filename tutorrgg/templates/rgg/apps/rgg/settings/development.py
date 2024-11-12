from ..devstack import *
from .common import *


{% if IS_MINIO_ENABLED %}
AWS_S3_ENDPOINT_URL = "{{ RGG_AWS_S3_ENDPOINT_URL }}:9000"
{% endif %}
