import json

class RedisEventBus:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        
    async def publish(self, topic: str, message: dict):
        # Stub
        pass
