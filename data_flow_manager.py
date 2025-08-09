"""
Data Flow Manager for ensuring seamless data flow between workflow stages
Handles case transitions and data inheritance between stages
"""
import streamlit as st
from database import get_db_connection, log_audit
import json
from datetime import datetime

def get_case_flow_data(case_id):
    """Get comprehensive flow data for a case from all previous stages"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get base case data
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        case_data = cursor.fetchone()
        
        if not case_data:
            return None
        
        # Get all comments/updates in chronological order
        cursor.execute("""
            SELECT * FROM case_comments 
            WHERE case_id = ? 
            ORDER BY created_at ASC
        """, (case_id,))
        comments = cursor.fetchall()
        
        # Get audit trail
        cursor.execute("""
            SELECT * FROM audit_logs 
            WHERE case_id = ? 
            ORDER BY created_at ASC
        """, (case_id,))
        audit_logs = cursor.fetchall()
        
        # Get uploaded documents
        cursor.execute("""
            SELECT * FROM uploaded_files 
            WHERE case_id = ? 
            ORDER BY uploaded_at ASC
        """, (case_id,))
        documents = cursor.fetchall()
        
        # Organize flow data by stages
        flow_data = {
            'case_basic': dict(case_data) if case_data else {},
            'comments': [dict(comment) for comment in comments],
            'audit_trail': [dict(log) for log in audit_logs],
            'documents': [dict(doc) for doc in documents],
            'stage_data': {}
        }
        
        # Extract stage-specific data from comments
        for comment in comments:
            if comment['comment'].startswith('STAGE_DATA:'):
                try:
                    stage_info = json.loads(comment['comment'][11:])  # Remove 'STAGE_DATA:' prefix
                    stage_name = stage_info.get('stage', 'Unknown')
                    flow_data['stage_data'][stage_name] = stage_info
                except json.JSONDecodeError:
                    continue
        
        return flow_data

def save_stage_data(case_id, stage_name, stage_data, user):
    """Save stage-specific data that will flow to next stages"""
    from database import add_case_comment
    
    # Create stage data package
    stage_package = {
        'stage': stage_name,
        'timestamp': datetime.now().isoformat(),
        'user': user,
        'data': stage_data
    }
    
    # Save as special comment
    stage_data_json = json.dumps(stage_package)
    add_case_comment(case_id, f"STAGE_DATA:{stage_data_json}", user)
    
    # Log audit
    log_audit(case_id, f"{stage_name} Data Saved", f"Stage data saved by {user}", user)

def get_previous_stage_data(case_id, stage_names):
    """Get data from specific previous stages"""
    flow_data = get_case_flow_data(case_id)
    
    if not flow_data:
        return {}
    
    previous_data = {}
    for stage_name in stage_names:
        if stage_name in flow_data['stage_data']:
            previous_data[stage_name] = flow_data['stage_data'][stage_name]['data']
    
    return previous_data

def update_case_with_flow_data(case_id, new_data, stage_name, user):
    """Update case with new data while preserving flow history"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build dynamic update query based on provided data
        update_fields = []
        values = []
        
        for key, value in new_data.items():
            if key != 'case_id':  # Don't update case_id
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        if update_fields:
            # Add updated_by and updated_at
            update_fields.extend(["updated_by = ?", "updated_at = CURRENT_TIMESTAMP"])
            values.extend([user])
            values.append(case_id)  # For WHERE clause
            
            query = f"UPDATE cases SET {', '.join(update_fields)} WHERE case_id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            # Save stage data for flow
            save_stage_data(case_id, stage_name, new_data, user)
            
            # Log audit
            log_audit(case_id, f"{stage_name} Update", f"Case updated by {user}", user)

def show_previous_stage_summary(case_id, current_stage):
    """Display summary of data from previous stages"""
    flow_data = get_case_flow_data(case_id)
    
    if not flow_data:
        return
    
    st.markdown("### 📊 Previous Stage Summary")
    
    # Show stage progression
    if flow_data['stage_data']:
        stages_completed = list(flow_data['stage_data'].keys())
        st.markdown(f"**Completed Stages:** {' → '.join(stages_completed)} → **{current_stage}**")
        
        # Show key data from each stage
        for stage_name, stage_info in flow_data['stage_data'].items():
            with st.expander(f"📋 {stage_name} Data", expanded=False):
                stage_data = stage_info.get('data', {})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Completed By:** {stage_info.get('user', 'Unknown')}")
                    st.markdown(f"**Date:** {stage_info.get('timestamp', 'Unknown')}")
                
                with col2:
                    if stage_data:
                        st.markdown("**Key Data:**")
                        for key, value in stage_data.items():
                            if isinstance(value, (str, int, float)) and len(str(value)) < 100:
                                st.markdown(f"• **{key.replace('_', ' ').title()}:** {value}")

