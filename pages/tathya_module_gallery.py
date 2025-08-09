"""
Tathya Module Gallery - Interactive API Module Showcase
Advanced module browser with detailed configurations and live previews
"""

import streamlit as st
from auth import is_authenticated, get_current_user

def show():
    """Display the interactive module gallery"""
    
    st.markdown("""
    <style>
    .gallery-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #a0c4ff 100%);
        color: white;
        text-align: center;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .module-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }
    
    .module-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 16px;
        padding: 25px;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
    }
    
    .module-card:hover {
        transform: translateY(-8px);
        border-color: #667eea;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
    }
    
    .module-icon {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 15px;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    
    .module-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .module-description {
        color: #6c757d;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .module-features {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 0.85rem;
    }
    
    .module-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .category-filter {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
    }
    
    .filter-button {
        background: white;
        border: 2px solid #dee2e6;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        font-weight: 500;
    }
    
    .filter-button.active {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border-color: #667eea;
    }
    
    .filter-button:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="gallery-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800;">📦 Module Gallery</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Explore & Configure API Modules</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not is_authenticated():
        st.error("Please log in to access Module Gallery")
        return
    
    # Category filter
    show_category_filter()
    
    # Module grid
    show_module_grid()

def show_category_filter():
    """Display category filter buttons"""
    
    categories = [
        {"name": "All", "icon": "🌟", "key": "all"},
        {"name": "Identity & KYC", "icon": "🆔", "key": "identity"},
        {"name": "Financial", "icon": "💰", "key": "financial"},
        {"name": "Digital", "icon": "🌐", "key": "digital"},
        {"name": "Analytics", "icon": "⚡", "key": "analytics"}
    ]
    
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = 'all'
    
    st.markdown('<div class="category-filter">', unsafe_allow_html=True)
    
    cols = st.columns(len(categories))
    for idx, category in enumerate(categories):
        with cols[idx]:
            if st.button(f"{category['icon']} {category['name']}", 
                        key=f"filter_{category['key']}", 
                        use_container_width=True):
                st.session_state.selected_category = category['key']
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_module_grid():
    """Display the interactive module grid"""
    
    modules = get_all_modules()
    
    # Filter modules based on selected category
    if st.session_state.selected_category != 'all':
        modules = [m for m in modules if m['category'] == st.session_state.selected_category]
    
    # Display modules in grid
    st.markdown('<div class="module-grid">', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, module in enumerate(modules):
        col_idx = idx % 3
        with cols[col_idx]:
            show_module_card(module, idx)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_module_card(module, idx):
    """Display an individual module card"""
    
    card_key = f"module_{idx}"
    
    # Module card HTML
    st.markdown(f"""
    <div class="module-card" id="{card_key}">
        <div class="module-badge">{module['type']}</div>
        <div class="module-icon">{module['icon']}</div>
        <div class="module-title">{module['name']}</div>
        <div class="module-description">{module['description']}</div>
        <div class="module-features">
            <strong>Features:</strong><br>
            {' • '.join(module['features'])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👁️ Preview", key=f"preview_{idx}", use_container_width=True):
            show_module_preview(module)
    with col2:
        if st.button("⚙️ Configure", key=f"configure_{idx}", use_container_width=True):
            show_module_config(module)
    with col3:
        if st.button("➕ Add to Builder", key=f"add_{idx}", use_container_width=True):
            add_to_builder(module)

def show_module_preview(module):
    """Show module preview with sample data"""
    
    st.markdown("---")
    st.markdown(f"### 👁️ Preview: {module['name']}")
    
    with st.expander("Module Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information:**")
            st.info(f"**Name:** {module['name']}")
            st.info(f"**Category:** {module['category'].title()}")
            st.info(f"**Type:** {module['type']}")
            st.info(f"**Complexity:** {module.get('complexity', 'Medium')}")
        
        with col2:
            st.markdown("**API Specifications:**")
            st.info(f"**Method:** {module.get('method', 'POST')}")
            st.info(f"**Response Time:** {module.get('response_time', '< 2s')}")
            st.info(f"**Success Rate:** {module.get('success_rate', '99.5%')}")
            st.info(f"**Rate Limit:** {module.get('rate_limit', '1000/hour')}")
        
        st.markdown("**Sample Input/Output:**")
        
        if module['category'] == 'identity':
            st.code("""
# Sample Input
{
  "document_number": "ABCDE1234F",
  "document_type": "PAN"
}

# Sample Output
{
  "status": "valid",
  "name": "John Doe",
  "verification_score": 0.95,
  "timestamp": "2025-01-04T10:30:00Z"
}
            """, language='json')
        
        elif module['category'] == 'financial':
            st.code("""
# Sample Input
{
  "account_number": "1234567890",
  "ifsc_code": "SBIN0001234"
}

# Sample Output
{
  "account_status": "active",
  "bank_name": "State Bank of India",
  "account_type": "savings",
  "kyc_compliant": true
}
            """, language='json')

def show_module_config(module):
    """Show module configuration interface"""
    
    st.markdown("---")
    st.markdown(f"### ⚙️ Configure: {module['name']}")
    
    with st.expander("Configuration Settings", expanded=True):
        
        # API Configuration
        st.markdown("**API Configuration:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("API Endpoint", 
                         value=f"https://api.tathya.com/{module['category']}/{module['name'].lower().replace(' ', '-')}",
                         key=f"config_endpoint_{module['name']}")
            st.selectbox("HTTP Method", ["POST", "GET", "PUT", "PATCH"], 
                        index=0 if module.get('method', 'POST') == 'POST' else 1,
                        key=f"config_method_{module['name']}")
            st.text_input("API Key", type="password", key=f"config_key_{module['name']}")
        
        with col2:
            st.number_input("Timeout (seconds)", min_value=1, max_value=300, value=30,
                           key=f"config_timeout_{module['name']}")
            st.number_input("Retry Attempts", min_value=0, max_value=5, value=2,
                           key=f"config_retry_{module['name']}")
            st.selectbox("Environment", ["Production", "Staging", "Development"],
                        key=f"config_env_{module['name']}")
        
        # Input Parameters
        st.markdown("**Input Parameters:**")
        params = module.get('parameters', [])
        
        for param in params:
            pcol1, pcol2, pcol3 = st.columns([2, 1, 1])
            with pcol1:
                st.text_input(f"Parameter: {param['name']}", 
                             value=param.get('default', ''),
                             key=f"param_{module['name']}_{param['name']}")
            with pcol2:
                st.selectbox("Type", ["string", "number", "boolean"], 
                           index=["string", "number", "boolean"].index(param.get('type', 'string')),
                           key=f"type_{module['name']}_{param['name']}")
            with pcol3:
                st.checkbox("Required", value=param.get('required', False),
                           key=f"req_{module['name']}_{param['name']}")
        
        # Validation Rules
        st.markdown("**Validation Rules:**")
        st.checkbox("Enable input validation", value=True, key=f"validation_{module['name']}")
        st.checkbox("Log all requests", value=False, key=f"logging_{module['name']}")
        st.checkbox("Cache responses", value=True, key=f"caching_{module['name']}")
        
        if st.button("💾 Save Configuration", key=f"save_{module['name']}", use_container_width=True):
            st.success(f"Configuration saved for {module['name']}!")

def add_to_builder(module):
    """Add module to workflow builder"""
    
    # Initialize builder session if not exists
    if 'builder_modules' not in st.session_state:
        st.session_state.builder_modules = []
    
    # Add module to builder
    builder_module = {
        "name": module['name'],
        "icon": module['icon'],
        "category": module['category'],
        "type": module['type'],
        "id": len(st.session_state.builder_modules)
    }
    
    st.session_state.builder_modules.append(builder_module)
    st.success(f"Added {module['name']} to Workflow Builder!")
    
    if st.button("🎨 Open Workflow Builder", key=f"open_builder_{module['name']}"):
        st.session_state.current_page = "Tathya Lab Builder"
        st.rerun()

def get_all_modules():
    """Return all available modules with detailed specifications"""
    
    return [
        # Identity & KYC Modules
        {
            "name": "PAN Verification",
            "icon": "🏦",
            "category": "identity",
            "type": "AI",
            "description": "Real-time PAN validation with fraud detection and authenticity scoring using advanced AI algorithms",
            "features": ["Real-time validation", "Fraud detection", "Name matching", "Format verification"],
            "complexity": "Medium",
            "method": "POST",
            "response_time": "< 1.5s",
            "success_rate": "99.8%",
            "rate_limit": "2000/hour",
            "parameters": [
                {"name": "pan_number", "type": "string", "required": True, "default": ""},
                {"name": "name_match", "type": "boolean", "required": False, "default": "false"},
                {"name": "include_details", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        {
            "name": "Aadhaar Analytics",
            "icon": "🆔",
            "category": "identity",
            "type": "ML",
            "description": "Comprehensive Aadhaar verification with OCR extraction and advanced validation algorithms",
            "features": ["OCR extraction", "Mask validation", "Address parsing", "Demographic analysis"],
            "complexity": "High",
            "method": "POST",
            "response_time": "< 3s",
            "success_rate": "99.2%",
            "rate_limit": "1500/hour",
            "parameters": [
                {"name": "aadhaar_number", "type": "string", "required": True, "default": ""},
                {"name": "verify_otp", "type": "boolean", "required": False, "default": "false"},
                {"name": "extract_details", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        {
            "name": "Face Match AI",
            "icon": "🧬",
            "category": "identity",
            "type": "CV",
            "description": "Advanced biometric verification using multiple deep learning models for accurate face matching",
            "features": ["Multi-model analysis", "Liveness detection", "Confidence scoring", "Anti-spoofing"],
            "complexity": "High",
            "method": "POST",
            "response_time": "< 4s",
            "success_rate": "98.9%",
            "rate_limit": "1000/hour",
            "parameters": [
                {"name": "reference_image", "type": "string", "required": True, "default": ""},
                {"name": "comparison_image", "type": "string", "required": True, "default": ""},
                {"name": "liveness_check", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        
        # Financial Modules
        {
            "name": "Bank Statement AI",
            "icon": "📊",
            "category": "financial",
            "type": "AI",
            "description": "Intelligent analysis of bank statements with transaction pattern recognition and risk scoring",
            "features": ["Pattern analysis", "Risk scoring", "Income calculation", "Expense categorization"],
            "complexity": "High",
            "method": "POST",
            "response_time": "< 5s",
            "success_rate": "97.8%",
            "rate_limit": "500/hour",
            "parameters": [
                {"name": "statement_file", "type": "string", "required": True, "default": ""},
                {"name": "analysis_period", "type": "number", "required": False, "default": "6"},
                {"name": "include_patterns", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        {
            "name": "UPI Intelligence",
            "icon": "💳",
            "category": "financial",
            "type": "ML",
            "description": "Real-time UPI ID verification with transaction behavior analysis and fraud detection",
            "features": ["ID validation", "Behavior analysis", "Fraud detection", "Transaction history"],
            "complexity": "Medium",
            "method": "POST",
            "response_time": "< 2s",
            "success_rate": "99.1%",
            "rate_limit": "1800/hour",
            "parameters": [
                {"name": "upi_id", "type": "string", "required": True, "default": ""},
                {"name": "verify_active", "type": "boolean", "required": False, "default": "true"},
                {"name": "fraud_check", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        {
            "name": "Credit Analytics",
            "icon": "📈",
            "category": "financial",
            "type": "AI",
            "description": "Advanced credit assessment using bureau data analysis and predictive modeling",
            "features": ["Credit scoring", "Risk assessment", "Bureau integration", "Predictive analysis"],
            "complexity": "High",
            "method": "POST",
            "response_time": "< 3s",
            "success_rate": "98.5%",
            "rate_limit": "1200/hour",
            "parameters": [
                {"name": "applicant_details", "type": "string", "required": True, "default": ""},
                {"name": "bureau_check", "type": "boolean", "required": False, "default": "true"},
                {"name": "predictive_score", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        
        # Digital Intelligence Modules
        {
            "name": "Mobile Intelligence",
            "icon": "📱",
            "category": "digital",
            "type": "AI",
            "description": "Advanced mobile number verification with carrier data analysis and fraud detection",
            "features": ["Carrier verification", "Port history", "Fraud detection", "MNRL checking"],
            "complexity": "Medium",
            "method": "POST",
            "response_time": "< 2s",
            "success_rate": "99.3%",
            "rate_limit": "2500/hour",
            "parameters": [
                {"name": "mobile_number", "type": "string", "required": True, "default": ""},
                {"name": "carrier_check", "type": "boolean", "required": False, "default": "true"},
                {"name": "mnrl_verify", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        {
            "name": "Email Analytics",
            "icon": "📧",
            "category": "digital",
            "type": "ML",
            "description": "Comprehensive email verification with domain analysis and authenticity scoring",
            "features": ["Domain verification", "Deliverability check", "Risk scoring", "Disposable detection"],
            "complexity": "Low",
            "method": "POST",
            "response_time": "< 1s",
            "success_rate": "99.7%",
            "rate_limit": "3000/hour",
            "parameters": [
                {"name": "email_address", "type": "string", "required": True, "default": ""},
                {"name": "domain_check", "type": "boolean", "required": False, "default": "true"},
                {"name": "deliverability", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        {
            "name": "Device Fingerprinting",
            "icon": "🖥️",
            "category": "digital",
            "type": "AI",
            "description": "Advanced device identification using machine learning and behavioral pattern analysis",
            "features": ["Device profiling", "Behavior analysis", "Fraud detection", "Session tracking"],
            "complexity": "High",
            "method": "POST",
            "response_time": "< 2.5s",
            "success_rate": "98.2%",
            "rate_limit": "1500/hour",
            "parameters": [
                {"name": "device_data", "type": "string", "required": True, "default": ""},
                {"name": "behavior_analysis", "type": "boolean", "required": False, "default": "true"},
                {"name": "fraud_scoring", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        
        # Advanced Analytics Modules
        {
            "name": "Fraud Intelligence",
            "icon": "🧠",
            "category": "analytics",
            "type": "AI",
            "description": "Next-generation fraud detection using ensemble models and anomaly detection algorithms",
            "features": ["Ensemble models", "Anomaly detection", "Risk scoring", "Real-time analysis"],
            "complexity": "Very High",
            "method": "POST",
            "response_time": "< 3s",
            "success_rate": "97.5%",
            "rate_limit": "800/hour",
            "parameters": [
                {"name": "transaction_data", "type": "string", "required": True, "default": ""},
                {"name": "model_ensemble", "type": "boolean", "required": False, "default": "true"},
                {"name": "anomaly_threshold", "type": "number", "required": False, "default": "0.8"}
            ]
        },
        {
            "name": "Behavioral Analytics",
            "icon": "🎭",
            "category": "analytics",
            "type": "NLP",
            "description": "Deep behavioral pattern analysis using natural language processing and sentiment analysis",
            "features": ["Pattern recognition", "Sentiment analysis", "Behavior modeling", "Risk profiling"],
            "complexity": "High",
            "method": "POST",
            "response_time": "< 4s",
            "success_rate": "96.8%",
            "rate_limit": "600/hour",
            "parameters": [
                {"name": "user_data", "type": "string", "required": True, "default": ""},
                {"name": "sentiment_analysis", "type": "boolean", "required": False, "default": "true"},
                {"name": "behavior_score", "type": "boolean", "required": False, "default": "true"}
            ]
        },
        {
            "name": "Predictive Analytics",
            "icon": "🔮",
            "category": "analytics",
            "type": "AI",
            "description": "Advanced predictive modeling for risk assessment and fraud prevention using AI algorithms",
            "features": ["Predictive modeling", "Risk forecasting", "Trend analysis", "ML algorithms"],
            "complexity": "Very High",
            "method": "POST",
            "response_time": "< 5s",
            "success_rate": "95.9%",
            "rate_limit": "400/hour",
            "parameters": [
                {"name": "historical_data", "type": "string", "required": True, "default": ""},
                {"name": "prediction_horizon", "type": "number", "required": False, "default": "30"},
                {"name": "confidence_level", "type": "number", "required": False, "default": "0.95"}
            ]
        }
    ]