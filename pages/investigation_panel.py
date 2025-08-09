import streamlit as st
import pandas as pd
from datetime import datetime, date
from auth import require_role, get_current_user
from models import get_cases_by_status, get_case_by_id, update_case_status, get_case_comments, add_case_comment
from database import get_db_connection, log_audit, get_investigator_names
from utils import generate_case_id, format_datetime
from pages.workflow_progress import show_workflow_progress
from case_display_utils import show_standardized_case_details, show_standardized_customer_info
from case_complexity_analyzer import show_complexity_analyzer_widget
from error_handler import handle_database_error, handle_file_operation_error, handle_validation_error, success_message, handle_unexpected_error
import io

@require_role(["Investigator", "Admin"])
def show():
    """Complete Investigation Panel following proper workflow sequence"""
    
    # Standardized Investigation Intelligence Header
    st.markdown("""
    <div style='
        text-align: center;
        margin: 15px 0 25px 0;
        padding: 10px;
    '>
        <h1 style='
            font-size: 2.4rem;
            font-weight: 600;
            color: inherit;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
            font-family: "Segoe UI", Arial, sans-serif;
        '>🕵️‍♂️ Tathya Investigation Intelligence</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Sub-header for this specific page
    st.markdown("""
    <div style='
        text-align: left;
        margin: 10px 0 20px 0;
        padding: 15px;
        border-radius: 10px;
        background: #f5f5f5;
        border-left: 4px solid #3498db;
        margin-bottom: 15px;
    '>
        <h3 style='
            margin: 0;
            color: #2c3e50;
            font-size: 1.5rem;
            font-weight: 500;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Case Allocation</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Allocate cases to investigation teams and process detailed information</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced styling for professional appearance
    st.markdown("""
    <style>
    .investigation-container {
        background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.08);
        border: 1px solid rgba(0, 102, 204, 0.1);
    }
    .section-header {
        color: #0066cc;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e9ecef;
    }
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .pending-badge {
        background: linear-gradient(135deg, #ffc107 0%, #ffb300 100%);
        color: #212529;
    }
    .active-badge {
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        color: white;
    }
    .completed-badge {
        background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
        color: white;
    }
    .case-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    .case-card:hover {
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.1);
        transform: translateY(-2px);
    }
    .workflow-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #f8f9ff 100%);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #0066cc;
    }
    
    /* Enhanced text visibility styles with clean design */
    .stTextInput > div > div > input {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: #f5f5f5 !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
    }
    
    .stTextArea > div > div > textarea {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: #f5f5f5 !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
    }
    
    .stTextInput label, .stTextArea label {
        color: #333333 !important;
        font-weight: 700 !important;
        font-size: 20px !important;
        margin-bottom: 8px !important;
    }
    
    /* Enhanced text display */
    .stText {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Enhanced captions */
    .stCaption {
        color: #666666 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    
    /* Enhanced markdown text */
    .stMarkdown p {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Enhanced headers - increased size */
    .stMarkdown h3 {
        color: #333333 !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Enhanced expander titles */
    .streamlit-expanderHeader {
        color: #333333 !important;
        font-weight: 700 !important;
        font-size: 18px !important;
    }
    
    /* Clean button styling with hover effects */
    .stButton > button {
        font-weight: 600 !important;
        font-size: 16px !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        border-color: #2c3e50 !important;
    }
    
    /* Clean download button styling with hover effects */
    .stDownloadButton > button {
        font-weight: 600 !important;
        font-size: 14px !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.12) !important;
    }
    
    /* Hover effects for expanders */
    .streamlit-expanderHeader:hover {
        background-color: #f8f9fa !important;
        transition: background-color 0.3s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Single consolidated section
    show_case_allocation()

def show_investigation_case_table(cases, current_user):
    """Show clean case cards for investigation with immediate allocation actions"""
    
    if not cases:
        st.info("📝 No cases available for investigation")
        return
    
    # Helper function to safely get values from sqlite3.Row objects
    def safe_get(case, key):
        try:
            # Handle sqlite3.Row objects
            if hasattr(case, 'keys') and hasattr(case, '__getitem__'):
                # This is a sqlite3.Row object
                return case[key] if key in case.keys() else 'N/A'
            elif hasattr(case, 'keys'):
                # This is a dict
                return case.get(key, 'N/A')
            else:
                # This is an object with attributes
                return getattr(case, key, 'N/A')
        except (KeyError, AttributeError, TypeError):
            return 'N/A'
    
    st.markdown("### 📋 Cases Available for Allocation")
    st.markdown("*Click on any case to view details and allocation options*")
    
    # Show each case in a clean card format with immediate allocation
    for i, case in enumerate(cases):
        case_id = safe_get(case, 'case_id')
        customer_name = safe_get(case, 'customer_name')
        case_type = safe_get(case, 'case_type')
        product = safe_get(case, 'product')
        loan_amount = safe_get(case, 'loan_amount') or 0
        status = safe_get(case, 'status')
        region = safe_get(case, 'region')
        branch = safe_get(case, 'branch_location')
        
        # Convert loan amount to float for formatting
        try:
            loan_amount_float = float(loan_amount) if loan_amount else 0
            formatted_loan = f"₹{loan_amount_float:,.2f}" if loan_amount_float > 0 else 'N/A'
        except (ValueError, TypeError):
            formatted_loan = 'N/A'
        
        # Case card with expandable details
        with st.container():
            st.markdown(f"""
            <div class="case-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #0066cc;">📋 {case_id}</h4>
                    <span class="status-badge pending-badge">{status}</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div><strong>Customer:</strong> {customer_name}</div>
                    <div><strong>Type:</strong> {case_type}</div>
                    <div><strong>Product:</strong> {product}</div>
                    <div><strong>Amount:</strong> {formatted_loan}</div>
                    <div><strong>Region:</strong> {region}</div>
                    <div><strong>Branch:</strong> {branch}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Expandable section for case details and allocation
            with st.expander(f"🎯 **Allocate Case {case_id}**", expanded=False):
                
                # Quick case details tabs
                detail_tabs = st.tabs(["📄 Case Info", "👤 Customer Details", "💬 History"])
                
                with detail_tabs[0]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Case ID:** {case_id}")
                        st.markdown(f"**Case Type:** {case_type}")
                        st.markdown(f"**Product:** {product}")
                        st.markdown(f"**Status:** {status}")
                    with col2:
                        st.markdown(f"**Loan Amount:** {formatted_loan}")
                        st.markdown(f"**Region:** {region}")
                        st.markdown(f"**Branch:** {branch}")
                        case_date = safe_get(case, 'case_date')
                        st.markdown(f"**Date:** {case_date}")
                
                with detail_tabs[1]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Name:** {customer_name}")
                        mobile = safe_get(case, 'mobile_number')
                        st.markdown(f"**Mobile:** {mobile}")
                        email = safe_get(case, 'email_id')
                        st.markdown(f"**Email:** {email}")
                    with col2:
                        pan = safe_get(case, 'pan')
                        st.markdown(f"**PAN:** {pan}")
                        dob = safe_get(case, 'date_of_birth')
                        st.markdown(f"**DOB:** {dob}")
                        disbursement_date = safe_get(case, 'disbursement_date')
                        st.markdown(f"**Disbursement:** {disbursement_date}")
                
                with detail_tabs[2]:
                    # Show case history
                    from case_display_utils import show_standardized_case_history
                    show_standardized_case_history(case_id)
                
                st.divider()
                
                # RISK SCORE ANALYSIS - Comprehensive risk assessment
                st.markdown("### 🔬 Risk Score Analysis")
                show_complexity_analyzer_widget(case, case_id)
                
                st.divider()
                
                # IMMEDIATE ALLOCATION ACTIONS - Right after case details
                show_case_allocation_actions(case, current_user)

def show_case_allocation_actions(case_details, current_user):
    """Show allocation actions immediately after case details"""
    
    # Safe extraction of case_id for allocation form  
    def safe_get(case, key):
        try:
            if hasattr(case, 'keys') and hasattr(case, '__getitem__'):
                return case[key] if key in case.keys() else 'N/A'
            elif hasattr(case, 'get'):
                return case.get(key, 'N/A')
            else:
                return getattr(case, key, 'N/A')
        except (KeyError, AttributeError, TypeError):
            return 'N/A'
    
    case_id = safe_get(case_details, 'case_id')
    
    st.markdown("### 🎯 Allocation Actions")
    st.markdown("*Choose allocation action for this case*")
    
    with st.form(f"allocation_form_{case_id}"):
        
        # 🔬 Automated Risk Assessment
        st.markdown("### 🔬 Automated Risk Assessment")
        st.markdown("*Click 'Analyze Case Complexity' above to generate automated risk score*")
        
        # Display risk score if analysis was run
        if f"risk_analysis_{case_id}" in st.session_state:
            analysis = st.session_state[f"risk_analysis_{case_id}"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Score", f"{analysis['complexity_score']}/100")
            with col2:
                st.metric("Risk Level", analysis['risk_level'])
            with col3:
                st.metric("Risk Factors", len(analysis['risk_factors']))
        
        st.divider()
        
        # 🕵️ Investigation Details (Editable)
        st.markdown("### 🕵️ Investigation Details")
        
        col1, col2 = st.columns(2)
        with col1:
            case_risk = st.selectbox("Risk Level", 
                ["Low", "Medium", "High", "Critical"], 
                key=f"risk_level_{case_id}")
            
            priority_level = st.selectbox("Priority Level", 
                ["Low", "Medium", "High", "Urgent"], 
                key=f"priority_{case_id}")
        
        with col2:
            risk_factors = st.multiselect("Risk Factors",
                ["Document Inconsistencies", "Income Mismatch", "Identity Issues", 
                 "Reference Problems", "Collateral Concerns", "Previous Defaults", "Other"],
                key=f"risk_factors_{case_id}")
            
            red_flags = st.multiselect("🚩 Red Flags",
                ["Forged Documents", "False Identity", "Income Inflation", "Multiple Applications",
                 "Suspicious References", "Address Discrepancies", "Employment Issues", "Other"],
                key=f"red_flags_{case_id}")
        
        # 📝 Case Description (Editable)
        st.markdown("### 📝 Case Description")
        current_description = safe_get(case_details, 'case_description') or ""
        updated_case_description = st.text_area("Case Description (Editable)", 
            value=current_description,
            placeholder="Edit or enhance the case description...",
            height=120, key=f"case_desc_{case_id}")
        
        # Preliminary Observations
        preliminary_observations = st.text_area("🔍 Preliminary Observations", 
            placeholder="Initial observations and findings about the case...",
            height=100, key=f"preliminary_obs_{case_id}")
        
        st.divider()
        
        # 🔒 Case Closure Options Section (Immediately after Investigation Details)
        st.markdown("### 🔒 Case Closure Options")
        st.markdown("*Select action for this case*")
        
        # Main dropdown for Case Action type
        case_action_type = st.selectbox("Select Action Type", 
            ["Select Action...", "Case close at Current stage", "Case Assignment"],
            key=f"case_action_{case_id}")
        
        # Initialize variables
        fraud_selected = False
        non_fraud_selected = False
        final_fraud_reason = ""
        fraud_tags = []
        closure_reason = ""
        case_action_comments = ""
        case_action_documents = None
        
        # Variables for assignment
        regional_selected = False
        agency_selected = False
        region_selection = ""
        investigator_name = ""
        investigator_email = ""
        assignment_instructions = ""
        agency_name = ""
        assignment_reason = ""
        expected_tat = ""
        agency_email = ""
        assignment_documents = None
        
        if case_action_type == "Case close at Current stage":
            st.markdown("**Case Closure Options:**")
            
            closure_type = st.radio("Classification", ["Fraud", "Non-Fraud"], key=f"closure_type_{case_id}")
            
            if closure_type == "Fraud":
                fraud_selected = True
                
                # Required fields for Fraud
                st.markdown("**Required Fields for Fraud Case:**")
                
                fraud_reasons = [
                    "Select Fraud Reason...",
                    "Document Forgery", "Identity Theft", "False Information",
                    "Collusion with Agent", "Multiple Applications", "Income Misrepresentation",
                    "Employment Fabrication", "Address Falsification", "Reference Manipulation",
                    "Bank Statement Tampering", "Other"
                ]
                final_fraud_reason = st.selectbox("Final Fraud Reason", fraud_reasons, key=f"fraud_reason_{case_id}")
                
                fraud_tag_options = [
                    "High Risk Customer", "Document Suspicious", "Verification Failed",
                    "Inconsistent Information", "Duplicate Application", "Fraudulent Intent",
                    "External Collusion", "System Abuse", "Policy Violation"
                ]
                fraud_tags = st.multiselect("Fraud Tags", fraud_tag_options, key=f"fraud_tags_{case_id}")
                
                case_action_comments = st.text_area("Comments/Remarks", 
                    placeholder="Detailed remarks about the fraud case...",
                    height=100, key=f"fraud_comments_{case_id}")
                
                case_action_documents = st.file_uploader("Document Upload", 
                    accept_multiple_files=True,
                    type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'],
                    key=f"fraud_docs_{case_id}")
                
            elif closure_type == "Non-Fraud":
                non_fraud_selected = True
                
                # Required fields for Non-Fraud
                st.markdown("**Required Fields for Non-Fraud Case:**")
                
                closure_reasons = [
                    "Select Closure Reason...",
                    "Insufficient Evidence", "Customer Verified", "Documentation Complete",
                    "No Risk Identified", "Policy Compliant", "Standard Processing",
                    "Low Risk Profile", "Resolved Satisfactorily", "Other"
                ]
                closure_reason = st.selectbox("Closure Reason", closure_reasons, key=f"closure_reason_{case_id}")
                
                case_action_comments = st.text_area("Reviewer Remarks", 
                    placeholder="Remarks for non-fraud closure...",
                    height=100, key=f"non_fraud_comments_{case_id}")
                
                case_action_documents = st.file_uploader("Document Upload", 
                    accept_multiple_files=True,
                    type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'],
                    key=f"non_fraud_docs_{case_id}")
        
        elif case_action_type == "Case Assignment":
            st.markdown("**Case Assignment Options:**")
            
            # Multi-selection for assignment types
            assignment_types = st.multiselect("Select Assignment Type(s)", 
                ["Regional Investigation", "Agency Investigation"],
                key=f"assignment_types_{case_id}")
            
            if "Regional Investigation" in assignment_types:
                regional_selected = True
                st.markdown("**📍 Regional Investigation Details:**")
                
                regions = ["Select Region...", "North", "South", "East", "West", "Central", "Northeast"]
                region_selection = st.selectbox("Region", regions, key=f"region_{case_id}")
                
                investigator_name = st.text_input("Investigator Name", 
                    placeholder="Auto-fill or manual entry",
                    key=f"investigator_name_{case_id}")
                
                investigator_email = st.text_input("Investigator Email ID", 
                    placeholder="investigator@company.com",
                    key=f"investigator_email_{case_id}")
                
                assignment_instructions = st.text_area("Instructions", 
                    placeholder="Specific investigation instructions...",
                    height=80, key=f"regional_instructions_{case_id}")
                
                assignment_documents = st.file_uploader("Document Upload", 
                    accept_multiple_files=True,
                    type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'],
                    key=f"regional_docs_{case_id}")
                
            if "Agency Investigation" in assignment_types:
                agency_selected = True
                st.markdown("**🏢 Agency Investigation Details:**")
                
                agencies = [
                    "Select Agency...", "PAMAC", "Astute", "CRIF High Mark",
                    "Experian", "Equifax", "TransUnion CIBIL", "Dun & Bradstreet",
                    "ICRA Management", "CRISIL Limited", "India Ratings",
                    "Brickwork Ratings", "Infomerics Valuation"
                ]
                agency_name = st.selectbox("Agency Name", agencies, key=f"agency_name_{case_id}")
                
                assignment_reason = st.text_area("Assignment Reason", 
                    placeholder="Reason for agency assignment...",
                    height=60, key=f"assignment_reason_{case_id}")
                
                expected_tat = st.text_input("Expected TAT", 
                    placeholder="e.g., 7 days, 2 weeks",
                    key=f"expected_tat_{case_id}")
                
                agency_email = st.text_input("Agency Email ID", 
                    placeholder="agency@domain.com",
                    key=f"agency_email_{case_id}")
                
                assignment_documents = st.file_uploader("Document Upload", 
                    accept_multiple_files=True,
                    type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'],
                    key=f"agency_docs_{case_id}")
        
        # Submit Case Action
        if st.form_submit_button("💾 Submit Case Action", type="primary"):
            from datetime import datetime
            username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
            
            # Validation
            if case_action_type == "Select Action...":
                st.warning("Please select a case action type")
                return
            
            # Initialize variables
            comment = ""
            success_msg = ""
            
            # Process Case Closure
            if case_action_type == "Case close at Current stage":
                if fraud_selected:
                    # Validate fraud fields
                    if final_fraud_reason == "Select Fraud Reason..." or not case_action_comments.strip():
                        st.warning("Please complete all required fields for fraud case")
                        return
                    
                    # Route to Final Reviewer for fraud cases
                    update_case_status(case_id, "Final Review", username)
                    comment = f"CASE ACTION - FRAUD CASE (ROUTED TO FINAL REVIEWER)\n"
                    comment += f"Risk Level: {case_risk}\n"
                    comment += f"Risk Factors: {', '.join(risk_factors) if risk_factors else 'None'}\n"
                    comment += f"Red Flags: {', '.join(red_flags) if red_flags else 'None'}\n"
                    comment += f"Priority Level: {priority_level}\n"
                    comment += f"Preliminary Observations: {preliminary_observations}\n"
                    comment += f"Fraud Reason: {final_fraud_reason}\n"
                    comment += f"Fraud Tags: {', '.join(fraud_tags) if fraud_tags else 'None'}\n"
                    comment += f"Comments: {case_action_comments}"
                    
                    success_msg = "Fraud case routed to Final Reviewer"
                    
                elif non_fraud_selected:
                    # Validate non-fraud fields
                    if closure_reason == "Select Closure Reason..." or not case_action_comments.strip():
                        st.warning("Please complete all required fields for non-fraud case")
                        return
                    
                    # Close case at current stage for non-fraud
                    update_case_status(case_id, "Closed", username)
                    comment = f"CASE ACTION - NON-FRAUD (CLOSED AT CURRENT STAGE)\n"
                    comment += f"Risk Level: {case_risk}\n"
                    comment += f"Risk Factors: {', '.join(risk_factors) if risk_factors else 'None'}\n"
                    comment += f"Priority Level: {priority_level}\n"
                    comment += f"Preliminary Observations: {preliminary_observations}\n"
                    comment += f"Closure Reason: {closure_reason}\n"
                    comment += f"Comments: {case_action_comments}"
                    
                    success_msg = "Non-fraud case closed at current stage"
                
                # Handle document uploads for closure
                if case_action_documents:
                    upload_status = handle_document_uploads_legacy(case_action_documents, case_id, "Case_Action")
                    if upload_status:
                        comment += f"\nDocuments uploaded: {upload_status}"
            
            # Process Case Assignment
            elif case_action_type == "Case Assignment":
                if not regional_selected and not agency_selected:
                    st.warning("Please select at least one assignment type")
                    return
                
                # Validate assignment fields
                valid_assignment = True
                
                if regional_selected:
                    if (region_selection == "Select Region..." or not investigator_name.strip() or 
                        not investigator_email.strip() or not assignment_instructions.strip()):
                        st.warning("Please complete all required fields for Regional Investigation")
                        valid_assignment = False
                    
                    # Validate email format
                    if investigator_email and "@" not in investigator_email:
                        st.warning("Please enter a valid investigator email address")
                        valid_assignment = False
                
                if agency_selected:
                    if (agency_name == "Select Agency..." or not assignment_reason.strip() or 
                        not expected_tat.strip() or not agency_email.strip()):
                        st.warning("Please complete all required fields for Agency Investigation")
                        valid_assignment = False
                    
                    # Validate email format
                    if agency_email and "@" not in agency_email:
                        st.warning("Please enter a valid agency email address")
                        valid_assignment = False
                
                if not valid_assignment:
                    return
                
                # Update case status based on assignment type
                if regional_selected and not agency_selected:
                    update_case_status(case_id, "Regional Investigation", username)
                elif agency_selected and not regional_selected:
                    update_case_status(case_id, "Agency Investigation", username)
                else:
                    update_case_status(case_id, "Under Investigation", username)
                
                comment = f"CASE ACTION - ASSIGNMENT\n"
                comment += f"Risk Level: {case_risk}\n"
                comment += f"Risk Factors: {', '.join(risk_factors) if risk_factors else 'None'}\n"
                comment += f"Priority Level: {priority_level}\n"
                comment += f"Preliminary Observations: {preliminary_observations}\n"
                
                if regional_selected:
                    comment += f"Regional Investigation:\n"
                    comment += f"- Region: {region_selection}\n"
                    comment += f"- Investigator: {investigator_name} ({investigator_email})\n"
                    comment += f"- Instructions: {assignment_instructions}\n"
                
                if agency_selected:
                    comment += f"Agency Investigation:\n"
                    comment += f"- Agency: {agency_name}\n"
                    comment += f"- Expected TAT: {expected_tat}\n"
                    comment += f"- Agency Email: {agency_email}\n"
                    comment += f"- Assignment Reason: {assignment_reason}\n"
                
                # Handle document uploads for assignment
                if assignment_documents:
                    upload_status = handle_document_uploads_legacy(assignment_documents, case_id, "Case_Assignment")
                    if upload_status:
                        comment += f"\nDocuments uploaded: {upload_status}"
                
                success_msg = f"Case assigned to {', '.join([t for t in ['Regional Investigation' if regional_selected else '', 'Agency Investigation' if agency_selected else ''] if t])}"
            
            # Save review data to database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS case_actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        case_id TEXT NOT NULL,
                        action_type TEXT,
                        fraud_reason TEXT,
                        fraud_tags TEXT,
                        closure_reason TEXT,
                        regional_assignment TEXT,
                        agency_assignment TEXT,
                        comments TEXT,
                        reviewed_by TEXT,
                        action_date TEXT,
                        FOREIGN KEY (case_id) REFERENCES cases (case_id)
                    )
                ''')
                
                cursor.execute('''
                    INSERT INTO case_actions 
                    (case_id, action_type, fraud_reason, fraud_tags, closure_reason, 
                     regional_assignment, agency_assignment, comments, reviewed_by, action_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    case_id, case_action_type, 
                    final_fraud_reason if fraud_selected else None,
                    ', '.join(fraud_tags) if fraud_tags else None,
                    closure_reason if non_fraud_selected else None,
                    f"{region_selection}|{investigator_name}|{investigator_email}" if regional_selected else None,
                    f"{agency_name}|{agency_email}|{expected_tat}" if agency_selected else None,
                    case_action_comments or assignment_instructions or assignment_reason,
                    current_user, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
            
            # Add comment and log audit
            add_case_comment(case_id, comment, current_user, "Case Action")
            log_audit(case_id, f"Case Action - {case_action_type}", f"Case processed by {current_user}", current_user)
            
            st.success(f"✅ {success_msg}!")
            st.rerun()

def handle_document_uploads_legacy(uploaded_files, case_id, folder_type):
    """Handle document uploads and return status message - legacy version"""
    import os
    from datetime import datetime
    
    if not uploaded_files:
        return None
    
    upload_dir = f"uploads/{case_id}/{folder_type}"
    os.makedirs(upload_dir, exist_ok=True)
    
    uploaded_files_list = []
    
    for file in uploaded_files:
        if file is not None:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.name}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            
            uploaded_files_list.append(filename)
    
    return f"{len(uploaded_files_list)} files uploaded to {folder_type}"

def show_case_allocation():
    """Show the main case allocation section with Case Action workflow"""
    st.markdown('<div class="section-header">Case Allocation</div>', unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Get cases for allocation (Submitted status cases)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT case_id, customer_name, case_type, product, region, status, case_date, 
                   loan_amount, branch_location, case_description, referred_by, lan,
                   disbursement_date, customer_dob, customer_pan, customer_aadhaar,
                   customer_mobile, customer_email, customer_occupation, customer_income,
                   customer_cibil_score, customer_relationship_status, customer_address_full,
                   created_by
            FROM cases 
            WHERE status = 'Submitted'
            ORDER BY case_date DESC
        """)
        allocation_cases = cursor.fetchall()
    
    if not allocation_cases:
        st.info("📝 No cases available for allocation")
        return
    
    # Show cases using simple text display
    show_cases_for_allocation(allocation_cases, current_user)

def get_mime_type(file_ext):
    """Get MIME type based on file extension"""
    mime_types = {
        'PDF': 'application/pdf',
        'JPG': 'image/jpeg',
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'DOC': 'application/msword',
        'DOCX': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'XLS': 'application/vnd.ms-excel',
        'XLSX': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'TXT': 'text/plain'
    }
    return mime_types.get(file_ext.upper(), 'application/octet-stream')

def get_case_uploaded_files(case_id):
    """Get uploaded files for a specific case"""
    try:
        import os
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            return []
        
        # Look for files related to this case ID
        case_files = []
        for filename in os.listdir(uploads_dir):
            if case_id in filename:
                file_path = os.path.join(uploads_dir, filename)
                if os.path.isfile(file_path):
                    file_ext = filename.split('.')[-1].upper() if '.' in filename else 'Unknown'
                    case_files.append({
                        'filename': filename,
                        'file_type': file_ext,
                        'file_path': file_path
                    })
        return case_files
    except Exception as e:
        return []

def show_cases_for_allocation(cases, current_user):
    """Display cases available for allocation with clickable Case IDs"""
    
    # Check if there's new case data from registration flow
    if 'new_case_data' in st.session_state:
        show_new_case_allocation_form(st.session_state.new_case_data, current_user)
        st.markdown("---")
    

    
    if not cases:
        st.info("📝 No cases available for allocation")
        return
    
    # Helper function to safely get values from sqlite3.Row objects
    def safe_get(case_obj, key, default='N/A'):
        try:
            if hasattr(case_obj, 'keys') and hasattr(case_obj, '__getitem__'):
                return case_obj[key] if key in case_obj.keys() and case_obj[key] is not None else default
            elif hasattr(case_obj, 'get'):
                return case_obj.get(key, default)
            else:
                return getattr(case_obj, key, default)
        except (KeyError, AttributeError, TypeError):
            return default
    
    # Display cases with simple presentable format
    for i, case in enumerate(cases, 1):
        case_id = safe_get(case, 'case_id')
        customer_name = safe_get(case, 'customer_name')
        case_type = safe_get(case, 'case_type')
        product = safe_get(case, 'product')
        region = safe_get(case, 'region')
        status = safe_get(case, 'status')
        loan_amount = safe_get(case, 'loan_amount', '0')
        branch = safe_get(case, 'branch_location')
        case_date = safe_get(case, 'case_date')
        
        # Format loan amount
        try:
            formatted_amount = f"₹{float(loan_amount):,.2f}" if loan_amount and float(loan_amount) > 0 else 'N/A'
        except (ValueError, TypeError):
            formatted_amount = 'N/A'
        
        # Create expandable section with clickable Case ID
        with st.expander(f"**{case_id}** - {customer_name} ({case_type}) - {formatted_amount}", expanded=False):
            # Display comprehensive case information similar to new case registration flow
            st.markdown("### 📋 Case Information")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.text_input("Case ID", value=case_id, disabled=True, key=f"old_case_id_{case_id}_{i}")
                st.text_input("Customer Name", value=customer_name, disabled=True, key=f"old_customer_name_{case_id}_{i}")
                st.text_input("LAN", value=safe_get(case, 'lan'), disabled=True, key=f"old_lan_{case_id}_{i}")
                st.text_input("Branch Location", value=branch, disabled=True, key=f"old_branch_{case_id}_{i}")
            
            with col2:
                st.text_input("Case Type", value=case_type, disabled=True, key=f"old_case_type_{case_id}_{i}")
                st.text_input("Product", value=product, disabled=True, key=f"old_product_{case_id}_{i}")
                st.text_input("Region", value=region, disabled=True, key=f"old_region_{case_id}_{i}")
                st.text_input("Status", value=status, disabled=True, key=f"old_status_{case_id}_{i}")
            
            with col3:
                st.text_input("Loan Amount", value=formatted_amount, disabled=True, key=f"old_loan_amount_{case_id}_{i}")
                st.text_input("Case Date", value=case_date, disabled=True, key=f"old_case_date_{case_id}_{i}")
                st.text_input("Disbursement Date", value=safe_get(case, 'disbursement_date'), disabled=True, key=f"old_disb_date_{case_id}_{i}")
                st.text_input("Referred By", value=safe_get(case, 'referred_by'), disabled=True, key=f"old_referred_by_{case_id}_{i}")
            
            # Customer Details Section
            with st.expander("👤 Customer Details", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Date of Birth", value=safe_get(case, 'customer_dob'), disabled=True, key=f"old_dob_{case_id}_{i}")
                    st.text_input("PAN Number", value=safe_get(case, 'customer_pan'), disabled=True, key=f"old_pan_{case_id}_{i}")
                    st.text_input("Mobile Number", value=safe_get(case, 'customer_mobile'), disabled=True, key=f"old_mobile_{case_id}_{i}")
                    st.text_input("Occupation", value=safe_get(case, 'customer_occupation'), disabled=True, key=f"old_occupation_{case_id}_{i}")
                    st.text_input("CIBIL Score", value=safe_get(case, 'customer_cibil_score'), disabled=True, key=f"old_cibil_{case_id}_{i}")
                
                with col2:
                    # Mask Aadhaar number for security
                    aadhaar = safe_get(case, 'customer_aadhaar')
                    masked_aadhaar = f"XXXX-XXXX-{aadhaar[-4:]}" if aadhaar and len(str(aadhaar)) >= 4 and aadhaar != 'N/A' else aadhaar
                    st.text_input("Aadhaar Number", value=masked_aadhaar, disabled=True, key=f"old_aadhaar_{case_id}_{i}")
                    st.text_input("Email", value=safe_get(case, 'customer_email'), disabled=True, key=f"old_email_{case_id}_{i}")
                    st.text_input("Income", value=safe_get(case, 'customer_income'), disabled=True, key=f"old_income_{case_id}_{i}")
                    st.text_input("Relationship Status", value=safe_get(case, 'customer_relationship_status'), disabled=True, key=f"old_relationship_{case_id}_{i}")
                
                # Address
                customer_address = safe_get(case, 'customer_address_full')
                if customer_address and customer_address != 'N/A':
                    st.text_area("Full Address", value=customer_address, disabled=True, height=80, key=f"old_address_{case_id}_{i}")
            
            # Case Description
            case_description = safe_get(case, 'case_description')
            if case_description and case_description != 'N/A':
                st.markdown("### 📝 Case Description")
                st.text_area("Description", value=case_description, disabled=True, height=120, key=f"old_description_{case_id}_{i}")
            
            # Check for uploaded documents
            uploaded_files = get_case_uploaded_files(case_id)
            if uploaded_files:
                st.markdown("### 📎 Uploaded Documents")
                with st.container():
                    st.info(f"📊 Total Documents: {len(uploaded_files)} files")
                    
                    for idx, file_info in enumerate(uploaded_files):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"**✅ {file_info.get('filename', 'Document')}**")
                            st.markdown(f"*Type: {file_info.get('file_type', 'Unknown')}*")
                        
                        with col2:
                            # Show file size if available
                            try:
                                import os
                                file_size = os.path.getsize(file_info.get('file_path', ''))
                                size_mb = file_size / (1024 * 1024)
                                st.markdown(f"**{size_mb:.2f} MB**")
                            except:
                                st.markdown("**Size: N/A**")
                        
                        with col3:
                            # Download button for each file
                            try:
                                with open(file_info.get('file_path', ''), 'rb') as file:
                                    file_data = file.read()
                                    st.download_button(
                                        label="📥 Download",
                                        data=file_data,
                                        file_name=file_info.get('filename', 'document'),
                                        mime=get_mime_type(file_info.get('file_type', '')),
                                        key=f"download_{case_id}_{idx}_{i}"
                                    )
                            except Exception as e:
                                st.markdown("*Download unavailable*")
                        
                        if idx < len(uploaded_files) - 1:
                            st.markdown("---")
            
            # Submission Information
            st.markdown("### 📋 Submission Details")
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Submitted By", value=safe_get(case, 'created_by'), disabled=True, key=f"old_submitted_by_{case_id}_{i}")
            
            with col2:
                st.text_input("Current Status", value=status, disabled=True, key=f"old_current_status_{case_id}_{i}")
            
            st.markdown("---")
            

            

            
            # Get case history/comments
            case_comments = get_case_comments_for_display(case_id)
            if case_comments:
                st.markdown("**💬 Case History:**")
                for comment in case_comments[:3]:  # Show last 3 comments
                    st.text(f"• {comment}")
            
            st.markdown("---")
            
            # Allocation action buttons
            st.markdown("**🎯 Case Allocation Actions:**")
            col_act1, col_act2, col_act3 = st.columns(3)
            
            with col_act1:
                if st.button("🔄 Regional Investigation", key=f"regional_{case_id}_{i}"):
                    st.session_state.selected_allocation_case = case_id
                    st.session_state.allocation_type = "Regional Investigation"
                    st.rerun()
            
            with col_act2:
                if st.button("🏢 Agency Investigation", key=f"agency_{case_id}_{i}"):
                    st.session_state.selected_allocation_case = case_id
                    st.session_state.allocation_type = "Agency Investigation"
                    st.rerun()
            
            with col_act3:
                if st.button("✅ Close Case", key=f"close_{case_id}_{i}"):
                    st.session_state.selected_allocation_case = case_id
                    st.session_state.allocation_type = "Case Closure"
                    st.rerun()
            
            # Handle allocation actions immediately after this case
            if ('selected_allocation_case' in st.session_state and 
                'allocation_type' in st.session_state and 
                st.session_state.selected_allocation_case == case_id):
                st.markdown("---")
                show_allocation_action_form(st.session_state.selected_allocation_case, st.session_state.allocation_type, current_user)

def show_new_case_allocation_form(case_data, current_user):
    """Display auto-populated case allocation form for newly registered cases"""
    
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    '>
        <h3 style='margin: 0; color: white;'>🔄 Log New Case ➝ Case Allocation</h3>
        <p style='margin: 5px 0 0 0; opacity: 0.9;'>Auto-populated from case registration submission</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display case information in organized layout
    st.markdown("### 📋 Case Information (Auto-filled)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.text_input("Case ID", value=case_data.get('case_id', ''), disabled=True, key="alloc_case_id")
        st.text_input("Customer Name", value=case_data.get('customer_name', ''), disabled=True, key="alloc_customer_name")
        st.text_input("LAN", value=case_data.get('lan', ''), disabled=True, key="alloc_lan")
        st.text_input("Branch Location", value=case_data.get('branch_location', ''), disabled=True, key="alloc_branch")
    
    with col2:
        st.text_input("Case Type", value=case_data.get('case_type', ''), disabled=True, key="alloc_case_type")
        st.text_input("Product", value=case_data.get('product', ''), disabled=True, key="alloc_product")
        st.text_input("Region", value=case_data.get('region', ''), disabled=True, key="alloc_region")
        st.text_input("Category", value=case_data.get('category', ''), disabled=True, key="alloc_category")
    
    with col3:
        loan_amount = case_data.get('loan_amount', 0)
        formatted_amount = f"₹{float(loan_amount):,.2f}" if loan_amount and float(loan_amount) > 0 else 'N/A'
        st.text_input("Loan Amount", value=formatted_amount, disabled=True, key="alloc_loan_amount")
        st.text_input("Case Date", value=case_data.get('case_date', ''), disabled=True, key="alloc_case_date")
        st.text_input("Disbursement Date", value=case_data.get('disbursement_date', ''), disabled=True, key="alloc_disb_date")
        st.text_input("Referred By", value=case_data.get('referred_by', ''), disabled=True, key="alloc_referred_by")
    
    # Customer Details Section
    with st.expander("👤 Customer Details (Auto-filled)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Date of Birth", value=case_data.get('customer_dob', ''), disabled=True, key="alloc_dob")
            st.text_input("PAN Number", value=case_data.get('customer_pan', ''), disabled=True, key="alloc_pan")
            st.text_input("Mobile Number", value=case_data.get('customer_mobile', ''), disabled=True, key="alloc_mobile")
            st.text_input("Occupation", value=case_data.get('customer_occupation', ''), disabled=True, key="alloc_occupation")
            st.text_input("CIBIL Score", value=case_data.get('customer_cibil_score', ''), disabled=True, key="alloc_cibil")
        
        with col2:
            # Mask Aadhaar number for security
            aadhaar = case_data.get('customer_aadhaar', '')
            masked_aadhaar = f"XXXX-XXXX-{aadhaar[-4:]}" if aadhaar and len(aadhaar) >= 4 else aadhaar
            st.text_input("Aadhaar Number", value=masked_aadhaar, disabled=True, key="alloc_aadhaar")
            st.text_input("Email", value=case_data.get('customer_email', ''), disabled=True, key="alloc_email")
            st.text_input("Income", value=case_data.get('customer_income', ''), disabled=True, key="alloc_income")
            st.text_input("Relationship Status", value=case_data.get('customer_relationship_status', ''), disabled=True, key="alloc_relationship")
        
        # Address
        st.text_area("Full Address", value=case_data.get('customer_address_full', ''), disabled=True, height=80, key="alloc_address")
    
    # Case Description
    st.markdown("### 📝 Case Description")
    st.text_area("Description", value=case_data.get('case_description', ''), disabled=True, height=120, key="alloc_description")
    
    # Document Information
    uploaded_docs = case_data.get('uploaded_documents', {})
    if any(uploaded_docs.values()):
        with st.expander("📎 Uploaded Documents", expanded=False):
            doc_count = 0
            doc_index = 0
            
            # PAN Card Image
            if uploaded_docs.get('pan_image'):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown("**✅ PAN Card Image**")
                    st.markdown("*Type: Image Document*")
                with col2:
                    try:
                        size_mb = len(uploaded_docs['pan_image'].getvalue()) / (1024 * 1024)
                        st.markdown(f"**{size_mb:.2f} MB**")
                    except:
                        st.markdown("**Size: N/A**")
                with col3:
                    st.download_button(
                        label="📥 Download",
                        data=uploaded_docs['pan_image'].getvalue(),
                        file_name="PAN_Card.jpg",
                        mime="image/jpeg",
                        key=f"new_pan_{case_data['case_id']}_{doc_index}"
                    )
                doc_count += 1
                doc_index += 1
                st.markdown("---")
            
            # Aadhaar Card Image
            if uploaded_docs.get('aadhaar_image'):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown("**✅ Aadhaar Card Image**")
                    st.markdown("*Type: Image Document*")
                with col2:
                    try:
                        size_mb = len(uploaded_docs['aadhaar_image'].getvalue()) / (1024 * 1024)
                        st.markdown(f"**{size_mb:.2f} MB**")
                    except:
                        st.markdown("**Size: N/A**")
                with col3:
                    st.download_button(
                        label="📥 Download",
                        data=uploaded_docs['aadhaar_image'].getvalue(),
                        file_name="Aadhaar_Card.jpg",
                        mime="image/jpeg",
                        key=f"new_aadhaar_{case_data['case_id']}_{doc_index}"
                    )
                doc_count += 1
                doc_index += 1
                st.markdown("---")
            
            # Customer Photo
            if uploaded_docs.get('customer_photo'):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown("**✅ Customer Photo**")
                    st.markdown("*Type: Image Document*")
                with col2:
                    try:
                        size_mb = len(uploaded_docs['customer_photo'].getvalue()) / (1024 * 1024)
                        st.markdown(f"**{size_mb:.2f} MB**")
                    except:
                        st.markdown("**Size: N/A**")
                with col3:
                    st.download_button(
                        label="📥 Download",
                        data=uploaded_docs['customer_photo'].getvalue(),
                        file_name="Customer_Photo.jpg",
                        mime="image/jpeg",
                        key=f"new_photo_{case_data['case_id']}_{doc_index}"
                    )
                doc_count += 1
                doc_index += 1
                st.markdown("---")
            
            # Bulk Identity Documents
            if uploaded_docs.get('bulk_identity_docs'):
                for idx, doc in enumerate(uploaded_docs['bulk_identity_docs']):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.text(f"✅ Identity Document {idx + 1}")
                        st.caption(f"Name: {doc.name}")
                    with col2:
                        try:
                            size_mb = len(doc.getvalue()) / (1024 * 1024)
                            st.caption(f"{size_mb:.2f} MB")
                        except:
                            st.caption("Size: N/A")
                    with col3:
                        st.download_button(
                            label="📥 Download",
                            data=doc.getvalue(),
                            file_name=doc.name,
                            mime=get_mime_type(doc.name.split('.')[-1] if '.' in doc.name else ''),
                            key=f"new_bulk_id_{case_data['case_id']}_{doc_index}"
                        )
                    doc_count += 1
                    doc_index += 1
                    if idx < len(uploaded_docs['bulk_identity_docs']) - 1:
                        st.markdown("---")
            
            # Bulk Supporting Documents
            if uploaded_docs.get('bulk_supporting_docs'):
                for idx, doc in enumerate(uploaded_docs['bulk_supporting_docs']):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.text(f"✅ Supporting Document {idx + 1}")
                        st.caption(f"Name: {doc.name}")
                    with col2:
                        try:
                            size_mb = len(doc.getvalue()) / (1024 * 1024)
                            st.caption(f"{size_mb:.2f} MB")
                        except:
                            st.caption("Size: N/A")
                    with col3:
                        st.download_button(
                            label="📥 Download",
                            data=doc.getvalue(),
                            file_name=doc.name,
                            mime=get_mime_type(doc.name.split('.')[-1] if '.' in doc.name else ''),
                            key=f"new_bulk_supp_{case_data['case_id']}_{doc_index}"
                        )
                    doc_count += 1
                    doc_index += 1
                    if idx < len(uploaded_docs['bulk_supporting_docs']) - 1:
                        st.markdown("---")
            
            # Additional Files
            if uploaded_docs.get('uploaded_files'):
                for idx, doc in enumerate(uploaded_docs['uploaded_files']):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.text(f"✅ Additional File {idx + 1}")
                        st.caption(f"Name: {doc.name}")
                    with col2:
                        try:
                            size_mb = len(doc.getvalue()) / (1024 * 1024)
                            st.caption(f"{size_mb:.2f} MB")
                        except:
                            st.caption("Size: N/A")
                    with col3:
                        st.download_button(
                            label="📥 Download",
                            data=doc.getvalue(),
                            file_name=doc.name,
                            mime=get_mime_type(doc.name.split('.')[-1] if '.' in doc.name else ''),
                            key=f"new_additional_{case_data['case_id']}_{doc_index}"
                        )
                    doc_count += 1
                    doc_index += 1
                    if idx < len(uploaded_docs['uploaded_files']) - 1:
                        st.markdown("---")
            
            st.info(f"📊 Total Documents: {doc_count} files")
    
    # Face Verification Result
    face_verification = case_data.get('face_verification_result')
    if face_verification:
        with st.expander("🔍 Identity Verification Status", expanded=False):
            if face_verification.get('verification_status') == 'VERIFIED':
                st.success(f"✅ Face verification passed ({face_verification.get('match_percentage', 0)}% match)")
            else:
                st.warning(f"⚠️ Face verification requires review ({face_verification.get('match_percentage', 0)}% match)")
    
    # Submission Information
    st.markdown("### 📋 Submission Details")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Submitted By", value=case_data.get('submitted_by', ''), disabled=True, key="alloc_submitted_by")
    
    with col2:
        st.text_input("Submission Time", value=case_data.get('submission_timestamp', ''), disabled=True, key="alloc_timestamp")
    
    st.markdown("---")
    
    # Case Allocation Actions (Preserve existing functionality)
    st.markdown("### 🎯 Case Allocation Actions")
    st.markdown("*Allocate this newly registered case for investigation or closure*")
    
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        if st.button("🔄 Regional Investigation Assignment", key=f"new_regional_{case_data['case_id']}", type="primary"):
            st.session_state.selected_allocation_case = case_data['case_id']
            st.session_state.allocation_type = "Regional Investigation"
            st.rerun()
    
    with col_act2:
        if st.button("🏢 Agency Field Investigation Assignment", key=f"new_agency_{case_data['case_id']}", type="primary"):
            st.session_state.selected_allocation_case = case_data['case_id']
            st.session_state.allocation_type = "Agency Investigation"
            st.rerun()
    
    with col_act3:
        if st.button("✅ Case Closure Options", key=f"new_close_{case_data['case_id']}", type="primary"):
            st.session_state.selected_allocation_case = case_data['case_id']
            st.session_state.allocation_type = "Case Closure"
            st.rerun()
    
    # Clear case data from session after allocation
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("🔄 Clear Registration Data", key="clear_new_case_data"):
            if 'new_case_data' in st.session_state:
                del st.session_state.new_case_data
            st.success("✅ Registration data cleared")
            st.rerun()

def get_investigation_details_for_case(case_id):
    """Get investigation details for a specific case"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT investigation_type, risk_level, status, findings, recommendations, 
                       investigator_name, created_at
                FROM investigation_details 
                WHERE case_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (case_id,))
            
            investigation = cursor.fetchone()
            
            if investigation:
                def safe_get_inv(obj, key, default='N/A'):
                    try:
                        if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
                            return obj[key] if key in obj.keys() and obj[key] is not None else default
                        elif hasattr(obj, 'get'):
                            return obj.get(key, default)
                        else:
                            return getattr(obj, key, default)
                    except (KeyError, AttributeError, TypeError):
                        return default
                
                return f"""Investigation Type: {safe_get_inv(investigation, 'investigation_type')}
Risk Level: {safe_get_inv(investigation, 'risk_level')}
Status: {safe_get_inv(investigation, 'status')}
Investigator: {safe_get_inv(investigation, 'investigator_name')}
Date: {safe_get_inv(investigation, 'created_at')}

Findings:
{safe_get_inv(investigation, 'findings')}

Recommendations:
{safe_get_inv(investigation, 'recommendations')}"""
            else:
                return None
                
    except Exception as e:
        return f"Error retrieving investigation details: {str(e)}"

def get_investigation_report_for_case(case_id):
    """Get investigation report file for a specific case"""
    try:
        import os
        import glob
        
        # Look for investigation reports in uploads directory
        report_patterns = [
            f"Investigation_Report_{case_id}_*.pdf",
            f"investigation_{case_id}_*.pdf",
            f"{case_id}_investigation_*.pdf"
        ]
        
        for pattern in report_patterns:
            files = glob.glob(os.path.join("uploads", pattern))
            if files:
                # Return the most recent file
                return max(files, key=os.path.getctime)
        
        return None
    except Exception as e:
        return None

def download_investigation_report(case_id, report_path):
    """Provide download functionality for investigation report"""
    try:
        import os
        
        if os.path.exists(report_path):
            with open(report_path, "rb") as file:
                file_data = file.read()
                filename = os.path.basename(report_path)
                
                st.download_button(
                    label=f"📥 Download {filename}",
                    data=file_data,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_{case_id}_{filename}"
                )
        else:
            st.error("Investigation report file not found")
    except Exception as e:
        st.error(f"Error downloading report: {str(e)}")

def get_case_comments_for_display(case_id):
    """Get case comments for display purposes"""
    try:
        comments = get_case_comments(case_id)
        if comments:
            return [f"{comment.get('created_at', 'N/A')} - {comment.get('comment', 'N/A')}" for comment in comments[-3:]]
        return []
    except Exception as e:
        return []

def show_allocation_action_form(case_id, allocation_type, current_user):
    """Show allocation action form based on selected type"""
    st.markdown(f"### 🎯 {allocation_type} for Case {case_id}")
    
    if allocation_type == "Regional Investigation":
        show_regional_investigation_form(case_id, current_user)
    elif allocation_type == "Agency Investigation":
        show_agency_investigation_form(case_id, current_user)
    elif allocation_type == "Case Closure":
        show_case_closure_form(case_id, current_user)

def show_regional_investigation_form(case_id, current_user):
    """Show regional investigation allocation form"""
    with st.form(f"regional_form_{case_id}"):
        st.markdown("**Regional Investigation Assignment**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            region = st.selectbox("Region", [
                "North", "South", "East", "West", "Central", "Northeast"
            ])
            investigator_names = get_investigator_names()
            assigned_to = st.selectbox("Assigned to", investigator_names or ["No investigators available"])
        
        with col2:
            investigation_type = st.selectbox("Investigation Type", [
                "Field Verification", "Document Verification", "Asset Verification", "Comprehensive Investigation"
            ])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        instructions = st.text_area("Investigation Instructions", height=100)
        
        # Document upload
        uploaded_files = st.file_uploader(
            "Upload Reference Documents", 
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'jpeg', 'png', 'docx']
        )
        
        if st.form_submit_button("🔄 Assign Regional Investigation"):
            if all([region, assigned_to, investigation_type, instructions]):
                assign_regional_investigation(case_id, region, assigned_to, investigation_type, priority, instructions, uploaded_files, current_user)
            else:
                st.error("Please fill all required fields")

