import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from auth import require_role, get_current_user
from models import get_cases_by_status, get_case_comments
from database import get_db_connection, log_audit
from utils import format_datetime

@require_role(["Admin", "Initiator", "Reviewer", "Approver", "Legal Reviewer", "Actioner", "Investigator"])
def show():
    """Customizable User Dashboard with Case Summary Widgets"""
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
        '>USER DASHBOARD</h2>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    username = current_user.get("username", "Unknown") if isinstance(current_user, dict) else current_user
    user_role = current_user.get("role", "Unknown") if isinstance(current_user, dict) else "Unknown"
    
    # Dashboard customization controls
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🎛️ Dashboard Customization")
    
    with col2:
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()
    
    # Widget selection
    widget_options = {
        "📈 Case Statistics": "case_stats",
        "🎯 My Cases Summary": "my_cases", 
        "📊 Status Distribution": "status_chart",
        "⏱️ Recent Activity": "recent_activity",
        "🔥 Priority Cases": "priority_cases",
        "📅 Timeline View": "timeline",
        "🏆 Performance Metrics": "performance",
        "📋 Workflow Progress": "workflow_progress"
    }
    
    # Multi-select for widgets
    selected_widgets = st.multiselect(
        "Select widgets to display:",
        options=list(widget_options.keys()),
        default=get_default_widgets(user_role),
        help="Choose which widgets to show on your dashboard"
    )
    
    # Widget layout options
    layout_col1, layout_col2 = st.columns(2)
    with layout_col1:
        layout_style = st.selectbox("Layout Style", ["2 Columns", "3 Columns", "Single Column"])
    with layout_col2:
        auto_refresh = st.selectbox("Auto Refresh", ["Off", "30 seconds", "1 minute", "5 minutes"])
    
    # Save user preferences
    save_user_preferences(username, selected_widgets, layout_style, auto_refresh)
    
    st.markdown("---")
    
    # Display selected widgets
    if selected_widgets:
        if layout_style == "Single Column":
            display_widgets_single_column(selected_widgets, widget_options, username, user_role)
        elif layout_style == "2 Columns":
            display_widgets_two_columns(selected_widgets, widget_options, username, user_role)
        else:  # 3 Columns
            display_widgets_three_columns(selected_widgets, widget_options, username, user_role)
    else:
        st.info("👆 Select widgets above to customize your dashboard")

def get_default_widgets(user_role):
    """Get default widgets based on user role"""
    role_defaults = {
        "Admin": ["📈 Case Statistics", "📊 Status Distribution", "⏱️ Recent Activity", "📋 Workflow Progress"],
        "Initiator": ["🎯 My Cases Summary", "📈 Case Statistics", "⏱️ Recent Activity"],
        "Reviewer": ["🎯 My Cases Summary", "🔥 Priority Cases", "📊 Status Distribution"],
        "Approver": ["🔥 Priority Cases", "📊 Status Distribution", "🏆 Performance Metrics"],
        "Investigator": ["🎯 My Cases Summary", "📅 Timeline View", "🔥 Priority Cases"],
        "Legal Reviewer": ["🔥 Priority Cases", "📊 Status Distribution", "⏱️ Recent Activity"],
        "Actioner": ["🔥 Priority Cases", "🏆 Performance Metrics", "📊 Status Distribution"]
    }
    return role_defaults.get(user_role, ["📈 Case Statistics", "🎯 My Cases Summary"])

def display_widgets_single_column(selected_widgets, widget_options, username, user_role):
    """Display widgets in single column layout"""
    for widget_name in selected_widgets:
        widget_key = widget_options[widget_name]
        render_widget(widget_key, widget_name, username, user_role)
        st.markdown("---")

def display_widgets_two_columns(selected_widgets, widget_options, username, user_role):
    """Display widgets in two column layout"""
    col1, col2 = st.columns(2)
    
    for i, widget_name in enumerate(selected_widgets):
        widget_key = widget_options[widget_name]
        
        if i % 2 == 0:
            with col1:
                render_widget(widget_key, widget_name, username, user_role)
        else:
            with col2:
                render_widget(widget_key, widget_name, username, user_role)

def display_widgets_three_columns(selected_widgets, widget_options, username, user_role):
    """Display widgets in three column layout"""
    col1, col2, col3 = st.columns(3)
    
    for i, widget_name in enumerate(selected_widgets):
        widget_key = widget_options[widget_name]
        
        if i % 3 == 0:
            with col1:
                render_widget(widget_key, widget_name, username, user_role)
        elif i % 3 == 1:
            with col2:
                render_widget(widget_key, widget_name, username, user_role)
        else:
            with col3:
                render_widget(widget_key, widget_name, username, user_role)

