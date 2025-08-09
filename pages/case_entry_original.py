import streamlit as st
import uuid
import os
from datetime import datetime
from models import create_simplified_case
from utils import validate_case_data, save_uploaded_file, generate_case_id
from auth import get_current_user, require_role

def query_gemini(prompt, max_tokens=1000):
    """Query Gemini API for intelligent responses"""
    try:
        # Initialize Gemini client if not already done
        if not hasattr(st.session_state, 'gemini_client'):
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                st.session_state.gemini_client = genai.Client(api_key=api_key)
            else:
                raise Exception("GEMINI_API_KEY not found in environment")
        
        client = st.session_state.gemini_client
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.3
            )
        )
        
        if response and response.text:
            return response.text
        else:
            return "Unable to generate response - empty response received"
            
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return f"Error generating response: {str(e)}"

def show():
    """Display case entry page"""
    # Check role access - Investigators and Initiators can create cases
    from auth import require_role
    require_role(["Initiator", "Investigator", "Admin"])
    
    # Add centered header with AI styling
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
        '>NEW CASE REGISTRATION</h2>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    options = get_dropdown_options()
    
    # Clean form styling without boxes
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
    .stNumberInput > div > div > input {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Enter New Case Details header
    st.markdown("### Enter New Case Details")
    
    # Auto-generate Case ID in format CASE20250728CE806A
    if "auto_case_id" not in st.session_state:
        st.session_state.auto_case_id = generate_case_id()

    # Start the form container
    with st.form("case_entry_main_form", clear_on_submit=False):
        case_id = st.text_input("Case ID", value=st.session_state.auto_case_id, disabled=True, help="Auto-generated unique case ID in format: CASE20250728CE806A")
        
        # Filter Fields Row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.selectbox(
                "Category *",
                ["Select Category...", "Lending", "Non-Lending"],
                help="Select the case category"
            )
        
        with col2:
            referred_by_options = [
                "Select Referred By...",
                "Branch Manager",
                "Sales Manager", 
                "Risk Team",
                "Legal Team",
                "Customer Service",
                "Whistleblower",
                "Third-Party Agency",
                "Internal Audit",
                "Automated Flag",
                "Customer Direct"
            ]
            referred_by = st.selectbox(
                "Referred By *",
                referred_by_options,
                help="Who referred this case"
            )
        
        with col3:
            type_of_case_options = [
                "Select Type of Case...",
                "Fraud Suspect",
                "Customer Complaint",
                "Whistleblower Input",
                "Internal Escalation",
                "Legal Referral",
                "Negative Verification",
                "High-Risk Profile",
                "Discrepant Documents",
                "Suspicious Activity Report (SAR)",
                "Repeat Offender / Pattern Match",
                "Misuse of Credentials",
                "Identity Mismatch",
                "Document Tampering",
                "Branch Escalation",
                "Third-Party Alert (External)",
                "Social Media Flagged Case",
                "Call Center Escalation",
                "Field Investigation Required",
                "Deviation Approval Request",
                "Others (Please Specify)"
            ]
            case_type = st.selectbox(
                "Type of Case *",
                type_of_case_options,
                help="Select the type of case"
            )
        
        st.markdown("---")
        st.subheader("📝 Customer Details")
        
        # Customer Demographics Section
        st.subheader("👤 Customer Demographics & Profile")
        
        # Basic Information
        col1, col2, col3 = st.columns(3)
        with col1:
            customer_name = st.text_input("Customer Name *", placeholder="Enter full customer name")
        with col2:
            customer_dob = st.date_input("Date of Birth *", max_value=datetime.today())
        with col3:
            customer_pan = st.text_input("PAN *", placeholder="ABCDE1234F", max_chars=10, help="10-character alphanumeric PAN")
        
        # Contact Information
        col1, col2 = st.columns(2)
        with col1:
            customer_mobile = st.text_input("Mobile Number *", placeholder="9876543210", max_chars=10, help="10-digit mobile number")
        with col2:
            customer_email = st.text_input("Email ID *", placeholder="customer@email.com")
        
        # Identity Information  
        col1, col2 = st.columns(2)
        with col1:
            customer_aadhaar = st.text_input("Aadhaar Number (Auto-masked)", 
                placeholder="123456789012", 
                max_chars=12, 
                help="12-digit Aadhaar number (will be automatically masked for privacy)",
                key="aadhaar_input")
            
            # Display masked version if Aadhaar is entered
            if customer_aadhaar and len(customer_aadhaar) >= 8:
                masked_aadhaar = "XXXX-XXXX-" + customer_aadhaar[-4:]
                st.text(f"Masked Display: {masked_aadhaar}")
            
        with col2:
            customer_relationship_status = st.selectbox("Relationship Status", 
                ["Single", "Married", "Divorced", "Widowed", "Separated"], 
                help="Customer's marital status")
        
        # Address Information
        customer_address_full = st.text_area("Complete Address", 
            placeholder="Enter complete address with pin code", 
            height=80,
            help="Full address including street, city, state, and pin code")
        
        # Financial Profile
        st.markdown("**💰 Financial Profile**")
        col1, col2, col3 = st.columns(3)
        with col1:
            customer_occupation = st.selectbox("Occupation", [
                "Salaried Employee", "Self Employed Business", "Self Employed Professional", 
                "Student", "Retired", "Housewife", "Unemployed", "Others"
            ], help="Customer's primary occupation")
        with col2:
            customer_income = st.selectbox("Monthly Income Range", [
                "Below ₹25,000", "₹25,000 - ₹50,000", "₹50,000 - ₹1,00,000", 
                "₹1,00,000 - ₹2,00,000", "₹2,00,000 - ₹5,00,000", "Above ₹5,00,000"
            ], help="Customer's monthly income bracket")
        with col3:
            customer_cibil_score = st.number_input("CIBIL Score", min_value=300, max_value=900, value=750, help="Customer's credit score (300-900)")
        
        # Loan Information
        st.markdown("**🏦 Loan Information**")
        col1, col2, col3 = st.columns(3)
        with col1:
            branch_location = st.text_input("Branch / Location *", placeholder="Enter branch name")
        with col2:
            loan_amount = st.number_input("Loan Amount *", min_value=0.0, step=1000.0, format="%.2f", help="Principal loan amount")
        with col3:
            disbursement_date = st.date_input("Disbursement Date *", max_value=datetime.today(), help="Date when loan was disbursed")
        
        # Case Details Section
        st.subheader("📋 Case Details")
        
        col1, col2 = st.columns(2)
        with col1:
            lan = st.text_input("LAN *", placeholder="Enter LAN number")
        with col2:
            product = st.selectbox("Product *", options["products"])
        
        col1, col2 = st.columns(2)
        with col1:
            region = st.selectbox("Region *", options["regions"])
        with col2:
            case_date = st.date_input("Case Date *", datetime.today())
        
        # Case description
        st.subheader("📝 Case Description")
        
        case_description = st.text_area(
            "Case Description *",
            placeholder="Provide detailed description of the case",
            height=120,
            key="case_description_input"
        )
        
        # AI Enhancement instruction
        st.info("💡 Tip: After filling the description, use the AI Assistant page to enhance it professionally.")
        
        st.markdown("---")
        # Document Upload Section
        st.subheader("Document upload")
        
        # Initialize variables
        pan_image = None
        aadhaar_image = None
        customer_photo = None
        bulk_identity_docs = None
        
        # Radio button for upload method
        upload_method = st.radio(
            "Choose upload method:",
            ["Single upload", "Upload all at once"],
            key="upload_method_radio",
            horizontal=True
        )
        
        if upload_method == "Upload all at once":
            # Bulk upload option
            bulk_identity_docs = st.file_uploader(
                "Upload All Identity Documents at Once",
                accept_multiple_files=True,
                type=['jpg', 'jpeg', 'png', 'pdf'],
                key="bulk_identity_upload",
                help="Select multiple identity documents (PAN, Aadhaar, Customer Photo) and upload them all at once"
            )
            
            if bulk_identity_docs:
                st.success(f"✅ {len(bulk_identity_docs)} identity document(s) uploaded")
                with st.expander("📄 Preview Documents"):
                    for i, doc in enumerate(bulk_identity_docs, 1):
                        col_preview1, col_preview2 = st.columns([1, 3])
                        with col_preview1:
                            if doc.type.startswith('image/'):
                                st.image(doc, caption=f"Doc {i}: {doc.name}", width=120)
                            else:
                                st.info(f"📄 {doc.name}")
                        with col_preview2:
                            st.markdown(f"**{i}. {doc.name}**")
                            st.markdown(f"Type: {doc.type} | Size: {doc.size} bytes")
                        if i < len(bulk_identity_docs):
                            st.markdown("---")
        else:
            bulk_identity_docs = None
        
        if upload_method == "Single upload":
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🆔 PAN Card Image**")
                pan_image = st.file_uploader(
                    "Upload PAN Card Image",
                    type=['jpg', 'jpeg', 'png', 'pdf'],
                    key="pan_image_upload",
                    help="Upload clear image of PAN card (front side)"
                )
                if pan_image:
                    if pan_image.type.startswith('image/'):
                        st.image(pan_image, caption="PAN Card Preview", width=200)
                    else:
                        st.success(f"✅ PAN document uploaded: {pan_image.name}")
            
            with col2:
                st.markdown("**🆔 Aadhaar Card Image**")
                aadhaar_image = st.file_uploader(
                    "Upload Aadhaar Card Image", 
                    type=['jpg', 'jpeg', 'png', 'pdf'],
                    key="aadhaar_image_upload",
                    help="Upload clear image of Aadhaar card (front side only - mask last 4 digits)"
                )
                if aadhaar_image:
                    if aadhaar_image.type.startswith('image/'):
                        st.image(aadhaar_image, caption="Aadhaar Card Preview", width=200)
                    else:
                        st.success(f"✅ Aadhaar document uploaded: {aadhaar_image.name}")
            
            with col3:
                st.markdown("**👤 Customer Photo**")
                customer_photo = st.file_uploader(
                    "Upload Customer Photo",
                    type=['jpg', 'jpeg', 'png'],
                    key="customer_photo_upload", 
                    help="Upload recent clear photo of the customer for identity verification"
                )
                if customer_photo:
                    st.image(customer_photo, caption="Customer Photo Preview", width=200)
        else:
            # Set variables to None if not in single upload mode
            pan_image = None
            aadhaar_image = None
            customer_photo = None
        
        # Document verification note
        st.info("📋 **Note:** These identity documents will be used for verification purposes during investigation. Ensure images are clear and readable.")
        
        # Identity Verification Tab (appears after image upload)
        if pan_image and customer_photo:
            st.markdown("---")
            st.subheader("🔍 Identity Verification")
            st.info("Compare uploaded PAN card photo with customer photo using AI verification")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**PAN Card Image**")
                st.image(pan_image, caption="PAN Card", width=250)
            with col2:
                st.markdown("**Customer Photo**")  
                st.image(customer_photo, caption="Customer Photo", width=250)
                
        elif (pan_image and not customer_photo) or (customer_photo and not pan_image):
            st.warning("⚠️ Upload both PAN card image and customer photo to enable identity verification")
        
        st.markdown("---")
        
        # Supporting Documents Section
        st.subheader("Supporting Documents")
        
        bulk_supporting_docs = st.file_uploader(
            "Upload All Supporting Documents at Once",
            accept_multiple_files=True,
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
            key="bulk_supporting_upload",
            help="Select all your supporting documents and upload them together"
        )
        
        if bulk_supporting_docs:
            st.success(f"✅ {len(bulk_supporting_docs)} supporting document(s) uploaded")
            with st.expander("📄 Preview Supporting Documents"):
                for i, doc in enumerate(bulk_supporting_docs, 1):
                    col_preview1, col_preview2 = st.columns([1, 3])
                    with col_preview1:
                        if doc.type.startswith('image/'):
                            st.image(doc, caption=f"Doc {i}", width=120)
                        else:
                            st.info(f"📄 {doc.name}")
                    with col_preview2:
                        st.markdown(f"**{i}. {doc.name}**")
                        st.markdown(f"Type: {doc.type} | Size: {doc.size} bytes")
                    if i < len(bulk_supporting_docs):
                        st.markdown("---")
        
        # Organized document sections in columns like Identity Documents
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🏢 Business Documents**")
            business_docs = st.file_uploader(
                "Upload Business Documents",
                accept_multiple_files=False,
                type=['pdf', 'doc', 'docx', 'xls', 'xlsx'],
                key="business_docs", 
                help="Business registration, GST, trade license documents"
            )
            if business_docs:
                st.success(f"✅ Business document uploaded")
                # Show document thumbnail/preview
                with st.expander("📄 Preview Business Document"):
                    st.markdown(f"**File:** {business_docs.name}")
                    st.markdown(f"**Type:** {business_docs.type}")
                    st.markdown(f"**Size:** {business_docs.size} bytes")
                    if business_docs.type.startswith('image/'):
                        st.image(business_docs, width=200, caption="Business Document Preview")
                    else:
                        st.info("📄 Document uploaded successfully (PDF/Doc preview not available)")
        
        with col2:
            st.markdown("**🏠 Property Documents**")
            property_docs = st.file_uploader(
                "Upload Property Documents",
                accept_multiple_files=False,
                type=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'],
                key="property_docs",
                help="Property papers, utility bills, address proof"
            )
            if property_docs:
                st.success(f"✅ Property document uploaded")
                # Show document thumbnail/preview
                with st.expander("📄 Preview Property Document"):
                    st.markdown(f"**File:** {property_docs.name}")
                    st.markdown(f"**Type:** {property_docs.type}")
                    st.markdown(f"**Size:** {property_docs.size} bytes")
                    if property_docs.type.startswith('image/'):
                        st.image(property_docs, width=200, caption="Property Document Preview")
                    else:
                        st.info("📄 Document uploaded successfully (PDF/Doc preview not available)")
        
        with col3:
            st.markdown("**📋 Additional Documents**")
            additional_docs = st.file_uploader(
                "Upload Additional Documents",
                accept_multiple_files=True,
                type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
                key="additional_docs",
                help="Affidavits, legal documents, other relevant files"
            )
            if additional_docs:
                st.success(f"✅ {len(additional_docs)} additional file(s) uploaded")
                # Show document thumbnails/previews
                with st.expander("📄 Preview Additional Documents"):
                    for i, doc in enumerate(additional_docs, 1):
                        st.markdown(f"**{i}. {doc.name}**")
                        st.markdown(f"Type: {doc.type} | Size: {doc.size} bytes")
                        if doc.type.startswith('image/'):
                            st.image(doc, width=200, caption=f"Document {i} Preview")
                        else:
                            st.info(f"📄 Document {i} uploaded successfully (PDF/Doc preview not available)")
                        if i < len(additional_docs):
                            st.markdown("---")
            
            # Combine all uploaded files for processing (including bulk uploads)
            uploaded_files = []
            
            # Add individual uploads
            if business_docs:
                uploaded_files.append(business_docs)
            if property_docs:
                uploaded_files.append(property_docs)
            if additional_docs:
                uploaded_files.extend(additional_docs)
            
            # Add bulk uploads
            if bulk_identity_docs:
                uploaded_files.extend(bulk_identity_docs)
            if bulk_supporting_docs:
                uploaded_files.extend(bulk_supporting_docs)
            
            # Document summary and guidance
            if uploaded_files:
                with st.expander(f"📄 View All Selected Files ({len(uploaded_files)} total)"):
                    # Count documents by source
                    individual_count = 0
                    bulk_identity_count = len(bulk_identity_docs) if bulk_identity_docs else 0
                    bulk_supporting_count = len(bulk_supporting_docs) if bulk_supporting_docs else 0
                    
                    if business_docs: individual_count += 1
                    if property_docs: individual_count += 1
                    if additional_docs: individual_count += len(additional_docs)
                    
                    st.markdown(f"**📊 Upload Summary:**")
                    st.markdown(f"- 📷 Identity Documents (Bulk): {bulk_identity_count}")
                    st.markdown(f"- 📎 Supporting Documents (Bulk): {bulk_supporting_count}")
                    st.markdown(f"- 📋 Individual Uploads: {individual_count}")
                    st.markdown("---")
                    
                    for i, file in enumerate(uploaded_files, 1):
                        # Determine source
                        source_icon = "📋"
                        if bulk_identity_docs and file in bulk_identity_docs:
                            source_icon = "📷"
                        elif bulk_supporting_docs and file in bulk_supporting_docs:
                            source_icon = "📎"
                        
                        st.markdown(f"**{i}.** {source_icon} {file.name} ({file.type}, {file.size} bytes)")
            
            st.info("💡 **Note:** These documents are optional but can provide additional context for case investigation.")
            
            # Upload summary
            if uploaded_files:
                total_files = len(uploaded_files)
                bulk_files = (len(bulk_identity_docs) if bulk_identity_docs else 0) + (len(bulk_supporting_docs) if bulk_supporting_docs else 0)
                individual_files = total_files - bulk_files
                
                st.success(f"📊 **Upload Summary**: {total_files} total files ({bulk_files} via bulk upload, {individual_files} individual)")
            
            # Form submission buttons
            col1, col2 = st.columns(2)
            
            with col1:
                save_draft = st.form_submit_button("💾 Save as Draft", use_container_width=True)
            
            with col2:
                submit_case = st.form_submit_button("📤 Submit Case", use_container_width=True)
            

        # Handle form submission
        if save_draft or submit_case:
            case_data = {
                "case_id": st.session_state.auto_case_id,
                "lan": lan.strip(),
                "customer_name": (customer_name or "").strip(),
                "customer_dob": customer_dob.strftime("%Y-%m-%d"),
                "customer_pan": (customer_pan or "").strip().upper(),
                "customer_aadhaar": (customer_aadhaar or "").strip(),
                "customer_mobile": (customer_mobile or "").strip(),
                "customer_email": (customer_email or "").strip().lower(),
                "customer_address_full": (customer_address_full or "").strip(),
                "customer_occupation": customer_occupation,
                "customer_income": customer_income,
                "customer_cibil_score": customer_cibil_score,
                "customer_relationship_status": customer_relationship_status,
                "branch_location": (branch_location or "").strip(),
                "loan_amount": loan_amount,
                "disbursement_date": disbursement_date.strftime("%Y-%m-%d"),
                "category": category,
                "case_type": case_type,
                "product": product,
                "region": region,
                "referred_by": referred_by,
                "case_description": (case_description or "").strip(),
                "case_date": case_date.strftime("%Y-%m-%d"),
                "status": "Submitted" if submit_case else "Draft"
            }
            
            # Validate data
            errors = validate_case_data(case_data)
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create case
                success, message = create_case(case_data, current_user)
                
                if success:
                    st.success(f"✅ Case {case_data['status'].lower()} successfully!")
                    
                    # Store submitted case data in session state for Case Allocation flow
                    if submit_case:  # Only for submitted cases, not drafts
                        st.session_state.new_case_data = {
                            **case_data,
                            'uploaded_documents': {
                                'pan_image': pan_image,
                                'aadhaar_image': aadhaar_image,
                                'customer_photo': customer_photo,
                                'bulk_identity_docs': bulk_identity_docs,
                                'bulk_supporting_docs': bulk_supporting_docs,
                                'uploaded_files': uploaded_files
                            },
                            'face_verification_result': st.session_state.get('face_verification_result', None),
                            'submission_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'submitted_by': current_user
                        }
                        st.info("📋 **Case data prepared for allocation workflow**")
                    
                    # Handle file uploads
                    total_files_uploaded = 0
                    
                    # Handle supporting documents
                    if uploaded_files:
                        st.info("Uploading supporting documents...")
                        for uploaded_file in uploaded_files:
                            file_success, filename = save_uploaded_file(
                                uploaded_file, case_data["case_id"]
                            )
                            if file_success:
                                total_files_uploaded += 1
                    
                    # Handle identity document images (individual uploads)
                    identity_docs = [
                        (pan_image, "PAN_Card"),
                        (aadhaar_image, "Aadhaar_Card"), 
                        (customer_photo, "Customer_Photo")
                    ]
                    
                    for doc_file, doc_type in identity_docs:
                        if doc_file is not None:
                            # Save identity document with specific naming
                            file_success, filename = save_identity_document(
                                doc_file, case_data["case_id"], doc_type
                            )
                            if file_success:
                                total_files_uploaded += 1
                    
                    if total_files_uploaded > 0:
                        st.success(f"✅ {total_files_uploaded} file(s) uploaded successfully (including identity documents)!")
                    
                    # Generate new case ID for next case
                    st.session_state.auto_case_id = generate_case_id()
                    
                    # Professional success notification
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
                        border: 1px solid #c3e6cb; 
                        border-radius: 8px; 
                        padding: 16px; 
                        margin: 16px 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        animation: slideIn 0.5s ease-out;
                    ">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="
                                background: #155724; 
                                color: white; 
                                border-radius: 50%; 
                                width: 24px; 
                                height: 24px; 
                                display: flex; 
                                align-items: center; 
                                justify-content: center; 
                                font-weight: bold;
                            ">✓</div>
                            <div>
                                <h4 style="margin: 0; color: #155724; font-size: 16px;">Case Submitted Successfully</h4>
                                <p style="margin: 4px 0 0 0; color: #155724; font-size: 14px;">
                                    Case ID: <strong>{}</strong> has been processed and is now under review.
                                </p>
                            </div>
                        </div>
                    </div>
                    <style>
                    @keyframes slideIn {{
                        from {{ opacity: 0; transform: translateY(-10px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
                    }}
                    </style>
                    """.format(case_data["case_id"]), unsafe_allow_html=True)
                    
                else:
                    st.error(f"❌ {message}")
        
        # Handle verification results from form submission (displayed in separate section)
        if st.session_state.get('run_verification', False) and 'verification_images' in st.session_state:
            st.markdown("---")
            st.subheader("🔍 Identity Verification Results")
            
            with st.spinner("Processing identity verification..."):
                try:
                    from face_verification_api import verify_face_match
                    
                    verification_data = st.session_state.verification_images
                    
                    verification_result = verify_face_match(
                        image1_bytes=verification_data['pan_image'],
                        image2_bytes=verification_data['customer_photo'],
                        provider=verification_data['api_provider']
                    )
                    
                    if verification_result['success']:
                        # Display verification results in organized layout
                        st.markdown("#### Verification Analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                label="Match Percentage", 
                                value=f"{verification_result['match_percentage']}%",
                                delta="High Match" if verification_result['match_percentage'] >= 85 else "Medium Match"
                            )
                        
                        with col2:
                            st.metric(
                                label="Confidence Score", 
                                value=f"{verification_result['confidence_score']:.3f}",
                                delta="High Confidence" if verification_result['confidence_score'] >= 0.7 else "Low Confidence"
                            )
                        
                        with col3:
                            status_icon = "✅" if verification_result['verification_status'] == 'VERIFIED' else "⚠️"
                            st.metric(
                                label="Verification Status", 
                                value=f"{status_icon} {verification_result['verification_status']}"
                            )
                        
                        # Professional verification summary
                        if verification_result['verification_status'] == 'VERIFIED':
                            st.success(f"""
                            **✅ Identity Verification: PASSED**
                            - Images show strong facial similarity ({verification_result['match_percentage']}% match)
                            - High confidence verification ({verification_result['confidence_score']:.3f} score)
                            - Verified using {verification_result['provider']}
                            - **You can now safely submit the case form**
                            """)
                        else:
                            st.warning(f"""
                            **⚠️ Identity Verification: REQUIRES REVIEW**
                            - Limited facial similarity detected ({verification_result['match_percentage']}% match)
                            - Confidence score: {verification_result['confidence_score']:.3f}
                            - **Consider reviewing images before case submission**
                            - Manual verification may be required during investigation
                            """)
                        
                        # Additional face details if available
                        if 'face_details' in verification_result:
                            with st.expander("📊 Detailed Face Analysis"):
                                face_details = verification_result['face_details']
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("PAN Image Face Confidence", f"{face_details.get('face1_confidence', 0):.3f}")
                                with col2:
                                    st.metric("Customer Photo Face Confidence", f"{face_details.get('face2_confidence', 0):.3f}")
                                
                                if face_details.get('landmarks_detected', False):
                                    st.info("✅ Face landmarks detected in both images")
                                else:
                                    st.warning("⚠️ Limited face landmarks detected")
                        
                        # Store verification result in session
                        st.session_state.face_verification_result = verification_result
                        
                    else:
                        st.error("❌ **Verification Failed**")
                        st.error(f"Error: {verification_result['error']}")
                        
                        if "API key" in verification_result['error'] or "credentials" in verification_result['error']:
                            st.info("💡 The selected API provider is not configured. Try Google Vision API or contact your administrator for API setup.")
                
                except Exception as e:
                    st.error(f"❌ Verification error: {str(e)}")
                    st.info("💡 Try using the Face Verification Test module for detailed testing, or contact support if the issue persists.")
            
            # Clear verification flag
            st.session_state.run_verification = False
        

        
        st.markdown('</div>', unsafe_allow_html=True)  # Close animated-form div
    
    # Display help information
    with st.expander("ℹ️ Help & Guidelines"):
        st.markdown("""
        ### Case Entry Guidelines:
        
        **Required Fields (marked with *):**
        - Case ID: Must be unique across the system
        - LAN: Loan Account Number
        - Case Description: Detailed explanation of the case
        
        **File Upload:**
        - Supported formats: PDF, DOC, DOCX, XLS, XLSX, JPG, JPEG, PNG
        - Maximum file size: 10MB per file
        - Multiple files can be uploaded
        
        **Status Options:**
        - **Draft**: Save case for later completion
        - **Submitted**: Submit case for review process
        
        **Important Notes:**
        - Case ID cannot be changed after creation
        - All uploaded files are securely stored
        - Audit trail is maintained for all actions
        """)