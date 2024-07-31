import chromadb
from app.config import settings
from app.models import FeedbackData, SetupGuide

# Create a persistent client
client = chromadb.PersistentClient(path=settings.chroma_db_path)

async def get_or_create_collection():
    return await client.get_or_create_collection("documents")

async def add_documents(documents):
    collection = await get_or_create_collection()
    await collection.add(
        documents=[doc.content for doc in documents],
        metadatas=[doc.metadata for doc in documents],
        ids=[doc.id for doc in documents]
    )

async def search_documents(query, n_results=5):
    collection = await get_or_create_collection()
    results = await collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results

def get_guide_by_id(guide_id: str) -> SetupGuide:
    collection = get_or_create_collection()
    result = collection.get(ids=[guide_id])
    if result['ids']:
        return SetupGuide(
            id=guide_id,
            content=result['documents'][0],
            project_type=result['metadatas'][0]['project_type'],
            sources=result['metadatas'][0]['sources']
        )
    return None

def update_guide_rating(guide_id: str, rating: int):
    collection = get_or_create_collection()
    collection.update(
        ids=[guide_id],
        metadatas=[{"rating": rating}]
    )

def store_feedback_data(feedback: FeedbackData):
    collection = get_or_create_collection()
    collection.add(
        documents=[feedback.comments],
        metadatas=[{"guide_id": feedback.guide_id, "rating": feedback.rating}],
        ids=[f"feedback_{feedback.guide_id}_{feedback.rating}"]
    )