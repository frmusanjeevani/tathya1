import streamlit as st
from auth import authenticate_user, is_authenticated, logout_user, check_session_timeout, update_last_activity
from database import init_database, create_account_request
from email_service import send_account_request_notification
import pages.dashboard as dashboard
import pages.case_entry as case_entry
import pages.reviewer_panel as reviewer_panel
import pages.approver_panel as approver_panel
import pages.approver2_panel as approver2_panel
import pages.legal_panel as legal_panel
import pages.closure_panel as closure_panel
import pages.admin_panel as admin_panel
import pages.investigation_panel as investigation_panel
import pages.investigator_panel as investigator_panel
import pages.final_review_panel as final_review_panel

import pages.user_dashboard as user_dashboard
import pages.agency_workflow as agency_workflow
import pages.smart_verification_suite as smart_verification_suite

import pages.login_page as login_page
import pages.tathya_verification_lab as tathya_verification_lab
import pages.regulatory_governance_suite as regulatory_governance_suite
import pages.fraud_risk_parameters as fraud_risk_parameters
import pages.advanced_risk_assessment as advanced_risk_assessment

# Initialize database
init_database()

# Page configuration
st.set_page_config(page_title="Tathya - Case Management System",
                   page_icon="🔎",
                   layout="wide",
                   initial_sidebar_state="collapsed")


