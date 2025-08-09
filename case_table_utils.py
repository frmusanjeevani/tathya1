"""
Expandable case table utilities for presentable case display
"""
import streamlit as st
from case_display_utils import show_standardized_case_details, show_standardized_customer_info, show_standardized_case_history, show_standardized_documents
from light_professional_styles import apply_light_professional_styling

def show_expandable_case_table(cases, current_user, panel_type="default"):
    """
    Display cases in expandable table format with presentable summary and detailed view
    """
    if not cases:
        st.info("📭 No cases available")
        return
    
    # Apply light professional styling
    apply_light_professional_styling()
    
    # Add CSS for presentable table styling
    st.markdown("""
    <style>
    .case-summary-table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-radius: 8px;
        overflow: hidden;
        background: #ffffff;
    }
    .case-summary-header {
        background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%);
        color: white;
        font-weight: 500;
        padding: 12px 8px;
        text-align: center;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .case-summary-row {
        background: #ffffff;
        border-bottom: 1px solid #f1f3f4;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .case-summary-row:hover {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    .case-summary-cell {
        padding: 10px 8px;
        text-align: center;
        font-size: 12px;
        border-right: 1px solid #f1f3f4;
        font-weight: 400;
        color: #3c4043;
    }
    .case-id-cell {
        font-weight: 500;
        color: #1a73e8;
        background: linear-gradient(135deg, #e8f0fe 0%, #ffffff 100%);
        font-size: 13px;
    }
    .status-badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 500;
        color: white;
        background: linear-gradient(135deg, #34a853 0%, #137333 100%);
        box-shadow: 0 1px 3px rgba(52, 168, 83, 0.3);
        text-transform: uppercase;
    }
    .loan-amount {
        font-weight: 500;
        color: #137333;
        background: linear-gradient(135deg, #e6f4ea 0%, #ffffff 100%);
        border-radius: 4px;
        padding: 4px 8px;
        border: 1px solid #c3e6cb;
    }
    .customer-name {
        font-weight: 600;
        color: #495057;
        background: linear-gradient(135deg, #fff3cd 0%, #ffffff 100%);
        border-radius: 4px;
        padding: 2px 6px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create summary table
    table_html = """
    <table class="case-summary-table">
        <thead>
            <tr>
                <th class="case-summary-header">Case ID</th>
                <th class="case-summary-header">Customer</th>
                <th class="case-summary-header">Type</th>
                <th class="case-summary-header">Product</th>
                <th class="case-summary-header">Region</th>
                <th class="case-summary-header">Loan Amount</th>
                <th class="case-summary-header">Status</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Add table rows
    for case in cases:
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
        
        case_id = safe_get(case, 'case_id')
        customer_name = safe_get(case, 'customer_name')
        case_type = safe_get(case, 'case_type')
        product = safe_get(case, 'product')
        region = safe_get(case, 'region')
        loan_amount = safe_get(case, 'loan_amount') or 0
        status = safe_get(case, 'status')
        
        # Convert loan amount to float for comparison
        try:
            loan_amount_float = float(loan_amount) if loan_amount else 0
            formatted_loan = f"₹{loan_amount_float:,.2f}" if loan_amount_float > 0 else 'N/A'
        except (ValueError, TypeError):
            formatted_loan = 'N/A'
        
        table_html += f"""
        <tr class="case-summary-row">
            <td class="case-summary-cell case-id-cell">{case_id}</td>
            <td class="case-summary-cell"><span class="customer-name">{customer_name}</span></td>
            <td class="case-summary-cell">{case_type}</td>
            <td class="case-summary-cell">{product}</td>
            <td class="case-summary-cell">{region}</td>
            <td class="case-summary-cell"><span class="loan-amount">{formatted_loan}</span></td>
            <td class="case-summary-cell"><span class="status-badge">{status}</span></td>
        </tr>
        """
    
    table_html += """
        </tbody>
    </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Create expandable sections for each case
    st.markdown("### 📋 Click to Expand Case Details")
    
    for case in cases:
        # Safe value extraction (handle both dict and sqlite3.Row)
        def safe_get(obj, key, default='N/A'):
            if hasattr(obj, 'get'):
                return obj.get(key, default)
            elif hasattr(obj, key):
                return getattr(obj, key) or default
            else:
                return default
        
        case_id = safe_get(case, 'case_id')
        customer_name = safe_get(case, 'customer_name')
        
        # Use streamlit expander for interaction
        with st.expander(f"📄 {case_id} - {customer_name}", expanded=False):
            # Display full case details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                show_standardized_case_details(case)
                show_standardized_customer_info(case)
            
            with col2:
                show_standardized_case_history(case_id)
                show_standardized_documents(case_id)
            
            # Panel-specific actions
            add_panel_specific_actions(case, current_user, panel_type)

def add_panel_specific_actions(case, current_user, panel_type):
    """Add panel-specific action buttons"""
    if panel_type == "reviewer":
        add_reviewer_actions(case, current_user)
    elif panel_type == "approver":
        add_approver_actions(case, current_user)
    elif panel_type == "legal":
        add_legal_actions(case, current_user)
    elif panel_type == "closure":
        add_closure_actions(case, current_user)

def add_reviewer_actions(case, current_user):
    """Add reviewer-specific actions"""
    # Safe value extraction (handle both dict and sqlite3.Row)
    def safe_get(obj, key, default='N/A'):
        if hasattr(obj, 'get'):
            return obj.get(key, default)
        elif hasattr(obj, key):
            return getattr(obj, key) or default
        else:
            return default
    
    case_id = safe_get(case, 'case_id')
    status = safe_get(case, 'status')
    
    if status in ['Submitted', 'Under Review']:
        st.divider()
        st.markdown("**Review Actions:**")
        
        # Comment section with AI suggestions
        st.markdown("**Add Review Comment**")
        col_comm1, col_comm2 = st.columns([3, 1])
        with col_comm2:
            if st.button("💡 Quick Remarks", key=f"review_sugg_{case_id}"):
                from ai_suggestions import get_remarks_suggestions
                suggestions = get_remarks_suggestions()["review_stage"]
                st.session_state[f"review_suggestions_{case_id}"] = suggestions
        
        # Show suggestions
        if f"review_suggestions_{case_id}" in st.session_state:
            st.markdown("**Quick Remarks:**")
            remarks_cols = st.columns(2)
            for i, suggestion in enumerate(st.session_state[f"review_suggestions_{case_id}"][:4]):
                col_idx = i % 2
                with remarks_cols[col_idx]:
                    if st.button(f"📝 {suggestion[:30]}...", key=f"rev_sugg_{case_id}_{i}", help=suggestion):
                        st.session_state[f"selected_review_{case_id}"] = suggestion
                        st.rerun()
        
        initial_comment = st.session_state.get(f"selected_review_{case_id}", "")
        review_comment = st.text_area(
            "Review Comment",
            value=initial_comment,
            key=f"review_comment_{case_id}",
            placeholder="Enter your review comments or use quick remarks above...",
            height=80
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"✅ Approve", key=f"approve_{case_id}"):
                if review_comment.strip():
                    comment_text = f"APPROVED: {review_comment}"
                    from models import update_case_status
                    if update_case_status(case_id, "Approved", current_user, comment_text):
                        st.success("✅ Case approved and sent to Approver 1")
                        st.rerun()
                else:
                    st.warning("Please add review comments")
        
        with col2:
            if st.button(f"❌ Reject", key=f"reject_{case_id}"):
                if review_comment.strip():
                    comment_text = f"REJECTED: {review_comment}"
                    from models import update_case_status
                    if update_case_status(case_id, "Rejected", current_user, comment_text):
                        st.success("❌ Case rejected")
                        st.rerun()
                else:
                    st.warning("Please add rejection reason")
        
        with col3:
            if st.button(f"📝 Add Comment", key=f"comment_{case_id}"):
                if review_comment.strip():
                    from models import add_case_comment
                    if add_case_comment(case_id, current_user, review_comment, "Review Comment"):
                        st.success("💬 Comment added")
                        st.rerun()
                else:
                    st.warning("Please enter a comment")

def add_approver_actions(case, current_user):
    """Add approver-specific actions"""
    # Implementation for approver actions
    pass

def add_legal_actions(case, current_user):
    """Add legal-specific actions"""
    # Implementation for legal actions
    pass

def add_closure_actions(case, current_user):
    """Add closure-specific actions"""
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
    
    case_id = safe_get(case, 'case_id')
    status = safe_get(case, 'status')
    
    if status in ['Legal Review', 'Final Review']:
        st.divider()
        st.markdown("**Closure Actions:**")
        
        # Closure action options
        closure_action = st.selectbox(
            "Action Type",
            ["Recovery Closure", "Settlement Closure", "Write-off", "Transfer to Legal"],
            key=f"closure_action_{case_id}"
        )
        
        # Closure comments
        closure_comment = st.text_area(
            "Closure Comments",
            placeholder="Enter closure details and rationale...",
            key=f"closure_comment_{case_id}",
            height=80
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"✅ Close Case", key=f"close_{case_id}"):
                if closure_comment.strip():
                    comment_text = f"CASE CLOSED - {closure_action}: {closure_comment}"
                    from models import update_case_status, add_case_comment
                    if add_case_comment(case_id, comment_text, current_user, "Closure Action"):
                        if update_case_status(case_id, "Closed", current_user):
                            st.success(f"✅ Case closed with action: {closure_action}")
                            st.rerun()
                else:
                    st.warning("Please add closure comments")
        
        with col2:
            if st.button(f"📤 Request Info", key=f"req_info_{case_id}"):
                if closure_comment.strip():
                    comment_text = f"ADDITIONAL INFO REQUESTED: {closure_comment}"
                    from models import add_case_comment, update_case_status
                    if add_case_comment(case_id, comment_text, current_user, "Info Request"):
                        if update_case_status(case_id, "Under Review", current_user):
                            st.success("📤 Additional information requested")
                            st.rerun()
                else:
                    st.warning("Please specify what information is needed")

def show_compact_case_grid(cases, title="Cases"):
    """
    Display cases in a compact grid format for dashboard views
    """
    if not cases:
        st.info(f"📭 No {title.lower()} available")
        return
    
    st.markdown(f"### 📊 {title}")
    
    # Create grid layout
    cols = st.columns(min(3, len(cases)))
    
    for i, case in enumerate(cases[:6]):  # Show max 6 cases in grid
        col_idx = i % 3
        
        with cols[col_idx]:
            case_id = case.get('case_id', 'N/A')
            customer_name = case.get('customer_name', 'N/A')
            status = case.get('status', 'N/A')
            loan_amount = case.get('loan_amount', 0)
            
            formatted_loan = f"₹{loan_amount:,.2f}" if loan_amount and loan_amount > 0 else 'N/A'
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
                border: 1px solid #dee2e6;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            ">
                <div style="font-weight: 600; color: #007bff; margin-bottom: 6px;">{case_id}</div>
                <div style="font-size: 14px; margin-bottom: 4px;">👤 {customer_name}</div>
                <div style="font-size: 12px; color: #666; margin-bottom: 6px;">💰 {formatted_loan}</div>
                <div style="text-align: center;">
                    <span style="
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-size: 11px;
                        font-weight: 600;
                    ">{status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    if len(cases) > 6:
        st.info(f"... and {len(cases) - 6} more cases")

def create_interactive_case_button(case, button_text="View Case", key_suffix=""):
    """
    Create an interactive button that shows case details when clicked
    """
    case_id = case.get('case_id', 'N/A')
    
    if st.button(f"{button_text}: {case_id}", key=f"btn_{case_id}_{key_suffix}"):
        st.session_state[f"show_case_{case_id}"] = not st.session_state.get(f"show_case_{case_id}", False)
    
    if st.session_state.get(f"show_case_{case_id}", False):
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                show_standardized_case_details(case)
                show_standardized_customer_info(case)
            
            with col2:
                show_standardized_case_history(case_id)
                show_standardized_documents(case_id)