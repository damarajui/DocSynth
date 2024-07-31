import uuid
from typing import List

import nltk
import tiktoken
from app.language_model import generate_text, get_embedding
from app.models import ProcessedDocument, SetupGuide
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

def count_tokens(text: str) -> int:
    encoder = tiktoken.get_encoding("cl100k_base")
    return len(encoder.encode(text))

def semantic_chunk_text(text: str, max_chunk_size: int = 500) -> List[str]:
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if count_tokens(current_chunk + sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

async def generate_setup_guide(docs: List[ProcessedDocument], project_type: str) -> SetupGuide:
    all_text = " ".join([doc.content for doc in docs])
    chunks = semantic_chunk_text(all_text)
    
    chunk_embeddings = []
    for chunk in chunks:
        try:
            embedding = await get_embedding(chunk)
            chunk_embeddings.append(embedding)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            continue
    
    summary_prompt = f"Generate concise setup instructions for a {project_type} project based on the following documentation:"
    
    # Sort chunks by relevance (assuming higher embedding value means more relevant)
    sorted_chunks = sorted(zip(chunks, chunk_embeddings), key=lambda x: x[1][0], reverse=True)
    
    # Add chunks to the prompt until we reach the token limit
    for chunk, embedding in sorted_chunks:
        chunk_tokens = count_tokens(chunk)
        if count_tokens(summary_prompt) + chunk_tokens > 14000:  # Leave some room for the response
            break
        summary_prompt += f"\n\nDocument chunk (relevance: {embedding[0]:.2f}):\n{chunk}"
    
    setup_guide_content = await generate_text(summary_prompt, max_tokens=2000)
    
    return SetupGuide(
        id=str(uuid.uuid4()),
        content=setup_guide_content,
        project_type=project_type,
        sources=[doc.source for doc in docs]
    )

async def regenerate_setup_guide(guide: SetupGuide, comments: str) -> SetupGuide:
    from app.language_model import generate_text
    
    prompt = f"""
    The following setup guide needs improvement based on user feedback:

    {guide.content}

    User feedback: {comments}

    Please generate an improved version of the setup guide, addressing the user's feedback.
    """
    
    improved_content = await generate_text(prompt, max_tokens=2000)
    
    return SetupGuide(
        content=improved_content,
        project_type=guide.project_type,
        sources=guide.sources
    )