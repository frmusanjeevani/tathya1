"""
Standardized case details display utilities
Reference format from Investigation Panel 🗂️ Case Investigation section
"""
import streamlit as st
from utils import format_datetime
from light_professional_styles import apply_light_professional_styling

def show_standardized_case_details(case_details, show_customer_info=True):
    """
    Display case details in standardized format used across all workflow stages
    Based on Investigation Panel Case Investigation format
    """
    
    # Apply light professional styling
    apply_light_professional_styling()
    
    # Add CSS styling
    st.markdown("""
    <style>
    .case-details-card {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
        border-radius: 10px;
        padding: 18px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid #e8eaed;
    }
    .case-details-header {
        color: #5f6368;
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 12px;
        border-bottom: 1px solid #dadce0;
        padding-bottom: 6px;
    }
    .case-info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 12px;
    }
    .case-info-item {
        background: #ffffff;
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #4285f4;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .case-info-label {
        font-weight: 500;
        color: #5f6368;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
        background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%);
        color: white;
        padding: 4px 8px;
        border-radius: 3px;
        text-align: center;
        font-size: 11px;
    }
    .case-info-value {
        color: #333333;
        font-size: 16px;
        font-weight: 500;
        background: #f5f5f5;
        padding: 12px 16px;
        border-radius: 6px;
        border: 1px solid #ddd;
        margin-top: 4px;
        line-height: 1.4;
    }
    .case-description {
        background: #ffffff;
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #34a853;
        margin-top: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .customer-info-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #90caf9;
    }
    .customer-info-header {
        color: #1565c0;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 15px;
        border-bottom: 2px solid #1976d2;
        padding-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Case Details Card
    st.markdown('<div class="case-details-card">', unsafe_allow_html=True)
    st.markdown('<div class="case-details-header">📄 Case Details</div>', unsafe_allow_html=True)
    
    # Safe value extraction with defaults (handle both dict and sqlite3.Row)
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
    
    case_id = safe_get(case_details, 'case_id')
    lan = safe_get(case_details, 'lan')
    case_type = safe_get(case_details, 'case_type')
    product = safe_get(case_details, 'product')
    region = safe_get(case_details, 'region')
    referred_by = safe_get(case_details, 'referred_by')
    status = safe_get(case_details, 'status')
    case_date = safe_get(case_details, 'case_date')
    case_description = safe_get(case_details, 'case_description')
    
    # Format case date
    formatted_case_date = format_datetime(case_date) if case_date != 'N/A' else 'N/A'
    
    st.markdown(f"""
    <div class="case-info-grid">
        <div class="case-info-item">
            <div class="case-info-label">Case ID</div>
            <div class="case-info-value">{case_id}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">LAN</div>
            <div class="case-info-value">{lan}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Case Type</div>
            <div class="case-info-value">{case_type}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Product</div>
            <div class="case-info-value">{product}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Region</div>
            <div class="case-info-value">{region}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Referred By</div>
            <div class="case-info-value">{referred_by}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Status</div>
            <div class="case-info-value"><span style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);">{status}</span></div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Case Date</div>
            <div class="case-info-value">{formatted_case_date}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="case-description">
        <div class="case-info-label" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">📝 Case Description</div>
        <div class="case-info-value" style="margin-top: 12px; line-height: 1.6; font-size: 15px; padding: 15px; background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%); border: 1px solid #d4edda; font-style: italic;">{case_description}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_standardized_customer_info(case_details):
    """
    Display customer information in standardized format
    """
    # Customer Info Card
    st.markdown('<div class="customer-info-card">', unsafe_allow_html=True)
    st.markdown('<div class="customer-info-header">👤 Customer Information</div>', unsafe_allow_html=True)
    
    # Safe value extraction with defaults (handle both dict and sqlite3.Row)
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
    
    customer_name = safe_get(case_details, 'customer_name')
    customer_mobile = safe_get(case_details, 'customer_mobile')
    customer_email = safe_get(case_details, 'customer_email')
    customer_pan = safe_get(case_details, 'customer_pan')
    customer_dob = safe_get(case_details, 'customer_dob')
    branch_location = safe_get(case_details, 'branch_location')
    loan_amount = safe_get(case_details, 'loan_amount') or 0
    disbursement_date = safe_get(case_details, 'disbursement_date')
    
    # Format values
    formatted_dob = format_datetime(customer_dob) if customer_dob != 'N/A' else 'N/A'
    # Convert loan amount to float for comparison
    try:
        loan_amount_float = float(loan_amount) if loan_amount else 0
        formatted_loan_amount = f"₹{loan_amount_float:,.2f}" if loan_amount_float > 0 else 'N/A'
    except (ValueError, TypeError):
        formatted_loan_amount = 'N/A'
    formatted_disbursement = format_datetime(disbursement_date) if disbursement_date != 'N/A' else 'N/A'
    
    st.markdown(f"""
    <div class="case-info-grid">
        <div class="case-info-item">
            <div class="case-info-label">Customer Name</div>
            <div class="case-info-value">{customer_name}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Mobile Number</div>
            <div class="case-info-value">{customer_mobile}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Email Address</div>
            <div class="case-info-value">{customer_email}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">PAN Number</div>
            <div class="case-info-value">{customer_pan}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Date of Birth</div>
            <div class="case-info-value">{formatted_dob}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Branch/Location</div>
            <div class="case-info-value">{branch_location}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Loan Amount</div>
            <div class="case-info-value" style="color: #28a745; font-weight: 700; font-size: 18px; background: linear-gradient(135deg, #d4edda 0%, #ffffff 100%); border: 2px solid #28a745; text-align: center;">{formatted_loan_amount}</div>
        </div>
        <div class="case-info-item">
            <div class="case-info-label">Disbursement Date</div>
            <div class="case-info-value">{formatted_disbursement}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_standardized_case_history(case_id):
    """
    Display case history/comments in standardized format
    """
    from models import get_case_comments
    
    st.markdown("""
    <style>
    .history-item {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #007bff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .history-header {
        font-weight: 600;
        color: #495057;
        font-size: 14px;
        margin-bottom: 6px;
    }
    .history-content {
        color: #212529;
        font-size: 13px;
        line-height: 1.4;
        background: white;
        padding: 8px;
        border-radius: 4px;
        border: 1px solid #e9ecef;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💬 Case History")
    comments = get_case_comments(case_id)
    if comments:
        for comment in comments[-5:]:  # Show last 5 comments
            # Handle both dict and sqlite3.Row objects  
            try:
                if hasattr(comment, 'keys') and hasattr(comment, '__getitem__'):
                    comment_type = comment['comment_type'] if 'comment_type' in comment.keys() else 'Comment'
                elif hasattr(comment, 'get'):
                    comment_type = comment.get('comment_type', 'Comment')
                else:
                    comment_type = getattr(comment, 'comment_type', 'Comment')
            except (KeyError, AttributeError, TypeError):
                comment_type = 'Comment'
            st.markdown(f"""
            <div class="history-item">
                <div class="history-header">👤 {comment['created_by']} • 📅 {format_datetime(comment['created_at'])} • 🏷️ {comment_type}</div>
                <div class="history-content">{comment['comment']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No case history available")

def show_standardized_documents(case_id):
    """
    Display supporting documents in standardized format
    """
    from models import get_case_documents
    from utils import format_file_size
    
    st.markdown("""
    <style>
    .document-item {
        background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
        border-radius: 8px;
        padding: 10px;
        margin: 6px 0;
        border-left: 4px solid #2196f3;
        box-shadow: 0 2px 4px rgba(33, 150, 243, 0.1);
    }
    .document-name {
        font-weight: 600;
        color: #1976d2;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .document-details {
        font-size: 12px;
        color: #666;
        background: white;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    documents = get_case_documents(case_id)
    if documents:
        st.markdown("### 📎 Supporting Documents")
        for doc in documents:
            st.markdown(f"""
            <div class="document-item">
                <div class="document-name">📄 {doc['original_filename']}</div>
                <span class="document-details">📊 {format_file_size(doc['file_size'])}</span>
                <span class="document-details">📅 {format_datetime(doc['uploaded_at'])}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No supporting documents available")