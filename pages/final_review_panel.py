import streamlit as st
import pandas as pd
from datetime import datetime
from auth import require_role, get_current_user
from models import get_cases_by_status, get_case_by_id, update_case_status, get_case_comments, add_case_comment
from database import log_audit, get_db_connection
from utils import format_datetime
from pages.workflow_progress import show_workflow_progress
from pdf_generator import show_pdf_download_button
from error_handler import handle_database_error, handle_validation_error, success_message, handle_api_error

@require_role(["Admin", "Reviewer"])
def show():
    """Final Adjudication Panel - Categorize cases with Fraud/Non-Fraud/Other Incident logic"""
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
        '>Final Adjudication</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Final categorization and adjudication of investigated cases</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Final categorization and adjudication of investigated cases**")
    
    current_user = get_current_user()
    
    # Get cases requiring final review or those sent to Legal/Actioner but not yet completed
    final_review_cases = get_cases_requiring_final_review()
    
    if final_review_cases:
        st.markdown(f"**{len(final_review_cases)} case(s) requiring final adjudication**")
        
        for case in final_review_cases:
            # Add status indicators for cases in Legal Review
            status_indicator = ""
            if case['status'] == 'Legal Review':
                legal_status = case.get('legal_status', 'Pending')
                actioner_status = case.get('actioner_status', 'Pending')
                status_indicator = f" | Legal: {legal_status} | Actioner: {actioner_status}"
            
            with st.expander(f"🎯 {case['case_id']} - {case['customer_name']} ({case['case_type']}){status_indicator}", expanded=False):
                show_enhanced_case_details(case, current_user)
    else:
        st.info("📭 No cases requiring final adjudication at this time")
        st.markdown("""
        **Cases will appear here when:**
        - Investigation has been completed
        - Primary review is finished
        - Cases are ready for final adjudication and categorization
        """)

