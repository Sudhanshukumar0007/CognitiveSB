import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

def make_celery():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Celery(
        "shadowbyte",
        broker=redis_url,
        backend=redis_url,
        include=["tasks"],
    )

celery = make_celery()
