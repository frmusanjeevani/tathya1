import streamlit as st
import pandas as pd
from datetime import datetime
from auth import require_role, get_current_user
from models import get_cases_by_status
from utils import format_datetime
import plotly.express as px
import plotly.graph_objects as go

@require_role(["Admin", "Initiator", "Reviewer", "Approver", "Legal Reviewer", "Actioner", "Investigator"])
def show():
    """Dashboard showing workflow-specific case management overview"""
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
        '>DASHBOARD WORKFLOW</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Complete overview of case management workflow**")
    
    current_user = get_current_user()
    user_role = st.session_state.get("role", "")
    
    # Add enhanced CSS for modern dashboard styling
    st.markdown("""
    <style>
    .workflow-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .workflow-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #0066cc;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #0066cc;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .workflow-sequence {
        background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Workflow sequence display
    st.markdown("""
    <div class="workflow-sequence">
        🔄 <strong>Complete Workflow Sequence:</strong><br>
        Case Entry → Allocator → Investigator → Primary Reviewer → Approver 1 → Approver 2 → Final Reviewer → Legal (SCN) → Actioner
    </div>
    """, unsafe_allow_html=True)
    
    # Get workflow statistics
    try:
        # Calculate basic stats
        all_statuses = ["Draft", "Submitted", "Under Investigation", "Under Review", "Final Review", 
                       "Approved", "Legal Review", "Closed", "Rejected"]
        stats = {"total_cases": 0, "by_status": {}}
        
        for status in all_statuses:
            cases = get_cases_by_status(status)
            stats["by_status"][status] = len(cases)
            stats["total_cases"] += len(cases)
        
        # Workflow stage metrics
        st.subheader("📈 Workflow Stage Overview")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            pending_allocation = len(get_cases_by_status("Submitted"))
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{pending_allocation}</div>
                <div class="metric-label">📋 Pending Allocation</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            under_investigation = len(get_cases_by_status("Under Investigation"))
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{under_investigation}</div>
                <div class="metric-label">🔬 Under Investigation</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            primary_review = len(get_cases_by_status("Under Review"))
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{primary_review}</div>
                <div class="metric-label">🔍 Primary Review</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            final_review = len(get_cases_by_status("Final Review"))
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{final_review}</div>
                <div class="metric-label">🎯 Final Review</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            legal_review = len(get_cases_by_status("Legal Review"))
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{legal_review}</div>
                <div class="metric-label">⚖️ Legal Review</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Overall statistics
        st.subheader("📊 Overall Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{stats["total_cases"]}</div>
                <div class="metric-label">Total Cases</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pending_total = (pending_allocation + under_investigation + 
                           primary_review + final_review + legal_review)
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{pending_total}</div>
                <div class="metric-label">Active Cases</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            approved_cases = stats["by_status"].get("Approved", 0)
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{approved_cases}</div>
                <div class="metric-label">Approved Cases</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            closed_cases = stats["by_status"].get("Closed", 0)
            st.markdown(f"""
            <div class="workflow-card">
                <div class="metric-value">{closed_cases}</div>
                <div class="metric-label">Closed Cases</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Workflow visualization charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Workflow Pipeline")
            if stats["by_status"]:
                # Create workflow pipeline chart
                workflow_stages = {
                    "Pending Allocation": pending_allocation,
                    "Under Investigation": under_investigation,
                    "Primary Review": primary_review,
                    "Final Review": final_review,
                    "Legal Review": legal_review,
                    "Approved": approved_cases,
                    "Closed": closed_cases
                }
                
                fig = px.funnel(
                    x=list(workflow_stages.values()),
                    y=list(workflow_stages.keys()),
                    title="Case Workflow Pipeline"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No workflow data available")
        
        with col2:
            st.subheader("📊 Status Distribution")
            if stats["by_status"]:
                fig = px.pie(
                    values=list(stats["by_status"].values()),
                    names=list(stats["by_status"].keys()),
                    title="Case Status Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No status data available")
        
        st.divider()
        
        # Role-specific workflow sections
        show_role_specific_workflow(user_role)
        
    except Exception as e:
        st.error(f"Error loading workflow dashboard: {str(e)}")

def show_role_specific_workflow(user_role):
    """Display role-specific workflow information"""
    
    if user_role in ["Admin", "Investigator"]:
        # Cases requiring allocation (for Allocator role)
        st.subheader("📋 Cases Requiring Allocation")
        try:
            allocation_cases = get_cases_by_status("Submitted")
            if allocation_cases:
                display_workflow_table(allocation_cases, "Allocation")
            else:
                st.info("📭 No cases requiring allocation")
        except Exception as e:
            st.error(f"Error loading allocation cases: {str(e)}")
    
    if user_role in ["Admin", "Investigator"]:
        # Cases under investigation
        st.subheader("🔬 Cases Under Investigation")
        try:
            investigation_cases = get_cases_by_status("Under Investigation")
            if investigation_cases:
                display_workflow_table(investigation_cases, "Investigation")
            else:
                st.info("🔬 No cases under investigation")
        except Exception as e:
            st.error(f"Error loading investigation cases: {str(e)}")
    
    if user_role in ["Admin", "Reviewer"]:
        # Cases requiring primary review
        st.subheader("🔍 Cases Requiring Primary Review")
        try:
            review_cases = get_cases_by_status("Under Review")
            if review_cases:
                display_workflow_table(review_cases, "Primary Review")
            else:
                st.info("🔍 No cases requiring primary review")
        except Exception as e:
            st.error(f"Error loading review cases: {str(e)}")
    
    if user_role in ["Admin", "Reviewer"]:
        # Cases requiring final review
        st.subheader("🎯 Cases Requiring Final Review")
        try:
            final_review_cases = get_cases_by_status("Final Review")
            if final_review_cases:
                display_workflow_table(final_review_cases, "Final Review")
            else:
                st.info("🎯 No cases requiring final review")
        except Exception as e:
            st.error(f"Error loading final review cases: {str(e)}")

def display_workflow_table(cases, stage_name):
    """Display a formatted table for workflow cases"""
    try:
        # Create DataFrame for better display
        case_data = []
        for case in cases[:10]:  # Limit to 10 most recent
            case_data.append({
                "Case ID": case["case_id"],
                "LAN": case["lan"] or "N/A",
                "Customer": case["customer_name"],
                "Type": case["case_type"],
                "Product": case["product"],
                "Region": case["region"],
                "Created": format_datetime(case["created_at"]),
                "Status": case["status"]
            })
        
        if case_data:
            df = pd.DataFrame(case_data)
            
            # Apply custom styling
            def style_case_id(val):
                return 'font-weight: bold; color: #0066cc;'
            
            def style_status(val):
                status_colors = {
                    "Submitted": "#e74c3c",
                    "Under Investigation": "#f39c12",
                    "Under Review": "#3498db",
                    "Final Review": "#9b59b6",
                    "Legal Review": "#8e44ad"
                }
                color = status_colors.get(val, "#95a5a6")
                return f'background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;'
            
            styled_df = df.style.map(style_case_id, subset=['Case ID']) \
                             .map(style_status, subset=['Status']) \
                             .set_table_styles([
                                 {'selector': 'thead th', 'props': [
                                     ('background', 'linear-gradient(135deg, #0066cc 0%, #0052a3 100%)'),
                                     ('color', 'white'),
                                     ('font-weight', 'bold'),
                                     ('text-align', 'center'),
                                     ('padding', '12px')
                                 ]},
                                 {'selector': 'tbody td', 'props': [
                                     ('padding', '10px'),
                                     ('text-align', 'center'),
                                     ('border-bottom', '1px solid #f0f0f0')
                                 ]},
                                 {'selector': 'tbody tr:hover', 'props': [
                                     ('background-color', '#f8f9fa')
                                 ]}
                             ])
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error displaying {stage_name} table: {str(e)}")