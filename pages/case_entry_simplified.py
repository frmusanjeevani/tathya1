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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.08);
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
        padding: 8px 0;
        border-bottom: 2px solid #e1e5e9;
    '>
        <h2 style='
            font-size: 1.5rem;
            font-weight: 600;
            color: #2c3e50;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: "Segoe UI", Arial, sans-serif;
        '>CASE ENTRY</h2>
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
                ["Select Category...", "Lending", "Non-Lending"],
                help="Select the case category"
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
        
        # Type of Case (full width)
        type_of_case_options = [
            "Select Type of Case...",
            "Fraud Suspect",
            "Customer Complaint",
            "Whistleblower Input",
            "Internal Escalation",
            "Legal Referral",
            "Negative Verification",
            "High-Risk Profile",
            "Discrepant Documents",
            "Suspicious Activity Report (SAR)",
            "Repeat Offender / Pattern Match",
            "Misuse of Credentials",
            "Identity Mismatch",
            "Document Tampering",
            "Branch Escalation",
            "Third-Party Alert (External)",
            "Social Media Flagged Case",
            "Call Center Escalation",
            "Field Investigation Required",
            "Deviation Approval Request",
            "Others (Please Specify)"
        ]
        case_type = st.selectbox(
            "Type of Case *",
            type_of_case_options,
            help="Select the type of case"
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
            if case_type == "Select Type of Case...":
                errors.append("Please select Type of Case")
            if not case_description.strip():
                errors.append("Case Description is required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Prepare case data with only the 7 fields
                case_data = {
                    'case_id': case_id,
                    'category': category,
                    'referred_by': referred_by,
                    'case_type': case_type,
                    'case_date': case_date.strftime("%Y-%m-%d"),
                    'case_description': case_description.strip(),
                    'created_by': current_user.get('username', 'Unknown'),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'Registered'
                }
                
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