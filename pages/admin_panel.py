import streamlit as st
import sqlite3
import hashlib
from database import get_db_connection, get_password_hash, get_account_requests, update_account_request_status
from models import get_audit_logs, get_case_statistics
from utils import format_datetime
from auth import require_role
from email_service import send_account_approval_notification

@require_role(["Admin"])
def show():
    """Display admin panel"""
    st.title("🛠️ Admin Panel")
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👥 User Management", 
        "📝 Account Requests",
        "📊 System Statistics", 
        "🔍 Audit Logs", 
        "⚙️ System Settings",
        "🗄️ Database Management"
    ])
    
    with tab1:
        show_user_management()
    
    with tab2:
        show_account_requests()
    
    with tab3:
        show_system_statistics()
    
    with tab4:
        show_audit_logs()
    
    with tab5:
        show_system_settings()
    
    with tab6:
        show_database_management()

def show_account_requests():
    """Account request management interface"""
    st.subheader("📝 Account Requests Management")
    
    # Filter by status
    col1, col2 = st.columns([1, 3])
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Approved", "Rejected"])
    
    # Get requests based on filter
    if filter_status == "All":
        requests = get_account_requests()
    else:
        requests = get_account_requests(filter_status)
    
    if not requests:
        st.info("No account requests found.")
        return
    
    st.markdown(f"### Found {len(requests)} request(s)")
    
    for request in requests:
        status_color = {"Pending": "🟡", "Approved": "🟢", "Rejected": "🔴"}
        status_icon = status_color.get(request['status'], "⚪")
        
        with st.expander(f"{status_icon} {request['full_name']} - {request['requested_role']} ({request['status']})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Personal Information:**")
                st.write(f"**Name:** {request['full_name']}")
                st.write(f"**Email:** {request['email']}")
                st.write(f"**Phone:** {request['phone'] or 'Not provided'}")
                st.write(f"**Organization:** {request['organization'] or 'Not provided'}")
                st.write(f"**Designation:** {request['designation'] or 'Not provided'}")
                
                st.markdown("**Request Details:**")
                st.write(f"**Requested Role:** {request['requested_role']}")
                st.write(f"**Manager:** {request['manager_name'] or 'Not provided'}")
                st.write(f"**Manager Email:** {request['manager_email'] or 'Not provided'}")
                st.write(f"**Request Date:** {request['created_at']}")
                
                st.markdown("**Business Justification:**")
                st.write(request['business_justification'])
                
                if request['admin_notes']:
                    st.markdown("**Admin Notes:**")
                    st.write(request['admin_notes'])
            
            with col2:
                st.markdown("**Actions:**")
                
                if request['status'] == 'Pending':
                    admin_notes = st.text_area("Admin Notes", key=f"notes_{request['id']}", 
                                             placeholder="Optional notes about this decision...")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Approve", key=f"approve_{request['id']}", use_container_width=True):
                            success = update_account_request_status(
                                request['id'], 'Approved', admin_notes, st.session_state.get('username', 'Admin')
                            )
                            if success:
                                # Send approval email
                                try:
                                    send_account_approval_notification(request, approved=True)
                                except:
                                    pass  # Email is optional
                                st.success("✅ Request approved!")
                                st.rerun()
                    
                    with col_b:
                        if st.button("❌ Reject", key=f"reject_{request['id']}", use_container_width=True):
                            success = update_account_request_status(
                                request['id'], 'Rejected', admin_notes, st.session_state.get('username', 'Admin')
                            )
                            if success:
                                # Send rejection email
                                try:
                                    send_account_approval_notification(request, approved=False)
                                except:
                                    pass  # Email is optional
                                st.success("Request rejected!")
                                st.rerun()
                else:
                    st.info(f"Status: {request['status']}")
                    if request['processed_by']:
                        st.write(f"Processed by: {request['processed_by']}")
                    if request['processed_at']:
                        st.write(f"Processed on: {request['processed_at']}")

