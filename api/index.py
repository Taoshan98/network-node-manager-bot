import os
import sys

# Ensure root directory is on the Python path for Vercel Serverless environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app

# Vercel entrypoint exposes 'app'
