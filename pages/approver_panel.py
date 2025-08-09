import streamlit as st
from models import get_cases_by_status, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from auth import get_current_user, require_role

@require_role(["Approver", "Admin"])
def show():
    """Display approver 1 panel"""
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
        '>Approver Panel</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Review and approve investigated cases for final processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Pending Approval", "✅ Approved", "❌ Rejected"])
    
    with tab1:
        st.subheader("📋 Cases Pending Approval")
        st.markdown("---")
        
        # Get cases requiring approval
        approved_cases = get_cases_by_status("Approved")  # Cases approved by reviewers, pending final approval
        
        if approved_cases:
            # Case level dropdown
            case_options = []
            for case in approved_cases:
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
                        
                case_id = safe_get(case, 'case_id', 'N/A')
                customer_name = safe_get(case, 'customer_name', 'N/A')
                case_type = safe_get(case, 'case_type', 'N/A')
                # Format amount for display  
                loan_amount = safe_get(case, 'loan_amount', 0)
                try:
                    loan_amount_float = float(loan_amount) if loan_amount else 0
                    formatted_loan = f"{loan_amount_float:,.0f}" if loan_amount_float > 0 else 'N/A'
                except (ValueError, TypeError):
                    formatted_loan = 'N/A'
                
                case_options.append(f"{case_id} - {customer_name} ({case_type}) - ₹{formatted_loan}")
            
            selected_case_display = st.selectbox(
                "Select Case for Approval:",
                ["Select a case..."] + case_options,
                key="approval_case_selector"
            )
            
            if selected_case_display != "Select a case...":
                # Extract case_id from selection
                selected_case_id = selected_case_display.split(" - ")[0]
                
                # Find the selected case
                selected_case = None
                for case in approved_cases:
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
                            
                    if safe_get(case, 'case_id') == selected_case_id:
                        selected_case = case
                        break
                
                if selected_case:
                    show_simple_approval_actions(selected_case, current_user)
        else:
            st.info("📭 No cases pending approval")
    
    with tab2:
        st.subheader("Final Approved Cases")
        # You might want to add a new status like "Final Approved" for this
        st.info("Cases with final approval will appear here")
    
    with tab3:
        st.subheader("Rejected Cases")
        rejected_cases = get_cases_by_status("Rejected")
        
        if rejected_cases:
            for case in rejected_cases:
                with st.expander(f"Case: {case['case_id']} - {get_status_color(case['status'])} {case['status']}"):
                    show_read_only_case_details(case)
        else:
            st.info("📭 No rejected cases")

def show_case_details_for_approval(case, current_user):
    """Display case details for approval workflow using standardized format"""
    from case_display_utils import show_standardized_case_details, show_standardized_customer_info, show_standardized_case_history, show_standardized_documents
    
    # Display standardized case details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_standardized_case_details(case)
        show_standardized_customer_info(case)
    
    with col2:
        show_standardized_case_history(case['case_id'])
        show_standardized_documents(case['case_id'])
    
    # Approval actions
    st.write("**Approval Actions:**")
    
    # Approval comments with AI suggestions
    st.markdown("**Approval Comments**")
    col_app1, col_app2 = st.columns([3, 1])
    with col_app2:
        if st.button("💡 Quick Remarks", key=f"approval_sugg_{case['case_id']}"):
            from ai_suggestions import get_remarks_suggestions
            suggestions = get_remarks_suggestions()["approval_stage"]
            st.session_state[f"approval_suggestions_{case['case_id']}"] = suggestions
    
    # Show suggestions
    if f"approval_suggestions_{case['case_id']}" in st.session_state:
        st.markdown("**Quick Remarks:**")
        approval_cols = st.columns(2)
        for i, suggestion in enumerate(st.session_state[f"approval_suggestions_{case['case_id']}"][:4]):
            col_idx = i % 2
            with approval_cols[col_idx]:
                if st.button(f"📝 {suggestion[:30]}...", key=f"app_sugg_{case['case_id']}_{i}", help=suggestion):
                    st.session_state[f"selected_approval_{case['case_id']}"] = suggestion
                    st.rerun()
    
    initial_approval = st.session_state.get(f"selected_approval_{case['case_id']}", "")
    approval_comment = st.text_area("Approval Comments",
        value=initial_approval,
        key=f"approval_comment_{case['case_id']}",
        placeholder="Enter your approval decision comments or use quick remarks above...",
        height=80
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"✅ Send to Approver 2", key=f"approve_to_a2_{case['case_id']}"):
            if approval_comment.strip():
                if update_case_status(case['case_id'], "Approver 2", current_user, f"APPROVER 1 APPROVED: {approval_comment}"):
                    st.success("✅ Case sent to Approver 2")
                    st.rerun()
            else:
                st.warning("Please add approval comments")
    
    with col2:
        if st.button(f"❌ Reject", key=f"final_reject_{case['case_id']}"):
            if approval_comment.strip():
                if update_case_status(case['case_id'], "Rejected", current_user, f"REJECTED: {approval_comment}"):
                    st.success("✅ Case rejected")
                    st.rerun()
            else:
                st.warning("Please add rejection comments")
    
    with col3:
        if st.button(f"🔙 Send Back for Review", key=f"send_back_{case['case_id']}"):
            if approval_comment.strip():
                if update_case_status(case['case_id'], "Under Review", current_user, f"SENT BACK: {approval_comment}"):
                    st.success("✅ Case sent back for review")
                    st.rerun()
            else:
                st.warning("Please add comments explaining why it's being sent back")

