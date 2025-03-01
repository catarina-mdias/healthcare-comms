import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from api.models import ExceptionResponse


class CommunicationServiceException(Exception):
    def __init__(
        self,
        base_exception: Exception,
    ):
        self.base_exception = base_exception
        self.message = f"CommunicationServiceException: {str(base_exception)}"

    def __str__(self):
        return self.message

    def to_dict(self):
        return {
            "message": self.message,
            "base_exception": str(self.base_exception),
        }


async def service_exception_handler(
    _: Request, exception: CommunicationServiceException
):
    logging.error(str(exception))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ExceptionResponse(
            content=exception.to_dict(),
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).model_dump(),
    )
