import asyncio
import base64
from urllib.parse import urlparse

import chardet
from app.models import FileInput, ProcessedDocument
from app.utils import fetch_url_content
from fastapi import UploadFile


async def process_documents(urls: list[str], files: list[FileInput]) -> list[ProcessedDocument]:
    tasks = []
    for url in urls:
        tasks.append(process_url(url))
    for file in files:
        tasks.append(process_file(file))
    return await asyncio.gather(*tasks)

async def process_url(url: str) -> ProcessedDocument:
    content = await fetch_url_content(url)
    return ProcessedDocument(
        source=url,
        content=content,
        doc_type="url",
        metadata={"domain": urlparse(url).netloc}
    )

async def process_file(file: FileInput) -> ProcessedDocument:
    # Decode the base64 content
    content = base64.b64decode(file.content).decode('utf-8', errors='ignore')
    return ProcessedDocument(
        source=file.filename,
        content=content,
        doc_type="file",
        metadata={"file_type": file.content_type}
    )

async def extract_text_from_file(file: UploadFile) -> str:
    content = await file.read()
    try:
        # Try UTF-8 first
        return content.decode('utf-8')
    except UnicodeDecodeError:
        # If UTF-8 fails, use chardet to detect encoding
        encoding = chardet.detect(content)['encoding']
        return content.decode(encoding or 'utf-8', errors='replace')