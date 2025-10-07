import redis.asyncio as aioredis

# Async connection to Valkey (hardcoded for Docker)
async_valkey_conn = aioredis.from_url("redis://valkey:6379/0", decode_responses=True)
