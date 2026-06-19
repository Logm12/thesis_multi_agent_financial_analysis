import redis
import hashlib
import os
from core.config import REDIS_URL

class RedisCache:
    def __init__(self):
        try:
            self.client = redis.from_url(REDIS_URL, decode_responses=True)
            self.client.ping()
            print(f"[Cache] Connected to Redis at {REDIS_URL}")
        except Exception as e:
            print(f"[Cache] Redis connection failed: {e}")
            self.client = None

    def _generate_key(self, file_path: str) -> str:
        """Tạo key dựa trên MD5 hash của đường dẫn và kích thước file."""
        if not os.path.exists(file_path):
            return hashlib.md5(file_path.encode()).hexdigest()
        
        file_size = os.path.getsize(file_path)
        key_data = f"{file_path}_{file_size}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_pdf_cache(self, file_path: str) -> str | None:
        if not self.client:
            return None
        key = self._generate_key(file_path)
        return self.client.get(f"pdf_cache:{key}")

    def set_pdf_cache(self, file_path: str, content: str, expire: int = 86400):
        if not self.client:
            return
        key = self._generate_key(file_path)
        try:
            self.client.set(f"pdf_cache:{key}", content, ex=expire)
            print(f"[Cache] Cached result for {file_path}")
        except Exception as e:
            print(f"[Cache] Failed to set cache: {e}")

    def get_ingest_cache(self, sha256: str) -> str | None:
        if not self.client:
            return None
        try:
            return self.client.get(f"ingest_cache:{sha256}")
        except Exception as e:
            print(f"[Cache] Failed to get ingest cache: {e}")
            return None

    def set_ingest_cache(self, sha256: str, task_id: str, expire: int = 86400):
        if not self.client:
            return
        try:
            self.client.set(f"ingest_cache:{sha256}", task_id, ex=expire)
            print(f"[Cache] Cached ingest mapping: {sha256} -> {task_id}")
        except Exception as e:
            print(f"[Cache] Failed to set ingest cache: {e}")

# Singleton instance
pdf_cache = RedisCache()

