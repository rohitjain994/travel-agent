"""Authentication utilities for the travel agent application."""
from database import Database
from typing import Optional, Dict, Any
import streamlit as st


class AuthManager:
    """Authentication manager for handling user sessions."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.db = Database()
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables."""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user" not in st.session_state:
            st.session_state.user = None
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
    
    def signup(self, username: str, email: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """Register a new user."""
        # Validation
        if not username or len(username) < 3:
            return {"success": False, "message": "Username must be at least 3 characters"}
        
        if not email or "@" not in email:
            return {"success": False, "message": "Please enter a valid email address"}
        
        if not password or len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters"}
        
        # Check if user already exists
        if self.db.user_exists(username=username):
            return {"success": False, "message": "Username already exists"}
        
        if self.db.user_exists(email=email):
            return {"success": False, "message": "Email already exists"}
        
        # Create user
        result = self.db.create_user(username, email, password, full_name)
        
        if result["success"]:
            # Auto-login after signup
            auth_result = self.db.authenticate_user(username, password)
            if auth_result and auth_result.get("success"):
                self._set_session(auth_result)
                return {"success": True, "message": "Account created successfully! You are now logged in."}
        
        return result
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and create session."""
        if not username or not password:
            return {"success": False, "message": "Please enter both username and password"}
        
        result = self.db.authenticate_user(username, password)
        
        if result and result.get("success"):
            self._set_session(result)
            return {"success": True, "message": "Login successful!"}
        elif result and not result.get("success"):
            return result
        else:
            return {"success": False, "message": "Invalid username or password"}
    
    def logout(self):
        """Logout user and clear session."""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_id = None
        # Clear other session state
        if "messages" in st.session_state:
            st.session_state.messages = []
        if "conversation_history" in st.session_state:
            st.session_state.conversation_history = []
    
    def _set_session(self, user_data: Dict[str, Any]):
        """Set user session."""
        st.session_state.authenticated = True
        st.session_state.user = user_data
        st.session_state.user_id = user_data.get("user_id")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return st.session_state.get("authenticated", False)
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user."""
        if self.is_authenticated():
            return st.session_state.get("user")
        return None
    
    def require_auth(self):
        """Decorator/check to require authentication."""
        if not self.is_authenticated():
            st.error("Please login to access this page")
            st.stop()