def show_agency_investigation_form(case_id, current_user):
    """Show agency investigation allocation form"""
    with st.form(f"agency_form_{case_id}"):
        st.markdown("**Agency Field Investigation Assignment**")
        
        # Get vendor list from database
        agency_list = get_vendor_agencies()
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_agency = st.selectbox("Select Agency", agency_list)
            investigation_scope = st.selectbox("Investigation Scope", [
                "Asset Verification", "Address Verification", "Employment Verification", 
                "Business Verification", "Comprehensive Field Investigation"
            ])
        
        with col2:
            expected_tat = st.number_input("Expected TAT (Days)", min_value=1, max_value=30, value=7)
            contact_email = st.text_input("Agency Email", value="SuneelKumar.Vishwakarma@adityabirlacapital.com")
        
        assignment_reason = st.text_area("Assignment Reason", height=80)
        special_instructions = st.text_area("Special Instructions", height=80)
        
        # Document upload
        uploaded_files = st.file_uploader(
            "Upload Case Documents", 
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'jpeg', 'png', 'docx']
        )
        
        if st.form_submit_button("🏢 Assign Agency Investigation"):
            if all([selected_agency, investigation_scope, assignment_reason, contact_email]):
                assign_agency_investigation(case_id, selected_agency, investigation_scope, expected_tat, contact_email, assignment_reason, special_instructions, uploaded_files, current_user)
            else:
                st.error("Please fill all required fields")