def show_enhanced_case_details(case, current_user):
    """Display detailed case information with enhanced final adjudication actions"""
    case_id = case.get('case_id', 'unknown')
    
    # Display standardized case details
    from case_display_utils import show_standardized_case_details, show_standardized_customer_info, show_standardized_case_history, show_standardized_documents
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_standardized_case_details(case)
        show_standardized_customer_info(case)
    
    with col2:
        show_standardized_case_history(case_id)
        show_standardized_documents(case_id)
    
    # Final Adjudication Section with Categorization Logic
    st.markdown("### 🏛️ Final Adjudication & Categorization")
    
    # Categorization Selection
    st.markdown("#### Case Categorization")
    col_cat1, col_cat2, col_cat3 = st.columns(3)
    
    with col_cat1:
        case_category = st.selectbox(
            "Select Final Category *",
            ["Select Category", "Fraud", "Non-Fraud", "Other Incident"],
            key=f"case_category_{case_id}",
            help="This determines the next workflow step"
        )
    
    with col_cat2:
        if case_category == "Fraud":
            fraud_type = st.selectbox(
                "Fraud Type *",
                ["Select Type", "Financial Fraud", "Identity Fraud", "Document Fraud", "Cyber Fraud", "Other Fraud"],
                key=f"fraud_type_{case_id}"
            )
        else:
            fraud_type = None
    
    with col_cat3:
        severity_level = st.selectbox(
            "Severity Level *",
            ["Select Severity", "Low", "Medium", "High", "Critical"],
            key=f"severity_{case_id}"
        )
    
    # Adjudication Summary
    st.markdown("#### Adjudication Summary")
    col_summary1, col_summary2 = st.columns([3, 1])
    
    with col_summary1:
        # Check if AI summary exists in session state
        ai_summary_key = f"ai_summary_{case_id}"
        initial_summary = st.session_state.get(ai_summary_key, "")
        
        adjudication_summary = st.text_area(
            "Final Adjudication Summary",
            value=initial_summary,
            height=100,
            placeholder="Enter final adjudication summary with rationale for categorization...",
            key=f"adjudication_summary_{case_id}"
        )
    
    with col_summary2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        
        # AI Assist button for adjudication
        if st.button("💡 AI Assist", key=f"ai_assist_{case_id}", help="Generate AI-powered adjudication summary"):
            try:
                ai_summary = generate_ai_adjudication_summary(case)
                st.session_state[ai_summary_key] = ai_summary
                st.session_state[f"show_ai_options_{case_id}"] = True
                st.rerun()
            except Exception as e:
                st.error("⚠️ Backend Error - Unable to generate AI summary")
    
    # Show AI options if AI summary was generated
    if st.session_state.get(f"show_ai_options_{case_id}", False):
        st.markdown("**AI Generated Summary:**")
        ai_summary = st.session_state.get(ai_summary_key, "")
        
        st.text_area(
            "AI Suggestion:",
            value=ai_summary,
            height=80,
            disabled=True,
            key=f"ai_suggestion_{case_id}"
        )
        
        col_ai1, col_ai2, col_ai3 = st.columns(3)
        with col_ai1:
            if st.button("✅ Accept", key=f"accept_ai_{case_id}"):
                try:
                    st.session_state[f"adjudication_summary_{case_id}"] = ai_summary
                    st.session_state[f"summary_filled_{case_id}"] = True
                    st.session_state[f"show_ai_options_{case_id}"] = False
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Backend Error - Unable to save AI summary")
        
        with col_ai2:
            if st.button("🔁 Regenerate", key=f"regenerate_ai_{case_id}"):
                try:
                    new_summary = generate_ai_adjudication_summary(case)
                    st.session_state[ai_summary_key] = new_summary
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Backend Error - Unable to regenerate summary")
        
        with col_ai3:
            if st.button("❌ Dismiss", key=f"dismiss_ai_{case_id}"):
                try:
                    st.session_state[f"show_ai_options_{case_id}"] = False
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Backend Error")
    
    # Show workflow routing information
    if case_category != "Select Category":
        st.markdown("#### Workflow Routing")
        if case_category == "Fraud":
            st.info("🔄 **Next Steps:** Fraud cases will be routed to Legal Compliance Center → Regulatory Reporting")
        elif case_category == "Non-Fraud":
            st.info("🔄 **Next Steps:** Non-fraud cases will be routed to Case Closure")
        elif case_category == "Other Incident":
            st.info("🔄 **Next Steps:** Incident cases will be routed to Stakeholder Actioner for resolution")
    
    # Action Buttons
    st.markdown("### 🎯 Final Actions")
    
    # Enable submit only when required fields are filled
    can_submit = (
        case_category != "Select Category" and 
        severity_level != "Select Severity" and
        adjudication_summary.strip() and
        (fraud_type != "Select Type" if case_category == "Fraud" else True)
    )
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button(
            "✅ Submit Adjudication", 
            key=f"submit_adjudication_{case_id}",
            disabled=not can_submit,
            help="Complete final adjudication and route to next stage" if can_submit else "Please fill all required fields"
        ):
            process_final_adjudication(case, case_category, fraud_type, severity_level, adjudication_summary, current_user)
            st.rerun()
    
    with col_action2:
        if st.button("📄 Generate Report", key=f"generate_report_{case_id}", disabled=not can_submit):
            generate_adjudication_report(case, case_category, fraud_type, severity_level, adjudication_summary)
    
    with col_action3:
        if st.button("🔄 Send Back for Re-investigation", key=f"send_back_{case_id}"):
            send_back_for_reinvestigation(case, adjudication_summary, current_user)
            st.rerun()

def get_cases_requiring_final_review():
    """Get cases that require final adjudication"""
    try:
        # Get cases from primary review, approvals, and investigation stages that are ready for final adjudication
        cases_for_adjudication = []
        
        # Cases from approved status (after primary review and approvals)
        approved_cases = get_cases_by_status("Approved")
        cases_for_adjudication.extend(approved_cases)
        
        # Cases from investigation completed status
        investigation_completed = get_cases_by_status("Investigation Complete")
        cases_for_adjudication.extend(investigation_completed)
        
        # Cases already in Legal Review but may need re-adjudication
        legal_review_cases = get_cases_by_status("Legal Review")
        cases_for_adjudication.extend(legal_review_cases)
        
        return cases_for_adjudication
        
    except Exception as e:
        st.error(f"Error retrieving cases for final adjudication: {str(e)}")
        return []

