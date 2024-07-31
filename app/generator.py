import tiktoken
from config import settings
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential

llm = ChatOpenAI(model_name="gpt-4-turbo-preview", openai_api_key=settings.openai_api_key)

prompt = ChatPromptTemplate.from_template(
    "Answer the following question based on the given context:\n\n"
    "Question: {question}\n\n"
    "Context: {context}\n\n"
    "Answer:"
)

chain = LLMChain(llm=llm, prompt=prompt)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def generate_answer_async(question: str, context: str) -> str:
    enc = tiktoken.encoding_for_model("gpt-4-turbo-preview")
    max_tokens = 4096 - len(enc.encode(question)) - len(enc.encode(context)) - 100  # Reserve 100 tokens for the answer
    return await chain.arun(question=question, context=context, max_tokens=max_tokens)