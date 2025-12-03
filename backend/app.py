import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend directory to path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.db import Base, engine
from routes import upload, generateStories, generateEpics, generateQA, listFiles, generateTestPlan, getEpics, getStories, getQA, getTestPlan, agents_router, rag_search

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware - must be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "localhost:5173",
        "localhost:5174",
        "*"  # Allow all origins in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(upload.router)
app.include_router(generateStories.router)
app.include_router(generateEpics.router)
app.include_router(generateQA.router)
app.include_router(listFiles.router)
app.include_router(generateTestPlan.router)
app.include_router(getEpics.router)
app.include_router(getStories.router)
app.include_router(getQA.router)
app.include_router(getTestPlan.router)
app.include_router(agents_router.router)
app.include_router(rag_search.router)