def generate_ai_adjudication_summary(case):
    """Generate AI-powered adjudication summary using Gemini"""
    try:
        import os
        from google import genai
        
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        case_data = f"""
        Case ID: {case.get('case_id', 'N/A')}
        Customer: {case.get('customer_name', 'N/A')}
        Case Type: {case.get('case_type', 'N/A')}
        Product: {case.get('product', 'N/A')}
        Loan Amount: ₹{case.get('loan_amount', 'N/A')}
        Status: {case.get('status', 'N/A')}
        Case Description: {case.get('case_description', 'N/A')}
        Risk Score: {case.get('risk_score', 'N/A')}
        """
        
        prompt = f"""As a financial compliance expert, provide a final adjudication summary for this case:

{case_data}

Generate a professional final adjudication summary that includes:
1. Case analysis and findings
2. Risk assessment and categorization rationale
3. Compliance implications
4. Recommended classification (Fraud/Non-Fraud/Other Incident)
5. Next steps recommendation

Keep the summary concise (150-200 words) and professional for regulatory documentation."""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text or "AI adjudication summary generation failed. Please enter summary manually."
        
    except Exception as e:
        return ""

def process_final_adjudication(case, category, fraud_type, severity, summary, current_user):
    """Process final adjudication and route to appropriate workflow"""
    try:
        case_id = case['case_id']
        
        # Save adjudication details
        adjudication_data = {
            'case_id': case_id,
            'category': category,
            'fraud_type': fraud_type,
            'severity': severity,
            'summary': summary,
            'adjudicated_by': current_user,
            'adjudicated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_adjudication_decision(adjudication_data)
        
        # Route based on categorization
        if category == "Fraud":
            # Route to Legal Compliance Center
            update_case_status(case_id, "Legal Review")
            add_case_comment(
                case_id,
                f"FINAL ADJUDICATION: Categorized as {category} ({fraud_type}) with {severity} severity. Routed to Legal Compliance Center for fraud processing.",
                current_user
            )
            st.success(f"✅ Case {case_id} categorized as {category} and routed to Legal Compliance Center")
            
        elif category == "Non-Fraud":
            # Route to Case Closure
            update_case_status(case_id, "Case Closure")
            add_case_comment(
                case_id,
                f"FINAL ADJUDICATION: Categorized as {category} with {severity} severity. Routed to Case Closure.",
                current_user
            )
            st.success(f"✅ Case {case_id} categorized as {category} and routed to Case Closure")
            
        elif category == "Other Incident":
            # Route to Stakeholder Actioner
            update_case_status(case_id, "Stakeholder Action")
            add_case_comment(
                case_id,
                f"FINAL ADJUDICATION: Categorized as {category} with {severity} severity. Routed to Stakeholder Actioner for resolution.",
                current_user
            )
            st.success(f"✅ Case {case_id} categorized as {category} and routed to Stakeholder Actioner")
            
        # Log audit trail
        log_audit(case_id, "Final Adjudication", f"Case adjudicated as {category} by {current_user}", current_user)
        
    except Exception as e:
        st.error(f"Error processing adjudication: {str(e)}")

def save_adjudication_decision(adjudication_data):
    """Save adjudication decision to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create adjudication_decisions table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS adjudication_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    fraud_type TEXT,
                    severity TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    adjudicated_by TEXT NOT NULL,
                    adjudicated_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases (case_id)
                )
            """)
            
            # Insert adjudication decision
            cursor.execute("""
                INSERT INTO adjudication_decisions (
                    case_id, category, fraud_type, severity, summary, adjudicated_by, adjudicated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                adjudication_data['case_id'],
                adjudication_data['category'],
                adjudication_data['fraud_type'],
                adjudication_data['severity'],
                adjudication_data['summary'],
                adjudication_data['adjudicated_by'],
                adjudication_data['adjudicated_at']
            ))
            
            conn.commit()
            
    except Exception as e:
        st.error(f"Error saving adjudication decision: {str(e)}")

def generate_adjudication_report(case, category, fraud_type, severity, summary):
    """Generate adjudication report"""
    st.info("📄 Adjudication report generation functionality will be implemented with PDF export")

def send_back_for_reinvestigation(case, summary, current_user):
    """Send case back for re-investigation"""
    try:
        case_id = case['case_id']
        update_case_status(case_id, "Investigation")
        add_case_comment(
            case_id,
            f"SENT BACK FOR RE-INVESTIGATION: {summary}",
            current_user
        )
        log_audit(case_id, "Sent Back", f"Case sent back for re-investigation by {current_user}", current_user)
        st.success(f"✅ Case {case_id} sent back for re-investigation")
        
    except Exception as e:
        st.error(f"Error sending case back: {str(e)}")