from typing import Dict, List, Union

from pydantic import BaseModel

from communication.schema import CommunicationUseCase, PatientProfile


class ExceptionResponse(BaseModel):
    code: int
    content: Union[Dict, str]


class MedicationAdherenceCommRequest(BaseModel):
    request_uuid: str
    patient_profile: PatientProfile


class MedicationAdherenceCommResponse(BaseModel):
    request_uuid: str
    message: str
    high_success_examples_id: List[int]
    low_success_examples_id: List[int]
    metadata: Dict


class CommunicationSuccessRequest(BaseModel):
    communication_use_case: CommunicationUseCase
    request_uuid: str
    high_success_examples_id: List[int]
    low_success_examples_id: List[int]
    was_successful: bool
