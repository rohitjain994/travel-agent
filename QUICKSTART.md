# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Installation

### Option 1: Using the setup script (Recommended)

```bash
./setup.sh
```

### Option 2: Manual setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Running the Application

1. Make sure your virtual environment is activated
2. Ensure your `.env` file contains a valid `GEMINI_API_KEY`
3. Run the Streamlit app:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Usage Examples

Try these example queries:

- "Plan a 5-day trip to Paris in March with a budget of $2000"
- "I want to visit Tokyo for a week in April. Help me plan the itinerary."
- "Create a travel plan for a weekend getaway to New York City"
- "Plan a 10-day European tour visiting Paris, Rome, and Barcelona"

## Architecture Overview

The system uses a multi-agent workflow:

1. **Planner Agent** → Creates the initial travel plan
2. **Researcher Agent** → Gathers detailed information (flights, hotels, etc.)
3. **Executor Agent** → Synthesizes everything into a final itinerary
4. **Validator Agent** → Validates and refines the plan

All agents are orchestrated using LangGraph, ensuring a smooth workflow.

## Troubleshooting

### API Key Issues
- Make sure your `.env` file is in the root directory
- Verify the API key is correct and has no extra spaces
- Check that the key has proper permissions

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're using the correct Python version (3.8+)

### LangGraph Errors
- Update LangGraph: `pip install --upgrade langgraph`
- Check that all state fields are properly defined

## Support

For issues or questions, please check the main README.md file.

