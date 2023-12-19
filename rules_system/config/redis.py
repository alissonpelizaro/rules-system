import os
import redis

def get_redis_instance(decode_responses: bool = False):
    """Get redis connection

    Returns:
        redis: Redis client
    """
    if os.environ.get("PYTEST_CURRENT_TEST"):
        from fakeredis import FakeStrictRedis
        return FakeStrictRedis(decode_responses=decode_responses)
    
    redis_host = os.environ.get('REDIS_HOST', 'localhost')
    redis_port = os.environ.get('REDIS_PORT', '6379')

    return redis.Redis(
        host=redis_host,
        port=redis_port,
        db=1,
        charset="utf-8",
        decode_responses=decode_responses
    )