def show_case_closure_form(case_id, current_user):
    """Show case closure form"""
    with st.form(f"closure_form_{case_id}"):
        st.markdown("**Case Closure - No Investigation Required**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            closure_reason = st.selectbox("Closure Reason", [
                "No Fraud Detected", "Insufficient Evidence", "Customer Resolution", 
                "Technical Error", "Duplicate Case", "Policy Exception"
            ])
        
        with col2:
            closure_category = st.selectbox("Closure Category", [
                "Administrative Closure", "Technical Closure", "Business Closure"
            ])
        
        closure_remarks = st.text_area("Closure Remarks", height=100)
        
        # Document upload
        uploaded_files = st.file_uploader(
            "Upload Closure Documents", 
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'jpeg', 'png', 'docx']
        )
        
        if st.form_submit_button("✅ Close Case"):
            if all([closure_reason, closure_remarks]):
                close_case_no_investigation(case_id, closure_reason, closure_category, closure_remarks, uploaded_files, current_user)
            else:
                st.error("Please fill closure reason and remarks")

def get_vendor_agencies():
    """Get list of vendor agencies"""
    return [
        "Alpha Investigation Services", "Beta Field Verification", "Gamma Asset Verification",
        "Delta Investigation Agency", "Epsilon Verification Services", "Zeta Field Services",
        "Eta Investigation Solutions", "Theta Verification Agency", "Iota Field Investigation",
        "Kappa Verification Services", "Lambda Investigation Agency", "Mu Field Verification"
    ]

