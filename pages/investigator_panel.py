import streamlit as st
from models import get_cases_by_status, get_case_by_id, update_case_status, add_case_comment, get_db_connection
from database import log_audit
from auth import get_current_user, require_role
from datetime import datetime
import uuid

@require_role(["Investigator", "Admin"])
def show():
    """Display investigator panel"""
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
        '>Investigator Panel</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Manage case investigations and generate comprehensive reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Clean form styling to match case entry
    st.markdown("""
    <style>
    .stTextArea > div > div > textarea {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
    }
    .stTextInput > div > div > input {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
    }
    .stSelectbox > div > div > div {
        background-color: #f8f9fa !important;
    }
    .stDateInput > div > div > input {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Tabs for different investigation functions
    tab1, tab2, tab3 = st.tabs(["🗂️ Case Investigation", "📊 Investigation Analytics", "📄 Report Generation"])
    
    with tab1:
        show_investigation_details()
    
    with tab2:
        show_investigation_analytics()
    
    with tab3:
        show_pdf_report_generation()

def show_investigation_details():
    """Show comprehensive investigation details form"""
    st.markdown("### 🔍 Investigation Details")
    
    # Case Selection
    submitted_cases = get_cases_by_status("Submitted") + get_cases_by_status("Under Investigation")
    
    if not submitted_cases:
        st.info("📭 No cases available for investigation")
        return
    
    # Select case for investigation
    case_options = [f"{case['case_id']} - {case['customer_name']}" for case in submitted_cases]
    selected_option = st.selectbox("Select Case for Investigation", case_options)
    
    if not selected_option:
        return
    
    selected_case = selected_option.split(" - ")[0]
    case_details = next((case for case in submitted_cases if case['case_id'] == selected_case), None)
    
    if not case_details:
        st.error("Case not found")
        return
    
    # Display case information
    st.markdown("#### 📄 Case Information")
    from case_display_utils import show_standardized_case_details, show_standardized_customer_info
    
    col1, col2 = st.columns([2, 1])
    with col1:
        show_standardized_case_details(case_details)
        show_standardized_customer_info(case_details)
    
    with col2:
        from case_display_utils import show_standardized_case_history, show_standardized_documents
        show_standardized_case_history(selected_case)
        show_standardized_documents(selected_case)
    
    st.divider()
    
    # Investigation Form
    st.markdown("#### 📝 Investigation Details")
    
    with st.form(f"investigation_form_{selected_case}"):
        # Document Verification Section
        st.markdown("**Document Verification**")
        col1, col2 = st.columns(2)
        with col1:
            pan_verification = st.selectbox("PAN Verification", ["Verified", "Not Verified", "Discrepancy Found"])
            aadhaar_verification = st.selectbox("Aadhaar Verification", ["Verified", "Not Verified", "Discrepancy Found"])
            bank_statement_verification = st.selectbox("Bank Statement", ["Verified", "Not Verified", "Discrepancy Found"])
        with col2:
            address_verification = st.selectbox("Address Verification", ["Verified", "Not Verified", "Discrepancy Found"])
            employment_verification = st.selectbox("Employment Verification", ["Verified", "Not Verified", "Unable to Verify"])
            mobile_verification = st.selectbox("Mobile Verification", ["Verified", "Not Verified", "Invalid"])
        
        # Field Verification Section
        st.markdown("**Field Verification**")
        col3, col4 = st.columns(2)
        with col3:
            cibil_review = st.selectbox("CIBIL Review", ["Completed", "Pending", "Discrepancy Found"])
            form26as_review = st.selectbox("Form 26AS Review", ["Completed", "Pending", "Discrepancy Found"])
        
        # Investigation Summary
        st.markdown("**Investigation Summary**")
        modus_operandi = st.text_area("Modus Operandi Summary", height=100, 
                                     placeholder="Describe the fraud technique/method used...")
        
        root_cause_analysis = st.text_area("Root Cause Analysis", height=100,
                                         placeholder="Identify key lapses or manipulation techniques...")
        
        # Recommended Actions
        st.markdown("**Recommended Actions**")
        col5, col6 = st.columns(2)
        with col5:
            business_action = st.text_input("Business Team Action")
            rcu_action = st.text_input("RCU/Credit Action")
            orm_action = st.text_input("ORM/Policy Action")
        with col6:
            compliance_action = st.text_input("Compliance Action")
            it_action = st.text_input("IT Action")
            legal_action = st.text_input("Legal Action")
        
        # Investigation Status
        investigation_status = st.selectbox("Investigation Status", 
                                          ["In Progress", "Completed", "Requires Review", "Escalated"])
        
        # Investigation Comments
        investigation_comments = st.text_area("Investigation Comments", height=100,
            placeholder="Add detailed investigation comments...")
        
        # Document Upload
        st.markdown("**Investigation Documents**")
        investigation_docs = st.file_uploader(
            "Upload Investigation Documents",
            type=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
            accept_multiple_files=True,
            key=f"inv_docs_{selected_case}"
        )
        
        # Submit Investigation
        if st.form_submit_button("💾 Save Investigation Details", type="primary"):
            # Get current user
            current_user = get_current_user()
            username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
            
            # Save investigation data
            investigation_data = {
                'case_id': selected_case,
                'pan_verification': pan_verification,
                'aadhaar_verification': aadhaar_verification,
                'bank_statement_verification': bank_statement_verification,
                'address_verification': address_verification,
                'employment_verification': employment_verification,
                'mobile_verification': mobile_verification,
                'cibil_review': cibil_review,
                'form26as_review': form26as_review,
                'modus_operandi': modus_operandi,
                'root_cause_analysis': root_cause_analysis,
                'business_action': business_action,
                'rcu_action': rcu_action,
                'orm_action': orm_action,
                'compliance_action': compliance_action,
                'it_action': it_action,
                'legal_action': legal_action,
                'investigation_status': investigation_status,
                'investigation_comments': investigation_comments,
                'investigated_by': username,
                'investigation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Handle file uploads
            uploaded_files_info = []
            if investigation_docs:
                uploaded_files_info = handle_investigation_file_uploads(investigation_docs, selected_case)
            
            # Save to investigation_details table
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO investigation_details (
                            case_id, pan_verification, aadhaar_verification, bank_statement_verification,
                            address_verification, employment_verification, mobile_verification,
                            cibil_review, form26as_review, modus_operandi, root_cause_analysis,
                            business_action, rcu_action, orm_action, compliance_action, 
                            it_action, legal_action, investigation_status, investigation_comments,
                            investigated_by, investigation_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        investigation_data['case_id'],
                        investigation_data['pan_verification'],
                        investigation_data['aadhaar_verification'],
                        investigation_data['bank_statement_verification'],
                        investigation_data['address_verification'],
                        investigation_data['employment_verification'],
                        investigation_data['mobile_verification'],
                        investigation_data['cibil_review'],
                        investigation_data['form26as_review'],
                        investigation_data['modus_operandi'],
                        investigation_data['root_cause_analysis'],
                        investigation_data['business_action'],
                        investigation_data['rcu_action'],
                        investigation_data['orm_action'],
                        investigation_data['compliance_action'],
                        investigation_data['it_action'],
                        investigation_data['legal_action'],
                        investigation_data['investigation_status'],
                        investigation_data['investigation_comments'],
                        investigation_data['investigated_by'],
                        investigation_data['investigation_date']
                    ))
                    conn.commit()
                
                # Add comprehensive investigation summary to case comments
                investigation_summary = f"""
INVESTIGATION COMPLETED by {username}

Document Verification:
- PAN: {pan_verification} | Aadhaar: {aadhaar_verification}
- Bank Statement: {bank_statement_verification} | Address: {address_verification}

Other Verifications:
- Employment: {employment_verification} | Mobile: {mobile_verification}
- CIBIL: {cibil_review} | Form 26AS: {form26as_review}

Investigation Summary:
- Modus Operandi: {modus_operandi[:100] if modus_operandi else 'Not provided'}{'...' if modus_operandi and len(modus_operandi) > 100 else ''}
- Root Cause: {root_cause_analysis[:100] if root_cause_analysis else 'Not provided'}{'...' if root_cause_analysis and len(root_cause_analysis) > 100 else ''}

Status: {investigation_status}
Comments: {investigation_comments[:100] if investigation_comments else 'No additional comments'}{'...' if investigation_comments and len(investigation_comments) > 100 else ''}
                """
                
                add_case_comment(
                    selected_case, 
                    investigation_summary, 
                    username,
                    "Investigation Report"
                )
                
                # Update case status based on investigation status
                if investigation_status == "Completed":
                    update_case_status(selected_case, "Final Review", username)
                elif investigation_status == "Escalated":
                    update_case_status(selected_case, "Escalated", username)
                elif investigation_status == "In Progress":
                    update_case_status(selected_case, "Under Investigation", username)
                
                st.success("✅ Investigation details saved successfully!")
                st.info("📋 Investigation findings have been added to case comments for reviewer workflow.")
                
                log_audit(
                    selected_case, 
                    "Investigation Completed", 
                    f"Investigation completed by {username}. Status: {investigation_status}",
                    username
                )
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error saving investigation details: {str(e)}")

def handle_investigation_file_uploads(files, case_id):
    """Handle file uploads for investigation"""
    uploaded_files = []
    
    for file in files:
        if file is not None:
            # Create unique filename
            file_ext = file.name.split('.')[-1]
            unique_filename = f"investigation_{case_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
            
            # Save file logic would go here
            uploaded_files.append({
                'original_name': file.name,
                'saved_name': unique_filename,
                'size': len(file.getvalue())
            })
    
    return uploaded_files

def show_investigation_analytics():
    """Show investigation analytics"""
    st.markdown("### 📊 Investigation Analytics")
    
    # Get investigation statistics
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Cases by investigation status
        cursor.execute("""
            SELECT investigation_status, COUNT(*) as count 
            FROM investigation_details 
            GROUP BY investigation_status
        """)
        status_data = cursor.fetchall()
        
        if status_data:
            st.markdown("#### Investigation Status Distribution")
            for status, count in status_data:
                st.metric(f"{status} Cases", count)
        else:
            st.info("No investigation data available")

def show_pdf_report_generation():
    """Show PDF report generation"""
    st.markdown("### 📄 Investigation Report Generation")
    
    # Get completed investigations
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT case_id FROM investigation_details 
            WHERE investigation_status = 'Completed'
            ORDER BY investigation_date DESC
        """)
        completed_cases = [row[0] for row in cursor.fetchall()]
    
    if completed_cases:
        selected_case = st.selectbox("Select Case for Report", completed_cases)
        
        if st.button("📄 Generate PDF Report"):
            st.success(f"PDF report generated for case {selected_case}")
            st.info("PDF report generation feature coming soon...")
    else:
        st.info("No completed investigations available for reporting")