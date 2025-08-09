"""
Simple case display utilities without formatting
"""
import streamlit as st

def show_simple_case_list(cases, current_user, panel_type="default"):
    """
    Show cases in simple plain text format
    Args:
        cases: List of case dictionaries
        current_user: Current user info
        panel_type: Type of panel for specific actions
    """
    if not cases:
        st.write("No cases available")
        return
    
    # Display cases in simple text format
    st.write("Cases Pending Review")
    st.write("")
    
    for i, case in enumerate(cases, 1):
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
        
        # Convert loan amount to simple format
        try:
            loan_amount_float = float(loan_amount) if loan_amount else 0
            formatted_loan = f"{loan_amount_float:,.0f}" if loan_amount_float > 0 else 'N/A'
        except (ValueError, TypeError):
            formatted_loan = 'N/A'
        
        # Display case info in standardized text box format
        case_display_text = f"{case_id} - {customer_name} ({case_type}) - ₹{formatted_loan}"
        
        st.markdown(f"""
        <div style='
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            margin: 10px 0;
            font-size: 16px;
            color: #333333;
            font-weight: 500;
            line-height: 1.5;
        '>
            <strong>{case_display_text}</strong><br>
            <span style='font-size: 14px; color: #666;'>Product: {product} | Region: {region} | Status: {status}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Add simple actions for closure panel with unique keys
        if panel_type == "closure":
            add_simple_closure_actions(case, current_user, i)
        elif panel_type == "reviewer":
            add_simple_reviewer_actions(case, current_user, i)
        elif panel_type == "legal":
            add_simple_legal_actions(case, current_user, i)

def add_simple_closure_actions(case, current_user, case_index=0):
    """Add simple closure actions without formatting"""
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
    status = safe_get(case, 'status')
    
    if status in ['Legal Review', 'Final Review']:
        st.write("   Actions available:")
        
        # Simple action selection
        closure_action = st.selectbox(
            "Action Type",
            ["Recovery Closure", "Settlement Closure", "Write-off", "Transfer to Legal"],
            key=f"closure_action_{case_id}_{case_index}"
        )
        
        # Simple comment input
        closure_comment = st.text_area(
            "Closure Comments",
            placeholder="Enter closure details...",
            key=f"closure_comment_{case_id}_{case_index}",
            height=60
        )
        
        # Simple buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Close Case", key=f"close_{case_id}_{case_index}"):
                if closure_comment.strip():
                    comment_text = f"CASE CLOSED - {closure_action}: {closure_comment}"
                    from models import update_case_status, add_case_comment
                    try:
                        if add_case_comment(case_id, comment_text, current_user, "Closure Action"):
                            if update_case_status(case_id, "Closed", current_user):
                                from error_handler import success_message
                                success_message("Case Closed", f"Case closed with action: {closure_action}")
                                st.rerun()
                    except Exception as e:
                        from error_handler import handle_database_error
                        handle_database_error("case closure", e)
                else:
                    from error_handler import handle_validation_error
                    handle_validation_error("Closure Comments", "Please add closure comments")
        
        with col2:
            if st.button(f"Request Info", key=f"req_info_{case_id}_{case_index}"):
                if closure_comment.strip():
                    comment_text = f"ADDITIONAL INFO REQUESTED: {closure_comment}"
                    from models import add_case_comment, update_case_status
                    try:
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
        
        st.write("")  # Add space after actions

def add_simple_reviewer_actions(case, current_user, case_index=0):
    """Add simple reviewer actions without formatting"""
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
    status = safe_get(case, 'status')
    
    if status in ['Submitted', 'Under Review']:
        st.write("   Review Actions:")
        
        # Simple comment input
        review_comment = st.text_area(
            "Review Comment",
            placeholder="Enter your review comments...",
            key=f"review_comment_{case_id}_{case_index}",
            height=60
        )
        
        # Simple buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"Approve", key=f"approve_{case_id}_{case_index}"):
                if review_comment.strip():
                    comment_text = f"APPROVED: {review_comment}"
                    from models import update_case_status
                    try:
                        if update_case_status(case_id, "Approved", current_user, comment_text):
                            from error_handler import success_message
                            success_message("Case Approved", "Case approved and sent to Approver 1")
                            st.rerun()
                    except Exception as e:
                        from error_handler import handle_database_error
                        handle_database_error("case approval", e)
                else:
                    from error_handler import handle_validation_error
                    handle_validation_error("Review Comments", "Please add review comments")
        
        with col2:
            if st.button(f"Reject", key=f"reject_{case_id}_{case_index}"):
                if review_comment.strip():
                    comment_text = f"REJECTED: {review_comment}"
                    from models import update_case_status
                    try:
                        if update_case_status(case_id, "Rejected", current_user, comment_text):
                            from error_handler import success_message
                            success_message("Case Rejected", "Case rejected")
                            st.rerun()
                    except Exception as e:
                        from error_handler import handle_database_error
                        handle_database_error("case rejection", e)
                else:
                    from error_handler import handle_validation_error
                    handle_validation_error("Rejection Reason", "Please add rejection reason")
        
        with col3:
            if st.button(f"Add Comment", key=f"comment_{case_id}_{case_index}"):
                if review_comment.strip():
                    from models import add_case_comment
                    try:
                        if add_case_comment(case_id, current_user, review_comment, "Review Comment"):
                            from error_handler import success_message
                            success_message("Comment Added", "Comment added successfully")
                            st.rerun()
                    except Exception as e:
                        from error_handler import handle_database_error
                        handle_database_error("comment addition", e)
                else:
                    from error_handler import handle_validation_error
                    handle_validation_error("Comment", "Please enter a comment")
        
        st.write("")  # Add space after actions

def add_simple_legal_actions(case, current_user, case_index=0):
    """Add simple legal actions without formatting"""
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
    status = safe_get(case, 'status')
    
    if status == 'Legal Review':
        st.write("   Legal Actions:")
        
        # Legal action type selection
        legal_action = st.selectbox(
            "Legal Action Type",
            ["Show Cause Notice", "Reasoned Order", "Legal Opinion", "Recovery Notice"],
            key=f"legal_action_{case_id}_{case_index}"
        )
        
        # Simple comment input
        legal_comment = st.text_area(
            "Legal Comments",
            placeholder="Enter legal analysis and recommendations...",
            key=f"legal_comment_{case_id}_{case_index}",
            height=60
        )
        
        # Simple buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Complete Legal Review", key=f"complete_legal_{case_id}_{case_index}"):
                if legal_comment.strip():
                    comment_text = f"LEGAL REVIEW COMPLETED - {legal_action}: {legal_comment}"
                    from models import update_case_status, add_case_comment
                    try:
                        if add_case_comment(case_id, comment_text, current_user, "Legal Review"):
                            if update_case_status(case_id, "Legal Review Complete", current_user):
                                from error_handler import success_message
                                success_message("Legal Review Complete", f"Legal review completed with action: {legal_action}")
                                st.rerun()
                    except Exception as e:
                        from error_handler import handle_database_error
                        handle_database_error("legal review completion", e)
                else:
                    from error_handler import handle_validation_error
                    handle_validation_error("Legal Comments", "Please add legal comments")
        
        with col2:
            if st.button(f"Request Additional Info", key=f"req_legal_info_{case_id}_{case_index}"):
                if legal_comment.strip():
                    comment_text = f"LEGAL INFO REQUESTED: {legal_comment}"
                    from models import add_case_comment, update_case_status
                    try:
                        if add_case_comment(case_id, comment_text, current_user, "Legal Info Request"):
                            if update_case_status(case_id, "Under Review", current_user):
                                from error_handler import success_message
                                success_message("Information Requested", "Additional information requested")
                                st.rerun()
                    except Exception as e:
                        from error_handler import handle_database_error
                        handle_database_error("legal information request", e)
                else:
                    from error_handler import handle_validation_error
                    handle_validation_error("Information Request", "Please specify what information is needed")
        
        st.write("")  # Add space after actions