import streamlit as st
from models import get_case_by_id
from utils import format_datetime

def show_workflow_progress(case_id):
    """Display animated workflow progress tracker"""
    
    # Get case details
    case = get_case_by_id(case_id)
    if not case:
        return
    
    current_status = case['status']
    
    # Define workflow steps following proper sequence
    workflow_steps = [
        {"name": "Case Entry", "status": "Draft", "icon": "📝", "description": "Case created and documented"},
        {"name": "Allocator", "status": "Allocated", "icon": "📋", "description": "Case allocated for investigation"},
        {"name": "Investigator", "status": "Under Investigation", "icon": "🔬", "description": "Detailed investigation and verification"},
        {"name": "Primary Reviewer", "status": "Under Review", "icon": "🔍", "description": "Primary review of investigation"},
        {"name": "Approver 1", "status": "Approved", "icon": "✅", "description": "First level approval"},
        {"name": "Approver 2", "status": "Second Approval", "icon": "✅", "description": "Second level approval"},
        {"name": "Final Reviewer", "status": "Final Review", "icon": "🎯", "description": "Final review before legal"},
        {"name": "Legal (SCN)", "status": "Legal Review", "icon": "⚖️", "description": "Legal review and SCN processing"},
        {"name": "Actioner", "status": "Closed", "icon": "🔒", "description": "Final action and case closure"}
    ]
    
    # CSS for animated progress tracker
    st.markdown("""
    <style>
    .progress-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    .progress-header {
        text-align: center;
        margin-bottom: 30px;
        color: #0066cc;
        font-weight: 600;
        font-size: 1.3rem;
    }
    
    .workflow-tracker {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        margin: 30px 0;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .progress-line {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #e9ecef 0%, #e9ecef 100%);
        z-index: 1;
        border-radius: 2px;
    }
    
    .progress-line-active {
        position: absolute;
        top: 50%;
        left: 0;
        height: 4px;
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        z-index: 2;
        border-radius: 2px;
        transition: width 1s ease-in-out;
        animation: progressPulse 2s infinite;
    }
    
    @keyframes progressPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
        50% { box-shadow: 0 0 0 8px rgba(40, 167, 69, 0); }
    }
    
    .step-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 3;
        min-width: 120px;
        margin: 0 5px;
    }
    
    .step-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .step-circle.completed {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        animation: stepBounce 0.6s ease-out;
        transform: scale(1.1);
    }
    
    .step-circle.current {
        background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
        color: white;
        animation: currentPulse 2s infinite, stepGlow 1.5s ease-in-out infinite alternate;
        transform: scale(1.15);
        box-shadow: 0 0 20px rgba(0, 102, 204, 0.6);
    }
    
    .step-circle.pending {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #6c757d;
        border: 2px solid #dee2e6;
    }
    
    .step-circle.rejected {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        color: white;
        animation: stepShake 0.5s ease-in-out;
    }
    
    @keyframes stepBounce {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1.1); }
    }
    
    @keyframes currentPulse {
        0%, 100% { transform: scale(1.15); }
        50% { transform: scale(1.25); }
    }
    
    @keyframes stepGlow {
        0% { box-shadow: 0 0 20px rgba(0, 102, 204, 0.6); }
        100% { box-shadow: 0 0 30px rgba(0, 102, 204, 0.9); }
    }
    
    @keyframes stepShake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .step-label {
        text-align: center;
        font-size: 0.85rem;
        font-weight: 600;
        color: #495057;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    
    .step-description {
        text-align: center;
        font-size: 0.75rem;
        color: #6c757d;
        line-height: 1.3;
        max-width: 100px;
    }
    
    .step-date {
        text-align: center;
        font-size: 0.7rem;
        color: #868e96;
        margin-top: 3px;
        font-style: italic;
    }
    
    .current-status-badge {
        display: inline-block;
        background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 10px 0;
        animation: badgePulse 2s infinite;
    }
    
    @keyframes badgePulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .progress-stats {
        display: flex;
        justify-content: space-around;
        margin-top: 25px;
        padding: 15px;
        background: rgba(0, 102, 204, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(0, 102, 204, 0.1);
    }
    
    .stat-item {
        text-align: center;
        flex: 1;
    }
    
    .stat-value {
        font-size: 1.4rem;
        font-weight: bold;
        color: #0066cc;
        display: block;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    @media (max-width: 768px) {
        .workflow-tracker {
            flex-direction: column;
            gap: 20px;
        }
        .progress-line, .progress-line-active {
            display: none;
        }
        .step-container {
            width: 100%;
            max-width: 200px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Calculate progress
    completed_steps = 0
    current_step_index = 0
    
    # Map current status to step (updated for proper workflow sequence)
    status_to_step = {
        "Draft": 0,
        "Submitted": 0,  # Still at case entry until allocated
        "Allocated": 1,
        "Under Investigation": 2,
        "Under Review": 3,
        "Approved": 4,
        "Second Approval": 5,
        "Final Review": 6,
        "Legal Review": 7,
        "Closed": 8,
        "Rejected": -1  # Special case for rejected
    }
    
    if current_status == "Rejected":
        current_step_index = -1
    else:
        current_step_index = status_to_step.get(current_status, 0)
        completed_steps = max(0, current_step_index)
    
    # Calculate progress percentage (fixed for proper workflow calculation)
    if current_status == "Rejected":
        progress_percentage = 0
    else:
        # For 8-step workflow, calculate based on actual completed steps
        total_steps = len(workflow_steps)
        if completed_steps >= total_steps:
            progress_percentage = 100
        else:
            progress_percentage = (completed_steps / (total_steps - 1)) * 100
    
    # Display progress tracker
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-header">
            📊 Workflow Progress Tracker - Case {case_id}
        </div>
        
        <div style="text-align: center;">
            <span class="current-status-badge">
                Current Status: {current_status}
            </span>
        </div>
        
        <div class="workflow-tracker">
            <div class="progress-line"></div>
            <div class="progress-line-active" style="width: {progress_percentage}%;"></div>
    """, unsafe_allow_html=True)
    
    # Generate step HTML
    for i, step in enumerate(workflow_steps):
        # Determine step state
        if current_status == "Rejected" and i > 0:
            step_class = "rejected" if i == current_step_index else "pending"
        elif i < current_step_index:
            step_class = "completed"
        elif i == current_step_index:
            step_class = "current"
        else:
            step_class = "pending"
        
        # Get step date if available
        step_date = ""
        if step_class == "completed" or step_class == "current":
            if step["status"] == case["status"]:
                # Handle both dict and sqlite3.Row objects
                try:
                    if hasattr(case, 'keys'):  # sqlite3.Row object
                        updated_at = case["updated_at"] if "updated_at" in case.keys() else None
                        created_at = case["created_at"] if "created_at" in case.keys() else None
                        step_date = format_datetime(updated_at or created_at or "")
                    else:  # dict object
                        step_date = format_datetime(case.get("updated_at", case.get("created_at", "")))
                except:
                    step_date = ""
        
        st.markdown(f"""
            <div class="step-container">
                <div class="step-circle {step_class}">
                    {step["icon"]}
                </div>
                <div class="step-label">{step["name"]}</div>
                <div class="step-description">{step["description"]}</div>
                {f'<div class="step-date">{step_date}</div>' if step_date else ''}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        
        <div class="progress-stats">
            <div class="stat-item">
                <span class="stat-value">{}</span>
                <div class="stat-label">Steps Completed</div>
            </div>
            <div class="stat-item">
                <span class="stat-value">{:.0f}%</span>
                <div class="stat-label">Progress</div>
            </div>
            <div class="stat-item">
                <span class="stat-value">{}</span>
                <div class="stat-label">Remaining Steps</div>
            </div>
        </div>
    </div>
    """.format(
        max(0, completed_steps),
        progress_percentage,
        max(0, len(workflow_steps) - completed_steps - 1)
    ), unsafe_allow_html=True)