def assign_regional_investigation(case_id, region, assigned_to, investigation_type, priority, instructions, uploaded_files, current_user):
    """Assign case to regional investigation"""
    try:
        # Handle file uploads
        uploaded_file_names = []
        if uploaded_files:
            uploaded_file_names = handle_file_uploads(uploaded_files, case_id, "regional_investigation")
        
        # Add assignment to database
        assignment_details = f"""REGIONAL INVESTIGATION ASSIGNED
        
Region: {region}
Assigned to: {assigned_to}
Investigation Type: {investigation_type}
Priority: {priority}
Instructions: {instructions}
Uploaded Files: {', '.join(uploaded_file_names) if uploaded_file_names else 'None'}
Assigned by: {current_user}"""
        
        if add_case_comment(case_id, assignment_details, current_user, "Regional Investigation Assignment"):
            # Update case status
            if update_case_status(case_id, "Under Investigation", current_user):
                success_message("Assignment Successful", f"Case {case_id} assigned to {assigned_to} for regional investigation")
                # Clear session state
                if 'selected_allocation_case' in st.session_state:
                    del st.session_state.selected_allocation_case
                if 'allocation_type' in st.session_state:
                    del st.session_state.allocation_type
                st.rerun()
    except Exception as e:
        handle_database_error("regional investigation assignment", e)

