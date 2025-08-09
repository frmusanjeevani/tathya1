import streamlit as st
from database import get_db_connection, update_case_status, add_case_comment, log_audit
from case_display_utils import show_standardized_case_details
from datetime import datetime
from standardized_case_styling import apply_standardized_case_styling, create_standard_case_display
from auth import require_role

def show():
    """Regional Investigation Panel for handling regional investigation responses"""
    require_role(["Investigator", "Regional Investigator", "Admin"])
    
    # Apply standardized styling
    apply_standardized_case_styling()
    
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
        '>Regional Investigation Workflow</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Process regional investigation cases and detailed field verification</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if "username" not in st.session_state or not st.session_state.get("authenticated"):
        st.error("Please log in to access this page")
        return
    
    current_user = st.session_state.get("username", "Unknown")
    
    show_regional_investigation_cases()

def show_regional_investigation_cases():
    """Display cases assigned to regional investigation and handle responses"""
    
    # Safe value extraction (handle both dict and sqlite3.Row)
    def safe_get(obj, key, default='N/A'):
        try:
            if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
                return obj[key] if key in obj.keys() and obj[key] is not None else default
            elif hasattr(obj, 'get'):
                return obj.get(key, default)
            else:
                return getattr(obj, key, default)
        except (KeyError, AttributeError, TypeError):
            return default
    
    # Get cases assigned to regional investigation (multiple sources for data flow)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM cases 
            WHERE status IN ('Regional Investigation', 'Under Investigation') 
            ORDER BY created_at DESC
        """)
        regional_cases = cursor.fetchall()
    
    if not regional_cases:
        st.info("📭 No cases assigned to regional investigation")
        return
    
    st.markdown("### 📋 Cases Under Regional Investigation")
    st.markdown(f"*{len(regional_cases)} case(s) assigned for regional investigation*")
    
    for case in regional_cases:
        case_id = safe_get(case, 'case_id')
        customer_name = safe_get(case, 'customer_name')
        case_type = safe_get(case, 'case_type')
        loan_amount = safe_get(case, 'loan_amount', 0)
        
        # Format amount for display
        try:
            loan_amount_float = float(loan_amount) if loan_amount else 0
            formatted_loan = f"{loan_amount_float:,.0f}" if loan_amount_float > 0 else 'N/A'
        except (ValueError, TypeError):
            formatted_loan = 'N/A'
        
        with st.expander(f"🔍 Regional Investigation: {case_id} - {customer_name} ({case_type}) - ₹{formatted_loan}", expanded=False):
            
            # Case Information Section
            st.markdown("### 📄 Case Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Case ID")
                create_standard_case_display(case_id, customer_name, case_type, formatted_loan, 
                                           f"Product: {safe_get(case, 'product')} | Region: {safe_get(case, 'region')}")
                
                st.markdown("#### Basic Details")
                st.markdown(f"""
                <div class='case-details-text'>
                    <strong>LAN:</strong> {safe_get(case, 'lan')}<br>
                    <strong>Product:</strong> {safe_get(case, 'product')}<br>
                    <strong>Region:</strong> {safe_get(case, 'region')}<br>
                    <strong>Branch:</strong> {safe_get(case, 'branch_location')}<br>
                    <strong>Referred By:</strong> {safe_get(case, 'referred_by')}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### Customer Information")
                st.markdown(f"""
                <div class='case-details-text'>
                    <strong>Name:</strong> {customer_name}<br>
                    <strong>Mobile:</strong> {safe_get(case, 'customer_mobile')}<br>
                    <strong>Email:</strong> {safe_get(case, 'customer_email')}<br>
                    <strong>PAN:</strong> {safe_get(case, 'customer_pan')}<br>
                    <strong>Occupation:</strong> {safe_get(case, 'customer_occupation')}<br>
                    <strong>Income:</strong> ₹{safe_get(case, 'customer_income')}
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Regional Investigation Details
            st.markdown("### 🔍 Regional Investigation Details")
            
            with st.form(f"regional_investigation_{case_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Investigation Scope")
                    investigation_type = st.selectbox("Investigation Type", 
                        ["Address Verification", "Employment Verification", "Reference Check", 
                         "Asset Verification", "Comprehensive Investigation"], 
                        key=f"reg_inv_type_{case_id}")
                    
                    priority_level = st.selectbox("Priority Level", 
                        ["Standard", "High", "Critical"], 
                        key=f"reg_priority_{case_id}")
                    
                    estimated_completion = st.date_input("Estimated Completion Date", 
                                                       key=f"reg_completion_{case_id}")
                
                with col2:
                    st.markdown("#### Investigation Team")
                    investigator_name = st.text_input("Lead Investigator", 
                                                    key=f"reg_investigator_{case_id}")
                    
                    team_members = st.text_area("Team Members", 
                                               placeholder="List team members involved in investigation...",
                                               key=f"reg_team_{case_id}")
                
                st.divider()
                
                # Investigation Findings
                st.markdown("### 📊 Investigation Findings")
                
                investigation_status = st.selectbox("Investigation Status", 
                    ["In Progress", "Findings Gathered", "Completed", "Requires Additional Info"], 
                    key=f"reg_status_{case_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    address_verified = st.selectbox("Address Verification", 
                        ["Not Started", "In Progress", "Verified", "Discrepancy Found"], 
                        key=f"reg_address_{case_id}")
                    
                    employment_verified = st.selectbox("Employment Verification", 
                        ["Not Started", "In Progress", "Verified", "Discrepancy Found"], 
                        key=f"reg_employment_{case_id}")
                
                with col2:
                    income_verified = st.selectbox("Income Verification", 
                        ["Not Started", "In Progress", "Verified", "Discrepancy Found"], 
                        key=f"reg_income_{case_id}")
                    
                    references_verified = st.selectbox("References Verification", 
                        ["Not Started", "In Progress", "Verified", "Discrepancy Found"], 
                        key=f"reg_references_{case_id}")
                
                # Investigation Report
                investigation_report = st.text_area("Investigation Report", 
                    placeholder="Detailed findings and observations from regional investigation...",
                    height=150, key=f"reg_report_{case_id}")
                
                # Risk Assessment
                st.markdown("#### Risk Assessment")
                risk_level = st.selectbox("Risk Level", 
                    ["Low", "Medium", "High", "Critical"], 
                    key=f"reg_risk_{case_id}")
                
                risk_factors = st.multiselect("Risk Factors Identified", 
                    ["Address Mismatch", "Employment Issues", "Income Discrepancy", 
                     "False References", "Document Forgery", "Identity Issues", "Other"], 
                    key=f"reg_risk_factors_{case_id}")
                
                # Request Missing Information Section
                st.divider()
                st.markdown("### 🔄 Request Missing Information")
                st.markdown("*Use this section if additional information is needed from previous stages*")
                
                missing_info_request = st.text_area("Request Missing Information", 
                    placeholder="Describe what additional information or documents are needed from Case Allocation or previous stages...",
                    key=f"reg_missing_info_{case_id}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    submit_findings = st.form_submit_button("📊 Submit Investigation Findings", 
                                                          type="primary")
                
                with col2:
                    request_info = st.form_submit_button("🔄 Request Additional Info")
                
                with col3:
                    mark_complete = st.form_submit_button("✅ Mark Investigation Complete")
                
                # Handle form submissions
                if submit_findings:
                    # Update case with investigation findings
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE cases SET 
                                investigation_findings = ?,
                                risk_level = ?,
                                updated_at = CURRENT_TIMESTAMP,
                                updated_by = ?
                            WHERE case_id = ?
                        """, (investigation_report, risk_level, st.session_state.get("username"), case_id))
                        conn.commit()
                    
                    # Add comment
                    add_case_comment(case_id, f"Regional Investigation Findings: {investigation_report[:100]}...", 
                                   st.session_state.get("username"))
                    
                    # Log audit
                    log_audit(case_id, "Regional Investigation Updated", 
                             f"Investigation findings submitted by {st.session_state.get('username')}", 
                             st.session_state.get("username"))
                    
                    st.success("✅ Investigation findings submitted successfully!")
                    st.rerun()
                
                elif request_info:
                    if missing_info_request:
                        # Add comment for missing information request
                        add_case_comment(case_id, f"MISSING INFO REQUEST: {missing_info_request}", 
                                       st.session_state.get("username"))
                        
                        # Update case status to indicate missing info needed
                        update_case_status(case_id, "Missing Information - Regional", 
                                         st.session_state.get("username"))
                        
                        log_audit(case_id, "Missing Information Requested", 
                                 f"Regional investigation requests additional info: {missing_info_request[:100]}...", 
                                 st.session_state.get("username"))
                        
                        st.success("✅ Missing information request sent to previous stage!")
                        st.rerun()
                    else:
                        st.error("Please describe what information is needed")
                
                elif mark_complete:
                    if investigation_report:
                        # Update case status to send to Primary Review
                        update_case_status(case_id, "Primary Review", st.session_state.get("username"))
                        
                        # Add completion comment
                        add_case_comment(case_id, f"Regional investigation completed. Risk Level: {risk_level}. Report: {investigation_report[:100]}...", 
                                       st.session_state.get("username"))
                        
                        log_audit(case_id, "Regional Investigation Completed", 
                                 f"Case moved to Primary Review by {st.session_state.get('username')}", 
                                 st.session_state.get("username"))
                        
                        st.success("✅ Regional investigation completed! Case moved to Primary Review.")
                        st.rerun()
                    else:
                        st.error("Please provide investigation report before marking complete")