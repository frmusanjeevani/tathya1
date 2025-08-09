import streamlit as st
from models import get_cases_by_status, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from auth import get_current_user, require_role

@require_role(["Approver", "Admin"])
def show():
    """Display approver 2 panel"""
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
        '>Approver 2 Panel</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Secondary approval level for enhanced case verification</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Pending Approval", "✅ Approved", "❌ Rejected"])
    
    with tab1:
        st.markdown("### 📋 Cases Pending Approver 2 Review")
        
        # Add professional styling
        st.markdown("""
        <style>
        .approval2-container {
            background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.08);
            border: 1px solid rgba(255, 152, 0, 0.1);
        }
        .case-header2 {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 8px 8px 0 0;
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 0;
        }
        .case-content2 {
            background: white;
            border: 1px solid #fff3e0;
            border-radius: 0 0 8px 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        approver2_cases = get_cases_by_status("Approver 2")  # Cases from Approver 1
        
        if approver2_cases:
            for case in approver2_cases:
                with st.expander(f"📋 Case: {case['case_id']} - {case['product']} ({case['region']})", expanded=False):
                    st.markdown(f"""
                    <div class="approval2-container">
                        <div class="case-content2">
                    """, unsafe_allow_html=True)
                    
                    show_case_details_for_approval2(case, current_user)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("📭 No cases pending Approver 2 review")
    
    with tab2:
        st.subheader("Approved Cases")
        approved_cases = get_cases_by_status("Final Review")
        
        if approved_cases:
            for case in approved_cases:
                with st.expander(f"Case: {case['case_id']} - {get_status_color(case['status'])} {case['status']}"):
                    show_read_only_case_details(case)
        else:
            st.info("📭 No approved cases")
    
    with tab3:
        st.subheader("Rejected Cases")
        rejected_cases = get_cases_by_status("Rejected")
        
        if rejected_cases:
            for case in rejected_cases:
                with st.expander(f"Case: {case['case_id']} - {get_status_color(case['status'])} {case['status']}"):
                    show_read_only_case_details(case)
        else:
            st.info("📭 No rejected cases")

def show_case_details_for_approval2(case, current_user):
    """Display case details for approver 2 workflow using standardized format"""
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
    st.write("**Approver 2 Actions:**")
    
    # Approval comments with AI suggestions
    st.markdown("**Approval Comments**")
    col_app1, col_app2 = st.columns([3, 1])
    with col_app2:
        if st.button("💡 Quick Remarks", key=f"approval2_sugg_{case['case_id']}"):
            from ai_suggestions import get_remarks_suggestions
            suggestions = get_remarks_suggestions()["approval_stage"]
            st.session_state[f"approval2_suggestions_{case['case_id']}"] = suggestions
    
    # Show suggestions
    if f"approval2_suggestions_{case['case_id']}" in st.session_state:
        st.markdown("**Quick Remarks:**")
        approval_cols = st.columns(2)
        for i, suggestion in enumerate(st.session_state[f"approval2_suggestions_{case['case_id']}"][:4]):
            col_idx = i % 2
            with approval_cols[col_idx]:
                if st.button(f"📝 {suggestion[:30]}...", key=f"app2_sugg_{case['case_id']}_{i}", help=suggestion):
                    st.session_state[f"selected_approval2_{case['case_id']}"] = suggestion
                    st.rerun()
    
    initial_approval = st.session_state.get(f"selected_approval2_{case['case_id']}", "")
    approval_comment = st.text_area("Approver 2 Comments",
        value=initial_approval,
        key=f"approval2_comment_{case['case_id']}",
        placeholder="Enter your approval decision comments or use quick remarks above...",
        height=80
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"✅ Send to Final Review", key=f"approve_to_final_{case['case_id']}"):
            if approval_comment.strip():
                if update_case_status(case['case_id'], "Final Review", current_user, f"APPROVER 2 APPROVED: {approval_comment}"):
                    st.success("✅ Case sent to Final Review")
                    st.rerun()
            else:
                st.warning("Please add approval comments")
    
    with col2:
        if st.button(f"❌ Reject", key=f"reject_a2_{case['case_id']}"):
            if approval_comment.strip():
                if update_case_status(case['case_id'], "Rejected", current_user, f"REJECTED BY APPROVER 2: {approval_comment}"):
                    st.success("✅ Case rejected")
                    st.rerun()
            else:
                st.warning("Please add rejection comments")
    
    with col3:
        if st.button(f"🔙 Send Back to Approver 1", key=f"send_back_a1_{case['case_id']}"):
            if approval_comment.strip():
                if update_case_status(case['case_id'], "Approved", current_user, f"SENT BACK TO APPROVER 1: {approval_comment}"):
                    st.success("✅ Case sent back to Approver 1")
                    st.rerun()
            else:
                st.warning("Please add comments")

def show_read_only_case_details(case):
    """Display read-only case details"""
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
        st.write(f"**Reviewed By:** {case['reviewed_by'] or 'N/A'}")
    
    st.write("**Case Description:**")
    st.write(case['case_description'])
    
    # Review history
    comments = get_case_comments(case['case_id'])
    if comments:
        st.write("**History:**")
        for comment in comments:
            st.write(f"**{comment['created_by']}** ({format_datetime(comment['created_at'])}) - *{comment['comment_type']}*")
            st.write(comment['comment'])
            st.divider()