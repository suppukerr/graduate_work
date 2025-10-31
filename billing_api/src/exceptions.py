from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from http import HTTPStatus
import logging

logger = logging.getLogger(__name__)


class HandledHTTPException(HTTPException):
    """Локальные, осознанные ошибки"""
    pass


async def timeout_exception_handler(
        request: Request,
        exc: httpx.TimeoutException):
    logger.error(f"Сервис не отвечает: {request.url} — {exc}")
    return JSONResponse(
        # status_code=503,
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        content={"detail": "Внутренний сервис временно недоступен"})


async def handled_http_exception_handler(
        request: Request,
        exc: HandledHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail})


async def http_exception_handler(
        request: Request,
        exc: HTTPException):
    logger.warning(f"HTTPException: {exc.detail} ({request.url})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "Ошибка подключения"})


async def general_exception_handler(
        request: Request,
        exc: Exception):
    logger.exception(f"Неожиданная ошибка на {request.url}: {exc}")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"detail": "Произошла внутренняя ошибка сервера"})
