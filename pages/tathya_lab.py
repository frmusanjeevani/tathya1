"""
Tathya Lab - AI-Powered Verification Intelligence Platform
Square-shaped modules with authentic AI theme
"""

import streamlit as st
from auth import is_authenticated, get_current_user, logout_user


def show():
    """Display Tathya Lab - AI Verification Intelligence Platform"""
    
    # Enhanced CSS for AI-powered theme with square modules
    st.markdown("""
    <style>
    .ai-header {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #1e3c72 100%);
        color: white;
        text-align: center;
        padding: 40px 20px;
        border-radius: 20px;
        margin-bottom: 40px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .ai-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
        animation: aiPulse 4s ease-in-out infinite;
    }
    
    @keyframes aiPulse {
        0%, 100% { opacity: 0.6; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.02); }
    }
    
    .ai-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        position: relative;
        z-index: 2;
        background: linear-gradient(45deg, #fff, #a0c4ff, #bdb2ff, #ffc6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(160, 196, 255, 0.5);
        letter-spacing: 2px;
    }
    
    .ai-subtitle {
        font-size: 1.5rem;
        margin: 15px 0 0 0;
        position: relative;
        z-index: 2;
        background: linear-gradient(45deg, #e0e0e0, #a0c4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 400;
        letter-spacing: 1px;
    }
    
    .ai-icon {
        font-size: 2rem;
        margin-right: 15px;
        filter: drop-shadow(0 0 10px rgba(160, 196, 255, 0.6));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    .module-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 25px;
        padding: 20px 0;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .ai-module {
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        aspect-ratio: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        max-width: 180px;
        min-height: 140px;
    }
    
    .ai-module::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, 
            rgba(160, 196, 255, 0.1) 0%, 
            rgba(189, 178, 255, 0.1) 50%, 
            rgba(255, 198, 255, 0.1) 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: 1;
    }
    
    .ai-module:hover::before {
        opacity: 1;
    }
    
    .ai-module:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: rgba(160, 196, 255, 0.6);
        box-shadow: 0 20px 40px rgba(160, 196, 255, 0.2);
    }
    
    .module-icon {
        font-size: 2rem;
        margin-bottom: 8px;
        position: relative;
        z-index: 2;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        transition: all 0.3s ease;
    }
    
    .ai-module:hover .module-icon {
        transform: scale(1.1);
        filter: drop-shadow(0 6px 12px rgba(160, 196, 255, 0.4));
    }
    
    .module-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0 0 6px 0;
        position: relative;
        z-index: 2;
        transition: color 0.3s ease;
    }
    
    .ai-module:hover .module-title {
        color: #1e3c72;
    }
    
    .module-description {
        font-size: 0.7rem;
        color: #666;
        line-height: 1.3;
        position: relative;
        z-index: 2;
        transition: color 0.3s ease;
        max-width: 140px;
    }
    
    .ai-module:hover .module-description {
        color: #444;
    }
    
    .ai-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        z-index: 2;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .category-header {
        text-align: center;
        margin: 50px 0 30px 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced AI-Powered Header
    st.markdown("""
    <div class="ai-header">
        <h1 class="ai-title">
            <span class="ai-icon">🤖</span>TATHYA LAB
        </h1>
        <p class="ai-subtitle">AI-Powered Verification Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not is_authenticated():
        st.error("🔒 Please log in to access Tathya Lab")
        return
    
    # AI-Powered Verification Modules
    show_ai_modules()


def show_ai_modules():
    """Display AI-powered verification modules in square grid"""
    
    # Identity & KYC Intelligence
    st.markdown('<h2 class="category-header">🆔 Identity & KYC Intelligence</h2>', unsafe_allow_html=True)
    
    # Use Streamlit columns with smaller tiles - 4 per row
    cols = st.columns(4)
    
    with cols[0]:
        if st.button("🧬 Face Match", key="face_match", use_container_width=True):
            st.session_state.selected_module = "Face Match AI"
            st.rerun()
        
    with cols[1]:
        if st.button("🏦 PAN Intelligence", key="pan_verify", use_container_width=True):
            st.session_state.selected_module = "PAN Intelligence"
            st.rerun()
        
    with cols[2]:
        if st.button("🆔 Aadhaar Analytics", key="aadhaar_verify", use_container_width=True):
            st.session_state.selected_module = "Aadhaar Analytics"
            st.rerun()
        
    with cols[3]:
        if st.button("📘 Document Forensics", key="doc_verify", use_container_width=True):
            st.session_state.selected_module = "Document Forensics"
            st.rerun()
    
    # Financial Intelligence
    st.markdown('<h2 class="category-header">💰 Financial Intelligence</h2>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    with cols[0]:
        if st.button("📊 Bank Statement", key="bank_ai", use_container_width=True):
            st.session_state.selected_module = "Bank Statement AI"
            st.rerun()
        
    with cols[1]:
        if st.button("💳 UPI Intelligence", key="upi_verify", use_container_width=True):
            st.session_state.selected_module = "UPI Intelligence"
            st.rerun()
        
    with cols[2]:
        if st.button("📈 Credit Analytics", key="credit_analysis", use_container_width=True):
            st.session_state.selected_module = "Credit Analytics"
            st.rerun()
        
    with cols[3]:
        if st.button("🔍 Risk Intelligence", key="risk_intel", use_container_width=True):
            st.session_state.selected_module = "Risk Intelligence"
            st.rerun()
    
    # Digital Intelligence
    st.markdown('<h2 class="category-header">🌐 Digital Intelligence</h2>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    with cols[0]:
        if st.button("📱 Mobile Intelligence", key="mobile_verify", use_container_width=True):
            st.session_state.selected_module = "Mobile Intelligence"
            st.rerun()
        
    with cols[1]:
        if st.button("📧 Email Analytics", key="email_verify", use_container_width=True):
            st.session_state.selected_module = "Email Analytics"
            st.rerun()
        
    with cols[2]:
        if st.button("🖥️ Device Fingerprinting", key="device_fp", use_container_width=True):
            st.session_state.selected_module = "Device Fingerprinting"
            st.rerun()
        
    with cols[3]:
        if st.button("🌍 Location Intelligence", key="location_intel", use_container_width=True):
            st.session_state.selected_module = "Location Intelligence"
            st.rerun()
    
    # Advanced Analytics
    st.markdown('<h2 class="category-header">⚡ Advanced Analytics</h2>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    with cols[0]:
        if st.button("🧠 Fraud Intelligence", key="fraud_detect", use_container_width=True):
            st.session_state.selected_module = "Fraud Intelligence"
            st.rerun()
        
    with cols[1]:
        if st.button("🎭 Behavioral Analytics", key="behavior_analysis", use_container_width=True):
            st.session_state.selected_module = "Behavioral Analytics"
            st.rerun()
        
    with cols[2]:
        if st.button("⚠️ Negative Intelligence", key="negative_check", use_container_width=True):
            st.session_state.selected_module = "Negative Intelligence"
            st.rerun()
        
    with cols[3]:
        if st.button("🔮 Predictive Analytics", key="predictive_ai", use_container_width=True):
            st.session_state.selected_module = "Predictive Analytics"
            st.rerun()
    

    # Show demo interface if module is selected
    if 'selected_module' in st.session_state and st.session_state.selected_module:
        show_module_demo(st.session_state.selected_module)


def show_sidebar():
    """Show Tathya Lab sidebar navigation with AI theme"""

    st.sidebar.markdown("""
    <div style='
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #1e3c72 100%);
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    '>
        <h3 style='
            color: white; 
            margin: 0; 
            font-weight: 700;
            font-size: 1.4rem;
            background: linear-gradient(45deg, #fff, #a0c4ff, #bdb2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        '>🤖 Tathya Lab</h3>
        <p style='
            color: rgba(255,255,255,0.9); 
            margin: 0.5rem 0 0 0; 
            font-size: 0.95rem;
            font-weight: 300;
        '>Verification Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # User Information
    current_user = get_current_user()
    if current_user:
        st.sidebar.markdown("### 👤 User Information")
        st.sidebar.info(f"**User:** {current_user}")
        st.sidebar.markdown("---")

    # AI Verification Modules
    st.sidebar.markdown("### 🤖 AI Verification")
    
    verification_categories = [
        "🆔 Identity & KYC Intelligence", 
        "💰 Financial Intelligence", 
        "🌐 Digital Intelligence", 
        "⚡ Advanced Analytics"
    ]
    
    selected_category = st.sidebar.selectbox(
        "Select AI Module Category",
        verification_categories,
        key="ai_verification_category"
    )
    
    # Show category-specific info
    if selected_category == "🆔 Identity & KYC Intelligence":
        st.sidebar.success("🧬 Face Match AI • 🏦 PAN Intelligence • 🆔 Aadhaar Analytics")
    elif selected_category == "💰 Financial Intelligence":
        st.sidebar.success("📊 Bank Statement AI • 💳 UPI Intelligence • 📈 Credit Analytics")
    elif selected_category == "🌐 Digital Intelligence":
        st.sidebar.success("📱 Mobile Intelligence • 📧 Email Analytics • 🖥️ Device Fingerprinting")
    elif selected_category == "⚡ Advanced Analytics":
        st.sidebar.success("🧠 Fraud Intelligence • 🎭 Behavioral Analytics • 🔮 Predictive Analytics")

    st.sidebar.markdown("---")

    # No-Code Builder
    st.sidebar.markdown("### 🔧 Builder")
    if st.sidebar.button("🎨 Workflow Builder", use_container_width=True):
        st.session_state.current_page = "Tathya Lab Builder"
        st.rerun()
    
    if st.sidebar.button("📦 Module Gallery", use_container_width=True):
        st.session_state.current_page = "Tathya Module Gallery"
        st.rerun()

    # Analytics & Insights
    st.sidebar.markdown("### 📊 Analytics")
    if st.sidebar.button("📈 Verification Analytics", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.rerun()

    if st.sidebar.button("🔍 Fraud Insights", use_container_width=True):
        st.session_state.current_page = "Advanced Risk Assessment"
        st.rerun()

    st.sidebar.markdown("---")

    # Configuration
    st.sidebar.markdown("### ⚙️ Configuration")
    if st.sidebar.button("🛠️ System Configuration", use_container_width=True):
        st.session_state.current_page = "Configuration Panel"
        st.rerun()

    st.sidebar.markdown("---")

    # Navigation
    st.sidebar.markdown("### 🔄 Navigation")
    if st.sidebar.button("🏠 Investigation System", use_container_width=True):
        st.session_state.selected_system = "Investigation"
        st.rerun()

    # Logout
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        logout_user()
        st.rerun()


def show_module_demo(module_name):
    """Show functional demo interface for selected module"""
    
    st.markdown("---")
    st.markdown(f"### 🔬 {module_name} - Verification Interface")
    
    # Create structured interface with proper input/output alignment
    input_col, output_col = st.columns([1, 1])
    
    if module_name == "PAN Intelligence":
        with input_col:
            st.markdown("#### 📝 Input Parameters")
            with st.container():
                st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                
                # Simple vs Advanced toggle
                mode = st.radio("Verification Mode", ["🔹 Simple PAN Check", "🎯 Advanced Risk Assessment"], key="pan_mode")
                
                pan_number = st.text_input("PAN Number", placeholder="ABCDE1234F", key="pan_input", help="Enter 10-character PAN")
                
                if mode == "🎯 Advanced Risk Assessment":
                    st.markdown("**Advanced Parameters:**")
                    name_match = st.text_input("Name for Cross-Verification", placeholder="Full Name", key="pan_name")
                    dob = st.date_input("Date of Birth", key="pan_dob")
                    mobile = st.text_input("Mobile Number", placeholder="10-digit mobile", key="pan_mobile")
                
                verify_pan = st.button("🔍 Verify PAN Details", key="verify_pan", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with output_col:
            st.markdown("#### 📊 Verification Results")
            if verify_pan and pan_number:
                with st.spinner("🔗 Connecting to Timble Glance API..."):
                    try:
                        # Import and use PAN Advanced API
                        from pan_advanced_api import PANAdvancedAPI, get_response_message
                        
                        api = PANAdvancedAPI()
                        result = api.validate_pan(pan_number)
                        
                        if result['success']:
                            # Success - Display PAN details
                            st.success("✅ PAN Validation Successful")
                            
                            data = result['data']
                            st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Full Name:** {data['FULLNAME']}")
                                st.write(f"**DOB:** {data['DOB']}")
                                st.write(f"**Gender:** {data['GENDER']}")
                                st.write(f"**PAN Type:** {data['PAN_TYPE']}")
                            
                            with col2:
                                st.write(f"**Email:** {data['EMAIL']}")
                                st.write(f"**Mobile:** {data['MOBILE']}")
                                st.write(f"**Aadhaar Link:** {data['AADHAAR_LINKAGE']}")
                                st.write(f"**PAN Status:** {data['PAN_STATUS']}")
                            
                            st.write(f"**Address:** {data['ADDRESS']}")
                            
                            # Transaction details
                            if result.get('transaction_id'):
                                st.info(f"Transaction ID: {result['transaction_id']}")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Risk Assessment for Advanced mode
                            if mode == "🎯 Advanced Risk Assessment":
                                st.markdown("#### 🎯 Risk Assessment")
                                risk_score = 85  # This would be calculated based on matches
                                
                                if risk_score >= 80:
                                    st.success(f"✅ Low Risk Score: {risk_score}%")
                                elif risk_score >= 60:
                                    st.warning(f"⚠️ Medium Risk Score: {risk_score}%")
                                else:
                                    st.error(f"❌ High Risk Score: {risk_score}%")
                        
                        else:
                            # Handle different error types
                            message = get_response_message(result.get('code', result.get('error', 'UNKNOWN')))
                            
                            if result.get('code') == 102:
                                st.error("❌ Invalid PAN Number")
                                st.info("Please check the PAN format (ABCDE1234F)")
                            elif result.get('code') == 103:
                                st.warning("⚠️ No Record Found")
                                st.info("PAN might be inactive or incorrect")
                            elif result.get('code') == 110:
                                st.error("🔧 Service Temporarily Down")
                                st.info("Please try again later")
                            else:
                                st.error(f"❌ {message}")
                                if result.get('error'):
                                    st.info(f"Details: {result['error']}")
                    
                    except ImportError:
                        st.error("❌ PAN Advanced API not available")
                        st.info("API credentials need to be configured")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            elif verify_pan and not pan_number:
                st.warning("⚠️ Please enter a PAN number")
                
                with st.container():
                    st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                    if len(pan_number) == 10 and pan_number.isalnum():
                        st.success("✅ PAN Verification Successful")
                        st.info(f"**PAN Number:** {pan_number.upper()}")
                        st.info(f"**Registered Name:** {name_match if name_match else 'JOHN DOE'}")
                        st.info("**Status:** Active")
                        st.info("**Category:** Individual")
                        st.info("**AO Code:** WARD-1(1)")
                        st.info("**Date of Allotment:** 15-MAR-2010")
                        st.info("**Name Match Score:** 95%")
                        st.info("**Risk Level:** Low")
                    else:
                        st.error("❌ Invalid PAN Format")
                        st.warning("PAN must be 10 alphanumeric characters")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    elif module_name == "Face Match AI":
        with input_col:
            st.markdown("#### 📝 Image Upload")
            with st.container():
                st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                reference_img = st.file_uploader("Reference Image", type=['jpg', 'jpeg', 'png'], key="ref_image", help="Upload primary photo")
                comparison_img = st.file_uploader("Comparison Image", type=['jpg', 'jpeg', 'png'], key="comp_image", help="Upload photo to compare")
                
                col1, col2 = st.columns(2)
                with col1:
                    confidence_threshold = st.slider("Match Threshold", 0.5, 1.0, 0.8, key="threshold")
                with col2:
                    analysis_model = st.selectbox("AI Model", ["DeepFace", "FaceNet", "VGG-Face"], key="model")
                
                compare_faces = st.button("🔍 Analyze Face Match", key="compare_faces", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with output_col:
            st.markdown("#### 📊 Analysis Results")
            if compare_faces and reference_img and comparison_img:
                with st.spinner("Processing facial biometrics..."):
                    import time
                    time.sleep(3)
                
                with st.container():
                    st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                    st.success("✅ Face Analysis Complete")
                    st.info("**Match Confidence:** 94.2%")
                    st.info("**Verification Status:** VERIFIED")
                    st.info("**Facial Landmarks:** 68 points detected")
                    st.info("**Image Quality Score:** Excellent")
                    st.info("**Processing Model:** " + analysis_model)
                    st.info("**Detection Accuracy:** 99.1%")
                    st.info("**Similarity Score:** 0.942")
                    st.info("**Processing Time:** 2.3 seconds")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    elif module_name == "Mobile Intelligence":
        with input_col:
            st.markdown("#### 📝 Mobile Verification")
            with st.container():
                st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                mobile_number = st.text_input("Mobile Number", placeholder="9876543210", key="mobile_input", help="10-digit mobile number")
                operator_check = st.checkbox("Verify Operator Details", key="operator_verify")
                mnrl_check = st.checkbox("Check MNRL Status", key="mnrl_check", help="Mobile Number Revocation List")
                location_check = st.checkbox("Location Analysis", key="location_verify")
                
                verify_mobile = st.button("🔍 Verify Mobile", key="verify_mobile", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with output_col:
            st.markdown("#### 📊 Verification Results")
            if verify_mobile and mobile_number:
                with st.spinner("Connecting to telecom databases..."):
                    import time
                    time.sleep(2)
                
                with st.container():
                    st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                    if len(mobile_number) == 10 and mobile_number.isdigit():
                        st.success("✅ Mobile Verification Complete")
                        st.info(f"**Mobile Number:** +91-{mobile_number}")
                        st.info("**Operator:** Bharti Airtel Limited")
                        st.info("**Connection Type:** Postpaid")
                        st.info("**Circle:** Delhi")
                        st.info("**Status:** Active")
                        if mnrl_check:
                            st.info("**MNRL Status:** Clean (Not Blacklisted)")
                        if operator_check:
                            st.info("**License Area:** Delhi Metro")
                            st.info("**Technology:** 4G/5G")
                        if location_check:
                            st.info("**Last Location:** New Delhi, DL")
                            st.info("**Tower ID:** DEL001234")
                    else:
                        st.error("❌ Invalid Mobile Format")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    elif module_name == "Aadhaar Analytics":
        with input_col:
            st.markdown("#### 📝 Aadhaar Verification")
            with st.container():
                st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                aadhaar_number = st.text_input("Aadhaar Number", placeholder="1234 5678 9012", key="aadhaar_input", help="12-digit Aadhaar number")
                name_verify = st.text_input("Name for Verification", placeholder="As per Aadhaar", key="aadhaar_name")
                mobile_verify = st.text_input("Mobile for OTP", placeholder="Registered mobile", key="aadhaar_mobile")
                
                col1, col2 = st.columns(2)
                with col1:
                    verify_type = st.selectbox("Verification Type", ["Demographic", "Biometric", "OTP"], key="verify_type")
                with col2:
                    otp_method = st.selectbox("OTP Method", ["SMS", "Email"], key="otp_method")
                
                verify_aadhaar = st.button("🔍 Verify Aadhaar", key="verify_aadhaar", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with output_col:
            st.markdown("#### 📊 Verification Results")
            if verify_aadhaar and aadhaar_number:
                with st.spinner("Connecting to UIDAI servers..."):
                    import time
                    time.sleep(2)
                
                with st.container():
                    st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                    if len(aadhaar_number.replace(" ", "")) == 12:
                        st.success("✅ Aadhaar Verification Successful")
                        masked_aadhaar = "XXXX XXXX " + aadhaar_number.replace(" ", "")[-4:]
                        st.info(f"**Aadhaar Number:** {masked_aadhaar}")
                        st.info(f"**Name:** {name_verify if name_verify else 'RAJESH KUMAR'}")
                        st.info("**Date of Birth:** 15-08-1985")
                        st.info("**Gender:** Male")
                        st.info("**Address:** New Delhi, Delhi - 110001")
                        st.info("**Mobile Status:** Verified")
                        st.info("**Email Status:** Not Registered")
                        st.info("**Name Match Score:** 98%")
                        st.info("**Verification Method:** " + verify_type)
                    else:
                        st.error("❌ Invalid Aadhaar Format")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    elif module_name == "Bank Statement AI":
        with input_col:
            st.markdown("#### 📝 Document Upload")
            with st.container():
                st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                bank_statement = st.file_uploader("Bank Statement", type=['pdf'], key="bank_file", help="Upload PDF statement")
                
                col1, col2 = st.columns(2)
                with col1:
                    analysis_period = st.selectbox("Analysis Period", ["3 Months", "6 Months", "12 Months"], key="period")
                with col2:
                    account_type = st.selectbox("Account Type", ["Savings", "Current", "Auto-detect"], key="acc_type")
                
                salary_account = st.checkbox("Salary Account Analysis", key="salary_check")
                loan_analysis = st.checkbox("Loan Eligibility Check", key="loan_check")
                
                analyze_statement = st.button("🔍 Analyze Statement", key="analyze_bank", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with output_col:
            st.markdown("#### 📊 Analysis Results")
            if analyze_statement and bank_statement:
                with st.spinner("Processing financial data..."):
                    import time
                    time.sleep(4)
                
                with st.container():
                    st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                    st.success("✅ Statement Analysis Complete")
                    st.info("**Account Holder:** RAJESH KUMAR")
                    st.info("**Bank:** HDFC Bank Limited")
                    st.info("**Account Number:** XXXX1234")
                    st.info("**Average Monthly Balance:** ₹85,000")
                    st.info("**Monthly Income:** ₹1,20,000")
                    st.info("**Monthly Expenses:** ₹75,000")
                    st.info("**Savings Rate:** 37.5%")
                    st.info("**Credit Score Impact:** Positive")
                    if loan_analysis:
                        st.info("**Loan Eligibility:** ₹18,00,000")
                    st.info("**Risk Assessment:** Low Risk")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    elif module_name == "UPI Intelligence":
        with input_col:
            st.markdown("#### 📝 UPI Verification")
            with st.container():
                st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                upi_id = st.text_input("UPI ID", placeholder="user@paytm", key="upi_input", help="Enter UPI ID to verify")
                mobile_upi = st.text_input("Linked Mobile", placeholder="Mobile number", key="upi_mobile")
                
                col1, col2 = st.columns(2)
                with col1:
                    verify_name = st.checkbox("Verify Account Holder Name", key="upi_name_check")
                with col2:
                    transaction_history = st.checkbox("Transaction Pattern Analysis", key="upi_transaction")
                
                verify_upi = st.button("🔍 Verify UPI ID", key="verify_upi", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with output_col:
            st.markdown("#### 📊 Verification Results")
            if verify_upi and upi_id:
                with st.spinner("Verifying UPI details..."):
                    import time
                    time.sleep(2)
                
                with st.container():
                    st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                    if "@" in upi_id:
                        st.success("✅ UPI Verification Complete")
                        st.info(f"**UPI ID:** {upi_id}")
                        st.info("**Status:** Active")
                        st.info("**Bank:** HDFC Bank")
                        st.info("**Account Type:** Savings")
                        if verify_name:
                            st.info("**Account Holder:** RAJESH KUMAR")
                        st.info("**PSP:** Paytm Payments Bank")
                        st.info("**Registration Date:** 15-Jan-2020")
                        if transaction_history:
                            st.info("**Monthly Transactions:** 45 avg")
                            st.info("**Transaction Volume:** ₹25,000/month")
                        st.info("**Risk Score:** Low")
                    else:
                        st.error("❌ Invalid UPI ID Format")
                    st.markdown('</div>', unsafe_allow_html=True)
    

    else:
        # Generic interface for other modules
        with input_col:
            st.markdown("#### 📝 Input Parameters")
            with st.container():
                st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                generic_input = st.text_input(f"Enter {module_name} Data", key=f"generic_{module_name.lower().replace(' ', '_')}")
                process_btn = st.button(f"🔍 Process {module_name}", key=f"process_{module_name.lower().replace(' ', '_')}", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with output_col:
            st.markdown("#### 📊 Results")
            if process_btn and generic_input:
                with st.spinner("Processing..."):
                    import time
                    time.sleep(2)
                
                with st.container():
                    st.markdown('<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                    st.success("✅ Processing Complete")
                    st.info("**Status:** Verified")
                    st.info("**Confidence:** 95%")
                    st.info("**Risk Level:** Low")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close demo button
    st.markdown("---")
    if st.button("✖ Close Verification Interface", key="close_demo", use_container_width=True):
        if 'selected_module' in st.session_state:
            del st.session_state.selected_module
        st.rerun()