import streamlit as st
from models import get_cases_by_status, get_case_by_id, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from pages.workflow_progress import show_workflow_progress
from auth import get_current_user, require_role
from database import get_db_connection, log_audit

@require_role(["Reviewer", "Investigator", "Admin"])
def show():
    """Display reviewer panel"""
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
        '>Reviewer Panel</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Primary review and assessment of investigated cases</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Show interaction requests for Primary Review stage
    try:
        from interaction_channels import show_interaction_requests_section
        show_interaction_requests_section("Primary Review", current_user)
    except Exception as e:
        st.info("📭 Interaction requests system initializing...")
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Pending Review", "🔄 In Progress", "✅ Completed"])
    
    with tab1:
        st.subheader("Cases Pending Review")
        
        # Get cases from multiple sources as Primary Review should receive from:
        # 1. Case Allocation (status: "Primary Review")
        # 2. Agency Investigation completed cases
        # 3. Regional Investigation completed cases
        primary_review_cases = get_cases_by_status("Primary Review")
        submitted_cases = get_cases_by_status("Submitted")  # Legacy cases
        
        all_review_cases = primary_review_cases + submitted_cases
        
        if all_review_cases:
            from standardized_page_format import show_standardized_case_list
            show_standardized_case_list(all_review_cases, "Primary Review", current_user, show_primary_review_case_details)
        else:
            st.info("📭 No cases pending primary review")
    
    with tab2:
        st.subheader("Cases Under Review")
        under_review_cases = get_cases_by_status("Under Review")
        
        if under_review_cases:
            from standardized_page_format import show_standardized_case_list
            show_standardized_case_list(under_review_cases, "Primary Review (In Progress)", current_user, show_primary_review_case_details)
        else:
            st.info("📭 No cases currently under review")
    
    with tab3:
        st.subheader("Completed Reviews")
        completed_cases = get_cases_by_status("Approved")
        
        if completed_cases:
            from standardized_page_format import show_standardized_case_list
            show_standardized_case_list(completed_cases, "Primary Review (Completed)", current_user, show_completed_review_summary)
        else:
            st.info("📭 No completed reviews")

def show_primary_review_case_details(case, current_user):
    """Show primary review case details with data flow integration"""
    from standardized_page_format import create_case_information_section, create_stage_interaction_section
    from data_flow_manager import show_previous_stage_summary, get_previous_stage_data, save_stage_data
    from interaction_channels import create_interaction_request_form
    
    # Safe value extraction
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
    
    case_id = safe_get(case, 'case_id')
    
    # Show case information
    create_case_information_section(case, show_flow_data=True)
    
    st.divider()
    
    # Show previous stage data (from Case Allocation, Agency, Regional)
    show_previous_stage_summary(case_id, "Primary Review")
    
    st.divider()
    
    # Primary Review Form
    st.markdown("### 🔍 Primary Review Assessment")
    
    with st.form(f"primary_review_{case_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            review_outcome = st.selectbox("Review Outcome", 
                ["Select Outcome...", "Approved", "Requires Clarification", "Rejected", "Refer to Approver"], 
                key=f"review_outcome_{case_id}")
            
            risk_assessment = st.selectbox("Risk Assessment", 
                ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"], 
                key=f"risk_assessment_{case_id}")
        
        with col2:
            compliance_status = st.selectbox("Compliance Status", 
                ["Compliant", "Minor Issues", "Major Issues", "Non-Compliant"], 
                key=f"compliance_{case_id}")
            
            recommended_action = st.selectbox("Recommended Action", 
                ["Proceed to Approval", "Additional Investigation", "Corrective Action", "Reject Case"], 
                key=f"recommended_action_{case_id}")
        
        # Review Comments
        review_comments = st.text_area("Review Comments", 
            placeholder="Detailed review comments and observations...",
            height=150, key=f"review_comments_{case_id}")
        
        # Key Findings
        key_findings = st.multiselect("Key Findings", 
            ["Documentation Complete", "Identity Verified", "Income Verified", "Address Verified", 
             "References Checked", "Risk Factors Identified", "Compliance Issues Found"], 
            key=f"key_findings_{case_id}")
        
        st.divider()
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            submit_review = st.form_submit_button("✅ Submit Review", type="primary")
        
        with col2:
            request_info = st.form_submit_button("🔄 Request Additional Info")
        
        with col3:
            save_draft = st.form_submit_button("💾 Save as Draft")
        
        # Handle form submissions
        if submit_review:
            if review_outcome != "Select Outcome..." and review_comments:
                # Save review data
                review_data = {
                    'review_outcome': review_outcome,
                    'risk_assessment': risk_assessment,
                    'compliance_status': compliance_status,
                    'recommended_action': recommended_action,
                    'review_comments': review_comments,
                    'key_findings': ','.join(key_findings)
                }
                
                save_stage_data(case_id, "Primary Review", review_data, current_user)
                
                # Update case status based on outcome
                if review_outcome == "Approved":
                    new_status = "Approved"
                elif review_outcome == "Refer to Approver":
                    new_status = "Approved"  # Goes to Approver 1
                else:
                    new_status = "Under Review"
                
                from models import update_case_status
                update_case_status(case_id, new_status, current_user)
                
                # Add comment
                from models import add_case_comment
                add_case_comment(case_id, f"PRIMARY REVIEW COMPLETED: {review_outcome}. {review_comments[:100]}...", current_user)
                
                st.success(f"✅ Primary review completed! Case status updated to {new_status}")
                st.rerun()
            else:
                st.error("Please select review outcome and provide comments")
        
        elif request_info:
            # Show request form
            st.markdown("---")
            create_interaction_request_form(case_id, "Primary Review", current_user)
        
        elif save_draft:
            if review_comments:
                # Save as draft
                review_data = {
                    'review_outcome': review_outcome,
                    'risk_assessment': risk_assessment,
                    'review_comments': review_comments,
                    'status': 'Draft'
                }
                
                save_stage_data(case_id, "Primary Review Draft", review_data, current_user)
                st.success("✅ Review draft saved!")
            else:
                st.error("Please provide some comments to save draft")

