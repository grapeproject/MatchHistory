import os
import sys
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

from starlette.middleware.wsgi import WSGIMiddleware

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lol.settings")
django_app = get_asgi_application()

# FastAPI 앱 임포트
from api.main import app as fastapi_app

# Django 통합
fastapi_app.mount("/django", WSGIMiddleware(django_app))

app = fastapi_app
