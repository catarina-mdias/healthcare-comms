import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from fastapi_router_controller import Controller

from api.exception import CommunicationServiceException
from api.models import (
    CommunicationSuccessRequest,
    ExceptionResponse,
    MedicationAdherenceCommRequest,
    MedicationAdherenceCommResponse,
)
from communication.medication_adherence import MedicationAdherenceCommunication
from communication.schema import CommunicationUseCase
from communication.utils import StrEnum

router = APIRouter()
controller = Controller(router, openapi_tag={"name": "communication"})


class CommunicationRoutersPath(StrEnum):
    MEDICATION_ADHERENCE = "/medication-adherence"
    SUCCESS = "/success"


@controller.resource()
class CommunicationController:
    def __init__(self):
        self.medication_adherence_comm_service = (
            MedicationAdherenceCommunication()
        )

    @controller.router.post(
        CommunicationRoutersPath.MEDICATION_ADHERENCE,
        summary=(
            "Main method to get a medication adherence communication "
            "personalized to patient"
        ),
        tags=["Communication"],
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "description": "Error: Bad request",
                "model": ExceptionResponse,
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY: {
                "description": "Error: Unprocessable entity",
                "model": ExceptionResponse,
            },
        },
        response_model=MedicationAdherenceCommResponse,
    )
    async def get_medication_adherence_comm(
        self,
        _: Request,
        request_body: MedicationAdherenceCommRequest,
    ) -> JSONResponse:
        logging.info(
            {
                "message": (
                    "Request Received - "
                    f"{self.get_medication_adherence_comm.__name__}"
                ),
                "body": request_body.model_dump(mode="json"),
            }
        )

        try:
            service_response = (
                await self.medication_adherence_comm_service.get_communication(
                    request_uuid=request_body.request_uuid,
                    patient_profile=request_body.patient_profile,
                )
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=MedicationAdherenceCommResponse(
                    **service_response
                ).model_dump(),
            )

        except Exception as base_exception:
            raise CommunicationServiceException(base_exception=base_exception)

    @controller.router.post(
        CommunicationRoutersPath.SUCCESS,
        summary=(
            "Update messages pool success likelihoods based on "
            "communication result. Prepared to support multiple use cases."
        ),
        tags=["Communication"],
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "description": "Error: Bad request",
                "model": ExceptionResponse,
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY: {
                "description": "Error: Unprocessable entity",
                "model": ExceptionResponse,
            },
        },
    )
    async def update_communication_success_likelihood(
        self,
        _: Request,
        request_body: CommunicationSuccessRequest,
    ) -> JSONResponse:
        logging.info(
            {
                "message": (
                    "Request Received - "
                    f"{self.update_communication_success_likelihood.__name__}"
                ),
                "body": request_body.model_dump(mode="json"),
            }
        )

        try:
            if (
                request_body.communication_use_case
                == CommunicationUseCase.MEDICATION_ADHERENCE
            ):
                await self.medication_adherence_comm_service.act_on_communication_result(  # noqa
                    was_successful=request_body.was_successful,
                    high_success_examples_id=(
                        request_body.high_success_examples_id
                    ),
                    low_success_examples_id=(
                        request_body.low_success_examples_id
                    ),
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Success likelihoods updated successfully"
                },
            )

        except Exception as base_exception:
            raise CommunicationServiceException(base_exception=base_exception)
