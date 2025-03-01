import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from fastapi_router_controller import Controller

from api.exception import CommunicationServiceException
from api.models import (
    AdherenceSuccessRequest,
    ExceptionResponse,
    MedicationAdherenceRequest,
    MedicationAdherenceResponse,
)
from medication_adherence.communication import MedicationAdherenceCommunication
from medication_adherence.utils import StrEnum

router = APIRouter()
controller = Controller(router, openapi_tag={"name": "communication"})


class CommunicationRoutersPath(StrEnum):
    MEDICATION_ADHERENCE = "/medication-adherence"
    ADHERENCE_SUCCESS = "/adherence-success"


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
        response_model=MedicationAdherenceResponse,
    )
    async def get_med_adherence_comm(
        self,
        _: Request,
        request_body: MedicationAdherenceRequest,
    ) -> JSONResponse:
        logging.info(
            {
                "message": (
                    "Request Received - "
                    f"{self.get_med_adherence_comm.__name__}"
                ),
                "body": request_body.model_dump(mode="json"),
            }
        )

        try:
            medication_adherence_response = (
                await self.medication_adherence_comm_service.get_communication(
                    request_uuid=request_body.request_uuid,
                    patient_profile=request_body.patient_profile,
                )
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=MedicationAdherenceResponse(
                    **medication_adherence_response
                ).model_dump(),
            )

        except Exception as base_exception:
            raise CommunicationServiceException(base_exception=base_exception)

    @controller.router.post(
        CommunicationRoutersPath.ADHERENCE_SUCCESS,
        summary=(
            "Update message success likelihoods based on adherence feedback"
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
    async def update_success_likelihood(
        self,
        _: Request,
        request_body: AdherenceSuccessRequest,
    ) -> JSONResponse:
        logging.info(
            {
                "message": (
                    "Request Received - "
                    f"{self.update_success_likelihood.__name__}"
                ),
                "body": request_body.model_dump(mode="json"),
            }
        )

        try:
            await (
                self.medication_adherence_comm_service.update_success_likelihoods(  # noqa
                    was_successful=request_body.was_successful,
                    high_success_examples_id=(
                        request_body.high_success_examples_id
                    ),
                    low_success_examples_id=(
                        request_body.low_success_examples_id
                    ),
                )
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Success likelihoods updated successfully"
                },
            )

        except Exception as base_exception:
            raise CommunicationServiceException(base_exception=base_exception)