def assign_agency_investigation(case_id, agency, scope, tat, email, reason, instructions, uploaded_files, current_user):
    """Assign case to agency investigation"""
    try:
        # Handle file uploads
        uploaded_file_names = []
        if uploaded_files:
            uploaded_file_names = handle_file_uploads(uploaded_files, case_id, "agency_investigation")
        
        # Add assignment to database
        assignment_details = f"""AGENCY INVESTIGATION ASSIGNED
        
Agency: {agency}
Investigation Scope: {scope}
Expected TAT: {tat} days
Contact Email: {email}
Assignment Reason: {reason}
Special Instructions: {instructions}
Uploaded Files: {', '.join(uploaded_file_names) if uploaded_file_names else 'None'}
Assigned by: {current_user}"""
        
        if add_case_comment(case_id, assignment_details, current_user, "Agency Investigation Assignment"):
            # Update case status
            if update_case_status(case_id, "Under Investigation", current_user):
                success_message("Assignment Successful", f"Case {case_id} assigned to {agency} for investigation")
                # Clear session state
                if 'selected_allocation_case' in st.session_state:
                    del st.session_state.selected_allocation_case
                if 'allocation_type' in st.session_state:
                    del st.session_state.allocation_type
                st.rerun()
    except Exception as e:
        handle_database_error("agency investigation assignment", e)

