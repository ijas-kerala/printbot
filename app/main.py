from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager
from app.services.job_worker import start_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start worker
    start_worker()
    yield
    # Shutdown: Clean up if needed

app = FastAPI(title="PrintBot API", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

from app.routers import upload, print_settings, status, admin

app.include_router(upload.router)
app.include_router(print_settings.router)
app.include_router(status.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    # Redirect root to upload page for now, or serve the upload page directly
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/")

@app.get("/health")
def health_check():
    return {"status": "ok"}
