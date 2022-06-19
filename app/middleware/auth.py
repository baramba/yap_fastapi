import logging
import os
from enum import Enum
from http import HTTPStatus

import httpx
from core.config import settings
from httpx import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

log = logging.getLogger(os.path.basename(__file__))


class AuthProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        headers = request.headers.items()
        request.scope["permissions"] = [AuthPerms.NO_PERMS.value]
        async with httpx.AsyncClient() as client:
            try:
                auth_resp: Response = await client.post(settings.AUTH_SERVER_URL, headers=headers, timeout=1)
                auth_resp.raise_for_status()
                request.scope["permissions"] = auth_resp.json()
            except httpx.HTTPError as e:
                log.error("Error while request Auth server {0}:\n {1}".format(e.request.url, e))

        return await call_next(request)


class AuthPerms(Enum):
    LIKEAGOD = {"id": 1, "name": "likeagod"}
    ADMIN = {"id": 2, "name": "admin"}
    USER = {"id": 3, "name": "user"}
    ROLES = {"id": 4, "name": "roles"}
    PERMISSIONS = {"id": 5, "name": "permissions"}
    NO_PERMS = {"id": -1, "name": "no_perms"}
