import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from models import get_cases_by_status, get_case_by_id, add_case_comment
from auth import get_current_user, require_auth
from database import get_db_connection
import uuid

def show():
    """Stakeholder Actioner module for task and action orchestration"""
    
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
        '>Stakeholder Actioner</h3>
        <p style='
            margin: 5px 0 0 0;
            color: #34495e;
            font-size: 0.95rem;
            font-family: "Segoe UI", Arial, sans-serif;
        '>Task and action orchestration center for stakeholder coordination</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_user = get_current_user()
    
    # Initialize session state
    if "actioner_case_id" not in st.session_state:
        st.session_state.actioner_case_id = ""
    if "actioner_tab" not in st.session_state:
        st.session_state.actioner_tab = "task_dashboard"
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Task Dashboard", 
        "➕ Create Action", 
        "👥 Stakeholder Management", 
        "📈 Progress Tracking",
        "📋 Reports"
    ])
    
    with tab1:
        show_task_dashboard()
    
    with tab2:
        show_create_action()
    
    with tab3:
        show_stakeholder_management()
    
    with tab4:
        show_progress_tracking()
    
    with tab5:
        show_action_reports()


def show_task_dashboard():
    """Main dashboard showing all active tasks and actions"""
    st.markdown("### Active Tasks & Actions Dashboard")
    
    # Summary metrics
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get task statistics
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(CASE WHEN due_date < date('now') THEN 1 ELSE 0 END) as overdue_count
                FROM stakeholder_actions 
                GROUP BY status
            """)
            task_stats = cursor.fetchall()
            
            # Get active actions for current user
            cursor.execute("""
                SELECT sa.*, c.customer_name, c.case_type
                FROM stakeholder_actions sa
                LEFT JOIN cases c ON sa.case_id = c.case_id
                WHERE sa.assigned_to = ? OR sa.created_by = ?
                ORDER BY sa.due_date ASC, sa.priority DESC
                LIMIT 10
            """, (current_user, current_user))
            user_actions = cursor.fetchall()
            
    except Exception as e:
        st.error(f"Error retrieving task data: {str(e)}")
        task_stats = []
        user_actions = []
    
    # Display summary metrics
    if task_stats:
        col1, col2, col3, col4 = st.columns(4)
        
        total_active = sum([stat['count'] for stat in task_stats if stat['status'] != 'Completed'])
        total_completed = sum([stat['count'] for stat in task_stats if stat['status'] == 'Completed'])
        total_overdue = sum([stat['overdue_count'] for stat in task_stats])
        total_pending = sum([stat['count'] for stat in task_stats if stat['status'] == 'Pending'])
        
        with col1:
            st.metric("Active Tasks", total_active)
        with col2:
            st.metric("Completed Tasks", total_completed) 
        with col3:
            st.metric("Overdue Tasks", total_overdue, delta=f"-{total_overdue}" if total_overdue > 0 else "0")
        with col4:
            st.metric("Pending Tasks", total_pending)
    
    # Display user's active tasks
    if user_actions:
        st.markdown("### Your Active Tasks")
        
        for action in user_actions:
            # Determine status color
            status_color = {
                'Pending': '🟡',
                'In Progress': '🔵', 
                'Completed': '🟢',
                'Overdue': '🔴'
            }.get(action['status'], '⚪')
            
            # Check if overdue
            due_date = datetime.strptime(action['due_date'], '%Y-%m-%d').date()
            is_overdue = due_date < date.today() and action['status'] != 'Completed'
            
            with st.expander(f"{status_color} {action['task_title']} - {action['case_id']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Case ID:** {action['case_id']}")
                    st.write(f"**Customer:** {action.get('customer_name', 'N/A')}")
                    st.write(f"**Task Type:** {action['task_type']}")
                    st.write(f"**Priority:** {action['priority']}")
                
                with col2:
                    st.write(f"**Assigned To:** {action['assigned_to']}")
                    st.write(f"**Stakeholder:** {action['stakeholder_type']}")
                    st.write(f"**Due Date:** {action['due_date']}")
                    if is_overdue:
                        st.error("⚠️ OVERDUE")
                    st.write(f"**Status:** {action['status']}")
                
                with col3:
                    st.write(f"**Created By:** {action['created_by']}")
                    st.write(f"**Created At:** {action['created_at']}")
                    if action['description']:
                        st.write(f"**Description:** {action['description'][:100]}...")
                
                # Action buttons
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button(f"📝 Update Status", key=f"update_{action['id']}"):
                        update_action_status(action['id'])
                        st.rerun()
                
                with col_b:
                    if st.button(f"💬 Add Comment", key=f"comment_{action['id']}"):
                        add_action_comment(action['id'])
                        st.rerun()
                
                with col_c:
                    if action['status'] != 'Completed':
                        if st.button(f"✅ Mark Complete", key=f"complete_{action['id']}"):
                            complete_action(action['id'])
                            st.rerun()
    
    else:
        st.info("📭 No active tasks assigned to you at this time")


def show_create_action():
    """Create new actions and tasks for stakeholders"""
    st.markdown("### Create New Action/Task")
    
    with st.form("create_action_form"):
        # Basic Information
        st.markdown("#### Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            case_id = st.text_input("Case ID *", placeholder="e.g., CASE-2025-001")
            task_title = st.text_input("Task Title *", placeholder="e.g., Document Collection from Customer")
            task_type = st.selectbox("Task Type *", [
                "Document Collection",
                "Customer Contact",
                "Verification Request", 
                "Legal Action",
                "Regulatory Submission",
                "Internal Review",
                "External Coordination",
                "Recovery Action",
                "Investigation Support",
                "Other"
            ])
            
        with col2:
            stakeholder_type = st.selectbox("Stakeholder Type *", [
                "Internal - Operations",
                "Internal - Legal", 
                "Internal - Compliance",
                "Internal - Risk",
                "Internal - IT",
                "External - Customer",
                "External - Vendor",
                "External - Law Enforcement",
                "External - Regulatory",
                "External - Legal Counsel"
            ])
            assigned_to = st.text_input("Assigned To *", placeholder="User ID or Department")
            priority = st.selectbox("Priority Level *", ["Low", "Medium", "High", "Critical"])
        
        # Task Details
        st.markdown("#### Task Details")
        description = st.text_area(
            "Task Description *",
            placeholder="Detailed description of the task to be performed...",
            height=100
        )
        
        expected_outcome = st.text_area(
            "Expected Outcome",
            placeholder="What should be achieved upon completion...",
            height=80
        )
        
        # Timeline and Dependencies
        col3, col4 = st.columns(2)
        with col3:
            due_date = st.date_input("Due Date *", value=date.today() + timedelta(days=7))
            estimated_hours = st.number_input("Estimated Hours", min_value=0.5, max_value=160.0, value=2.0, step=0.5)
        
        with col4:
            dependency_on = st.text_input("Depends On (Task ID)", placeholder="Optional - if this task depends on another")
            notify_stakeholders = st.multiselect("Notify Stakeholders", [
                "Case Owner",
                "Department Head", 
                "Compliance Team",
                "Risk Team",
                "Legal Team"
            ])
        
        # Instructions and Resources
        st.markdown("#### Instructions & Resources")
        special_instructions = st.text_area(
            "Special Instructions",
            placeholder="Any special instructions or considerations...",
            height=80
        )
        
        resources_needed = st.text_area(
            "Resources/Access Needed",
            placeholder="Systems access, documents, approvals needed...",
            height=80
        )
        
        # Submission
        col_submit1, col_submit2, col_submit3 = st.columns(3)
        with col_submit2:
            submitted = st.form_submit_button("🎯 Create Action", use_container_width=True)
        
        if submitted:
            if case_id and task_title and task_type and stakeholder_type and assigned_to and description:
                # Create new action
                action_data = {
                    "case_id": case_id,
                    "task_title": task_title,
                    "task_type": task_type,
                    "stakeholder_type": stakeholder_type,
                    "assigned_to": assigned_to,
                    "priority": priority,
                    "description": description,
                    "expected_outcome": expected_outcome,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "estimated_hours": estimated_hours,
                    "dependency_on": dependency_on,
                    "special_instructions": special_instructions,
                    "resources_needed": resources_needed,
                    "created_by": get_current_user(),
                    "status": "Pending"
                }
                
                action_id = save_stakeholder_action(action_data)
                if action_id:
                    st.success(f"✅ Action created successfully! Action ID: {action_id}")
                    
                    # Send notifications if requested
                    if notify_stakeholders:
                        send_stakeholder_notifications(action_id, notify_stakeholders, action_data)
                        st.info("📧 Notifications sent to selected stakeholders")
                    
                    # Add case comment
                    add_case_comment(
                        case_id,
                        f"New action created: {task_title} (assigned to {assigned_to})",
                        get_current_user()
                    )
                    st.rerun()
                else:
                    st.error("❌ Error creating action. Please try again.")
            else:
                st.error("❌ Please fill in all required fields (*)")


def show_stakeholder_management():
    """Manage stakeholder contacts and groups"""
    st.markdown("### Stakeholder Management")
    
    # Stakeholder directory
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT stakeholder_type, assigned_to
                FROM stakeholder_actions
                ORDER BY stakeholder_type, assigned_to
            """)
            stakeholders = cursor.fetchall()
    except Exception as e:
        st.error(f"Error retrieving stakeholders: {str(e)}")
        stakeholders = []
    
    if stakeholders:
        # Group by stakeholder type
        stakeholder_groups = {}
        for stakeholder in stakeholders:
            group = stakeholder['stakeholder_type']
            if group not in stakeholder_groups:
                stakeholder_groups[group] = []
            stakeholder_groups[group].append(stakeholder['assigned_to'])
        
        for group, members in stakeholder_groups.items():
            with st.expander(f"{group} ({len(members)} members)", expanded=False):
                for member in sorted(set(members)):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"👤 {member}")
                    with col2:
                        # Get active task count for this stakeholder
                        try:
                            with get_db_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    SELECT COUNT(*) as active_count
                                    FROM stakeholder_actions
                                    WHERE assigned_to = ? AND status != 'Completed'
                                """, (member,))
                                count = cursor.fetchone()['active_count']
                                st.write(f"Active Tasks: {count}")
                        except:
                            st.write("Active Tasks: N/A")
                    
                    with col3:
                        if st.button(f"📧 Contact", key=f"contact_{group}_{member}"):
                            st.info(f"Contact functionality for {member}")


def show_progress_tracking():
    """Track progress across all actions and cases"""
    st.markdown("### Progress Tracking")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_case = st.text_input("Filter by Case ID", placeholder="e.g., CASE-2025-001")
    with col2:
        filter_stakeholder = st.selectbox("Filter by Stakeholder Type", [
            "All",
            "Internal - Operations",
            "Internal - Legal",
            "Internal - Compliance", 
            "External - Customer",
            "External - Regulatory"
        ])
    with col3:
        filter_status = st.selectbox("Filter by Status", [
            "All", "Pending", "In Progress", "Completed", "Overdue"
        ])
    
    # Get filtered data
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build query based on filters
            where_conditions = []
            params = []
            
            if filter_case:
                where_conditions.append("sa.case_id LIKE ?")
                params.append(f"%{filter_case}%")
            
            if filter_stakeholder != "All":
                where_conditions.append("sa.stakeholder_type = ?")
                params.append(filter_stakeholder)
            
            if filter_status != "All":
                if filter_status == "Overdue":
                    where_conditions.append("sa.due_date < date('now') AND sa.status != 'Completed'")
                else:
                    where_conditions.append("sa.status = ?")
                    params.append(filter_status)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            cursor.execute(f"""
                SELECT sa.*, c.customer_name, c.case_type
                FROM stakeholder_actions sa
                LEFT JOIN cases c ON sa.case_id = c.case_id
                WHERE {where_clause}
                ORDER BY sa.due_date ASC, sa.priority DESC
            """, params)
            
            filtered_actions = cursor.fetchall()
            
    except Exception as e:
        st.error(f"Error retrieving actions: {str(e)}")
        filtered_actions = []
    
    if filtered_actions:
        st.markdown(f"### Found {len(filtered_actions)} Actions")
        
        # Convert to DataFrame for better display
        actions_df = pd.DataFrame([dict(action) for action in filtered_actions])
        
        # Display key columns
        display_columns = [
            'case_id', 'task_title', 'stakeholder_type', 'assigned_to', 
            'priority', 'status', 'due_date', 'created_by'
        ]
        
        st.dataframe(
            actions_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Progress summary
        status_summary = actions_df['status'].value_counts()
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Status Distribution")
            for status, count in status_summary.items():
                st.write(f"**{status}:** {count}")
        
        with col2:
            st.markdown("#### Priority Distribution") 
            priority_summary = actions_df['priority'].value_counts()
            for priority, count in priority_summary.items():
                st.write(f"**{priority}:** {count}")
    
    else:
        st.info("📭 No actions found matching the selected filters")


def show_action_reports():
    """Generate reports on stakeholder actions and performance"""
    st.markdown("### Action Reports & Analytics")
    
    # Report type selection
    report_type = st.selectbox("Select Report Type", [
        "Stakeholder Performance",
        "Case Action Summary", 
        "Overdue Tasks Report",
        "Workload Distribution",
        "Task Type Analysis"
    ])
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To Date", value=date.today())
    
    if st.button("📊 Generate Report", use_container_width=True):
        generate_stakeholder_report(report_type, start_date, end_date)


def save_stakeholder_action(action_data):
    """Save stakeholder action to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create stakeholder_actions table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholder_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    task_title TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    assigned_to TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    description TEXT NOT NULL,
                    expected_outcome TEXT,
                    due_date DATE NOT NULL,
                    estimated_hours REAL,
                    actual_hours REAL DEFAULT 0,
                    dependency_on TEXT,
                    special_instructions TEXT,
                    resources_needed TEXT,
                    status TEXT DEFAULT 'Pending',
                    progress_percentage INTEGER DEFAULT 0,
                    created_by TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME NULL
                )
            """)
            
            # Insert action
            cursor.execute("""
                INSERT INTO stakeholder_actions (
                    case_id, task_title, task_type, stakeholder_type, assigned_to,
                    priority, description, expected_outcome, due_date, estimated_hours,
                    dependency_on, special_instructions, resources_needed, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action_data['case_id'], action_data['task_title'], action_data['task_type'],
                action_data['stakeholder_type'], action_data['assigned_to'], action_data['priority'],
                action_data['description'], action_data['expected_outcome'], action_data['due_date'],
                action_data['estimated_hours'], action_data['dependency_on'], 
                action_data['special_instructions'], action_data['resources_needed'],
                action_data['created_by']
            ))
            
            conn.commit()
            return cursor.lastrowid
            
    except Exception as e:
        st.error(f"Error saving action: {str(e)}")
        return None


def update_action_status(action_id):
    """Update action status"""
    st.info("Status update functionality will be implemented with detailed progress tracking")


def complete_action(action_id):
    """Mark action as completed"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE stakeholder_actions 
                SET status = 'Completed', completed_at = ?, progress_percentage = 100
                WHERE id = ?
            """, (datetime.now(), action_id))
            conn.commit()
            st.success("Action marked as completed!")
    except Exception as e:
        st.error(f"Error completing action: {str(e)}")


def send_stakeholder_notifications(action_id, stakeholders, action_data):
    """Send notifications to stakeholders"""
    # This would integrate with email/SMS services
    pass


def generate_stakeholder_report(report_type, start_date, end_date):
    """Generate stakeholder performance reports"""
    st.info(f"Generating {report_type} report for period {start_date} to {end_date}")
    # Report generation logic would be implemented here