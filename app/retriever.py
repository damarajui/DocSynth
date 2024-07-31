from app.database import search_documents
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt, wait_exponential

model = SentenceTransformer('all-MiniLM-L6-v2')

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def retrieve_documents(query: str, n_results: int = 5):
    results = search_documents(query, n_results)
    return results['documents'][0], results['metadatas'][0]