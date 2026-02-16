"""Gunicorn configuration for production."""

import multiprocessing
import os

from app.config import get_settings

settings = get_settings()

# Server socket
bind = f"{settings.host}:{settings.port}"
backlog = 2048

# Worker processes
workers = settings.workers
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = settings.log_level.lower()

# Process naming
proc_name = "hydro-search"

# Server mechanics
daemon = False
pidfile = "/tmp/hydro-search.pid"

# SSL (configure in production)
keyfile = os.getenv("SSL_KEYFILE")
certfile = os.getenv("SSL_CERTFILE")