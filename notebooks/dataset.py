#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
from typing import Dict, Tuple

from medication_adherence.chat_model import ChatModel, generate_message
from medication_adherence.config import DATA_DIR, get_settings
from medication_adherence.prompt import PromptTemplate
from medication_adherence.utils import load_json_file


# In[3]:


patients = load_json_file(DATA_DIR / "patients.json")
messages = load_json_file(DATA_DIR / "messages.json")


# In[5]:


prompt_template_dataset_generator = PromptTemplate(
    system_message_template_file="dataset_generator_system_message.jinja2",
    user_message_template_file="dataset_generator_user_message.jinja2",
)
chat_model = ChatModel(get_settings().OPENAI_API_KEY)

TEMPERATURE = 0.1  # low value as we want determinstic responses
GPT_MODEL = "gpt-4o"


# In[6]:


async def get_success_likelihood(
    patient_data: Dict, message_text: str
) -> Tuple[float, str]:

    system_message = prompt_template_dataset_generator.build_system_message()

    user_message = prompt_template_dataset_generator.build_user_message(
        patient_data=patient_data, message_text=message_text
    )

    response = await generate_message(
        chat_model=chat_model,
        system_message=system_message,
        user_message=user_message,
        model=GPT_MODEL,
        temperature=TEMPERATURE,
        json_format=True,
    )
    response_dict = json.loads(response)

    return float(response_dict["likelihood"]), response_dict["explanation"]


# In[ ]:


dataset = []
for patient in patients:
    for message in messages:
        message_text = message["message"]
        likelihood, reasoning = await get_success_likelihood(
            patient_data=patient, message_text=message_text
        )
        row = {
            "patient_profile": patient,
            "message": message_text,
            "reasoning": reasoning,
            "success_likelihood": likelihood,
        }
        dataset.append(row)


# In[ ]:


with open(
    DATA_DIR / "medication_adherence_kb.json", "w", encoding="utf-8"
) as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"Generated dataset with {len(dataset)} rows and saved to file")

