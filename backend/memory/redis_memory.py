import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("metaai.memory")


class RedisClientError(Exception):
    pass


class _RedisClient:
    _instance: Optional["_RedisClient"] = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            import redis.asyncio as aioredis
            from backend.config import settings
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=5,
            )
            logger.info("Connected to Redis at %s", settings.REDIS_URL)
        except Exception as e:
            logger.warning("Redis connection failed (will use fallback): %s", e)
            self._client = None

    @property
    def client(self):
        return self._client


def _get_redis():
    return _RedisClient().client


class ConversationMemory:
    def __init__(self, session_id: str, max_messages: int = 50):
        self.session_id = session_id
        self.max_messages = max_messages
        self._prefix = f"conversation:{session_id}"
        self._fallback: list[dict] = []

    async def add_message(self, role: str, content: str, metadata: Optional[dict] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        r = _get_redis()
        if r:
            try:
                key = f"{self._prefix}:messages"
                await r.rpush(key, json.dumps(message))
                await r.ltrim(key, -self.max_messages, -1)
                await r.expire(key, 86400)
                return
            except Exception as e:
                logger.warning("Redis add_message failed: %s", e)

        self._fallback.append(message)
        if len(self._fallback) > self.max_messages:
            self._fallback.pop(0)

    async def get_history(self) -> list[dict]:
        r = _get_redis()
        if r:
            try:
                key = f"{self._prefix}:messages"
                raw = await r.lrange(key, 0, -1)
                return [json.loads(m) for m in raw] if raw else []
            except Exception as e:
                logger.warning("Redis get_history failed: %s", e)
        return self._fallback

    async def clear(self):
        r = _get_redis()
        if r:
            try:
                await r.delete(f"{self._prefix}:messages")
            except Exception as e:
                logger.warning("Redis clear failed: %s", e)
        self._fallback.clear()


class AgentMemory:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._prefix = f"agent_memory:{agent_id}"
        self._fallback: dict = {}

    async def set(self, key: str, value: Any, ttl: int = 3600):
        r = _get_redis()
        entry = {"value": value, "updated_at": datetime.now(timezone.utc).isoformat()}
        if r:
            try:
                redis_key = f"{self._prefix}:{key}"
                await r.setex(redis_key, ttl, json.dumps(entry))
                return
            except Exception as e:
                logger.warning("Redis set failed: %s", e)
        self._fallback[key] = entry

    async def get(self, key: str) -> Any:
        r = _get_redis()
        if r:
            try:
                redis_key = f"{self._prefix}:{key}"
                raw = await r.get(redis_key)
                if raw:
                    entry = json.loads(raw)
                    return entry.get("value")
                return None
            except Exception as e:
                logger.warning("Redis get failed: %s", e)
        entry = self._fallback.get(key)
        return entry.get("value") if entry else None

    async def delete(self, key: str):
        r = _get_redis()
        if r:
            try:
                await r.delete(f"{self._prefix}:{key}")
            except Exception as e:
                logger.warning("Redis delete failed: %s", e)
        self._fallback.pop(key, None)


class LongTermMemory:
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self._prefix = f"ltm:{namespace}"
        self._fallback: dict = {}

    async def store(self, key: str, data: dict, ttl: int = 86400 * 30):
        r = _get_redis()
        entry = {"data": data, "stored_at": datetime.now(timezone.utc).isoformat()}
        if r:
            try:
                redis_key = f"{self._prefix}:{key}"
                await r.setex(redis_key, ttl, json.dumps(entry))
                return
            except Exception as e:
                logger.warning("Redis LTM store failed: %s", e)
        self._fallback[key] = entry

    async def retrieve(self, key: str) -> Optional[dict]:
        r = _get_redis()
        if r:
            try:
                raw = await r.get(f"{self._prefix}:{key}")
                if raw:
                    entry = json.loads(raw)
                    return entry.get("data")
                return None
            except Exception as e:
                logger.warning("Redis LTM retrieve failed: %s", e)
        entry = self._fallback.get(key)
        return entry.get("data") if entry else None

    async def search(self, query: str, max_results: int = 10) -> list[dict]:
        r = _get_redis()
        if r:
            try:
                pattern = f"{self._prefix}:*"
                cursor = 0
                results = []
                while cursor is not None:
                    cursor, keys = await r.scan(cursor, match=pattern, count=100)
                    for k in keys:
                        if len(results) >= max_results:
                            break
                        raw = await r.get(k)
                        if raw:
                            try:
                                entry = json.loads(raw)
                                key_name = k.split(":")[-1]
                                if query.lower() in key_name.lower():
                                    results.append({"key": key_name, "data": entry.get("data")})
                            except json.JSONDecodeError:
                                pass
                    if cursor == 0 or len(results) >= max_results:
                        break
                return results[:max_results]
            except Exception as e:
                logger.warning("Redis LTM search failed: %s", e)
        return []

    async def forget(self, key: str):
        r = _get_redis()
        if r:
            try:
                await r.delete(f"{self._prefix}:{key}")
            except Exception as e:
                logger.warning("Redis LTM forget failed: %s", e)
        self._fallback.pop(key, None)
