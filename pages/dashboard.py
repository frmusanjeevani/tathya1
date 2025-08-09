import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from models import get_case_statistics, get_audit_logs, get_cases_by_status
from utils import get_status_color, format_datetime
from auth import get_current_user_role
from pages.workflow_progress import show_mini_progress, show_workflow_progress
from light_professional_styles import apply_light_professional_styling, get_light_professional_table_style, style_case_id_light

def show():
    """Display dashboard page"""
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
        '>Case Management Dashboard</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Comprehensive overview of case statistics and workflow status</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Apply light professional styling
    apply_light_professional_styling()
    
    # Get statistics
    stats = get_case_statistics()
    user_role = get_current_user_role()
    
    # Key metrics with light professional styling
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
        border: 1px solid #e8eaed;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .metric-card:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
        border-color: #4285f4;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 500;
        color: #1a73e8;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        font-weight: 400;
    }
    .dashboard-table {
        background: #ffffff;
        border-radius: 6px;
        border: 1px solid #e8eaed;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .dashboard-table th {
        background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%);
        color: white;
        font-weight: 500;
        padding: 10px;
        font-size: 13px;
    }
    .dashboard-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #f1f3f4;
        color: #333333;
        font-size: 16px;
        background: #f5f5f5;
    }
    .dashboard-table tbody tr:hover {
        background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="metric-value">{stats["total_cases"]}</div>
            <div class="metric-label">Total Cases</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        pending_cases = stats["by_status"].get("Submitted", 0) + stats["by_status"].get("Under Review", 0) + stats["by_status"].get("Under Investigation", 0) + stats["by_status"].get("Final Review", 0)
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="metric-value">{pending_cases}</div>
            <div class="metric-label">Pending Cases</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        approved_cases = stats["by_status"].get("Approved", 0)
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="metric-value">{approved_cases}</div>
            <div class="metric-label">Approved Cases</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        closed_cases = stats["by_status"].get("Closed", 0)
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="metric-value">{closed_cases}</div>
            <div class="metric-label">Closed Cases</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # TAT (Turn Around Time) Section
    st.subheader("📊 Turn Around Time (TAT) Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg. Review TAT", "2.5 days", delta="-0.3 days")
    
    with col2:
        st.metric("Avg. Approval TAT", "1.8 days", delta="+0.2 days")
    
    with col3:
        st.metric("Avg. Legal Review TAT", "3.2 days", delta="-0.5 days")
    
    with col4:
        st.metric("Avg. Closure TAT", "1.2 days", delta="-0.1 days")
    
    # TAT Trend Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("TAT Trends")
        # Sample data for TAT trends
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=["Week 1", "Week 2", "Week 3", "Week 4"],
            y=[2.8, 2.5, 2.3, 2.5],
            mode='lines+markers',
            name='Review TAT',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=["Week 1", "Week 2", "Week 3", "Week 4"],
            y=[2.0, 1.8, 1.6, 1.8],
            mode='lines+markers',
            name='Approval TAT',
            line=dict(color='green')
        ))
        fig.add_trace(go.Scatter(
            x=["Week 1", "Week 2", "Week 3", "Week 4"],
            y=[3.7, 3.2, 3.0, 3.2],
            mode='lines+markers',
            name='Legal Review TAT',
            line=dict(color='purple')
        ))
        fig.update_layout(
            title="TAT Trends (Days)",
            xaxis_title="Time Period",
            yaxis_title="Days",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("SLA Compliance")
        # SLA compliance data
        sla_data = {
            "Review": 85,
            "Approval": 92,
            "Legal Review": 78,
            "Closure": 95
        }
        
        fig = px.bar(
            x=list(sla_data.keys()),
            y=list(sla_data.values()),
            title="SLA Compliance (%)",
            labels={"x": "Process", "y": "Compliance %"},
            color=list(sla_data.values()),
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cases by Status")
        if stats["by_status"]:
            fig = px.pie(
                values=list(stats["by_status"].values()),
                names=list(stats["by_status"].keys()),
                title="Case Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No case data available")
    
    with col2:
        st.subheader("Cases by Region")
        if stats["by_region"]:
            fig = px.bar(
                x=list(stats["by_region"].keys()),
                y=list(stats["by_region"].values()),
                title="Cases by Region",
                labels={"x": "Region", "y": "Number of Cases"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No regional data available")
    
    # Recent cases with enhanced formatting
    st.subheader("Recent Cases")
    
    # Add enhanced table styling
    st.markdown("""
    <style>
    .enhanced-table {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    .enhanced-table table {
        width: 100%;
        border-collapse: collapse;
    }
    .enhanced-table th {
        background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
        color: white;
        padding: 15px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .enhanced-table td {
        padding: 12px;
        border-bottom: 1px solid #f0f0f0;
        color: #333;
        font-size: 13px;
        transition: all 0.2s ease;
    }
    .enhanced-table tr:hover td {
        background-color: #FFF4D9;
        transform: scale(1.01);
    }
    .enhanced-table tr:last-child td {
        border-bottom: none;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-submitted { background: #fff3cd; color: #856404; }
    .status-approved { background: #d4edda; color: #155724; }
    .status-rejected { background: #f8d7da; color: #721c24; }
    .status-draft { background: #e2e3e5; color: #383d41; }
    </style>
    """, unsafe_allow_html=True)
    
    if stats["recent_cases"]:
        # Create enhanced HTML table
        table_rows = ""
        for case in stats["recent_cases"]:
            status_class = f"status-{case['status'].lower().replace(' ', '-')}"
            table_rows += f"""
            <tr>
                <td><strong>{case['case_id']}</strong></td>
                <td>{case['lan'] or 'N/A'}</td>
                <td><span class="status-badge {status_class}">{case['status']}</span></td>
                <td>{case['product']}</td>
                <td>{case['region']}</td>
                <td>{format_datetime(case['created_at'])}</td>
                <td>{case['created_by']}</td>
            </tr>
            """
        
        # Create enhanced dataframe with proper styling
        cases_data = []
        for case in stats["recent_cases"]:
            cases_data.append({
                "Case ID": case["case_id"],
                "LAN": case["lan"] or "N/A",
                "Status": case["status"],
                "Product": case["product"],
                "Region": case["region"],
                "Created": format_datetime(case["created_at"]),
                "Created By": case["created_by"]
            })
        
        # Display as enhanced dataframe with custom styling
        if cases_data:
            import pandas as pd
            df = pd.DataFrame(cases_data)
            
            # Apply styling to the dataframe
            def style_status(val):
                if val == "Approved":
                    return 'background-color: #d4edda; color: #155724; font-weight: bold; padding: 4px 8px; border-radius: 12px;'
                elif val == "Submitted":
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold; padding: 4px 8px; border-radius: 12px;'
                elif val == "Rejected":
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold; padding: 4px 8px; border-radius: 12px;'
                elif val == "Closed":
                    return 'background-color: #e2e3e5; color: #383d41; font-weight: bold; padding: 4px 8px; border-radius: 12px;'
                else:
                    return 'font-weight: bold; padding: 4px 8px;'
            

            
            # Apply styling and display
            styled_df = df.style.map(style_status, subset=['Status']) \
                             .map(style_case_id_light, subset=['Case ID']) \
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
    else:
        st.info("No recent cases found")
    
    # Role-specific sections with enhanced formatting
    if user_role in ["Reviewer", "Admin"]:
        st.subheader("🔍 Cases Requiring Review")
        # Get cases that need review (Submitted status)

        review_cases = get_cases_by_status("Submitted")
        
        if review_cases:
            # Create enhanced review table
            table_rows = ""
            for case in review_cases:
                table_rows += f"""
                <tr>
                    <td><strong>{case['case_id']}</strong></td>
                    <td>{case['lan'] or 'N/A'}</td>
                    <td>{case['case_type']}</td>
                    <td>{case['product']}</td>
                    <td>{case['region']}</td>
                    <td>{format_datetime(case['created_at'])}</td>
                </tr>
                """
            
            # Create enhanced dataframe for review cases
            review_data = []
            for case in review_cases:
                review_data.append({
                    "Case ID": case["case_id"],
                    "LAN": case["lan"] or "N/A",
                    "Case Type": case["case_type"],
                    "Product": case["product"],
                    "Region": case["region"],
                    "Submitted": format_datetime(case["created_at"])
                })
            
            if review_data:
                import pandas as pd
                df = pd.DataFrame(review_data)
                
                def style_case_id(val):
                    return 'font-weight: bold; color: #0066cc;'
                
                styled_df = df.style.map(style_case_id, subset=['Case ID']) \
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
        else:
            st.info("📭 No cases pending review")
    
    # Investigation Panel Section
    if user_role in ["Investigator", "Admin"]:
        st.subheader("🔍 Cases Under Investigation")
        investigation_cases = get_cases_by_status("Under Investigation")
        
        if investigation_cases:
            investigation_data = []
            for case in investigation_cases:
                investigation_data.append({
                    "Case ID": case["case_id"],
                    "LAN": case["lan"] or "N/A",
                    "Case Type": case["case_type"],
                    "Product": case["product"],
                    "Region": case["region"],
                    "Assigned": format_datetime(case["updated_at"])
                })
            
            if investigation_data:
                import pandas as pd
                df = pd.DataFrame(investigation_data)
                
                styled_df = df.style.map(style_case_id_light, subset=['Case ID']) \
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
        else:
            st.info("📭 No cases under investigation")

    # Final Review Section
    if user_role in ["Approver", "Admin"]:
        st.subheader("🎯 Cases Requiring Final Review")
        final_review_cases = get_cases_by_status("Final Review")
        
        if final_review_cases:
            final_review_data = []
            for case in final_review_cases:
                final_review_data.append({
                    "Case ID": case["case_id"],
                    "LAN": case["lan"] or "N/A",
                    "Case Type": case["case_type"],
                    "Product": case["product"],
                    "Region": case["region"],
                    "Investigation Completed": format_datetime(case["updated_at"])
                })
            
            if final_review_data:
                import pandas as pd
                df = pd.DataFrame(final_review_data)
                
                styled_df = df.style.map(style_case_id_light, subset=['Case ID']) \
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
        else:
            st.info("📭 No cases pending final review")

    if user_role in ["Approver", "Admin"]:
        st.subheader("✅ Cases Requiring Approval")
        # Get cases that need approval (Approved by reviewer status)
        approval_cases = get_cases_by_status("Approved")
        
        if approval_cases:
            # Create enhanced approval table
            table_rows = ""
            for case in approval_cases:
                table_rows += f"""
                <tr>
                    <td><strong>{case['case_id']}</strong></td>
                    <td>{case['lan'] or 'N/A'}</td>
                    <td>{case['case_type']}</td>
                    <td>{case['product']}</td>
                    <td>{case['region']}</td>
                    <td>{format_datetime(case['updated_at'])}</td>
                </tr>
                """
            
            # Create enhanced dataframe for approval cases
            approval_data = []
            for case in approval_cases:
                approval_data.append({
                    "Case ID": case["case_id"],
                    "LAN": case["lan"] or "N/A",
                    "Case Type": case["case_type"],
                    "Product": case["product"],
                    "Region": case["region"],
                    "Reviewed": format_datetime(case["updated_at"])
                })
            
            if approval_data:
                import pandas as pd
                df = pd.DataFrame(approval_data)
                
                styled_df = df.style.map(style_case_id_light, subset=['Case ID']) \
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
        else:
            st.info("📭 No cases pending approval")
    
    # Recent activity with enhanced formatting
    st.subheader("Recent Activity")
    recent_logs = get_audit_logs(limit=10)
    if recent_logs:
        # Create enhanced activity table
        table_rows = ""
        for log in recent_logs:
            table_rows += f"""
            <tr>
                <td>{format_datetime(log['performed_at'])}</td>
                <td><strong>{log['case_id'] or 'System'}</strong></td>
                <td><span class="status-badge status-submitted">{log['action']}</span></td>
                <td>{log['details'] or 'N/A'}</td>
                <td>{log['performed_by']}</td>
            </tr>
            """
        
        # Create enhanced dataframe for activity logs
        activity_data = []
        for log in recent_logs:
            activity_data.append({
                "Time": format_datetime(log["performed_at"]),
                "Case ID": log["case_id"] or "System",
                "Action": log["action"],
                "Details": log["details"] or "N/A",
                "User": log["performed_by"]
            })
        
        if activity_data:
            import pandas as pd
            df = pd.DataFrame(activity_data)
            
            def style_case_id(val):
                if val != "System":
                    return 'font-weight: bold; color: #0066cc;'
                return 'font-weight: bold; color: #666;'
            
            def style_action(val):
                return 'background-color: #fff3cd; color: #856404; font-weight: bold; padding: 4px 8px; border-radius: 12px;'
            
            styled_df = df.style.map(style_case_id, subset=['Case ID']) \
                             .map(style_action, subset=['Action']) \
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
    else:
        st.info("No recent activity found")
