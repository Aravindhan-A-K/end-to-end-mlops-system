from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import uuid
from app.core.logger import logger

class Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next):
        correlation_id = request.headers.get("x-correlation-id")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        start_time = time.time()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            latency = time.time() - start_time
            if response is not None:
                response.headers['x-correlation-id'] = correlation_id
            
            logger.info(
                "Request completed",
                extra={
                    "correlationId": correlation_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code if response else 500,
                    "API_latency": latency
                }
            )