def render_widget(widget_key, widget_name, username, user_role):
    """Render individual widget based on type"""
    st.markdown(f"### {widget_name}")
    
    if widget_key == "case_stats":
        render_case_statistics_widget(username, user_role)
    elif widget_key == "my_cases":
        render_my_cases_widget(username, user_role)
    elif widget_key == "status_chart":
        render_status_distribution_widget(username, user_role)
    elif widget_key == "recent_activity":
        render_recent_activity_widget(username, user_role)
    elif widget_key == "priority_cases":
        render_priority_cases_widget(username, user_role)
    elif widget_key == "timeline":
        render_timeline_widget(username, user_role)
    elif widget_key == "performance":
        render_performance_widget(username, user_role)
    elif widget_key == "workflow_progress":
        render_workflow_progress_widget(username, user_role)

def render_case_statistics_widget(username, user_role):
    """Render case statistics widget"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get case counts by status
            cursor.execute("SELECT status, COUNT(*) as count FROM cases GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # Get total cases
            total_cases = sum(status_counts.values())
            
            # Display metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("Total Cases", total_cases)
            with metric_col2:
                st.metric("Active", status_counts.get("Submitted", 0) + status_counts.get("Under Review", 0))
            with metric_col3:
                st.metric("Approved", status_counts.get("Approved", 0))
            with metric_col4:
                st.metric("Closed", status_counts.get("Closed", 0))
                
    except Exception as e:
        st.error(f"Error loading case statistics: {str(e)}")

def render_my_cases_widget(username, user_role):
    """Render my cases summary widget"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user's cases
            if user_role == "Admin":
                cursor.execute("SELECT * FROM cases ORDER BY created_at DESC LIMIT 5")
            else:
                cursor.execute("SELECT * FROM cases WHERE created_by = ? ORDER BY created_at DESC LIMIT 5", (username,))
            
            cases = cursor.fetchall()
            
            if cases:
                for case in cases:
                    case_dict = dict(case)
                    
                    # Create case card
                    with st.container():
                        st.markdown(f"""
                        **{case_dict['case_id']}** - {case_dict['customer_name']}
                        
                        📊 Status: `{case_dict['status']}` | 🏢 {case_dict['case_type']} | 💰 ₹{case_dict.get('loan_amount', 0):,.0f}
                        """)
                        st.divider()
            else:
                st.info("No cases found")
                
    except Exception as e:
        st.error(f"Error loading my cases: {str(e)}")