def show_mini_progress(case_status):
    """Display mini progress indicator for tables"""
    
    # Define status colors and progress
    status_config = {
        "Draft": {"color": "#6c757d", "progress": 10, "icon": "📝"},
        "Submitted": {"color": "#ffc107", "progress": 25, "icon": "📤"},
        "Under Review": {"color": "#17a2b8", "progress": 35, "icon": "🔍"},
        "Under Investigation": {"color": "#fd7e14", "progress": 50, "icon": "🔬"},
        "Final Review": {"color": "#6f42c1", "progress": 70, "icon": "🎯"},
        "Approved": {"color": "#28a745", "progress": 85, "icon": "✅"},
        "Legal Review": {"color": "#dc3545", "progress": 90, "icon": "⚖️"},
        "Closed": {"color": "#343a40", "progress": 100, "icon": "🔒"},
        "Rejected": {"color": "#dc3545", "progress": 0, "icon": "❌"}
    }
    
    config = status_config.get(case_status, {"color": "#6c757d", "progress": 0, "icon": "❓"})
    
    return f"""
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.1rem;">{config["icon"]}</span>
        <div style="flex: 1; background: #e9ecef; height: 6px; border-radius: 3px; min-width: 80px;">
            <div style="background: {config["color"]}; height: 100%; width: {config["progress"]}%; border-radius: 3px; transition: width 0.3s ease;"></div>
        </div>
        <span style="font-size: 0.75rem; color: {config["color"]}; font-weight: 600; min-width: 30px;">{config["progress"]}%</span>
    </div>
    """