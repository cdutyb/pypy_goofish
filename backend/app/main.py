import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import goods

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000",
                   "http://localhost:5001", "http://127.0.0.1:5001",
                   "http://localhost:5002", "http://127.0.0.1:5002",
                   "http://localhost:5003", "http://127.0.0.1:5003"],  # 前端的地址，允许凭证时 allow_origins 不能设定为 ['*']，必须指定源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(goods.router, prefix="")

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
