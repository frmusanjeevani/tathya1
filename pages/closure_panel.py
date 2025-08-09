import streamlit as st
from models import get_cases_by_status, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from auth import get_current_user, require_role

@require_role(["Actioner", "Admin"])
def show():
    """Display actioner panel"""
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
        '>Closure Panel</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Final case closure with action recommendations and risk evaluation</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Cases from Final Review available for closure action (parallel with Legal)**")
    
    current_user = get_current_user()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["⏳ Ready for Closure", "✅ Closed Cases", "📊 Closure Analytics"])
    
    with tab1:
        st.subheader("📋 Cases Ready for Closure")
        st.markdown("---")
        
        # Cases ready for closure (from Final Review - parallel with Legal)
        ready_cases = get_cases_by_status("Legal Review")
        
        if ready_cases:
            show_enhanced_cases_ready_for_closure(ready_cases, current_user)
        else:
            st.info("📭 No cases ready for closure at this time")
    
    with tab2:
        st.subheader("Closed Cases")
        closed_cases = get_cases_by_status("Closed")
        
        from simple_case_display import show_simple_case_list
        show_simple_case_list(closed_cases, current_user, "default")
    
    with tab3:
        st.subheader("Closure Analytics")
        show_closure_analytics()

def show_closure_case_details(case, current_user):
    """Display case details for closure workflow using standardized format"""
    from case_display_utils import show_standardized_case_details, show_standardized_customer_info, show_standardized_case_history, show_standardized_documents
    
    # Display standardized case details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_standardized_case_details(case)
        show_standardized_customer_info(case)
    
    with col2:
        show_standardized_case_history(case['case_id'])
        show_standardized_documents(case['case_id'])
    
    # Enhanced Actioner Actions with Sequential Workflow
    st.markdown("### 🧑‍💼 Actioner Actions")
    
    # Step 1: Action Type Selection (Required First)
    action_type = st.selectbox(
        "Select Action Type (Required First):",
        ["", "Recovery Closure", "Settlement Closure", "Write-off", "Transfer to Legal", "No Action Required"],
        key=f"action_type_{case['case_id']}"
    )
    
    # Only show subsequent fields after action type is selected
    if action_type:
        st.success(f"✅ Selected: {action_type}")
        
        # Step 2: Show relevant sub-fields based on action type
        if action_type == "Recovery Closure":
            show_recovery_closure_fields(case, current_user)
        elif action_type == "Settlement Closure":
            show_settlement_closure_fields(case, current_user)
        elif action_type == "Write-off":
            show_writeoff_fields(case, current_user)
        elif action_type == "Transfer to Legal":
            show_transfer_legal_fields(case, current_user)
        elif action_type == "No Action Required":
            show_no_action_fields(case, current_user)
        
        # Show common action fields
        show_common_actioner_fields(case, current_user, action_type)
    else:
        st.info("⚠️ Please select an Action Type first to proceed with actioner workflow")

def show_recovery_closure_fields(case, current_user):
    """Show fields specific to recovery closure"""
    st.markdown("#### 💰 Recovery Closure Details")
    
    col1, col2 = st.columns(2)
    with col1:
        recovery_amount = st.number_input(
            "Recovery Amount (₹):",
            min_value=0.0,
            key=f"recovery_amount_{case['case_id']}"
        )
    
    with col2:
        recovery_method = st.selectbox(
            "Recovery Method:",
            ["Direct Payment", "Legal Settlement", "Asset Recovery", "Partial Recovery"],
            key=f"recovery_method_{case['case_id']}"
        )

def show_settlement_closure_fields(case, current_user):
    """Show fields specific to settlement closure"""
    st.markdown("#### 🤝 Settlement Details")
    
    col1, col2 = st.columns(2)
    with col1:
        settlement_amount = st.number_input(
            "Settlement Amount (₹):",
            min_value=0.0,
            key=f"settlement_amount_{case['case_id']}"
        )
    
    with col2:
        settlement_terms = st.selectbox(
            "Settlement Terms:",
            ["One-time Payment", "Installment Plan", "Negotiated Settlement"],
            key=f"settlement_terms_{case['case_id']}"
        )

def show_writeoff_fields(case, current_user):
    """Show fields specific to write-off"""
    st.markdown("#### 📋 Write-off Details")
    
    writeoff_reason = st.selectbox(
        "Write-off Reason:",
        ["Uncollectable", "Customer Deceased", "Company Closed", "Legal Limitations"],
        key=f"writeoff_reason_{case['case_id']}"
    )

def show_transfer_legal_fields(case, current_user):
    """Show fields specific to legal transfer"""
    st.markdown("#### ⚖️ Legal Transfer Details")
    
    legal_reason = st.text_area(
        "Reason for Legal Transfer:",
        placeholder="Explain why this case needs legal intervention...",
        key=f"legal_reason_{case['case_id']}"
    )

def show_no_action_fields(case, current_user):
    """Show fields for no action required"""
    st.markdown("#### ✅ No Action Required")
    
    no_action_reason = st.text_area(
        "Reason for No Action:",
        placeholder="Explain why no action is required...",
        key=f"no_action_reason_{case['case_id']}"
    )

def show_common_actioner_fields(case, current_user, action_type):
    """Show common fields for all action types"""
    st.markdown("#### 📝 Action Details")
    
    action_comments = st.text_area(
        "Action Comments:",
        placeholder="Enter detailed comments about the action taken...",
        height=100,
        key=f"action_comments_{case['case_id']}"
    )
    
    # Document upload
    uploaded_files = st.file_uploader(
        "Upload Supporting Documents:",
        accept_multiple_files=True,
        type=['pdf', 'jpg', 'jpeg', 'png', 'docx'],
        key=f"action_docs_{case['case_id']}"
    )
    
    # Submit action button
    if st.button(f"📤 Submit {action_type}", key=f"submit_action_{case['case_id']}"):
        if action_comments.strip():
            # Process the actioner action
            process_actioner_action(case, current_user, action_type, action_comments, uploaded_files)
        else:
            st.error("Please add action comments before submitting")

