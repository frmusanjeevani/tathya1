"""
Standardized Page Format Template based on Case Allocation page
Provides consistent page structure across all workflow stages
"""
import streamlit as st
from standardized_case_styling import apply_standardized_case_styling, create_standard_case_display

def create_standardized_page_header(page_title, subtitle=None):
    """Create standardized page header with Investigation Intelligence branding"""
    
    # Apply standardized styling
    apply_standardized_case_styling()
    
    # Main Investigation Intelligence Header
    st.markdown("""
    <div style='
        text-align: center;
        margin: 15px 0 25px 0;
        padding: 10px;
    '>
        <h1 style='
            font-size: 2.4rem;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 8px;
            letter-spacing: 0.5px;
            font-family: "Segoe UI", Arial, sans-serif;
        '>🕵️‍♂️ Tathya Investigation Intelligence</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Page-specific sub-header
    st.markdown(f"""
    <div style='
        text-align: left;
        margin: 10px 0 20px 0;
        padding: 8px 0;
        border-bottom: 2px solid #e1e5e9;
    '>
        <h2 style='
            font-size: 1.5rem;
            font-weight: 600;
            color: #2c3e50;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: "Segoe UI", Arial, sans-serif;
        '>{page_title}</h2>
        {f'<p style="color: #666; margin: 5px 0 0 0; font-size: 14px;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_case_information_section(case_data, show_flow_data=True):
    """Create standardized Case Information section"""
    from data_flow_manager import show_previous_stage_summary, show_workflow_progress_tracker
    
    st.markdown("### 📄 Case Information")
    
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
    
    case_id = safe_get(case_data, 'case_id')
    customer_name = safe_get(case_data, 'customer_name')
    case_type = safe_get(case_data, 'case_type')
    loan_amount = safe_get(case_data, 'loan_amount', 0)
    
    # Format amount
    try:
        loan_amount_float = float(loan_amount) if loan_amount else 0
        formatted_loan = f"{loan_amount_float:,.0f}" if loan_amount_float > 0 else 'N/A'
    except (ValueError, TypeError):
        formatted_loan = 'N/A'
    
    # Case ID section with standardized display
    st.markdown("#### Case ID")
    create_standard_case_display(case_id, customer_name, case_type, formatted_loan, 
                               f"Product: {safe_get(case_data, 'product')} | Region: {safe_get(case_data, 'region')}")
    
    # Basic case details in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Details")
        st.markdown(f"""
        <div class='case-details-text'>
            <strong>LAN:</strong> {safe_get(case_data, 'lan')}<br>
            <strong>Product:</strong> {safe_get(case_data, 'product')}<br>
            <strong>Region:</strong> {safe_get(case_data, 'region')}<br>
            <strong>Branch:</strong> {safe_get(case_data, 'branch_location')}<br>
            <strong>Referred By:</strong> {safe_get(case_data, 'referred_by')}<br>
            <strong>Status:</strong> {safe_get(case_data, 'status')}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Customer Information")
        st.markdown(f"""
        <div class='case-details-text'>
            <strong>Name:</strong> {customer_name}<br>
            <strong>Mobile:</strong> {safe_get(case_data, 'customer_mobile')}<br>
            <strong>Email:</strong> {safe_get(case_data, 'customer_email')}<br>
            <strong>PAN:</strong> {safe_get(case_data, 'customer_pan')}<br>
            <strong>Occupation:</strong> {safe_get(case_data, 'customer_occupation')}<br>
            <strong>Income:</strong> ₹{safe_get(case_data, 'customer_income')}
        </div>
        """, unsafe_allow_html=True)
    
    # Show workflow progress and previous stage data if requested
    if show_flow_data:
        st.divider()
        show_workflow_progress_tracker(case_id)
        st.divider()
        show_previous_stage_summary(case_id, "Current Stage")

def create_standardized_case_section(case_data, section_title, additional_info=""):
    """Create a standardized case section with consistent formatting"""
    
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
    
    case_id = safe_get(case_data, 'case_id')
    customer_name = safe_get(case_data, 'customer_name')
    case_type = safe_get(case_data, 'case_type')
    loan_amount = safe_get(case_data, 'loan_amount', 0)
    
    # Format amount
    try:
        loan_amount_float = float(loan_amount) if loan_amount else 0
        formatted_loan = f"{loan_amount_float:,.0f}" if loan_amount_float > 0 else 'N/A'
    except (ValueError, TypeError):
        formatted_loan = 'N/A'
    
    # Create standardized case display
    with st.expander(f"{section_title}: {case_id} - {customer_name} ({case_type}) - ₹{formatted_loan}", expanded=False):
        create_case_information_section(case_data)
        
        if additional_info:
            st.markdown(additional_info)
        
        return case_data

def create_stage_interaction_section(stage_name, current_user):
    """Create standardized interaction section for a workflow stage"""
    from interaction_channels import show_interaction_requests_section, create_interaction_request_form
    
    st.divider()
    
    # Show pending interaction requests
    show_interaction_requests_section(stage_name, current_user)

def create_standardized_form_section(title, form_fields, case_id, stage_name, current_user):
    """Create a standardized form section"""
    from data_flow_manager import create_stage_data_form
    
    st.markdown(f"### {title}")
    
    return create_stage_data_form(case_id, stage_name, current_user, form_fields)

def create_action_buttons_section(case_id, stage_name, actions_config):
    """Create standardized action buttons section"""
    st.markdown("### 🎯 Actions")
    
    cols = st.columns(len(actions_config))
    
    for i, (action_key, action_config) in enumerate(actions_config.items()):
        with cols[i]:
            button_type = action_config.get('type', 'secondary')
            if st.button(action_config['label'], key=f"{stage_name}_{action_key}_{case_id}", type=button_type):
                return action_key
    
    return None

def standardize_page_layout(page_title, subtitle=None):
    """Apply standardized page layout and return helper functions"""
    
    # Create header
    create_standardized_page_header(page_title, subtitle)
    
    # Return helper functions for consistent usage
    return {
        'create_case_section': create_standardized_case_section,
        'create_info_section': create_case_information_section,
        'create_interaction_section': create_stage_interaction_section,
        'create_form_section': create_standardized_form_section,
        'create_actions_section': create_action_buttons_section
    }

def show_standardized_case_list(cases, stage_name, current_user, case_handler_function):
    """Show standardized list of cases for a workflow stage"""
    
    if not cases:
        st.info(f"📭 No cases available for {stage_name}")
        return
    
    st.markdown(f"### 📋 Cases for {stage_name}")
    st.markdown(f"*{len(cases)} case(s) available*")
    
    for case in cases:
        case_section = create_standardized_case_section(
            case, 
            f"📋 {stage_name}",
            f"Available for {stage_name.lower()} processing"
        )
        
        # Call the specific handler function for this case
        case_handler_function(case, current_user)

def create_workflow_status_indicator(current_status, available_actions):
    """Create workflow status indicator"""
    
    status_colors = {
        'Draft': '#6c757d',
        'Submitted': '#007bff', 
        'Under Investigation': '#17a2b8',
        'Agency Investigation': '#ffc107',
        'Regional Investigation': '#fd7e14',
        'Primary Review': '#28a745',
        'Under Review': '#28a745',
        'Approved': '#20c997',
        'Approver 2': '#6f42c1',
        'Final Review': '#e83e8c',
        'Legal Review': '#dc3545',
        'Closed': '#343a40'
    }
    
    color = status_colors.get(current_status, '#6c757d')
    
    st.markdown(f"""
    <div style='
        background: {color};
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
        font-size: 14px;
    '>
        Current Status: {current_status}
    </div>
    """, unsafe_allow_html=True)
    
    if available_actions:
        st.markdown("**Available Actions:**")
        for action in available_actions:
            st.markdown(f"• {action}")

# Template form fields for different stages
STAGE_FORM_FIELDS = {
    "Case Allocation": {
        "allocation_type": {
            "type": "select",
            "label": "Allocation Type", 
            "options": ["Internal Investigation", "Agency Investigation", "Regional Investigation"]
        },
        "assigned_investigator": {
            "type": "text",
            "label": "Assigned Investigator"
        },
        "priority_level": {
            "type": "select",
            "label": "Priority Level",
            "options": ["Low", "Medium", "High", "Critical"]
        },
        "allocation_notes": {
            "type": "textarea",
            "label": "Allocation Notes"
        }
    },
    
    "Primary Review": {
        "review_outcome": {
            "type": "select",
            "label": "Review Outcome",
            "options": ["Approved", "Requires Clarification", "Rejected", "Refer to Approver"]
        },
        "risk_assessment": {
            "type": "select", 
            "label": "Risk Assessment",
            "options": ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
        },
        "review_comments": {
            "type": "textarea",
            "label": "Review Comments"
        },
        "recommended_action": {
            "type": "text",
            "label": "Recommended Action"
        }
    },
    
    "Agency Investigation": {
        "investigation_status": {
            "type": "select",
            "label": "Investigation Status",
            "options": ["In Progress", "Completed", "Requires Additional Info"]
        },
        "findings": {
            "type": "textarea",
            "label": "Investigation Findings"
        },
        "risk_factors": {
            "type": "multiselect",
            "label": "Risk Factors",
            "options": ["Document Issues", "Identity Problems", "Income Discrepancy", "Address Issues", "Reference Problems"]
        }
    },
    
    "Regional Investigation": {
        "verification_status": {
            "type": "select",
            "label": "Verification Status", 
            "options": ["Verified", "Partially Verified", "Discrepancies Found", "Unable to Verify"]
        },
        "site_visit_conducted": {
            "type": "select",
            "label": "Site Visit Conducted",
            "options": ["Yes", "No", "Not Required"]
        },
        "verification_report": {
            "type": "textarea",
            "label": "Verification Report"
        }
    }
}