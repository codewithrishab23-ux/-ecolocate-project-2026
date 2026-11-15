"""
WSGI Entry Point for EcoLocate
Production WSGI entry point for Gunicorn / Render / Cloud hosting.
"""

import os
import sys

# Ensure application directory is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

# Optionally attach WhiteNoise middleware for high-performance static asset serving
try:
    from whitenoise import WhiteNoise
    static_dir = os.path.join(BASE_DIR, "static")
    if os.path.isdir(static_dir):
        app.wsgi_app = WhiteNoise(app.wsgi_app, root=static_dir, prefix="static/")
except ImportError:
    pass

if __name__ == "__main__":
    app.run()