def process_actioner_action(case, current_user, action_type, comments, files):
    """Process the actioner action"""
    case_id = case['case_id']
    
    try:
        # Update case status and add comments
        from models import update_case_status, add_case_comment
        from database import log_audit
        
        # Add action comment
        add_case_comment(case_id, f"ACTIONER ACTION: {action_type}\n{comments}", "Actioner Action", current_user)
        
        # Log audit
        log_audit(case_id, f"Actioner Action: {action_type}", comments, current_user)
        
        # Handle file uploads if any
        if files:
            # Save uploaded files
            for file in files:
                # Implementation for file saving would go here
                pass
        
        st.success(f"✅ {action_type} action submitted successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing action: {str(e)}")
        show_standardized_customer_info(case)
    
    with col2:
        show_standardized_case_history(case['case_id'])
        show_standardized_documents(case['case_id'])
    
    # Review history
    comments = get_case_comments(case['case_id'])
    if comments:
        st.write("**Review History:**")
        for comment in comments:
            comment_type = comment['comment_type'] if 'comment_type' in comment.keys() else 'Comment'
            st.write(f"**{comment['created_by']}** ({format_datetime(comment['created_at'])}) - *{comment_type}*")
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
    
    # Action Recommendations Section
    st.markdown("### 💡 Action Recommendations")
    st.markdown("---")
    
    # AI-powered action recommendations
    rec_col1, rec_col2 = st.columns([2, 1])
    with rec_col1:
        st.markdown("**Recommended Actions Based on Case Analysis:**")
        
        # Generate case-specific recommendations
        case_type = case['case_type'] if case['case_type'] else 'General'
        loan_amount = case['loan_amount'] if case['loan_amount'] else 0
        
        if 'fraud' in case_type.lower():
            st.markdown("🔍 **Fraud Case Recommendations:**")
            st.markdown("• File FIR if amount exceeds ₹50,000")
            st.markdown("• Block customer account immediately")
            st.markdown("• Coordinate with Legal for recovery proceedings")
            st.markdown("• Update credit bureau records")
        elif 'default' in case_type.lower():
            st.markdown("💰 **Default Case Recommendations:**")
            st.markdown("• Initiate recovery process through collection agency")
            st.markdown("• Consider settlement if customer shows willingness")
            st.markdown("• Legal notice for amounts above ₹1,00,000")
        else:
            st.markdown("📋 **General Case Recommendations:**")
            st.markdown("• Review case merits and supporting documents")
            st.markdown("• Consider customer profile and payment history")
            st.markdown("• Coordinate with relevant departments for resolution")
            
        if loan_amount and loan_amount > 500000:
            st.markdown("⚠️ **High Value Case:** Special approval required for closure")
    
    # Enhanced Action Recommendation Fields
    st.markdown("### 📋 Detailed Action Assessment")
    
    # Risk Assessment
    risk_col1, risk_col2 = st.columns(2)
    with risk_col1:
        risk_level = st.selectbox("Risk Level Assessment", 
            ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"],
            key=f"risk_level_{case['case_id']}")
        
        recovery_potential = st.selectbox("Recovery Potential",
            ["High (>80%)", "Medium (50-80%)", "Low (20-50%)", "Negligible (<20%)"],
            key=f"recovery_potential_{case['case_id']}")
    
    with risk_col2:
        customer_cooperation = st.selectbox("Customer Cooperation Level",
            ["Fully Cooperative", "Partially Cooperative", "Non-Cooperative", "Hostile"],
            key=f"customer_coop_{case['case_id']}")
        
        legal_complexity = st.selectbox("Legal Complexity",
            ["Simple", "Moderate", "Complex", "Highly Complex"],
            key=f"legal_complexity_{case['case_id']}")
    
    # Action Timeline
    st.markdown("**📅 Recommended Timeline:**")
    timeline_col1, timeline_col2 = st.columns(2)
    with timeline_col1:
        immediate_action = st.text_area("Immediate Actions (Next 7 days)",
            placeholder="List immediate actions required...",
            height=60, key=f"immediate_action_{case['case_id']}")
    
    with timeline_col2:
        followup_action = st.text_area("Follow-up Actions (Next 30 days)",
            placeholder="List follow-up actions...",
            height=60, key=f"followup_action_{case['case_id']}")
    
    # Expected Outcome
    outcome_col1, outcome_col2 = st.columns(2)
    with outcome_col1:
        expected_recovery = st.number_input("Expected Recovery Amount (₹)",
            min_value=0, value=0, key=f"expected_recovery_{case['case_id']}")
    
    with outcome_col2:
        closure_timeline = st.selectbox("Expected Closure Timeline",
            ["Within 1 month", "1-3 months", "3-6 months", "6-12 months", "More than 1 year"],
            key=f"closure_timeline_{case['case_id']}")
    
    with rec_col2:
        if st.button("🤖 Generate AI Recommendations", key=f"ai_rec_{case['case_id']}"):
            st.info("AI recommendations would be generated here using case analysis")
    
    st.markdown("---")
    
    # Closure actions
    st.markdown("### 🔒 Actioner Closure Actions")
    st.info("💡 This case is available for closure action while Legal Review runs in parallel")
    
    closure_reason = st.selectbox(
        "Closure Reason",
        [
            "Case Resolved Successfully",
            "Recovery Completed",
            "Settlement Reached",
            "Legal Action Completed",
            "Customer Satisfied",
            "No Further Action Required",
            "Transferred to Other Department",
            "Duplicate Case",
            "Other"
        ],
        key=f"closure_reason_{case['case_id']}"
    )
    
    if closure_reason == "Other":
        other_reason = st.text_input(
            "Specify Other Reason",
            key=f"other_closure_{case['case_id']}"
        )
    
    # Closure comments with AI suggestions
    st.markdown("**Closure Comments**")
    col_clos1, col_clos2 = st.columns([3, 1])
    with col_clos2:
        if st.button("💡 Quick Remarks", key=f"closure_sugg_{case['case_id']}"):
            from ai_suggestions import get_remarks_suggestions
            suggestions = get_remarks_suggestions()["closure_stage"]
            st.session_state[f"closure_suggestions_{case['case_id']}"] = suggestions
    
    # Show suggestions
    if f"closure_suggestions_{case['case_id']}" in st.session_state:
        st.markdown("**Quick Remarks:**")
        closure_cols = st.columns(2)
        for i, suggestion in enumerate(st.session_state[f"closure_suggestions_{case['case_id']}"][:4]):
            col_idx = i % 2
            with closure_cols[col_idx]:
                if st.button(f"📝 {suggestion[:30]}...", key=f"clos_sugg_{case['case_id']}_{i}", help=suggestion):
                    st.session_state[f"selected_closure_{case['case_id']}"] = suggestion
                    st.rerun()
    
    initial_closure = st.session_state.get(f"selected_closure_{case['case_id']}", "")
    closure_comments = st.text_area("Closure Comments",
        value=initial_closure,
        key=f"closure_comment_{case['case_id']}",
        placeholder="Enter detailed closure comments, actions taken, and final resolution or use quick remarks above...",
        height=80
    )
    
    # Additional closure details
    col1, col2 = st.columns(2)
    
    with col1:
        recovery_amount = st.number_input(
            "Recovery Amount (if applicable)",
            min_value=0.0,
            key=f"recovery_{case['case_id']}"
        )
    
    with col2:
        follow_up_required = st.checkbox(
            "Follow-up Required",
            key=f"followup_{case['case_id']}"
        )
    
    if follow_up_required:
        follow_up_date = st.date_input(
            "Follow-up Date",
            key=f"followup_date_{case['case_id']}"
        )
        follow_up_notes = st.text_area(
            "Follow-up Notes",
            key=f"followup_notes_{case['case_id']}"
        )
    else:
        follow_up_date = None
        follow_up_notes = ""
    
    # Closure buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"🔒 Close Case", key=f"close_{case['case_id']}"):
            if closure_comments.strip():
                final_comment = f"CASE CLOSED - Reason: {closure_reason}\n\nDetails: {closure_comments}"
                
                if recovery_amount > 0:
                    final_comment += f"\n\nRecovery Amount: ₹{recovery_amount:,.2f}"
                
                if follow_up_required:
                    final_comment += f"\n\nFollow-up Required: Yes (Date: {follow_up_date})\nNotes: {follow_up_notes}"
                
                if update_case_status(case['case_id'], "Closed", current_user, final_comment):
                    st.success("✅ Case closed successfully")
                    st.rerun()
            else:
                st.warning("Please add closure comments")
    
    with col2:
        if st.button(f"🔙 Send Back", key=f"send_back_closure_{case['case_id']}"):
            if closure_comments.strip():
                comment_text = f"SENT BACK FROM CLOSURE: {closure_comments}"
                if update_case_status(case['case_id'], "Under Review", current_user, comment_text):
                    st.success("✅ Case sent back for review")
                    st.rerun()
            else:
                st.warning("Please specify reason for sending back")
    
    with col3:
        if st.button(f"📝 Add Note", key=f"add_note_closure_{case['case_id']}"):
            if closure_comments.strip():
                add_case_comment(case['case_id'], closure_comments, "Closure Note", current_user)
                st.success("✅ Note added")
                st.rerun()
            else:
                st.warning("Please enter a note")

def show_closed_case_details(case):
    """Display read-only details for closed cases"""
    
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
        st.write(f"**Closed By:** {case['closed_by'] or 'N/A'}")
        st.write(f"**Closed At:** {format_datetime(case['closed_at'])}")
        st.write(f"**Created By:** {case['created_by']}")
        st.write(f"**Case Date:** {case['case_date']}")
    
    # Case description
    st.write("**Case Description:**")
    st.write(case['case_description'])
    
    # Comments history (including closure reason)
    comments = get_case_comments(case['case_id'])
    if comments:
        st.write("**Complete History:**")
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

