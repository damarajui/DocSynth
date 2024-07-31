import json
from typing import Optional

import redis
from app.config import settings
from app.models import SetupGuide

redis_client = redis.Redis.from_url(settings.redis_url)

async def get_cached_answer(query: str) -> Optional[SetupGuide]:
    cached_data = redis_client.get(query)
    if cached_data:
        guide_dict = json.loads(cached_data)
        return SetupGuide(**guide_dict)
    return None

async def cache_answer(query: str, guide: SetupGuide):
    guide_json = json.dumps(guide.dict())
    redis_client.setex(query, settings.cache_ttl, guide_json)