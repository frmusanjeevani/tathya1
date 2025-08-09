import sqlite3
from datetime import datetime
from database import get_db_connection, log_audit

# Import internal fraud functions
from models_internal_fraud import (
    create_internal_fraud_case, 
    get_internal_fraud_cases, 
    get_internal_fraud_case_by_id,
    update_internal_fraud_case,
    update_internal_fraud_case_status,
    get_internal_fraud_case_statistics
)

def create_simplified_case(case_data):
    """Create a simplified case record with only basic information"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create simplified cases table with dynamic case details fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases_simplified (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    referred_by TEXT NOT NULL,
                    case_type TEXT NOT NULL,
                    case_date DATE NOT NULL,
                    case_description TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    status TEXT DEFAULT 'Registered',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Fraud Suspect fields
                    suspected_fraud_modus_operandi TEXT,
                    source_of_suspicion TEXT,
                    initial_loss_estimate TEXT,
                    
                    -- Customer Complaint fields
                    complaint_nature TEXT,
                    customer_statement_summary TEXT,
                    date_of_incident TEXT,
                    
                    -- Internal Escalation fields
                    escalation_source TEXT,
                    escalation_reason TEXT,
                    related_department TEXT,
                    
                    -- Legal Referral fields
                    law_enforcement_agency TEXT,
                    fir_case_number TEXT,
                    date_of_referral TEXT,
                    
                    -- Credential Misuse fields
                    type_of_credentials_misused TEXT,
                    method_of_compromise TEXT,
                    date_detected TEXT,
                    
                    -- Branch Escalation fields
                    branch_name_code TEXT,
                    escalation_trigger TEXT,
                    responsible_officer TEXT,
                    
                    -- Third-Party Alert fields
                    source_entity TEXT,
                    alert_type TEXT,
                    date_of_alert TEXT,
                    
                    -- Social Media Flag fields
                    platform TEXT,
                    post_content_link TEXT,
                    date_posted TEXT,
                    
                    -- Call Center Escalation fields
                    call_id_reference TEXT,
                    -- escalation_reason already defined above
                    date_of_call TEXT,
                    
                    -- Audit Observation fields
                    audit_type TEXT,
                    observation_summary TEXT,
                    audit_date TEXT,
                    
                    -- EWS Early Warning Signal fields
                    signal_type TEXT,
                    trigger_source TEXT,
                    observation_date TEXT,
                    
                    -- Other (Specify) fields
                    description TEXT,
                    source TEXT,
                    date_noted TEXT
                )
            ''')
            
            # Build dynamic insert query based on case_data keys
            base_fields = ['case_id', 'category', 'referred_by', 'case_type', 'case_date', 
                          'case_description', 'created_by', 'created_at', 'status']
            
            # Add case details fields that exist in case_data
            detail_fields = [
                'suspected_fraud_modus_operandi', 'source_of_suspicion', 'initial_loss_estimate',
                'complaint_nature', 'customer_statement_summary', 'date_of_incident',
                'escalation_source', 'escalation_reason', 'related_department',
                'law_enforcement_agency', 'fir_case_number', 'date_of_referral',
                'type_of_credentials_misused', 'method_of_compromise', 'date_detected',
                'branch_name_code', 'escalation_trigger', 'responsible_officer',
                'source_entity', 'alert_type', 'date_of_alert',
                'platform', 'post_content_link', 'date_posted',
                'call_id_reference', 'date_of_call',
                'audit_type', 'observation_summary', 'audit_date',
                'signal_type', 'trigger_source', 'observation_date',
                'description', 'source', 'date_noted'
            ]
            
            all_fields = base_fields.copy()
            values = [
                case_data['case_id'], case_data['category'], case_data['referred_by'],
                case_data['case_type'], case_data['case_date'], case_data['case_description'],
                case_data['created_by'], case_data['created_at'], case_data['status']
            ]
            
            # Add case detail values
            for field in detail_fields:
                all_fields.append(field)
                values.append(case_data.get(field, None))
            
            placeholders = ', '.join(['?'] * len(all_fields))
            fields_str = ', '.join(all_fields)
            
            # Insert the case with dynamic fields
            cursor.execute(f'''
                INSERT INTO cases_simplified ({fields_str}) VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            
            # Log audit trail
            log_audit(
                case_data['case_id'], 
                "Case Registered", 
                f"Simplified case entry by {case_data['created_by']}", 
                case_data['created_by']
            )
            
            return True
            
    except Exception as e:
        import streamlit as st
        st.error(f"Database error: {str(e)}")
        return False

def get_user_by_username(username):
    """Get user by username"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
        return cursor.fetchone()

