import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + str(os.environ.get("PORT", 8000))
backlog = 2048

# Worker processes - Optimized for Render's resources
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging configuration
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Server mechanics
preload_app = True
daemon = False

# Process naming
proc_name = "factsandfakes_ai"

# Performance tuning
worker_tmp_dir = "/dev/shm"  # Use memory for worker temp files if available

# Graceful timeout
graceful_timeout = 30

# Limits
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190