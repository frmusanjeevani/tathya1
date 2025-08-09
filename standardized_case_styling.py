"""
Standardized case display styling system for consistent text size and box formatting
across all pages in the Tathya application
"""
import streamlit as st

def apply_standardized_case_styling():
    """Apply consistent case display styling across all pages"""
    st.markdown("""
    <style>
    /* Standard Case Display Box */
    .standard-case-box {
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin: 10px 0;
        font-size: 16px;
        color: #333333;
        font-weight: 500;
        line-height: 1.5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Case ID Display - Primary format */
    .case-id-display {
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin: 10px 0;
        font-size: 16px;
        color: #333333;
        font-weight: 600;
        line-height: 1.5;
    }
    
    /* Case Details Text Box */
    .case-details-text {
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 16px;
        color: #333333;
        font-weight: 500;
        line-height: 1.4;
    }
    
    /* Sub-information styling */
    .case-sub-info {
        font-size: 14px;
        color: #666;
        margin-top: 6px;
    }
    
    /* Text input standardization */
    .stTextInput > div > div > input {
        font-size: 16px !important;
        color: #333333 !important;
        background: #f5f5f5 !important;
        border: 1px solid #ddd !important;
        padding: 12px 16px !important;
    }
    
    /* Text area standardization */
    .stTextArea > div > div > textarea {
        font-size: 16px !important;
        color: #333333 !important;
        background: #f5f5f5 !important;
        border: 1px solid #ddd !important;
        padding: 12px 16px !important;
    }
    
    /* Select box standardization */
    .stSelectbox > div > div > select {
        font-size: 16px !important;
        color: #333333 !important;
        background: #f5f5f5 !important;
        border: 1px solid #ddd !important;
    }
    
    /* Multiselect standardization */
    .stMultiSelect > div > div {
        font-size: 16px !important;
        color: #333333 !important;
        background: #f5f5f5 !important;
        border: 1px solid #ddd !important;
    }
    </style>
    """, unsafe_allow_html=True)

def create_standard_case_display(case_id, customer_name, case_type, amount, additional_info=""):
    """Create standardized case display format used across all pages"""
    case_display_text = f"{case_id} - {customer_name} ({case_type}) - ₹{amount}"
    
    html_content = f"""
    <div class='case-id-display'>
        <strong>{case_display_text}</strong>
        {f"<div class='case-sub-info'>{additional_info}</div>" if additional_info else ""}
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)

def create_standard_text_box(content, box_type="default"):
    """Create standardized text box with consistent formatting"""
    css_class = "standard-case-box" if box_type == "default" else "case-details-text"
    
    st.markdown(f"""
    <div class='{css_class}'>
        {content}
    </div>
    """, unsafe_allow_html=True)