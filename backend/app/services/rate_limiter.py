import time
from collections import defaultdict, deque

# Maximum requests allowed
MAX_REQUESTS = 5

# Time window in seconds
WINDOW_SECONDS = 60

# Stores request timestamps for each IP address
request_history = defaultdict(deque)


def is_rate_limited(client_ip: str) -> bool:
    """
    Returns True if the client has exceeded
    the allowed number of requests.
    """

    now = time.time()

    requests = request_history[client_ip]

    # Remove requests outside the time window
    while requests and requests[0] <= now - WINDOW_SECONDS:
        requests.popleft()

    # Check if limit has been reached
    if len(requests) >= MAX_REQUESTS:
        return True

    # Record this request
    requests.append(now)

    return False