def get_user_role(username):
    """Get user role"""
    user = get_user_by_username(username)
    return user["role"] if user else None

def create_case(case_data, created_by):
    """Create a new case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if case_id already exists
        cursor.execute("SELECT COUNT(*) FROM cases WHERE case_id = ?", (case_data["case_id"],))
        if cursor.fetchone()[0] > 0:
            return False, "Case ID already exists"
        
        # Handle case data with comprehensive demographics
        cursor.execute('''
            INSERT INTO cases (case_id, lan, case_type, product, region, referred_by, 
                             case_description, case_date, created_by, status,
                             customer_name, customer_dob, customer_pan, customer_aadhaar,
                             customer_mobile, customer_email, customer_address_full,
                             customer_occupation, customer_income, customer_cibil_score,
                             customer_relationship_status, branch_location, loan_amount, disbursement_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case_data["case_id"],
            case_data["lan"],
            case_data["case_type"],
            case_data["product"],
            case_data["region"],
            case_data["referred_by"],
            case_data["case_description"],
            case_data["case_date"],
            created_by,
            case_data.get("status", "Draft"),
            case_data.get("customer_name", ""),
            case_data.get("customer_dob", ""),
            case_data.get("customer_pan", ""),
            case_data.get("customer_aadhaar", ""),
            case_data.get("customer_mobile", ""),
            case_data.get("customer_email", ""),
            case_data.get("customer_address_full", ""),
            case_data.get("customer_occupation", ""),
            case_data.get("customer_income", ""),
            case_data.get("customer_cibil_score", 0),
            case_data.get("customer_relationship_status", ""),
            case_data.get("branch_location", ""),
            case_data.get("loan_amount", 0),
            case_data.get("disbursement_date", "")
        ))
        
        conn.commit()
        
        # Log audit
        log_audit(case_data["case_id"], "Case Created", f"Case created with status: {case_data.get('status', 'Draft')}", created_by)
        
        return True, "Case created successfully"

def get_cases_by_status(status=None, created_by=None):
    """Get cases by status and/or creator from cases_simplified table"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Query cases_simplified table (where Case Entry data is stored)
            query = "SELECT * FROM cases_simplified"
            params = []
            conditions = []
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if created_by:
                conditions.append("created_by = ?")
                params.append(created_by)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            cases = []
            for row in rows:
                case_dict = dict(zip(columns, row))
                cases.append(case_dict)
            
            return cases
            
    except Exception as e:
        print(f"Error getting cases by status: {e}")
        return []

def get_case_by_id(case_id):
    """Get case by case_id from cases_simplified table"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cases_simplified WHERE case_id = ?", (case_id,))
            
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            
            if row:
                return dict(zip(columns, row))
            return None
            
    except Exception as e:
        print(f"Error getting case by ID: {e}")
        return None

def update_case_status(case_id, new_status, updated_by, comments=None):
    """Update case status in cases_simplified table"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Update case status in cases_simplified table
            cursor.execute('''
                UPDATE cases_simplified 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE case_id = ?
            ''', (new_status, case_id))
            
            conn.commit()
            
            # Log audit
            log_audit(
                user_id=updated_by,
                action=f"Status updated to {new_status}",
                table_name="cases_simplified",
                record_id=case_id
            )
            
            return True
            
    except Exception as e:
        print(f"Error updating case status: {e}")
        return False

