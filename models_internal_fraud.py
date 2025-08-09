import sqlite3
from datetime import datetime
from database import get_db_connection, log_audit

def create_internal_fraud_case(case_data):
    """Create a new internal fraud case record"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create internal fraud cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS internal_fraud_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT UNIQUE NOT NULL,
                    case_type TEXT NOT NULL,
                    detection_date DATE,
                    reported_by TEXT,
                    reporting_channel TEXT,
                    incident_description TEXT,
                    supporting_documents TEXT,
                    allocated_to TEXT,
                    allocation_date DATE,
                    allocation_remarks TEXT,
                    investigation_start_date DATE,
                    investigation_summary TEXT,
                    preliminary_findings TEXT,
                    evidence_collected TEXT,
                    final_reviewer TEXT,
                    reviewer_comments TEXT,
                    approver1_name TEXT,
                    approver1_decision TEXT,
                    approver2_name TEXT,
                    approver2_decision TEXT,
                    code_breach TEXT,
                    code_reference TEXT,
                    primary_closure_remarks TEXT,
                    hr_action TEXT,
                    scn_date DATE,
                    committee_review TEXT,
                    final_closure_date DATE,
                    final_closure_remarks TEXT,
                    created_by TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    status TEXT DEFAULT 'Initiated',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    current_stage TEXT DEFAULT 'Case Initiation',
                    workflow_stage INTEGER DEFAULT 1
                )
            ''')
            
            # Insert internal fraud case data
            cursor.execute('''
                INSERT INTO internal_fraud_cases (
                    case_id, case_type, detection_date, reported_by, reporting_channel,
                    incident_description, supporting_documents, allocated_to, allocation_date,
                    allocation_remarks, investigation_start_date, investigation_summary,
                    preliminary_findings, evidence_collected, final_reviewer, reviewer_comments,
                    approver1_name, approver1_decision, approver2_name, approver2_decision,
                    code_breach, code_reference, primary_closure_remarks, hr_action,
                    scn_date, committee_review, final_closure_date, final_closure_remarks,
                    created_by, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_data['case_id'], case_data['case_type'], case_data['detection_date'],
                case_data['reported_by'], case_data['reporting_channel'],
                case_data['incident_description'], case_data.get('supporting_documents', ''),
                case_data['allocated_to'], case_data['allocation_date'],
                case_data['allocation_remarks'], case_data['investigation_start_date'],
                case_data['investigation_summary'], case_data['preliminary_findings'],
                case_data.get('evidence_collected', ''), case_data['final_reviewer'],
                case_data['reviewer_comments'], case_data['approver1_name'],
                case_data['approver1_decision'], case_data['approver2_name'],
                case_data['approver2_decision'], case_data['code_breach'],
                case_data['code_reference'], case_data['primary_closure_remarks'],
                case_data['hr_action'], case_data['scn_date'], case_data['committee_review'],
                case_data['final_closure_date'], case_data['final_closure_remarks'],
                case_data['created_by'], case_data['created_at'], case_data['status']
            ))
            
            conn.commit()
            
            # Log audit
            log_audit(
                case_id=case_data['case_id'],
                action=f"Created internal fraud case {case_data['case_id']}",
                details="Internal fraud case created successfully",
                performed_by=case_data['created_by']
            )
            
            return True
            
    except Exception as e:
        print(f"Error creating internal fraud case: {e}")
        return False

def get_internal_fraud_cases():
    """Get all internal fraud cases"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM internal_fraud_cases ORDER BY created_at DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            cases = []
            for row in rows:
                case_dict = dict(zip(columns, row))
                cases.append(case_dict)
            
            return cases
            
    except Exception as e:
        print(f"Error getting internal fraud cases: {e}")
        return []

def get_internal_fraud_case_by_id(case_id):
    """Get specific internal fraud case by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM internal_fraud_cases WHERE case_id = ?
            ''', (case_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
    except Exception as e:
        print(f"Error getting internal fraud case by ID: {e}")
        return None

def update_internal_fraud_case(case_id, update_data):
    """Update internal fraud case"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key != 'case_id':  # Don't update case_id
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(case_id)  # For WHERE clause
            
            query = f'''
                UPDATE internal_fraud_cases 
                SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                WHERE case_id = ?
            '''
            
            cursor.execute(query, values)
            conn.commit()
            
            # Log audit
            log_audit(
                case_id=case_id,
                action=f"Updated internal fraud case {case_id}",
                details="Internal fraud case updated successfully",
                performed_by=update_data.get('updated_by', 'system')
            )
            
            return True
            
    except Exception as e:
        print(f"Error updating internal fraud case: {e}")
        return False

def update_internal_fraud_case_status(case_id, new_status, updated_by):
    """Update internal fraud case status"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE internal_fraud_cases 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE case_id = ?
            ''', (new_status, case_id))
            
            conn.commit()
            
            # Log audit
            log_audit(
                case_id=case_id,
                action=f"Status updated to {new_status}",
                details=f"Status changed to {new_status}",
                performed_by=updated_by
            )
            
            return True
            
    except Exception as e:
        print(f"Error updating internal fraud case status: {e}")
        return False

def get_internal_fraud_case_statistics():
    """Get statistics for internal fraud cases"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total cases
            cursor.execute('SELECT COUNT(*) FROM internal_fraud_cases')
            total_cases = cursor.fetchone()[0]
            
            # Cases by status
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM internal_fraud_cases 
                GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # Cases by type
            cursor.execute('''
                SELECT case_type, COUNT(*) as count 
                FROM internal_fraud_cases 
                GROUP BY case_type
            ''')
            type_counts = dict(cursor.fetchall())
            
            # HR actions
            cursor.execute('''
                SELECT hr_action, COUNT(*) as count 
                FROM internal_fraud_cases 
                WHERE hr_action IS NOT NULL AND hr_action != ''
                GROUP BY hr_action
            ''')
            hr_action_counts = dict(cursor.fetchall())
            
            return {
                'total_cases': total_cases,
                'status_distribution': status_counts,
                'type_distribution': type_counts,
                'hr_actions': hr_action_counts
            }
            
    except Exception as e:
        print(f"Error getting internal fraud case statistics: {e}")
        return {
            'total_cases': 0,
            'status_distribution': {},
            'type_distribution': {},
            'hr_actions': {}
        }