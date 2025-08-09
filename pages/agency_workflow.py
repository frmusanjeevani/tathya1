import streamlit as st
from database import get_db_connection, update_case_status, add_case_comment, log_audit
from case_display_utils import show_standardized_case_details
from datetime import datetime

def show():
    """Agency Workflow Panel for handling agency investigation responses"""
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
        '>Agency Workflow</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Manage agency investigation responses and case processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if "username" not in st.session_state or not st.session_state.get("authenticated"):
        st.error("Please log in to access this page")
        return
    
    current_user = st.session_state.get("username", "Unknown")
    
    show_agency_cases()

def show_agency_cases():
    """Display cases assigned to agencies and handle responses"""
    
    # Safe value extraction (handle both dict and sqlite3.Row)
    def safe_get(obj, key, default='N/A'):
        try:
            if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
                # This is a sqlite3.Row object
                return obj[key] if key in obj.keys() and obj[key] is not None else default
            elif hasattr(obj, 'get'):
                # This is a dict
                return obj.get(key, default)
            else:
                # This is an object with attributes
                return getattr(obj, key, default)
        except (KeyError, AttributeError, TypeError):
            return default
    
    # Get cases with Agency Investigation status
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, ca.assignee as agency_name, ca.tat, ca.assignment_date 
            FROM cases c
            LEFT JOIN case_assignments ca ON c.case_id = ca.case_id
            WHERE c.status = 'Agency Investigation' AND ca.assignment_types LIKE '%Agency Field Investigation%'
            ORDER BY c.created_at DESC
        """)
        agency_cases = cursor.fetchall()
    
    if not agency_cases:
        st.info("📋 No cases currently assigned to agencies")
        return
    
    st.markdown("### 📋 Cases Assigned to Agencies")
    
    # Add CSS for hover animations
    st.markdown("""
    <style>
    .stSelectbox > div > div > select:hover {
        transform: scale(1.02);
        transition: transform 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stSelectbox > div > div > select:active {
        transform: scale(1.0);
        transition: transform 0.1s ease;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create case options for dropdown
    case_options = []
    case_dict = {}
    
    for case in agency_cases:
        case_id = safe_get(case, 'case_id', 'Unknown')
        customer_name = safe_get(case, 'customer_name', 'Unknown')
        case_type = safe_get(case, 'case_type', 'Unknown')
        agency_name = safe_get(case, 'agency_name', 'Unknown')
        
        display_text = f"{case_id} - {customer_name} ({case_type}) - Agency: {agency_name}"
        case_options.append(display_text)
        case_dict[display_text] = case
    
    # Add filter dropdown for case selection
    selected_case_display = st.selectbox(
        "Select a case to view/respond:",
        ["Select a case..."] + case_options,
        key="agency_case_filter"
    )
    
    if selected_case_display != "Select a case...":
        selected_case = case_dict[selected_case_display]
        st.markdown("---")
        show_agency_case_response_form(selected_case)

def show_agency_case_response_form(case_details):
    """Show form for agency to submit investigation response"""
    
    # Safe value extraction (handle both dict and sqlite3.Row)
    def safe_get(obj, key, default='N/A'):
        try:
            if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
                # This is a sqlite3.Row object
                return obj[key] if key in obj.keys() and obj[key] is not None else default
            elif hasattr(obj, 'get'):
                # This is a dict
                return obj.get(key, default)
            else:
                # This is an object with attributes
                return getattr(obj, key, default)
        except (KeyError, AttributeError, TypeError):
            return default
    
    case_id = safe_get(case_details, 'case_id', 'Unknown')
    agency_name = safe_get(case_details, 'agency_name', 'Unknown')
    
    # Display case information
    st.markdown("#### 📄 Case Information")
    show_standardized_case_details(case_details)
    
    st.divider()
    
    # Agency Investigation Response Form
    st.markdown("#### 📝 Agency Investigation Response")
    
    # Create unique form key using case_id and timestamp
    import time
    unique_key = f"agency_response_{case_id}_{int(time.time())}{hash(str(case_details)) % 1000}"
    
    with st.form(unique_key):
        st.markdown(f"**Agency:** {agency_name}")
        st.markdown(f"**Case ID:** {case_id}")
        
        # Investigation Status
        investigation_status = st.selectbox(
            "Investigation Status",
            ["Investigation Completed", "Investigation In Progress", "Unable to Investigate", "Additional Information Required"]
        )
        
        # Investigation Findings
        st.markdown("**Investigation Findings**")
        
        col1, col2 = st.columns(2)
        with col1:
            customer_contacted = st.selectbox("Customer Contacted", ["Yes", "No", "Unable to Contact"])
            document_verification = st.selectbox("Document Verification", ["Completed", "Partial", "Not Possible"])
            address_verification = st.selectbox("Address Verification", ["Verified", "Not Verified", "Address Invalid"])
        
        with col2:
            identity_verification = st.selectbox("Identity Verification", ["Verified", "Not Verified", "Discrepancies Found"])
            employment_verification = st.selectbox("Employment Verification", ["Verified", "Not Verified", "Unable to Verify"])
            reference_verification = st.selectbox("Reference Verification", ["Verified", "Not Verified", "References Invalid"])
        
        # Investigation Summary
        investigation_summary = st.text_area(
            "Investigation Summary",
            placeholder="Detailed summary of investigation conducted, findings, observations...",
            height=150
        )
        
        # Risk Assessment
        risk_assessment = st.selectbox("Risk Assessment", ["Low Risk", "Medium Risk", "High Risk", "Fraud Suspected"])
        
        # Recommendation
        recommendation = st.selectbox(
            "Recommendation",
            ["Proceed with Case", "Reject Case", "Require Additional Review", "Flag for Legal Action"]
        )
        
        # Additional Comments
        additional_comments = st.text_area(
            "Additional Comments/Observations",
            placeholder="Any additional observations, concerns, or recommendations...",
            height=100
        )
        
        # Supporting Documents
        st.markdown("**Supporting Documents**")
        # Create truly unique key using timestamp and hash
        import time
        import hashlib
        unique_file_key = f"agency_docs_{case_id}_{int(time.time() * 1000)}_{hashlib.md5(str(case_details).encode()).hexdigest()[:8]}"
        
        uploaded_files = st.file_uploader(
            "Upload Investigation Documents",
            type=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
            accept_multiple_files=True,
            key=unique_file_key
        )
        
        # Response Routing
        st.markdown("#### 🔄 Response Routing")
        response_routing = st.selectbox(
            "Route Response To",
            ["Case Allocator", "Investigation Panel", "Primary Reviewer"],
            help="Select where this agency response should be routed in the workflow"
        )
        
        # Submit Response
        if st.form_submit_button("📤 Submit Agency Response", type="primary"):
            submit_agency_response(
                case_id, agency_name, investigation_status, investigation_summary,
                risk_assessment, recommendation, additional_comments, response_routing,
                {
                    'customer_contacted': customer_contacted,
                    'document_verification': document_verification,
                    'address_verification': address_verification,
                    'identity_verification': identity_verification,
                    'employment_verification': employment_verification,
                    'reference_verification': reference_verification
                },
                uploaded_files
            )

def submit_agency_response(case_id, agency_name, investigation_status, investigation_summary,
                          risk_assessment, recommendation, additional_comments, response_routing,
                          verification_details, uploaded_files):
    """Process agency investigation response and route to appropriate workflow stage"""
    
    current_user = st.session_state.get("username", agency_name)
    
    try:
        # Save agency response to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create agency responses table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agency_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    agency_name TEXT,
                    investigation_status TEXT,
                    investigation_summary TEXT,
                    risk_assessment TEXT,
                    recommendation TEXT,
                    additional_comments TEXT,
                    verification_details TEXT,
                    response_routing TEXT,
                    submitted_by TEXT,
                    submission_date TEXT,
                    FOREIGN KEY (case_id) REFERENCES cases (case_id)
                )
            ''')
            
            # Insert agency response
            cursor.execute('''
                INSERT INTO agency_responses 
                (case_id, agency_name, investigation_status, investigation_summary, 
                 risk_assessment, recommendation, additional_comments, verification_details,
                 response_routing, submitted_by, submission_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_id, agency_name, investigation_status, investigation_summary,
                risk_assessment, recommendation, additional_comments, str(verification_details),
                response_routing, current_user, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
        
        # Handle file uploads
        if uploaded_files:
            import os
            upload_dir = f"uploads/agency_responses/{case_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            for file in uploaded_files:
                file_path = os.path.join(upload_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
        
        # Route response based on selection
        route_agency_response(case_id, response_routing, agency_name, investigation_status, 
                            risk_assessment, recommendation, current_user)
        
        st.success("✅ Agency response submitted successfully!")
        st.info(f"📍 Response routed to: {response_routing}")
        
        # Show next steps based on routing
        if response_routing == "Case Allocator":
            st.info("🔄 Case returned to Case Allocator for review and next steps")
        elif response_routing == "Investigation Panel":
            st.info("🔍 Case sent to Investigation Panel for further investigation")
        elif response_routing == "Primary Reviewer":
            st.info("📋 Case sent to Primary Reviewer for review and approval")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error submitting agency response: {str(e)}")

def route_agency_response(case_id, response_routing, agency_name, investigation_status, 
                         risk_assessment, recommendation, submitted_by):
    """Route agency response to appropriate workflow stage"""
    
    # Create response comment
    comment = f"AGENCY INVESTIGATION RESPONSE\nAgency: {agency_name}\nStatus: {investigation_status}\nRisk: {risk_assessment}\nRecommendation: {recommendation}\nRouted to: {response_routing}"
    
    # Update case status based on routing
    if response_routing == "Case Allocator":
        new_status = "Allocator Review"
    elif response_routing == "Investigation Panel":
        new_status = "Under Investigation"
    elif response_routing == "Primary Reviewer":
        new_status = "Under Review"
    else:
        new_status = "Agency Response Received"
    
    # Update case status
    update_case_status(case_id, new_status, submitted_by)
    
    # Add comment
    add_case_comment(case_id, comment, submitted_by, "Agency Response")
    
    # Log audit
    log_audit(case_id, f"Agency Response - {response_routing}", f"Agency response processed by {submitted_by}", submitted_by)

def safe_get(obj, key, default=''):
    """Safely get value from object (handles both dict and sqlite3.Row)"""
    try:
        if hasattr(obj, key):
            return getattr(obj, key, default)
        elif isinstance(obj, dict):
            return obj.get(key, default)
        elif hasattr(obj, '__getitem__'):
            return obj[key] if key in obj else default
        else:
            return default
    except (KeyError, IndexError, AttributeError):
        return default

if __name__ == "__main__":
    show()