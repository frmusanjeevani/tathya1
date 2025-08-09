import streamlit as st
from models import get_cases_by_status, update_case_status, get_case_comments, add_case_comment, get_case_documents
from utils import get_status_color, format_datetime, format_file_size
from auth import get_current_user, require_role
from error_handler import handle_database_error, handle_validation_error, success_message

@require_role(["Legal Reviewer", "Admin"])
def show():
    """Display legal reviewer panel"""
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
        '>Legal Panel</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Legal compliance center for fraud case processing and regulatory actions</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Simple dropdown selection for case level
    st.subheader("Cases Requiring Legal Review")
    st.markdown("---")
    
    # Get cases requiring legal review
    legal_cases = get_cases_by_status("Legal Review")
    
    if legal_cases:
        # Case level dropdown
        case_options = []
        for case in legal_cases:
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
            case_options.append(f"{case_id} - {customer_name} ({case_type})")
        
        selected_case_display = st.selectbox(
            "Select Case for Legal Review:",
            ["Select a case..."] + case_options,
            key="legal_case_selector"
        )
        
        if selected_case_display != "Select a case...":
            # Extract case_id from selection
            selected_case_id = selected_case_display.split(" - ")[0]
            
            # Find the selected case
            selected_case = None
            for case in legal_cases:
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
                show_simple_legal_case_actions(selected_case, current_user)
    else:
        st.info("📭 No cases requiring legal review at this time")
    
    # Cases Ready for Closure section
    st.markdown("---")
    st.subheader("📋 Cases Ready for Closure")
    
    # Get cases that are ready for closure
    closure_ready_cases = get_cases_by_status("Legal Review Complete")
    
    if closure_ready_cases:
        closure_case_options = []
        for case in closure_ready_cases:
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
            closure_case_options.append(f"{case_id} - {customer_name} ({case_type})")
        
        selected_closure_case = st.selectbox(
            "Select Case for Closure:",
            ["Select a case..."] + closure_case_options,
            key="closure_case_selector"
        )
        
        if selected_closure_case != "Select a case...":
            selected_closure_id = selected_closure_case.split(" - ")[0]
            
            # Find the selected case
            closure_case = None
            for case in closure_ready_cases:
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
                        
                if safe_get(case, 'case_id') == selected_closure_id:
                    closure_case = case
                    break
            
            if closure_case:
                show_simple_closure_actions(closure_case, current_user)
    else:
        st.info("📭 No cases ready for closure at this time")

