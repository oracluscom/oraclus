import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .common.exceptions import InvalidEthereumAddress
from .common.loggers import logger
from .config import settings


class CheckAPIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if the request is to an allowed URL
        if self.is_to_allowed_url(request.url.path):
            return await call_next(request)

        # Check if the request is from an allowed origin
        if self.is_from_allowed_origin(request.headers.get("referer")):
            return await call_next(request)

        # Check if the request has a valid API key
        api_key = request.query_params.get("api_key")
        keys_list = self.pull_api_keys_from_other_host()

        if api_key and api_key in keys_list:
            return await call_next(request)
        else:
            logger.warning(f"Invalid API key: {api_key}")
            # raise HTTPException(status_code=403, detail="Forbidden: Invalid API key")
            return JSONResponse(status_code=403, content={"detail": "Forbidden: Invalid API key"})

    def is_to_allowed_url(self, path: str) -> bool:
        allowed_urls = settings.allowed_urls
        return any(path.startswith(url) for url in allowed_urls)

    def is_from_allowed_origin(self, referer: str) -> bool:
        if referer is None:
            return False
        allowed_origins = settings.allowed_origins
        return any(referer.startswith(domain) for domain in allowed_origins)

    def pull_api_keys_from_other_host(self):
        try:
            keys_list = []
        except:
            keys_list = []
        return keys_list


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except InvalidEthereumAddress as e:
            response = JSONResponse(content={"detail": str(e)}, status_code=400)
        return response
