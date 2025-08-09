"""
Light Professional Styling Module for Tathya Case Management System
Provides consistent light professional color scheme throughout the application
"""

def get_light_professional_css():
    """Returns CSS for light professional styling"""
    return """
    <style>
    /* Global Light Professional Theme */
    .light-professional-table {
        background: #ffffff;
        border: 1px solid #e8eaed;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        overflow: hidden;
    }
    
    .light-professional-header {
        background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%) !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 10px !important;
        font-size: 13px !important;
        text-align: center !important;
    }
    
    .light-professional-cell {
        padding: 8px 10px !important;
        border-bottom: 1px solid #f1f3f4 !important;
        color: #3c4043 !important;
        font-size: 12px !important;
        text-align: center !important;
    }
    
    .light-professional-row:hover {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%) !important;
    }
    
    .light-case-id {
        font-weight: 500 !important;
        color: #1a73e8 !important;
    }
    
    .light-status-badge {
        padding: 4px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 500;
        color: white;
        background: linear-gradient(135deg, #34a853 0%, #137333 100%);
        text-transform: uppercase;
    }
    
    .light-metric-card {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
        border: 1px solid #e8eaed;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    .light-metric-card:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
        border-color: #4285f4;
    }
    
    .light-case-details {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
        border-radius: 10px;
        padding: 18px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid #e8eaed;
    }
    
    .light-case-info-label {
        background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%);
        color: white;
        padding: 4px 8px;
        border-radius: 3px;
        text-align: center;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    .light-case-info-value {
        color: #3c4043;
        font-size: 14px;
        font-weight: 500;
        background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
        padding: 6px 10px;
        border-radius: 4px;
        border: 1px solid #f1f3f4;
        margin-top: 3px;
    }
    
    /* Override Streamlit dataframe styling */
    div[data-testid="stDataFrame"] table thead th {
        background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%) !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 10px !important;
        font-size: 13px !important;
    }
    
    div[data-testid="stDataFrame"] table tbody td {
        padding: 8px 10px !important;
        border-bottom: 1px solid #f1f3f4 !important;
        color: #3c4043 !important;
        font-size: 12px !important;
    }
    
    div[data-testid="stDataFrame"] table tbody tr:hover {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%) !important;
    }
    
    /* Case review sections */
    .review-section {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
        border: 1px solid #e8eaed;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    
    .review-header {
        color: #5f6368;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 12px;
        border-bottom: 1px solid #dadce0;
        padding-bottom: 6px;
    }
    
    /* Expandable sections */
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%) !important;
        border: 1px solid #e8eaed !important;
        border-radius: 6px !important;
    }
    
    .stExpander > div:first-child:hover {
        background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%) !important;
        border-color: #4285f4 !important;
    }
    
    /* Left-align navigation button text in sidebar */
    .stSidebar .stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 12px !important;
    }
    
    /* Left-align text in expandable sections */
    .stSidebar .stExpander .stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 12px !important;
    }
    </style>
    """

def apply_light_professional_styling():
    """Apply light professional styling to Streamlit components"""
    import streamlit as st
    st.markdown(get_light_professional_css(), unsafe_allow_html=True)

def get_light_professional_table_style():
    """Get light professional table styling for pandas DataFrames"""
    return [
        {'selector': 'thead th', 'props': [
            ('background', 'linear-gradient(135deg, #4285f4 0%, #1a73e8 100%)'),
            ('color', 'white'),
            ('font-weight', '500'),
            ('text-align', 'center'),
            ('padding', '10px'),
            ('font-size', '13px')
        ]},
        {'selector': 'tbody td', 'props': [
            ('padding', '8px 10px'),
            ('text-align', 'center'),
            ('border-bottom', '1px solid #f1f3f4'),
            ('color', '#3c4043'),
            ('font-size', '12px')
        ]},
        {'selector': 'tbody tr:hover', 'props': [
            ('background', 'linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%)')
        ]}
    ]

def style_case_id_light(val):
    """Light professional styling for Case ID columns"""
    return 'font-weight: 500; color: #1a73e8;'

def create_light_professional_html_table(data, headers):
    """Create HTML table with light professional styling"""
    html = "<table class='light-professional-table' style='width:100%; border-collapse: collapse;'>"
    
    # Headers
    html += "<thead><tr>"
    for header in headers:
        html += f"<th class='light-professional-header'>{header}</th>"
    html += "</tr></thead>"
    
    # Body
    html += "<tbody>"
    for row in data:
        html += "<tr class='light-professional-row'>"
        for i, cell in enumerate(row):
            if i == 0:  # First column (usually Case ID)
                html += f"<td class='light-professional-cell light-case-id'>{cell}</td>"
            else:
                html += f"<td class='light-professional-cell'>{cell}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    
    return html