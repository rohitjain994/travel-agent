"""Configuration settings for the travel agent."""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")

# Model configuration
MODEL_NAME = "gemini-2.0-flash-lite"
TEMPERATURE = 0.7

# Agent configuration
MAX_ITERATIONS = 10
VERBOSE = True