def show_simple_legal_case_actions(case, current_user):
    """Display simple legal case actions without complex formatting"""
    
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
    
    # Legal action type selection
    legal_action_type = st.selectbox(
        "Legal Action Type:",
        ["", "Show Cause Notice (SCN)", "Reasoned Order", "Legal Opinion", "Recovery Notice"],
        key=f"legal_action_{case_id}"
    )
    
    if legal_action_type:
        # Legal comments
        legal_comments = st.text_area(
            "Legal Analysis:",
            placeholder="Enter legal analysis and recommendations...",
            height=100,
            key=f"legal_comments_{case_id}"
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Complete Legal Review", key=f"complete_legal_{case_id}"):
                if legal_comments.strip():
                    try:
                        comment_text = f"LEGAL REVIEW COMPLETED - {legal_action_type}: {legal_comments}"
                        from models import add_case_comment, update_case_status
                        
                        if add_case_comment(case_id, comment_text, current_user, "Legal Review"):
                            if update_case_status(case_id, "Legal Review Complete", current_user):
                                success_message("Legal Review Complete", f"Legal review completed with {legal_action_type}")
                                st.rerun()
                    except Exception as e:
                        handle_database_error("legal review completion", e)
                else:
                    handle_validation_error("Legal Comments", "Please provide legal analysis")
        
        with col2:
            if st.button("Request Additional Info", key=f"req_info_{case_id}"):
                if legal_comments.strip():
                    try:
                        comment_text = f"ADDITIONAL INFO REQUESTED: {legal_comments}"
                        from models import add_case_comment, update_case_status
                        
                        if add_case_comment(case_id, comment_text, current_user, "Legal Info Request"):
                            if update_case_status(case_id, "Under Review", current_user):
                                success_message("Information Requested", "Additional information requested")
                                st.rerun()
                    except Exception as e:
                        handle_database_error("information request", e)
                else:
                    handle_validation_error("Information Request", "Please specify what information is needed")

def show_simple_closure_actions(case, current_user):
    """Display simple closure actions for legal cases"""
    
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
    
    st.write(f"**Case ID:** {case_id}")
    st.write(f"**Customer:** {customer_name}")
    st.write(f"**Type:** {case_type}")
    st.write("")
    
    # Closure action selection
    closure_action = st.selectbox(
        "Closure Action:",
        ["", "Recovery Closure", "Settlement Closure", "Write-off", "Transfer to Collections"],
        key=f"closure_action_{case_id}"
    )
    
    if closure_action:
        # Closure comments
        closure_comments = st.text_area(
            "Closure Details:",
            placeholder="Enter closure details and final remarks...",
            height=80,
            key=f"closure_comments_{case_id}"
        )
        
        if st.button("Close Case", key=f"close_case_{case_id}"):
            if closure_comments.strip():
                try:
                    comment_text = f"CASE CLOSED - {closure_action}: {closure_comments}"
                    from models import add_case_comment, update_case_status
                    
                    if add_case_comment(case_id, comment_text, current_user, "Case Closure"):
                        if update_case_status(case_id, "Closed", current_user):
                            success_message("Case Closed", f"Case closed with action: {closure_action}")
                            st.rerun()
                except Exception as e:
                    handle_database_error("case closure", e)
            else:
                handle_validation_error("Closure Details", "Please provide closure details")

def show_legal_case_details(case, current_user):
    """Display case details for legal review using standardized format"""
    from case_display_utils import show_standardized_case_details, show_standardized_customer_info, show_standardized_case_history, show_standardized_documents
    
    # Display standardized case details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_standardized_case_details(case)
        show_standardized_customer_info(case)
    
    with col2:
        show_standardized_case_history(case['case_id'])
        show_standardized_documents(case['case_id'])
    
    # Enhanced Legal Review Actions with Sequential Workflow
    st.markdown("### 🧑‍⚖️ Legal Review Actions")
    
    # Step 1: Legal Action Type Selection (Required First)
    legal_action_type = st.selectbox(
        "Select Legal Action Type (Required First):",
        ["", "Show Cause Notice (SCN)", "Reasoned Order", "Legal Opinion", "Recovery Notice", "No Legal Action Required"],
        key=f"legal_action_type_{case['case_id']}"
    )
    
    # Only show subsequent fields after action type is selected
    if legal_action_type:
        st.success(f"✅ Selected: {legal_action_type}")
        
        # Step 2: Show SCN to Legal tab and other fields only after action type selection
        if legal_action_type == "Show Cause Notice (SCN)":
            # Show enhanced SCN section
            st.markdown("#### 📄 SCN to Legal Tab")
            
            scn_details = st.text_area(
                "SCN Details:",
                placeholder="Enter details for Show Cause Notice...",
                height=100,
                key=f"scn_details_{case['case_id']}"
            )
            
            scn_deadline = st.date_input(
                "Response Deadline:",
                key=f"scn_deadline_{case['case_id']}"
            )
            
            if st.button(f"📤 Send SCN", key=f"send_scn_{case['case_id']}"):
                if scn_details.strip():
                    # Process SCN sending
                    from models import add_case_comment
                    from database import log_audit
                    
                    add_case_comment(case['case_id'], f"SCN SENT: {scn_details}\nDeadline: {scn_deadline}", "Legal SCN", current_user)
                    log_audit(case['case_id'], "SCN Sent", f"Show Cause Notice sent with deadline: {scn_deadline}", current_user)
                    
                    st.success("✅ Show Cause Notice sent successfully!")
                    st.rerun()
                else:
                    st.error("Please enter SCN details")
        
        # Legal comments with AI suggestions (now enabled)
        st.markdown("**Legal Review Comments**")
        col_leg1, col_leg2 = st.columns([3, 1])
        with col_leg2:
            if st.button("💡 Quick Remarks", key=f"legal_sugg_{case['case_id']}"):
                from ai_suggestions import get_remarks_suggestions
                suggestions = get_remarks_suggestions()["legal_stage"]
                st.session_state[f"legal_suggestions_{case['case_id']}"] = suggestions
    else:
        st.info("⚠️ Please select a Legal Action Type first to proceed with legal review")
    
    # Show suggestions
    if f"legal_suggestions_{case['case_id']}" in st.session_state:
        st.markdown("**Quick Remarks:**")
        legal_cols = st.columns(2)
        for i, suggestion in enumerate(st.session_state[f"legal_suggestions_{case['case_id']}"][:4]):
            col_idx = i % 2
            with legal_cols[col_idx]:
                if st.button(f"📝 {suggestion[:30]}...", key=f"leg_sugg_{case['case_id']}_{i}", help=suggestion):
                    st.session_state[f"selected_legal_{case['case_id']}"] = suggestion
                    st.rerun()
    
    initial_legal = st.session_state.get(f"selected_legal_{case['case_id']}", "")
    legal_comment = st.text_area(
        "Legal Review Comments",
        value=initial_legal,
        key=f"legal_comment_{case['case_id']}",
        placeholder="Enter legal analysis and recommendations or use quick remarks above...",
        height=80,
        label_visibility="collapsed"
    )
    
    # Legal action type
    legal_action = st.selectbox(
        "Legal Action Required",
        ["No Legal Action", "Show Cause Notice", "Recovery Action", "Settlement", "Closure", "Other"],
        key=f"legal_action_{case['case_id']}"
    )
    
    if legal_action == "Other":
        other_action = st.text_input(
            "Specify Other Action",
            key=f"other_action_{case['case_id']}"
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"✅ Legal Cleared", key=f"legal_clear_{case['case_id']}"):
            if legal_comment.strip():
                comment_text = f"LEGAL CLEARED: {legal_comment}"
                if legal_action != "No Legal Action":
                    comment_text += f" | Action: {legal_action}"
                
                if update_case_status(case['case_id'], "Approved", current_user, comment_text):
                    st.success("✅ Case legally cleared")
                    st.rerun()
            else:
                st.warning("Please add legal review comments")
    
    with col2:
        if st.button(f"⚠️ Legal Issues", key=f"legal_issues_{case['case_id']}"):
            if legal_comment.strip():
                comment_text = f"LEGAL ISSUES IDENTIFIED: {legal_comment}"
                if legal_action != "No Legal Action":
                    comment_text += f" | Action Required: {legal_action}"
                
                if update_case_status(case['case_id'], "Under Review", current_user, comment_text):
                    st.success("✅ Legal issues logged, case sent back for review")
                    st.rerun()
            else:
                st.warning("Please specify the legal issues")
    
    with col3:
        if st.button(f"📄 Issue SCN", key=f"issue_scn_{case['case_id']}"):
            if legal_comment.strip():
                comment_text = f"SHOW CAUSE NOTICE ISSUED: {legal_comment}"
                add_case_comment(case['case_id'], comment_text, "SCN Issued", current_user)
                st.success("✅ Show Cause Notice marked as issued")
                st.rerun()
            else:
                st.warning("Please add SCN details")
    
    with col4:
        if st.button(f"🔒 Close Case", key=f"close_legal_{case['case_id']}"):
            if legal_comment.strip():
                comment_text = f"CASE CLOSED BY LEGAL: {legal_comment}"
                if update_case_status(case['case_id'], "Closed", current_user, comment_text):
                    st.success("✅ Case closed")
                    st.rerun()
            else:
                st.warning("Please add closure reason")

def show_scn_orders_section():
    """Display SCN and Orders management section"""
    
    st.write("### Show Cause Notices & Orders Management")
    
    # SCN/Orders entry form
    with st.expander("📝 Create New SCN/Order"):
        with st.form("scn_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                scn_case_id = st.text_input("Related Case ID")
                scn_type = st.selectbox("Type", ["Show Cause Notice", "Recovery Order", "Settlement Order", "Closure Order"])
                scn_date = st.date_input("Issue Date")
            
            with col2:
                scn_number = st.text_input("SCN/Order Number")
                scn_status = st.selectbox("Status", ["Draft", "Issued", "Response Received", "Closed"])
                response_date = st.date_input("Response Due Date")
            
            scn_details = st.text_area("Details/Content", height=100)
            
            if st.form_submit_button("📤 Create SCN/Order"):
                if all([scn_case_id, scn_number, scn_details]):
                    # Here you would save SCN/Order to database
                    # For now, just show success message
                    st.success("✅ SCN/Order created successfully")
                else:
                    st.error("Please fill all required fields")
    
    # Display existing SCN/Orders (this would come from database)
    st.write("### Existing SCN/Orders")
    
    # Sample data - in real implementation, this would come from database
    sample_scns = [
        {
            "scn_number": "SCN/2024/001",
            "case_id": "CASE001",
            "type": "Show Cause Notice",
            "status": "Issued",
            "issue_date": "2024-01-15",
            "response_due": "2024-01-30"
        },
        {
            "scn_number": "RO/2024/001",
            "case_id": "CASE002",
            "type": "Recovery Order",
            "status": "Response Received",
            "issue_date": "2024-01-10",
            "response_due": "2024-01-25"
        }
    ]
    
    if sample_scns:
        for scn in sample_scns:
            with st.expander(f"{scn['scn_number']} - {scn['type']} ({scn['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**SCN/Order Number:** {scn['scn_number']}")
                    st.write(f"**Related Case:** {scn['case_id']}")
                    st.write(f"**Type:** {scn['type']}")
                
                with col2:
                    st.write(f"**Status:** {scn['status']}")
                    st.write(f"**Issue Date:** {scn['issue_date']}")
                    st.write(f"**Response Due:** {scn['response_due']}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"📝 Update Status", key=f"update_{scn['scn_number']}"):
                        st.info("Status update functionality")
                
                with col2:
                    if st.button(f"📎 Add Documents", key=f"docs_{scn['scn_number']}"):
                        st.info("Document management functionality")
                
                with col3:
                    if st.button(f"🔒 Close", key=f"close_scn_{scn['scn_number']}"):
                        st.info("SCN closure functionality")
    else:
        st.info("No SCN/Orders found")

def show_enhanced_scn_orders_section(current_user):
    """Enhanced Show Cause Notice and Orders Management with AI generation"""
    from datetime import datetime
    
    st.markdown("### 📄 Show Cause Notices & Orders Management")
    
    # Get all cases assigned to legal team
    legal_cases = get_cases_by_status("Legal Review")
    
    if not legal_cases:
        st.warning("📭 No cases currently assigned to legal team")
        return
    
    # Case selection dropdown
    case_options = {f"{case['case_id']} - {case['customer_name']} ({case['case_type']})": case for case in legal_cases}
    selected_case_option = st.selectbox("🔍 Select Case for Legal Action", 
                                       [""] + list(case_options.keys()),
                                       help="Choose a case to generate legal documents")
    
    if not selected_case_option:
        st.info("👆 Please select a case to proceed with legal document generation")
        return
    
    selected_case = case_options[selected_case_option]
    
    # Display comprehensive case information
    st.markdown("---")
    st.markdown("### 📋 Case Information & Demographics")
    
    # Case details in organized layout
    case_col1, case_col2, case_col3 = st.columns(3)
    
    with case_col1:
        st.markdown("**🆔 Case Identification**")
        st.markdown(f"**Case ID:** `{selected_case['case_id']}`")
        st.markdown(f"**LAN:** `{selected_case['lan']}`")
        st.markdown(f"**Case Type:** {selected_case['case_type']}")
        st.markdown(f"**Product:** {selected_case['product']}")
        st.markdown(f"**Region:** {selected_case['region']}")
        st.markdown(f"**Branch:** {selected_case['branch_location']}")
    
    with case_col2:
        st.markdown("**👤 Customer Demographics**")
        st.markdown(f"**Name:** {selected_case['customer_name']}")
        st.markdown(f"**PAN:** {selected_case['customer_pan']}")
        st.markdown(f"**Mobile:** {selected_case['customer_mobile']}")
        st.markdown(f"**Email:** {selected_case['customer_email']}")
        if selected_case['customer_dob']:
            st.markdown(f"**DOB:** {selected_case['customer_dob']}")
        if selected_case['loan_amount']:
            st.markdown(f"**Loan Amount:** ₹{selected_case['loan_amount']:,.2f}")
    
    with case_col3:
        st.markdown("**📊 Case Status & Timeline**")
        st.markdown(f"**Status:** {selected_case['status']}")
        st.markdown(f"**Case Date:** {selected_case['case_date']}")
        st.markdown(f"**Created By:** {selected_case['created_by']}")
        st.markdown(f"**Referred By:** {selected_case['referred_by']}")
        if selected_case['disbursement_date']:
            st.markdown(f"**Disbursement:** {selected_case['disbursement_date']}")
    
    # Case description
    st.markdown("**📝 Case Description:**")
    st.markdown(f"_{selected_case['case_description']}_")
    
    # Legal document generation section
    st.markdown("---")
    st.markdown("### ⚖️ Legal Document Generation")
    
    doc_col1, doc_col2 = st.columns([2, 1])
    
    with doc_col1:
        document_type = st.selectbox("Select Document Type", 
            ["Show Cause Notice (SCN)", "Reasoned Order", "Legal Opinion", "Recovery Notice", "Demand Notice"])
        
        # Additional details for document generation
        legal_grounds = st.text_area("Legal Grounds/Basis", 
                                   placeholder="Enter legal grounds and basis for the document...", 
                                   height=100)
        
        specific_violations = st.text_area("Specific Violations/Issues", 
                                         placeholder="Detail specific violations or issues identified...", 
                                         height=80)
        
        response_deadline = st.date_input("Response Deadline (if applicable)")
        
        additional_instructions = st.text_area("Additional Instructions/Requirements", 
                                             placeholder="Any additional legal instructions or requirements...", 
                                             height=60)
    
    with doc_col2:
        st.markdown("**🤖 AI-Powered Generation**")
        if st.button("✨ Generate with AI", type="primary", use_container_width=True):
            if legal_grounds.strip():
                # Generate AI-powered legal document
                generated_content = generate_legal_document_ai(selected_case, document_type, legal_grounds, specific_violations, additional_instructions)
                st.session_state[f"generated_doc_{selected_case['case_id']}"] = generated_content
                st.success("✅ AI document generated successfully!")
                st.rerun()
            else:
                st.warning("Please provide legal grounds before generating document")
        
        st.markdown("**📝 Manual Template**")
        if st.button("📋 Load Template", use_container_width=True):
            template_content = get_legal_document_template(document_type, selected_case)
            st.session_state[f"generated_doc_{selected_case['case_id']}"] = template_content
            st.success("✅ Template loaded successfully!")
            st.rerun()
    
    # Display generated document
    if f"generated_doc_{selected_case['case_id']}" in st.session_state:
        st.markdown("---")
        st.markdown("### 📄 Generated Legal Document")
        
        generated_doc = st.session_state[f"generated_doc_{selected_case['case_id']}"]
        
        # Editable document content
        final_document = st.text_area("Legal Document Content", 
                                    value=generated_doc, 
                                    height=400,
                                    help="Review and edit the generated document as needed")
        
        # Action buttons
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("💾 Save Document", type="primary"):
                save_legal_document(selected_case['case_id'], document_type, final_document, current_user)
                st.success("✅ Document saved successfully!")
        
        with action_col2:
            if st.button("📧 Send to Customer"):
                send_legal_document(selected_case, document_type, final_document, current_user)
                st.success("✅ Document sent to customer!")
        
        with action_col3:
            if st.button("📎 Download PDF"):
                generate_pdf_download(selected_case, document_type, final_document)
                st.success("✅ PDF generated!")
        
        with action_col4:
            if st.button("🗑️ Clear Document"):
                del st.session_state[f"generated_doc_{selected_case['case_id']}"]
                st.rerun()

def generate_legal_document_ai(case, doc_type, legal_grounds, violations, instructions):
    """Generate legal document using AI (placeholder for Gemini integration)"""
    from datetime import datetime
    
    # Safely get case values with defaults for None values (used by all document types)
    def safe_get(case_obj, key, default='N/A'):
        try:
            if hasattr(case_obj, 'keys') and hasattr(case_obj, '__getitem__'):
                return case_obj[key] if key in case_obj.keys() and case_obj[key] is not None else default
            elif hasattr(case_obj, 'keys'):
                return case_obj.get(key, default)
            else:
                return getattr(case_obj, key, default)
        except (KeyError, AttributeError, TypeError):
            return default
    
    customer_name = safe_get(case, 'customer_name')
    customer_pan = safe_get(case, 'customer_pan')
    customer_mobile = safe_get(case, 'customer_mobile')
    customer_email = safe_get(case, 'customer_email')
    lan = safe_get(case, 'lan')
    loan_amount = safe_get(case, 'loan_amount', '0')
    disbursement_date = safe_get(case, 'disbursement_date')
    case_type = safe_get(case, 'case_type')
    product = safe_get(case, 'product')
    region = safe_get(case, 'region')
    branch_location = safe_get(case, 'branch_location')
    case_description = safe_get(case, 'case_description')
    
    # Basic document structure based on type
    if doc_type == "Show Cause Notice (SCN)":
        
        content = f"""**SHOW CAUSE NOTICE**

Case Reference: {case['case_id']}
Date: {datetime.now().strftime('%B %d, %Y')}

To: {customer_name}
PAN: {customer_pan}
Mobile: {customer_mobile}
Email: {customer_email}

**SUBJECT: Show Cause Notice - Loan Account No. {lan}**

Dear {customer_name},

This notice is issued to you in connection with your loan account bearing number {lan} for ₹{loan_amount:,.2f} disbursed on {disbursement_date}.

**GROUNDS FOR NOTICE:**
{legal_grounds}

**SPECIFIC VIOLATIONS/ISSUES IDENTIFIED:**
{violations}

**CASE DETAILS:**
- Case Type: {case_type}
- Product: {product}
- Region: {region}
- Branch: {branch_location}

**DESCRIPTION:**
{case_description}

{instructions}

You are hereby called upon to show cause within [X] days from the receipt of this notice as to why appropriate action should not be taken against you.

Failure to respond within the stipulated time will result in appropriate legal action being initiated against you without further notice.

**Authorized Signatory**
Legal Department
[Company Name]
Date: {datetime.now().strftime('%B %d, %Y')}"""
    
    elif doc_type == "Reasoned Order":
        content = f"""**REASONED ORDER**

Case Reference: {case['case_id']}
Order Date: {datetime.now().strftime('%B %d, %Y')}

In the matter of: {customer_name} (PAN: {customer_pan})
Loan Account No.: {lan}

**BACKGROUND:**
This order is passed in connection with loan account {lan} for ₹{loan_amount:,.2f} disbursed to {customer_name} on {disbursement_date}.

**CASE DETAILS:**
- Case Type: {case_type}
- Product: {product}
- Region: {region}
- Branch: {branch_location}

**FACTS OF THE CASE:**
{case_description}

**LEGAL GROUNDS:**
{legal_grounds}

**FINDINGS:**
{violations}

**DECISION:**
Based on the facts, evidence, and legal provisions cited above, it is hereby ordered that:

{instructions}

This order is effective immediately and is subject to appeal within the prescribed time limit.

**Authorized Officer**
Legal Department
[Company Name]
Date: {datetime.now().strftime('%B %d, %Y')}"""
    
    else:
        content = f"""**{doc_type.upper()}**

Case Reference: {case['case_id']}
Date: {datetime.now().strftime('%B %d, %Y')}

Customer: {customer_name}
PAN: {customer_pan}
Loan Account: {lan}
Amount: ₹{loan_amount:,.2f}

**SUBJECT:** {doc_type} - {case_type}

**DETAILS:**
{case_description}

**LEGAL BASIS:**
{legal_grounds}

**SPECIFIC ISSUES:**
{violations}

**INSTRUCTIONS:**
{instructions}

**Authorized Signatory**
Legal Department
[Company Name]"""
    
    return content

def get_legal_document_template(doc_type, case):
    """Get standard template for legal documents"""
    return f"""**{doc_type.upper()} TEMPLATE**

[Standard template for {doc_type}]

Case: {case['case_id']}
Customer: {case['customer_name']}
Account: {case['lan']}

[Template content will be populated here]"""

def save_legal_document(case_id, doc_type, content, current_user):
    """Save legal document to database"""
    from database import log_audit
    username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
    add_case_comment(case_id, f"LEGAL DOCUMENT GENERATED: {doc_type}\\n\\n{content[:200]}...", username, "Legal Document")
    log_audit(case_id, f"Legal Document Generated ({doc_type})", f"Document generated by {username}", username)

def send_legal_document(case, doc_type, content, current_user):
    """Send legal document to customer"""
    from database import log_audit
    username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
    add_case_comment(case['case_id'], f"LEGAL DOCUMENT SENT: {doc_type} sent to {case['customer_email']}", username, "Legal Document")
    log_audit(case['case_id'], f"Legal Document Sent ({doc_type})", f"Document sent to customer by {username}", username)

def generate_pdf_download(case, doc_type, content):
    """Generate PDF download for legal document"""
    st.info("PDF generation functionality will be implemented with ReportLab integration")
