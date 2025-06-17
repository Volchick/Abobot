import time
import asyncio
from collections import deque
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

class VKRateLimitMiddleware(BaseHTTPMiddleware):
    VK_REQUEST_LIMIT = 3
    VK_TIME_WINDOW = 1  # секунда
    vk_request_times = deque(maxlen=VK_REQUEST_LIMIT)
    vk_request_lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Применяем лимит только к VK callback
        if request.url.path.startswith("/vk/"):
            async with self.vk_request_lock:
                now = time.monotonic()
                if len(self.vk_request_times) == self.VK_REQUEST_LIMIT:
                    earliest = self.vk_request_times[0]
                    wait_time = self.VK_TIME_WINDOW - (now - earliest)
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                self.vk_request_times.append(time.monotonic())
        response = await call_next(request)
        return response