def close_case_no_investigation(case_id, reason, category, remarks, uploaded_files, current_user):
    """Close case without investigation"""
    try:
        # Handle file uploads
        uploaded_file_names = []
        if uploaded_files:
            uploaded_file_names = handle_file_uploads(uploaded_files, case_id, "case_closure")
        
        # Add closure details to database
        closure_details = f"""CASE CLOSED - NO INVESTIGATION REQUIRED
        
Closure Reason: {reason}
Closure Category: {category}
Remarks: {remarks}
Uploaded Files: {', '.join(uploaded_file_names) if uploaded_file_names else 'None'}
Closed by: {current_user}"""
        
        if add_case_comment(case_id, closure_details, current_user, "Case Closure"):
            # Update case status
            if update_case_status(case_id, "Closed", current_user):
                success_message("Case Closed", f"Case {case_id} has been closed successfully")
                # Clear session state
                if 'selected_allocation_case' in st.session_state:
                    del st.session_state.selected_allocation_case
                if 'allocation_type' in st.session_state:
                    del st.session_state.allocation_type
                st.rerun()
    except Exception as e:
        handle_database_error("case closure", e)

def handle_file_uploads(uploaded_files, case_id, folder_type):
    """Handle file uploads for case allocation"""
    try:
        import os
        from datetime import datetime
        
        uploaded_file_names = []
        
        # Create directory structure
        base_dir = "uploads"
        case_dir = os.path.join(base_dir, case_id)
        allocation_dir = os.path.join(case_dir, folder_type)
        
        os.makedirs(allocation_dir, exist_ok=True)
        
        for uploaded_file in uploaded_files:
            if uploaded_file is not None:
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = uploaded_file.name.split('.')[-1]
                filename = f"{folder_type}_{timestamp}_{uploaded_file.name}"
                filepath = os.path.join(allocation_dir, filename)
                
                # Save file
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                uploaded_file_names.append(filename)
        
        return uploaded_file_names
    except Exception as e:
        handle_file_operation_error("file upload", e)
        return []
    with st.expander("📎 Supporting Documents", expanded=True):
        if documents:
            st.text("Uploaded Documents:")
            for i, doc in enumerate(documents, 1):
                st.text(f"{i}. {safe_get(doc, 'original_filename')} ({safe_get(doc, 'upload_type', 'Document')})")
                st.text(f"   Uploaded by {safe_get(doc, 'uploaded_by')} on {safe_get(doc, 'uploaded_at')}")
        else:
            st.info("No documents uploaded for this case")
    
    st.markdown("---")

