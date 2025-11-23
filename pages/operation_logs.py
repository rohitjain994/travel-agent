"""Operation logs page for Travel Buddy."""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from travel_agent.core import AuthManager, logger

st.set_page_config(
    page_title="Operation Logs - Travel Buddy",
    page_icon="📊",
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
st.markdown("# 📊 Operation Logs")
st.markdown("### Real-time monitoring of agent operations and system activities")
st.markdown("---")

# Get logs
logs = logger.get_logs()
summary = logger.get_log_summary()

# Summary metrics
if summary["total"] > 0:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Operations", summary["total"])
    
    with col2:
        success_count = summary["by_status"].get("success", 0)
        st.metric("Successful", success_count, delta=None)
    
    with col3:
        error_count = summary["by_status"].get("error", 0)
        st.metric("Errors", error_count, delta=None)
    
    with col4:
        warning_count = summary["by_status"].get("warning", 0)
        st.metric("Warnings", warning_count, delta=None)
    
    st.markdown("---")
    
    # Filter options
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        filter_agent = st.selectbox(
            "Filter by Agent",
            ["All"] + list(summary["by_agent"].keys())
        )
    
    with filter_col2:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "success", "error", "warning", "info"]
        )
    
    with filter_col3:
        log_limit = st.slider("Number of logs to display", 10, 100, 50)
    
    st.markdown("---")
    
    # Filter logs
    filtered_logs = logs
    if filter_agent != "All":
        filtered_logs = [log for log in filtered_logs if log["agent"] == filter_agent]
    if filter_status != "All":
        filtered_logs = [log for log in filtered_logs if log["status"] == filter_status]
    
    # Display logs
    if filtered_logs:
        st.markdown(f"### Showing {len(filtered_logs[-log_limit:])} log entries")
        
        # Format logs as plain text
        log_text_lines = []
        for log in reversed(filtered_logs[-log_limit:]):  # Newest first
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00'))
                time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = log["timestamp"]
            
            # Build log line
            status_upper = log["status"].upper()
            agent = log["agent"]
            operation = log["operation"]
            
            # Format log entry as plain text
            log_line = f"[{time_str}] [{status_upper}] [{agent}] {operation}"
            
            if log.get("details"):
                log_line += f": {log['details']}"
            
            if log.get("duration"):
                log_line += f" (Duration: {log['duration']:.2f}s)"
            
            log_text_lines.append(log_line)
        
        # Combine all logs into a single text block
        log_text = "\n".join(log_text_lines)
        
        # Display in dropdown with code block
        with st.expander(f"📋 View Log Entries ({len(log_text_lines)} entries)", expanded=False):
            st.code(log_text, language="text")
            
            # Add download button for logs
            st.download_button(
                label="📥 Download Logs as Text",
                data=log_text,
                file_name=f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("No logs match the selected filters.")
    
    # Actions
    st.markdown("---")
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        if st.button("🗑️ Clear All Logs", use_container_width=True):
            logger.clear_logs()
            st.success("Logs cleared!")
            st.rerun()
    
    with action_col2:
        if st.button("🔄 Refresh Logs", use_container_width=True):
            st.rerun()
    
    # Agent statistics
    st.markdown("---")
    st.markdown("### 📈 Agent Statistics")
    
    if summary["by_agent"]:
        stats_cols = st.columns(len(summary["by_agent"]))
        for idx, (agent, count) in enumerate(summary["by_agent"].items()):
            with stats_cols[idx]:
                st.metric(agent, count)
    
else:
    st.info("No operation logs yet. Start a conversation to see agent activities.")
    
    st.markdown("### 📝 What are Operation Logs?")
    st.markdown("""
    Operation logs track all activities performed by Travel Buddy:
    
    - **Agent Operations**: Each agent's execution and results
    - **LLM Calls**: API calls to Gemini with duration and size
    - **State Transitions**: Workflow progression between agents
    - **Errors & Warnings**: System issues and retry attempts
    - **Performance Metrics**: Execution times and durations
    
    All logs are timestamped and categorized for easy monitoring and debugging.
    """)

