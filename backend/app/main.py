from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import endpoints
from app.services.search_engine import search_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code chạy khi server khởi động
    search_engine.warmup() 
    yield
    # Code chạy khi server tắt (nếu cần dọn dẹp)
# Khởi tạo App
app = FastAPI(title="Job Recommender AI Demo", version="1.0")

# Cấu hình CORS (Để Frontend React gọi được API)
# Cho phép mọi nguồn (trong môi trường dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký Router
app.include_router(endpoints.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)