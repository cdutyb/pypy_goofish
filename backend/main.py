from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import goods

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 前端的地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goods.router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
