"""
Login Page for Tathya Case Management System
"""

import streamlit as st
from datetime import datetime
from auth import authenticate_user
from database import get_db_connection

def show_login_page():
    """Display clean login page with minimal white background"""
    
    # Initialize session state
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    
    # Clean white background CSS
    st.markdown("""
    <style>
    /* Clean white background */
    .stApp {
        background-color: white !important;
    }
    .main .block-container {
        background-color: white !important;
        padding-top: 2rem !important;
    }
    /* Hide sidebar completely */
    .css-1d391kg, .stSidebar {
        display: none !important;
    }
    /* Hide main menu and header */
    #MainMenu, header, .stDeployButton {
        visibility: hidden !important;
    }
    /* Remove default margins and padding */
    .element-container {
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Top row: ABCL logo (right)
    col_spacer, col_logo = st.columns([3, 1])
    
    with col_logo:
        try:
            st.image("static/images/abcl_logo.jpg", width=150)
        except:
            st.markdown("**ABCL**")

    # Main content area
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Left middle: Tathya logo | Right middle: Login form
    col1, col2 = st.columns([1, 1])

    with col1:
        # Tathya logo on left middle
        st.markdown("<div style='text-align: center; margin-top: 50px;'>", unsafe_allow_html=True)
        try:
            st.image("static/images/tathya.png", width=300)
        except:
            st.markdown("# Tathya")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Clean login form on right middle
        st.markdown("<div style='margin-top: 80px; max-width: 400px;'>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Login")
            
            user_id = st.text_input("User ID", placeholder="Enter User ID")
            password = st.text_input("Password", type="password", placeholder="Enter Password")
            
            # System selection dropdown
            system_options = [
                "Select System...",
                "Investigation",
                "Tathya Lab"
            ]
            system = st.selectbox("System", system_options)
            
            login_submitted = st.form_submit_button("Login", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Handle login submission
        if login_submitted:
            handle_login_submission(user_id, password, system)
    
    # Bottom right: Powered by text
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col_spacer2, col_powered = st.columns([3, 1])
    with col_powered:
        st.markdown("<div style='text-align: right;'><i>Powered by Fraud Risk Management</i></div>", unsafe_allow_html=True)


def handle_login_submission(user_id, password, system):
    """Handle login form submission"""
    
    # Validate inputs
    if not user_id or not password:
        st.error("Please enter User ID and Password")
        return
    
    if system == "Select System...":
        st.error("Please select a system")
        return
    
    # Check login attempts
    if st.session_state.login_attempts >= 3:
        st.error("Account locked. Contact administrator.")
        return
    
    # Authenticate user
    success, message = authenticate_user(user_id, password)
    
    if success:
        # Reset login attempts on successful login
        st.session_state.login_attempts = 0
        
        # Set session state based on selected system
        st.session_state.authenticated = True
        st.session_state.username = user_id
        st.session_state.system = system
        st.session_state.role = "Admin"  # Default role
        
        # Log successful login
        log_login_attempt(user_id, "Admin", True, f"Login successful - System: {system}")
        
        # No special redirects needed for current systems
        
        st.success("Login successful!")
        st.rerun()
    else:
        # Increment login attempts
        st.session_state.login_attempts += 1
        
        # Log failed login
        log_login_attempt(user_id, "Unknown", False, f"{message} - System: {system}")
        
        remaining = 3 - st.session_state.login_attempts
        if remaining > 0:
            st.error(f"Login failed: {message}. {remaining} attempts remaining.")
        else:
            st.error("Account locked after 3 failed attempts. Contact administrator.")


def log_login_attempt(user_id, role, success, message):
    """Log login attempt to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO login_logs (user_id, role, success, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, role, success, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
    except Exception as e:
        # Silent logging - don't show database errors to user
        pass