def show_completed_review_summary(case, current_user):
    """Show summary of completed reviews"""
    from data_flow_manager import get_previous_stage_data
    
    case_id = case.get('case_id', 'N/A')
    
    # Get review data
    review_data = get_previous_stage_data(case_id, ["Primary Review"])
    
    if "Primary Review" in review_data:
        review_info = review_data["Primary Review"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Review Outcome:** {review_info.get('review_outcome', 'N/A')}")
            st.markdown(f"**Risk Assessment:** {review_info.get('risk_assessment', 'N/A')}")
        
        with col2:
            st.markdown(f"**Compliance Status:** {review_info.get('compliance_status', 'N/A')}")
            st.markdown(f"**Recommended Action:** {review_info.get('recommended_action', 'N/A')}")
        
        if review_info.get('review_comments'):
            st.markdown(f"**Comments:** {review_info['review_comments'][:200]}...")

def show_comprehensive_case_review(case, current_user):
    """Display comprehensive case review with all information from case entry and allocation"""
    
    # Safe value extraction
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
    
    case_id = safe_get(case, 'case_id')
    
    # Create comprehensive sections
    st.markdown("### 📋 Comprehensive Case Overview")
    
    # Section 1: Basic Case Information
    with st.expander("📄 Basic Case Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Case Identification**")
            st.text(f"Case ID: {safe_get(case, 'case_id')}")
            st.text(f"LAN: {safe_get(case, 'lan')}")
            st.text(f"Case Type: {safe_get(case, 'case_type')}")
            st.text(f"Product: {safe_get(case, 'product')}")
            
        with col2:
            st.markdown("**Status & Timeline**")
            st.text(f"Status: {safe_get(case, 'status')}")
            st.text(f"Case Date: {safe_get(case, 'case_date')}")
            st.text(f"Created By: {safe_get(case, 'created_by')}")
            st.text(f"Referred By: {safe_get(case, 'referred_by')}")
            
        with col3:
            st.markdown("**Geographic & Financial**")
            st.text(f"Region: {safe_get(case, 'region')}")
            st.text(f"Branch: {safe_get(case, 'branch_location')}")
            st.text(f"Loan Amount: ₹{safe_get(case, 'loan_amount')}")
            st.text(f"Disbursement Date: {safe_get(case, 'disbursement_date')}")
    
    # Section 2: Customer Demographics
    with st.expander("👤 Customer Demographics", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Personal Information**")
            st.text(f"Customer Name: {safe_get(case, 'customer_name')}")
            st.text(f"Date of Birth: {safe_get(case, 'customer_dob')}")
            st.text(f"PAN: {safe_get(case, 'customer_pan')}")
            st.text(f"Customer Type: {safe_get(case, 'customer_type')}")
            
        with col2:
            st.markdown("**Contact Information**")
            st.text(f"Mobile: {safe_get(case, 'customer_mobile')}")
            st.text(f"Email: {safe_get(case, 'customer_email')}")
            st.text(f"KYC Status: {safe_get(case, 'kyc_status')}")
            st.text(f"Risk Category: {safe_get(case, 'risk_category')}")
    
    # Section 3: Case Description
    with st.expander("📝 Case Description", expanded=True):
        description = safe_get(case, 'case_description')
        st.text_area("Case Details", value=description, height=100, disabled=True)
    
    # Section 4: Case Actions & Assignments
    with st.expander("🎯 Case Actions & Assignments", expanded=True):
        # Get case actions from database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM case_actions 
                WHERE case_id = ? 
                ORDER BY created_at DESC
            """, (case_id,))
            case_actions = cursor.fetchall()
            
            cursor.execute("""
                SELECT * FROM case_assignments 
                WHERE case_id = ? 
                ORDER BY created_at DESC
            """, (case_id,))
            case_assignments = cursor.fetchall()
        
        if case_actions:
            st.markdown("**Case Actions Taken:**")
            for action in case_actions:
                st.text(f"• {safe_get(action, 'action_type')} by {safe_get(action, 'created_by')} on {safe_get(action, 'created_at')}")
                if safe_get(action, 'action_details'):
                    st.text(f"  Details: {safe_get(action, 'action_details')}")
        
        if case_assignments:
            st.markdown("**Case Assignments:**")
            for assignment in case_assignments:
                st.text(f"• {safe_get(assignment, 'assignment_type')} assigned to {safe_get(assignment, 'assigned_to')}")
                st.text(f"  Details: {safe_get(assignment, 'assignment_details')}")
                st.text(f"  Date: {safe_get(assignment, 'created_at')}")
    
    # Section 5: Case History & Comments
    with st.expander("📋 Case History & Comments", expanded=True):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM case_comments 
                WHERE case_id = ? 
                ORDER BY created_at DESC
            """, (case_id,))
            comments = cursor.fetchall()
            
            cursor.execute("""
                SELECT * FROM audit_logs 
                WHERE case_id = ? 
                ORDER BY performed_at DESC
            """, (case_id,))
            audit_logs = cursor.fetchall()
        
        if comments:
            st.markdown("**Case Comments:**")
            for comment in comments:
                st.text(f"• {safe_get(comment, 'created_by')} ({safe_get(comment, 'comment_type')}): {safe_get(comment, 'comment')}")
                st.text(f"  Date: {safe_get(comment, 'created_at')}")
        
        if audit_logs:
            st.markdown("**Audit Trail:**")
            for log in audit_logs[:5]:  # Show last 5 audit entries
                st.text(f"• {safe_get(log, 'action')} by {safe_get(log, 'performed_by')} on {safe_get(log, 'performed_at')}")
    
    # Section 6: Documents
    with st.expander("📎 Case Documents", expanded=True):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM case_documents 
                WHERE case_id = ? 
                ORDER BY uploaded_at DESC
            """, (case_id,))
            documents = cursor.fetchall()
        
        if documents:
            st.markdown("**Uploaded Documents:**")
            for doc in documents:
                st.text(f"• {safe_get(doc, 'original_filename')} ({safe_get(doc, 'upload_type')})")
                st.text(f"  Uploaded by {safe_get(doc, 'uploaded_by')} on {safe_get(doc, 'uploaded_at')}")
        else:
            st.info("No documents uploaded for this case")
    
    # Section 7: Review Actions
    if safe_get(case, 'status') in ['Submitted', 'Under Review', 'Under Investigation']:
        with st.expander("✅ Review Actions", expanded=True):
            st.markdown("**Reviewer Decision**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                review_decision = st.selectbox(
                    "Review Decision:",
                    ["Select Decision...", "Approve", "Reject", "Send to Approver 1", "Request Additional Information"],
                    key=f"review_decision_{case_id}"
                )
            
            with col2:
                reviewer_comments = st.text_area(
                    "Reviewer Comments:",
                    height=100,
                    key=f"reviewer_comments_{case_id}"
                )
            
            if st.button(f"📤 Submit Review", key=f"submit_review_{case_id}"):
                if review_decision != "Select Decision..." and reviewer_comments.strip():
                    # Process review decision
                    new_status = "Approver 1" if review_decision == "Send to Approver 1" else review_decision
                    
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE cases 
                            SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, updated_by = ?
                            WHERE case_id = ?
                        """, (new_status, current_user, current_user, case_id))
                        
                        # Add comment
                        cursor.execute("""
                            INSERT INTO case_comments (case_id, comment, comment_type, created_by, created_at)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (case_id, f"REVIEWER DECISION: {review_decision}\n{reviewer_comments}", "Review", current_user))
                        
                        conn.commit()
                    
                    st.success(f"✅ Review submitted successfully! Case status updated to: {new_status}")
                    st.rerun()
                else:
                    st.error("Please select a decision and add comments")

def show_case_details(case, current_user, allow_review=True):
    """Legacy function for backward compatibility"""
    pass
