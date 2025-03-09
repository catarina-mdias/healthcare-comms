import random
import uuid
from typing import Dict, List

import requests

from communication.config import DATA_DIR
from communication.schema import CommunicationUseCase, PatientProfile
from communication.utils import load_json_file

# Global variables
LOCALHOST_BASE_URL = "http://localhost:8080"
test_patients = load_json_file(DATA_DIR / "test_patients.json")


def get_random_patient() -> PatientProfile:
    """Get a random patient from test data."""
    random_patient = random.choice(test_patients)
    return PatientProfile.model_validate(random_patient)


def build_medication_adherence_body(patient_profile: PatientProfile) -> Dict:
    """Build the request body for medication adherence endpoint."""
    return {
        "request_uuid": str(uuid.uuid4()),
        "patient_profile": patient_profile.model_dump(),
    }


def build_adherence_success_body(
    was_successful: bool,
    request_uuid: str,
    low_success_examples_id: List[int],
    high_success_examples_id: List[int],
) -> Dict:
    """Build the request body for adherence success endpoint."""
    return {
        "communication_use_case": CommunicationUseCase.MEDICATION_ADHERENCE,
        "request_uuid": request_uuid,
        "was_successful": was_successful,
        "low_success_examples_id": low_success_examples_id,
        "high_success_examples_id": high_success_examples_id,
    }


def get_medication_adherence_message(base_url: str) -> Dict:
    """Get a medication adherence message from the API."""
    patient_profile = get_random_patient()
    request_body = build_medication_adherence_body(
        patient_profile=patient_profile
    )

    response = requests.post(
        f"{base_url}/communication/medication-adherence",
        json=request_body,
    )
    response.raise_for_status()
    return response.json()


def get_adherence_success(
    base_url: str,
    was_successful: bool,
    request_uuid: str,
    low_success_examples_id: List[int],
    high_success_examples_id: List[int],
) -> Dict:
    """Get adherence success response from the API."""
    request_body = build_adherence_success_body(
        was_successful,
        request_uuid,
        low_success_examples_id,
        high_success_examples_id,
    )

    response = requests.post(
        f"{base_url}/communication/success",
        json=request_body,
    )
    response.raise_for_status()
    return response.json()


def main(base_url: str = LOCALHOST_BASE_URL):
    """Main function to demonstrate API client usage."""
    result = get_medication_adherence_message(base_url=base_url)
    print("Full response:", result)

    print("\n\nMessage:", result["message"])

    print("\nWas this message successful? (yes or no)")
    user_input = input().lower()
    success = user_input in ["yes", "y"]

    result = get_adherence_success(
        base_url=base_url,
        was_successful=success,
        request_uuid=result["request_uuid"],
        low_success_examples_id=result["low_success_examples_id"],
        high_success_examples_id=result["high_success_examples_id"],
    )

    print(result["message"])


if __name__ == "__main__":
    main()
