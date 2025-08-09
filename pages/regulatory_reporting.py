import streamlit as st
import pandas as pd
from datetime import datetime, date
from models import get_cases_by_status, get_case_by_id, update_case_status, add_case_comment
from auth import get_current_user, require_auth
from database import get_db_connection
import uuid

def show():
    """Regulatory Reporting module for Fraud cases - FMR1 compliance"""
    
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
        '>Regulatory Reporting</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>FMR1 compliance and RBI reporting center for fraud cases</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Initialize session state
    if "regulatory_case_id" not in st.session_state:
        st.session_state.regulatory_case_id = ""
    if "regulatory_tab" not in st.session_state:
        st.session_state.regulatory_tab = "pending_reports"
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Pending Reports", 
        "📊 FMR1 Reporting", 
        "📤 RBI Submissions", 
        "📈 Analytics"
    ])
    
    with tab1:
        show_pending_reports()
    
    with tab2:
        show_fmr1_reporting()
    
    with tab3:
        show_rbi_submissions()
    
    with tab4:
        show_regulatory_analytics()


def show_pending_reports():
    """Display cases pending regulatory reporting"""
    st.markdown("### Cases Requiring Regulatory Reporting")
    
    # Get fraud cases from Legal Compliance Center
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Get cases categorized as 'Fraud' from Final Adjudication
            cursor.execute("""
                SELECT c.*, cc.comments as adjudication_category 
                FROM cases c 
                LEFT JOIN case_comments cc ON c.case_id = cc.case_id 
                WHERE c.status = 'Legal Review' 
                AND cc.comments LIKE '%Fraud%'
                ORDER BY c.created_at DESC
            """)
            fraud_cases = cursor.fetchall()
    except Exception as e:
        st.error(f"Error retrieving fraud cases: {str(e)}")
        fraud_cases = []
    
    if not fraud_cases:
        st.info("📭 No fraud cases pending regulatory reporting at this time.")
        return
    
    # Display cases in a structured format
    for case in fraud_cases:
        with st.expander(f"Case {case['case_id']} - {case['customer_name']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Case ID:** {case['case_id']}")
                st.write(f"**Customer:** {case['customer_name']}")
                st.write(f"**PAN:** {case.get('pan_number', 'N/A')}")
                st.write(f"**Amount Involved:** ₹{case.get('amount_involved', 0):,.2f}")
            
            with col2:
                st.write(f"**Case Type:** {case.get('case_type', 'N/A')}")
                st.write(f"**Branch:** {case.get('branch_name', 'N/A')}")
                st.write(f"**Date Created:** {case.get('created_at', 'N/A')}")
                st.write(f"**Current Status:** {case['status']}")
            
            with col3:
                st.write(f"**Risk Score:** {case.get('risk_score', 'N/A')}")
                st.write(f"**Priority:** {case.get('priority_level', 'Medium')}")
                st.write(f"**Investigation Type:** {case.get('investigation_type', 'N/A')}")
            
            # Action buttons
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button(f"📝 Create FMR1 Report", key=f"fmr1_{case['case_id']}"):
                    st.session_state.regulatory_case_id = case['case_id']
                    st.session_state.regulatory_tab = "fmr1"
                    st.rerun()
            
            with col_b:
                if st.button(f"📊 View Case Details", key=f"details_{case['case_id']}"):
                    st.session_state.regulatory_case_id = case['case_id']
                    st.rerun()
            
            with col_c:
                if st.button(f"✅ Mark Completed", key=f"complete_{case['case_id']}"):
                    complete_regulatory_reporting(case['case_id'])
                    st.success(f"Case {case['case_id']} regulatory reporting marked as completed")
                    st.rerun()


