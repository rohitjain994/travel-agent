"""About page for Travel Buddy."""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from travel_agent.core import AuthManager

st.set_page_config(
    page_title="About - Travel Buddy",
    page_icon="ℹ️",
    layout="wide"
)

auth = AuthManager()

# Check authentication
if not auth.is_authenticated():
    st.warning("🔐 Please login to access this page")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True, type="primary"):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("📝 Sign Up", use_container_width=True):
            st.switch_page("pages/signup.py")
    st.stop()

# Header
st.markdown("# ℹ️ About Travel Buddy")
st.markdown("### Multi-Agent Architecture for Intelligent Travel Planning")
st.markdown("---")

# Introduction
st.markdown("""
Travel Buddy uses a sophisticated multi-agent architecture powered by Google's Gemini LLM 
and orchestrated with LangGraph. Each agent specializes in a specific aspect of travel planning, 
working together to create comprehensive, actionable travel itineraries.
""")

# Agent Information
st.markdown("## 🤖 Agent Architecture")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 Planner Agent")
    st.info("""
    **Role**: Travel Planning Specialist
    
    **Responsibilities**:
    - Analyzes user requirements (destination, dates, budget, preferences)
    - Creates day-by-day itinerary structure
    - Identifies research tasks needed
    - Provides budget estimates
    - Breaks down the plan into actionable steps
    
    **Output**: Comprehensive travel plan with research requirements
    """)

    st.markdown("### 🔍 Researcher Agent")
    st.info("""
    **Role**: Travel Information Specialist
    
    **Responsibilities**:
    - Researches flights, hotels, restaurants, activities
    - Provides multiple options with prices and ratings
    - Compares options and makes recommendations
    - Supplies booking information and links
    - Considers user preferences and budget constraints
    
    **Output**: Detailed research results with options and recommendations
    """)

with col2:
    st.markdown("### ✨ Executor Agent")
    st.info("""
    **Role**: Itinerary Synthesis Specialist
    
    **Responsibilities**:
    - Combines plan and research into executable itinerary
    - Adds specific times and details
    - Includes booking information and links
    - Provides travel tips and reminders
    - Creates comprehensive final report
    
    **Output**: Complete, actionable travel itinerary
    """)

    st.markdown("### ✅ Validator Agent")
    st.info("""
    **Role**: Quality Assurance Specialist
    
    **Responsibilities**:
    - Checks for completeness and consistency
    - Validates dates, times, and locations
    - Verifies budget realism
    - Suggests improvements and refinements
    - Provides next steps for enhancement
    
    **Output**: Validation feedback and improvement suggestions
    """)

st.markdown("---")

# Workflow
st.markdown("## 🔄 Workflow Process")

st.markdown("""
The system follows a structured workflow orchestrated by LangGraph:

1. **Planning Phase**: Planner Agent creates the initial travel plan
2. **Research Phase**: Researcher Agent gathers detailed information
3. **Execution Phase**: Executor Agent synthesizes everything into a final itinerary
4. **Validation Phase**: Validator Agent validates and provides improvement suggestions

Each phase builds upon the previous one, ensuring a comprehensive and well-validated travel plan.
""")

# Technology Stack
st.markdown("## 🛠️ Technology Stack")

tech_cols = st.columns(3)

with tech_cols[0]:
    st.markdown("""
    **Core Technologies**:
    - Python 3.12+
    - Streamlit
    - LangGraph
    - LangChain
    """)

with tech_cols[1]:
    st.markdown("""
    **AI & ML**:
    - Google Gemini 2.0 Flash Lite
    - Multi-Agent Architecture
    - LLM Integration
    """)

with tech_cols[2]:
    st.markdown("""
    **Data & Storage**:
    - SQLite Database
    - ReportLab (PDF)
    - Session Management
    """)

st.markdown("---")

# Features
st.markdown("## ✨ Key Features")

feature_cols = st.columns(2)

with feature_cols[0]:
    st.markdown("""
    - 🤖 Multi-Agent Architecture
    - 🧠 Gemini LLM Integration
    - 🔄 LangGraph Orchestration
    - 📋 Comprehensive Planning
    - 📊 Operation Logging
    """)

with feature_cols[1]:
    st.markdown("""
    - 🔐 User Authentication
    - 💾 Chat History Persistence
    - 📚 Conversation Management
    - 📥 PDF Export
    - 🚀 Next Steps Guidance
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Powered by Gemini LLM • Multi-Agent Architecture • LangGraph Orchestration</p>
    <p>Built with ❤️ for intelligent travel planning</p>
</div>
""", unsafe_allow_html=True)

