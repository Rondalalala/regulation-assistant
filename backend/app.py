from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import regulations, authority, search, upload, parse
from services.data_store import get_config

app = FastAPI(title="制度助手 API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(regulations.router, prefix="/api/regulations")
app.include_router(authority.router, prefix="/api/authority")
app.include_router(search.router, prefix="/api/search")
app.include_router(upload.router, prefix="/api/upload")
app.include_router(parse.router, prefix="/api/parse")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/config")
def config():
    return get_config()
