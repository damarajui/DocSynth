from app.config import settings
from openai import OpenAI
from tiktoken import encoding_for_model, get_encoding

client = OpenAI(api_key=settings.openai_api_key)

def count_tokens(text: str, model: str = "gpt-4-turbo-preview") -> int:
    try:
        enc = encoding_for_model(model)
        return len(enc.encode(text))
    except KeyError:
        print(f"Warning: model {model} not found. Using cl100k_base encoding.")
        enc = get_encoding("cl100k_base")
        return len(enc.encode(text))

def truncate_text(text: str, max_tokens: int, model: str = "gpt-4-turbo-preview") -> str:
    enc = encoding_for_model(model)
    encoded = enc.encode(text)
    if len(encoded) <= max_tokens:
        return text
    return enc.decode(encoded[:max_tokens])

async def generate_text(prompt: str, max_tokens: int = 1000) -> str:
    try:
        truncated_prompt = truncate_text(prompt, 14000)  # Truncate to leave room for response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at creating concise setup guides from technical documentation and you often consult online resources and you use your best contextual judgement when dealing with user input."},
                {"role": "user", "content": truncated_prompt}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error generating text: {str(e)}")

async def get_embedding(text: str):
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f"Error getting embedding: {str(e)}")