def create_stage_data_form(case_id, stage_name, current_user, form_fields):
    """Create a standardized form for capturing stage data"""
    st.markdown(f"### 📝 {stage_name} Data Entry")
    
    with st.form(f"{stage_name}_data_form_{case_id}"):
        form_data = {}
        
        # Dynamic form fields based on stage requirements
        for field_name, field_config in form_fields.items():
            field_type = field_config.get('type', 'text')
            label = field_config.get('label', field_name.replace('_', ' ').title())
            default = field_config.get('default', '')
            options = field_config.get('options', [])
            
            if field_type == 'text':
                form_data[field_name] = st.text_input(label, value=default, key=f"{stage_name}_{field_name}_{case_id}")
            elif field_type == 'textarea':
                form_data[field_name] = st.text_area(label, value=default, key=f"{stage_name}_{field_name}_{case_id}")
            elif field_type == 'select':
                form_data[field_name] = st.selectbox(label, options, key=f"{stage_name}_{field_name}_{case_id}")
            elif field_type == 'multiselect':
                form_data[field_name] = st.multiselect(label, options, key=f"{stage_name}_{field_name}_{case_id}")
            elif field_type == 'number':
                form_data[field_name] = st.number_input(label, value=default, key=f"{stage_name}_{field_name}_{case_id}")
            elif field_type == 'date':
                form_data[field_name] = st.date_input(label, key=f"{stage_name}_{field_name}_{case_id}")
        
        if st.form_submit_button(f"💾 Save {stage_name} Data", type="primary"):
            # Filter out empty values
            clean_data = {k: v for k, v in form_data.items() if v not in [None, '', []]}
            
            if clean_data:
                update_case_with_flow_data(case_id, clean_data, stage_name, current_user)
                st.success(f"✅ {stage_name} data saved successfully!")
                st.rerun()
            else:
                st.error("Please fill in at least one field")
        
        return form_data

def get_workflow_progression(case_id):
    """Get the workflow progression for a case"""
    flow_data = get_case_flow_data(case_id)
    
    if not flow_data:
        return []
    
    # Standard workflow stages
    all_stages = [
        "Case Registration",
        "Case Allocation", 
        "Agency Investigation",
        "Regional Investigation",
        "Primary Review",
        "Approver 1",
        "Approver 2", 
        "Final Review",
        "Legal Review",
        "Closure"
    ]
    
    # Get completed stages
    completed_stages = list(flow_data['stage_data'].keys())
    current_status = flow_data['case_basic'].get('status', 'Unknown')
    
    # Map status to stage
    status_to_stage = {
        'Draft': 'Case Registration',
        'Submitted': 'Case Allocation',
        'Agency Investigation': 'Agency Investigation', 
        'Regional Investigation': 'Regional Investigation',
        'Under Investigation': 'Case Allocation',
        'Primary Review': 'Primary Review',
        'Under Review': 'Primary Review',
        'Approved': 'Approver 1',
        'Approver 2': 'Approver 2',
        'Final Review': 'Final Review', 
        'Legal Review': 'Legal Review',
        'Closed': 'Closure'
    }
    
    current_stage = status_to_stage.get(current_status, current_status)
    
    return {
        'all_stages': all_stages,
        'completed_stages': completed_stages,
        'current_stage': current_stage,
        'current_status': current_status
    }

def show_workflow_progress_tracker(case_id):
    """Display workflow progress tracker"""
    progression = get_workflow_progression(case_id)
    
    st.markdown("### 🔄 Workflow Progress Tracker")
    
    # Create progress visualization
    progress_html = "<div style='display: flex; align-items: center; margin: 20px 0;'>"
    
    for i, stage in enumerate(progression['all_stages']):
        # Determine stage status
        if stage in progression['completed_stages']:
            status_icon = "✅"
            status_color = "#28a745"
        elif stage == progression['current_stage']:
            status_icon = "🔄"
            status_color = "#007bff"
        else:
            status_icon = "⏳"
            status_color = "#6c757d"
        
        # Add stage
        progress_html += f"""
        <div style='
            text-align: center; 
            margin: 0 10px;
            padding: 10px;
            border-radius: 8px;
            background: {"#e8f5e8" if stage in progression['completed_stages'] else "#e3f2fd" if stage == progression['current_stage'] else "#f8f9fa"};
            border: 2px solid {status_color};
            min-width: 120px;
        '>
            <div style='font-size: 20px; margin-bottom: 5px;'>{status_icon}</div>
            <div style='font-size: 12px; font-weight: bold; color: {status_color};'>{stage}</div>
        </div>
        """
        
        # Add arrow (except for last stage)
        if i < len(progression['all_stages']) - 1:
            progress_html += f"""
            <div style='
                font-size: 20px; 
                color: {"#28a745" if stage in progression['completed_stages'] else "#6c757d"};
                margin: 0 5px;
            '>→</div>
            """
    
    progress_html += "</div>"
    
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # Show current status
    st.markdown(f"**Current Status:** {progression['current_status']} | **Current Stage:** {progression['current_stage']}")