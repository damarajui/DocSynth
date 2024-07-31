import pytest
from app.generator import generate_answer_async


@pytest.mark.asyncio
async def test_generate_answer_async():
    question = "What is the capital of France?"
    context = "France is a country in Western Europe. Its capital city is Paris."
    answer = await generate_answer_async(question, context)
    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "Paris" in answer