def show_fmr1_reporting():
    """FMR1 Report generation and submission"""
    st.markdown("### FMR1 Report Generation")
    
    # Case selection
    case_id_input = st.text_input(
        "Enter Case ID for FMR1 Reporting",
        value=st.session_state.get("regulatory_case_id", ""),
        placeholder="e.g., CASE-2025-001"
    )
    
    if case_id_input:
        case_details = get_case_by_id(case_id_input)
        if not case_details:
            st.error("Case not found or not eligible for regulatory reporting")
            return
        
        st.success(f"Case {case_id_input} loaded for FMR1 reporting")
        
        # FMR1 Reporting Form
        with st.form("fmr1_report_form"):
            st.markdown("#### FMR1 Fraud Reporting Details")
            
            # Part 1: Basic Information
            st.markdown("**Part 1: Basic Information**")
            col1, col2 = st.columns(2)
            
            with col1:
                reporting_date = st.date_input("Reporting Date", value=date.today())
                fraud_amount = st.number_input(
                    "Fraud Amount (₹)", 
                    value=float(case_details.get('amount_involved', 0)),
                    min_value=0.0,
                    format="%.2f"
                )
                fraud_type = st.selectbox("Fraud Type", [
                    "Card Fraud",
                    "Internet Banking Fraud", 
                    "Mobile Banking Fraud",
                    "ATM Fraud",
                    "Account Takeover",
                    "Identity Theft",
                    "Document Fraud",
                    "Other"
                ])
                
            with col2:
                detection_method = st.selectbox("Detection Method", [
                    "Customer Complaint",
                    "Internal Monitoring",
                    "Account Monitoring",
                    "Transaction Monitoring",
                    "Audit",
                    "Law Enforcement",
                    "Other"
                ])
                geographical_area = st.selectbox("Geographical Area", [
                    "Metro",
                    "Urban", 
                    "Semi-Urban",
                    "Rural"
                ])
                recovery_amount = st.number_input(
                    "Recovery Amount (₹)", 
                    value=0.0,
                    min_value=0.0,
                    format="%.2f"
                )
            
            # Part 2: Incident Details
            st.markdown("**Part 2: Incident Details**")
            incident_description = st.text_area(
                "Incident Description",
                placeholder="Detailed description of the fraud incident...",
                height=100
            )
            
            modus_operandi = st.text_area(
                "Modus Operandi",
                placeholder="How the fraud was committed...",
                height=100
            )
            
            # Part 3: Action Taken
            st.markdown("**Part 3: Action Taken**")
            col3, col4 = st.columns(2)
            
            with col3:
                police_complaint = st.selectbox("Police Complaint Filed", ["Yes", "No"])
                if police_complaint == "Yes":
                    fir_number = st.text_input("FIR Number")
                    police_station = st.text_input("Police Station")
                else:
                    fir_number = ""
                    police_station = ""
                    
            with col4:
                staff_involvement = st.selectbox("Staff Involvement", ["Yes", "No", "Under Investigation"])
                if staff_involvement == "Yes":
                    staff_action = st.text_area("Action Against Staff", height=80)
                else:
                    staff_action = ""
            
            # Part 4: Prevention Measures
            st.markdown("**Part 4: Prevention Measures**")
            prevention_measures = st.text_area(
                "Prevention Measures Implemented",
                placeholder="Measures taken to prevent similar incidents...",
                height=100
            )
            
            # Submission
            col_submit1, col_submit2, col_submit3 = st.columns(3)
            with col_submit2:
                submitted = st.form_submit_button("📤 Generate FMR1 Report", use_container_width=True)
            
            if submitted:
                # Generate FMR1 report
                fmr1_data = {
                    "case_id": case_id_input,
                    "reporting_date": reporting_date.strftime("%Y-%m-%d"),
                    "fraud_amount": fraud_amount,
                    "fraud_type": fraud_type,
                    "detection_method": detection_method,
                    "geographical_area": geographical_area,
                    "recovery_amount": recovery_amount,
                    "incident_description": incident_description,
                    "modus_operandi": modus_operandi,
                    "police_complaint": police_complaint,
                    "fir_number": fir_number,
                    "police_station": police_station,
                    "staff_involvement": staff_involvement,
                    "staff_action": staff_action,
                    "prevention_measures": prevention_measures,
                    "generated_by": get_current_user(),
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save FMR1 report
                save_fmr1_report(fmr1_data)
                st.success("✅ FMR1 Report generated successfully!")
                
                # Update case status
                add_case_comment(
                    case_id_input,
                    f"FMR1 Report generated and submitted to RBI on {reporting_date}",
                    get_current_user()
                )
                st.rerun()


def show_rbi_submissions():
    """RBI submission tracking and management"""
    st.markdown("### RBI Submission Management")
    
    # Get all FMR1 reports
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM regulatory_reports 
                WHERE report_type = 'FMR1' 
                ORDER BY generated_at DESC
            """)
            fmr1_reports = cursor.fetchall()
    except Exception as e:
        st.error(f"Error retrieving FMR1 reports: {str(e)}")
        fmr1_reports = []
    
    if not fmr1_reports:
        st.info("📭 No FMR1 reports available for submission")
        return
    
    # Display reports
    for report in fmr1_reports:
        with st.expander(f"FMR1 Report - {report['case_id']} ({report['reporting_date']})", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Case ID:** {report['case_id']}")
                st.write(f"**Fraud Amount:** ₹{report['fraud_amount']:,.2f}")
                st.write(f"**Fraud Type:** {report['fraud_type']}")
                st.write(f"**Recovery Amount:** ₹{report['recovery_amount']:,.2f}")
            
            with col2:
                st.write(f"**Reporting Date:** {report['reporting_date']}")
                st.write(f"**Detection Method:** {report['detection_method']}")
                st.write(f"**Police Complaint:** {report['police_complaint']}")
                st.write(f"**Staff Involvement:** {report['staff_involvement']}")
            
            with col3:
                st.write(f"**Generated By:** {report['generated_by']}")
                st.write(f"**Generated At:** {report['generated_at']}")
                submission_status = report.get('submission_status', 'Pending')
                if submission_status == 'Submitted':
                    st.success(f"**Status:** ✅ {submission_status}")
                else:
                    st.warning(f"**Status:** ⏳ {submission_status}")
            
            # Action buttons
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button(f"📥 Download Report", key=f"download_{report['case_id']}"):
                    generate_fmr1_pdf(report)
            
            with col_b:
                if submission_status == 'Pending':
                    if st.button(f"📤 Mark as Submitted", key=f"submit_{report['case_id']}"):
                        mark_report_submitted(report['case_id'])
                        st.success("Report marked as submitted to RBI")
                        st.rerun()


def show_regulatory_analytics():
    """Analytics and reporting dashboard"""
    st.markdown("### Regulatory Reporting Analytics")
    
    # Get analytics data
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Monthly fraud reporting stats
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', reporting_date) as month,
                    COUNT(*) as report_count,
                    SUM(fraud_amount) as total_amount,
                    SUM(recovery_amount) as total_recovery
                FROM regulatory_reports 
                WHERE report_type = 'FMR1'
                GROUP BY strftime('%Y-%m', reporting_date)
                ORDER BY month DESC
                LIMIT 12
            """)
            monthly_stats = cursor.fetchall()
            
            # Fraud type distribution
            cursor.execute("""
                SELECT fraud_type, COUNT(*) as count, SUM(fraud_amount) as amount
                FROM regulatory_reports 
                WHERE report_type = 'FMR1'
                GROUP BY fraud_type
                ORDER BY count DESC
            """)
            fraud_types = cursor.fetchall()
            
    except Exception as e:
        st.error(f"Error retrieving analytics: {str(e)}")
        monthly_stats = []
        fraud_types = []
    
    if monthly_stats:
        # Monthly trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Monthly Fraud Reports")
            df_monthly = pd.DataFrame(monthly_stats, columns=['Month', 'Reports', 'Amount', 'Recovery'])
            st.dataframe(df_monthly, use_container_width=True)
        
        with col2:
            st.markdown("#### Fraud Type Distribution") 
            df_types = pd.DataFrame(fraud_types, columns=['Type', 'Count', 'Amount'])
            st.dataframe(df_types, use_container_width=True)
        
        # Summary metrics
        col_a, col_b, col_c, col_d = st.columns(4)
        
        total_reports = sum([stat['report_count'] for stat in monthly_stats])
        total_amount = sum([stat['total_amount'] for stat in monthly_stats])
        total_recovery = sum([stat['total_recovery'] for stat in monthly_stats])
        recovery_rate = (total_recovery / total_amount * 100) if total_amount > 0 else 0
        
        with col_a:
            st.metric("Total FMR1 Reports", total_reports)
        with col_b:
            st.metric("Total Fraud Amount", f"₹{total_amount:,.0f}")
        with col_c:
            st.metric("Total Recovery", f"₹{total_recovery:,.0f}")
        with col_d:
            st.metric("Recovery Rate", f"{recovery_rate:.1f}%")