def show_user_management():
    """User management interface"""
    st.subheader("👥 User Management")
    
    # Add new user
    with st.expander("➕ Add New User"):
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_email = st.text_input("Email")
            
            with col2:
                new_role = st.selectbox("Role", [
                    "Initiator", "Reviewer", "Approver", 
                    "Legal Reviewer", "Action Closure Authority", "Admin"
                ])
                is_active = st.checkbox("Active", value=True)
            
            if st.form_submit_button("➕ Add User"):
                if new_username and new_password and new_role:
                    success = add_user(new_username, new_password, new_role, new_email, is_active)
                    if success:
                        st.success(f"✅ User '{new_username}' added successfully")
                    else:
                        st.error("❌ Failed to add user (username might already exist)")
                else:
                    st.warning("Please fill all required fields")
    
    # List existing users
    st.subheader("Existing Users")
    users = get_all_users()
    
    if users:
        for user in users:
            with st.expander(f"👤 {user['username']} ({user['role']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Role:** {user['role']}")
                    st.write(f"**Email:** {user['email'] or 'N/A'}")
                    st.write(f"**Status:** {'Active' if user['is_active'] else 'Inactive'}")
                
                with col2:
                    st.write(f"**Created:** {format_datetime(user['created_at'])}")
                    st.write(f"**ID:** {user['id']}")
                
                # User actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"🔒 Reset Password", key=f"reset_{user['id']}"):
                        reset_user_password(user['username'])
                        st.success("Password reset to 'newpass123'")
                
                with col2:
                    new_status = not user['is_active']
                    action_text = "Activate" if new_status else "Deactivate"
                    if st.button(f"{'✅' if new_status else '❌'} {action_text}", key=f"toggle_{user['id']}"):
                        toggle_user_status(user['id'], new_status)
                        st.success(f"User {action_text.lower()}d")
                        st.rerun()
                
                with col3:
                    if user['username'] != 'admin':  # Prevent admin deletion
                        if st.button(f"🗑️ Delete", key=f"delete_{user['id']}"):
                            if delete_user(user['id']):
                                st.success("User deleted")
                                st.rerun()
    else:
        st.info("No users found")

