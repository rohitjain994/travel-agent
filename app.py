"""Streamlit UI for the travel agent chatbot."""
import streamlit as st
import re
from orchestrator import TravelAgentOrchestrator
from logger_config import logger
from auth import AuthManager
from datetime import datetime
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

# Initialize authentication
auth = AuthManager()

# Check authentication
if not auth.is_authenticated():
    st.warning("🔐 Please login to access the Travel Agent")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True, type="primary"):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("📝 Sign Up", use_container_width=True):
            st.switch_page("pages/signup.py")
    st.markdown("---")
    st.info("💡 Use the sidebar navigation to access Login or Sign Up pages")
    st.stop()

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = TravelAgentOrchestrator()

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "processing" not in st.session_state:
    st.session_state.processing = False

if "show_logs" not in st.session_state:
    st.session_state.show_logs = False

if "chat_loaded" not in st.session_state:
    st.session_state.chat_loaded = False


def display_agent_status(agent_name: str, status: str):
    """Display agent status in sidebar."""
    with st.sidebar:
        st.markdown(f"### 🤖 {agent_name}")
        st.markdown(f"**Status:** {status}")
        st.markdown("---")


def main():
    """Main application function."""
    # Header
    user = auth.get_current_user()
    st.markdown('<div class="main-header">✈️ Travel Agent Chatbot</div>', unsafe_allow_html=True)
    if user:
        st.markdown(f"### Welcome back, {user.get('full_name', user.get('username', 'User'))}! 👋")
    else:
        st.markdown("### Your AI-powered travel planning assistant")
    
    # Sidebar
    with st.sidebar:
        # User info
        user = auth.get_current_user()
        if user:
            st.markdown(f"### 👤 {user.get('full_name', user.get('username', 'User'))}")
            st.caption(f"@{user.get('username', '')}")
            
            # Show chat history stats
            from database import Database
            db = Database()
            chat_count = db.get_chat_count(user.get("user_id"))
            if chat_count > 0:
                st.caption(f"💬 {chat_count} messages saved")
            
            if st.button("🚪 Logout", use_container_width=True):
                auth.logout()
                st.rerun()
            st.markdown("---")
            
            # Show previous conversations
            st.markdown("### 💬 Previous Conversations")
            conversations = db.get_conversations(user.get("user_id"), limit=10)
            
            if conversations:
                for conv in conversations:
                    # Format date
                    try:
                        # Handle different datetime formats
                        updated_str = conv['updated_at']
                        if 'T' in updated_str:
                            updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00').split('.')[0])
                        else:
                            updated = datetime.strptime(updated_str, '%Y-%m-%d %H:%M:%S')
                        date_str = updated.strftime("%b %d, %Y")
                    except:
                        date_str = conv['updated_at'][:10] if conv['updated_at'] else "Unknown"
                    
                    # Create button for each conversation
                    button_label = f"📝 {conv['title']}"
                    if st.button(
                        button_label,
                        key=f"conv_{conv['conversation_id']}",
                        use_container_width=True,
                        help=f"{date_str} • {conv['message_count']} messages"
                    ):
                        # Load this conversation
                        st.session_state.current_conversation_id = conv['conversation_id']
                        messages = db.get_chat_history(user.get("user_id"), conversation_id=conv['conversation_id'])
                        if messages:
                            st.session_state.messages = [
                                {"role": msg["role"], "content": msg["content"]}
                                for msg in messages
                            ]
                            st.session_state.conversation_history = [
                                {"role": msg["role"], "content": msg["content"]}
                                for msg in messages
                            ]
                        st.rerun()
                
                if st.button("➕ New Conversation", use_container_width=True, type="primary"):
                    st.session_state.current_conversation_id = None
                    st.session_state.messages = []
                    st.session_state.conversation_history = []
                    st.rerun()
            else:
                st.info("No previous conversations. Start chatting to create one!")
            
            st.markdown("---")
        
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
            # Clear current conversation from database
            if auth.is_authenticated():
                user = auth.get_current_user()
                if user and user.get("user_id") and st.session_state.current_conversation_id:
                    from database import Database
                    db = Database()
                    db.clear_chat_history(user["user_id"], st.session_state.current_conversation_id)
            st.session_state.current_conversation_id = None
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
        # Get current user
        user = auth.get_current_user()
        user_id = user.get("user_id") if user else None
        
        # Get or create conversation_id
        if not st.session_state.current_conversation_id:
            st.session_state.current_conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add user message to chat
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        st.session_state.conversation_history.append(user_message)
        
        # Save user message to database
        if user_id:
            from database import Database
            db = Database()
            db.save_chat_message(
                user_id, 
                "user", 
                prompt, 
                conversation_id=st.session_state.current_conversation_id
            )
        
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
                        with st.expander("✅ Validation & Next Steps", expanded=True):
                            st.markdown(result["validation"])
                        response_parts.append("**Plan Validated** ✓")
                    
                    # Extract and highlight next steps from validation or itinerary
                    next_steps_text = ""
                    validation_text = result.get("validation", "")
                    itinerary_text = result.get("final_itinerary", "")
                    
                    # Look for "Next Steps" section in validation (multiple patterns)
                    patterns = [
                        r'(?i)(?:next steps for improvement|next steps for enhancement|next steps)[:]*\s*\n*(.*?)(?=\n\n|\n##|\n#|$)',
                        r'(?i)(?:##\s*)?next steps[:\s]*(.*?)(?=\n\n##|\n#|$)',
                        r'(?i)next steps[:\s]*\n(.*?)(?=\n\n|$)',
                    ]
                    
                    for pattern in patterns:
                        if not next_steps_text and validation_text:
                            match = re.search(pattern, validation_text, re.DOTALL)
                            if match:
                                next_steps_text = match.group(1).strip()
                                if len(next_steps_text) > 50:  # Ensure it's substantial
                                    break
                    
                    # If not found in validation, check itinerary
                    if not next_steps_text and itinerary_text:
                        for pattern in patterns:
                            match = re.search(pattern, itinerary_text, re.DOTALL)
                            if match:
                                next_steps_text = match.group(1).strip()
                                if len(next_steps_text) > 50:  # Ensure it's substantial
                                    break
                    
                    # If still not found, use the entire validation as next steps
                    if not next_steps_text and validation_text:
                        # Check if validation contains improvement suggestions
                        if any(keyword in validation_text.lower() for keyword in 
                               ['improvement', 'suggest', 'recommend', 'next', 'enhance', 'refine']):
                            next_steps_text = validation_text
                    
                    # Display next steps prominently
                    st.markdown("---")
                    st.markdown("### 🚀 Next Steps for Improvement")
                    if next_steps_text:
                        st.info(next_steps_text)
                    else:
                        # Fallback message
                        st.info("""
                        **To make your travel plan even more promising, consider:**
                        - Providing more specific preferences (dietary restrictions, activity levels, interests)
                        - Sharing your budget range for better recommendations
                        - Specifying any must-see attractions or experiences
                        - Adding travel dates for accurate pricing and availability
                        - Mentioning any special occasions or requirements
                        """)
                    
                    # Create summary response
                    summary = "\n\n".join(response_parts)
                    if not summary:
                        summary = "I've processed your travel request. Please check the details above."
                    
                    # Add assistant response to history
                    full_response = f"{summary}\n\n{result.get('final_itinerary', result.get('plan', ''))}"
                    assistant_message = {"role": "assistant", "content": full_response}
                    st.session_state.messages.append(assistant_message)
                    st.session_state.conversation_history.append(assistant_message)
                    
                    # Save assistant message to database
                    if user_id:
                        from database import Database
                        db = Database()
                        db.save_chat_message(
                            user_id, 
                            "assistant", 
                            full_response,
                            conversation_id=st.session_state.current_conversation_id
                        )
                    
                except Exception as e:
                    # Handle rate limit errors specifically
                    from agents.base_agent import RateLimitError
                    
                    if isinstance(e, RateLimitError):
                        error_msg = f"⚠️ **Rate Limit Error**\n\n{str(e)}\n\n💡 **Suggestions:**\n- Wait a few moments before trying again\n- The system will automatically retry with delays\n- Consider breaking your request into smaller parts"
                        st.warning("⚠️ API Rate Limit Reached")
                    else:
                        error_msg = f"❌ **Error:** {str(e)}\n\nPlease try again or rephrase your request."
                        st.error("❌ An error occurred")
                    
                    error_message = {"role": "assistant", "content": error_msg}
                    st.session_state.messages.append(error_message)
                    st.session_state.conversation_history.append(error_message)
                    
                    # Save error message to database
                    if user_id:
                        from database import Database
                        db = Database()
                        db.save_chat_message(
                            user_id, 
                            "assistant", 
                            error_msg,
                            conversation_id=st.session_state.current_conversation_id
                        )
    
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

