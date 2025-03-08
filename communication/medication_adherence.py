import json
from typing import Dict, List, Tuple

from communication.chat_model import ChatModel, generate_message
from communication.communication import Communication
from communication.config import DATA_DIR, get_settings
from communication.prompt import PromptTemplate
from communication.schema import CommunicationUseCase, PatientProfile
from communication.utils import load_json_file
from communication.vector_database import VectorDatabase

settings = get_settings()

# LLM Completion configs
GPT_MODEL = "gpt-4o"
TEMPERATURE = 0.6

# Prompt template configs
PROMPT_TEMPLATE_MED_ADHERENCE = PromptTemplate(
    system_message_template_file="med_adherence_system_message.jinja2",
    user_message_template_file="med_adherence_user_message.jinja2",
)

# Vector DB configs
EMBEDDING_MODEL = "text-embedding-3-small"
SIMILARITY_THRESHOLD = 0.75
TOP_N_PATIENTS = 3

# Knowledge base configs
PATIENTS_FILENAME = "patients.json"
PATIENTS_FILE_JQ_SCHEMA = ".[] | {content: .profile, metadata: {id: .id}}"

MEDICATION_ADHERENCE_DATASET_FILENAME = "medication_adherence.json"

# Message generation configs
HIGH_SUCCESS_MESSAGES_COUNT = 3
LOW_SUCCESS_MESSAGES_COUNT = 2

UPDATE_DELTA = 0.05


class MedicationAdherenceCommunication(Communication):
    def __init__(
        self,
    ):
        super().__init__(use_case=CommunicationUseCase.MEDICATION_ADHERENCE)
        self.patients_vector_db = self._init_vector_db()
        self.medication_adherence_data = load_json_file(
            DATA_DIR / MEDICATION_ADHERENCE_DATASET_FILENAME
        )
        self.chat_model = ChatModel(openai_key=settings.OPENAI_API_KEY)

    @staticmethod
    def _init_vector_db():
        return VectorDatabase(
            kb_file_name=PATIENTS_FILENAME,
            kb_directory_path=DATA_DIR,
            embedding_model=EMBEDDING_MODEL,
            openai_key=settings.OPENAI_API_KEY,
            file_jq_schema=PATIENTS_FILE_JQ_SCHEMA,
        )

    async def get_communication(
        self, request_uuid: str, patient_profile: PatientProfile
    ) -> Dict:

        patient_profile = patient_profile.model_dump()

        similar_profile_ids = self._get_similar_profiles(
            {k: v for k, v in patient_profile.items() if k != "name"}
        )

        high_success_messages, low_success_messages = (
            self._get_messages_given_similar_profiles(similar_profile_ids)
        )

        system_message = PROMPT_TEMPLATE_MED_ADHERENCE.build_system_message()
        user_message = PROMPT_TEMPLATE_MED_ADHERENCE.build_user_message(
            patient_profile=patient_profile,
            high_success_messages=[
                row["message"] for row in high_success_messages
            ],
            low_success_messages=[
                row["message"] for row in low_success_messages
            ],
        )

        response = await generate_message(
            chat_model=self.chat_model,
            system_message=system_message,
            user_message=user_message,
            model=GPT_MODEL,
            temperature=TEMPERATURE,
            json_format=True,
        )

        response_dict = json.loads(response)

        return {
            "request_uuid": request_uuid,
            "message": response_dict["message"],
            "high_success_examples_id": [
                row["id"] for row in high_success_messages
            ],
            "low_success_examples_id": [
                row["id"] for row in low_success_messages
            ],
            "metadata": {
                "user_message": user_message,
                "system_message": system_message,
                "reasoning": response_dict["explanation"],
            },
        }

    async def act_on_communication_result(
        self,
        was_successful: bool,
        high_success_examples_id: List[int],
        low_success_examples_id: List[int],
    ) -> None:

        # Create ID-to-entry mapping for faster lookups
        kb_data_map = {
            entry["id"]: entry for entry in self.medication_adherence_data
        }

        # Update high success examples
        for id in high_success_examples_id:
            if id in kb_data_map:
                self._update_entry_likelihood(
                    kb_data_map[id], was_successful, is_high_success=True
                )

        # Update low success examples
        for id in low_success_examples_id:
            if id in kb_data_map:
                self._update_entry_likelihood(
                    kb_data_map[id], was_successful, is_high_success=False
                )

        # Save updated data
        with open(
            DATA_DIR / MEDICATION_ADHERENCE_DATASET_FILENAME,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.medication_adherence_data, f, indent=2, ensure_ascii=False
            )

    def _get_similar_profiles(self, patient_dict: Dict) -> List[int]:
        similar_profiles = self.patients_vector_db.get_documents_with_similarity_score(  # noqa
            user_query=str(patient_dict),
            top_k=TOP_N_PATIENTS,
            score_threshold=SIMILARITY_THRESHOLD,
        )
        return [doc.document_id for doc in similar_profiles]

    def _get_messages_given_similar_profiles(
        self, similar_profile_ids: List[int]
    ) -> Tuple[List[Dict], List[Dict]]:
        filtered_messages = [
            row
            for row in self.medication_adherence_data
            if row["patient_id"] in similar_profile_ids
        ]
        sorted_messages_by_likelihood = sorted(
            filtered_messages,
            key=lambda x: x["success_likelihood"],
            reverse=True,
        )

        high_success_messages = sorted_messages_by_likelihood[
            :HIGH_SUCCESS_MESSAGES_COUNT
        ]
        low_success_messages = sorted_messages_by_likelihood[
            -LOW_SUCCESS_MESSAGES_COUNT:
        ]

        return high_success_messages, low_success_messages

    @staticmethod
    def _update_entry_likelihood(
        entry, was_successful: bool, is_high_success: bool
    ) -> None:

        should_increase = (is_high_success and was_successful) or (
            not is_high_success and not was_successful
        )

        if should_increase:
            entry["success_likelihood"] = min(
                entry["success_likelihood"] + UPDATE_DELTA, 1.0
            )
        else:
            entry["success_likelihood"] = max(
                entry["success_likelihood"] - UPDATE_DELTA, 0.0
            )
