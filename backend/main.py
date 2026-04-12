from __future__ import annotations
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import scales, transfer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown code: Dispose of the engine
    await engine.dispose()

# API Metadata
app = FastAPI(
    title="Automated Grade Transfer System API",
    description="""
    This API facilitates the automated transfer of academic grades between university systems.
    It supports configurable equivalences for multiple international scales.
    """,
    version="1.0.0",
    contact={
        "name": "Academic Support Team",
        "email": "support@university.edu",
    },
    #root_path="/backend",
    lifespan=lifespan
)

# CORS Configuration
# Essential for allowing your Web Interface (Frontend) to make requests to this API
origins = [
    "http://localhost:3000",  # Common for React/Next.js
    "http://localhost:5173",  # Common for Vite/Vue
    # Add your production domain here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(scales.router)
app.include_router(transfer.router)

# Root Health Check
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": "Grade Transfer System API is operational",
        #"supported_countries": ["Afganistan", "Albania", "Alemania"] # Based on PDF data
    }