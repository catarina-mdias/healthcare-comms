from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from communication.config import PROMPTS_DIR
from communication.utils import StrEnum


class PromptTemplateModelRole(StrEnum):
    SYSTEM_MESSAGE = "system_message"
    USER_MESSAGE = "user_message"


class PromptTemplate:
    system_message_template_file: str
    user_message_template_file: str

    def __init__(
        self,
        system_message_template_file: str,
        user_message_template_file: str,
        prompts_dir: Path = PROMPTS_DIR,
    ):

        self._jinja_env = Environment(
            loader=FileSystemLoader([prompts_dir]),
            trim_blocks=True,
        )

        self._template_filenames = {
            PromptTemplateModelRole.SYSTEM_MESSAGE: (
                system_message_template_file
            ),
            PromptTemplateModelRole.USER_MESSAGE: user_message_template_file,
        }

    def build_system_message(self, **kwargs) -> str:
        return self._build_message(
            prompt_model_role=PromptTemplateModelRole.SYSTEM_MESSAGE, **kwargs
        )

    def build_user_message(self, **kwargs) -> str:
        return self._build_message(
            prompt_model_role=PromptTemplateModelRole.USER_MESSAGE, **kwargs
        )

    def _build_message(
        self, prompt_model_role: PromptTemplateModelRole, **kwargs
    ) -> str:
        template_text = self._jinja_env.get_template(
            self._template_filenames[prompt_model_role]
        )

        message_rendered = template_text.render(kwargs)

        return message_rendered