def show_closure_analytics():
    """Display closure analytics and statistics"""
    
    st.write("### Closure Performance Metrics")
    
    # Sample metrics - in real implementation, these would come from database queries
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cases Closed This Month", "45")
    
    with col2:
        st.metric("Average Closure Time", "12.5 days")
    
    with col3:
        st.metric("Total Recovery Amount", "₹2.5M")
    
    with col4:
        st.metric("Follow-up Cases", "8")
    
    st.divider()
    
    # Closure reasons chart
    st.write("### Closure Reasons Distribution")
    
    # Sample data - replace with actual database query
    closure_reasons = {
        "Case Resolved Successfully": 25,
        "Recovery Completed": 15,
        "Settlement Reached": 10,
        "Legal Action Completed": 8,
        "No Further Action Required": 5,
        "Other": 3
    }
    
    import plotly.express as px
    
    fig = px.pie(
        values=list(closure_reasons.values()),
        names=list(closure_reasons.keys()),
        title="Case Closure Reasons"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly closure trend
    st.write("### Monthly Closure Trend")
    
    # Sample trend data
    import pandas as pd
    from datetime import datetime, timedelta
    
    dates = pd.date_range(start=datetime.now() - timedelta(days=180), end=datetime.now(), freq='ME')
    closures = [30, 35, 28, 42, 38, 45]  # Sample data
    
    trend_data = pd.DataFrame({
        'Month': dates,
        'Closures': closures
    })
    
    fig = px.line(trend_data, x='Month', y='Closures', title='Monthly Case Closures')
    st.plotly_chart(fig, use_container_width=True)
    
    # Export options
    st.write("### Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Closure Report"):
            st.info("Closure report export functionality")
    
    with col2:
        if st.button("📈 Generate Analytics Dashboard"):
            st.info("Advanced analytics dashboard")

def show_enhanced_cases_ready_for_closure(cases, current_user):
    """Display cases ready for closure in simple presentable format with clickable Case IDs"""
    
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
    
    # Header for the cases list
    st.markdown("**Cases Available for Closure** *(Click on Case ID to expand and view full details including investigation reports)*")
    st.markdown("---")
    
    # Display each case in simple numbered format
    for i, case in enumerate(cases, 1):
        case_id = safe_get(case, 'case_id', 'N/A')
        customer_name = safe_get(case, 'customer_name', 'N/A')
        case_type = safe_get(case, 'case_type', 'N/A')
        product = safe_get(case, 'product', 'N/A')
        region = safe_get(case, 'region', 'N/A')
        status = safe_get(case, 'status', 'N/A')
        loan_amount = safe_get(case, 'loan_amount', 0)
        branch = safe_get(case, 'branch_location', 'N/A')
        case_date = safe_get(case, 'case_date', 'N/A')
        
        # Format loan amount
        amount_display = f"₹{loan_amount:,}" if isinstance(loan_amount, (int, float)) and loan_amount > 0 else str(loan_amount)
        
        # Display case in simple presentable format with all required headers
        st.write(f"{i}. **Case ID:** {case_id}, **Customer:** {customer_name}, **Type:** {case_type}, **Product:** {product}, **Region:** {region}, **Status:** {status}, **Amount:** {amount_display}, **Branch:** {branch}, **Date:** {case_date}")
        
        # Clickable Case ID using expander for full details
        with st.expander(f"🔍 View Full Details - {case_id}", expanded=False):
            show_complete_case_details_with_investigation(case, current_user)

def show_complete_case_details_with_investigation(case, current_user):
    """Show complete case details with comprehensive investigation details and reports"""
    
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
    
    # Basic Case Information
    st.markdown("#### 📄 Case Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Case Identification**")
        st.write(f"Case ID: {safe_get(case, 'case_id')}")
        st.write(f"LAN: {safe_get(case, 'lan')}")
        st.write(f"Case Type: {safe_get(case, 'case_type')}")
        
    with col2:
        st.markdown("**Customer Information**")
        st.write(f"Customer: {safe_get(case, 'customer_name')}")
        st.write(f"Mobile: {safe_get(case, 'customer_mobile')}")
        st.write(f"Email: {safe_get(case, 'customer_email')}")
        
    with col3:
        st.markdown("**Financial Details**")
        st.write(f"Product: {safe_get(case, 'product')}")
        loan_amt = safe_get(case, 'loan_amount', 0)
        amount_display = f"₹{loan_amt:,}" if isinstance(loan_amt, (int, float)) and loan_amt > 0 else str(loan_amt)
        st.write(f"Amount: {amount_display}")
        st.write(f"Branch: {safe_get(case, 'branch_location')}")
    
    # Customer Demographic Details Section
    st.markdown("---")
    st.markdown("#### 👤 Customer Demographic Details")
    show_customer_demographic_details(case)
    
    # Investigation Details
    st.markdown("---")
    st.markdown("#### 🔍 Investigation Details")
    show_comprehensive_investigation_details(case_id)
    
    # Investigation Report
    st.markdown("#### 📋 Investigation Reports")
    show_investigation_reports_with_download(case_id)
    
    # Show Cause Notice Section
    st.markdown("---")
    st.markdown("#### 📄 Show Cause Notice (SCN) Generation")
    show_cause_notice_section(case, current_user)
    
    # Communication Template Section
    st.markdown("---")
    st.markdown("#### 📝 Select Actionable Communication Template")
    st.write("Please choose the appropriate pre-filled message template based on the team you're addressing:")
    
    show_communication_template_selector(case_id, current_user)

def show_investigation_details(case_id):
    """Show investigation details from investigation stage"""
    try:
        from database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM investigation_details 
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
                
                st.write(f"**Investigation Type:** {safe_get_inv(investigation, 'investigation_type', 'N/A')}")
                st.write(f"**Risk Level:** {safe_get_inv(investigation, 'risk_level', 'N/A')}")
                st.write(f"**Investigation Status:** {safe_get_inv(investigation, 'status', 'N/A')}")
                st.write(f"**Findings:** {safe_get_inv(investigation, 'findings', 'N/A')}")
                st.write(f"**Recommendations:** {safe_get_inv(investigation, 'recommendations', 'N/A')}")
                st.write(f"**Investigator:** {safe_get_inv(investigation, 'investigator_name', 'N/A')}")
                st.write(f"**Investigation Date:** {safe_get_inv(investigation, 'created_at', 'N/A')}")
            else:
                st.info("No investigation details found for this case")
                
    except Exception as e:
        st.error(f"Error loading investigation details: {str(e)}")

def show_investigation_report(case_id):
    """Show investigation report if available"""
    try:
        from database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT filename, file_path, uploaded_at
                FROM case_documents 
                WHERE case_id = ? AND (filename LIKE '%investigation%report%' OR filename LIKE '%Investigation%Report%')
                ORDER BY uploaded_at DESC
                LIMIT 1
            """, (case_id,))
            
            report = cursor.fetchone()
            
            if report:
                def safe_get_rep(obj, key, default='N/A'):
                    try:
                        if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
                            return obj[key] if key in obj.keys() and obj[key] is not None else default
                        elif hasattr(obj, 'get'):
                            return obj.get(key, default)
                        else:
                            return getattr(obj, key, default)
                    except (KeyError, AttributeError, TypeError):
                        return default
                
                st.write(f"**Report:** {safe_get_rep(report, 'filename', 'N/A')}")
                st.write(f"**Generated:** {safe_get_rep(report, 'uploaded_at', 'N/A')}")
                
                # Create download button for the report
                if st.button(f"📥 Download Investigation Report", key=f"download_report_{case_id}"):
                    st.success("Investigation report download initiated")
                    
                # Show report preview if it's a PDF
                with st.expander("📖 Report Preview"):
                    st.info("Investigation report preview would be displayed here")
            else:
                st.info("No investigation report found for this case")
                
    except Exception as e:
        st.error(f"Error loading investigation report: {str(e)}")

def show_communication_template_selector(case_id, current_user):
    """Show communication template selector with predefined options"""
    
    # Communication template options
    template_options = {
        "": "Select a team...",
        "Legal Team (Non-Litigation)": "Dear Legal Team (Non-Litigation),\nPlease file a Police Complaint against the involved party.",
        "Collections Team": "Dear Collections Team,\nPlease do the needful as appropriate.",
        "Compliance Team": "Dear Compliance Team,\nPlease do the needful as appropriate.",
        "FRMU Team": "Dear FRMU Team,\nPlease do the FMR Reporting to RBI.",
        "ORM / Policy Team": "Dear ORM / Policy,\nPlease do the necessary provisioning.",
        "Information Technology Team": "Dear Information Technology Team,\nPlease tag/change the risk categorisation of said loan account as \"HIGH RISK\" in System.",
        "Hunter Team": "Dear Hunter Team,\nBasis the investigation findings, please upload negative remarks in Hunter System.",
        "Audit Team": "Dear Audit Team,\nPlease initiate a review of this account under exceptional transaction monitoring.",
        "Product Team": "Dear Product Team,\nPlease re-evaluate the product rules or features associated with this case.",
        "Operations Team": "Dear Operations Team,\nPlease restrict any further disbursements or benefits on the said account.",
        "Credit Team": "Dear Credit Team,\nPlease revisit the credit underwriting and risk profiling criteria used in this case.",
        "HR/Training Team": "Dear HR/Training Team,\nPlease conduct a refresher or sensitization session for the involved staff.",
        "Legal Team (Litigation)": "Dear Legal Team (Litigation),\nPlease initiate civil/criminal litigation proceedings based on the current findings.",
        "Risk Analytics Team": "Dear Risk Analytics Team,\nPlease include this case in trend analysis and update the fraud typology repository."
    }
    
    # Template selection dropdown
    selected_template = st.selectbox(
        "Select Communication Template:",
        list(template_options.keys()),
        key=f"comm_template_{case_id}"
    )
    
    if selected_template and selected_template != "":
        # Show selected template
        st.markdown("**Selected Template:**")
        template_text = st.text_area(
            "Template Message:",
            value=template_options[selected_template],
            height=100,
            key=f"template_text_{case_id}"
        )
        
        # Additional instructions
        st.markdown("**Additional Instructions (Optional):**")
        additional_instructions = st.text_area(
            "Case-specific or custom comments:",
            placeholder="Add any case-specific comments or additional instructions here...",
            height=80,
            key=f"additional_instructions_{case_id}"
        )
        
        # Send button
        if st.button("📤 Send Communication", key=f"send_comm_{case_id}"):
            try:
                # Combine template and additional instructions
                full_message = template_text
                if additional_instructions.strip():
                    full_message += f"\n\nAdditional Instructions:\n{additional_instructions}"
                
                # Add comment to case
                from models import add_case_comment
                comment_text = f"COMMUNICATION SENT TO {selected_template}: {full_message}"
                
                if add_case_comment(case_id, comment_text, current_user, "Communication Sent"):
                    from error_handler import success_message
                    success_message("Communication Sent", f"Message sent to {selected_template}")
                    st.rerun()
                    
            except Exception as e:
                from error_handler import handle_database_error
                handle_database_error("communication sending", e)

def show_customer_demographic_details(case):
    """Show comprehensive customer demographic details in full-screen format"""
    
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
    
    # Create professional demographic display with full-screen layout
    st.markdown("""
    <style>
    .demographic-container {
        background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
        border: 1px solid #e3e6ff;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        width: 100%;
    }
    .demographic-section {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #0066cc;
    }
    .demographic-field {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
        align-items: center;
    }
    .field-label {
        font-weight: bold;
        color: #333;
        min-width: 180px;
        font-size: 14px;
    }
    .field-value {
        color: #666;
        text-align: right;
        flex: 1;
        font-size: 14px;
        word-break: break-word;
    }
    .section-header {
        font-size: 18px;
        font-weight: bold;
        color: #0066cc;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e3e6ff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    case_id = safe_get(case, 'case_id', 'N/A')
    
    st.markdown('<div class="demographic-container">', unsafe_allow_html=True)
    
    # Case Overview Section (Full Width)
    st.markdown('<div class="demographic-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Case Overview</div>', unsafe_allow_html=True)
    
    # Create comprehensive case overview table
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Case ID:</span><span class="field-value">{case_id}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Type:</span><span class="field-value">{safe_get(case, "case_type")}</span></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Product:</span><span class="field-value">{safe_get(case, "product")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Region:</span><span class="field-value">{safe_get(case, "region")}</span></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Status:</span><span class="field-value">{safe_get(case, "status")}</span></div>', unsafe_allow_html=True)
        loan_amt = safe_get(case, "loan_amount", 0)
        amount_str = f"₹{loan_amt:,}" if isinstance(loan_amt, (int, float)) and loan_amt > 0 else str(loan_amt)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Amount:</span><span class="field-value">{amount_str}</span></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Branch:</span><span class="field-value">{safe_get(case, "branch_location")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Date:</span><span class="field-value">{safe_get(case, "case_date")}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Customer Identity Section
    st.markdown('<div class="demographic-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">👤 Customer Identity & Personal Details</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Full Name:</span><span class="field-value">{safe_get(case, "customer_name")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Date of Birth:</span><span class="field-value">{safe_get(case, "customer_dob")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">PAN Number:</span><span class="field-value">{safe_get(case, "customer_pan")}</span></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Aadhaar Number:</span><span class="field-value">{safe_get(case, "customer_aadhaar")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Relationship Status:</span><span class="field-value">{safe_get(case, "customer_relationship_status")}</span></div>', unsafe_allow_html=True)
        cibil_score = safe_get(case, "customer_cibil_score", 0)
        cibil_str = str(cibil_score) if isinstance(cibil_score, (int, float)) and cibil_score > 0 else "N/A"
        st.markdown(f'<div class="demographic-field"><span class="field-label">CIBIL Score:</span><span class="field-value">{cibil_str}</span></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Occupation:</span><span class="field-value">{safe_get(case, "customer_occupation")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Income Range:</span><span class="field-value">{safe_get(case, "customer_income")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">LAN:</span><span class="field-value">{safe_get(case, "lan")}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Contact & Address Section
    st.markdown('<div class="demographic-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📞 Contact Information & Address</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Mobile Number:</span><span class="field-value">{safe_get(case, "customer_mobile")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Email Address:</span><span class="field-value">{safe_get(case, "customer_email")}</span></div>', unsafe_allow_html=True)
    
    with col2:
        address_text = safe_get(case, "customer_address_full", "N/A")
        # Truncate long addresses for display
        display_address = (address_text[:50] + "...") if len(address_text) > 50 else address_text
        st.markdown(f'<div class="demographic-field"><span class="field-label">Complete Address:</span><span class="field-value" title="{address_text}">{display_address}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Branch Location:</span><span class="field-value">{safe_get(case, "branch_location")}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Financial & Loan Details Section
    st.markdown('<div class="demographic-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">💰 Financial & Loan Details</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        loan_amt = safe_get(case, "loan_amount", 0)
        amount_display = f"₹{loan_amt:,}" if isinstance(loan_amt, (int, float)) and loan_amt > 0 else str(loan_amt)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Loan Amount:</span><span class="field-value">{amount_display}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Product Type:</span><span class="field-value">{safe_get(case, "product")}</span></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Disbursement Date:</span><span class="field-value">{safe_get(case, "disbursement_date")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Region:</span><span class="field-value">{safe_get(case, "region")}</span></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="demographic-field"><span class="field-label">Current Status:</span><span class="field-value">{safe_get(case, "status")}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="demographic-field"><span class="field-label">Created Date:</span><span class="field-value">{safe_get(case, "case_date")}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_comprehensive_investigation_details(case_id):
    """Show comprehensive investigation details from investigation stage"""
    try:
        from database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get investigation details
            cursor.execute("""
                SELECT * FROM investigation_details 
                WHERE case_id = ?
                ORDER BY created_at DESC
            """, (case_id,))
            
            investigations = cursor.fetchall()
            
            # Get case comments related to investigation
            cursor.execute("""
                SELECT * FROM case_comments 
                WHERE case_id = ? AND (comment_type LIKE '%Investigation%' OR comment_type LIKE '%investigation%')
                ORDER BY created_at DESC
            """, (case_id,))
            
            investigation_comments = cursor.fetchall()
            
            if investigations or investigation_comments:
                # Investigation Details
                if investigations:
                    st.markdown("**Investigation Analysis:**")
                    for investigation in investigations:
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
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"• **Investigation Type:** {safe_get_inv(investigation, 'investigation_type', 'N/A')}")
                            st.write(f"• **Risk Level:** {safe_get_inv(investigation, 'risk_level', 'N/A')}")
                            st.write(f"• **Status:** {safe_get_inv(investigation, 'status', 'N/A')}")
                            st.write(f"• **Investigator:** {safe_get_inv(investigation, 'investigator_name', 'N/A')}")
                        
                        with col2:
                            st.write(f"• **Investigation Date:** {safe_get_inv(investigation, 'created_at', 'N/A')}")
                            findings = safe_get_inv(investigation, 'findings', 'N/A')
                            st.write(f"• **Key Findings:** {findings[:100]}..." if len(findings) > 100 else f"• **Key Findings:** {findings}")
                        
                        recommendations = safe_get_inv(investigation, 'recommendations', 'N/A')
                        st.write(f"• **Recommendations:** {recommendations}")
                        st.markdown("---")
                
                # Investigation Comments
                if investigation_comments:
                    st.markdown("**Investigation Comments & Updates:**")
                    for comment in investigation_comments[:3]:  # Show latest 3 comments
                        def safe_get_comment(obj, key, default='N/A'):
                            try:
                                if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
                                    return obj[key] if key in obj.keys() and obj[key] is not None else default
                                elif hasattr(obj, 'get'):
                                    return obj.get(key, default)
                                else:
                                    return getattr(obj, key, default)
                            except (KeyError, AttributeError, TypeError):
                                return default
                        
                        comment_text = safe_get_comment(comment, 'comment', 'N/A')
                        comment_type = safe_get_comment(comment, 'comment_type', 'N/A')
                        created_by = safe_get_comment(comment, 'created_by', 'N/A')
                        created_at = safe_get_comment(comment, 'created_at', 'N/A')
                        
                        st.write(f"• **{comment_type}** by {created_by} on {created_at}")
                        st.write(f"  {comment_text}")
                        st.markdown("")
            else:
                st.info("No detailed investigation information found for this case")
                
    except Exception as e:
        st.error(f"Error loading investigation details: {str(e)}")

def show_investigation_reports_with_download(case_id):
    """Show investigation reports with download functionality"""
    try:
        from database import get_db_connection
        import os
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get investigation reports and related documents
            cursor.execute("""
                SELECT filename, file_path, uploaded_at, uploaded_by, file_size
                FROM documents 
                WHERE case_id = ? AND (
                    filename LIKE '%investigation%' OR 
                    filename LIKE '%Investigation%' OR
                    filename LIKE '%report%' OR
                    filename LIKE '%Report%' OR
                    filename LIKE '%evidence%' OR
                    filename LIKE '%Evidence%'
                )
                ORDER BY uploaded_at DESC
            """, (case_id,))
            
            reports = cursor.fetchall()
            
            if reports:
                st.markdown("**Available Investigation Reports & Documents:**")
                
                for i, report in enumerate(reports, 1):
                    def safe_get_report(obj, key, default='N/A'):
                        try:
                            if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
                                return obj[key] if key in obj.keys() and obj[key] is not None else default
                            elif hasattr(obj, 'get'):
                                return obj.get(key, default)
                            else:
                                return getattr(obj, key, default)
                        except (KeyError, AttributeError, TypeError):
                            return default
                    
                    filename = safe_get_report(report, 'filename', 'N/A')
                    file_path = safe_get_report(report, 'file_path', 'N/A')
                    uploaded_at = safe_get_report(report, 'uploaded_at', 'N/A')
                    uploaded_by = safe_get_report(report, 'uploaded_by', 'N/A')
                    file_size = safe_get_report(report, 'file_size', 0)
                    
                    # Format file size
                    if isinstance(file_size, (int, float)) and file_size > 0:
                        size_str = f"{file_size/1024:.1f} KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f} MB"
                    else:
                        size_str = "Unknown size"
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"{i}. **{filename}**")
                        st.write(f"   Uploaded by: {uploaded_by} on {uploaded_at}")
                        st.write(f"   Size: {size_str}")
                    
                    with col2:
                        # Check if file exists
                        if file_path != 'N/A' and os.path.exists(file_path):
                            try:
                                with open(file_path, 'rb') as file:
                                    file_data = file.read()
                                st.download_button(
                                    label="📥 Download",
                                    data=file_data,
                                    file_name=filename,
                                    mime="application/octet-stream",
                                    key=f"download_report_{case_id}_{i}"
                                )
                            except Exception as e:
                                st.write("❌ File not accessible")
                        else:
                            st.write("❌ File not found")
                    
                    st.markdown("")
            else:
                st.info("No investigation reports found for this case. Reports may have been uploaded during the investigation stage.")
                
    except Exception as e:
        st.error(f"Error loading investigation reports: {str(e)}")

def show_cause_notice_section(case, current_user):
    """Show comprehensive Show Cause Notice generation with AI assistance"""
    
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
    
    st.write("Generate Show Cause Notice based on customer information and investigation findings:")
    
    # SCN Type Selection
    scn_type = st.selectbox(
        "Select SCN Type:",
        ["Show Cause Notice (SCN)", "Reasoned Order", "Legal Opinion", "Recovery Notice"],
        key=f"scn_type_{case_id}"
    )
    
    # AI Draft Generation Section
    st.markdown("#### 🤖 AI-Powered SCN Draft Generation")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("✨ Generate AI Draft", key=f"ai_scn_draft_{case_id}"):
            ai_draft = generate_ai_scn_draft(case, scn_type)
            st.session_state[f"scn_draft_{case_id}"] = ai_draft
            st.session_state[f"scn_content_{case_id}"] = ai_draft
    
    # Show AI generated draft if available
    if f"scn_draft_{case_id}" in st.session_state:
        st.markdown("**🤖 AI Generated Draft:**")
        with st.expander("View AI Draft", expanded=True):
            st.text_area(
                "AI Generated Content:",
                value=st.session_state[f"scn_draft_{case_id}"],
                height=200,
                key=f"ai_draft_display_{case_id}",
                disabled=True
            )
            
            col_ai1, col_ai2, col_ai3 = st.columns(3)
            with col_ai1:
                if st.button("✅ Accept Draft", key=f"accept_draft_{case_id}"):
                    st.session_state[f"scn_content_{case_id}"] = st.session_state[f"scn_draft_{case_id}"]
                    st.success("AI draft accepted and loaded for editing")
                    st.rerun()
            
            with col_ai2:
                if st.button("🔄 Regenerate", key=f"regen_draft_{case_id}"):
                    new_draft = generate_ai_scn_draft(case, scn_type)
                    st.session_state[f"scn_draft_{case_id}"] = new_draft
                    st.success("New AI draft generated")
                    st.rerun()
            
            with col_ai3:
                if st.button("📝 Edit Manually", key=f"edit_manual_{case_id}"):
                    st.session_state[f"scn_content_{case_id}"] = st.session_state[f"scn_draft_{case_id}"]
                    st.info("Draft loaded for manual editing below")
                    st.rerun()
    
    # Manual SCN Content Editor
    st.markdown("#### 📝 SCN Content Editor")
    
    initial_content = st.session_state.get(f"scn_content_{case_id}", "")
    scn_content = st.text_area(
        "SCN Content:",
        value=initial_content,
        height=300,
        key=f"scn_editor_{case_id}",
        placeholder="Enter Show Cause Notice content or use AI generation above..."
    )
    
    # SCN Details
    col_det1, col_det2 = st.columns(2)
    
    with col_det1:
        scn_grounds = st.text_area(
            "Legal Grounds:",
            placeholder="Enter legal grounds for issuing SCN...",
            height=80,
            key=f"scn_grounds_{case_id}"
        )
        
        response_deadline = st.date_input(
            "Response Deadline:",
            key=f"scn_deadline_{case_id}"
        )
    
    with col_det2:
        violations = st.text_area(
            "Specific Violations:",
            placeholder="List specific violations or issues identified...",
            height=80,
            key=f"scn_violations_{case_id}"
        )
        
        scn_instructions = st.text_area(
            "Special Instructions:",
            placeholder="Any special instructions or requirements...",
            height=60,
            key=f"scn_instructions_{case_id}"
        )
    
    # Action Buttons
    st.markdown("#### 📤 SCN Actions")
    
    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
    
    with col_act1:
        if st.button("📋 Preview SCN", key=f"preview_scn_{case_id}"):
            if scn_content.strip():
                preview_scn_document(case, scn_content, scn_grounds, violations, response_deadline, scn_instructions, scn_type)
            else:
                st.warning("Please enter SCN content first")
    
    with col_act2:
        if st.button("💾 Save Draft", key=f"save_scn_draft_{case_id}"):
            if scn_content.strip():
                save_scn_draft(case_id, scn_content, scn_grounds, violations, response_deadline, scn_instructions, scn_type, current_user)
            else:
                st.warning("Please enter SCN content first")
    
    with col_act3:
        if st.button("📤 Issue SCN", key=f"issue_scn_{case_id}"):
            if scn_content.strip() and scn_grounds.strip():
                issue_show_cause_notice(case, scn_content, scn_grounds, violations, response_deadline, scn_instructions, scn_type, current_user)
            else:
                st.warning("Please enter SCN content and legal grounds")
    
    with col_act4:
        if st.button("📄 Generate PDF", key=f"pdf_scn_{case_id}"):
            if scn_content.strip():
                generate_scn_pdf(case, scn_content, scn_grounds, violations, response_deadline, scn_instructions, scn_type)
            else:
                st.warning("Please enter SCN content first")

def generate_ai_scn_draft(case, scn_type):
    """Generate AI-powered SCN draft based on case and investigation information"""
    
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
    
    try:
        from datetime import datetime
        
        # Extract case information
        case_id = safe_get(case, 'case_id')
        customer_name = safe_get(case, 'customer_name')
        lan = safe_get(case, 'lan')
        loan_amount = safe_get(case, 'loan_amount', 0)
        case_type = safe_get(case, 'case_type')
        case_description = safe_get(case, 'case_description')
        product = safe_get(case, 'product')
        branch = safe_get(case, 'branch_location')
        
        # Get investigation details if available  
        investigation_details = get_investigation_details_for_scn(case_id)
        
        # Create comprehensive AI prompt
        ai_prompt = f"""Generate a professional {scn_type} document based on the following case information:

Case Details:
- Case ID: {case_id}
- Customer Name: {customer_name}
- LAN: {lan}
- Loan Amount: ₹{loan_amount:,}
- Case Type: {case_type}
- Product: {product}
- Branch: {branch}
- Case Description: {case_description}

Investigation Findings:
{investigation_details}

Please generate a comprehensive, legally sound {scn_type} that includes:
1. Proper legal formatting and structure
2. Specific references to violations or issues
3. Clear grounds for the notice
4. Professional tone and language
5. Appropriate legal citations where applicable
6. Clear instructions for response

The document should be detailed, professional, and based on the case facts provided."""

        # Use AI to generate the draft
        try:
            import os
            from google import genai
            
            # Check if Gemini API key is available
            if os.environ.get("GEMINI_API_KEY"):
                client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=ai_prompt
                )
                
                if response.text:
                    return response.text
                else:
                    return generate_template_scn_draft(case, scn_type)
            else:
                return generate_template_scn_draft(case, scn_type)
                
        except Exception as e:
            st.error(f"AI generation failed: {str(e)}")
            return generate_template_scn_draft(case, scn_type)
            
    except Exception as e:
        st.error(f"Error generating AI draft: {str(e)}")
        return generate_template_scn_draft(case, scn_type)

def generate_template_scn_draft(case, scn_type):
    """Generate template-based SCN draft as fallback"""
    
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
    
    from datetime import datetime
    
    # Extract case information with safe access
    case_id = safe_get(case, 'case_id')
    customer_name = safe_get(case, 'customer_name')
    lan = safe_get(case, 'lan')
    loan_amount = safe_get(case, 'loan_amount', 0)
    case_type = safe_get(case, 'case_type')
    case_description = safe_get(case, 'case_description')
    product = safe_get(case, 'product')
    branch = safe_get(case, 'branch_location')
    customer_pan = safe_get(case, 'pan', 'N/A')
    customer_mobile = safe_get(case, 'mobile_number', 'N/A')
    customer_email = safe_get(case, 'email_id', 'N/A')
    disbursement_date = safe_get(case, 'disbursement_date', 'N/A')
    
    if scn_type == "Show Cause Notice (SCN)":
        return f"""**SHOW CAUSE NOTICE**

Case Reference: {case_id}
Date: {datetime.now().strftime('%B %d, %Y')}

To: {customer_name}
PAN: {customer_pan}
Mobile: {customer_mobile}
Email: {customer_email}

**SUBJECT: Show Cause Notice - Loan Account No. {lan}**

Dear {customer_name},

This notice is issued to you in connection with your loan account bearing number {lan} for ₹{loan_amount:,.2f} disbursed on {disbursement_date}.

**CASE DETAILS:**
- Case Type: {case_type}
- Product: {product}
- Branch: {branch}
- Case Description: {case_description}

**GROUNDS FOR NOTICE:**
Based on our investigation and review of your loan account, certain discrepancies and violations have been identified that require your immediate attention and response.

**SPECIFIC VIOLATIONS/ISSUES IDENTIFIED:**
1. [To be specified based on investigation findings]
2. [Additional violations as applicable]
3. [Other relevant issues]

**INVESTIGATION FINDINGS:**
[Investigation details and findings to be inserted]

You are hereby called upon to show cause within 15 days from the receipt of this notice as to why appropriate legal action should not be taken against you for the above-mentioned violations.

**REQUIRED RESPONSE:**
You are required to submit a written response addressing each of the issues raised in this notice, along with supporting documents and evidence.

Failure to respond within the stipulated time will result in appropriate legal and recovery action being initiated against you without further notice.

**Contact Information:**
For any clarifications, please contact our Legal Department at [Contact Details].

**Authorized Signatory**
Legal Department
Aditya Birla Capital Limited
Date: {datetime.now().strftime('%B %d, %Y')}"""

    elif scn_type == "Reasoned Order":
        return f"""**REASONED ORDER**

Case Reference: {case_id}
Order Date: {datetime.now().strftime('%B %d, %Y')}

In the matter of: {customer_name} (PAN: {customer_pan})
Loan Account No.: {lan}

**BACKGROUND:**
This order is passed in connection with the loan account of {customer_name} for ₹{loan_amount:,.2f} under {product} product.

**CASE DETAILS:**
- Case Type: {case_type}
- Branch: {branch}
- Case Description: {case_description}

**FINDINGS:**
After careful examination of the case and investigation reports:
[Investigation findings and analysis]

**LEGAL PROVISIONS:**
[Applicable legal provisions and regulations]

**ORDER:**
Based on the findings and applicable legal provisions, it is hereby ordered that:
1. [Specific order/direction]
2. [Additional orders as applicable]

**COMPLIANCE:**
This order is to be complied with within [X] days from the date of receipt.

**Authorized Officer**
Legal Department
Date: {datetime.now().strftime('%B %d, %Y')}"""

    elif scn_type == "Recovery Notice":
        return f"""**RECOVERY NOTICE**

Case Reference: {case_id}
Notice Date: {datetime.now().strftime('%B %d, %Y')}

To: {customer_name}
Address: [Customer Address]
PAN: {customer_pan}

**SUBJECT: Final Notice for Recovery - Loan Account No. {lan}**

Dear {customer_name},

This final notice is served upon you for the recovery of outstanding dues under your loan account {lan} for ₹{loan_amount:,.2f}.

**OUTSTANDING DETAILS:**
- Principal Amount: ₹{loan_amount:,.2f}
- Interest and Charges: [To be calculated]
- Total Outstanding: [Total Amount]

**CASE BACKGROUND:**
{case_description}

**FINAL DEMAND:**
You are hereby required to pay the entire outstanding amount within 7 days from the receipt of this notice.

**CONSEQUENCES OF NON-PAYMENT:**
Failure to pay within the stipulated time will result in:
1. Legal action for recovery
2. Reporting to credit bureaus
3. Enforcement of security/guarantees
4. Criminal proceedings if applicable

**Contact for Payment:**
[Payment details and contact information]

**Authorized Officer**
Recovery Department
Date: {datetime.now().strftime('%B %d, %Y')}"""

    else:  # Legal Opinion
        return f"""**LEGAL OPINION**

Case Reference: {case_id}
Opinion Date: {datetime.now().strftime('%B %d, %Y')}

**MATTER:** {customer_name} - Loan Account {lan}

**CASE SUMMARY:**
This legal opinion is provided in the matter of {customer_name} regarding loan account {lan} for ₹{loan_amount:,.2f}.

**CASE DETAILS:**
- Case Type: {case_type}
- Product: {product}
- Branch: {branch}
- Description: {case_description}

**LEGAL ANALYSIS:**
[Detailed legal analysis of the case]

**APPLICABLE LAWS:**
[Relevant legal provisions and regulations]

**OPINION:**
Based on the facts and applicable legal provisions, it is our opinion that:
1. [Legal opinion point 1]
2. [Legal opinion point 2]
3. [Additional opinions as applicable]

**RECOMMENDATIONS:**
1. [Recommended course of action]
2. [Alternative recommendations]

**Prepared by:**
Legal Department
Date: {datetime.now().strftime('%B %d, %Y')}"""

def get_investigation_details_for_scn(case_id):
    """Get investigation details for SCN generation"""
    try:
        from database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT investigation_type, risk_level, status, findings, recommendations, investigator_name
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
Findings: {safe_get_inv(investigation, 'findings')}
Recommendations: {safe_get_inv(investigation, 'recommendations')}
Investigator: {safe_get_inv(investigation, 'investigator_name')}"""
            else:
                return "No investigation details available for this case."
                
    except Exception as e:
        return f"Error retrieving investigation details: {str(e)}"

def preview_scn_document(case, content, grounds, violations, deadline, instructions, scn_type):
    """Preview the SCN document"""
    st.markdown("### 📖 SCN Document Preview")
    
    with st.expander("Document Preview", expanded=True):
        st.markdown("**Document Type:** " + scn_type)
        st.markdown("**Response Deadline:** " + str(deadline))
        st.markdown("---")
        st.text_area("Complete Document:", value=content, height=400, disabled=True)
        
        if grounds:
            st.markdown("**Legal Grounds:**")
            st.text(grounds)
        
        if violations:
            st.markdown("**Violations:**")
            st.text(violations)
        
        if instructions:
            st.markdown("**Special Instructions:**")
            st.text(instructions)

def save_scn_draft(case_id, content, grounds, violations, deadline, instructions, scn_type, current_user):
    """Save SCN as draft"""
    try:
        from models import add_case_comment
        
        draft_content = f"SCN DRAFT SAVED - Type: {scn_type}\n\nContent:\n{content}\n\nLegal Grounds: {grounds}\nViolations: {violations}\nDeadline: {deadline}\nInstructions: {instructions}"
        
        if add_case_comment(case_id, draft_content, current_user, "SCN Draft"):
            from error_handler import success_message
            success_message("SCN Draft Saved", "Show Cause Notice draft has been saved successfully")
            st.rerun()
        
    except Exception as e:
        from error_handler import handle_database_error
        handle_database_error("SCN draft saving", e)

def issue_show_cause_notice(case, content, grounds, violations, deadline, instructions, scn_type, current_user):
    """Issue the Show Cause Notice officially"""
    try:
        from models import add_case_comment, update_case_status
        
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
        
        issued_content = f"SCN ISSUED - Type: {scn_type}\n\nContent:\n{content}\n\nLegal Grounds: {grounds}\nViolations: {violations}\nResponse Deadline: {deadline}\nSpecial Instructions: {instructions}\n\nStatus: OFFICIALLY ISSUED"
        
        if add_case_comment(case_id, issued_content, current_user, "SCN Issued"):
            # Update case status to Legal Review Complete after SCN issuance
            if update_case_status(case_id, "Legal Review Complete", current_user):
                from error_handler import success_message
                success_message("SCN Issued Successfully", f"{scn_type} has been officially issued with response deadline: {deadline}")
                st.rerun()
        
    except Exception as e:
        from error_handler import handle_database_error
        handle_database_error("SCN issuance", e)

def generate_scn_pdf(case, content, grounds, violations, deadline, instructions, scn_type):
    """Generate PDF version of SCN"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from datetime import datetime
        import os
        
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
        
        # Create PDF file
        filename = f"SCN_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join("uploads", filename)
        
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(scn_type, title_style))
        story.append(Spacer(1, 12))
        
        # Content
        content_paragraphs = content.split('\n')
        for para in content_paragraphs:
            if para.strip():
                story.append(Paragraph(para, styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
        from error_handler import success_message
        success_message("PDF Generated", f"SCN PDF generated successfully: {filename}")
        
        # Provide download link
        with open(filepath, "rb") as pdf_file:
            st.download_button(
                label="📥 Download SCN PDF",
                data=pdf_file.read(),
                file_name=filename,
                mime="application/pdf",
                key=f"download_scn_pdf_{case_id}"
            )
        
    except Exception as e:
        from error_handler import handle_database_error
        handle_database_error("PDF generation", e)

def show_communication_template_selector(case_id, current_user):
    """Show communication template selector for different teams"""
    
    st.write("Select appropriate communication template:")
    
    # Communication template options
    template_type = st.selectbox(
        "Template Type:",
        [
            "Investigation Team Instruction",
            "Legal Team Communication", 
            "Recovery Team Notice",
            "Customer Communication",
            "Branch Notification",
            "Management Escalation"
        ],
        key=f"comm_template_{case_id}"
    )
    
    # Generate template based on selection
    if st.button("📋 Generate Template", key=f"gen_template_{case_id}"):
        template_content = generate_communication_template(template_type, case_id)
        st.session_state[f"comm_content_{case_id}"] = template_content
        st.success(f"{template_type} template generated")
        st.rerun()
    
    # Display generated template
    if f"comm_content_{case_id}" in st.session_state:
        st.markdown("**Generated Communication Template:**")
        
        template_content = st.text_area(
            "Template Content:",
            value=st.session_state[f"comm_content_{case_id}"],
            height=200,
            key=f"template_editor_{case_id}"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 Send Communication", key=f"send_comm_{case_id}"):
                if template_content.strip():
                    send_communication_template(case_id, template_type, template_content, current_user)
                else:
                    st.warning("Please enter communication content")
        
        with col2:
            if st.button("💾 Save Draft", key=f"save_comm_draft_{case_id}"):
                if template_content.strip():
                    save_communication_draft(case_id, template_type, template_content, current_user)
                else:
                    st.warning("Please enter communication content")
        
        with col3:
            if st.button("📄 Export Template", key=f"export_template_{case_id}"):
                if template_content.strip():
                    export_communication_template(case_id, template_type, template_content)
                else:
                    st.warning("Please enter communication content")

def generate_communication_template(template_type, case_id):
    """Generate communication template based on type"""
    
    from datetime import datetime
    
    templates = {
        "Investigation Team Instruction": f"""**INVESTIGATION INSTRUCTION**

Case Reference: {case_id}
Date: {datetime.now().strftime('%B %d, %Y')}

To: Investigation Team

**SUBJECT: Investigation Instructions for Case {case_id}**

Dear Investigation Team,

Please proceed with the investigation of the above-referenced case with the following instructions:

**Investigation Scope:**
- [Specify investigation scope and objectives]
- [Key areas to focus on]
- [Required documentation and evidence]

**Timeline:**
- Investigation to be completed within [X] days
- Interim report due on [Date]
- Final report submission deadline: [Date]

**Contact Information:**
For any clarifications, please contact the case manager at [Contact Details].

**Authorized by:**
Legal Department
Date: {datetime.now().strftime('%B %d, %Y')}""",

        "Legal Team Communication": f"""**LEGAL TEAM COMMUNICATION**

Case Reference: {case_id}
Date: {datetime.now().strftime('%B %d, %Y')}

To: Legal Department

**SUBJECT: Legal Review Required for Case {case_id}**

Dear Legal Team,

The above case requires your legal review and guidance. Please find the case details and required actions below:

**Case Summary:**
[Brief case summary and key issues]

**Legal Questions:**
1. [Specific legal question 1]
2. [Specific legal question 2]
3. [Additional legal considerations]

**Required Actions:**
- Legal opinion on case merits
- Recommended legal course of action
- Risk assessment and compliance review

**Timeline:**
Please provide your legal opinion within [X] business days.

**Contact:**
Case Manager: [Name and Contact]

Best regards,
Case Management Team""",

        "Recovery Team Notice": f"""**RECOVERY TEAM NOTICE**

Case Reference: {case_id}
Date: {datetime.now().strftime('%B %d, %Y')}

To: Recovery Department

**SUBJECT: Recovery Action Required - Case {case_id}**

Dear Recovery Team,

Please initiate recovery proceedings for the above-referenced case based on the following details:

**Recovery Details:**
- Outstanding Amount: ₹[Amount]
- Last Payment Date: [Date]
- Customer Contact Status: [Status]

**Recommended Actions:**
1. [Primary recovery action]
2. [Secondary recovery measures]
3. [Escalation procedures if required]

**Documentation:**
All case files and legal opinions are attached for your reference.

**Timeline:**
Please commence recovery actions within [X] days and provide status updates weekly.

Recovery Department Head
Date: {datetime.now().strftime('%B %d, %Y')}""",

        "Customer Communication": f"""**CUSTOMER COMMUNICATION**

Case Reference: {case_id}
Date: {datetime.now().strftime('%B %d, %Y')}

**SUBJECT: Important Update Regarding Your Account**

Dear Valued Customer,

We are writing to inform you about the current status of your account and the steps being taken in relation to case {case_id}.

**Current Status:**
[Brief description of case status and customer's position]

**Required Action from Your End:**
1. [Specific action required]
2. [Additional steps if applicable]
3. [Documentation needed]

**Next Steps:**
[Outline of the process going forward]

**Contact Information:**
For any queries or to discuss this matter, please contact us at:
Phone: [Phone Number]
Email: [Email Address]

We appreciate your cooperation in resolving this matter.

Best regards,
Customer Service Team
Aditya Birla Capital Limited""",

        "Branch Notification": f"""**BRANCH NOTIFICATION**

Case Reference: {case_id}
Date: {datetime.now().strftime('%B %d, %Y')}

To: Branch Manager

**SUBJECT: Case Update and Required Actions - {case_id}**

Dear Branch Manager,

Please note the following updates and required actions for the above-referenced case:

**Case Status Update:**
[Current status and recent developments]

**Branch Actions Required:**
1. [Specific action item 1]
2. [Specific action item 2]
3. [Documentation or follow-up needed]

**Customer Interaction Guidelines:**
[Any specific instructions for customer interactions]

**Reporting Requirements:**
Please provide status updates by [Date] and notify immediately of any significant developments.

**Support Available:**
For technical or procedural support, contact the case management team at [Contact Details].

Thank you for your cooperation.

Case Management Department""",

        "Management Escalation": f"""**MANAGEMENT ESCALATION**

Case Reference: {case_id}
Date: {datetime.now().strftime('%B %d, %Y')}

To: Senior Management

**SUBJECT: Case Escalation - Immediate Attention Required**

Dear Management,

The above case requires immediate management attention and decision due to the following critical factors:

**Escalation Reasons:**
1. [Primary reason for escalation]
2. [Additional critical factors]
3. [Risk implications]

**Case Summary:**
[Brief but comprehensive case overview]

**Financial Impact:**
- Exposure Amount: ₹[Amount]
- Potential Loss: ₹[Amount]
- Recovery Prospects: [Assessment]

**Recommended Management Actions:**
1. [Immediate action required]
2. [Strategic decision needed]
3. [Resource allocation required]

**Timeline:**
Immediate review and decision required to prevent further complications.

**Prepared by:**
Case Management Team
Date: {datetime.now().strftime('%B %d, %Y')}
Contact: [Contact Details]"""
    }
    
    return templates.get(template_type, "Template not found")

def send_communication_template(case_id, template_type, content, current_user):
    """Send communication template"""
    try:
        from models import add_case_comment
        
        communication_record = f"COMMUNICATION SENT - Type: {template_type}\n\nContent:\n{content}\n\nSent by: {current_user}\nStatus: SENT"
        
        if add_case_comment(case_id, communication_record, current_user, f"Communication - {template_type}"):
            from error_handler import success_message
            success_message("Communication Sent", f"{template_type} has been sent successfully")
            st.rerun()
        
    except Exception as e:
        from error_handler import handle_database_error
        handle_database_error("communication sending", e)

def save_communication_draft(case_id, template_type, content, current_user):
    """Save communication as draft"""
    try:
        from models import add_case_comment
        
        draft_record = f"COMMUNICATION DRAFT - Type: {template_type}\n\nContent:\n{content}\n\nSaved by: {current_user}\nStatus: DRAFT"
        
        if add_case_comment(case_id, draft_record, current_user, f"Communication Draft - {template_type}"):
            from error_handler import success_message
            success_message("Draft Saved", f"{template_type} draft has been saved successfully")
            st.rerun()
        
    except Exception as e:
        from error_handler import handle_database_error
        handle_database_error("communication draft saving", e)

def export_communication_template(case_id, template_type, content):
    """Export communication template as file"""
    try:
        from datetime import datetime
        import os
        
        # Create export file
        filename = f"Communication_{template_type.replace(' ', '_')}_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join("uploads", filename)
        
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        # Write content to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Communication Template: {template_type}\n")
            f.write(f"Case Reference: {case_id}\n")
            f.write(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
            f.write("="*50 + "\n\n")
            f.write(content)
        
        from error_handler import success_message
        success_message("Template Exported", f"Communication template exported successfully: {filename}")
        
        # Provide download link
        with open(filepath, "r", encoding='utf-8') as file:
            st.download_button(
                label="📥 Download Template",
                data=file.read(),
                file_name=filename,
                mime="text/plain",
                key=f"download_comm_template_{case_id}"
            )
        
    except Exception as e:
        from error_handler import handle_database_error
        handle_database_error("template export", e)