def render_status_distribution_widget(username, user_role):
    """Render status distribution chart widget"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) as count FROM cases GROUP BY status")
            data = cursor.fetchall()
            
            if data:
                # Convert to list of dictionaries for DataFrame
                data_list = [{'Status': row[0], 'Count': row[1]} for row in data]
                df = pd.DataFrame(data_list)
                
                # Create pie chart
                fig = px.pie(df, values='Count', names='Status', 
                           title="Case Status Distribution",
                           color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(height=300, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available")
                
    except Exception as e:
        st.error(f"Error loading status chart: {str(e)}")

def render_recent_activity_widget(username, user_role):
    """Render recent activity widget"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get recent audit logs
            if user_role == "Admin":
                cursor.execute("""
                    SELECT case_id, action, details, performed_by, created_at 
                    FROM audit_logs 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
            else:
                cursor.execute("""
                    SELECT case_id, action, details, performed_by, created_at 
                    FROM audit_logs 
                    WHERE performed_by = ?
                    ORDER BY created_at DESC 
                    LIMIT 5
                """, (username,))
            
            activities = cursor.fetchall()
            
            if activities:
                for activity in activities:
                    activity_dict = dict(activity)
                    st.markdown(f"""
                    **{activity_dict['action']}** - {activity_dict['case_id']}
                    
                    👤 {activity_dict['performed_by']} | ⏰ {format_datetime(activity_dict['created_at'])}
                    """)
                    st.divider()
            else:
                st.info("No recent activity")
                
    except Exception as e:
        st.error(f"Error loading recent activity: {str(e)}")

def render_priority_cases_widget(username, user_role):
    """Render priority cases widget"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get high priority cases (high loan amounts or urgent status)
            cursor.execute("""
                SELECT * FROM cases 
                WHERE status IN ('Under Review', 'Final Review', 'Legal Review') 
                AND (loan_amount > 500000 OR case_type LIKE '%Fraud%')
                ORDER BY loan_amount DESC, created_at ASC
                LIMIT 5
            """)
            
            priority_cases = cursor.fetchall()
            
            if priority_cases:
                for case in priority_cases:
                    case_dict = dict(case)
                    priority_level = "🔴 HIGH" if case_dict.get('loan_amount', 0) > 1000000 else "🟡 MEDIUM"
                    
                    st.markdown(f"""
                    {priority_level} **{case_dict['case_id']}**
                    
                    👤 {case_dict['customer_name']} | 💰 ₹{case_dict.get('loan_amount', 0):,.0f} | 📊 {case_dict['status']}
                    """)
                    st.divider()
            else:
                st.info("No priority cases")
                
    except Exception as e:
        st.error(f"Error loading priority cases: {str(e)}")

def render_timeline_widget(username, user_role):
    """Render timeline widget"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get cases created in last 7 days
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM cases 
                WHERE created_at >= date('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            timeline_data = cursor.fetchall()
            
            if timeline_data:
                # Convert to list of dictionaries for DataFrame
                data_list = [{'Date': row[0], 'Cases': row[1]} for row in timeline_data]
                df = pd.DataFrame(data_list)
                
                # Create line chart
                fig = px.line(df, x='Date', y='Cases', 
                            title="Cases Created (Last 7 Days)",
                            markers=True)
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No timeline data")
                
    except Exception as e:
        st.error(f"Error loading timeline: {str(e)}")

def render_performance_widget(username, user_role):
    """Render performance metrics widget"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate performance metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_processed,
                    AVG(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) * 100 as approval_rate,
                    COUNT(CASE WHEN created_at >= date('now', '-30 days') THEN 1 END) as last_30_days
                FROM cases
                WHERE performed_by = ? OR created_by = ?
            """, (username, username))
            
            metrics = cursor.fetchone()
            
            if metrics:
                metrics_dict = dict(metrics)
                
                perf_col1, perf_col2 = st.columns(2)
                with perf_col1:
                    st.metric("Cases Processed", metrics_dict.get('total_processed', 0))
                    st.metric("Last 30 Days", metrics_dict.get('last_30_days', 0))
                
                with perf_col2:
                    approval_rate = metrics_dict.get('approval_rate', 0)
                    st.metric("Approval Rate", f"{approval_rate:.1f}%")
                    
                    # Performance indicator
                    if approval_rate > 80:
                        st.success("🏆 Excellent Performance")
                    elif approval_rate > 60:
                        st.info("👍 Good Performance")
                    else:
                        st.warning("📈 Room for Improvement")
            else:
                st.info("No performance data")
                
    except Exception as e:
        st.error(f"Error loading performance metrics: {str(e)}")

def render_workflow_progress_widget(username, user_role):
    """Render workflow progress widget"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get workflow stage counts
            workflow_stages = [
                "Draft", "Submitted", "Under Review", "Under Investigation", 
                "Final Review", "Legal Review", "Approved", "Closed"
            ]
            
            stage_counts = {}
            for stage in workflow_stages:
                cursor.execute("SELECT COUNT(*) FROM cases WHERE status = ?", (stage,))
                count = cursor.fetchone()[0]
                stage_counts[stage] = count
            
            # Create horizontal bar chart
            stages = list(stage_counts.keys())
            counts = list(stage_counts.values())
            
            fig = go.Figure(data=[go.Bar(y=stages, x=counts, orientation='h')])
            fig.update_layout(
                title="Workflow Stage Distribution",
                height=300,
                yaxis={'categoryorder': 'array', 'categoryarray': stages}
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading workflow progress: {str(e)}")

def save_user_preferences(username, widgets, layout, refresh):
    """Save user dashboard preferences"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create preferences table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    username TEXT PRIMARY KEY,
                    dashboard_widgets TEXT,
                    layout_style TEXT,
                    auto_refresh TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Save preferences
            widgets_str = ",".join(widgets) if widgets else ""
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences 
                (username, dashboard_widgets, layout_style, auto_refresh, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (username, widgets_str, layout, refresh, datetime.now()))
            
            conn.commit()
            
    except Exception as e:
        st.error(f"Error saving preferences: {str(e)}")

def load_user_preferences(username):
    """Load user dashboard preferences"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dashboard_widgets, layout_style, auto_refresh 
                FROM user_preferences 
                WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            if result:
                return dict(result)
            
    except Exception:
        pass
    
    return None