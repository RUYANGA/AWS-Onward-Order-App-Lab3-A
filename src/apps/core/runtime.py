"""Find out which ECS task and Availability Zone is serving this request.

Shown on the page so reviewers can watch the load balancer spread traffic,
new tasks appear under load, and traffic move when a task or AZ is lost.
"""

import json
import os
import socket
import urllib.request
from functools import lru_cache


@lru_cache(maxsize=1)
def task_info():
    """Return the short ECS task id and Availability Zone of this container.

    Reads the ECS task metadata endpoint (v4) once per process. Outside ECS the
    hostname and ``"local"`` are returned instead.

    Returns:
        A dict with ``task`` and ``zone`` keys.
    """
    info = {"task": socket.gethostname(), "zone": "local"}
    base = os.getenv("ECS_CONTAINER_METADATA_URI_V4")
    if not base:
        return info
    try:
        # The URI is set by the ECS agent and always points at the link-local endpoint.
        with urllib.request.urlopen(f"{base}/task", timeout=2) as resp:  # nosec B310
            meta = json.load(resp)
        info["task"] = meta.get("TaskARN", "").rsplit("/", 1)[-1][:12] or info["task"]
        info["zone"] = meta.get("AvailabilityZone", "unknown")
    except (OSError, ValueError):
        pass
    return info
