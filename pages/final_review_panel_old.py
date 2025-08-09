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
    
    # Sub-header for this specific page  
    st.markdown("""
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
        '>FINAL ADJUDICATION</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Final categorization and adjudication of investigated cases**")
    
    current_user = get_current_user()
    
    # Get cases requiring final review or those sent to Legal/Actioner but not yet completed
    final_review_cases = get_cases_requiring_final_review()
    
    if final_review_cases:
        st.markdown(f"**{len(final_review_cases)} case(s) requiring final review**")
        
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
        st.info("📭 No cases requiring final review at this time")
        st.markdown("""
        **Cases will appear here when:**
        - Investigation has been completed
        - Primary review is finished
        - Cases are ready for final review before legal processing
        - Cases sent to Legal/Actioner that haven't been completed by BOTH
        
        **Note:** Cases remain visible until BOTH Legal and Actioner are closed. If only one action is completed, the case stays in queue.
        """)

def show_enhanced_case_details(case, current_user):
    """Display detailed case information with enhanced final review actions"""
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
        
        # AI Assist button in bottom left corner style
        if st.button("💡 AI Assist", key=f"ai_assist_{case_id}", help="Generate AI-powered summary"):
            try:
                # Generate AI summary using case details
                ai_summary = generate_ai_case_summary(case)
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
                    st.session_state[f"review_summary_{case_id}"] = ai_summary
                    st.session_state[f"summary_filled_{case_id}"] = True
                    st.session_state[f"show_ai_options_{case_id}"] = False
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Backend Error - Unable to save AI summary")
        
        with col_ai2:
            if st.button("🔁 Regenerate", key=f"regenerate_ai_{case_id}"):
                try:
                    new_summary = generate_ai_case_summary(case, regenerate=True)
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
    
    # Check if summary is filled (either manually or via AI)
    summary_filled = bool(review_summary.strip()) or st.session_state.get(f"summary_filled_{case_id}", False)
    
    # PDF Generation Section - Only enabled after summary is filled
    st.markdown("### 📄 Generate Report")
    if summary_filled:
        show_pdf_download_button(case, "📄 Generate Final Review PDF")
    else:
        st.button("📄 Generate Report", disabled=True, help="Please fill the review summary first", key=f"pdf_gen_disabled_{case['case_id']}")

def generate_ai_case_summary(case, regenerate=False):
    """Generate AI-powered case summary using Gemini"""
    try:
        import os
        from google import genai
        from google.genai import types
        
        # Initialize Gemini client
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Prepare case data for AI analysis
        case_data = f"""
        Case ID: {case.get('case_id', 'N/A')}
        Customer: {case.get('customer_name', 'N/A')}
        Case Type: {case.get('case_type', 'N/A')}
        Product: {case.get('product', 'N/A')}
        Loan Amount: ₹{case.get('loan_amount', 'N/A')}
        Region: {case.get('region', 'N/A')}
        Status: {case.get('status', 'N/A')}
        Case Description: {case.get('case_description', 'N/A')}
        Customer Mobile: {case.get('customer_mobile', 'N/A')}
        Customer Email: {case.get('customer_email', 'N/A')}
        Disbursement Date: {case.get('disbursement_date', 'N/A')}
        """
        
        prompt = f"""As a financial compliance expert, provide a comprehensive final review summary for this case:

{case_data}

Generate a professional final review summary that includes:
1. Case overview and key facts
2. Risk assessment and findings
3. Investigation outcomes
4. Compliance considerations
5. Recommended actions

Keep the summary concise (150-200 words) and professional for regulatory documentation."""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text or "AI summary generation failed. Please enter summary manually."
        
    except Exception as e:
        from error_handler import warning_message
        warning_message("AI Assistant Unavailable", "AI summary generation is currently unavailable. Please enter the review summary manually.")
        return ""

def show_case_details(case, current_user, allow_review=False):
    """Legacy function - redirect to enhanced version"""
    show_enhanced_case_details(case, current_user)
    
    # Show current status for Legal Review cases
    if case['status'] == 'Legal Review':
        st.markdown("### 📊 Processing Status")
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            legal_status = case.get('legal_status', 'Pending')
            legal_color = "🟢" if legal_status == 'Completed' else "🟡"
            st.markdown(f"**⚖️ Legal Review:** {legal_color} {legal_status}")
        
        with status_col2:
            actioner_status = case.get('actioner_status', 'Pending')
            actioner_color = "🟢" if actioner_status == 'Completed' else "🟡"
            st.markdown(f"**🔒 Actioner:** {actioner_color} {actioner_status}")
        
        # Show completion status and closure option
        if case.get('legal_status') == 'Completed' and case.get('actioner_status') == 'Completed':
            st.success("✅ Both Legal and Actioner have completed their work. Case can be closed.")
            
            # Add final closure option
            if st.button(f"🔒 Mark Case as Closed", key=f"close_case_{case_id}"):
                username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
                if update_case_status(case_id, "Closed", username):
                    add_case_comment(case_id, "CASE CLOSED - Both Legal and Actioner completed", username, "Case Closure")
                    log_audit(case_id, "Case Closed", f"Case closed after Legal and Actioner completion by {username}", username)
                    st.success("✅ Case marked as closed")
                    st.rerun()
        elif case.get('legal_status') == 'Completed' or case.get('actioner_status') == 'Completed':
            completed_action = "Legal" if case.get('legal_status') == 'Completed' else "Actioner"
            pending_action = "Actioner" if case.get('legal_status') == 'Completed' else "Legal"
            st.info(f"⏳ {completed_action} completed. Waiting for {pending_action} to complete before case can be closed.")
        else:
            st.warning("⏳ Both Legal and Actioner actions are still pending.")

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

# Helper functions for getting cases requiring final review
                review_comment = st.text_area(
                    "Action Comment",
                    placeholder="Enter comments for sending to Legal/Actioner...",
                    height=80,
                    key=f"pending_action_comment_{case_id}"
                )
                
                # Note: Team Action Recommendations moved to new Final Review form section below
                
                # Create table header
                st.markdown("""
                <style>
                .team-action-table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0;
                }
                .team-action-table th {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                    color: #495057;
                }
                .team-action-table td {
                    border: 1px solid #dee2e6;
                    padding: 10px;
                    vertical-align: middle;
                }
                .team-action-table tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
                .team-action-table tr:hover {
                    background-color: #e9ecef;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Display table header
                st.markdown("""
                <table class="team-action-table">
                    <thead>
                        <tr>
                            <th width="10%">✅ Select</th>
                            <th width="25%">Team Name</th>
                            <th width="35%">Action Options</th>
                            <th width="30%">Team Email</th>
                        </tr>
                    </thead>
                </table>
                """, unsafe_allow_html=True)
                
                # Create form rows for each team
                selected_teams = []
                for i, team_info in enumerate(team_data):
                    team_col1, team_col2, team_col3, team_col4 = st.columns([0.1, 0.25, 0.35, 0.3])
                    
                    with team_col1:
                        team_selected = st.checkbox("Select Team", key=f"select_team_{i}_{case_id}", label_visibility="collapsed")
                    
                    with team_col2:
                        st.markdown(f"**{team_info['team']}**")
                    
                    with team_col3:
                        action_option = st.selectbox("Action Type", 
                            [team_info['action'], "Not Required"],
                            key=f"action_option_{i}_{case_id}",
                            label_visibility="collapsed"
                        )
                    
                    with team_col4:
                        # Make team email editable
                        team_email = st.text_input("Team Email", 
                            value=team_info['email'], 
                            key=f"team_email_{i}_{case_id}",
                            label_visibility="collapsed")
                    
                    # Store selected teams and their actions
                    if team_selected:
                        selected_teams.append(f"{team_info['team']}: {action_option} (Email: {team_email})")
                
                st.markdown("---")
                # Actioner Action Type dropdown
                st.markdown("#### Actioner Action Type")
                actioner_action_type = st.selectbox("Select Actioner Action Type",
                    ["Recovery Closure", "Settlement Closure", "Write-off", "Transfer to Legal"],
                    key=f"pending_actioner_action_{case_id}")
                
                # Send to Action button (below Send Case for Action)
                send_to_action = st.form_submit_button("🔒 Send to Action", type="primary")
                
                # Legal Action Type section
                st.markdown("#### Legal Action Type")
                legal_action_type = st.selectbox("Select Legal Action Type", 
                    ["Show Cause Notice (SCN)", "Reasoned Order", "Legal Opinion", "Recovery Notice"],
                    key=f"pending_legal_action_{case_id}")
                
                # Send to Legal button (below Legal Action Type)
                send_to_legal_now = st.form_submit_button("⚖️ Send to Legal")
                
                # Handle form submissions
                if send_to_action:
                    if review_comment.strip():
                        username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
                        
                        # Build action summary
                        action_summary = f"SENT TO ACTION ({actioner_action_type}): {review_comment}"
                        if selected_teams:
                            action_summary += f"\n\nSelected Team Actions:\n" + "\n".join([f"• {team}" for team in selected_teams])
                        
                        add_case_comment(case_id, action_summary, username, "Final Review")
                        log_audit(case_id, f"Sent to Action ({actioner_action_type})", f"Case sent to Action by {username} with {len(selected_teams)} team actions", username)
                        st.success(f"✅ Case sent to Action for {actioner_action_type} with {len(selected_teams)} team action(s)")
                        st.rerun()
                    else:
                        st.warning("Please add a comment before sending to Action")
                
                elif send_to_legal_now:
                    if review_comment.strip():
                        username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
                        add_case_comment(case_id, f"SENT TO LEGAL ({legal_action_type}): {review_comment}", username, "Final Review")
                        log_audit(case_id, f"Sent to Legal ({legal_action_type})", f"Case sent to Legal by {username}", username)
                        st.success(f"✅ Case sent to Legal for {legal_action_type}")
                        st.rerun()
                    else:
                        st.warning("Please add a comment before sending to Legal")
    
    # Final review actions (only for cases still in Final Review status)
    case_id = case['case_id']  # Define case_id from case data
    if allow_review and case['status'] == 'Final Review':
        st.markdown("**🎯 Final Review Actions**")
        
        with st.form(f"final_review_form_{case_id}"):
            review_comment = st.text_area(
                "Final Review Comment",
                placeholder="Enter your final review comments...",
                height=100,
                key=f"final_review_comment_{case_id}"
            )
            
            # Separate sections for Legal and Actioner
            st.markdown("### ⚖️ Legal Review Actions")
            legal_col1, legal_col2 = st.columns(2)
            
            with legal_col1:
                send_to_legal = st.form_submit_button("⚖️ Send to Legal (SCN/Reasoned Order)", type="primary")
            with legal_col2:
                legal_reason = st.selectbox("Legal Action Type", 
                    ["Show Cause Notice (SCN)", "Reasoned Order", "Legal Opinion", "Recovery Notice"],
                    key=f"legal_action_{case_id}")
            
            st.markdown("### 🔒 Actioner Actions")
            actioner_col1, actioner_col2 = st.columns(2)
            
            with actioner_col1:
                send_to_actioner = st.form_submit_button("🔒 Send to Actioner (Case Closure)")
            with actioner_col2:
                actioner_action = st.selectbox("Closure Action Type",
                    ["Recovery Closure", "Settlement Closure", "Write-off", "Transfer to Legal"],
                    key=f"actioner_action_{case_id}")
            
            # Recommended Actions Section
            st.markdown("### 📤 Recommended Actions")
            st.markdown("**Select team(s) for specific actions and communications:**")
            
            # Team-specific communication templates
            team_templates = {
                "Audit Team": "Dear Audit Team,\nPlease initiate a review of this account under exceptional transaction monitoring.",
                "Product Team": "Dear Product Team,\nPlease re-evaluate the product rules or features associated with this case.",
                "Operations Team": "Dear Operations Team,\nPlease restrict any further disbursements or benefits on the said account.",
                "Credit Team": "Dear Credit Team,\nPlease revisit the credit underwriting and risk profiling criteria used in this case.",
                "HR/Training Team": "Dear HR/Training Team,\nPlease conduct a refresher or sensitisation session for the involved staff.",
                "Legal Team (Litigation)": "Dear Legal Team (Litigation),\nPlease initiate civil/criminal litigation proceedings based on the current findings.",
                "Risk Analytics Team": "Dear Risk Analytics Team,\nPlease include this case in trend analysis and update the fraud typology repository."
            }
            
            # Multi-select dropdown for teams
            selected_teams = st.multiselect(
                "Select Team(s) for Communication:",
                list(team_templates.keys()),
                key=f"recommended_teams_{case_id}"
            )
            
            # Show templates for selected teams
            if selected_teams:
                st.markdown("**📝 Communication Templates:**")
                for team in selected_teams:
                    with st.expander(f"📧 {team} - Communication Template", expanded=True):
                        st.text_area(
                            f"Template for {team}:",
                            value=team_templates[team],
                            height=80,
                            disabled=True,
                            key=f"template_{team}_{case_id}"
                        )
            
            # Optional additional instructions
            additional_instructions = st.text_area(
                "✅ [Optional] Additional Instructions",
                placeholder="Add case-specific or custom comments here before sending...",
                height=100,
                key=f"additional_instructions_{case_id}"
            )
            
            st.markdown("### 🔄 Other Actions")
            other_col1, other_col2, other_col3 = st.columns(3)
            
            with other_col1:
                return_to_investigation = st.form_submit_button("🔄 Return to Investigation")
            with other_col2:
                direct_approve = st.form_submit_button("✅ Direct Approve")
            with other_col3:
                reject_case = st.form_submit_button("❌ Reject Case")
            
            # Handle form submissions
            if send_to_legal:
                if review_comment.strip():
                    username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
                    # Update status to trigger both Legal and Actioner panels
                    if update_case_status(case_id, "Legal Review", username):
                        # Prepare comment with recommended actions if selected
                        comment_text = f"FINAL REVIEW COMPLETED - Sent to Legal ({legal_reason}): {review_comment}"
                        
                        if selected_teams:
                            comment_text += f"\n\n📤 Recommended Actions sent to {len(selected_teams)} team(s):"
                            for team in selected_teams:
                                comment_text += f"\n• {team}: {team_templates[team][:100]}..."
                        
                        if additional_instructions.strip():
                            comment_text += f"\n\n✅ Additional Instructions: {additional_instructions}"
                        
                        # Add status marker for parallel processing
                        add_case_comment(case_id, comment_text, username, "Final Review")
                        log_audit(case_id, f"Final Review - Sent to Legal ({legal_reason})", f"Case sent to Legal by {username} with {len(selected_teams)} team recommendations", username)
                        st.success(f"✅ Case sent to Legal Review for {legal_reason}" + (f" with recommendations to {len(selected_teams)} teams" if selected_teams else ""))
                        st.rerun()
                else:
                    st.warning("Please add a comment before sending to legal")
            
            elif send_to_actioner:
                if review_comment.strip():
                    username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
                    if update_case_status(case_id, "Legal Review", username):  # Same status for parallel processing
                        # Prepare comment with recommended actions if selected
                        comment_text = f"FINAL REVIEW COMPLETED - Sent to Actioner ({actioner_action}): {review_comment}"
                        
                        if selected_teams:
                            comment_text += f"\n\n📤 Recommended Actions sent to {len(selected_teams)} team(s):"
                            for team in selected_teams:
                                comment_text += f"\n• {team}: {team_templates[team][:100]}..."
                        
                        if additional_instructions.strip():
                            comment_text += f"\n\n✅ Additional Instructions: {additional_instructions}"
                        
                        add_case_comment(case_id, comment_text, username, "Final Review")
                        log_audit(case_id, f"Final Review - Sent to Actioner ({actioner_action})", f"Case sent to Actioner by {username} with {len(selected_teams)} team recommendations", username)
                        st.success(f"✅ Case sent to Actioner for {actioner_action}" + (f" with recommendations to {len(selected_teams)} teams" if selected_teams else ""))
                        st.rerun()
                else:
                    st.warning("Please add a comment before sending to actioner")
            
            elif direct_approve:
                if review_comment.strip():
                    username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
                    if update_case_status(case_id, "Approved", username):
                        # Prepare comment with recommended actions if selected
                        comment_text = f"FINAL REVIEW COMPLETED - Approved for Action: {review_comment}"
                        
                        if selected_teams:
                            comment_text += f"\n\n📤 Recommended Actions sent to {len(selected_teams)} team(s):"
                            for team in selected_teams:
                                comment_text += f"\n• {team}: {team_templates[team][:100]}..."
                        
                        if additional_instructions.strip():
                            comment_text += f"\n\n✅ Additional Instructions: {additional_instructions}"
                        
                        add_case_comment(case_id, comment_text, username, "Final Review")
                        log_audit(case_id, "Final Review - Approved", f"Final review approved by {username} with {len(selected_teams)} team recommendations", username)
                        st.success("✅ Case approved for action" + (f" with recommendations to {len(selected_teams)} teams" if selected_teams else ""))
                        st.rerun()
                else:
                    st.warning("Please add a comment before approving")
            
            elif return_to_investigation:
                if review_comment.strip():
                    username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
                    if update_case_status(case_id, "Under Investigation", username):
                        add_case_comment(case_id, f"RETURNED TO INVESTIGATION from Final Review: {review_comment}", username, "Final Review")
                        log_audit(case_id, "Returned to Investigation", f"Returned by {username} from final review", username)
                        st.success("🔄 Case returned to investigation")
                        st.rerun()
                else:
                    st.warning("Please add a comment before returning to investigation")
            
            elif reject_case:
                if review_comment.strip():
                    username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
                    if update_case_status(case_id, "Rejected", username):
                        add_case_comment(case_id, f"CASE REJECTED at Final Review: {review_comment}", username, "Final Review")
                        log_audit(case_id, "Case Rejected", f"Case rejected by {username} at final review", username)
                        st.success("❌ Case rejected")
                        st.rerun()
                else:
                    st.warning("Please add a comment before rejecting")

def get_cases_requiring_final_review():
    """Get cases that require final review or are in Legal/Actioner but not completed by both"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get cases in Final Review status
        cursor.execute("SELECT * FROM cases WHERE status = 'Final Review' ORDER BY updated_at DESC")
        final_review_cases = [dict(row) for row in cursor.fetchall()]
        
        # Get cases in Legal Review that haven't been closed by both Legal and Actioner
        cursor.execute("SELECT * FROM cases WHERE status = 'Legal Review' ORDER BY updated_at DESC")
        legal_cases = [dict(row) for row in cursor.fetchall()]
        
        # Check which Legal Review cases have both Legal and Actioner completion
        active_legal_cases = []
        for case in legal_cases:
            case_id = case['case_id']
            
            # Check if case has been completed by both Legal and Actioner
            cursor.execute("""
                SELECT comment, comment_type FROM case_comments 
                WHERE case_id = ? AND (
                    comment LIKE '%LEGAL DOCUMENT SENT%' OR 
                    comment LIKE '%LEGAL CLEARED%' OR 
                    comment LIKE '%CASE CLOSED BY LEGAL%' OR
                    comment LIKE '%ACTIONER COMPLETED%' OR
                    comment LIKE '%RECOVERY CLOSURE%' OR
                    comment LIKE '%SETTLEMENT CLOSURE%' OR
                    comment LIKE '%WRITE-OFF COMPLETED%'
                )
                ORDER BY created_at DESC
            """, (case_id,))
            
            completion_comments = cursor.fetchall()
            
            # Check if both legal and actioner have completed their work
            legal_completed = any('LEGAL' in comment[0].upper() and 
                                ('SENT' in comment[0] or 'CLEARED' in comment[0] or 'CLOSED' in comment[0]) 
                                for comment in completion_comments)
            
            actioner_completed = any(('ACTIONER' in comment[0].upper() or 
                                    'RECOVERY CLOSURE' in comment[0].upper() or 
                                    'SETTLEMENT CLOSURE' in comment[0].upper() or 
                                    'WRITE-OFF' in comment[0].upper()) 
                                   for comment in completion_comments)
            
            # Always include Legal Review cases in Final Review Panel until BOTH are completed
            # This ensures cases stay visible even if only one action is closed
            case['legal_status'] = 'Completed' if legal_completed else 'Pending'
            case['actioner_status'] = 'Completed' if actioner_completed else 'Pending'
            
            # Add all Legal Review cases - they stay until both Legal AND Actioner are completed
            active_legal_cases.append(case)
        
        # Combine both lists and remove duplicates
        all_cases = final_review_cases + active_legal_cases
        
        # Remove duplicates by case_id
        seen_case_ids = set()
        unique_cases = []
        for case in all_cases:
            if case['case_id'] not in seen_case_ids:
                seen_case_ids.add(case['case_id'])
                unique_cases.append(case)
        
        return unique_cases