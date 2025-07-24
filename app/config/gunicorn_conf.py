import gunicorn
from app.config import settings


gunicorn.SERVER = "undisclosed"
gunicorn.SERVER_SOFTWARE = "undisclosed"

bind = [f"{settings.APP_HOST}:{settings.APP_PORT}"]
workers = 1
threads = 1
reload = False
timeout = 0
worker_class = "uvicorn.workers.UvicornWorker"