def show_case_action_form_for_case(case_id, current_user):
    """Show the comprehensive Case Action form for a specific case"""
    # Get case details
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        case_details = cursor.fetchone()
    
    if not case_details:
        st.error("Case not found")
        return
    
    # Add CSS for hover and click animations
    st.markdown("""
    <style>
    .stSelectbox > div > div > select:hover {
        transform: scale(1.02);
        transition: transform 0.2s ease;
    }
    .stRadio > div:hover {
        transform: translateX(3px);
        transition: transform 0.2s ease;
    }
    .stTextArea > div > div > textarea:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: box-shadow 0.2s ease;
    }
    .stFileUploader > div:hover {
        background-color: #f0f8ff;
        transition: background-color 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }
    .stButton > button:active {
        transform: translateY(0px);
        transition: transform 0.1s ease;
    }
    .stMultiSelect > div:hover {
        transform: scale(1.01);
        transition: transform 0.2s ease;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧑‍💼 Case Action")
    st.info(f"Taking action for Case ID: {case_id}")
    
    # Main Case Action dropdown
    action_type = st.selectbox(
        "Select Action Type:",
        ["", "Case close at Current stage", "Case Assignment"],
        key=f"action_type_{case_id}"
    )
    
    if action_type == "Case close at Current stage":
        show_case_closure_form(case_id, current_user)
    elif action_type == "Case Assignment":
        show_case_assignment_form(case_id, current_user)

def show_case_closure_form(case_id, current_user):
    """Show case closure form with Fraud/Non-Fraud options"""
    st.markdown("#### 🔒 Case Closure Options")
    
    closure_type = st.radio(
        "Select closure type:",
        ["Fraud", "Non-Fraud"],
        key=f"closure_type_{case_id}"
    )
    
    if closure_type == "Fraud":
        with st.form(f"fraud_closure_{case_id}"):
            st.markdown("##### 🚨 Fraud Case Closure")
            
            # Final fraud reason dropdown
            fraud_reasons = [
                "Identity Theft", "Document Forgery", "Income Misrepresentation", 
                "Employment Fraud", "Collateral Fraud", "First Party Fraud", 
                "Third Party Fraud", "Conspiracy Fraud", "Other"
            ]
            fraud_reason = st.selectbox(
                "Final fraud reason *",
                [""] + fraud_reasons,
                key=f"fraud_reason_{case_id}"
            )
            
            # Fraud tags multi-select
            fraud_tags_options = [
                "High Risk", "Financial Loss", "Criminal Activity", "Systemic Fraud",
                "Repeat Offender", "Multi-Branch Impact", "External Agency Involved",
                "Legal Action Required", "Recovery Possible", "Investigation Complete"
            ]
            fraud_tags = st.multiselect(
                "Fraud tags *",
                fraud_tags_options,
                key=f"fraud_tags_{case_id}"
            )
            
            # Comments/Remarks
            fraud_comments = st.text_area(
                "Comments/Remarks *",
                height=100,
                key=f"fraud_comments_{case_id}"
            )
            
            # Document Upload
            fraud_documents = st.file_uploader(
                "Upload Supporting Documents",
                accept_multiple_files=True,
                type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'],
                key=f"fraud_docs_{case_id}"
            )
            
            # Submit button
            if st.form_submit_button("🎯 Route to Final Reviewer"):
                if fraud_reason and fraud_tags and fraud_comments:
                    # Process fraud case routing
                    process_fraud_case_routing(case_id, fraud_reason, fraud_tags, fraud_comments, fraud_documents, current_user)
                    st.success("✅ Case routed to Final Reviewer successfully!")
                    st.session_state[f'show_action_form_{case_id}'] = False
                    st.rerun()
                else:
                    st.error("Please fill all required fields marked with *")
    
    elif closure_type == "Non-Fraud":
        with st.form(f"non_fraud_closure_{case_id}"):
            st.markdown("##### ✅ Non-Fraud Case Closure")
            
            # Closure reason dropdown
            closure_reasons = [
                "Insufficient Evidence", "Customer Cooperation", "Technical Error",
                "Process Issue", "Data Quality Issue", "Resolved Satisfactorily",
                "Outside Scope", "Duplicate Case", "Other"
            ]
            closure_reason = st.selectbox(
                "Closure reason *",
                [""] + closure_reasons,
                key=f"closure_reason_{case_id}"
            )
            
            # Reviewer remarks
            reviewer_remarks = st.text_area(
                "Reviewer remarks *",
                height=100,
                key=f"reviewer_remarks_{case_id}"
            )
            
            # Document Upload
            closure_documents = st.file_uploader(
                "Upload Supporting Documents",
                accept_multiple_files=True,
                type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'],
                key=f"closure_docs_{case_id}"
            )
            
            # Submit button
            if st.form_submit_button("🔒 Close Case at Current Stage"):
                if closure_reason and reviewer_remarks:
                    # Process non-fraud case closure
                    process_non_fraud_case_closure(case_id, closure_reason, reviewer_remarks, closure_documents, current_user)
                    st.success("✅ Case closed at current stage successfully!")
                    st.session_state[f'show_action_form_{case_id}'] = False
                    st.rerun()
                else:
                    st.error("Please fill all required fields marked with *")

def show_case_assignment_form(case_id, current_user):
    """Show case assignment form with Regional/Agency options"""
    st.markdown("#### 📤 Case Assignment Options")
    
    # Multi-selection for assignment types
    assignment_types = st.multiselect(
        "Select assignment type(s):",
        ["Regional Investigation", "Agency Investigation"],
        key=f"assignment_types_{case_id}"
    )
    
    with st.form(f"assignment_form_{case_id}"):
        assignment_data = {}
        
        if "Regional Investigation" in assignment_types:
            st.markdown("##### 🌍 Regional Investigation Assignment")
            
            # Region dropdown
            regions = [
                "North Region", "South Region", "East Region", "West Region",
                "Central Region", "Northeast Region", "Mumbai Region", 
                "Delhi NCR Region", "Bangalore Region", "Chennai Region"
            ]
            region = st.selectbox(
                "Region *",
                [""] + regions,
                key=f"region_{case_id}"
            )
            
            # Investigator name
            investigator_name = st.text_input(
                "Investigator name *",
                key=f"investigator_name_{case_id}"
            )
            
            # Investigator Email with validation
            investigator_email = st.text_input(
                "Investigator Email ID *",
                placeholder="investigator@domain.com",
                key=f"investigator_email_{case_id}"
            )
            
            # Instructions
            instructions = st.text_area(
                "Instructions *",
                height=80,
                key=f"instructions_{case_id}"
            )
            
            # Document Upload for Regional
            regional_documents = st.file_uploader(
                "Upload Documents for Regional Team",
                accept_multiple_files=True,
                type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'],
                key=f"regional_docs_{case_id}"
            )
            
            assignment_data['regional'] = {
                'region': region,
                'investigator_name': investigator_name,
                'investigator_email': investigator_email,
                'instructions': instructions,
                'documents': regional_documents
            }
        
        if "Agency Investigation" in assignment_types:
            st.markdown("##### 🏢 Agency Investigation Assignment")
            
            # Agency name dropdown
            agencies = ["PAMAC", "Astute", "Detectives Inc", "Investigative Services Ltd", "Field Experts", "Regional Detectives"]
            agency_name = st.selectbox(
                "Agency name *",
                [""] + agencies,
                key=f"agency_name_{case_id}"
            )
            
            # Assignment reason
            assignment_reason = st.text_input(
                "Assignment reason *",
                key=f"assignment_reason_{case_id}"
            )
            
            # Expected TAT
            expected_tat = st.selectbox(
                "Expected TAT *",
                ["", "7 days", "15 days", "30 days", "45 days", "60 days", "90 days"],
                key=f"expected_tat_{case_id}"
            )
            
            # Agency Email with validation
            agency_email = st.text_input(
                "Agency Email ID *",
                placeholder="agency@domain.com",
                key=f"agency_email_{case_id}"
            )
            
            # Document Upload for Agency
            agency_documents = st.file_uploader(
                "Upload Documents for Agency",
                accept_multiple_files=True,
                type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'],
                key=f"agency_docs_{case_id}"
            )
            
            assignment_data['agency'] = {
                'agency_name': agency_name,
                'assignment_reason': assignment_reason,
                'expected_tat': expected_tat,
                'agency_email': agency_email,
                'documents': agency_documents
            }
        
        # Submit button
        if st.form_submit_button("📤 Assign Case"):
            if assignment_types:
                # Validate email formats
                email_valid = True
                if 'regional' in assignment_data and assignment_data['regional']['investigator_email']:
                    if '@' not in assignment_data['regional']['investigator_email'] or '.com' not in assignment_data['regional']['investigator_email']:
                        st.error("Invalid investigator email format. Must contain @domain.com")
                        email_valid = False
                
                if 'agency' in assignment_data and assignment_data['agency']['agency_email']:
                    if '@' not in assignment_data['agency']['agency_email'] or '.com' not in assignment_data['agency']['agency_email']:
                        st.error("Invalid agency email format. Must contain @domain.com")
                        email_valid = False
                
                if email_valid and validate_assignment_data(assignment_data, assignment_types):
                    # Process case assignment
                    process_case_assignment(case_id, assignment_data, assignment_types, current_user)
                    st.success("✅ Case assigned successfully!")
                    st.session_state[f'show_action_form_{case_id}'] = False
                    st.rerun()
                else:
                    if email_valid:
                        st.error("Please fill all required fields marked with *")
            else:
                st.error("Please select at least one assignment type")

def validate_assignment_data(assignment_data, assignment_types):
    """Validate assignment form data"""
    if "Regional Investigation" in assignment_types:
        regional = assignment_data.get('regional', {})
        if not all([regional.get('region'), regional.get('investigator_name'), 
                   regional.get('investigator_email'), regional.get('instructions')]):
            return False
    
    if "Agency Investigation" in assignment_types:
        agency = assignment_data.get('agency', {})
        if not all([agency.get('agency_name'), agency.get('assignment_reason'), 
                   agency.get('expected_tat'), agency.get('agency_email')]):
            return False
    
    return True

def process_fraud_case_routing(case_id, fraud_reason, fraud_tags, fraud_comments, fraud_documents, current_user):
    """Process fraud case routing to Final Reviewer"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update case status to route to Final Reviewer
        cursor.execute("""
            UPDATE cases 
            SET status = 'Final Review', 
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE case_id = ?
        """, (current_user, case_id))
        
        # Add case action record
        cursor.execute("""
            INSERT INTO case_actions (case_id, action_type, action_details, created_by, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (case_id, 'Fraud Closure', f"Reason: {fraud_reason}, Tags: {', '.join(fraud_tags)}, Comments: {fraud_comments}", current_user))
        
        # Handle document uploads
        if fraud_documents:
            handle_document_uploads(case_id, fraud_documents, "fraud_closure", current_user)
        
        conn.commit()

def process_non_fraud_case_closure(case_id, closure_reason, reviewer_remarks, closure_documents, current_user):
    """Process non-fraud case closure at current stage"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update case status to Closed
        cursor.execute("""
            UPDATE cases 
            SET status = 'Closed', 
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE case_id = ?
        """, (current_user, case_id))
        
        # Add case action record
        cursor.execute("""
            INSERT INTO case_actions (case_id, action_type, action_details, created_by, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (case_id, 'Non-Fraud Closure', f"Reason: {closure_reason}, Remarks: {reviewer_remarks}", current_user))
        
        # Handle document uploads
        if closure_documents:
            handle_document_uploads(case_id, closure_documents, "non_fraud_closure", current_user)
        
        conn.commit()

def process_case_assignment(case_id, assignment_data, assignment_types, current_user):
    """Process case assignment to Regional/Agency Investigation"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update case status to Under Investigation
        cursor.execute("""
            UPDATE cases 
            SET status = 'Under Investigation', 
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE case_id = ?
        """, (current_user, case_id))
        
        # Create assignment records
        try:
            for assignment_type in assignment_types:
                if assignment_type == "Regional Investigation" and 'regional' in assignment_data:
                    regional = assignment_data['regional']
                    cursor.execute("""
                        INSERT INTO case_assignments (case_id, assignment_type, assignment_details, assigned_to, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (case_id, 'Regional Investigation', 
                         f"Region: {regional['region']}, Investigator: {regional['investigator_name']}, Email: {regional['investigator_email']}, Instructions: {regional['instructions']}", 
                         regional['investigator_email'], current_user))
                    # Handle regional documents
                    if regional['documents']:
                        handle_document_uploads(case_id, regional['documents'], "regional_assignment", current_user)
                
                elif assignment_type == "Agency Investigation" and 'agency' in assignment_data:
                    agency = assignment_data['agency']
                    cursor.execute("""
                        INSERT INTO case_assignments (case_id, assignment_type, assignment_details, assigned_to, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (case_id, 'Agency Investigation', 
                         f"Agency: {agency['agency_name']}, Reason: {agency['assignment_reason']}, TAT: {agency['expected_tat']}, Email: {agency['agency_email']}", 
                         agency['agency_email'], current_user))
                    
                    # Handle agency documents
                    if agency['documents']:
                        handle_document_uploads(case_id, agency['documents'], "agency_assignment", current_user)
        except Exception as e:
            handle_database_error("case assignment creation", e)
            return
        
        conn.commit()

def handle_document_uploads(case_id, documents, upload_type, current_user):
    """Handle document uploads with organized directory structure"""
    import os
    import uuid
    
    upload_dir = f"uploads/{case_id}/{upload_type}"
    os.makedirs(upload_dir, exist_ok=True)
    
    for document in documents:
        if document is not None:
            # Generate unique filename
            file_extension = document.name.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(document.getbuffer())
            
            # Record in database with error handling
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO case_documents (case_id, original_filename, stored_filename, file_path, upload_type, uploaded_by, uploaded_at)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (case_id, document.name, unique_filename, file_path, upload_type, current_user))
                    conn.commit()
            except Exception as e:
                st.error("⚠️ Backend Error - Unable to save document record")
