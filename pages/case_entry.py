import streamlit as st
import uuid
import os
from datetime import datetime
from models import create_simplified_case
from utils import validate_case_data, save_uploaded_file, generate_case_id
from auth import get_current_user, require_role

def show():
    """Display simplified case entry page with only 7 required fields"""
    # Check role access - Investigators and Initiators can create cases
    require_role(["Initiator", "Investigator", "Admin"])
    
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
        '>New Case Registration</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Register a new case with essential details - All marked fields (*) are required</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Clean form styling
    st.markdown("""
    <style>
    .stTextArea > div > div > textarea {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
    }
    .stTextInput > div > div > input {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
    }
    .stSelectbox > div > div > div {
        background-color: #f8f9fa !important;
    }
    .stDateInput > div > div > input {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### Enter New Case Details")
    
    # Auto-generate Case ID
    if "auto_case_id" not in st.session_state:
        st.session_state.auto_case_id = generate_case_id()

    # Main form with only the 7 required fields
    with st.form("simplified_case_entry_form", clear_on_submit=False):
        
        # Basic Case Info Section
        st.markdown("#### 📋 Basic Case Info")
        
        # Case ID
        case_id = st.text_input(
            "Case ID", 
            value=st.session_state.auto_case_id, 
            disabled=True, 
            help="Auto-generated unique case ID"
        )
        
        # 3-column layout for other basic fields
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Category
            category = st.selectbox(
                "Category *",
                ["Select Category...", "Lending", "Digital", "Non-Lending"],
                help="Select the case category",
                key="category_selector"
            )
        
        with col2:
            # Referred By
            referred_by_options = [
                "Select Referred By...",
                "Branch Manager",
                "Sales Manager", 
                "Risk Team",
                "Legal Team",
                "Customer Service",
                "Whistleblower",
                "Third-Party Agency",
                "Internal Audit",
                "Automated Flag",
                "Customer Direct"
            ]
            referred_by = st.selectbox(
                "Referred By *",
                referred_by_options,
                help="Who referred this case"
            )
        
        with col3:
            # Case Date
            case_date = st.date_input(
                "Case Date *",
                value=datetime.today(),
                help="Date when case was identified/reported"
            )
        
        # Type of Case (full width) - Dynamic based on Category
        if category in ["Lending", "Digital"]:
            # Auto-select Fraud Suspect for Lending and Digital categories
            type_of_case_options = ["Fraud Suspect"]
            case_type = st.selectbox(
                "Case Type *",
                type_of_case_options,
                help="Automatically set to Fraud Suspect for Lending/Digital categories",
                key="case_type_selector",
                disabled=True
            )
            case_type = "Fraud Suspect"  # Force the value
        elif category == "Non-Lending":
            # Full options for Non-Lending category
            type_of_case_options = [
                "Select Type of Case...",
                "Fraud Suspect",
                "Attempted Fraud",
                "Customer Complaint", 
                "Internal Escalation",
                "Legal Referral",
                "Credential Misuse",
                "Branch Escalation",
                "Third-Party Alert",
                "Social Media Flag",
                "Call Center Escalation",
                "Audit Observation",
                "EWS – Early Warning Signal",
                "Other (Specify)"
            ]
            case_type = st.selectbox(
                "Case Type *",
                type_of_case_options,
                help="Select the type of case",
                key="case_type_selector"
            )
        else:
            # Default when no category selected
            case_type = st.selectbox(
                "Case Type *",
                ["Select Category First..."],
                help="Please select a category first",
                key="case_type_selector",
                disabled=True
            )
        
        st.markdown("---")
        
        # Dynamic Case Details Section based on Case Type
        case_details = {}
        if case_type and case_type not in ["Select Type of Case...", "Select Category First..."]:
            st.markdown("#### 📋 Case Details")
            
            # Create container for dynamic updates
            details_container = st.container()
            
            with details_container:
                if case_type == "Fraud Suspect":
                    case_details['suspected_fraud_modus_operandi'] = st.text_area(
                        "Suspected Fraud Modus Operandi *", 
                        placeholder="Describe the suspected method of fraud...",
                        height=80,
                        key="fraud_modus"
                    )
                    case_details['source_of_suspicion'] = st.text_input(
                        "Source of Suspicion *",
                        placeholder="How was this suspected fraud identified?",
                        key="fraud_source"
                    )
                    case_details['initial_loss_estimate'] = st.number_input(
                        "Initial Loss Estimate (₹)",
                        min_value=0.0,
                        step=1000.0,
                        format="%.2f",
                        key="fraud_loss"
                    )
                
                elif case_type == "Attempted Fraud":
                    case_details['suspected_fraud_modus_operandi'] = st.text_area(
                        "Suspected Fraud Modus Operandi *", 
                        placeholder="Describe the attempted fraud method...",
                        height=80,
                        key="attempted_fraud_modus"
                    )
                    case_details['source_of_suspicion'] = st.text_input(
                        "Source of Suspicion *",
                        placeholder="How was this attempted fraud identified?",
                        key="attempted_fraud_source"
                    )
                    case_details['initial_loss_estimate'] = st.number_input(
                        "Initial Loss Estimate (₹)",
                        min_value=0.0,
                        step=1000.0,
                        format="%.2f",
                        key="attempted_fraud_loss"
                    )
                
                elif case_type == "Customer Complaint":
                    case_details['complaint_nature'] = st.text_input(
                        "Complaint Nature *",
                        placeholder="Nature of the customer complaint",
                        key="complaint_nature"
                    )
                    case_details['customer_statement_summary'] = st.text_area(
                        "Customer Statement Summary *",
                        placeholder="Summary of customer's statement...",
                        height=80,
                        key="complaint_summary"
                    )
                    case_details['date_of_incident'] = st.date_input(
                        "Date of Incident *",
                        key="complaint_date"
                    )
                
                elif case_type == "Internal Escalation":
                    case_details['escalation_source'] = st.text_input(
                        "Escalation Source *",
                        placeholder="Department/Team that escalated this case",
                        key="escalation_source"
                    )
                    case_details['escalation_reason'] = st.text_area(
                        "Escalation Reason *",
                        placeholder="Reason for escalation...",
                        height=80,
                        key="escalation_reason"
                    )
                    case_details['related_department'] = st.text_input(
                        "Related Department *",
                        placeholder="Department involved in the issue",
                        key="related_department"
                    )
                
                elif case_type == "Legal Referral":
                    case_details['law_enforcement_agency'] = st.text_input(
                        "Law Enforcement Agency *",
                        placeholder="Name of law enforcement agency",
                        key="law_enforcement_agency"
                    )
                    case_details['fir_case_number'] = st.text_input(
                        "FIR/Case Number *",
                        placeholder="Official case/FIR number",
                        key="fir_case_number"
                    )
                    case_details['date_of_referral'] = st.date_input(
                        "Date of Referral *",
                        key="date_of_referral"
                    )
                
                elif case_type == "Credential Misuse":
                    case_details['type_of_credentials_misused'] = st.text_input(
                        "Type of Credentials Misused *",
                        placeholder="What type of credentials were misused?",
                        key="type_of_credentials_misused"
                    )
                    case_details['method_of_compromise'] = st.text_area(
                        "Method of Compromise *",
                        placeholder="How were the credentials compromised?...",
                        height=80,
                        key="method_of_compromise"
                    )
                    case_details['date_detected'] = st.date_input(
                        "Date Detected *",
                        key="date_detected"
                    )
                
                elif case_type == "Branch Escalation":
                    case_details['branch_name_code'] = st.text_input(
                        "Branch Name/Code *",
                        placeholder="Branch name or code",
                        key="branch_name_code"
                    )
                    case_details['escalation_trigger'] = st.text_area(
                        "Escalation Trigger *",
                        placeholder="What triggered the escalation?...",
                        height=80,
                        key="escalation_trigger"
                    )
                    case_details['responsible_officer'] = st.text_input(
                        "Responsible Officer *",
                        placeholder="Name of responsible officer",
                        key="responsible_officer"
                    )
                
                elif case_type == "Third-Party Alert":
                    case_details['source_entity'] = st.text_input(
                        "Source Entity *",
                        placeholder="Entity that provided the alert",
                        key="source_entity"
                    )
                    case_details['alert_type'] = st.text_input(
                        "Alert Type *",
                        placeholder="Type of alert received",
                        key="alert_type"
                    )
                    case_details['date_of_alert'] = st.date_input(
                        "Date of Alert *",
                        key="date_of_alert"
                    )
                
                elif case_type == "Social Media Flag":
                    case_details['platform'] = st.text_input(
                        "Platform *",
                        placeholder="Social media platform",
                        key="platform"
                    )
                    case_details['post_content_link'] = st.text_input(
                        "Post/Content Link *",
                        placeholder="Link to the flagged content",
                        key="post_content_link"
                    )
                    case_details['date_posted'] = st.date_input(
                        "Date Posted *",
                        key="date_posted"
                    )
                
                elif case_type == "Call Center Escalation":
                    case_details['call_id_reference'] = st.text_input(
                        "Call ID/Reference *",
                        placeholder="Call reference number",
                        key="call_id_reference"
                    )
                    case_details['escalation_reason'] = st.text_area(
                        "Escalation Reason *",
                        placeholder="Reason for escalating from call center...",
                        height=80,
                        key="call_escalation_reason"
                    )
                    case_details['date_of_call'] = st.date_input(
                        "Date of Call *",
                        key="date_of_call"
                    )
                
                elif case_type == "Audit Observation":
                    case_details['audit_type'] = st.text_input(
                        "Audit Type *",
                        placeholder="Type of audit (Internal/External/Compliance etc.)",
                        key="audit_type"
                    )
                    case_details['observation_summary'] = st.text_area(
                        "Observation Summary *",
                        placeholder="Summary of audit observation...",
                        height=80,
                        key="observation_summary"
                    )
                    case_details['audit_date'] = st.date_input(
                        "Audit Date *",
                        key="audit_date"
                    )
                
                elif case_type == "EWS – Early Warning Signal":
                    case_details['signal_type'] = st.text_input(
                        "Signal Type *",
                        placeholder="Type of early warning signal",
                        key="signal_type"
                    )
                    case_details['trigger_source'] = st.text_input(
                        "Trigger Source *",
                        placeholder="Source that triggered the EWS",
                        key="trigger_source"
                    )
                    case_details['observation_date'] = st.date_input(
                        "Observation Date *",
                        key="observation_date"
                    )
                
                elif case_type == "Other (Specify)":
                    case_details['description'] = st.text_area(
                        "Description *",
                        placeholder="Detailed description of the case...",
                        height=80,
                        key="other_description"
                    )
                    case_details['source'] = st.text_input(
                        "Source *",
                        placeholder="Source of information",
                        key="other_source"
                    )
                    case_details['date_noted'] = st.date_input(
                        "Date Noted *",
                        key="date_noted"
                    )
            
            st.markdown("---")
        
        # Case Description Section
        st.markdown("#### 📝 Case Description")
        case_description = st.text_area(
            "Case Description *",
            placeholder="Provide detailed description of the case, including relevant facts, circumstances, and initial observations...",
            height=120,
            help="Detailed description of the case including background, circumstances, and key concerns"
        )
        
        st.markdown("---")
        
        # Documents Section
        st.markdown("#### 📎 Documents")
        supporting_evidence = st.file_uploader(
            "Supporting Evidence",
            type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="Upload relevant documents as supporting evidence"
        )
        
        # Display uploaded files
        if supporting_evidence:
            st.markdown("**Uploaded Files:**")
            for file in supporting_evidence:
                file_size = len(file.getvalue()) / 1024  # Size in KB
                st.write(f"📄 {file.name} ({file_size:.1f} KB)")
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button(
            "🎯 Register Case", 
            type="primary",
            use_container_width=True
        )
        
        # Form submission handling
        if submitted:
            # Validation
            errors = []
            
            if category == "Select Category...":
                errors.append("Please select a Category")
            if referred_by == "Select Referred By...":
                errors.append("Please select who Referred this case")
            if case_type in ["Select Type of Case...", "Select Category First..."]:
                errors.append("Please select Case Type")
            
            # Validate case details based on case type
            if case_type != "Select Type of Case..." and case_details:
                for field_name, field_value in case_details.items():
                    if isinstance(field_value, str) and not field_value.strip():
                        field_display = field_name.replace('_', ' ').title()
                        errors.append(f"{field_display} is required for {case_type}")
                    elif field_value is None:
                        field_display = field_name.replace('_', ' ').title()
                        errors.append(f"{field_display} is required for {case_type}")
            if not case_description.strip():
                errors.append("Case Description is required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Prepare case data with case type and dynamic case details
                case_data = {
                    'case_id': case_id,
                    'category': category,
                    'referred_by': referred_by,
                    'case_type': case_type,
                    'case_date': case_date.strftime("%Y-%m-%d"),
                    'case_description': case_description.strip(),
                    'created_by': current_user if isinstance(current_user, str) else current_user.get('username', 'Unknown'),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'Registered'
                }
                
                # Add case details to case data
                for field_name, field_value in case_details.items():
                    if isinstance(field_value, str):
                        case_data[field_name] = field_value.strip()
                    else:
                        case_data[field_name] = str(field_value) if field_value is not None else None
                
                try:
                    # Create the simplified case
                    success = create_simplified_case(case_data)
                    
                    if success:
                        # Save uploaded files if any
                        if supporting_evidence:
                            for file in supporting_evidence:
                                save_uploaded_file(file, case_id, "Supporting Evidence")
                        
                        st.success(f"✅ Case {case_id} registered successfully!")
                        st.success("🔄 Case will now be available in Case Assignment for detailed processing")
                        
                        # Reset form
                        st.session_state.auto_case_id = generate_case_id()
                        st.rerun()
                    else:
                        st.error("❌ Failed to register case. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error registering case: {str(e)}")
    
    # Information box
    st.info("""
    **📝 Case Entry Process:**
    
    1. **Basic Information**: Enter essential case details and categorization
    2. **Case Description**: Provide comprehensive case background  
    3. **Supporting Evidence**: Upload relevant documents
    4. **Next Step**: Case moves to Case Assignment for detailed customer information and investigation planning
    
    *Note: Detailed customer demographics, financial information, and investigation details will be captured in the Case Assignment module.*
    """)

def create_simplified_case(case_data):
    """Create a simplified case record with only basic information"""
    from database import get_db_connection, log_audit
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create simplified cases table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases_simplified (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    referred_by TEXT NOT NULL,
                    case_type TEXT NOT NULL,
                    case_date DATE NOT NULL,
                    case_description TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    status TEXT DEFAULT 'Registered',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert the case
            cursor.execute('''
                INSERT INTO cases_simplified (
                    case_id, category, referred_by, case_type, case_date, 
                    case_description, created_by, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_data['case_id'],
                case_data['category'],
                case_data['referred_by'],
                case_data['case_type'],
                case_data['case_date'],
                case_data['case_description'],
                case_data['created_by'],
                case_data['created_at'],
                case_data['status']
            ))
            
            conn.commit()
            
            # Log audit trail
            log_audit(
                case_data['case_id'], 
                "Case Registered", 
                f"Simplified case entry by {case_data['created_by']}", 
                case_data['created_by']
            )
            
            return True
            
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False