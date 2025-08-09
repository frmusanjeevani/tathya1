import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from database import get_db_connection

def analyze_case_complexity(case_details):
    """
    One-click case complexity analyzer with comprehensive risk assessment
    Returns complexity score, risk level, and detailed analysis
    """
    
    # Initialize complexity score
    complexity_score = 0
    risk_factors = []
    recommendations = []
    
    # Helper function to safely get values
    def safe_get(key, default='N/A'):
        try:
            if hasattr(case_details, 'get'):
                return case_details.get(key, default)
            else:
                return getattr(case_details, key, default)
        except:
            return default
    
    # 1. LOAN AMOUNT ANALYSIS (Weight: 25%)
    loan_amount = safe_get('loan_amount', '0')
    try:
        loan_amount = float(loan_amount) if loan_amount else 0
    except:
        loan_amount = 0
    
    if loan_amount >= 1000000:  # 10L+
        complexity_score += 25
        risk_factors.append("High Value Loan (₹10L+)")
        recommendations.append("Assign senior investigator with financial fraud expertise")
    elif loan_amount >= 500000:  # 5L+
        complexity_score += 15
        risk_factors.append("Medium Value Loan (₹5L+)")
        recommendations.append("Standard investigation with financial verification")
    elif loan_amount >= 100000:  # 1L+
        complexity_score += 8
        risk_factors.append("Standard Value Loan")
    
    # 2. CASE TYPE ANALYSIS (Weight: 20%)
    case_type = safe_get('case_type', '').lower()
    if 'financial fraud' in case_type or 'embezzlement' in case_type:
        complexity_score += 20
        risk_factors.append("Financial Fraud Case")
        recommendations.append("Require forensic accounting analysis")
    elif 'identity theft' in case_type or 'document fraud' in case_type:
        complexity_score += 15
        risk_factors.append("Identity/Document Fraud")
        recommendations.append("Verify all identity documents and credentials")
    elif 'money laundering' in case_type:
        complexity_score += 18
        risk_factors.append("Money Laundering Suspected")
        recommendations.append("Track transaction patterns and source of funds")
    elif 'default' in case_type:
        complexity_score += 10
        risk_factors.append("Payment Default Case")
    
    # 3. CUSTOMER PROFILE ANALYSIS (Weight: 15%)
    customer_name = safe_get('customer_name', '')
    customer_pan = safe_get('customer_pan', '')
    customer_mobile = safe_get('customer_mobile', '')
    customer_email = safe_get('customer_email', '')
    
    # Check for incomplete customer information
    missing_info = 0
    if not customer_name or customer_name == 'N/A':
        missing_info += 1
    if not customer_pan or customer_pan == 'N/A':
        missing_info += 1
    if not customer_mobile or customer_mobile == 'N/A':
        missing_info += 1
    if not customer_email or customer_email == 'N/A':
        missing_info += 1
    
    if missing_info >= 3:
        complexity_score += 15
        risk_factors.append("Incomplete Customer Information")
        recommendations.append("Conduct comprehensive customer verification")
    elif missing_info >= 2:
        complexity_score += 10
        risk_factors.append("Limited Customer Information")
    
    # 4. TEMPORAL ANALYSIS (Weight: 15%)
    case_date = safe_get('case_date')
    disbursement_date = safe_get('disbursement_date')
    
    case_datetime = None
    disbursement_datetime = None
    
    try:
        if case_date and case_date != 'N/A':
            if isinstance(case_date, str):
                case_datetime = datetime.strptime(case_date, '%Y-%m-%d %H:%M:%S')
            else:
                case_datetime = case_date
            
            if case_datetime:
                days_since_case = (datetime.now() - case_datetime).days
                
                if days_since_case > 30:
                    complexity_score += 12
                    risk_factors.append("Aged Case (30+ days)")
                    recommendations.append("Expedite investigation due to case age")
                elif days_since_case > 14:
                    complexity_score += 8
                    risk_factors.append("Moderately Aged Case (14+ days)")
        
        # Check disbursement to case time gap
        if disbursement_date and disbursement_date != 'N/A' and case_date and case_date != 'N/A' and case_datetime:
            if isinstance(disbursement_date, str):
                disbursement_datetime = datetime.strptime(disbursement_date, '%Y-%m-%d')
            else:
                disbursement_datetime = disbursement_date
            
            if disbursement_datetime:
                gap_days = (case_datetime - disbursement_datetime).days
                
                if gap_days <= 7:
                    complexity_score += 10
                    risk_factors.append("Quick Default (Within 7 days)")
                    recommendations.append("Investigate possible fraudulent intent")
                elif gap_days <= 30:
                    complexity_score += 6
                    risk_factors.append("Early Default (Within 30 days)")
    except:
        pass
    
    # 5. GEOGRAPHIC AND PRODUCT ANALYSIS (Weight: 10%)
    region = safe_get('region', '')
    product = safe_get('product', '')
    branch_location = safe_get('branch_location', '')
    
    # High-risk regions (example criteria)
    high_risk_regions = ['tier 3', 'rural', 'remote']
    if any(risk_region in region.lower() for risk_region in high_risk_regions):
        complexity_score += 8
        risk_factors.append("High-Risk Geographic Location")
        recommendations.append("Conduct field verification")
    
    # Complex products
    complex_products = ['business loan', 'commercial', 'unsecured', 'credit card']
    if any(complex_prod in product.lower() for complex_prod in complex_products):
        complexity_score += 6
        risk_factors.append("Complex Financial Product")
    
    # 6. CASE DESCRIPTION ANALYSIS (Weight: 10%)
    case_description = safe_get('case_description', '')
    
    # Keyword analysis for complexity indicators
    high_complexity_keywords = ['multiple', 'suspicious', 'fraudulent', 'forged', 'fake', 'criminal', 'conspiracy']
    medium_complexity_keywords = ['disputed', 'unclear', 'investigation required', 'verification needed']
    
    description_lower = case_description.lower()
    high_keywords_found = sum(1 for keyword in high_complexity_keywords if keyword in description_lower)
    medium_keywords_found = sum(1 for keyword in medium_complexity_keywords if keyword in description_lower)
    
    if high_keywords_found >= 2:
        complexity_score += 10
        risk_factors.append("Multiple High-Risk Indicators in Description")
        recommendations.append("Assign experienced fraud investigator")
    elif high_keywords_found >= 1:
        complexity_score += 6
        risk_factors.append("High-Risk Keywords in Description")
    elif medium_keywords_found >= 2:
        complexity_score += 4
        risk_factors.append("Multiple Investigation Flags in Description")
    
    # 7. HISTORICAL CASE ANALYSIS (Weight: 5%)
    # Check for similar cases from same customer or region
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check for multiple cases from same customer
            cursor.execute("SELECT COUNT(*) FROM cases WHERE customer_pan = ? OR customer_mobile = ?", 
                         (customer_pan, customer_mobile))
            similar_cases = cursor.fetchone()[0]
            
            if similar_cases > 1:
                complexity_score += 5
                risk_factors.append(f"Multiple Cases from Same Customer ({similar_cases} cases)")
                recommendations.append("Review customer's complete case history")
    except:
        pass
    
    # Determine risk level based on complexity score
    if complexity_score >= 70:
        risk_level = "CRITICAL"
        risk_color = "#dc3545"  # Red
    elif complexity_score >= 50:
        risk_level = "HIGH"
        risk_color = "#fd7e14"  # Orange
    elif complexity_score >= 30:
        risk_level = "MEDIUM"
        risk_color = "#ffc107"  # Yellow
    elif complexity_score >= 15:
        risk_level = "LOW"
        risk_color = "#28a745"  # Green
    else:
        risk_level = "MINIMAL"
        risk_color = "#6c757d"  # Gray
    
    # Generate priority recommendations based on risk level
    if risk_level == "CRITICAL":
        recommendations.insert(0, "URGENT: Escalate to senior management immediately")
        recommendations.append("Consider legal consultation")
        recommendations.append("Implement enhanced monitoring")
    elif risk_level == "HIGH":
        recommendations.insert(0, "High priority investigation required")
        recommendations.append("Weekly progress review")
    elif risk_level == "MEDIUM":
        recommendations.insert(0, "Standard investigation with regular monitoring")
    
    return {
        'complexity_score': min(complexity_score, 100),  # Cap at 100
        'risk_level': risk_level,
        'risk_color': risk_color,
        'risk_factors': risk_factors,
        'recommendations': recommendations,
        'loan_amount': loan_amount,
        'case_type': case_type,
        'analysis_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def create_complexity_visualization(analysis_result):
    """Create visual risk indicators and charts"""
    
    # 1. Risk Level Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = analysis_result['complexity_score'],
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Case Complexity Score"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': analysis_result['risk_color']},
            'steps': [
                {'range': [0, 15], 'color': "#e9ecef"},
                {'range': [15, 30], 'color': "#d4edda"},
                {'range': [30, 50], 'color': "#fff3cd"},
                {'range': [50, 70], 'color': "#f8d7da"},
                {'range': [70, 100], 'color': "#f5c6cb"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=300,
        font={'color': "darkblue", 'family': "Arial"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    # 2. Risk Factors Bar Chart
    if analysis_result['risk_factors']:
        fig_factors = px.bar(
            x=list(range(len(analysis_result['risk_factors']))),
            y=[1] * len(analysis_result['risk_factors']),
            color=[analysis_result['risk_level']] * len(analysis_result['risk_factors']),
            title="Identified Risk Factors",
            labels={'x': 'Risk Factor', 'y': 'Presence'},
            color_discrete_map={
                'CRITICAL': '#dc3545',
                'HIGH': '#fd7e14', 
                'MEDIUM': '#ffc107',
                'LOW': '#28a745',
                'MINIMAL': '#6c757d'
            }
        )
        
        fig_factors.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(len(analysis_result['risk_factors']))),
                ticktext=[factor[:30] + "..." if len(factor) > 30 else factor 
                         for factor in analysis_result['risk_factors']]
            ),
            height=400,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
    else:
        fig_factors = None
    
    return fig_gauge, fig_factors

def show_complexity_analyzer_widget(case_details, case_id):
    """Display one-click complexity analyzer widget"""
    
    # Add the analyzer button
    if st.button(f"🔬 Analyze Case Complexity", key=f"complexity_analyzer_{case_id}", 
                help="One-click comprehensive case complexity and risk analysis"):
        
        # Perform analysis
        with st.spinner("Analyzing case complexity..."):
            analysis_result = analyze_case_complexity(case_details)
            # Store in session state for later use
            st.session_state[f"risk_analysis_{case_id}"] = analysis_result
        
        # Display results in an expander
        with st.expander("📊 Case Complexity Analysis Results", expanded=True):
            
            # Risk Level Banner
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {analysis_result['risk_color']}20 0%, {analysis_result['risk_color']}10 100%); 
                        border: 2px solid {analysis_result['risk_color']}; 
                        border-radius: 10px; padding: 15px; margin: 10px 0; text-align: center;">
                <h2 style="color: {analysis_result['risk_color']}; margin: 0;">
                    🚨 RISK LEVEL: {analysis_result['risk_level']}
                </h2>
                <h3 style="color: {analysis_result['risk_color']}; margin: 5px 0;">
                    Complexity Score: {analysis_result['complexity_score']}/100
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Create visualizations
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Risk gauge
                fig_gauge, fig_factors = create_complexity_visualization(analysis_result)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                # Risk factors chart
                if fig_factors:
                    st.plotly_chart(fig_factors, use_container_width=True)
                else:
                    st.info("No specific risk factors identified")
            
            # Risk Factors Details
            if analysis_result['risk_factors']:
                st.markdown("### 🔍 Identified Risk Factors")
                for i, factor in enumerate(analysis_result['risk_factors'], 1):
                    st.markdown(f"""
                    <div style="background: #f8f9fa; border-left: 4px solid {analysis_result['risk_color']}; 
                                padding: 10px; margin: 5px 0; border-radius: 5px;">
                        <strong>{i}.</strong> {factor}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Recommendations
            if analysis_result['recommendations']:
                st.markdown("### 💡 Investigation Recommendations")
                for i, rec in enumerate(analysis_result['recommendations'], 1):
                    priority_color = "#dc3545" if i == 1 and analysis_result['risk_level'] in ['CRITICAL', 'HIGH'] else "#0066cc"
                    st.markdown(f"""
                    <div style="background: #e3f2fd; border-left: 4px solid {priority_color}; 
                                padding: 10px; margin: 5px 0; border-radius: 5px;">
                        <strong>{i}.</strong> {rec}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Analysis Summary
            st.markdown("### 📋 Analysis Summary")
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.metric("Complexity Score", f"{analysis_result['complexity_score']}/100")
            
            with summary_col2:
                st.metric("Risk Factors", len(analysis_result['risk_factors']))
            
            with summary_col3:
                st.metric("Recommendations", len(analysis_result['recommendations']))
            
            # Analysis timestamp
            st.caption(f"Analysis completed on: {analysis_result['analysis_timestamp']}")
            
            # Export option
            if st.button("📄 Export Analysis Report", key=f"export_analysis_{case_id}"):
                export_analysis_report(analysis_result, case_details, case_id)

def export_analysis_report(analysis_result, case_details, case_id):
    """Export complexity analysis to downloadable report"""
    
    # Helper function to safely get values
    def safe_get(key, default='N/A'):
        try:
            if hasattr(case_details, 'get'):
                return case_details.get(key, default)
            else:
                return getattr(case_details, key, default)
        except:
            return default
    
    report_content = f"""
# CASE COMPLEXITY ANALYSIS REPORT
**Case ID:** {case_id}
**Analysis Date:** {analysis_result['analysis_timestamp']}

## RISK ASSESSMENT
- **Risk Level:** {analysis_result['risk_level']}
- **Complexity Score:** {analysis_result['complexity_score']}/100

## CASE DETAILS
- **Customer Name:** {safe_get('customer_name')}
- **Loan Amount:** ₹{analysis_result['loan_amount']:,.2f}
- **Case Type:** {safe_get('case_type')}
- **Product:** {safe_get('product')}
- **Region:** {safe_get('region')}

## IDENTIFIED RISK FACTORS
"""
    
    for i, factor in enumerate(analysis_result['risk_factors'], 1):
        report_content += f"{i}. {factor}\n"
    
    report_content += "\n## INVESTIGATION RECOMMENDATIONS\n"
    
    for i, rec in enumerate(analysis_result['recommendations'], 1):
        report_content += f"{i}. {rec}\n"
    
    report_content += f"""
## ANALYSIS METHODOLOGY
This analysis considers multiple factors including:
- Loan amount and financial exposure
- Case type and fraud indicators
- Customer profile completeness
- Temporal patterns and timing
- Geographic and product risk factors
- Case description keywords
- Historical case patterns

**Generated by Tathya Case Management System**
"""
    
    # Create download button
    st.download_button(
        label="📥 Download Analysis Report",
        data=report_content,
        file_name=f"case_complexity_analysis_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown",
        key=f"download_analysis_{case_id}"
    )
    
    st.success("Analysis report ready for download!")