"""Streamlit UI for the travel agent chatbot."""
import streamlit as st
from orchestrator import TravelAgentOrchestrator
from logger_config import logger
import time


# Page configuration
st.set_page_config(
    page_title="Travel Agent Chatbot",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        background-color: #f0f2f6;
    }
    .stChatMessage {
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = TravelAgentOrchestrator()

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

if "show_logs" not in st.session_state:
    st.session_state.show_logs = False


def display_agent_status(agent_name: str, status: str):
    """Display agent status in sidebar."""
    with st.sidebar:
        st.markdown(f"### 🤖 {agent_name}")
        st.markdown(f"**Status:** {status}")
        st.markdown("---")


def main():
    """Main application function."""
    # Header
    st.markdown('<div class="main-header">✈️ Travel Agent Chatbot</div>', unsafe_allow_html=True)
    st.markdown("### Your AI-powered travel planning assistant")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Agent Status")
        st.markdown("---")
        st.info("This system uses a multi-agent architecture:\n\n"
                "1. **Planner** - Creates travel plans\n"
                "2. **Researcher** - Gathers travel information\n"
                "3. **Executor** - Synthesizes final itinerary\n"
                "4. **Validator** - Validates and refines plans")
        
        st.markdown("---")
        st.session_state.show_logs = st.checkbox("📊 Show Operation Logs", value=st.session_state.show_logs)
        
        if st.session_state.show_logs:
            st.markdown("### 📊 Operation Logs")
            logs = logger.get_logs()
            
            if logs:
                # Show log summary
                summary = logger.get_log_summary()
                st.metric("Total Operations", summary["total"])
                
                # Filter options
                filter_agent = st.selectbox(
                    "Filter by Agent",
                    ["All"] + list(summary["by_agent"].keys())
                )
                
                # Show filtered logs
                filtered_logs = logs if filter_agent == "All" else logger.get_logs(agent=filter_agent)
                
                # Display logs in reverse order (newest first)
                for log in reversed(filtered_logs[-20:]):  # Show last 20 logs
                    status_emoji = {
                        "success": "✅",
                        "error": "❌",
                        "warning": "⚠️",
                        "info": "ℹ️"
                    }.get(log["status"], "📝")
                    
                    with st.expander(f"{status_emoji} [{log['agent']}] {log['operation']}", expanded=False):
                        st.text(f"Time: {log['timestamp']}")
                        if log.get("duration"):
                            st.text(f"Duration: {log['duration']:.2f}s")
                        if log.get("details"):
                            st.text(f"Details: {log['details']}")
            else:
                st.info("No logs yet. Start a conversation to see operations.")
        
        st.markdown("---")
        
        if st.button("🔄 Clear Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            logger.clear_logs()
            st.rerun()
        
        if st.button("🗑️ Clear Logs"):
            logger.clear_logs()
            st.success("Logs cleared!")
            st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your travel plans..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("Planning your trip..."):
                try:
                    # Show processing status
                    status_placeholder = st.empty()
                    
                    # Process through orchestrator
                    result = st.session_state.orchestrator.process_query(
                        prompt,
                        st.session_state.conversation_history
                    )
                    
                    # Display results
                    response_parts = []
                    
                    # Show plan
                    if result.get("plan"):
                        with st.expander("📝 Travel Plan", expanded=True):
                            st.markdown(result["plan"])
                        response_parts.append("**Travel Plan Created** ✓")
                    
                    # Show research results
                    if result.get("research_results"):
                        with st.expander("🔍 Research Results", expanded=False):
                            st.markdown(result["research_results"])
                        response_parts.append("**Research Completed** ✓")
                    
                    # Show final itinerary
                    if result.get("final_itinerary"):
                        st.markdown("### ✨ Final Travel Itinerary")
                        st.markdown(result["final_itinerary"])
                        response_parts.append("**Final Itinerary Ready** ✓")
                    
                    # Show validation
                    if result.get("validation"):
                        with st.expander("✅ Validation", expanded=False):
                            st.markdown(result["validation"])
                        response_parts.append("**Plan Validated** ✓")
                    
                    # Create summary response
                    summary = "\n\n".join(response_parts)
                    if not summary:
                        summary = "I've processed your travel request. Please check the details above."
                    
                    # Add assistant response to history
                    full_response = f"{summary}\n\n{result.get('final_itinerary', result.get('plan', ''))}"
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.session_state.conversation_history.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Powered by Gemini LLM • Multi-Agent Architecture • LangGraph Orchestration"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

