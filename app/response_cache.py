
from collections import OrderedDict
from threading import Lock
from time import monotonic


class ResponseCache:
    def __init__(self, max_size=128, ttl_seconds=300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = OrderedDict()
        self._lock = Lock()

    def get(self, key):
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return None

            expires_at, value = entry

            if monotonic() >= expires_at:
                del self._cache[key]
                return None

            self._cache.move_to_end(key)
            return value.copy()

    def set(self, key, value):
        with self._lock:
            self._cache[key] = (
                monotonic() + self.ttl_seconds,
                value.copy()
            )
            self._cache.move_to_end(key)

            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)


response_cache = ResponseCache()
