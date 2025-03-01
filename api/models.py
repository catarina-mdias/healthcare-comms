from typing import Dict, List, Union

from pydantic import BaseModel

from medication_adherence.schema import PatientProfile


class ExceptionResponse(BaseModel):
    code: int
    content: Union[Dict, str]


class MedicationAdherenceRequest(BaseModel):
    request_uuid: str
    patient_profile: PatientProfile


class MedicationAdherenceResponse(BaseModel):
    request_uuid: str
    message: str
    high_success_examples_id: List[int]
    low_success_examples_id: List[int]
    metadata: Dict


class AdherenceSuccessRequest(BaseModel):
    medication_adherence_request_uuid: str
    high_success_examples_id: List[int]
    low_success_examples_id: List[int]
    was_successful: bool
