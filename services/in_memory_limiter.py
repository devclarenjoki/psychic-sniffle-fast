# services/in_memory_limiter.py

import time
import asyncio
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Request, HTTPException, status

class InMemoryRateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
        self.storage: Dict[str, Deque[float]] = defaultdict(deque)

    async def __call__(self, request: Request):
        # Use the client's IP address as the key
        key = request.client.host
        now = time.time()
        
        # Clean up old timestamps from the queue
        while self.storage[key] and self.storage[key][0] <= now - self.seconds:
            self.storage[key].popleft()
        
        # Check if the limit has been exceeded
        if len(self.storage[key]) >= self.times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
        
        # Add the current timestamp to the queue
        self.storage[key].append(now)

# A factory function to create the dependency
def rate_limit(times: int, seconds: int):
    return InMemoryRateLimiter(times=times, seconds=seconds)