import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django_app = get_asgi_application()

# FastAPI 앱 임포트
from api.main import app as fastapi_app

# Django 통합
fastapi_app.mount("/django", WSGIMiddleware(django_app))