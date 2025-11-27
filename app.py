from fastapi import FastAPI
from config.db import Base, engine
from routes import upload, generateStories, generateEpics, generateQA, listFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(upload.router)
app.include_router(generateStories.router)
app.include_router(generateEpics.router)
app.include_router(generateQA.router)
app.include_router(listFiles.router)