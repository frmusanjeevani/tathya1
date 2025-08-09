import streamlit as st
import pandas as pd
from datetime import datetime, date
from models import get_cases_by_status, get_case_by_id, create_case_allocation, get_case_allocations
from auth import get_current_user, require_role
from utils import generate_case_id, save_uploaded_file
import os

@require_role(["Investigator", "Admin"])
def show():
    """Case Allocation module with seamless data transfer from Case Entry"""
    
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
        '>Case Allocation</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Seamlessly transfer and allocate cases from Case Entry to investigation teams</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Tab options
    tab1, tab2, tab3 = st.tabs(["📋 New Allocation", "📂 View Allocations", "📊 Allocation Statistics"])
    
    with tab1:
        st.markdown("### Create New Case Allocation")
        show_case_allocation_form(current_user)
    
    with tab2:
        st.markdown("### Current Case Allocations")
        show_allocated_cases()
    
    with tab3:
        st.markdown("### Allocation Analytics")
        show_allocation_statistics()

def show_case_allocation_form(current_user):
    """Show comprehensive case allocation form with data transfer from Case Entry"""
    
    # Get available cases from Case Entry (status = 'Registered')
    available_cases = get_cases_by_status("Registered")
    
    # Debug: Show how many cases were found
    st.info(f"Found {len(available_cases) if available_cases else 0} registered cases available for allocation")
    
    if not available_cases:
        st.warning("📭 No cases available for allocation. Please register new cases in Case Entry first.")
        st.info("If cases exist but are not showing, they may already be allocated or have a different status.")
        return
    
    # Case Selection Section
    st.markdown("#### 🎯 Case Assignment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Case selection dropdown
        case_options = []
        for case in available_cases:
            case_id = case.get('case_id', 'Unknown')
            category = case.get('category', 'Unknown')
            case_type = case.get('case_type', 'Unknown')
            case_options.append(f"{case_id} - {category} - {case_type}")
        
        selected_case_display = st.selectbox(
            "Case Selection",
            options=case_options,
            help="Select a case from Case Entry to allocate for investigation"
        )
        
        # Extract selected case ID
        selected_case_id = selected_case_display.split(' - ')[0] if selected_case_display else None
        
        # Investigation Type
        investigation_type = st.radio(
            "Investigation Type",
            options=["Internal Investigation", "External Investigation", "Agency Investigation", "Regional Investigation"],
            horizontal=True
        )
    
    with col2:
        # Assigned Investigator
        investigators = ["John Smith", "Sarah Johnson", "Mike Davis", "Lisa Wong", "David Brown", "Emma Wilson"]
        assigned_investigator = st.selectbox(
            "Assigned Investigator",
            options=investigators
        )
        
        # Priority Level
        priority_level = st.selectbox(
            "Priority Level",
            options=["High", "Medium", "Low", "Urgent"]
        )
        
        # Expected Completion
        expected_completion = st.date_input(
            "Expected Completion",
            value=date.today(),
            min_value=date.today()
        )
    
    # Get selected case data for auto-population
    selected_case_data = None
    if selected_case_id:
        for case in available_cases:
            if case.get('case_id') == selected_case_id:
                selected_case_data = case
                break
    
    # Allocation Notes Section
    st.markdown("#### 📝 Allocation Notes")
    
    col1, col2 = st.columns(2)
    with col1:
        allocation_notes = st.text_area(
            "Allocation Notes",
            height=100,
            help="General notes about the case allocation"
        )
    
    with col2:
        special_instructions = st.text_area(
            "Special Instructions",
            height=100,
            help="Specific instructions for the investigator"
        )
    
    # Basic Case Info Section (Auto-populated from Case Entry)
    st.markdown("#### ℹ️ Basic Case Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Product options
        product_options = ["Home Loan", "Personal Loan", "Business Loan", "Credit Card", "Auto Loan", "Other"]
        product = st.selectbox(
            "Product",
            options=product_options,
            index=0
        )
        
        branch_location = st.text_input(
            "Branch/Location",
            value=selected_case_data.get('branch_location', '') if selected_case_data else '',
            help="Branch or location details"
        )
    
    with col2:
        # Region options
        region_options = ["North", "South", "East", "West", "Central", "Northeast"]
        region = st.selectbox(
            "Region",
            options=region_options
        )
    
    # Loan Information Section
    st.markdown("#### 💰 Loan Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        lan = st.text_input(
            "LAN (Loan Account Number)",
            value=selected_case_data.get('lan', '') if selected_case_data else '',
            help="Loan Account Number"
        )
    
    with col2:
        customer_name = st.text_input(
            "Customer Name",
            value=selected_case_data.get('customer_name', '') if selected_case_data else '',
            help="Primary customer name"
        )
    
    with col3:
        loan_amount = st.number_input(
            "Loan Amount",
            min_value=0.0,
            value=float(selected_case_data.get('loan_amount', 0)) if selected_case_data and selected_case_data.get('loan_amount') else 0.0,
            step=1000.0,
            format="%.2f"
        )
    
    with col4:
        disbursement_date = st.date_input(
            "Disbursement Date",
            value=date.today()
        )
    
    # Customer Demographics Section
    st.markdown("#### 👤 Customer Demographics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_of_birth = st.date_input(
            "Date of Birth",
            value=date(1990, 1, 1),
            max_value=date.today()
        )
        
        pan = st.text_input(
            "PAN",
            value=selected_case_data.get('pan', '') if selected_case_data else '',
            max_chars=10,
            help="PAN Card Number"
        )
        
        mobile_number = st.text_input(
            "Mobile Number",
            value=selected_case_data.get('mobile_number', '') if selected_case_data else '',
            max_chars=10,
            help="Primary mobile number"
        )
    
    with col2:
        email_id = st.text_input(
            "Email ID",
            value=selected_case_data.get('email_id', '') if selected_case_data else '',
            help="Primary email address"
        )
        
        # Masked Aadhaar display
        aadhaar_number = st.text_input(
            "Aadhaar Number",
            value=selected_case_data.get('aadhaar_number', '') if selected_case_data else '',
            max_chars=12,
            help="Aadhaar card number"
        )
        
        # Relationship Status
        relationship_status = st.selectbox(
            "Relationship Status",
            options=["Single", "Married", "Divorced", "Widowed", "Other"]
        )
    
    with col3:
        complete_address = st.text_area(
            "Complete Address",
            value=selected_case_data.get('complete_address', '') if selected_case_data else '',
            height=120,
            help="Full residential address"
        )
    
    # Financial Profile Section
    st.markdown("#### 💼 Financial Profile")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Occupation options
        occupation_options = ["Salaried", "Self-Employed", "Business Owner", "Professional", "Retired", "Student", "Other"]
        occupation = st.selectbox(
            "Occupation",
            options=occupation_options
        )
    
    with col2:
        # Monthly Income Range
        income_ranges = ["< 25,000", "25,000 - 50,000", "50,000 - 1,00,000", "1,00,000 - 2,50,000", "2,50,000 - 5,00,000", "> 5,00,000"]
        monthly_income_range = st.selectbox(
            "Monthly Income Range",
            options=income_ranges
        )
    
    with col3:
        cibil_score = st.number_input(
            "CIBIL Score",
            min_value=300,
            max_value=900,
            value=750,
            step=1
        )
    
    # Business Profile Section
    st.markdown("#### 🏢 Business Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        gst_business_proof = st.file_uploader(
            "GST/Business Proof",
            type=['pdf', 'jpg', 'jpeg', 'png'],
            help="Upload GST certificate or business proof documents"
        )
    
    # Documents Section
    st.markdown("#### 📄 Documents")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pan_card_image = st.file_uploader(
            "PAN Card Image",
            type=['jpg', 'jpeg', 'png', 'pdf'],
            help="Upload PAN card document"
        )
    
    with col2:
        aadhaar_card_image = st.file_uploader(
            "Aadhaar Card Image",
            type=['jpg', 'jpeg', 'png', 'pdf'],
            help="Upload Aadhaar card document"
        )
    
    with col3:
        customer_photo = st.file_uploader(
            "Customer Photo",
            type=['jpg', 'jpeg', 'png'],
            help="Upload customer photograph"
        )
    
    with col4:
        supporting_documents = st.file_uploader(
            "Supporting Documents",
            type=['pdf', 'jpg', 'jpeg', 'png', 'docx'],
            accept_multiple_files=True,
            help="Upload additional supporting documents"
        )
    
    # Submit button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎯 Create Case Allocation", type="primary", use_container_width=True):
            if not selected_case_id:
                st.error("Please select a case to allocate")
                return
            
            # Prepare allocation data
            allocation_data = {
                'case_id': selected_case_id,
                'investigation_type': investigation_type,
                'assigned_investigator': assigned_investigator,
                'priority_level': priority_level,
                'expected_completion': expected_completion.isoformat(),
                'allocation_notes': allocation_notes,
                'special_instructions': special_instructions,
                'product': product,
                'branch_location': branch_location,
                'region': region,
                'lan': lan,
                'customer_name': customer_name,
                'loan_amount': loan_amount,
                'disbursement_date': disbursement_date.isoformat(),
                'date_of_birth': date_of_birth.isoformat(),
                'pan': pan,
                'mobile_number': mobile_number,
                'email_id': email_id,
                'aadhaar_number': aadhaar_number,
                'relationship_status': relationship_status,
                'complete_address': complete_address,
                'occupation': occupation,
                'monthly_income_range': monthly_income_range,
                'cibil_score': cibil_score,
                'created_by': current_user,
                'created_at': datetime.now().isoformat(),
                'status': 'Allocated'
            }
            
            # Handle file uploads
            uploaded_files = {}
            if gst_business_proof:
                uploaded_files['gst_business_proof'] = save_uploaded_file(gst_business_proof, selected_case_id)
            if pan_card_image:
                uploaded_files['pan_card_image'] = save_uploaded_file(pan_card_image, selected_case_id)
            if aadhaar_card_image:
                uploaded_files['aadhaar_card_image'] = save_uploaded_file(aadhaar_card_image, selected_case_id)
            if customer_photo:
                uploaded_files['customer_photo'] = save_uploaded_file(customer_photo, selected_case_id)
            if supporting_documents:
                doc_paths = [save_uploaded_file(doc, selected_case_id) for doc in supporting_documents]
                uploaded_files['supporting_documents'] = ','.join(doc_paths) if doc_paths else ''
            
            allocation_data.update(uploaded_files)
            
            # Create allocation record
            success = create_case_allocation(allocation_data)
            
            if success:
                st.success(f"✅ Case {selected_case_id} successfully allocated to {assigned_investigator}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to create case allocation. Please try again.")

def show_allocated_cases():
    """Display all allocated cases"""
    allocated_cases = get_case_allocations()
    
    if not allocated_cases:
        st.info("📭 No cases have been allocated yet.")
        return
    
    # Display cases in a structured format
    for i, case in enumerate(allocated_cases):
        with st.expander(f"🎯 {case.get('case_id', 'Unknown')} - {case.get('assigned_investigator', 'Unknown')} - {case.get('priority_level', 'Medium')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Case Details:**")
                st.write(f"**Case ID:** {case.get('case_id', 'N/A')}")
                st.write(f"**Investigation Type:** {case.get('investigation_type', 'N/A')}")
                st.write(f"**Priority:** {case.get('priority_level', 'N/A')}")
                st.write(f"**Expected Completion:** {case.get('expected_completion', 'N/A')}")
            
            with col2:
                st.markdown("**Customer Information:**")
                st.write(f"**Name:** {case.get('customer_name', 'N/A')}")
                st.write(f"**LAN:** {case.get('lan', 'N/A')}")
                st.write(f"**Product:** {case.get('product', 'N/A')}")
                st.write(f"**Loan Amount:** ₹{case.get('loan_amount', 'N/A')}")
            
            with col3:
                st.markdown("**Assignment Details:**")
                st.write(f"**Investigator:** {case.get('assigned_investigator', 'N/A')}")
                st.write(f"**Region:** {case.get('region', 'N/A')}")
                st.write(f"**Branch:** {case.get('branch_location', 'N/A')}")
                st.write(f"**Created By:** {case.get('created_by', 'N/A')}")

def show_allocation_statistics():
    """Display allocation statistics and analytics"""
    allocated_cases = get_case_allocations()
    
    if not allocated_cases:
        st.info("📊 No allocation data available for analytics.")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(allocated_cases)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Allocations", len(df))
    
    with col2:
        high_priority = len(df[df['priority_level'] == 'High']) if 'priority_level' in df.columns else 0
        st.metric("High Priority Cases", high_priority)
    
    with col3:
        unique_investigators = df['assigned_investigator'].nunique() if 'assigned_investigator' in df.columns else 0
        st.metric("Active Investigators", unique_investigators)
    
    with col4:
        avg_loan_amount = df['loan_amount'].mean() if 'loan_amount' in df.columns else 0
        st.metric("Avg Loan Amount", f"₹{avg_loan_amount:,.0f}")
    
    # Charts
    if 'priority_level' in df.columns:
        st.markdown("#### Priority Level Distribution")
        priority_counts = df['priority_level'].value_counts()
        st.bar_chart(priority_counts)
    
    if 'assigned_investigator' in df.columns:
        st.markdown("#### Cases by Investigator")
        investigator_counts = df['assigned_investigator'].value_counts()
        st.bar_chart(investigator_counts)