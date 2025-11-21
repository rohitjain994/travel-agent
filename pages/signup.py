"""Signup page for travel agent application."""
import streamlit as st
import time
from auth import AuthManager


def show_signup_page():
    """Display signup page."""
    auth = AuthManager()
    
    # Redirect if already logged in
    if auth.is_authenticated():
        st.success("You are already logged in!")
        if st.button("Go to Main App"):
            st.switch_page("app.py")
        return
    
    st.set_page_config(
        page_title="Sign Up - Travel Agent",
        page_icon="✈️",
        layout="centered"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .signup-container {
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
    st.markdown('<div class="signup-container">', unsafe_allow_html=True)
    st.markdown("# ✈️ Travel Agent")
    st.markdown("### Create a new account")
    st.markdown("---")
    
    # Signup form
    with st.form("signup_form"):
        full_name = st.text_input("Full Name (Optional)", placeholder="Enter your full name")
        username = st.text_input("Username *", placeholder="Choose a username (min 3 chars)")
        email = st.text_input("Email *", placeholder="Enter your email address")
        password = st.text_input("Password *", type="password", placeholder="Choose a password (min 6 chars)")
        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button("📝 Sign Up", use_container_width=True)
        with col2:
            if st.form_submit_button("🔐 Login", use_container_width=True):
                st.switch_page("pages/login.py")
        
        if submit_button:
            # Validation
            if not username or not email or not password:
                st.error("Please fill in all required fields (*)")
            elif len(username) < 3:
                st.error("Username must be at least 3 characters")
            elif "@" not in email:
                st.error("Please enter a valid email address")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                result = auth.signup(username, email, password, full_name)
                if result["success"]:
                    st.success(result["message"])
                    st.info("Redirecting to main app...")
                    st.rerun()
                else:
                    st.error(result["message"])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Terms and conditions
    st.markdown("---")
    st.caption("By signing up, you agree to our Terms of Service and Privacy Policy")


if __name__ == "__main__":
    show_signup_page()

