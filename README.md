# 🏥 Healthcare Communication System - Medication Adherence

## Project Overview
This project develops an AI-powered system to boost medication adherence using personalized SMS, 
leveraging patient profiles, retrieval-augmented generation, and feedback loops to optimize messages. 

---

## Repository Structure
```
healthcare-comms/
│── api/                                          # API endpoints and logic
│   ├── init.py                                   # Package initialization
│   ├── controllers.py                            # API route handlers
│   ├── exception.py                              # Error handling
│   ├── main.py                                   # FastAPI application entry point
│   ├── models.py                                 # Pydantic models
│── api_client/                                   # Client-side API interaction
│   ├── medication_adherence.py                   # Adherence API client
│── communication/                                # Communicaiton generation business logic
│   ├── init.py                                   # Package initialization
│   ├── chat_model.py                             # Chat model utils
│   ├── communication.py                          # Communication Abstract Class
│   ├── config.py                                 # Configuration settings
│   ├── medication_adherence.py                   # Adherence-specific communication logic
│   ├── prompt.py                                 # Prompt management
│   ├── schema.py                                 # Data and Enums
│   ├── utils.py                                  # Other Utility functions
│   ├── vector_database.py                        # Vector database Class for RAG Utility
│── data/                                         # Datasets
│   ├── medication_adherence.json                 # Dataset with messages and patient profiles pairs and success likelihood
│   ├── messages.json                             # Message templates
│   ├── patients.json                             # Patient profiles
│   ├── test_patients.json                        # Test patient profiles
│── notebooks/                                    # Jupyter Notebooks
│   ├── dataset.ipynb                             # Message Pool dataset building
│   ├── medication_adherence.py                   # Auxiliary notebook that can be used to medication adherence pipeline
│── prompts/                                      # Prompt templates
│   ├── dataset_generator_system_message.jinja2   # System message prompt used for dataset generation
│   ├── dataset_generator_user_message.jinja2     # User message prompt used for dataset generation
│   ├── med_adherence_system_message.jinja2       # System message prompt used for medication adherence communication
│   ├── med_adherence_user_message.jinja2         # User message prompt used for medication adherence communication
│── tests/                                        # Unit tests
│   ├── test_prompt.py                            # Prompt Template Unit tests
│   ├── test_vector_database.py                   # Vector database Utility Unit tests
│── env/                                          # Virtual environment
│   ├── .env.example                              # Example env file
│   ├── flake8                                    # Linting config
│   ├── .gitignore                                # Git ignore rules
│   ├── .pre-commit-config.yaml                   # Pre-commit hooks
│   ├── Makefile                                  # Build automation
│   ├── Pipfile                                   # Dependency management
│   ├── Pipfile.lock                              # Locked dependencies
│   ├── pyproject.toml                            # Project config
│   ├── README.md                                 # Project documentation
│   ├── setup.py                                  # Package setup
```
---


## Setup Instructions
### Clone the Repository
```bash
git clone https://github.com/catarina-mdias/healthcare-comms.git
cd healthcare-comms
```

### Create & Activate Virtual Environment
```bash
make venv
```

### Setup Environment Variables
Create a `.env` file in the project root and dd your OpenAI API Key.
```
OPENAI_API_KEY=your-openai-key-here
```

## Testing
Run the unit tests with the following command. This will run both prompt template and vector database unit tests.
```bash
make test
```

## Running the API
Start the FastAPI application with the following command:
```bash
make launch-app
```

### Test Endpoints and run messaging pipeline
Assuming application running:
```bash
python api_client/medication_adherence.py
```

## API
The `api/` folder contains the core FastAPI application logic, serving as the interface for the healthcare communication system. It includes:

- `__init__.py`: Initializes the API package.
- `controllers.py`: Defines API endpoints using `fastapi-router-controller`, with two main routes:
  - `/medication-adherence`: Generates personalized medication adherence messages based on a `MedicationAdherenceCommRequest`, returning a `MedicationAdherenceCommResponse` with message and metadata, handling errors via `CommunicationServiceException`.
  - `/success`: Updates success likelihoods in the message pool based on a `CommunicationSuccessRequest`, prepared to support multiple use cases such as medication adherence, with logging and error handling.
- `exception.py`: Manages custom exceptions like `CommunicationServiceException` and their handling.
- `main.py`: FastAPI application entry point, orchestrating the API lifecycle.
- `models.py`: Pydantic models for request/response validation.

This folder facilitates integration with external systems, aligning with the project’s API design for message generation and success updates.

## Communication
The communication/ folder houses the core logic for generating and managing personalized messages, implementing the system's AI-driven messaging pipeline. It includes:

- `__init__.py`: Initializes the communication package.  
- `chat_model.py`: Provides utilities for interacting with LLMs like GPT-4o, including the `generate_message` function for message creation.  
- `communication.py`: Defines the abstract `Communication` class, specifying methods (`get_communication`, `act_on_communication_result`) for message generation and feedback handling across use cases.  
- `config.py`: Manages configuration settings.   
- `medication_adherence.py`: Implements `MedicationAdherenceCommunication`, a subclass for medication adherence messaging. It uses RAG with `text-embedding-3-small` and Chroma DB to retrieve similar profiles, generates messages via GPT-4o, and updates success likelihoods. Uses the prompt templates in the `prompts/` folder to load system and user messages used for message generation.  
- `prompt.py`: Handles prompt management with `PromptTemplate`, loading and formatting system and user message. Leverages Jinja2 templates for dynamic variables rendering. 
- `schema.py`: Defines data schemas and enums.  
- `utils.py`: Contains helper functions.  
- `vector_database.py`: Implements `VectorDatabase` for RAG, providing documentation loading, vector storage, and similarity search capabilities.  

This folder orchestrates the message generation pipeline, from profile retrieval to feedback updates, ensuring adaptability and personalization.

## Other Folders
- `data/`: Stores the project’s datasets in JSON format, including `medication_adherence.json` (message-patient pairs with success likelihoods), `messages.json` (message templates), `patients.json` (patient profiles), and `test_patients.json (profiles for testing). These files provide the foundational data for message generation and validation.
- `prompts/`: Contains Jinja2 prompt templates used for message generation (`med_adherence_*.jinja2`) and dataset generation (`dataset_generator_*.jinja2`).
- `tests/`: Unit tests to validate core functionalities, with `test_prompt.py` testing prompt template loading and formatting, and `test_vector_database.py` verifying the vector database’s similarity search and retrieval accuracy.
- `notebooks/`: Houses the Jupyter notebooks. `dataset.ipynb` used to generate the message-patient dataset with GPT-4o-assigned success likelihoods; and `medication_adherence.ipynb` - an auxiliary notebook for testing the medication adherence pipeline.

## Contact

Please connect with me at:

👤 Name: Catarina Dias  
📧 Email: [catarina.m.dias8@gmail.com](mailto:catarina.m.dias8@gmail.com)  
🔗 LinkedIn: [Catarina Dias](https://www.linkedin.com/in/catarinamdias/)

Thank you for your time!