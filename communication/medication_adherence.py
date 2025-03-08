import json
from typing import Dict, List

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
TEMPERATURE = 0.5

# Prompt template configs
PROMPT_TEMPLATE_MED_ADHERENCE = PromptTemplate(
    system_message_template_file="med_adherence_system_message.jinja2",
    user_message_template_file="med_adherence_user_message.jinja2",
)

# Vector DB configs
EMBEDDING_MODEL = "text-embedding-3-small"
SIMILARITY_THRESHOLD = 0.75
TOP_N_DOCS = 100

# Knowledge base configs
KB_FILE_NAME = "medication_adherence_kb.json"
KB_FILES_JQ_SCHEMA = ".[] | {content: .patient_profile, metadata: {id: .id}}"

# Message generation configs
HIGH_SUCCESS_MESSAGES_COUNT = 3
LOW_SUCCESS_MESSAGES_COUNT = 2

UPDATE_DELTA = 0.05


class MedicationAdherenceCommunication(Communication):
    def __init__(
        self,
    ):
        super().__init__(use_case=CommunicationUseCase.MEDICATION_ADHERENCE)
        self.medication_adherence_vector_db = self._init_vector_db()
        self.chat_model = ChatModel(openai_key=settings.OPENAI_API_KEY)

    @staticmethod
    def _init_vector_db():
        return VectorDatabase(
            kb_file_name=KB_FILE_NAME,
            kb_directory_path=DATA_DIR,
            embedding_model=EMBEDDING_MODEL,
            openai_key=settings.OPENAI_API_KEY,
            file_jq_schema=KB_FILES_JQ_SCHEMA,
        )

    async def get_communication(
        self, request_uuid: str, patient_profile: PatientProfile
    ) -> Dict:

        patient_profile = patient_profile.model_dump()

        similar_profile_ids = self._get_similar_profiles(
            {k: v for k, v in patient_profile.items() if k != "name"}
        )

        sorted_entries = self._get_sorted_entries(
            profile_ids=similar_profile_ids
        )

        high_success_messages = sorted_entries[:HIGH_SUCCESS_MESSAGES_COUNT]
        low_success_messages = sorted_entries[-LOW_SUCCESS_MESSAGES_COUNT:]

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
        # Load knowledge base data
        kb_file_path = DATA_DIR / KB_FILE_NAME
        kb_data = load_json_file(kb_file_path)

        # Create ID-to-entry mapping for faster lookups
        kb_data_map = {entry["id"]: entry for entry in kb_data}

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
        with open(kb_file_path, "w", encoding="utf-8") as f:
            json.dump(kb_data, f, indent=2, ensure_ascii=False)

        # Reinitialize vector database with updated data
        self.medication_adherence_vector_db = self._init_vector_db()

    def _get_similar_profiles(self, patient_dict: Dict) -> List[int]:
        similar_profiles = self.medication_adherence_vector_db.get_documents_with_similarity_score(  # noqa
            user_query=str(patient_dict),
            top_k=TOP_N_DOCS,
            score_threshold=SIMILARITY_THRESHOLD,
        )
        return [doc.document_id for doc in similar_profiles]

    @staticmethod
    def _get_sorted_entries(profile_ids: List[int]) -> List[Dict]:
        kb_data = load_json_file(DATA_DIR / KB_FILE_NAME)
        matching_entries = [
            entry for entry in kb_data if entry["id"] in profile_ids
        ]
        sorted_entries = sorted(
            matching_entries,
            key=lambda x: x["success_likelihood"],
            reverse=True,
        )
        return sorted_entries

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
