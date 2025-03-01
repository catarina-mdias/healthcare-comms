import random
import uuid
from typing import Dict, List

import requests

from medication_adherence.config import DATA_DIR
from medication_adherence.schema import PatientProfile
from medication_adherence.utils import load_json_file


class CommunicationApiClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_patients = load_json_file(DATA_DIR / "test_patients.json")

    def _get_random_patient(self) -> PatientProfile:
        random_patient = random.choice(self.test_patients)
        return PatientProfile.model_validate(random_patient)

    @staticmethod
    def _build_medication_adherence_body(
        patient_profile: PatientProfile,
    ) -> Dict:
        return {
            "request_uuid": str(uuid.uuid4()),
            "patient_profile": patient_profile.model_dump(),
        }

    @staticmethod
    def _build_adherence_success_body(
        was_successful: bool,
        request_uuid: str,
        low_success_examples_id: List[int],
        high_success_examples_id: List[int],
    ) -> Dict:
        return {
            "medication_adherence_request_uuid": request_uuid,
            "was_successful": was_successful,
            "low_success_examples_id": low_success_examples_id,
            "high_success_examples_id": high_success_examples_id,
        }

    def get_medication_adherence_message(self) -> Dict:
        """Synchronous call to get medication adherence message"""
        patient_profile = self._get_random_patient()
        request_body = self._build_medication_adherence_body(patient_profile)

        response = requests.post(
            f"{self.base_url}/communication/medication-adherence",
            json=request_body,
        )
        response.raise_for_status()
        return response.json()

    def get_adherence_success(
        self,
        was_successful: bool,
        request_uuid: str,
        low_success_examples_id: List[int],
        high_success_examples_id: List[int],
    ) -> Dict:

        request_body = self._build_adherence_success_body(
            was_successful,
            request_uuid,
            low_success_examples_id,
            high_success_examples_id,
        )

        response = requests.post(
            f"{self.base_url}/communication/adherence-success",
            json=request_body,
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    client = CommunicationApiClient()
    result = client.get_medication_adherence_message()
    print("Full response:", result)

    print("Message:", result["message"])

    print("Was this message successful? (yes or no)")
    user_input = input().lower()
    success = user_input in ["yes", "y"]

    result = client.get_adherence_success(
        was_successful=success,
        request_uuid=result["request_uuid"],
        low_success_examples_id=result["low_success_examples_id"],
        high_success_examples_id=result["high_success_examples_id"],
    )

    print(result)
