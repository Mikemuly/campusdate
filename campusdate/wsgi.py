"""
WSGI config for campusdate project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusdate.settings')
application = get_wsgi_application()
