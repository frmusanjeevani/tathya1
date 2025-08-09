"""
Interaction Channels System for handling communication between workflow stages
Allows stages to request missing information and receive responses
"""
import streamlit as st
from database import get_db_connection, add_case_comment, log_audit
from datetime import datetime

def create_interaction_request(case_id, from_stage, to_stage, request_type, message, requested_by):
    """Create an interaction request between workflow stages"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create interaction requests table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interaction_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                from_stage TEXT NOT NULL,
                to_stage TEXT NOT NULL,
                request_type TEXT NOT NULL,
                message TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                response TEXT,
                responded_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                responded_at TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id)
            )
        """)
        
        # Insert interaction request
        cursor.execute("""
            INSERT INTO interaction_requests 
            (case_id, from_stage, to_stage, request_type, message, requested_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (case_id, from_stage, to_stage, request_type, message, requested_by))
        
        conn.commit()
        
        # Add case comment
        add_case_comment(case_id, f"INTERACTION REQUEST from {from_stage} to {to_stage}: {message}", requested_by)
        
        # Log audit
        log_audit(case_id, "Interaction Request Created", 
                 f"{from_stage} requested {request_type} from {to_stage}", requested_by)
        
        return cursor.lastrowid

def get_pending_requests_for_stage(stage_name):
    """Get all pending interaction requests for a specific stage"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ir.*, c.customer_name, c.case_type, c.product, c.region
            FROM interaction_requests ir
            JOIN cases c ON ir.case_id = c.case_id
            WHERE ir.to_stage = ? AND ir.status = 'Pending'
            ORDER BY ir.created_at DESC
        """, (stage_name,))
        return cursor.fetchall()

def respond_to_interaction_request(request_id, response, responded_by):
    """Respond to an interaction request"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get request details
        cursor.execute("SELECT * FROM interaction_requests WHERE id = ?", (request_id,))
        request = cursor.fetchone()
        
        if not request:
            return False, "Request not found"
        
        # Update request with response
        cursor.execute("""
            UPDATE interaction_requests 
            SET response = ?, responded_by = ?, responded_at = CURRENT_TIMESTAMP, status = 'Responded'
            WHERE id = ?
        """, (response, responded_by, request_id))
        
        conn.commit()
        
        # Add case comment
        add_case_comment(request['case_id'], 
                        f"INTERACTION RESPONSE from {request['to_stage']} to {request['from_stage']}: {response}", 
                        responded_by)
        
        # Log audit
        log_audit(request['case_id'], "Interaction Request Responded", 
                 f"{request['to_stage']} responded to {request['from_stage']} request", responded_by)
        
        return True, "Response recorded successfully"

def show_interaction_requests_section(stage_name, current_user):
    """Display interaction requests section for a workflow stage"""
    st.markdown("### 💬 Interaction Requests")
    
    # Get pending requests for this stage
    pending_requests = get_pending_requests_for_stage(stage_name)
    
    if pending_requests:
        st.markdown(f"**{len(pending_requests)} pending request(s) for {stage_name}:**")
        
        for request in pending_requests:
            with st.expander(f"🔔 Request from {request['from_stage']} - Case: {request['case_id']}", expanded=False):
                st.markdown(f"""
                **Case:** {request['case_id']} - {request['customer_name']} ({request['case_type']})  
                **Product:** {request['product']} | **Region:** {request['region']}  
                **Request Type:** {request['request_type']}  
                **Requested By:** {request['requested_by']}  
                **Date:** {request['created_at']}  
                
                **Request Message:**
                """)
                
                st.markdown(f"""
                <div style='
                    background: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 8px 0;
                    font-size: 16px;
                    color: #333;
                '>
                    {request['message']}
                </div>
                """, unsafe_allow_html=True)
                
                # Response form
                with st.form(f"response_form_{request['id']}"):
                    response_text = st.text_area(
                        "Your Response", 
                        placeholder="Provide the requested information or clarification...",
                        height=100,
                        key=f"response_{request['id']}"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("📤 Send Response", type="primary"):
                            if response_text:
                                success, message = respond_to_interaction_request(
                                    request['id'], response_text, current_user
                                )
                                if success:
                                    st.success("✅ Response sent successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {message}")
                            else:
                                st.error("Please provide a response")
                    
                    with col2:
                        if st.form_submit_button("📋 Mark as Reviewed"):
                            # Mark as reviewed without response
                            with get_db_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    UPDATE interaction_requests 
                                    SET status = 'Reviewed', responded_by = ?, responded_at = CURRENT_TIMESTAMP
                                    WHERE id = ?
                                """, (current_user, request['id']))
                                conn.commit()
                            
                            st.success("✅ Marked as reviewed!")
                            st.rerun()
    else:
        st.info("📭 No pending interaction requests")

def create_interaction_request_form(case_id, current_stage, current_user):
    """Create form for making interaction requests"""
    st.markdown("### 🔄 Request Missing Information")
    st.markdown("*Use this section to request additional information from previous or related stages*")
    
    with st.form(f"interaction_request_{case_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Determine available stages based on current stage
            available_stages = get_available_stages_for_request(current_stage)
            to_stage = st.selectbox("Request From Stage", available_stages, 
                                  key=f"to_stage_{case_id}")
        
        with col2:
            request_type = st.selectbox("Request Type", 
                ["Missing Documents", "Clarification Needed", "Additional Information", 
                 "Verification Required", "Update Required", "Other"], 
                key=f"request_type_{case_id}")
        
        request_message = st.text_area("Request Details", 
            placeholder="Describe what information or clarification you need...",
            height=100, key=f"request_message_{case_id}")
        
        if st.form_submit_button("📤 Send Request", type="primary"):
            if to_stage and request_message:
                request_id = create_interaction_request(
                    case_id, current_stage, to_stage, request_type, request_message, current_user
                )
                st.success(f"✅ Request sent to {to_stage}! (Request ID: {request_id})")
                st.rerun()
            else:
                st.error("Please fill in all fields")

def get_available_stages_for_request(current_stage):
    """Get list of stages that can be requested from based on current stage"""
    stage_flow = {
        "Case Allocation": ["Case Registration"],
        "Agency Investigation": ["Case Allocation"],
        "Regional Investigation": ["Case Allocation"],
        "Primary Review": ["Case Allocation", "Agency Investigation", "Regional Investigation"],
        "Approver 1": ["Primary Review", "Regional Investigation", "Agency Investigation"],
        "Approver 2": ["Approver 1", "Primary Review"],
        "Final Review": ["Approver 2", "Approver 1"],
        "Legal Review": ["Final Review", "Primary Review"],
        "Closure": ["Legal Review", "Final Review"]
    }
    
    return stage_flow.get(current_stage, ["Case Registration", "Case Allocation"])

def get_interaction_history(case_id):
    """Get interaction history for a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM interaction_requests 
            WHERE case_id = ? 
            ORDER BY created_at DESC
        """, (case_id,))
        return cursor.fetchall()

def show_interaction_history(case_id):
    """Display interaction history for a case"""
    history = get_interaction_history(case_id)
    
    if history:
        st.markdown("### 📋 Interaction History")
        
        for interaction in history:
            status_color = "🟢" if interaction['status'] == 'Responded' else "🟡" if interaction['status'] == 'Reviewed' else "🔴"
            
            with st.expander(f"{status_color} {interaction['from_stage']} → {interaction['to_stage']} ({interaction['request_type']})", expanded=False):
                st.markdown(f"""
                **Request:** {interaction['message']}  
                **Requested By:** {interaction['requested_by']}  
                **Date:** {interaction['created_at']}  
                **Status:** {interaction['status']}
                """)
                
                if interaction['response']:
                    st.markdown(f"""
                    **Response:** {interaction['response']}  
                    **Responded By:** {interaction['responded_by']}  
                    **Response Date:** {interaction['responded_at']}
                    """)
    else:
        st.info("📭 No interaction history for this case")