from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import accounts, dashboard, videos

app = FastAPI(title="RV Matrix Hub API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(accounts.router)
app.include_router(videos.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
