import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from models import get_case_statistics, get_cases_by_status
from utils import format_datetime
from auth import get_current_user_role, require_role
from pages.workflow_progress import show_workflow_progress, show_mini_progress

@require_role(["Admin", "Reviewer", "Approver", "Investigator", "Legal Reviewer", "Actioner"])
def show():
    """Enhanced workflow dashboard with progress visualization"""
    # Add centered header with AI styling
    st.markdown("""
    <div style='
        text-align: center;
        margin: 15px 0 15px 0;
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
        '>🔎 Tathya Investigation Intelligence</h1>
        <p style='
            font-size: 1.1rem;
            color: #666;
            font-weight: 400;
            margin: 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.03);
            font-family: "Segoe UI", Arial, sans-serif;
        '>Represents inspection, search, and scrutiny</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Real-time workflow visualization with animated progress tracking**")
    
    # Get all cases for workflow analysis
    all_cases = []
    statuses = ["Draft", "Submitted", "Under Review", "Under Investigation", "Final Review", "Approved", "Legal Review", "Closed", "Rejected"]
    
    for status in statuses:
        cases = get_cases_by_status(status)
        all_cases.extend(cases)
    
    if not all_cases:
        st.info("No cases found in the system")
        return
    
    # Workflow pipeline visualization
    st.subheader("🔄 Workflow Pipeline Overview")
    
    # Create pipeline metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    pipeline_stages = {
        "Entry": len([c for c in all_cases if c['status'] == 'Draft']),
        "Primary Review": len([c for c in all_cases if c['status'] in ['Submitted', 'Under Review']]),
        "Investigation": len([c for c in all_cases if c['status'] == 'Under Investigation']),
        "Final Review": len([c for c in all_cases if c['status'] == 'Final Review']),
        "Completed": len([c for c in all_cases if c['status'] in ['Approved', 'Closed']])
    }
    
    with col1:
        st.metric("📝 Entry", pipeline_stages["Entry"], delta=None)
    with col2:
        st.metric("🔍 Primary Review", pipeline_stages["Primary Review"], delta=None)
    with col3:
        st.metric("🔬 Investigation", pipeline_stages["Investigation"], delta=None)
    with col4:
        st.metric("🎯 Final Review", pipeline_stages["Final Review"], delta=None)
    with col5:
        st.metric("✅ Completed", pipeline_stages["Completed"], delta=None)
    
    # Workflow funnel chart
    st.subheader("📈 Workflow Funnel Analysis")
    
    funnel_data = pd.DataFrame({
        'Stage': list(pipeline_stages.keys()),
        'Cases': list(pipeline_stages.values())
    })
    
    fig_funnel = px.funnel(funnel_data, x='Cases', y='Stage', 
                          title="Case Flow Through Workflow Stages",
                          color='Cases',
                          color_continuous_scale='Blues')
    fig_funnel.update_layout(height=400)
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Workflow timeline with animated progress
    st.subheader("⏱️ Recent Workflow Activity")
    
    # Get recent cases with progress
    recent_cases = sorted(all_cases, key=lambda x: x.get('updated_at', x.get('created_at', '')), reverse=True)[:10]
    
    if recent_cases:
        for i, case in enumerate(recent_cases):
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    st.markdown(f"**{case['case_id']}**")
                    st.caption(f"{case['case_type']} • {case['product']}")
                
                with col2:
                    # Show mini progress bar
                    progress_html = show_mini_progress(case['status'])
                    st.markdown(progress_html, unsafe_allow_html=True)
                
                with col3:
                    if st.button("📊 View", key=f"view_{case['case_id']}_{i}"):
                        st.session_state[f"show_progress_{case['case_id']}"] = True
                
                # Show detailed progress if button clicked
                if st.session_state.get(f"show_progress_{case['case_id']}", False):
                    with st.expander(f"📈 Detailed Progress - {case['case_id']}", expanded=True):
                        show_workflow_progress(case['case_id'])
                        if st.button("Close", key=f"close_{case['case_id']}_{i}"):
                            st.session_state[f"show_progress_{case['case_id']}"] = False
                            st.rerun()
                
                st.divider()
    
    # Workflow performance metrics
    st.subheader("⚡ Workflow Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution pie chart
        status_counts = {}
        for case in all_cases:
            status = case['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig_pie = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Current Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Case type workflow analysis
        case_types = {}
        for case in all_cases:
            case_type = case['case_type']
            case_types[case_type] = case_types.get(case_type, 0) + 1
        
        if case_types:
            fig_bar = px.bar(
                x=list(case_types.keys()),
                y=list(case_types.values()),
                title="Cases by Type",
                labels={'x': 'Case Type', 'y': 'Number of Cases'},
                color=list(case_types.values()),
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Workflow bottleneck analysis
    st.subheader("🚦 Bottleneck Analysis")
    
    bottleneck_data = {
        "Primary Review": len([c for c in all_cases if c['status'] in ['Submitted', 'Under Review']]),
        "Investigation": len([c for c in all_cases if c['status'] == 'Under Investigation']),
        "Final Review": len([c for c in all_cases if c['status'] == 'Final Review']),
        "Legal Review": len([c for c in all_cases if c['status'] == 'Legal Review'])
    }
    
    # Find bottleneck
    if bottleneck_data:
        max_stage = max(bottleneck_data, key=bottleneck_data.get)
        max_count = bottleneck_data[max_stage]
        
        if max_count > 0:
            st.warning(f"🚨 **Bottleneck Alert**: {max_count} cases are currently in {max_stage} stage")
            
            # Show bottleneck breakdown
            bottleneck_df = pd.DataFrame(list(bottleneck_data.items()), columns=['Stage', 'Cases'])
            fig_bottleneck = px.bar(
                bottleneck_df, 
                x='Stage', 
                y='Cases',
                title="Cases by Workflow Stage",
                color='Cases',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_bottleneck, use_container_width=True)
        else:
            st.success("✅ No significant bottlenecks detected in the workflow")
    
    # Interactive case search and progress view
    st.subheader("🔍 Case Progress Lookup")
    
    # Case ID search
    case_ids = [case['case_id'] for case in all_cases]
    selected_case_id = st.selectbox(
        "Select a case to view detailed progress:",
        [""] + case_ids,
        key="progress_lookup"
    )
    
    if selected_case_id:
        selected_case = next((case for case in all_cases if case['case_id'] == selected_case_id), None)
        if selected_case:
            st.markdown("---")
            st.markdown(f"### 📊 Progress Details for {selected_case_id}")
            show_workflow_progress(selected_case_id)
            
            # Additional case details
            with st.expander("📋 Case Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Case Type:** {selected_case['case_type']}")
                    st.write(f"**Product:** {selected_case['product']}")
                    st.write(f"**Region:** {selected_case['region']}")
                with col2:
                    st.write(f"**Created By:** {selected_case['created_by']}")
                    st.write(f"**Created:** {format_datetime(selected_case['created_at'])}")
                    st.write(f"**Last Updated:** {format_datetime(selected_case.get('updated_at', selected_case['created_at']))}")