def get_case_comments(case_id):
    """Get comments for a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM case_comments 
            WHERE case_id = ? 
            ORDER BY created_at DESC
        ''', (case_id,))
        return cursor.fetchall()

def add_case_comment(case_id, comment, comment_type, created_by):
    """Add comment to a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO case_comments (case_id, comment, comment_type, created_by)
            VALUES (?, ?, ?, ?)
        ''', (case_id, comment, comment_type, created_by))
        conn.commit()
        
        # Log audit
        log_audit(case_id, "Comment Added", f"Comment type: {comment_type}", created_by)

def get_case_documents(case_id):
    """Get documents for a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM documents 
            WHERE case_id = ? 
            ORDER BY uploaded_at DESC
        ''', (case_id,))
        return cursor.fetchall()

def add_case_document(case_id, filename, original_filename, file_path, file_size, uploaded_by):
    """Add document to a case"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO documents (case_id, filename, original_filename, file_path, file_size, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (case_id, filename, original_filename, file_path, file_size, uploaded_by))
        conn.commit()
        
        # Log audit
        log_audit(case_id, "Document Added", f"Document: {original_filename}", uploaded_by)

def get_case_statistics():
    """Get case statistics for dashboard"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        stats = {}
        
        # Total cases
        cursor.execute("SELECT COUNT(*) FROM cases")
        stats["total_cases"] = cursor.fetchone()[0]
        
        # Cases by status
        cursor.execute("SELECT status, COUNT(*) FROM cases GROUP BY status")
        stats["by_status"] = dict(cursor.fetchall())
        
        # Cases by region
        cursor.execute("SELECT region, COUNT(*) FROM cases GROUP BY region")
        stats["by_region"] = dict(cursor.fetchall())
        
        # Cases by product
        cursor.execute("SELECT product, COUNT(*) FROM cases GROUP BY product")
        stats["by_product"] = dict(cursor.fetchall())
        
        # Recent cases
        cursor.execute("SELECT * FROM cases ORDER BY created_at DESC LIMIT 10")
        stats["recent_cases"] = cursor.fetchall()
        
        return stats

def get_audit_logs(case_id=None, limit=100):
    """Get audit logs"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if case_id:
            cursor.execute('''
                SELECT * FROM audit_logs 
                WHERE case_id = ? 
                ORDER BY performed_at DESC 
                LIMIT ?
            ''', (case_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM audit_logs 
                ORDER BY performed_at DESC 
                LIMIT ?
            ''', (limit,))
        
        return cursor.fetchall()



def search_cases(search_term, filters=None):
    """Search cases with optional filters"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM cases 
            WHERE (case_id LIKE ? OR lan LIKE ? OR case_description LIKE ?)
        '''
        params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
        
        if filters:
            if filters.get("status"):
                query += " AND status = ?"
                params.append(filters["status"])
            
            if filters.get("region"):
                query += " AND region = ?"
                params.append(filters["region"])
            
            if filters.get("product"):
                query += " AND product = ?"
                params.append(filters["product"])
            
            if filters.get("date_from"):
                query += " AND case_date >= ?"
                params.append(filters["date_from"])
            
            if filters.get("date_to"):
                query += " AND case_date <= ?"
                params.append(filters["date_to"])
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        return cursor.fetchall()


# Achievement and Gamification Functions
def get_user_achievements(username):
    """Get user's earned achievements"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT ua.*, a.name, a.description, a.icon, a.tier, a.points, a.category
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.username = ?
                ORDER BY ua.earned_at DESC
            ''', (username,))
            return cursor.fetchall()
        except:
            return []  # Return empty if tables don't exist yet