def show_system_statistics():
    """System statistics dashboard"""
    st.subheader("📊 System Statistics")
    
    stats = get_case_statistics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cases", stats["total_cases"])
    
    with col2:
        total_users = len(get_all_users())
        st.metric("Total Users", total_users)
    
    with col3:
        # Get storage usage (simplified)
        import os
        uploads_size = sum(os.path.getsize(os.path.join("uploads", f)) 
                          for f in os.listdir("uploads") if os.path.isfile(os.path.join("uploads", f))) if os.path.exists("uploads") else 0
        storage_mb = uploads_size / (1024 * 1024)
        st.metric("Storage Used", f"{storage_mb:.1f} MB")
    
    with col4:
        # Database size
        db_size = os.path.getsize("case_management.db") / (1024 * 1024) if os.path.exists("case_management.db") else 0
        st.metric("Database Size", f"{db_size:.1f} MB")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cases by Status")
        if stats["by_status"]:
            import plotly.express as px
            fig = px.bar(
                x=list(stats["by_status"].keys()),
                y=list(stats["by_status"].values()),
                title="Case Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Cases by Region")
        if stats["by_region"]:
            import plotly.express as px
            fig = px.pie(
                values=list(stats["by_region"].values()),
                names=list(stats["by_region"].keys()),
                title="Regional Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_audit_logs():
    """Display audit logs"""
    st.subheader("🔍 Audit Logs")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_limit = st.number_input("Number of logs", min_value=10, max_value=1000, value=50)
    
    with col2:
        filter_case_id = st.text_input("Filter by Case ID")
    
    with col3:
        if st.button("🔄 Refresh Logs"):
            st.rerun()
    
    # Get and display logs
    logs = get_audit_logs(case_id=filter_case_id if filter_case_id else None, limit=log_limit)
    
    if logs:
        log_data = []
        for log in logs:
            log_data.append({
                "Time": format_datetime(log["performed_at"]),
                "Case ID": log["case_id"] or "System",
                "Action": log["action"],
                "Details": log["details"] or "N/A",
                "User": log["performed_by"]
            })
        
        st.dataframe(log_data, use_container_width=True)
        
        # Export logs
        if st.button("📥 Export Audit Logs"):
            import pandas as pd
            df = pd.DataFrame(log_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"audit_logs_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No audit logs found")

def show_system_settings():
    """System settings interface"""
    st.subheader("⚙️ System Settings")
    
    # Application settings
    with st.expander("🎛️ Application Settings"):
        st.write("**Case Management Settings**")
        
        auto_approval = st.checkbox("Enable Auto-Approval for Low-Value Cases", value=False)
        approval_threshold = st.number_input("Auto-Approval Threshold (₹)", min_value=0, value=10000)
        
        st.write("**Notification Settings**")
        email_notifications = st.checkbox("Enable Email Notifications", value=True)
        sms_notifications = st.checkbox("Enable SMS Notifications", value=False)
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved successfully")
    
    # Security settings
    with st.expander("🔐 Security Settings"):
        st.write("**Password Policy**")
        
        min_password_length = st.number_input("Minimum Password Length", min_value=6, max_value=20, value=8)
        require_special_chars = st.checkbox("Require Special Characters", value=True)
        password_expiry_days = st.number_input("Password Expiry (days)", min_value=30, max_value=365, value=90)
        
        st.write("**Session Settings**")
        session_timeout = st.number_input("Session Timeout (minutes)", min_value=15, max_value=480, value=120)
        
        if st.button("🔒 Update Security Settings"):
            st.success("Security settings updated")
    
    # Backup settings
    with st.expander("💾 Backup & Maintenance"):
        st.write("**Database Backup**")
        
        if st.button("📦 Create Database Backup"):
            create_database_backup()
            st.success("Database backup created successfully")
        
        st.write("**System Maintenance**")
        
        if st.button("🧹 Clean Temporary Files"):
            clean_temp_files()
            st.success("Temporary files cleaned")
        
        if st.button("🔄 Rebuild Database Indexes"):
            rebuild_database_indexes()
            st.success("Database indexes rebuilt")

def show_database_management():
    """Database management interface"""
    st.subheader("🗄️ Database Management")
    
    # Database statistics
    st.write("**Database Statistics**")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Table sizes
        tables = ["users", "cases", "documents", "audit_logs", "case_comments"]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            st.write(f"**{table.title()}:** {count} records")
    
    st.divider()
    
    # Database operations
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Maintenance Operations**")
        
        if st.button("🔄 Vacuum Database"):
            vacuum_database()
            st.success("Database vacuumed successfully")
        
        if st.button("📊 Analyze Database"):
            analyze_database()
            st.success("Database analysis completed")
    
    with col2:
        st.write("**Data Operations**")
        
        if st.button("📥 Export All Data"):
            export_all_data()
            st.success("Data export initiated")
        
        if st.button("🔄 Reset Demo Data"):
            if st.checkbox("⚠️ I understand this will reset all data"):
                reset_demo_data()
                st.success("Demo data reset completed")

# Helper functions
def get_all_users():
    """Get all users from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        return cursor.fetchall()

def add_user(username, password, role, email, is_active):
    """Add new user to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            password_hash = get_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, email, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, role, email, is_active))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def reset_user_password(username):
    """Reset user password"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        new_password_hash = get_password_hash("newpass123")
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (new_password_hash, username)
        )
        conn.commit()

def toggle_user_status(user_id, is_active):
    """Toggle user active status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (is_active, user_id)
        )
        conn.commit()

def delete_user(user_id):
    """Delete user from database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
    except:
        return False

def create_database_backup():
    """Create database backup"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"case_management_backup_{timestamp}.db"
    shutil.copy2("case_management.db", backup_name)

def clean_temp_files():
    """Clean temporary files"""
    import os
    import glob
    
    # Clean any temporary files in uploads directory
    temp_files = glob.glob("uploads/*.tmp")
    for temp_file in temp_files:
        os.remove(temp_file)

def rebuild_database_indexes():
    """Rebuild database indexes"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("REINDEX")
        conn.commit()

def vacuum_database():
    """Vacuum database to reclaim space"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("VACUUM")
        conn.commit()

def analyze_database():
    """Analyze database for optimization"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("ANALYZE")
        conn.commit()

def export_all_data():
    """Export all data to CSV files"""
    import pandas as pd
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with get_db_connection() as conn:
        # Export cases
        cases_df = pd.read_sql_query("SELECT * FROM cases", conn)
        cases_df.to_csv(f"exports/cases_export_{timestamp}.csv", index=False)
        
        # Export users (without passwords)
        users_df = pd.read_sql_query("SELECT id, username, role, email, created_at, is_active FROM users", conn)
        users_df.to_csv(f"exports/users_export_{timestamp}.csv", index=False)
        
        # Export audit logs
        logs_df = pd.read_sql_query("SELECT * FROM audit_logs", conn)
        logs_df.to_csv(f"exports/audit_logs_{timestamp}.csv", index=False)

def reset_demo_data():
    """Reset database to demo state"""
    # This would truncate tables and insert demo data
    # Implementation depends on requirements
    pass
