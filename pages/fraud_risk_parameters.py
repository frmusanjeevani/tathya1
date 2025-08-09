import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from auth import require_role

def show():
    """Display Refined Fraud Risk Parameters by Scope page"""
    # Check role access
    require_role(["Admin", "Legal Reviewer", "Approver", "Investigator"])
    
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
        '>Refined Fraud Risk Parameters</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Advanced fraud risk assessment and parameter configuration by scope</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add professional styling
    st.markdown("""
    <style>
    .risk-card {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .risk-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
        border-color: #4285f4;
    }
    .parameter-section {
        background: #ffffff;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid #4285f4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .risk-level-high {
        border-left-color: #ea4335;
        background: linear-gradient(135deg, #fff5f5 0%, #ffeaea 100%);
    }
    .risk-level-medium {
        border-left-color: #fbbc04;
        background: linear-gradient(135deg, #fffcf0 0%, #fff8e1 100%);
    }
    .risk-level-low {
        border-left-color: #34a853;
        background: linear-gradient(135deg, #f0fff4 0%, #e8f5e8 100%);
    }
    .metric-container {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1a73e8;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Scope Selection
    st.markdown("## 🎯 Risk Assessment Scope")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assessment_scope = st.selectbox(
            "Assessment Scope",
            ["Individual Case", "Portfolio Level", "Regional Analysis", "Product Specific", "Time-based Analysis"],
            help="Select the scope for fraud risk parameter analysis"
        )
    
    with col2:
        risk_category = st.selectbox(
            "Risk Category",
            ["Financial Risk", "Identity Risk", "Behavioral Risk", "Transaction Risk", "Document Risk", "Compliance Risk"],
            help="Choose primary risk category to focus on"
        )
    
    with col3:
        time_period = st.selectbox(
            "Analysis Period",
            ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last 1 Year", "Custom Range"],
            help="Select time period for risk analysis"
        )
    
    # Custom date range if selected
    if time_period == "Custom Range":
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("Start Date", datetime.now().replace(day=1))
        with col_date2:
            end_date = st.date_input("End Date", datetime.now())
    
    st.markdown("---")
    
    # Risk Parameter Configuration
    st.markdown("## ⚙️ Risk Parameter Configuration")
    
    # Create expandable sections for different parameter categories
    with st.expander("💰 Financial Risk Parameters", expanded=True):
        st.markdown('<div class="parameter-section risk-level-high">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            loan_amount_threshold = st.slider("High Risk Loan Amount Threshold (₹)", 100000, 10000000, 5000000, step=100000)
            income_ratio_threshold = st.slider("Income to Loan Ratio Threshold", 0.1, 2.0, 0.3, step=0.1)
            cibil_threshold = st.slider("Minimum CIBIL Score", 300, 900, 650, step=10)
        
        with col2:
            repayment_history_weight = st.slider("Repayment History Weight (%)", 0, 100, 40, step=5)
            collateral_coverage_ratio = st.slider("Collateral Coverage Ratio", 0.5, 3.0, 1.2, step=0.1)
            debt_to_income_ratio = st.slider("Debt-to-Income Ratio Threshold", 0.1, 1.0, 0.6, step=0.05)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("🆔 Identity Risk Parameters"):
        st.markdown('<div class="parameter-section risk-level-medium">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            document_verification_threshold = st.slider("Document Verification Confidence (%)", 50, 100, 85, step=5)
            face_match_threshold = st.slider("Face Match Accuracy (%)", 50, 100, 90, step=5)
            address_verification_score = st.slider("Address Verification Score", 0, 100, 75, step=5)
        
        with col2:
            identity_cross_check_weight = st.slider("Identity Cross-check Weight (%)", 0, 100, 30, step=5)
            duplicate_detection_sensitivity = st.slider("Duplicate Detection Sensitivity", 0.5, 1.0, 0.8, step=0.05)
            kyc_completeness_threshold = st.slider("KYC Completeness Threshold (%)", 60, 100, 90, step=5)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("📊 Behavioral Risk Parameters"):
        st.markdown('<div class="parameter-section risk-level-medium">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            transaction_pattern_anomaly = st.slider("Transaction Pattern Anomaly Score", 0, 100, 70, step=5)
            frequency_analysis_weight = st.slider("Transaction Frequency Weight (%)", 0, 100, 25, step=5)
            geographical_risk_factor = st.slider("Geographical Risk Factor", 0.0, 2.0, 1.0, step=0.1)
        
        with col2:
            time_based_pattern_weight = st.slider("Time-based Pattern Weight (%)", 0, 100, 20, step=5)
            social_network_analysis = st.slider("Social Network Risk Score", 0, 100, 50, step=5)
            communication_pattern_score = st.slider("Communication Pattern Score", 0, 100, 60, step=5)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("📄 Document Risk Parameters"):
        st.markdown('<div class="parameter-section risk-level-low">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            document_authenticity_score = st.slider("Document Authenticity Score", 0, 100, 80, step=5)
            ocr_confidence_threshold = st.slider("OCR Confidence Threshold (%)", 50, 100, 85, step=5)
            metadata_analysis_weight = st.slider("Metadata Analysis Weight (%)", 0, 100, 15, step=5)
        
        with col2:
            forgery_detection_sensitivity = st.slider("Forgery Detection Sensitivity", 0.5, 1.0, 0.85, step=0.05)
            document_consistency_score = st.slider("Document Consistency Score", 0, 100, 75, step=5)
            digital_signature_validation = st.slider("Digital Signature Weight (%)", 0, 100, 35, step=5)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Risk Score Calculation
    st.markdown("## 📈 Risk Score Analysis")
    
    # Calculate composite risk score
    financial_risk = (100 - (loan_amount_threshold/100000)) * 0.3
    identity_risk = (100 - document_verification_threshold) * 0.25
    behavioral_risk = transaction_pattern_anomaly * 0.25
    document_risk = (100 - document_authenticity_score) * 0.20
    
    composite_risk_score = financial_risk + identity_risk + behavioral_risk + document_risk
    composite_risk_score = max(0, min(100, composite_risk_score))  # Normalize to 0-100
    
    # Display risk metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{financial_risk:.1f}</div>
            <div class="metric-label">Financial Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{identity_risk:.1f}</div>
            <div class="metric-label">Identity Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{behavioral_risk:.1f}</div>
            <div class="metric-label">Behavioral Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{document_risk:.1f}</div>
            <div class="metric-label">Document Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Composite Risk Score with color coding
    risk_color = "#ea4335" if composite_risk_score > 70 else "#fbbc04" if composite_risk_score > 40 else "#34a853"
    risk_level = "HIGH" if composite_risk_score > 70 else "MEDIUM" if composite_risk_score > 40 else "LOW"
    
    st.markdown(f"""
    <div style="
        text-align: center;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 2px solid {risk_color};
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <h2 style="color: {risk_color}; margin-bottom: 10px;">Composite Risk Score</h2>
        <div style="font-size: 3rem; font-weight: bold; color: {risk_color}; margin-bottom: 5px;">
            {composite_risk_score:.1f}
        </div>
        <div style="font-size: 1.2rem; color: {risk_color}; font-weight: 600;">
            {risk_level} RISK
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk Distribution Chart
    st.markdown("### 📊 Risk Distribution Analysis")
    
    # Create a donut chart for risk distribution
    risk_data = {
        'Risk Category': ['Financial Risk', 'Identity Risk', 'Behavioral Risk', 'Document Risk'],
        'Risk Score': [financial_risk, identity_risk, behavioral_risk, document_risk],
        'Weight': ['30%', '25%', '25%', '20%']
    }
    
    fig = px.pie(
        values=risk_data['Risk Score'],
        names=risk_data['Risk Category'],
        title="Risk Score Distribution by Category",
        color_discrete_sequence=['#ea4335', '#fbbc04', '#4285f4', '#34a853'],
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Risk Score: %{value:.1f}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        height=400,
        title_x=0.5,
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Parameter Impact Analysis
    st.markdown("### 🎯 Parameter Impact Analysis")
    
    # Create impact analysis table
    impact_data = pd.DataFrame({
        'Parameter': [
            'Loan Amount Threshold', 'Document Verification', 'Transaction Pattern',
            'Document Authenticity', 'CIBIL Score', 'Face Match Accuracy'
        ],
        'Current Value': [
            f"₹{loan_amount_threshold:,}", f"{document_verification_threshold}%", 
            f"{transaction_pattern_anomaly}", f"{document_authenticity_score}%",
            f"{cibil_threshold}", f"{face_match_threshold}%"
        ],
        'Risk Impact': ['High', 'High', 'Medium', 'Medium', 'High', 'Medium'],
        'Weight': ['30%', '25%', '25%', '20%', '15%', '10%'],
        'Recommendation': [
            'Consider lowering threshold', 'Maintain current level', 'Increase sensitivity',
            'Maintain current level', 'Consider raising minimum', 'Increase threshold'
        ]
    })
    
    st.dataframe(
        impact_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Parameter': st.column_config.TextColumn('Parameter', width=200),
            'Current Value': st.column_config.TextColumn('Current Value', width=150),
            'Risk Impact': st.column_config.TextColumn('Risk Impact', width=100),
            'Weight': st.column_config.TextColumn('Weight', width=80),
            'Recommendation': st.column_config.TextColumn('Recommendation', width=200)
        }
    )
    
    # Configuration Actions
    st.markdown("---")
    st.markdown("## 💾 Configuration Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("✅ Risk parameters configuration saved successfully!")
            st.info("Configuration saved for scope: " + assessment_scope)
    
    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.warning("⚠️ Configuration reset to default values")
            st.rerun()
    
    with col3:
        if st.button("📋 Export Parameters", use_container_width=True):
            # Create export data
            export_data = {
                'scope': assessment_scope,
                'risk_category': risk_category,
                'time_period': time_period,
                'composite_risk_score': composite_risk_score,
                'parameters': {
                    'financial': {
                        'loan_amount_threshold': loan_amount_threshold,
                        'income_ratio_threshold': income_ratio_threshold,
                        'cibil_threshold': cibil_threshold
                    },
                    'identity': {
                        'document_verification_threshold': document_verification_threshold,
                        'face_match_threshold': face_match_threshold,
                        'address_verification_score': address_verification_score
                    },
                    'behavioral': {
                        'transaction_pattern_anomaly': transaction_pattern_anomaly,
                        'frequency_analysis_weight': frequency_analysis_weight,
                        'geographical_risk_factor': geographical_risk_factor
                    },
                    'document': {
                        'document_authenticity_score': document_authenticity_score,
                        'ocr_confidence_threshold': ocr_confidence_threshold,
                        'metadata_analysis_weight': metadata_analysis_weight
                    }
                }
            }
            
            st.success("✅ Parameters exported successfully!")
            st.json(export_data)
    
    # Additional Information
    st.markdown("---")
    st.info("""
    **💡 Parameter Configuration Guidelines:**
    - **High Risk Thresholds**: Set stricter values for critical parameters
    - **Medium Risk Balance**: Maintain moderate sensitivity for operational efficiency
    - **Low Risk Optimization**: Focus on automation and processing speed
    - **Regular Review**: Update parameters based on fraud trends and business requirements
    """)

if __name__ == "__main__":
    show()