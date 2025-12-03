from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.db import Base, engine
from routes import upload, generateStories, generateEpics, generateQA, listFiles, generateTestPlan, getEpics, getStories, getQA, getTestPlan, agents_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
