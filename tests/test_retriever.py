import pytest
from app.document_processor import process_documents
from app.models import ProcessedDocument, SetupGuide
from app.retriever import retrieve_documents_async
from app.summarizer import generate_setup_guide
from fastapi import UploadFile


@pytest.mark.asyncio
async def test_retrieve_documents_async():
    query = "Test query"
    documents, metadatas = await retrieve_documents_async(query)
    assert isinstance(documents, list)
    assert isinstance(metadatas, list)
    assert len(documents) > 0
    assert len(metadatas) > 0

@pytest.mark.asyncio
async def test_generate_setup_guide():
    docs = [
        ProcessedDocument(source="test.com", content="Test content", doc_type="url", metadata={})
    ]
    project_type = "Web"
    guide = await generate_setup_guide(docs, project_type)
    assert isinstance(guide, SetupGuide)
    assert guide.project_type == project_type
    assert len(guide.content) > 0

@pytest.mark.asyncio
async def test_process_documents():
    urls = ["https://example.com"]
    files = [UploadFile(filename="test.txt", file=b"Test content")]
    processed_docs = await process_documents(urls, files)
    assert len(processed_docs) == 2
    assert processed_docs[0].doc_type == "url"
    assert processed_docs[1].doc_type == "file"