import aiohttp
import openai
import tiktoken
from app.config import settings
from fastapi import UploadFile


async def fetch_url_content(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def extract_text_from_file(file: UploadFile) -> str:
    content = await file.read()
    if file.content_type == "application/pdf":
        return extract_text_from_pdf(content)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(content)
    else:
        return content.decode("utf-8")

def extract_text_from_pdf(content: bytes) -> str:
    from io import BytesIO

    from PyPDF2 import PdfReader
    reader = PdfReader(BytesIO(content))
    return " ".join(page.extract_text() for page in reader.pages)

def extract_text_from_docx(content: bytes) -> str:
    from io import BytesIO

    from docx import Document
    doc = Document(BytesIO(content))
    return " ".join(paragraph.text for paragraph in doc.paragraphs)

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

async def get_embedding(text: str) -> list[float]:
    response = await openai.Embedding.acreate(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def count_tokens(text: str, model: str = "gpt-4-turbo-preview") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except KeyError:
        print(f"Warning: model {model} not found. Using cl100k_base encoding.")
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

def truncate_text(text: str, max_tokens: int, model: str = "gpt-4-turbo-preview") -> str:
    enc = tiktoken.encoding_for_model(model)
    encoded = enc.encode(text)
    if len(encoded) <= max_tokens:
        return text
    return enc.decode(encoded[:max_tokens])

async def generate_text(prompt: str, max_tokens: int, model: str = "gpt-4-turbo-preview") -> str:
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

async def generate_text_with_token_limit(prompt: str, max_tokens: int = 1000, model: str = "gpt-4-turbo-preview"):
    prompt_tokens = count_tokens(prompt, model)
    available_tokens = settings.max_total_tokens - prompt_tokens - settings.token_buffer
    if available_tokens <= 0:
        raise ValueError("Prompt is too long for the specified max_tokens.")
    truncated_max_tokens = min(max_tokens, available_tokens)
    return await generate_text(prompt, truncated_max_tokens, model)