def get_user_stats(username):
    """Get comprehensive user statistics for gamification"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        stats = {}
        
        # Total cases handled
        cursor.execute('''
            SELECT COUNT(*) FROM cases 
            WHERE created_by = ? OR reviewed_by = ? OR approved_by = ? OR closed_by = ?
        ''', (username, username, username, username))
        stats["total_cases"] = cursor.fetchone()[0]
        
        # Cases this month
        cursor.execute('''
            SELECT COUNT(*) FROM cases 
            WHERE (created_by = ? OR reviewed_by = ? OR approved_by = ? OR closed_by = ?)
            AND created_at >= date('now', 'start of month')
        ''', (username, username, username, username))
        stats["cases_this_month"] = cursor.fetchone()[0]
        
        # Mock values for demo
        stats["avg_resolution_time"] = 2.3
        stats["quality_score"] = 85.0
        stats["quality_improvement"] = 2.5
        
        # Achievement points
        try:
            cursor.execute('''
                SELECT COALESCE(SUM(a.points), 0) FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.username = ?
            ''', (username,))
            stats["total_points"] = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COALESCE(SUM(a.points), 0) FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.username = ? AND ua.earned_at >= date('now', '-7 days')
            ''', (username,))
            stats["points_this_week"] = cursor.fetchone()[0]
        except:
            stats["total_points"] = 0
            stats["points_this_week"] = 0
        
        return stats

def get_leaderboard(type_filter="overall_points"):
    """Get leaderboard data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            if type_filter == "overall_points":
                cursor.execute('''
                    SELECT u.username, u.name, u.team,
                           COALESCE(SUM(a.points), 0) as score
                    FROM users u
                    LEFT JOIN user_achievements ua ON u.username = ua.username
                    LEFT JOIN achievements a ON ua.achievement_id = a.id
                    WHERE u.is_active = 1
                    GROUP BY u.username, u.name, u.team
                    ORDER BY score DESC
                    LIMIT 20
                ''')
            elif type_filter == "cases_this_month":
                cursor.execute('''
                    SELECT u.username, u.name, u.team,
                           COUNT(c.id) as score
                    FROM users u
                    LEFT JOIN cases c ON (u.username = c.created_by OR u.username = c.reviewed_by 
                                        OR u.username = c.approved_by OR u.username = c.closed_by)
                    AND c.created_at >= date('now', 'start of month')
                    WHERE u.is_active = 1
                    GROUP BY u.username, u.name, u.team
                    ORDER BY score DESC
                    LIMIT 20
                ''')
            else:
                cursor.execute('''
                    SELECT u.username, u.name, u.team,
                           COUNT(c.id) as score
                    FROM users u
                    LEFT JOIN cases c ON (u.username = c.created_by OR u.username = c.reviewed_by 
                                        OR u.username = c.approved_by OR u.username = c.closed_by)
                    WHERE u.is_active = 1
                    GROUP BY u.username, u.name, u.team
                    ORDER BY score DESC
                    LIMIT 20
                ''')
            
            return cursor.fetchall()
        except:
            return []

