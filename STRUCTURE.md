# Repository Structure

This document describes the standard repository structure for the Travel Agent project.

## Directory Structure

```
travel-agent-1/
├── src/                          # Source code directory
│   └── travel_agent/             # Main package
│       ├── __init__.py          # Package initialization
│       ├── agents/              # Agent modules
│       │   ├── __init__.py
│       │   ├── base_agent.py    # Base agent class with retry logic
│       │   ├── planner_agent.py
│       │   ├── researcher_agent.py
│       │   ├── executor_agent.py
│       │   └── validator_agent.py
│       ├── core/                # Core functionality
│       │   ├── __init__.py
│       │   ├── config.py        # Configuration settings
│       │   ├── database.py      # Database operations
│       │   ├── auth.py          # Authentication
│       │   ├── logger_config.py # Logging system
│       │   └── orchestrator.py  # LangGraph orchestrator
│       └── utils/               # Utility functions
│           ├── __init__.py
│           └── pdf_generator.py # PDF generation
│
├── pages/                        # Streamlit pages (must be at root)
│   ├── login.py                 # Login page
│   ├── signup.py                # Signup page
│   ├── about.py                 # About page
│   └── operation_logs.py        # Operation logs page
│
├── tests/                        # Test files
│   └── __init__.py
│
├── docs/                         # Documentation
│
├── scripts/                      # Utility scripts
│   └── setup.sh                 # Setup script
│
├── config/                       # Configuration files
│
├── app.py                        # Main Streamlit entry point
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── pyproject.toml                # Modern Python project config
├── MANIFEST.in                   # Package manifest
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── .python-version               # Python version
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
├── CONTRIBUTING.md               # Contribution guidelines
└── STRUCTURE.md                  # This file
```

## Package Organization

### `src/travel_agent/agents/`
Contains all agent implementations:
- **BaseAgent**: Base class with LLM integration and retry logic
- **PlannerAgent**: Creates travel plans
- **ResearcherAgent**: Gathers travel information
- **ExecutorAgent**: Synthesizes final itinerary
- **ValidatorAgent**: Validates and refines plans

### `src/travel_agent/core/`
Core system modules:
- **config.py**: Application configuration and settings
- **database.py**: SQLite database operations
- **auth.py**: User authentication and session management
- **logger_config.py**: Logging system
- **orchestrator.py**: LangGraph workflow orchestration

### `src/travel_agent/utils/`
Utility modules:
- **pdf_generator.py**: PDF generation from markdown content

### `pages/`
Streamlit pages (must be at root for Streamlit to recognize):
- **login.py**: User login
- **signup.py**: User registration
- **about.py**: Agent information
- **operation_logs.py**: System operation logs

## Entry Points

- **app.py**: Main Streamlit application entry point
- **setup.py**: Package installation entry point

## Installation

Install the package in development mode:
```bash
pip install -e .
```

This makes the `travel_agent` package available for import.

## Import Structure

All imports use the `travel_agent` package prefix:
```python
from travel_agent.core import TravelAgentOrchestrator, AuthManager
from travel_agent.agents import PlannerAgent
from travel_agent.utils import create_download_pdf
```

## Benefits of This Structure

1. **Standard Python Package**: Follows PEP 420 and modern Python packaging standards
2. **Clear Organization**: Logical separation of concerns
3. **Scalability**: Easy to add new modules and features
4. **Testability**: Clear structure for writing tests
5. **Maintainability**: Easy to navigate and understand
6. **Distribution Ready**: Can be packaged and distributed as a Python package

