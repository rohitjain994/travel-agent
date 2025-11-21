"""Login page for travel agent application."""
import streamlit as st
from auth import AuthManager


def show_login_page():
    """Display login page."""
    auth = AuthManager()
    
    # Redirect if already logged in
    if auth.is_authenticated():
        st.success("You are already logged in!")
        if st.button("Go to Main App"):
            st.switch_page("app.py")
        return
    
    st.set_page_config(
        page_title="Login - Travel Agent",
        page_icon="✈️",
        layout="centered"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("# ✈️ Travel Agent")
    st.markdown("### Login to your account")
    st.markdown("---")
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username or Email", placeholder="Enter your username or email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button("🔐 Login", use_container_width=True)
        with col2:
            if st.form_submit_button("📝 Sign Up", use_container_width=True):
                st.switch_page("pages/signup.py")
        
        if submit_button:
            if username and password:
                result = auth.login(username, password)
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])
            else:
                st.warning("Please fill in all fields")
    
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    show_login_page()