def check_and_award_achievements(username, action_type, case_data=None):
    """Check if user qualifies for new achievements and award them"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user's current stats
            stats = get_user_stats(username)
            
            # Check various achievement conditions
            achievements_to_award = []
            
            # First Case achievement
            if stats["total_cases"] == 1:
                achievements_to_award.append("first_case")
            
            # Case milestones
            case_milestones = [5, 10, 25, 50, 100]
            if stats["total_cases"] in case_milestones:
                achievements_to_award.append(f"cases_{stats['total_cases']}")
            
            # Award achievements
            for achievement_id in achievements_to_award:
                award_achievement(username, achievement_id, conn)
    except:
        pass  # Fail silently if achievement system not ready

def award_achievement(username, achievement_id, conn=None):
    """Award an achievement to a user"""
    try:
        if conn is None:
            with get_db_connection() as conn:
                _award_achievement_internal(username, achievement_id, conn)
        else:
            _award_achievement_internal(username, achievement_id, conn)
    except:
        pass

def _award_achievement_internal(username, achievement_id, conn):
    """Internal function to award achievement"""
    cursor = conn.cursor()
    
    # Check if user already has this achievement
    cursor.execute('''
        SELECT COUNT(*) FROM user_achievements 
        WHERE username = ? AND achievement_id = ?
    ''', (username, achievement_id))
    
    if cursor.fetchone()[0] == 0:
        # Award the achievement
        cursor.execute('''
            INSERT INTO user_achievements (username, achievement_id, earned_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (username, achievement_id))
        conn.commit()



# Hook achievements to case creation and updates  
def trigger_achievement_check(username, action_type, case_data=None):
    """Trigger achievement checking after case actions"""
    try:
        check_and_award_achievements(username, action_type, case_data)
    except:
        pass  # Fail silently

def create_case_allocation(allocation_data):
    """Create a new case allocation record"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create case allocations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS case_allocations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    investigation_type TEXT NOT NULL,
                    assigned_investigator TEXT NOT NULL,
                    priority_level TEXT NOT NULL,
                    expected_completion DATE,
                    allocation_notes TEXT,
                    special_instructions TEXT,
                    product TEXT,
                    branch_location TEXT,
                    region TEXT,
                    lan TEXT,
                    customer_name TEXT,
                    loan_amount REAL,
                    disbursement_date DATE,
                    date_of_birth DATE,
                    pan TEXT,
                    mobile_number TEXT,
                    email_id TEXT,
                    aadhaar_number TEXT,
                    relationship_status TEXT,
                    complete_address TEXT,
                    occupation TEXT,
                    monthly_income_range TEXT,
                    cibil_score INTEGER,
                    gst_business_proof TEXT,
                    pan_card_image TEXT,
                    aadhaar_card_image TEXT,
                    customer_photo TEXT,
                    supporting_documents TEXT,
                    created_by TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    status TEXT DEFAULT 'Allocated',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert allocation data
            cursor.execute('''
                INSERT INTO case_allocations (
                    case_id, investigation_type, assigned_investigator, priority_level,
                    expected_completion, allocation_notes, special_instructions, product,
                    branch_location, region, lan, customer_name, loan_amount,
                    disbursement_date, date_of_birth, pan, mobile_number, email_id,
                    aadhaar_number, relationship_status, complete_address, occupation,
                    monthly_income_range, cibil_score, gst_business_proof, pan_card_image,
                    aadhaar_card_image, customer_photo, supporting_documents,
                    created_by, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                allocation_data['case_id'], allocation_data['investigation_type'],
                allocation_data['assigned_investigator'], allocation_data['priority_level'],
                allocation_data['expected_completion'], allocation_data['allocation_notes'],
                allocation_data['special_instructions'], allocation_data['product'],
                allocation_data['branch_location'], allocation_data['region'],
                allocation_data['lan'], allocation_data['customer_name'],
                allocation_data['loan_amount'], allocation_data['disbursement_date'],
                allocation_data['date_of_birth'], allocation_data['pan'],
                allocation_data['mobile_number'], allocation_data['email_id'],
                allocation_data['aadhaar_number'], allocation_data['relationship_status'],
                allocation_data['complete_address'], allocation_data['occupation'],
                allocation_data['monthly_income_range'], allocation_data['cibil_score'],
                allocation_data.get('gst_business_proof'), allocation_data.get('pan_card_image'),
                allocation_data.get('aadhaar_card_image'), allocation_data.get('customer_photo'),
                allocation_data.get('supporting_documents', ''), allocation_data['created_by'],
                allocation_data['created_at'], allocation_data['status']
            ))
            
            # Update original case status to 'Allocated'
            cursor.execute('''
                UPDATE cases_simplified SET status = 'Allocated', updated_at = ? WHERE case_id = ?
            ''', (datetime.now().isoformat(), allocation_data['case_id']))
            
            conn.commit()
            
            # Log audit
            log_audit(
                user_id=allocation_data['created_by'],
                action=f"Created case allocation for {allocation_data['case_id']}",
                table_name="case_allocations",
                record_id=allocation_data['case_id']
            )
            
            return True
            
    except Exception as e:
        print(f"Error creating case allocation: {e}")
        return False

def get_case_allocations():
    """Get all case allocations"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM case_allocations ORDER BY created_at DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            cases = []
            for row in rows:
                case_dict = dict(zip(columns, row))
                cases.append(case_dict)
            
            return cases
            
    except Exception as e:
        print(f"Error getting case allocations: {e}")
        return []