def show_read_only_case_details(case):
    """Display read-only case details"""
    
    # Basic case information
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Case ID:** {case['case_id']}")
        st.write(f"**LAN:** {case['lan']}")
        st.write(f"**Type:** {case['case_type']}")
        st.write(f"**Product:** {case['product']}")
        st.write(f"**Region:** {case['region']}")
    
    with col2:
        st.write(f"**Status:** {get_status_color(case['status'])} {case['status']}")
        st.write(f"**Referred By:** {case['referred_by']}")
        st.write(f"**Case Date:** {case['case_date']}")
        st.write(f"**Created By:** {case['created_by']}")
        st.write(f"**Last Updated:** {format_datetime(case['updated_at'])}")
    
    # Case description
    st.write("**Case Description:**")
    st.write(case['case_description'])
    
    # Comments history
    comments = get_case_comments(case['case_id'])
    if comments:
        st.write("**Comments History:**")
        for comment in comments:
            st.write(f"**{comment['created_by']}** ({format_datetime(comment['created_at'])}) - *{comment['comment_type']}*")
            st.write(comment['comment'])
            st.divider()
    
    # Documents
    documents = get_case_documents(case['case_id'])
    if documents:
        st.write("**Supporting Documents:**")
        for doc in documents:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📎 {doc['original_filename']}")
            with col2:
                st.write(format_file_size(doc['file_size']))
            with col3:
                st.write(format_datetime(doc['uploaded_at']))

def show_simple_approval_actions(case, current_user):
    """Display simple approval actions without complex formatting"""
    
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
    
    # Simple case info display
    case_id = safe_get(case, 'case_id', 'N/A')
    customer_name = safe_get(case, 'customer_name', 'N/A')
    case_type = safe_get(case, 'case_type', 'N/A')
    loan_amount = safe_get(case, 'loan_amount', 'N/A')
    
    st.write(f"**Case ID:** {case_id}")
    st.write(f"**Customer:** {customer_name}")
    st.write(f"**Type:** {case_type}")
    st.write(f"**Loan Amount:** ₹{loan_amount}")
    st.write("")
    
    # Approval comments
    approval_comments = st.text_area(
        "Approval Comments:",
        placeholder="Enter approval comments and recommendations...",
        height=100,
        key=f"approval_comments_{case_id}"
    )
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"Approve Case", key=f"approve_{case_id}"):
            if approval_comments.strip():
                try:
                    comment_text = f"APPROVED BY APPROVER 1: {approval_comments}"
                    from models import add_case_comment, update_case_status
                    
                    if add_case_comment(case_id, comment_text, current_user, "Approval"):
                        if update_case_status(case_id, "Approver 2", current_user):
                            from error_handler import success_message
                            success_message("Case Approved", "Case approved and sent to Approver 2")
                            st.rerun()
                except Exception as e:
                    from error_handler import handle_database_error
                    handle_database_error("case approval", e)
            else:
                from error_handler import handle_validation_error
                handle_validation_error("Approval Comments", "Please provide approval comments")
    
    with col2:
        if st.button("Request Additional Info", key=f"req_info_{case_id}"):
            if approval_comments.strip():
                try:
                    comment_text = f"ADDITIONAL INFO REQUESTED: {approval_comments}"
                    from models import add_case_comment, update_case_status
                    
                    if add_case_comment(case_id, comment_text, current_user, "Info Request"):
                        if update_case_status(case_id, "Under Review", current_user):
                            from error_handler import success_message
                            success_message("Information Requested", "Additional information requested")
                            st.rerun()
                except Exception as e:
                    from error_handler import handle_database_error
                    handle_database_error("information request", e)
            else:
                from error_handler import handle_validation_error
                handle_validation_error("Information Request", "Please specify what information is needed")
