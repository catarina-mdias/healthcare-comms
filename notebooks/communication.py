#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import uuid  # noqa

from medication_adherence.communication import MedicationAdherenceCommunication
from medication_adherence.config import DATA_DIR
from medication_adherence.schema import PatientProfile
from medication_adherence.utils import load_json_file

# In[2]:


test_patients = load_json_file(DATA_DIR / "test_patients.json")


# In[3]:


patient_profile = PatientProfile.model_validate(random.choice(test_patients))


# In[4]:


communication_obj = MedicationAdherenceCommunication()


# In[5]:


communication_dict = await communication_obj.get_communication(
    request_uuid=str(uuid.uuid4()), patient_profile=patient_profile
)


# In[8]:


communication_dict["message"]


# In[9]:


print(communication_dict)
