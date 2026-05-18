from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError, HTTPException
from app.core.logger import logger

def register_exception(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError):
        logger.error("Validation error occurred", extra={"correlation_id": getattr(request.state, "correlation_id", None),"error": str(exc)})
        return JSONResponse(status_code=422, content={"detail": "Validation error"})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error("HTTP error occurred", extra={"correlation_id": getattr(request.state, "correlation_id", None),"error": str(exc)})
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
