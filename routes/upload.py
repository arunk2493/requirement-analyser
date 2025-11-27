from fastapi import APIRouter, UploadFile, File, HTTPException
from models.file_model import Upload
from config.db import get_db
import uuid, json
from PyPDF2 import PdfReader
from docx import Document

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Extract text from file
        if file.filename.endswith(".pdf"):
            reader = PdfReader(file.file)
            text = "".join([p.extract_text() + "\n" for p in reader.pages])
        elif file.filename.endswith(".docx"):
            doc = Document(file.file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            contents = await file.read()
            try:
                text = contents.decode("utf-8")
            except UnicodeDecodeError:
                text = contents.decode("latin1")

        # Store as JSON
        content_json = {"requirement": text}

        # Store in DB
        with get_db() as db:
            upload_obj = Upload(filename=file.filename, content=content_json)
            db.add(upload_obj)

        return {"message": "File uploaded successfully", "upload_id": upload_obj.id}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
