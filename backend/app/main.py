from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import accounts, admin, auth, banners, dashboard, identities, members, orders, settings, tutorials, users, videos

app = FastAPI(title="RV Matrix Hub API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(accounts.router)
app.include_router(identities.router)
app.include_router(videos.router)
app.include_router(banners.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(members.router)
app.include_router(settings.public_router)
app.include_router(settings.admin_router)
app.include_router(tutorials.router)
app.include_router(orders.products_router)
app.include_router(orders.orders_router)

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
