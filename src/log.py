"""Module for providing universal logger."""
import os
import structlog

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
structlog.configure(processors=[
    structlog.processors.add_log_level,
    structlog.processors.JSONRenderer()
])
logger = structlog.get_logger()
