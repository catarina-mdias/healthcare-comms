#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import uuid  # noqa

from communication.config import DATA_DIR
from communication.medication_adherence import MedicationAdherenceCommunication
from communication.schema import PatientProfile
from communication.utils import load_json_file


# In[2]:


test_patients = load_json_file(DATA_DIR / "test_patients.json")


# In[3]:


patient_profile = PatientProfile.model_validate(random.choice(test_patients))


# In[4]:


medication_adherence_communication = MedicationAdherenceCommunication()


# In[5]:


med_adherence_comm_result = (
    await medication_adherence_communication.get_communication(
        request_uuid=str(uuid.uuid4()),
        patient_profile=patient_profile,
    )
)


# In[6]:


med_adherence_comm_result["message"]


# In[7]:


print(med_adherence_comm_result)


# In[8]:


SUCCESSFUL = True
await medication_adherence_communication.act_on_communication_result(
    was_successful=SUCCESSFUL,
    low_success_examples_id=med_adherence_comm_result[
        "low_success_examples_id"
    ],
    high_success_examples_id=med_adherence_comm_result[
        "high_success_examples_id"
    ],
)

