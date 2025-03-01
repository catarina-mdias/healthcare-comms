import faulthandler
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_router_controller import ControllersTags

from api.controllers import CommunicationController
from api.exception import (
    CommunicationServiceException,
    service_exception_handler,
)

faulthandler.enable()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.info("Application started.")
    yield
    logging.info("Shutting down...")


def create_application() -> FastAPI:
    logging.info("Creating application...")

    application = FastAPI(
        root_path="/communication",
        openapi_tags=ControllersTags,
        lifespan=lifespan,
    )

    application.include_router(CommunicationController.router())

    application.add_exception_handler(
        CommunicationServiceException, service_exception_handler
    )

    return application


app = create_application()
