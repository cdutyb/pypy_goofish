import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from routes import goods

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"], # 前端的地址，允许凭证时 allow_origins 不能设定为 ['*']，必须指定源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goods.router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