def save_fmr1_report(report_data):
    """Save FMR1 report to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create regulatory_reports table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regulatory_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    reporting_date DATE NOT NULL,
                    fraud_amount REAL NOT NULL,
                    fraud_type TEXT NOT NULL,
                    detection_method TEXT,
                    geographical_area TEXT,
                    recovery_amount REAL DEFAULT 0,
                    incident_description TEXT,
                    modus_operandi TEXT,
                    police_complaint TEXT,
                    fir_number TEXT,
                    police_station TEXT,
                    staff_involvement TEXT,
                    staff_action TEXT,
                    prevention_measures TEXT,
                    generated_by TEXT NOT NULL,
                    generated_at DATETIME NOT NULL,
                    submission_status TEXT DEFAULT 'Pending',
                    submitted_at DATETIME NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert FMR1 report
            cursor.execute("""
                INSERT INTO regulatory_reports (
                    case_id, report_type, reporting_date, fraud_amount, fraud_type,
                    detection_method, geographical_area, recovery_amount, incident_description,
                    modus_operandi, police_complaint, fir_number, police_station,
                    staff_involvement, staff_action, prevention_measures, generated_by, generated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_data['case_id'], 'FMR1', report_data['reporting_date'],
                report_data['fraud_amount'], report_data['fraud_type'],
                report_data['detection_method'], report_data['geographical_area'],
                report_data['recovery_amount'], report_data['incident_description'],
                report_data['modus_operandi'], report_data['police_complaint'],
                report_data['fir_number'], report_data['police_station'],
                report_data['staff_involvement'], report_data['staff_action'],
                report_data['prevention_measures'], report_data['generated_by'],
                report_data['generated_at']
            ))
            
            conn.commit()
    except Exception as e:
        st.error(f"Error saving FMR1 report: {str(e)}")


def complete_regulatory_reporting(case_id):
    """Mark regulatory reporting as completed"""
    try:
        update_case_status(case_id, "Regulatory Reporting Complete")
        add_case_comment(
            case_id,
            f"Regulatory reporting completed by {get_current_user()}",
            get_current_user()
        )
    except Exception as e:
        st.error(f"Error completing regulatory reporting: {str(e)}")


def mark_report_submitted(case_id):
    """Mark FMR1 report as submitted to RBI"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE regulatory_reports 
                SET submission_status = 'Submitted', submitted_at = ?
                WHERE case_id = ? AND report_type = 'FMR1'
            """, (datetime.now(), case_id))
            conn.commit()
    except Exception as e:
        st.error(f"Error updating submission status: {str(e)}")


def generate_fmr1_pdf(report_data):
    """Generate PDF version of FMR1 report"""
    st.info("📄 PDF generation functionality will be implemented based on RBI format requirements")
    # This would integrate with the existing PDF generation system