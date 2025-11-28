from redis.asyncio import Redis
from app.config import base

redis_client = Redis(host=base.REDIS_HOST, port=base.REDIS_PORT, db=base.REDIS_DB)