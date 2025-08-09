"""
Regulatory Governance Suite - Standalone Regulatory Management System
"""

import streamlit as st
import os
from datetime import datetime
import pandas as pd
import json
import base64
import io

# Import PDF processing library
try:
    import PyPDF2
except ImportError:
    st.error("PyPDF2 library not found. Please install PyPDF2.")

# Import Gemini AI services
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Google Gemini AI libraries not found. Please install google-genai.")

def initialize_gemini_client():
    """Initialize Gemini AI client"""
    try:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            st.error("🔑 Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
            return None
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Failed to initialize Gemini client: {str(e)}")
        return None

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file based on file type"""
    try:
        if uploaded_file.type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            # For text and Word files, try to read as text
            content = uploaded_file.read()
            try:
                return content.decode('utf-8')
            except:
                return content.decode('latin-1')
        else:
            st.warning(f"⚠️ File type {uploaded_file.type} not fully supported for text extraction")
            return ""
    except Exception as e:
        st.error(f"❌ Error extracting text: {str(e)}")
        return ""

def analyze_document_with_gemini(text_content, client):
    """Analyze document text using Gemini AI to extract regulatory information"""
    if not client or not text_content:
        return None
    
    try:
        prompt = f"""
        Analyze the following regulatory document and extract key information for the Regulatory Advisory Analyzer. 
        Please identify and extract the following fields where available:

        1. Advisory Title
        2. Reference Number/Issuing Body
        3. Date Issued
        4. Effective Date/Deadline
        5. Objective/Purpose
        6. Key Issues Addressed
        7. Required Actions
        8. Stakeholders Involved
        9. Impact Areas
        10. Documentation Required
        11. Timeline and Milestones

        Document text:
        {text_content[:4000]}  # Limit to avoid token limits

        Please respond in JSON format with these exact keys: advisory_title, reference_number, issuing_authority, category, objective, key_issues, key_requirements. If a field is not found, use "Not detected" as the value.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        if response.text:
            return json.loads(response.text)
        return None

    except Exception as e:
        st.error(f"❌ Error analyzing document with Gemini: {str(e)}")
        return None

def generate_qa_analysis(text_content, question, client):
    """Generate Q&A analysis based on document content with structured sections"""
    if not client or not text_content or not question:
        return None
    
    try:
        prompt = f"""
        As a regulatory compliance expert, analyze the following regulatory document and answer this question: {question}

        Document content:
        {text_content[:5000]}

        Please provide a comprehensive structured analysis in JSON format with these sections:

        1. "direct_answer": Direct response to the question (2-3 sentences)
        2. "key_findings": Main findings from the document relevant to the question
        3. "compliance_requirements": Specific compliance obligations identified
        4. "deadlines_timelines": Important dates and deadlines mentioned
        5. "action_items": Specific actions organizations should take
        6. "risks_consequences": Potential risks and consequences of non-compliance
        7. "implementation_guidance": Practical steps for implementation
        8. "relevant_citations": Specific sections or quotes from the document

        Format as JSON with these exact keys. If a section is not applicable, use an empty string.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        if response.text:
            return json.loads(response.text)
        return None

    except Exception as e:
        st.error(f"Error generating Q&A analysis: {str(e)}")
        return None

def generate_comprehensive_analysis(text_content, client):
    """Generate comprehensive regulatory document analysis"""
    if not client or not text_content:
        return None
    
    try:
        prompt = f"""
        As a senior regulatory compliance analyst, perform a comprehensive analysis of this regulatory document:

        Document content:
        {text_content[:6000]}

        Please provide a detailed analysis covering:

        1. SUMMARY: Executive summary of the regulation (2-3 sentences)
        
        2. COMPLIANCE_REQUIREMENTS: List all specific compliance requirements and obligations
        
        3. DEADLINES: Identify all important dates, deadlines, and timelines mentioned
        
        4. RISKS: Assess compliance risks, penalties, and consequences of non-compliance
        
        5. ACTIONS: Recommend specific action items organizations should take
        
        6. BUSINESS_IMPACT: Analyze potential impact on business operations, processes, and costs

        Format your response as JSON with these exact keys: summary, compliance_requirements, deadlines, risks, actions, business_impact
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        if response.text:
            return json.loads(response.text)
        return None

    except Exception as e:
        st.error(f"Error generating comprehensive analysis: {str(e)}")
        return None

def show_user_dashboard_sidebar():
    """Display comprehensive user dashboard sidebar for Regulatory Governance Suite"""
    
    # Custom CSS for sidebar styling
    st.markdown("""
    <style>
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .user-info-section {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        width: 100%;
        box-sizing: border-box;
        overflow: hidden;
        word-wrap: break-word;
    }
    
    .nav-item {
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        background: white;
        border: 1px solid #e9ecef;
    }
    
    .nav-item:hover {
        background: #e3f2fd;
        border-color: #2196f3;
        transform: translateX(5px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # System Switch Options (placed above User Information)
    st.markdown("#### 🔄 Switch System")
    
    # Switch buttons in sidebar
    col_switch1, col_switch2 = st.columns(2)
    
    with col_switch1:
        if st.button("🕵️ Investigation", key="reg_switch_to_inv", help="Switch to Investigation System", use_container_width=True):
            st.session_state.selected_system = "Investigation"
            st.rerun()
    
    with col_switch2:
        if st.button("🔬 Verification", key="reg_switch_to_lab", help="Switch to Verification Lab", use_container_width=True):  
            st.session_state.selected_system = "Configuration Panel"
            st.rerun()
    
    st.markdown("---")
    
    # User Information Section - contained in sidebar
    current_user = st.session_state.get('authenticated_user', 'Unknown')
    current_role = st.session_state.get('user_role', 'Unknown')  
    user_name = st.session_state.get('user_name', 'Unknown User')
    
    # User Information Section - fully contained
    st.markdown("#### 👤 User Information")
    st.markdown(f"""
    <div class="user-info-section">
        <strong>User ID:</strong> {current_user}<br>
        <strong>Role:</strong> {current_role}<br>
        <strong>Name:</strong> {user_name}
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Navigation Section - fully contained
    st.markdown("#### 🧭 Quick Navigation")

    # Navigation buttons for Regulatory Governance Suite - fully contained
    nav_options = [
        ("📘", "Regulatory Analyzer", "regulatory_analyzer"),
        ("📄", "Policy Library", "policy_library"),
        ("⚙️", "Compliance Tasks", "compliance_tasks"),
        ("📝", "SOP Templates", "sop_templates"),
        ("📅", "Milestones", "milestones"),
        ("📎", "Docs & Audit Trail", "docs_audit_trail")
    ]
    
    for icon, title, key in nav_options:
        if st.button(f"{icon} {title}", key=f"nav_{key}", 
                    help=f"Navigate to {title}", use_container_width=True):
            st.session_state.regulatory_active_section = key
            st.rerun()

def show():
    """Main function to display Regulatory Governance Suite"""
    
    # Load custom CSS
    st.markdown("""
    <style>
    /* Professional layout styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        text-align: center;
        font-weight: 600;
    }
    
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    
    .analysis-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stakeholder-tag {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .milestone-row {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Common header with branding and logos
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])

    with header_col1:
        try:
            st.image("static/images/tathya.png", width=250)
        except:
            st.markdown("# 📘 Tathya")
            st.markdown("### Regulatory Excellence")

    with header_col2:
        st.markdown("")
    
    with header_col3:
        try:
            st.image("static/images/abcl_logo.jpg", width=250)
        except:
            st.markdown("### 🏢 ABCL")


    

    
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
        '>Regulatory Governance Suite</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Comprehensive Regulatory Management & Compliance Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize active section
    if 'regulatory_active_section' not in st.session_state:
        st.session_state.regulatory_active_section = "regulatory_analyzer"
    
    # Create two-column layout
    col_sidebar, col_main = st.columns([1, 3])
    
    with col_sidebar:
        # Create a bordered container to visually contain sidebar content
        st.markdown("""
        <div style='
            border: 1px solid #e0e0e0; 
            border-radius: 10px; 
            padding: 1rem; 
            background: #fafafa;
            height: fit-content;
            width: 100%;
            box-sizing: border-box;
        '>
        """, unsafe_allow_html=True)
        
        show_user_dashboard_sidebar()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_main:
        # Display content based on active section
        active_section = st.session_state.get('regulatory_active_section', 'regulatory_analyzer')
        
        if active_section == "regulatory_analyzer":
            show_regulatory_analyzer()
        elif active_section == "policy_library":
            show_policy_library()
        elif active_section == "compliance_tasks":
            show_compliance_tasks()
        elif active_section == "sop_templates":
            show_sop_templates()
        elif active_section == "milestones":
            show_milestones()
        elif active_section == "docs_audit_trail":
            show_docs_audit_trail()

def show_regulatory_analyzer():
    """Display the main Regulatory Analyzer section"""
    
    st.markdown("""
    <div class="section-header">
        <h2>📘 Regulatory Advisory Analyzer</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Document Repository Functionality
    st.markdown("### ✅ Document Repository")
    
    # File upload area
    st.markdown("""
    <div class="upload-area">
        <h4>📁 Upload Regulatory Documents</h4>
        <p>Supported formats: PDF, Word, Excel</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls'],
        help="Upload regulatory documents for analysis"
    )
    
    if uploaded_files:
        st.success(f"📄 {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Initialize Gemini client
        gemini_client = initialize_gemini_client()
        
        for idx, file in enumerate(uploaded_files):
            with st.expander(f"📋 Analyze: {file.name}", expanded=(idx == 0)):
                # Extract text from uploaded file
                extracted_text = extract_text_from_file(file)
                
                if extracted_text:
                    st.success(f"✅ Text extracted from {file.name}")
                    
                    # Auto-analyze with Gemini AI
                    if gemini_client and st.button(f"🤖 Auto-Fill Fields with Gemini AI", key=f"auto_fill_{idx}"):
                        with st.spinner("🔄 Analyzing document with Gemini AI..."):
                            analysis_result = analyze_document_with_gemini(extracted_text, gemini_client)
                            if analysis_result:
                                st.session_state[f"gemini_analysis_{file.name}"] = analysis_result
                                st.success("✅ Fields auto-filled with AI analysis!")
                                st.rerun()
                
                show_regulatory_analysis_template(file.name, extracted_text, gemini_client)

def show_regulatory_analysis_template(filename, extracted_text="", gemini_client=None):
    """Display the comprehensive regulatory analysis template with AI auto-fill capabilities"""
    
    st.markdown(f"### 📘 Regulatory Advisory Analyzer - {filename}")
    
    # Get AI analysis if available
    analysis_key = f"gemini_analysis_{filename}"
    ai_analysis = st.session_state.get(analysis_key, {})
    
    # Create tabs for Auto-filled and Manual sections
    tab1, tab2, tab3 = st.tabs(["🤖 Auto-Filled Fields", "✍️ Manual Input Fields", "🔍 AI Document Analysis"])
    
    with tab1:
        st.markdown("#### 🤖 Auto-Filled from Document Analysis")
        st.info("These fields are automatically filled using Google Gemini AI analysis of your uploaded document.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "Advisory Title", 
                value=ai_analysis.get("advisory_title", "Not detected"),
                disabled=True,
                key=f"auto_title_{filename}"
            )
            st.text_input(
                "Reference No. / Issuing Body", 
                value=ai_analysis.get("reference_number", "Not detected"),
                disabled=True,
                key=f"auto_ref_{filename}"
            )
            st.text_area(
                "Objective/Purpose", 
                value=ai_analysis.get("objective", "Not detected"),
                disabled=True,
                key=f"auto_objective_{filename}",
                height=100
            )
        
        with col2:
            st.text_input(
                "Issuing Authority", 
                value=ai_analysis.get("issuing_authority", "Not detected"),
                disabled=True,
                key=f"auto_authority_{filename}"
            )
            st.text_input(
                "Regulatory Category", 
                value=ai_analysis.get("category", "Not detected"),
                disabled=True,
                key=f"auto_category_{filename}"
            )
            st.text_area(
                "Key Requirements", 
                value=ai_analysis.get("key_requirements", "Not detected"),
                disabled=True,
                key=f"auto_requirements_{filename}",
                height=100
            )
        
        st.text_area(
            "Key Issues Addressed", 
            value=ai_analysis.get("key_issues", "Not detected"),
            disabled=True,
            key=f"auto_issues_{filename}",
            height=80
        )
    
    with tab2:
        st.markdown("#### ✍️ Manual Input Required")
        st.info("Please fill these fields based on your organization's specific requirements and analysis.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date_issued = st.date_input("Date Issued", key=f"date_issued_{filename}")
            effective_date = st.date_input("Effective Date / Deadline", key=f"effective_{filename}")
            priority_level = st.selectbox(
                "Priority Level", 
                ["High", "Medium", "Low"], 
                key=f"priority_{filename}"
            )
        
        with col2:
            compliance_deadline = st.date_input("Compliance Deadline", key=f"compliance_deadline_{filename}")
            responsible_dept = st.text_input("Responsible Department", key=f"dept_{filename}")
            estimated_effort = st.selectbox(
                "Estimated Effort", 
                ["Low (1-2 weeks)", "Medium (1-2 months)", "High (3+ months)"], 
                key=f"effort_{filename}"
            )
    
    st.markdown("---")
    
    # 3. Action Required / Process to Follow
    st.markdown("#### ⚙️ 3. Action Required / Process to Follow")
    
    # Initialize action items in session state
    action_key = f"action_items_{filename}"
    if action_key not in st.session_state:
        st.session_state[action_key] = [
            {"step": 1, "action": "", "owner": "", "support": "", "timeline": "", "status": "Pending"}
        ]
    
    # Add new action item button
    if st.button("➕ Add Action Item", key=f"add_action_{filename}"):
        new_step = len(st.session_state[action_key]) + 1
        st.session_state[action_key].append({
            "step": new_step, "action": "", "owner": "", "support": "", "timeline": "", "status": "Pending"
        })
        st.rerun()
    
    # Display action items table
    for i, item in enumerate(st.session_state[action_key]):
        st.markdown(f"**Step {item['step']}**")
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            item['action'] = st.text_input(f"Action Item", value=item['action'], key=f"action_{filename}_{i}")
        with col2:
            item['owner'] = st.text_input(f"Owner Dept", value=item['owner'], key=f"owner_{filename}_{i}")
        with col3:
            item['support'] = st.text_input(f"Support Teams", value=item['support'], key=f"support_{filename}_{i}")
        with col4:
            item['timeline'] = st.text_input(f"Timeline", value=item['timeline'], key=f"timeline_{filename}_{i}")
        with col5:
            item['status'] = st.selectbox(f"Status", ["Pending", "In Progress", "Completed"], 
                                        index=["Pending", "In Progress", "Completed"].index(item['status']),
                                        key=f"status_{filename}_{i}")
    
    st.markdown("---")
    
    # 4. Stakeholders Involved
    st.markdown("#### 🧑‍🤝‍🧑 4. Stakeholders Involved")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        primary_owners = st.text_area("Primary Owners", key=f"primary_{filename}")
    with col2:
        secondary_contributors = st.text_area("Secondary Contributors", key=f"secondary_{filename}")
    with col3:
        external_liaisons = st.text_area("External Liaisons", key=f"external_{filename}")
    
    st.markdown("---")
    
    # 5. Impact Areas
    st.markdown("#### 🧾 5. Impact Areas")
    impact_areas = [
        "Policy Changes", "SOP / Process Realignment", "Customer Communication",
        "Product Changes", "Tech Platform Changes", "MIS / Reporting Adjustments"
    ]
    
    selected_impacts = []
    cols = st.columns(3)
    for i, area in enumerate(impact_areas):
        with cols[i % 3]:
            if st.checkbox(area, key=f"impact_{area}_{filename}"):
                selected_impacts.append(area)
    
    st.markdown("---")
    
    # 6. Documentation Required
    st.markdown("#### 📝 6. Documentation Required")
    doc_checklist = [
        "Updated Policy", "Revised SOP", "Audit Trails", 
        "Evidence of Implementation", "Customer Communication"
    ]
    
    completed_docs = []
    cols = st.columns(3)
    for i, doc in enumerate(doc_checklist):
        with cols[i % 3]:
            if st.checkbox(doc, key=f"doc_{doc}_{filename}"):
                completed_docs.append(doc)
    
    st.markdown("---")
    
    # 7. Timelines & Milestones
    st.markdown("#### 📅 7. Timelines & Milestones")
    
    milestone_key = f"milestones_{filename}"
    if milestone_key not in st.session_state:
        st.session_state[milestone_key] = [
            {"milestone": "", "owner": "", "deadline": "", "status": "Pending"}
        ]
    
    if st.button("➕ Add Milestone", key=f"add_milestone_{filename}"):
        st.session_state[milestone_key].append({"milestone": "", "owner": "", "deadline": "", "status": "Pending"})
        st.rerun()
    
    for i, milestone in enumerate(st.session_state[milestone_key]):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            milestone['milestone'] = st.text_input("Milestone", value=milestone['milestone'], key=f"mile_{filename}_{i}")
        with col2:
            milestone['owner'] = st.text_input("Owner", value=milestone['owner'], key=f"mile_owner_{filename}_{i}")
        with col3:
            milestone['deadline'] = st.text_input("Deadline", value=milestone['deadline'], key=f"mile_deadline_{filename}_{i}")
        with col4:
            milestone['status'] = st.selectbox("Status", ["Pending", "In Progress", "Completed"], 
                                             index=["Pending", "In Progress", "Completed"].index(milestone['status']),
                                             key=f"mile_status_{filename}_{i}")
    
    st.markdown("---")
    
    # 8. Key Takeaways
    st.markdown("#### ✅ 8. Key Takeaways")
    col1, col2 = st.columns(2)
    
    with col1:
        regulatory_summary = st.text_area("Summary of regulatory change", key=f"summary_{filename}")
        implementation_challenges = st.text_area("Implementation challenges", key=f"challenges_{filename}")
    
    with col2:
        audit_risks = st.text_area("Audit risks", key=f"risks_{filename}")
        tracking_link = st.text_input("Internal tracking link", key=f"tracking_{filename}")
    
    st.markdown("---")
    
    # 9. Reference Documents
    st.markdown("#### 🌐 9. Reference Documents")
    col1, col2 = st.columns(2)
    
    with col1:
        regulatory_circulars = st.text_area("Regulatory circulars (URLs)", key=f"circulars_{filename}")
        public_notices = st.text_area("Public notices (URLs)", key=f"notices_{filename}")
    
    with col2:
        internal_docs = st.text_area("Internal documentation (URLs)", key=f"internal_{filename}")
        live_dashboards = st.text_area("Live dashboards (URLs)", key=f"dashboards_{filename}")
    
    with tab3:
        st.markdown("#### 🔍 AI Document Analysis")
        
        if extracted_text and gemini_client:
            # Simple Q&A Analysis Section
            st.markdown("Ask any question about your regulatory document:")
            
            user_question = st.text_area(
                "Your Question:",
                placeholder="Ask anything about this document - compliance requirements, deadlines, actions needed, risks, business impact, etc.",
                height=120,
                key=f"qa_question_{filename}"
            )
            
            if st.button("🔍 Get AI Answer", key=f"qa_analyze_{filename}", use_container_width=True):
                if user_question:
                    with st.spinner("Analyzing document and generating answer..."):
                        qa_result = generate_qa_analysis(extracted_text, user_question, gemini_client)
                        if qa_result:
                            st.session_state[f"qa_result_{filename}"] = qa_result
                            st.rerun()
            
            # Display Q&A result in expandable sections
            qa_result = st.session_state.get(f"qa_result_{filename}")
            if qa_result:
                st.markdown("**🎯 AI Analysis Results:**")
                
                if isinstance(qa_result, dict):
                    # Structured response with expandable sections
                    analysis_sections = [
                        ("💡 Direct Answer", qa_result.get("direct_answer", "")),
                        ("🔍 Key Findings", qa_result.get("key_findings", "")),
                        ("⚖️ Compliance Requirements", qa_result.get("compliance_requirements", "")),
                        ("📅 Deadlines & Timelines", qa_result.get("deadlines_timelines", "")),
                        ("✅ Action Items", qa_result.get("action_items", "")),
                        ("⚠️ Risks & Consequences", qa_result.get("risks_consequences", "")),
                        ("🛠️ Implementation Guidance", qa_result.get("implementation_guidance", "")),
                        ("📖 Relevant Citations", qa_result.get("relevant_citations", ""))
                    ]
                    
                    for section_title, content in analysis_sections:
                        if content and content.strip():
                            with st.expander(section_title, expanded=(section_title == "💡 Direct Answer")):
                                content_html = content.replace('\n', '<br>')
                                st.markdown(f"""
                                <div style='
                                    background: #ffffff; 
                                    padding: 1rem; 
                                    border-radius: 8px; 
                                    border-left: 4px solid #667eea;
                                    line-height: 1.6;
                                '>
                                    {content_html}
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    # Fallback for plain text response
                    st.text_area(
                        "Answer:",
                        value=str(qa_result),
                        height=300,
                        disabled=True,
                        key=f"qa_answer_display_{filename}"
                    )
        
        else:
            st.info("Upload a document to use AI Q&A analysis")
    
    # Save Analysis button
    if st.button("💾 Save Analysis", key=f"save_{filename}"):
        st.success("✅ Analysis saved successfully!")

def show_policy_library():
    """Display Policy Library section"""
    st.markdown("""
    <div class="section-header">
        <h2>📄 Policy Library</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📚 Policy Library management interface will be implemented here.")

def show_compliance_tasks():
    """Display Compliance Tasks section"""
    st.markdown("""
    <div class="section-header">
        <h2>⚙️ Compliance Tasks</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("✅ Compliance task management interface will be implemented here.")

def show_sop_templates():
    """Display SOP Templates section"""
    st.markdown("""
    <div class="section-header">
        <h2>📝 SOP Templates</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📋 SOP template management interface will be implemented here.")

def show_milestones():
    """Display Milestones section"""
    st.markdown("""
    <div class="section-header">
        <h2>📅 Milestones</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🎯 Milestone tracking interface will be implemented here.")

def show_docs_audit_trail():
    """Display Docs & Audit Trail section"""
    st.markdown("""
    <div class="section-header">
        <h2>📎 Docs & Audit Trail</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📋 Document audit trail interface will be implemented here.")