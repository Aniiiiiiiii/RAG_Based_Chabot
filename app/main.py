import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.endpoints import answer
from app.database.connection import engine
from app.database.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    yield
    print("Application is shutting down.")

app = FastAPI(lifespan=lifespan)

app.include_router(answer.router)

if __name__  == "__main__":
    uvicorn.run(app,host="192.168.1.182",port=8000)