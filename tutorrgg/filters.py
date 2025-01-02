from tutorpod_autoscaling.hooks import AUTOSCALING_CONFIG


@AUTOSCALING_CONFIG.add()
def _add_rgg_autoscaling(autoscaling_config):
    """Add autoscaling configuration for RGG."""
    autoscaling_config.update(
        {
            "rgg": {
                "enable_hpa": True,
                "memory_request": "300Mi",
                "cpu_request": 0.25,
                "memory_limit": "600Mi",
                "cpu_limit": 1,
                "min_replicas": 1,
                "max_replicas": 10,
                "avg_cpu": 80,
                "avg_memory": "",
                "enable_vpa": False,
            },
            "rgg-worker": {
                "enable_hpa": True,
                "memory_request": "500Mi",
                "cpu_request": 0.25,
                "memory_limit": "1000Mi",
                "cpu_limit": 1,
                "min_replicas": 1,
                "max_replicas": 10,
                "avg_cpu": 80,
                "avg_memory": "",
                "enable_vpa": False,
            },
        }
    )
    return autoscaling_config
