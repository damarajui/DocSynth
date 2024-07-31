import logging
from contextlib import asynccontextmanager
from typing import List
from urllib.parse import quote

from app.document_processor import extract_text_from_file, process_documents
from app.feedback_handler import handle_feedback
from app.init import initialize_app
from app.models import DocumentInput, FeedbackData, ProcessedDocument, SetupGuide
from app.summarizer import generate_setup_guide
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, HttpUrl, constr

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_app()
    yield

app = FastAPI(lifespan=lifespan)

class SanitizedDocumentInput(BaseModel):
    urls: List[HttpUrl] = []
    files: List[UploadFile] = []
    project_type: constr(strip_whitespace=True, min_length=1, max_length=50)

def sanitize_input(input: DocumentInput) -> SanitizedDocumentInput:
    return SanitizedDocumentInput(
        urls=[HttpUrl(quote(url, safe=':/?&=')) for url in input.urls],
        files=input.files,
        project_type=input.project_type
    )

@app.post("/generate_guide", response_model=SetupGuide)
async def generate_guide(input: DocumentInput):
    try:
        processed_docs = await process_documents(input.urls, input.files)
        guide = await generate_setup_guide(processed_docs, input.project_type)
        logger.info(f"Generated guide for project type: {input.project_type}")
        return guide
    except Exception as e:
        logger.error(f"Error generating guide: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await extract_text_from_file(file)
        processed_doc = ProcessedDocument(
            source=file.filename,
            content=content,
            doc_type="file",
            metadata={"file_type": file.content_type}
        )
        return {"message": "File uploaded and processed successfully", "document": processed_doc}
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def feedback(feedback_data: FeedbackData):
    try:
        result = await handle_feedback(feedback_data)
        logger.info(f"Received feedback for guide {feedback_data.guide_id}")
        if result:
            return {"message": "Feedback received and guide updated", "updated_guide": result}
        else:
            return {"message": "Feedback received, thank you!"}
    except Exception as e:
        logger.error(f"Error handling feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))