# Load custom CSS animations
def load_css():
    with open("static/css/animations.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def show_account_request_form():
    """Display account request form"""
    st.markdown("### 📝 Request Account Access")
    st.markdown(
        "Please fill out this form to request access to the Tathya system.")

    with st.form("account_request_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name *",
                                      placeholder="Enter your full name")
            email = st.text_input("Email Address *",
                                  placeholder="your.email@company.com")
            phone = st.text_input("Phone Number", placeholder="Mobile number")
            organization = st.text_input("Organization",
                                         placeholder="Department/Company")

        with col2:
            designation = st.text_input("Designation",
                                        placeholder="Your job title")
            requested_role = st.selectbox("Requested Role *", [
                "Initiator", "Reviewer", "Investigator", "Approver",
                "Legal Reviewer", "Actioner"
            ])
            manager_name = st.text_input("Reporting Manager",
                                         placeholder="Manager's name")
            manager_email = st.text_input(
                "Manager Email", placeholder="manager.email@company.com")

        business_justification = st.text_area(
            "Business Justification *",
            placeholder=
            "Please explain why you need access to this system and how you will use it...",
            height=100)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit_request = st.form_submit_button("📤 Submit Request",
                                                   use_container_width=True)
        with col3:
            cancel_request = st.form_submit_button("❌ Cancel",
                                                   use_container_width=True)

        if submit_request:
            if full_name and email and requested_role and business_justification:
                try:
                    # Create request data
                    request_data = {
                        'full_name': full_name,
                        'email': email,
                        'phone': phone,
                        'organization': organization,
                        'designation': designation,
                        'requested_role': requested_role,
                        'business_justification': business_justification,
                        'manager_name': manager_name,
                        'manager_email': manager_email
                    }

                    # Save to database
                    request_id = create_account_request(request_data)

                    # Send email notification
                    email_sent = send_account_request_notification(
                        request_data)

                    st.success("✅ Account request submitted successfully!")
                    if email_sent:
                        st.info("📧 Administrator has been notified via email")
                    else:
                        st.warning(
                            "⚠️ Request saved but email notification failed. Administrator will review it in the system."
                        )

                    st.info(
                        "🕐 Your request will be reviewed by the administrator. You will be contacted via email once processed."
                    )

                    # Clear the form
                    st.session_state.show_account_request = False
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error submitting request: {str(e)}")
            else:
                st.error("❌ Please fill in all required fields (*)")

        if cancel_request:
            st.session_state.show_account_request = False
            st.rerun()


def show_login():
    """Display login form"""
    load_css()

    # Check if account request form should be shown
    if st.session_state.get('show_account_request', False):
        show_account_request_form()
        return

    # Header with branding, system switcher, and ABCL logo
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    with header_col1:
        st.markdown("""
            <div style="margin-bottom: 5px;">
            <h3 style="color: #77787B; font-weight: 600;">
                AI-Powered Fraud Risk Intelligence Suite
            </h3>
        </div>
        """,
                    unsafe_allow_html=True)

    with header_col2:
        st.markdown("")  # Empty space

    with header_col3:
        try:
            st.image("static/images/abcl_logo.jpg", width=150)
        except:
            st.markdown("### 🏢 ABCL")

    # Layout with Tathya logo on left middle and login form on right middle
    col1, col2 = st.columns([1, 1])

    with col1:
        # Tathya logo on left middle
        st.markdown(
            "<div style='margin-top: 10px; display: flex; align-items: center; justify-content: flex-end; height: 250px;'>",
            unsafe_allow_html=True)
        try:
            st.image("static/images/tathya.png", width=300)
        except:
            st.markdown("# 🔎 Tathya")
            st.markdown("### Every Clue Counts")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # System selector above login box - extreme right
        st.markdown(
            "<div style='margin-top: 50px; display: flex; justify-content: flex-end;'>",
            unsafe_allow_html=True)

        # Initialize system selection if not set
        if 'selected_system' not in st.session_state:
            st.session_state.selected_system = "Investigation"

        # Enhanced radio buttons with custom styling positioned on extreme right
        st.markdown("""
        <style>
        /* Custom radio button styling */
        div[data-testid="stRadio"] > div {
            display: flex !important;
            justify-content: flex-end !important;
            gap: 12px !important;
        }
        
        div[data-testid="stRadio"] > div > label {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
            border: 2px solid #e8eaed !important;
            border-radius: 20px !important;
            padding: 8px 16px !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
            position: relative !important;
            overflow: hidden !important;
            min-width: 100px !important;
            text-align: center !important;
            font-size: 12px !important;
        }
        
        div[data-testid="stRadio"] > div > label:hover {
            transform: translateY(-1px) scale(1.05) !important;
            border-color: #4285f4 !important;
            box-shadow: 0 4px 16px rgba(66,133,244,0.2) !important;
            background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%) !important;
        }
        
        div[data-testid="stRadio"] > div > label[data-checked="true"] {
            background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%) !important;
            color: white !important;
            border-color: #1a73e8 !important;
            transform: scale(1.05) !important;
            box-shadow: 0 6px 20px rgba(66,133,244,0.3) !important;
        }
        
        div[data-testid="stRadio"] > div > label[data-checked="true"]:hover {
            transform: scale(1.08) translateY(-1px) !important;
        }
        </style>
        """,
                    unsafe_allow_html=True)

        system_choice = st.radio(
            "System",
            [
                "Investigation",
                "Tathya Lab",
                "Internal Fraud Management"
            ],
            index=0 if st.session_state.selected_system == "Investigation" else
            1 if st.session_state.selected_system == "Tathya Lab" else 
            2 if st.session_state.selected_system == "Internal Fraud Management" else 0,
            key="system_selector",
            horizontal=True,
            label_visibility="collapsed")

        # Update session state when selection changes
        if system_choice != st.session_state.selected_system:
            st.session_state.selected_system = system_choice

        st.markdown("</div>", unsafe_allow_html=True)

        # Login form section on right middle
        st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("### UAT Mode")
            username = st.text_input("User ID",
                                     placeholder="Enter your User ID")
            password = st.text_input("Password",
                                     type="password",
                                     placeholder="Enter your password")

            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_b:
                login_button = st.form_submit_button("🎯 Hit",
                                                     use_container_width=True)

            if login_button:
                if username and password:
                    # Authenticate user directly
                    success, message = authenticate_user(username, password)
                    if success:
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please enter both User ID and password")

        # Account request button below login form
        st.markdown("<div style='margin-top: 15px; text-align: center;'>",
                    unsafe_allow_html=True)
        if st.button("📝 Request Account Access",
                     key="request_account_btn",
                     use_container_width=True):
            st.session_state.show_account_request = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Footer branding for login page
    st.markdown("---", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0; margin-top: 5px; color: #414042;">
        <div style="font-style: italic; font-size: 16px;">
             <span style="color: #C7222A; font-weight: italic;">Powered by Fraud Risk Management Unit</span>
        </div>
        <div style="font-size: 14px; opacity: 0.7;">
            © 2025 Aditya Birla Capital Ltd.
        </div>
    </div>
    """,
                unsafe_allow_html=True)


def show_role_selector():
    """Show role selector below ABCL logo, right-aligned"""
    if st.session_state.get("all_roles_access", False):
        # Initialize role selector visibility
        if "show_role_selector" not in st.session_state:
            st.session_state.show_role_selector = False

        # Role selector positioned extreme right below ABCL logo, same size as logo
        role_col1, role_col2 = st.columns([3.5, 1])
        with role_col2:
            # Custom CSS for extreme right positioning and wider box
            st.markdown("""
            <style>
            .role-selector-container {
                margin-top: -20px;
                padding: -10;
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                width: 50%;
            }
            </style>
            """,
                        unsafe_allow_html=True)

            # Role selector button and panel with container class
            st.markdown('<div class="role-selector-container">',
                        unsafe_allow_html=True)

            # Role button with full width
            if st.button("🧑‍💼 Role",
                         help="Switch Role",
                         key="role_toggle",
                         use_container_width=True):
                st.session_state.show_role_selector = not st.session_state.show_role_selector
                st.rerun()

            # Show role selector panel if enabled with full width
            if st.session_state.get("show_role_selector", False):
                available_roles = [
                    "Initiator", "Reviewer", "Approver", "Legal Reviewer",
                    "Actioner", "Investigator"
                ]
                if st.session_state.get("user_role") == "Admin":
                    available_roles.append("Admin")

                current_role = st.session_state.get("role", "")
                current_index = 0
                if current_role in available_roles:
                    current_index = available_roles.index(current_role)

                selected_role = st.selectbox("Active Role:",
                                             available_roles,
                                             index=current_index,
                                             key="role_selector")

                if st.button("Apply",
                             key="role_apply",
                             use_container_width=True):
                    st.session_state.role = selected_role
                    st.session_state.show_role_selector = False
                    st.success(f"✅ Switched to {selected_role}")
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


def show_sidebar(role):
    """Display sidebar navigation based on user role"""
    # Session timeout disabled - persistent sessions until manual logout

    load_css()

    with st.sidebar:
        # User info header with right-aligned text and left-aligned navigation buttons
        st.markdown("""
        <style>
        .user-info {
            text-align: left;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .user-info h3 {
            text-align: left;
            margin-bottom: 10px;
            color: #495057;
        }
        .user-info p {
            text-align: left;
            margin: 5px 0;
            font-size: 14px;
        }
        
        /* Left-align navigation button text in sidebar */
        .stSidebar .stButton > button {
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 12px !important;
        }
        
        /* Left-align text in expandable sections */
        .stSidebar .stExpander .stButton > button {
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 12px !important;
        }
        
        /* Ensure Analytics and Utility section buttons are left-aligned */
        .stSidebar div[data-testid="stVerticalBlock"] .stButton > button {
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 12px !important;
        }
        </style>
        """,
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div class="user-info">
            <h3>👤 User Information</h3>
            <p><strong>User:</strong> {st.session_state.get('username', 'Unknown')}</p>
            <p><strong>Role:</strong> {role}</p>
            <p><strong>Name:</strong> {st.session_state.get('user_name', 'N/A')}</p>
            <p><strong>Team:</strong> {st.session_state.get('user_team', 'N/A')}</p>
        </div>
        """,
                    unsafe_allow_html=True)

        # Enhanced system switcher button with animations
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[key="switch_to_lab"] {
            background: linear-gradient(135deg, #f8f9fa 0%, #e8eaed 100%) !important;
            color: #3c4043 !important;
            border: 1px solid #dadce0 !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-weight: 500 !important;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stButton"] > button[key="switch_to_lab"]:hover {
            transform: translateX(4px) scale(1.02) !important;
            background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%) !important;
            color: white !important;
            border-color: #1a73e8 !important;
            box-shadow: 0 4px 12px rgba(66,133,244,0.25) !important;
        }
        </style>
        """,
                    unsafe_allow_html=True)

        st.markdown("---")

        if role == "Admin":
            # Initialize session state for expandable panels
            if "case_management_expanded" not in st.session_state:
                st.session_state.case_management_expanded = True
            if "workflow_stages_expanded" not in st.session_state:
                st.session_state.workflow_stages_expanded = True
            if "analytics_management_expanded" not in st.session_state:
                st.session_state.analytics_management_expanded = True

            # Advanced Risk Assessment - Before Case Management
            if st.button("Advanced Risk Assessment",
                         key="admin_advanced_risk_assessment",
                         use_container_width=True):
                st.session_state.current_page = "Advanced Risk Assessment"
                st.rerun()

            # Case Management Section
            with st.expander(
                    "Case Management",
                    expanded=st.session_state.case_management_expanded):
                # Case Management
                if st.button("Case Entry",
                             key="admin_case_entry",
                             use_container_width=True):
                    st.session_state.current_page = "Case Entry"
                    st.rerun()
                if st.button("Case Allocation",
                             key="admin_case_allocation",
                             use_container_width=True):
                    st.session_state.current_page = "Case Allocation"
                    st.rerun()
                if st.button("Case Assignment",
                             key="admin_investigator",
                             use_container_width=True):
                    st.session_state.current_page = "Investigation Panel"
                    st.rerun()
                if st.button("Agency Investigation",
                             key="admin_agency_workflow",
                             use_container_width=True):
                    st.session_state.current_page = "Agency Workflow"
                    st.rerun()
                if st.button("Field Investigation",
                             key="admin_regional_investigation",
                             use_container_width=True):
                    st.session_state.current_page = "Regional Investigation"
                    st.rerun()
                if st.button("Investigation Assessment",
                             key="admin_primary_reviewer",
                             use_container_width=True):
                    st.session_state.current_page = "Reviewer Panel"
                    st.rerun()
                if st.button("Level 1 Approval",
                             key="admin_approver1_panel",
                             use_container_width=True):
                    st.session_state.current_page = "Approver Panel"
                    st.rerun()
                if st.button("Level 2 Approval",
                             key="admin_approver2_panel",
                             use_container_width=True):
                    st.session_state.current_page = "Approver 2 Panel"
                    st.rerun()
                if st.button("Final Adjudication",
                             key="admin_final_reviewer",
                             use_container_width=True):
                    st.session_state.current_page = "Final Review Panel"
                    st.rerun()
                if st.button("Legal Compliance Center",
                             key="admin_legal",
                             use_container_width=True):
                    st.session_state.current_page = "Legal Panel"
                    st.rerun()
                if st.button("Regulatory Reporting",
                             key="admin_regulatory_reporting",
                             use_container_width=True):
                    st.session_state.current_page = "Regulatory Reporting"
                    st.rerun()
                if st.button("Case Closure",
                             key="admin_actioner",
                             use_container_width=True):
                    st.session_state.current_page = "Closure Panel"
                    st.rerun()
                if st.button("Stakeholder Actioner",
                             key="admin_stakeholder_actioner",
                             use_container_width=True):
                    st.session_state.current_page = "Stakeholder Actioner"
                    st.rerun()

            # Analytics Section
            st.markdown("**Analytics**")
            if st.button("Workflow Analytics",
                         key="admin_workflow_process",
                         use_container_width=True):
                st.session_state.current_page = "Workflow Dashboard"
                st.rerun()
            if st.button("Executive Dashboard",
                         key="admin_dashboard_analytics",
                         use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()

            # Utility Section
            st.markdown("**Utility**")
            if st.button("Admin Panel",
                         key="admin_panel_main",
                         use_container_width=True):
                st.session_state.current_page = "Admin Panel"
                st.rerun()
            if st.button("Role Management",
                         key="admin_role_management",
                         use_container_width=True):
                # Toggle role selector
                if "show_role_selector" not in st.session_state:
                    st.session_state.show_role_selector = False
                st.session_state.show_role_selector = not st.session_state.show_role_selector
                st.rerun()

            if st.button("Smart Verification Suite",
                         key="admin_smart_verification",
                         use_container_width=True):
                st.session_state.current_page = "Smart Verification Suite"
                st.rerun()

            if st.button("Refined Fraud Risk Parameters by Scope",
                         key="admin_fraud_risk_parameters",
                         use_container_width=True):
                st.session_state.current_page = "Fraud Risk Parameters"
                st.rerun()

            if st.button("Configuration Panel",
                         key="admin_configuration_panel",
                         use_container_width=True):
                st.session_state.current_page = "Configuration Panel"
                st.rerun()

            if st.button("System Design",
                         key="admin_system_design",
                         use_container_width=True):
                st.session_state.current_page = "System Design"
                st.rerun()

            if st.button(" Excel Workflow Analysis",
                         key="admin_excel_download",
                         use_container_width=True):
                st.session_state.current_page = "Excel Download"
                st.rerun()

        elif role == "Initiator":
            if st.button("📊 Executive Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
            if st.button("📝 Case Entry", use_container_width=True):
                st.session_state.current_page = "Case Entry"
                st.rerun()

        elif role == "Investigator":
            if st.button("📊 Executive Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
            if st.button("📝 Case Entry", use_container_width=True):
                st.session_state.current_page = "Case Entry"
                st.rerun()
            if st.button("🎯 Case Allocation", use_container_width=True):
                st.session_state.current_page = "Case Allocation"
                st.rerun()
            if st.button("📋 Case Assignment", use_container_width=True):
                st.session_state.current_page = "Investigator Panel"
                st.rerun()
            if st.button("🔍 Investigation Assessment", use_container_width=True):
                st.session_state.current_page = "Reviewer Panel"
                st.rerun()
            if st.button("Configuration Panel",
                         key="investigator_configuration_panel",
                         use_container_width=True):
                st.session_state.current_page = "Configuration Panel"
                st.rerun()

        elif role == "Reviewer":
            if st.button("📊 Executive Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
            if st.button("🔍 Primary Review Center", use_container_width=True):
                st.session_state.current_page = "Reviewer Panel"
                st.rerun()

        elif role == "Approver":
            if st.button("📊 Executive Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
            if st.button("✅ Approval Authority L1", use_container_width=True):
                st.session_state.current_page = "Approver Panel"
                st.rerun()
            if st.button("✅ Approval Authority L2", use_container_width=True):
                st.session_state.current_page = "Approver 2 Panel"
                st.rerun()

        elif role == "Legal Reviewer":
            if st.button("📊 Executive Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
            if st.button("🧑‍⚖️ Legal Compliance Center",
                         use_container_width=True):
                st.session_state.current_page = "Legal Panel"
                st.rerun()

        elif role == "Actioner":
            if st.button("📊 Executive Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
            if st.button("🎯 Case Resolution Center", use_container_width=True):
                st.session_state.current_page = "Closure Panel"
                st.rerun()

        # Role selector for showing role options when toggled
        if st.session_state.get("show_role_selector", False):
            st.markdown("---")
            st.markdown("**Switch Role (for demonstration):**")
            new_role = st.selectbox("Select Role:", [
                "Admin", "Initiator", "Investigator", "Reviewer", "Approver",
                "Legal Reviewer", "Actioner"
            ],
                                    index=[
                                        "Admin", "Initiator", "Investigator",
                                        "Reviewer", "Approver",
                                        "Legal Reviewer", "Actioner"
                                    ].index(role))
            if new_role != role:
                st.session_state.role = new_role
                st.session_state.show_role_selector = False
                st.rerun()

        # Logout button
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()


def show_main_content():
    """Display main application content based on user role"""
    role = st.session_state.get("role", "")

    # Add page transition effects and professional border styling
    st.markdown("""
    <style>
    .main .block-container {
        animation: fadeInSlide 0.5s ease-out;
        background-color: #FFFFFF !important;
        border: 1px solid rgba(0, 51, 102, 0.12) !important;
        border-radius: 15px !important;
        box-shadow: 0 3px 20px rgba(0, 0, 0, 0.08), 
                    0 1px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
        margin: 15px auto !important;
        padding: 2rem !important;
        backdrop-filter: blur(10px) !important;
        max-width: 95% !important;
    }
    
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    @keyframes fadeInSlide {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """,
                unsafe_allow_html=True)

    # Common header with branding and logos
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])

    with header_col1:
        try:
            st.image("static/images/tathya.png", width=250)
        except:
            # No fallback text to avoid duplication
            st.markdown("")

    with header_col2:
        # Center space - no button here
        st.markdown("")

    with header_col3:
        try:
            st.image("static/images/abcl_logo.jpg", width=250)
        except:
            st.markdown("### 🏢 ABCL")

    # Role selector moved to sidebar Utility section

    # Initialize current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Update last activity
    update_last_activity()

    # Show sidebar
    show_sidebar(role)

    # Display page content based on current page
    current_page = st.session_state.get("current_page", "Dashboard")

    if current_page == "Dashboard":
        user_dashboard.show()
    elif current_page == "Case Entry":
        case_entry.show()
    elif current_page == "Reviewer Panel":
        reviewer_panel.show()
    elif current_page == "Final Review Panel":
        final_review_panel.show()
    elif current_page == "Approver Panel":
        approver_panel.show()
    elif current_page == "Approver 2 Panel":
        approver2_panel.show()
    elif current_page == "Legal Panel":
        legal_panel.show()
    elif current_page == "Closure Panel":
        closure_panel.show()
    elif current_page == "Admin Panel":
        admin_panel.show()
    elif current_page == "Investigation Panel":
        investigation_panel.show()
    elif current_page == "Investigator Panel":
        investigator_panel.show()
    elif current_page == "Case Allocation":
        import pages.case_allocation as case_allocation
        case_allocation.show()

    elif current_page == "Workflow Dashboard":
        import pages.dashboard_workflow as dashboard_workflow
        dashboard_workflow.show()
    elif current_page == "Agency Workflow":
        agency_workflow.show()
    elif current_page == "Regional Investigation":
        import pages.regional_investigation as regional_investigation
        regional_investigation.show()

    elif current_page == "Smart Verification Suite":
        smart_verification_suite.smart_verification_suite()

    elif current_page == "Fraud Risk Parameters":
        fraud_risk_parameters.show()
    elif current_page == "Advanced Risk Assessment":
        advanced_risk_assessment.show()
    elif current_page == "Configuration Panel":
        import pages.tathya_verification_lab as tathya_verification_lab
        tathya_verification_lab.show()
    elif current_page == "Tathya Lab Builder":
        import pages.tathya_lab_builder as tathya_lab_builder
        tathya_lab_builder.show()
    elif current_page == "Tathya Module Gallery":
        import pages.tathya_module_gallery as tathya_module_gallery
        tathya_module_gallery.show()
    elif current_page == "System Design":
        import pages.system_design as system_design
        system_design.show()
    elif current_page == "Excel Download":
        import pages.download_excel_analysis as download_excel_analysis
        download_excel_analysis.show()
    elif current_page == "Regulatory Reporting":
        import pages.regulatory_reporting as regulatory_reporting
        regulatory_reporting.show()
    elif current_page == "Stakeholder Actioner":
        import pages.stakeholder_actioner as stakeholder_actioner
        stakeholder_actioner.show()


def show_skip_options():
    """Show temporary skip options for 3D animation and login"""
    st.markdown("""
    <div style='
        text-align: center;
        margin: 50px auto;
        padding: 30px;
        max-width: 600px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    '>
        <h2 style='color: #2c3e50; margin-bottom: 20px;'>🚀 Temporary Dev Options</h2>
        <p style='color: #34495e; font-size: 16px; margin-bottom: 25px;'>
            Skip intro animations and login for faster development access
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Quick Access Options")
        
        # Quick access to Internal Fraud Management
        if st.button("⚖️ Internal Fraud Management", use_container_width=True, type="primary"):
            # Skip both 3D animation and login, direct to Internal Fraud Management
            st.session_state.show_intro = False
            st.session_state.authenticated = True
            st.session_state.username = "dev_user"
            st.session_state.user_role = "Admin"
            st.session_state.all_roles_access = True
            st.session_state.role = "Admin"
            st.session_state.selected_system = "Internal Fraud Management"
            st.session_state.skip_options_shown = True
            st.rerun()
        
        st.markdown("---")
        
        # Standard flow option
        if st.button("🎯 Standard Flow (3D + Login)", use_container_width=True):
            st.session_state.skip_options_shown = True
            st.rerun()

def main():
    """Main application function"""
    
    # Show skip options first (temporary development feature)
    if not st.session_state.get("skip_options_shown", False):
        show_skip_options()
        return

    # Check if intro animation should be shown
    if "show_intro" not in st.session_state:
        st.session_state.show_intro = True

    # Show intro animation on first load (unless skipped)
    if st.session_state.show_intro and not is_authenticated() and not st.session_state.get("skip_3d", False):
        try:
            import pages.intro_animation as intro_animation
            intro_animation.show()
        except Exception:
            # Fallback to simple CSS animation
            import pages.intro_simple as intro_simple
            intro_simple.show()
        return

    if is_authenticated() or st.session_state.get("skip_login", False):
        # Route based on selected system
        selected_system = st.session_state.get("selected_system",
                                               "Investigation")

        if selected_system == "Regulatory Governance Suite":
            regulatory_governance_suite.show()
        elif selected_system == "Tathya Lab":
            import pages.tathya_lab as tathya_lab
            # Show sidebar navigation for Tathya Lab
            tathya_lab.show_sidebar()
            # Show main content
            tathya_lab.show()
        elif selected_system == "Internal Fraud Management":
            import pages.internal_fraud_management as internal_fraud_management
            internal_fraud_management.show()
        else:
            # Default to Investigation system
            show_main_content()
    else:
        show_login()


if __name__ == "__main__":
    main()
