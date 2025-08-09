import streamlit as st
import pandas as pd
from datetime import datetime, date
from models_internal_fraud import create_internal_fraud_case, get_internal_fraud_cases, update_internal_fraud_case, get_internal_fraud_case_by_id
from auth import get_current_user, require_role
from utils import generate_case_id, save_uploaded_file
import os

def show():
    """Internal Fraud Management - Workflow-based system with role-specific access"""
    
    # Dark Blue Theme Styling
    st.markdown("""
    <style>
    /* Internal Fraud Management Dark Blue Theme */
    .internal-fraud-header {
        background: #0D3B66;
        color: white !important;
        padding: 25px;
        border-radius: 4px;
        margin-bottom: 30px;
        text-align: center;
        font-family: "Inter", "Roboto", sans-serif;
    }
    
    .internal-fraud-header h1 {
        color: white !important;
        font-weight: bold;
        margin: 0;
        font-size: 2.2rem;
    }
    
    .internal-fraud-header p {
        color: white !important;
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .section-header {
        background: #0D3B66;
        color: white !important;
        padding: 15px 20px;
        border-radius: 4px;
        margin: 25px 0 20px 0;
        font-weight: bold;
        font-family: "Inter", "Roboto", sans-serif;
        font-size: 1.1rem;
    }
    
    .stButton > button {
        background-color: #0D3B66 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        font-family: "Inter", "Roboto", sans-serif !important;
    }
    
    .stButton > button:hover {
        background-color: #09427A !important;
    }
    
    .stButton > button:focus {
        background-color: #09427A !important;
        box-shadow: 0 0 0 2px #09427A !important;
    }
    
    .stSelectbox > div > div, .stTextInput > div > div, .stTextArea > div > div, .stDateInput > div > div {
        background-color: #ffffff !important;
        border-radius: 4px !important;
        border: 1px solid #9e9e9e !important;
    }
    
    .stSelectbox > div > div:focus-within, .stTextInput > div > div:focus-within, 
    .stTextArea > div > div:focus-within, .stDateInput > div > div:focus-within {
        border-color: #09427A !important;
        box-shadow: 0 0 0 2px rgba(9, 66, 122, 0.2) !important;
    }
    
    .stFileUploader > div {
        background-color: #ffffff !important;
        border: 1px solid #9e9e9e !important;
        border-radius: 4px !important;
    }
    
    .stRadio > div {
        background-color: #e3f2fd !important;
        padding: 10px !important;
        border-radius: 4px !important;
    }
    
    /* Typography */
    body, .stApp {
        font-family: "Inter", "Roboto", sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: bold !important;
        color: #424242 !important;
    }
    
    .case-overview-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 4px;
        border: 1px solid #9e9e9e;
        margin: 15px 0;
    }
    
    .mandatory-field {
        color: #d32f2f;
        font-weight: bold;
    }
    
    .stSelectbox > div > div {
        border-color: #1976d2 !important;
    }
    
    .stTextInput > div > div {
        border-color: #1976d2 !important;
    }
    
    .stTextArea > div > div {
        border-color: #1976d2 !important;
    }
    
    .role-badge {
        display: inline-block;
        background: #1976d2;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        margin: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main Header
    st.markdown("""
    <div class="internal-fraud-header">
        <h1>Internal Fraud Management</h1>
        <p>Workflow-based system for capturing, processing, and closing internal and employee fraud cases</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    user_role = st.session_state.get('user_role', 'Initiator')
    
    # Show sidebar navigation for workflow sections
    show_sidebar_navigation()
    
    # Get selected workflow section from session state
    selected_section = st.session_state.get('if_selected_section', 'Case Initiation')
    
    # Route to appropriate workflow section based on selection and role
    if selected_section == "Case Initiation":
        show_case_initiation_workflow()
    elif selected_section == "Case Allocation":
        show_case_allocation_workflow()
    elif selected_section == "Investigation":
        show_investigation_workflow()
    elif selected_section == "Review & Assessment":
        show_review_assessment_workflow()
    elif selected_section == "Approver 1 Decision":
        show_approver1_workflow()
    elif selected_section == "Approver 2 Decision":
        show_approver2_workflow()
    elif selected_section == "Code of Conduct":
        show_code_conduct_workflow()
    elif selected_section == "Closure Process":
        show_closure_workflow()
    elif selected_section == "Analytics":
        show_internal_fraud_analytics()
    else:
        show_case_initiation_workflow()

def show_sidebar_navigation():
    """Show sidebar navigation for workflow sections"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Internal Fraud Workflow")
    
    # Workflow sections with role-based access
    workflow_sections = [
        ("Case Initiation", ["Initiator", "Admin", "All Roles Access"]),
        ("Case Allocation", ["Allocator", "Admin", "All Roles Access"]),
        ("Investigation", ["Investigator", "Admin", "All Roles Access"]),
        ("Review & Assessment", ["Reviewer", "Admin", "All Roles Access"]),
        ("Approver 1 Decision", ["Approver 1", "Admin", "All Roles Access"]),
        ("Approver 2 Decision", ["Approver 2", "Admin", "All Roles Access"]),
        ("Code of Conduct", ["HR", "Legal", "Admin", "All Roles Access"]),
        ("Closure Process", ["Closer", "Admin", "All Roles Access"]),
        ("Analytics", ["Admin", "Viewer", "All Roles Access"])
    ]
    
    user_role = st.session_state.get('user_role', 'Initiator')
    
    for section_name, allowed_roles in workflow_sections:
        if user_role in allowed_roles or user_role == "All Roles Access":
            if st.sidebar.button(f"🔹 {section_name}", key=f"if_nav_{section_name.replace(' ', '_').lower()}"):
                st.session_state.if_selected_section = section_name
                st.rerun()
    
    # Show current selection
    current_section = st.session_state.get('if_selected_section', 'Case Initiation')
    st.sidebar.markdown(f"**Current:** {current_section}")

def show_case_initiation_workflow():
    """Case Initiation workflow section"""
    st.markdown('<div class="section-header">Case Initiation</div>', unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Case selection for existing cases
    cases = get_internal_fraud_cases()
    case_options = ["Create New Case"] + [f"{case.get('case_id')} - {case.get('case_type', 'Unknown')}" for case in cases]
    
    selected_case = st.selectbox("Select Case:", case_options)
    
    if selected_case == "Create New Case":
        show_new_case_initiation_form()
    else:
        case_id = selected_case.split(" - ")[0]
        case_data = get_internal_fraud_case_by_id(case_id)
        if case_data:
            show_edit_case_initiation_form(case_data)

def show_new_case_initiation_form():
    """Form for new case initiation"""
    with st.form("case_initiation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            case_id = generate_case_id()
            st.text_input("Case ID", value=case_id, disabled=True)
            
            case_type = st.selectbox(
                "Type of Case *",
                ["Internal Fraud", "Employee Fraud"]
            )
            
            detection_date = st.date_input(
                "Date of Detection *", 
                value=date.today(),
                max_value=date.today()
            )
        
        with col2:
            reported_by = st.selectbox(
                "Reported By *",
                ["HR", "FRMU", "Other"]
            )
            
            reporting_channel = st.selectbox(
                "Reporting Channel *",
                ["Email", "Phone", "Whistleblower", "Other"]
            )
        
        incident_description = st.text_area(
            "Brief Description of Incident *",
            placeholder="Provide detailed description of the incident...",
            max_chars=1000,
            height=120
        )
        
        supporting_documents = st.file_uploader(
            "Supporting Documents",
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'xlsx']
        )
        
        submitted = st.form_submit_button("Submit Case Initiation", type="primary")
        
        if submitted:
            if not incident_description:
                st.error("Brief Description of Incident is mandatory")
                return
            
            case_data = {
                'case_id': case_id,
                'case_type': case_type,
                'detection_date': detection_date.isoformat(),
                'reported_by': reported_by,
                'reporting_channel': reporting_channel,
                'incident_description': incident_description,
                'created_by': get_current_user(),
                'created_at': datetime.now().isoformat(),
                'status': 'Initiated',
                'current_stage': 'Case Initiation',
                'workflow_stage': 1
            }
            
            # Handle file uploads
            if supporting_documents:
                doc_paths = []
                for doc in supporting_documents:
                    path = save_uploaded_file(doc, case_id)
                    if path:
                        doc_paths.append(path)
                case_data['supporting_documents'] = ','.join(doc_paths)
            
            success = create_internal_fraud_case(case_data)
            if success:
                st.success(f"Case {case_id} initiated successfully!")
                st.rerun()
            else:
                st.error("Failed to create case. Please try again.")

def show_edit_case_initiation_form(case_data):
    """Form for editing existing case initiation"""
    st.info(f"Editing Case: {case_data.get('case_id')}")
    
    with st.form("edit_case_initiation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Case ID", value=case_data.get('case_id'), disabled=True)
            
            case_type = st.selectbox(
                "Type of Case *",
                ["Internal Fraud", "Employee Fraud"],
                index=["Internal Fraud", "Employee Fraud"].index(case_data.get('case_type', 'Internal Fraud'))
            )
            
            detection_date = st.date_input(
                "Date of Detection *", 
                value=datetime.strptime(case_data.get('detection_date'), '%Y-%m-%d').date() if case_data.get('detection_date') else date.today(),
                max_value=date.today()
            )
        
        with col2:
            reported_by = st.selectbox(
                "Reported By *",
                ["HR", "FRMU", "Other"],
                index=["HR", "FRMU", "Other"].index(case_data.get('reported_by', 'HR'))
            )
            
            reporting_channel = st.selectbox(
                "Reporting Channel *",
                ["Email", "Phone", "Whistleblower", "Other"],
                index=["Email", "Phone", "Whistleblower", "Other"].index(case_data.get('reporting_channel', 'Email'))
            )
        
        incident_description = st.text_area(
            "Brief Description of Incident *",
            value=case_data.get('incident_description', ''),
            max_chars=1000,
            height=120
        )
        
        supporting_documents = st.file_uploader(
            "Supporting Documents",
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'xlsx']
        )
        
        submitted = st.form_submit_button("Update Case Initiation", type="primary")
        
        if submitted:
            if not incident_description:
                st.error("Brief Description of Incident is mandatory")
                return
            
            update_data = {
                'case_type': case_type,
                'detection_date': detection_date.isoformat(),
                'reported_by': reported_by,
                'reporting_channel': reporting_channel,
                'incident_description': incident_description,
                'updated_at': datetime.now().isoformat()
            }
            
            # Handle file uploads
            if supporting_documents:
                doc_paths = []
                for doc in supporting_documents:
                    path = save_uploaded_file(doc, case_data.get('case_id'))
                    if path:
                        doc_paths.append(path)
                update_data['supporting_documents'] = ','.join(doc_paths)
            
            success = update_internal_fraud_case(case_data.get('case_id'), update_data)
            if success:
                st.success("Case initiation updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update case. Please try again.")

def show_case_allocation_workflow():
    """Case Allocation workflow section"""
    st.markdown('<div class="section-header">Case Allocation</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    initiated_cases = [case for case in cases if case.get('status') in ['Initiated', 'Allocated']]
    
    if not initiated_cases:
        st.info("No cases available for allocation.")
        return
    
    case_options = [f"{case.get('case_id')} - {case.get('case_type', 'Unknown')}" for case in initiated_cases]
    selected_case = st.selectbox("Select Case for Allocation:", case_options)
    
    if selected_case:
        case_id = selected_case.split(" - ")[0]
        case_data = get_internal_fraud_case_by_id(case_id)
        
        if case_data:
            st.info(f"Case: {case_id} - {case_data.get('incident_description', '')[:100]}...")
            
            with st.form("case_allocation_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    team_options = ["Investigation Team Alpha", "Investigation Team Beta", "HR Investigation Unit", "Legal Investigation Team", "Internal Audit Team", "Special Committee"]
                    current_allocation = case_data.get('allocated_to', '')
                    default_index = 0
                    if current_allocation and current_allocation in team_options:
                        default_index = team_options.index(current_allocation)
                    
                    allocated_to = st.selectbox(
                        "Allocated To *",
                        team_options,
                        index=default_index
                    )
                    
                    allocation_date = st.date_input(
                        "Allocation Date",
                        value=datetime.strptime(case_data.get('allocation_date'), '%Y-%m-%d').date() if case_data.get('allocation_date') else date.today()
                    )
                
                with col2:
                    allocation_remarks = st.text_area(
                        "Allocation Remarks *",
                        value=case_data.get('allocation_remarks', ''),
                        placeholder="Special instructions or notes for the allocated team...",
                        height=100
                    )
                
                submitted = st.form_submit_button("Submit Case Allocation", type="primary")
                
                if submitted:
                    if not allocation_remarks:
                        st.error("Allocation Remarks are mandatory")
                        return
                    
                    update_data = {
                        'allocated_to': allocated_to,
                        'allocation_date': allocation_date.isoformat(),
                        'allocation_remarks': allocation_remarks,
                        'status': 'Allocated',
                        'current_stage': 'Case Allocation',
                        'workflow_stage': 2,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    success = update_internal_fraud_case(case_id, update_data)
                    if success:
                        st.success("Case allocation submitted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update allocation. Please try again.")

def show_investigation_workflow():
    """Investigation workflow section"""
    st.markdown('<div class="section-header">Investigation</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    allocated_cases = [case for case in cases if case.get('status') in ['Allocated', 'Under Investigation']]
    
    if not allocated_cases:
        st.info("No cases available for investigation.")
        return
    
    case_options = [f"{case.get('case_id')} - {case.get('case_type', 'Unknown')}" for case in allocated_cases]
    selected_case = st.selectbox("Select Case for Investigation:", case_options)
    
    if selected_case:
        case_id = selected_case.split(" - ")[0]
        case_data = get_internal_fraud_case_by_id(case_id)
        
        if case_data:
            st.info(f"Allocated to: {case_data.get('allocated_to', 'N/A')}")
            
            with st.form("investigation_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    investigation_start_date = st.date_input(
                        "Investigation Start Date",
                        value=datetime.strptime(case_data.get('investigation_start_date'), '%Y-%m-%d').date() if case_data.get('investigation_start_date') else date.today()
                    )
                    
                    investigation_summary = st.text_area(
                        "Investigation Summary *",
                        value=case_data.get('investigation_summary', ''),
                        placeholder="Detailed summary of investigation findings...",
                        max_chars=2000,
                        height=120
                    )
                
                with col2:
                    evidence_collected = st.file_uploader(
                        "Evidence Collected",
                        accept_multiple_files=True,
                        type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'xlsx']
                    )
                    
                    preliminary_findings = st.text_area(
                        "Preliminary Findings *",
                        value=case_data.get('preliminary_findings', ''),
                        placeholder="Key findings and observations...",
                        max_chars=1000,
                        height=100
                    )
                
                submitted = st.form_submit_button("Submit Investigation", type="primary")
                
                if submitted:
                    if not investigation_summary or not preliminary_findings:
                        st.error("Investigation Summary and Preliminary Findings are mandatory")
                        return
                    
                    update_data = {
                        'investigation_start_date': investigation_start_date.isoformat(),
                        'investigation_summary': investigation_summary,
                        'preliminary_findings': preliminary_findings,
                        'status': 'Under Investigation',
                        'current_stage': 'Investigation',
                        'workflow_stage': 3,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Handle evidence files
                    if evidence_collected:
                        evidence_paths = []
                        for doc in evidence_collected:
                            path = save_uploaded_file(doc, case_id)
                            if path:
                                evidence_paths.append(path)
                        update_data['evidence_collected'] = ','.join(evidence_paths)
                    
                    success = update_internal_fraud_case(case_id, update_data)
                    if success:
                        st.success("Investigation submitted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update investigation. Please try again.")

def show_review_assessment_workflow():
    """Review & Assessment workflow section"""
    st.markdown('<div class="section-header">Review & Assessment</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    investigation_cases = [case for case in cases if case.get('status') in ['Under Investigation', 'Under Review']]
    
    if not investigation_cases:
        st.info("No cases available for review.")
        return
    
    case_options = [f"{case.get('case_id')} - {case.get('case_type', 'Unknown')}" for case in investigation_cases]
    selected_case = st.selectbox("Select Case for Review:", case_options)
    
    if selected_case:
        case_id = selected_case.split(" - ")[0]
        case_data = get_internal_fraud_case_by_id(case_id)
        
        if case_data:
            # Show investigation summary
            st.markdown("### Investigation Summary")
            st.write(case_data.get('investigation_summary', 'No summary available'))
            st.write(f"**Preliminary Findings:** {case_data.get('preliminary_findings', 'No findings available')}")
            
            with st.form("review_assessment_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    final_reviewer = st.selectbox(
                        "Final Reviewer Name",
                        ["", "John Smith - Senior Investigator", "Sarah Johnson - Investigation Manager", "Michael Brown - Legal Advisor", "Lisa Wilson - HR Director", "David Chen - Audit Manager"],
                        index=0 if not case_data.get('final_reviewer') else ["", "John Smith - Senior Investigator", "Sarah Johnson - Investigation Manager", "Michael Brown - Legal Advisor", "Lisa Wilson - HR Director", "David Chen - Audit Manager"].index(case_data.get('final_reviewer', ''))
                    )
                    
                    reviewer_comments = st.text_area(
                        "Reviewer Comments",
                        value=case_data.get('reviewer_comments', ''),
                        placeholder="Detailed review comments and recommendations...",
                        height=120
                    )
                
                with col2:
                    review_recommendation = st.selectbox(
                        "Review Recommendation",
                        ["Proceed to Approval", "Require More Investigation", "Close Case", "Escalate to Legal"]
                    )
                    
                    risk_assessment = st.selectbox(
                        "Risk Assessment",
                        ["High Risk", "Medium Risk", "Low Risk", "No Risk"]
                    )
                
                submitted = st.form_submit_button("Submit Review & Assessment", type="primary")
                
                if submitted:
                    update_data = {
                        'final_reviewer': final_reviewer,
                        'reviewer_comments': reviewer_comments,
                        'status': 'Under Review',
                        'current_stage': 'Review & Assessment',
                        'workflow_stage': 4,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    success = update_internal_fraud_case(case_id, update_data)
                    if success:
                        st.success("Review assessment submitted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update review. Please try again.")

def show_approver1_workflow():
    """Approver 1 Decision workflow section"""
    st.markdown('<div class="section-header">Approver 1 Decision</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    review_cases = [case for case in cases if case.get('status') in ['Under Review', 'Pending Approval']]
    
    if not review_cases:
        st.info("No cases available for Approver 1 decision.")
        return
    
    case_options = [f"{case.get('case_id')} - {case.get('case_type', 'Unknown')}" for case in review_cases]
    selected_case = st.selectbox("Select Case for Approver 1 Decision:", case_options)
    
    if selected_case:
        case_id = selected_case.split(" - ")[0]
        case_data = get_internal_fraud_case_by_id(case_id)
        
        if case_data:
            # Show case summary
            st.markdown("### Case Summary")
            st.write(f"**Reviewer:** {case_data.get('final_reviewer', 'N/A')}")
            st.write(f"**Reviewer Comments:** {case_data.get('reviewer_comments', 'No comments')}")
            
            with st.form("approver1_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    approver1_name = st.selectbox(
                        "Approver 1 Name *",
                        ["", "Robert Taylor - Department Head", "Jennifer Lee - Regional Manager", "Mark Anderson - Compliance Officer", "Amanda Garcia - Senior Manager"],
                        index=0 if not case_data.get('approver1_name') else ["", "Robert Taylor - Department Head", "Jennifer Lee - Regional Manager", "Mark Anderson - Compliance Officer", "Amanda Garcia - Senior Manager"].index(case_data.get('approver1_name', ''))
                    )
                    
                    approver1_decision = st.selectbox(
                        "Approver 1 Decision *",
                        ["Approve", "Reject", "Send Back"],
                        index=0 if not case_data.get('approver1_decision') else ["Approve", "Reject", "Send Back"].index(case_data.get('approver1_decision', 'Approve'))
                    )
                
                with col2:
                    approver1_comments = st.text_area(
                        "Approver 1 Comments",
                        placeholder="Comments and rationale for decision...",
                        height=120
                    )
                    
                    approval_date = st.date_input(
                        "Approval Date",
                        value=date.today()
                    )
                
                submitted = st.form_submit_button("Submit Approver 1 Decision", type="primary")
                
                if submitted:
                    if not approver1_name:
                        st.error("Approver 1 Name is mandatory")
                        return
                    
                    update_data = {
                        'approver1_name': approver1_name,
                        'approver1_decision': approver1_decision,
                        'status': 'Pending Approval' if approver1_decision == 'Approve' else 'Rejected',
                        'current_stage': 'Approver 1 Decision',
                        'workflow_stage': 5,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    success = update_internal_fraud_case(case_id, update_data)
                    if success:
                        st.success("Approver 1 decision submitted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to submit decision. Please try again.")

def show_approver2_workflow():
    """Approver 2 Decision workflow section"""
    st.markdown('<div class="section-header">Approver 2 Decision</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    approval_cases = [case for case in cases if case.get('status') == 'Pending Approval' and case.get('approver1_decision') == 'Approve']
    
    if not approval_cases:
        st.info("No cases available for Approver 2 decision.")
        return
    
    case_options = [f"{case.get('case_id')} - {case.get('case_type', 'Unknown')}" for case in approval_cases]
    selected_case = st.selectbox("Select Case for Approver 2 Decision:", case_options)
    
    if selected_case:
        case_id = selected_case.split(" - ")[0]
        case_data = get_internal_fraud_case_by_id(case_id)
        
        if case_data:
            # Show approver 1 decision
            st.markdown("### Approver 1 Decision")
            st.write(f"**Approver 1:** {case_data.get('approver1_name', 'N/A')}")
            st.write(f"**Decision:** {case_data.get('approver1_decision', 'N/A')}")
            
            with st.form("approver2_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    approver2_name = st.selectbox(
                        "Approver 2 Name *",
                        ["", "Thomas Wilson - VP Operations", "Karen Martinez - Chief Risk Officer", "Steven Davis - General Manager", "Michelle Thompson - Director"],
                        index=0 if not case_data.get('approver2_name') else ["", "Thomas Wilson - VP Operations", "Karen Martinez - Chief Risk Officer", "Steven Davis - General Manager", "Michelle Thompson - Director"].index(case_data.get('approver2_name', ''))
                    )
                    
                    approver2_decision = st.selectbox(
                        "Approver 2 Decision *",
                        ["Approve", "Reject", "Send Back"],
                        index=0 if not case_data.get('approver2_decision') else ["Approve", "Reject", "Send Back"].index(case_data.get('approver2_decision', 'Approve'))
                    )
                
                with col2:
                    approver2_comments = st.text_area(
                        "Approver 2 Comments",
                        placeholder="Comments and rationale for final decision...",
                        height=120
                    )
                    
                    final_approval_date = st.date_input(
                        "Final Approval Date",
                        value=date.today()
                    )
                
                submitted = st.form_submit_button("Submit Approver 2 Decision", type="primary")
                
                if submitted:
                    if not approver2_name:
                        st.error("Approver 2 Name is mandatory")
                        return
                    
                    update_data = {
                        'approver2_name': approver2_name,
                        'approver2_decision': approver2_decision,
                        'status': 'Approved' if approver2_decision == 'Approve' else 'Rejected',
                        'current_stage': 'Approver 2 Decision',
                        'workflow_stage': 6,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    success = update_internal_fraud_case(case_id, update_data)
                    if success:
                        st.success("Approver 2 decision submitted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to submit decision. Please try again.")

def show_code_conduct_workflow():
    """Code of Conduct workflow section"""
    st.markdown('<div class="section-header">Code of Conduct</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    approved_cases = [case for case in cases if case.get('status') == 'Approved']
    
    if not approved_cases:
        st.info("No approved cases available for code of conduct assessment.")
        return
    
    case_options = [f"{case.get('case_id')} - {case.get('case_type', 'Unknown')}" for case in approved_cases]
    selected_case = st.selectbox("Select Case for Code of Conduct Assessment:", case_options)
    
    if selected_case:
        case_id = selected_case.split(" - ")[0]
        case_data = get_internal_fraud_case_by_id(case_id)
        
        if case_data:
            with st.form("code_conduct_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    code_breach = st.radio(
                        "Breach of Code of Conduct *",
                        ["Yes", "No"],
                        index=0 if case_data.get('code_breach') == 'Yes' else 1
                    )
                    
                    if code_breach == "Yes":
                        code_reference = st.text_area(
                            "Code of Conduct Reference Clause *",
                            value=case_data.get('code_reference', ''),
                            placeholder="Specific code section breached",
                            height=100
                        )
                    else:
                        code_reference = ""
                        st.text_area(
                            "Code of Conduct Reference Clause",
                            value="Not applicable",
                            disabled=True,
                            height=100
                        )
                
                with col2:
                    disciplinary_action = st.selectbox(
                        "Recommended Disciplinary Action",
                        ["Warning", "Suspension", "Termination", "Training", "No Action"]
                    )
                    
                    conduct_assessment = st.text_area(
                        "Code of Conduct Assessment",
                        placeholder="Detailed assessment of code violations and recommendations...",
                        height=120
                    )
                
                submitted = st.form_submit_button("Submit Code Assessment", type="primary")
                
                if submitted:
                    if code_breach == "Yes" and not code_reference:
                        st.error("Code of Conduct Reference Clause is mandatory when breach is 'Yes'")
                        return
                    
                    update_data = {
                        'code_breach': code_breach,
                        'code_reference': code_reference,
                        'status': 'Code Assessment Complete',
                        'current_stage': 'Code of Conduct',
                        'workflow_stage': 7,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    success = update_internal_fraud_case(case_id, update_data)
                    if success:
                        st.success("Code of conduct assessment submitted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update assessment. Please try again.")

def show_closure_workflow():
    """Closure Process workflow section"""
    st.markdown('<div class="section-header">Closure Process</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    closure_cases = [case for case in cases if case.get('status') in ['Code Assessment Complete', 'Closure in Progress']]
    
    if not closure_cases:
        st.info("No cases available for closure.")
        return
    
    case_options = [f"{case.get('case_id')} - {case.get('case_type', 'Unknown')}" for case in closure_cases]
    selected_case = st.selectbox("Select Case for Closure:", case_options)
    
    if selected_case:
        case_id = selected_case.split(" - ")[0]
        case_data = get_internal_fraud_case_by_id(case_id)
        
        if case_data:
            # Show code assessment
            st.markdown("### Code Assessment")
            st.write(f"**Code Breach:** {case_data.get('code_breach', 'N/A')}")
            if case_data.get('code_reference'):
                st.write(f"**Reference:** {case_data.get('code_reference')}")
            
            with st.form("closure_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    primary_closure_remarks = st.text_area(
                        "Primary Closure Remarks",
                        value=case_data.get('primary_closure_remarks', ''),
                        placeholder="Summary of actions taken and case resolution...",
                        height=100
                    )
                    
                    hr_action = st.selectbox(
                        "HR Review & Action",
                        ["", "Warning", "Termination", "Suspension", "Other"],
                        index=0 if not case_data.get('hr_action') else ["", "Warning", "Termination", "Suspension", "Other"].index(case_data.get('hr_action', ''))
                    )
                    
                    scn_date = st.date_input(
                        "Employee Show Cause Notice Date",
                        value=datetime.strptime(case_data.get('scn_date'), '%Y-%m-%d').date() if case_data.get('scn_date') else None
                    )
                
                with col2:
                    committee_review = st.text_area(
                        "Committee Review Remarks",
                        value=case_data.get('committee_review', ''),
                        placeholder="Committee review comments and decisions...",
                        height=100
                    )
                    
                    final_closure_date = st.date_input(
                        "Final Closure Date *",
                        value=datetime.strptime(case_data.get('final_closure_date'), '%Y-%m-%d').date() if case_data.get('final_closure_date') else date.today()
                    )
                    
                    final_closure_remarks = st.text_area(
                        "Final Closure Remarks *",
                        value=case_data.get('final_closure_remarks', ''),
                        placeholder="Final remarks and lessons learned...",
                        height=100
                    )
                
                submitted = st.form_submit_button("Submit Case Closure", type="primary")
                
                if submitted:
                    if not final_closure_remarks:
                        st.error("Final Closure Remarks are mandatory")
                        return
                    
                    update_data = {
                        'primary_closure_remarks': primary_closure_remarks,
                        'hr_action': hr_action,
                        'scn_date': scn_date.isoformat() if scn_date else None,
                        'committee_review': committee_review,
                        'final_closure_date': final_closure_date.isoformat(),
                        'final_closure_remarks': final_closure_remarks,
                        'status': 'Closed',
                        'current_stage': 'Closed',
                        'workflow_stage': 8,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    success = update_internal_fraud_case(case_id, update_data)
                    if success:
                        st.success("Case closure submitted successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to close case. Please try again.")

def show_internal_fraud_analytics():
    """Analytics and reports for internal fraud cases"""
    st.markdown('<div class="section-header">Internal Fraud Analytics & Reports</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    
    if not cases:
        st.info("No data available for analytics.")
        return
    
    # Create analytics dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        # Case Type Distribution
        case_types = {}
        for case in cases:
            case_type = case.get('case_type', 'Unknown')
            case_types[case_type] = case_types.get(case_type, 0) + 1
        
        if case_types:
            st.subheader("Case Type Distribution")
            import pandas as pd
            df_types = pd.DataFrame(list(case_types.items()))
            df_types.columns = ['Type', 'Count']
            df_types = df_types.set_index('Type')
            st.bar_chart(df_types)
    
    with col2:
        # Status Distribution
        statuses = {}
        for case in cases:
            status = case.get('status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        if statuses:
            st.subheader("Status Distribution")
            import pandas as pd
            df_status = pd.DataFrame(list(statuses.items()))
            df_status.columns = ['Status', 'Count']
            df_status = df_status.set_index('Status')
            st.bar_chart(df_status)
    
    # Workflow Stage Analysis
    st.subheader("Workflow Stage Analysis")
    stage_counts = {}
    stage_names = {
        1: "Case Initiation",
        2: "Case Allocation",
        3: "Investigation",
        4: "Review & Assessment",
        5: "Approver 1 Decision",
        6: "Approver 2 Decision",
        7: "Code of Conduct",
        8: "Closure Process"
    }
    
    for case in cases:
        stage = stage_names.get(case.get('workflow_stage', 1), 'Unknown')
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    if stage_counts:
        import pandas as pd
        df_stages = pd.DataFrame(list(stage_counts.items()))
        df_stages.columns = ['Stage', 'Count']
        df_stages = df_stages.set_index('Stage')
        st.bar_chart(df_stages)
    
    # HR Actions Summary
    st.subheader("HR Actions Summary")
    hr_actions = {}
    for case in cases:
        action = case.get('hr_action', 'Pending')
        if action and action != "":
            hr_actions[action] = hr_actions.get(action, 0) + 1
    
    if hr_actions:
        import pandas as pd
        df_hr = pd.DataFrame(list(hr_actions.items()))
        df_hr.columns = ['HR Action', 'Count']
        st.dataframe(df_hr, use_container_width=True)
    else:
        st.info("No HR actions recorded yet.")
    
    # Cases Summary Table
    st.subheader("Cases Summary")
    if cases:
        import pandas as pd
        df_summary = pd.DataFrame(cases)
        # Select key columns for display
        display_columns = ['case_id', 'case_type', 'status', 'current_stage', 'reported_by', 'allocated_to', 'detection_date']
        available_columns = [col for col in display_columns if col in df_summary.columns]
        if available_columns:
            st.dataframe(df_summary[available_columns], use_container_width=True)
    
    # Export functionality
    st.markdown("---")
    if st.button("Export Cases Report", type="primary"):
        import pandas as pd
        df_export = pd.DataFrame(cases)
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="Download CSV Report",
            data=csv,
            file_name=f"internal_fraud_cases_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_internal_fraud_analytics():
    """Analytics and reports for internal fraud cases"""
    st.markdown('<div class="section-header">Internal Fraud Analytics & Reports</div>', unsafe_allow_html=True)
    
    cases = get_internal_fraud_cases()
    
    if not cases:
        st.info("📊 No data available for analytics.")
        return
    
    # Create analytics dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        # Case Type Distribution
        case_types = {}
        for case in cases:
            case_type = case.get('case_type', 'Unknown')
            case_types[case_type] = case_types.get(case_type, 0) + 1
        
        if case_types:
            st.subheader("📊 Case Type Distribution")
            import pandas as pd
            df_types = pd.DataFrame(list(case_types.items()))
            df_types.columns = ['Type', 'Count']
            df_types = df_types.set_index('Type')
            st.bar_chart(df_types)
    
    with col2:
        # Status Distribution
        statuses = {}
        for case in cases:
            status = case.get('status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        if statuses:
            st.subheader("📈 Status Distribution")
            import pandas as pd
            df_status = pd.DataFrame(list(statuses.items()))
            df_status.columns = ['Status', 'Count']
            df_status = df_status.set_index('Status')
            st.bar_chart(df_status)
    
    # HR Actions Summary
    st.subheader("👥 HR Actions Summary")
    hr_actions = {}
    for case in cases:
        action = case.get('hr_action', 'Pending')
        if action:
            hr_actions[action] = hr_actions.get(action, 0) + 1
    
    if hr_actions:
        import pandas as pd
        df_hr = pd.DataFrame(list(hr_actions.items()))
        df_hr.columns = ['HR Action', 'Count']
        st.dataframe(df_hr, use_container_width=True)
    
    # Export functionality
    st.markdown("---")
    if st.button("📥 Export Cases Report", type="primary"):
        # Convert cases to DataFrame for export
        import pandas as pd
        df_export = pd.DataFrame(cases)
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="💾 Download CSV Report",
            data=csv,
            file_name=f"internal_fraud_cases_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )