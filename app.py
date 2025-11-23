"""Streamlit UI for Travel Buddy."""
import streamlit as st
import re
import sys
from pathlib import Path
import threading
from queue import Queue

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from travel_agent.core import TravelAgentOrchestrator, logger, AuthManager
from travel_agent.core.database import Database
from travel_agent.utils import create_download_pdf
from datetime import datetime
import time


# Page configuration
st.set_page_config(
    page_title="Travel Buddy",
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

# Auto-scroll JavaScript to scroll to bottom (last message)
st.markdown("""
<script>
function scrollToBottom() {
    // Wait for content to render
    setTimeout(function() {
        // Find the main content area
        const mainContent = document.querySelector('[data-testid="stAppViewContainer"]');
        if (mainContent) {
            // Scroll to bottom smoothly
            mainContent.scrollTo({
                top: mainContent.scrollHeight,
                behavior: 'smooth'
            });
        }
        
        // Also try scrolling the window
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
        
        // Try to find chat messages container and scroll it
        const chatMessages = document.querySelectorAll('[data-testid="stChatMessage"]');
        if (chatMessages.length > 0) {
            const lastMessage = chatMessages[chatMessages.length - 1];
            lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }, 100);
}

// Scroll on page load
window.addEventListener('load', scrollToBottom);

// Scroll when new content is added (MutationObserver)
const observer = new MutationObserver(function(mutations) {
    scrollToBottom();
});

// Observe changes to the document body
observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Also scroll after a short delay to catch dynamically added content
setTimeout(scrollToBottom, 500);
</script>
""", unsafe_allow_html=True)

# Initialize authentication
auth = AuthManager()

# Check authentication
if not auth.is_authenticated():
    st.warning("🔐 Please login to access Travel Buddy")
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

if "processing_query" not in st.session_state:
    st.session_state.processing_query = None

if "processing_result" not in st.session_state:
    st.session_state.processing_result = None

if "processing_error" not in st.session_state:
    st.session_state.processing_error = None

if "processing_thread" not in st.session_state:
    st.session_state.processing_thread = None

if "processing_queue" not in st.session_state:
    st.session_state.processing_queue = Queue()

if "chat_loaded" not in st.session_state:
    st.session_state.chat_loaded = False


def display_agent_status(agent_name: str, status: str):
    """Display agent status in sidebar."""
    with st.sidebar:
        st.markdown(f"### 🤖 {agent_name}")
        st.markdown(f"**Status:** {status}")
        st.markdown("---")


def process_query_in_background(query: str, conversation_history: list, result_queue: Queue, user_id: int = None, conversation_id: str = None):
    """Process query in background thread and put result in queue (thread-safe)."""
    # Note: This function runs in a separate thread
    # We cannot access st.session_state from here, so we use a queue instead
    try:
        orchestrator = TravelAgentOrchestrator()
        
        # Process through orchestrator
        result = orchestrator.process_query(
            query,
            conversation_history
        )
        
        # Put result in queue (thread-safe)
        result_queue.put({"type": "success", "result": result})
        
    except Exception as e:
        # Handle errors
        from travel_agent.agents.base_agent import RateLimitError
        
        if isinstance(e, RateLimitError):
            error_msg = f"⚠️ **Rate Limit Error**\n\n{str(e)}\n\n💡 **Suggestions:**\n- Wait a few moments before trying again\n- The system will automatically retry with delays\n- Consider breaking your request into smaller parts"
        else:
            error_msg = f"❌ **Error:** {str(e)}\n\nPlease try again or rephrase your request."
        
        # Put error in queue (thread-safe)
        result_queue.put({"type": "error", "error": error_msg})


def main():
    """Main application function."""
    # Header
    user = auth.get_current_user()
    st.markdown('<div class="main-header">✈️ Travel Buddy</div>', unsafe_allow_html=True)
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
        
        # Navigation
        st.header("🧭 Navigation")
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("ℹ️ About", use_container_width=True):
                st.switch_page("pages/about.py")
        with nav_col2:
            if st.button("📊 Logs", use_container_width=True):
                st.switch_page("pages/operation_logs.py")
        
        st.markdown("---")
        
        # Quick stats
        st.header("📈 Quick Stats")
        summary = logger.get_log_summary()
        if summary["total"] > 0:
            st.metric("Total Operations", summary["total"])
            success_count = summary["by_status"].get("success", 0)
            st.caption(f"✅ {success_count} successful")
        else:
            st.info("No operations yet")
        
        st.markdown("---")
        
        if st.button("🔄 Clear Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            logger.clear_logs()
            # Clear current conversation from database
            if auth.is_authenticated():
                user = auth.get_current_user()
                if user and user.get("user_id") and st.session_state.current_conversation_id:
                    db = Database()
                    db.clear_chat_history(user["user_id"], st.session_state.current_conversation_id)
            st.session_state.current_conversation_id = None
            st.rerun()
        
        if st.button("🗑️ Clear Logs"):
            logger.clear_logs()
            st.success("Logs cleared!")
            st.rerun()
    
    # Check for results from background thread (thread-safe queue)
    if not st.session_state.processing_queue.empty():
        try:
            queue_result = st.session_state.processing_queue.get_nowait()
            if queue_result["type"] == "success":
                st.session_state.processing_result = queue_result["result"]
                st.session_state.processing = False
            elif queue_result["type"] == "error":
                st.session_state.processing_error = queue_result["error"]
                st.session_state.processing = False
        except:
            pass  # Queue might be empty, ignore
    
    # Check for pending processing result and display it
    if st.session_state.processing_result is not None:
        result = st.session_state.processing_result
        processing_query = st.session_state.processing_query
        
        # Build full response content
        response_content_parts = []
        response_parts = []
        
        if result.get("plan"):
            response_content_parts.append("## 📝 Travel Plan\n\n" + result["plan"])
            response_parts.append("**Travel Plan Created** ✓")
        
        if result.get("research_results"):
            response_content_parts.append("## 🔍 Research Results\n\n" + result["research_results"])
            response_parts.append("**Research Completed** ✓")
        
        if result.get("final_itinerary"):
            response_content_parts.append("## ✨ Final Travel Itinerary\n\n" + result["final_itinerary"])
            response_parts.append("**Final Itinerary Ready** ✓")
        
        if result.get("validation"):
            response_content_parts.append("## ✅ Validation & Next Steps\n\n" + result["validation"])
            response_parts.append("**Plan Validated** ✓")
        
        # Extract next steps
        next_steps_text = ""
        validation_text = result.get("validation", "")
        itinerary_text = result.get("final_itinerary", "")
        
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
                    if len(next_steps_text) > 50:
                        break
        
        if not next_steps_text and itinerary_text:
            for pattern in patterns:
                match = re.search(pattern, itinerary_text, re.DOTALL)
                if match:
                    next_steps_text = match.group(1).strip()
                    if len(next_steps_text) > 50:
                        break
        
        if not next_steps_text and validation_text:
            if any(keyword in validation_text.lower() for keyword in 
                   ['improvement', 'suggest', 'recommend', 'next', 'enhance', 'refine']):
                next_steps_text = validation_text
        
        if next_steps_text:
            response_content_parts.append("## 🚀 Next Steps for Improvement\n\n" + next_steps_text)
        else:
            fallback_steps = """
**To make your travel plan even more promising, consider:**
- Providing more specific preferences (dietary restrictions, activity levels, interests)
- Sharing your budget range for better recommendations
- Specifying any must-see attractions or experiences
- Adding travel dates for accurate pricing and availability
- Mentioning any special occasions or requirements
            """
            response_content_parts.append("## 🚀 Next Steps for Improvement\n\n" + fallback_steps)
        
        full_response = "\n\n---\n\n".join(response_content_parts)
        summary = "\n\n".join(response_parts) if response_parts else "I've processed your travel request."
        
        # Add to messages if not already there
        assistant_message = {"role": "assistant", "content": full_response}
        if not any(msg.get("content") == full_response for msg in st.session_state.messages if msg.get("role") == "assistant"):
            st.session_state.messages.append(assistant_message)
            st.session_state.conversation_history.append(assistant_message)
            
            # Save to database
            user = auth.get_current_user()
            user_id = user.get("user_id") if user else None
            if user_id:
                db = Database()
                db.save_chat_message(
                    user_id, 
                    "assistant", 
                    full_response,
                    conversation_id=st.session_state.current_conversation_id
                )
        
        # Clear processing state
        st.session_state.processing = False
        st.session_state.processing_query = None
        st.session_state.processing_result = None
        st.rerun()
    
    # Check for processing error
    if st.session_state.processing_error is not None:
        error_msg = st.session_state.processing_error
        error_message = {"role": "assistant", "content": error_msg}
        if not any(msg.get("content") == error_msg for msg in st.session_state.messages if msg.get("role") == "assistant"):
            st.session_state.messages.append(error_message)
            st.session_state.conversation_history.append(error_message)
            
            # Save to database
            user = auth.get_current_user()
            user_id = user.get("user_id") if user else None
            if user_id:
                db = Database()
                db.save_chat_message(
                    user_id, 
                    "assistant", 
                    error_msg,
                    conversation_id=st.session_state.current_conversation_id
                )
        
        # Clear error state
        st.session_state.processing_error = None
        st.session_state.processing = False
        st.session_state.processing_query = None
        st.rerun()
    
    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Display assistant messages in expandable dropdown
                with st.expander(f"💬 Assistant Response {idx + 1}", expanded=False):
                    st.markdown(message["content"])
                    
                    # Add download PDF button
                    try:
                        pdf_data = create_download_pdf(message["content"], f"travel_plan_{idx + 1}.pdf")
                        st.download_button(
                            label="📥 Download as PDF",
                            data=pdf_data,
                            file_name=f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx + 1}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
            else:
                # Display user messages directly
                st.markdown(message["content"])
    
    # Add scroll trigger after messages are displayed
    if st.session_state.messages:
        st.markdown("""
        <script>
        // Scroll to bottom after messages are rendered
        setTimeout(function() {
            const mainContent = document.querySelector('[data-testid="stAppViewContainer"]');
            if (mainContent) {
                mainContent.scrollTo({
                    top: mainContent.scrollHeight,
                    behavior: 'smooth'
                });
            }
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
            const chatMessages = document.querySelectorAll('[data-testid="stChatMessage"]');
            if (chatMessages.length > 0) {
                const lastMessage = chatMessages[chatMessages.length - 1];
                lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
        }, 200);
        </script>
        """, unsafe_allow_html=True)
    
    # Show processing indicator if processing
    if st.session_state.processing and st.session_state.processing_query:
        with st.chat_message("assistant"):
            st.info(f"🔄 **Processing your query:** {st.session_state.processing_query[:100]}...")
            st.markdown("⏳ Your request is being processed in the background. You can navigate to other pages and come back - the result will appear here when ready!")
        
        # Scroll to processing indicator
        st.markdown("""
        <script>
        setTimeout(function() {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        # Auto-refresh every 3 seconds
        time.sleep(3)
        st.rerun()
    
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
            db = Database()
            db.save_chat_message(
                user_id, 
                "user", 
                prompt, 
                conversation_id=st.session_state.current_conversation_id
            )
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Start processing in background thread
        if st.session_state.processing_thread is None or not st.session_state.processing_thread.is_alive():
            # Set processing state
            st.session_state.processing = True
            st.session_state.processing_query = prompt
            
            # Create and start background thread
            # Pass the queue instead of trying to access session state
            thread = threading.Thread(
                target=process_query_in_background,
                args=(prompt, st.session_state.conversation_history.copy(), st.session_state.processing_queue, user_id, st.session_state.current_conversation_id),
                daemon=True
            )
            thread.start()
            st.session_state.processing_thread = thread
            
            # Show processing indicator
            with st.chat_message("assistant"):
                st.info(f"🔄 **Processing started:** {prompt[:100]}...")
                st.markdown("⏳ Your request is being processed in the background. You can navigate to other pages and come back - the result will appear here when ready!")
                st.rerun()
        else:
            # Already processing, show status
            with st.chat_message("assistant"):
                st.warning("⏳ Another query is already being processed. Please wait for it to complete.")
        
    
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

