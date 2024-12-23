import os
import sys
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

load_dotenv()

# Add PYTHONPATH from .env
pythonpath = os.getenv("PYTHONPATH")
if pythonpath and pythonpath not in sys.path:
    sys.path.append(pythonpath)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lol.settings")
django_app = get_asgi_application()

# FastAPI 앱 임포트
from api.main import app as fastapi_app
from starlette.middleware.wsgi import WSGIMiddleware

fastapi_app.mount("/django", WSGIMiddleware(django_app))

app = fastapi_app


