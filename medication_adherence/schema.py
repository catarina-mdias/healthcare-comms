from pydantic import BaseModel, Field

from medication_adherence.utils import StrEnum


# Define enums for fields with limited valid options
class Gender(StrEnum):
    MALE = "Male"
    FEMALE = "Female"


class SocioeconomicStatus(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class SeverityOfCondition(StrEnum):
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"


class MessageTonePreference(StrEnum):
    CASUAL = "Casual"
    FORMAL = "Formal"
    MOTIVATIONAL = "Motivational"


class PatientProfile(BaseModel):
    """
    A model representing a patient profile with features relevant to
    medication adherence messaging.
    """

    name: str = Field(..., description="Patient's name")

    age: int = Field(..., ge=0, description="Patient's age in years")

    gender: Gender = Field(
        ..., description="Patient's gender (e.g., 'Male', 'Female')"
    )

    socioeconomic_status: SocioeconomicStatus = Field(
        ...,
        description=(
            "Economic and social standing (e.g., 'Low', 'Medium', 'High')"
        ),
    )

    primary_medical_condition: str = Field(
        ..., description=("Main health condition (e.g., 'Asthma', 'Diabetes')")
    )

    severity_of_condition: SeverityOfCondition = Field(
        ...,
        description=(
            "Severity of the primary condition (e.g., 'Mild', 'Moderate', "
            "'Severe')"
        ),
    )

    medication_name: str = Field(
        ...,
        description=(
            "Name of the prescribed medication (e.g., 'Albuterol', "
            "'Metformin')"
        ),
    )

    medication_type: str = Field(
        ...,
        description=(
            "Form of the medication (e.g., 'Pill', 'Inhaler', 'Injection')"
        ),
    )

    dosage_instructions: str = Field(
        ...,
        description=(
            "Instructions for taking the medication (e.g., 'Two puffs as "
            "needed')"
        ),
    )

    frequency_of_administration: str = Field(
        ...,
        description=(
            "How often the medication is taken (e.g., 'Daily', 'As needed')"
        ),
    )

    health_literacy_level: str = Field(
        ...,
        description=(
            "Patient's understanding of health information (e.g., 'Low', "
            "'Medium', 'High')"
        ),
    )

    daily_routine: str = Field(
        ...,
        description=(
            "Patient's typical daily schedule (e.g., 'Morning person', "
            "'Night owl')"
        ),
    )

    physical_activity_level: str = Field(
        ...,
        description=(
            "Level of physical activity (e.g., 'Sedentary', 'Active')"
        ),
    )

    caregiver_presence: bool = Field(
        ...,
        description=("Indicates if a caregiver is involved (True/False)"),
    )

    message_tone_preference: MessageTonePreference = Field(
        ...,
        description=(
            "Preferred tone for messages (e.g., 'Casual', 'Formal', "
            "'Motivational')"
        ),
    )

    motivation_level: str = Field(
        ...,
        description=(
            "Patient's motivation to adhere to treatment (e.g., 'Low', "
            "'Medium', 'High')"
        ),
    )

    beliefs_about_medication: str = Field(
        ...,
        description=(
            "Attitude toward medication (e.g., 'Trusting', 'Skeptical')"
        ),
    )

    stress_level: str = Field(
        ...,
        description="Patient's stress level (e.g., 'Low', 'Medium', 'High')",
    )

    time_since_diagnosis: int = Field(
        ...,
        ge=0,
        description=(
            "Years since the patient was diagnosed with their primary "
            "condition"
        ),
    )

    side_effect_sensitivity: str = Field(
        ...,
        description=(
            "Sensitivity to medication side effects (e.g., 'None', 'Mild',"
            " 'Severe')"
        ),
    )

    appointment_frequency: str = Field(
        ...,
        description=(
            "Frequency of healthcare appointments (e.g., 'Monthly', "
            "'Quarterly', 'Rarely')"
        ),
    )

    technology_comfort: str = Field(
        ...,
        description=(
            "Comfort level with technology (e.g., 'Low', 'Medium', 'High')"
        ),
    )
