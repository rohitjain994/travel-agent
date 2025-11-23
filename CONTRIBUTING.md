# Contributing to Travel Agent

Thank you for your interest in contributing to the Travel Agent project!

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install in development mode: `pip install -e .`

## Project Structure

- `src/travel_agent/` - Main package source code
- `pages/` - Streamlit pages (must be at root for Streamlit)
- `tests/` - Test files
- `docs/` - Documentation
- `app.py` - Main Streamlit entry point

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

## Testing

Run tests with:
```bash
pytest tests/
```

## Submitting Changes

1. Create a feature branch
2. Make your changes
3. Add tests if applicable
4. Update documentation
5. Submit a pull request

