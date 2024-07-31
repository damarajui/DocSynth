from pydantic import BaseModel


class FileInput(BaseModel):
    filename: str
    content: str  # This will be base64 encoded
    content_type: str

class DocumentInput(BaseModel):
    urls: list[str] = []
    files: list[FileInput] = []
    project_type: str

class ProcessedDocument(BaseModel):
    source: str
    content: str
    doc_type: str
    metadata: dict

class SetupGuide(BaseModel):
    id: str
    content: str
    project_type: str
    sources: list[str]

class FeedbackData(BaseModel):
    guide_id: str
    rating: int
    comments: str