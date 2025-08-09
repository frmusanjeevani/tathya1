import sqlite3
import os
import hashlib
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = "case_management.db"

def get_password_hash(password):
    """Generate password hash"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_account_request(request_data):
    """Create a new account request"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO account_requests 
            (full_name, email, phone, organization, designation, requested_role, 
             business_justification, manager_name, manager_email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_data['full_name'],
            request_data['email'],
            request_data.get('phone'),
            request_data.get('organization'),
            request_data.get('designation'),
            request_data['requested_role'],
            request_data['business_justification'],
            request_data.get('manager_name'),
            request_data.get('manager_email')
        ))
        conn.commit()
        return cursor.lastrowid

def get_account_requests(status=None):
    """Get account requests"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute('SELECT * FROM account_requests WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM account_requests ORDER BY created_at DESC')
        return cursor.fetchall()

def update_account_request_status(request_id, status, admin_notes=None, processed_by=None):
    """Update account request status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE account_requests 
            SET status = ?, admin_notes = ?, processed_by = ?, processed_at = ?
            WHERE id = ?
        ''', (status, admin_notes, processed_by, datetime.now(), request_id))
        conn.commit()
        return cursor.rowcount > 0

@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database with tables and default data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT,
                name TEXT,
                team TEXT,
                functional_designation TEXT,
                referred_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create interaction_requests table for workflow communication
        cursor.execute('''
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
        ''')
        
        # Account requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                organization TEXT,
                designation TEXT,
                requested_role TEXT NOT NULL,
                business_justification TEXT NOT NULL,
                manager_name TEXT,
                manager_email TEXT,
                status TEXT DEFAULT 'Pending',
                admin_notes TEXT,
                processed_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        ''')
        
        # Cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE NOT NULL,
                lan TEXT NOT NULL,
                case_type TEXT NOT NULL,
                product TEXT NOT NULL,
                region TEXT NOT NULL,
                referred_by TEXT NOT NULL,
                case_description TEXT NOT NULL,
                case_date DATE NOT NULL,
                status TEXT DEFAULT 'Draft',
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by TEXT,
                reviewed_at TIMESTAMP,
                approved_by TEXT,
                approved_at TIMESTAMP,
                legal_reviewed_by TEXT,
                legal_reviewed_at TIMESTAMP,
                closed_by TEXT,
                closed_at TIMESTAMP,
                closure_reason TEXT,
                -- SLA tracking
                fmr1_due_date DATE,
                fmr1_submitted_date DATE,
                fmr3_due_date DATE,
                fmr3_submitted_date DATE,
                document_retention_date DATE,
                sla_status TEXT DEFAULT 'On Track',
                -- Demographics
                customer_name TEXT,
                customer_dob DATE,
                customer_pan TEXT,
                customer_address TEXT,
                customer_mobile TEXT,
                customer_email TEXT,
                branch_location TEXT,
                loan_amount DECIMAL(15,2),
                disbursement_date DATE,
                repayment_status TEXT,
                linked_loan_accounts TEXT,
                customer_type TEXT DEFAULT 'Individual',
                kyc_status TEXT DEFAULT 'Pending',
                risk_category TEXT,
                case_source TEXT,
                FOREIGN KEY (created_by) REFERENCES users (username)
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                uploaded_by TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (uploaded_by) REFERENCES users (username)
            )
        ''')
        
        # Audit logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                action TEXT NOT NULL,
                details TEXT,
                performed_by TEXT NOT NULL,
                performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (performed_by) REFERENCES users (username)
            )
        ''')
        
        # Case actions table for Case Action workflow
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_details TEXT,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (created_by) REFERENCES users (username)
            )
        ''')
        
        # Case documents table for document uploads
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_type TEXT,
                uploaded_by TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (uploaded_by) REFERENCES users (username)
            )
        ''')
        
        # Case comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                comment TEXT NOT NULL,
                comment_type TEXT DEFAULT 'General',
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (created_by) REFERENCES users (username)
            )
        ''')
        
        # Investigation details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investigation_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                investigation_type TEXT,
                investigation_status TEXT DEFAULT 'In Progress',
                field_verification_status TEXT DEFAULT 'Pending',
                document_verification_status TEXT DEFAULT 'Pending',
                reference_verification_status TEXT DEFAULT 'Pending',
                technical_verification_status TEXT DEFAULT 'Pending',
                investigation_findings TEXT,
                risk_assessment TEXT,
                fraud_indicators TEXT,
                recommendations TEXT,
                evidence_collected TEXT,
                investigation_date DATE,
                completed_date DATE,
                investigator_name TEXT,
                supervisor_name TEXT,
                final_conclusion TEXT,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (case_id),
                FOREIGN KEY (created_by) REFERENCES users (username)
            )
        ''')
        
        # Case assignments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                assignment_types TEXT,
                assignee TEXT,
                tat TEXT,
                assigned_by TEXT,
                assignment_date TEXT,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (case_id) REFERENCES cases (case_id)
            )
        ''')
        
        # Agency responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agency_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                agency_name TEXT,
                investigation_status TEXT,
                investigation_summary TEXT,
                risk_assessment TEXT,
                recommendation TEXT,
                additional_comments TEXT,
                verification_details TEXT,
                response_routing TEXT,
                submitted_by TEXT,
                submission_date TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (case_id)
            )
        ''')
        
        conn.commit()
        
        # Add new columns to existing users table if they don't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN team TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN functional_designation TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN referred_by TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN all_roles_access BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add missing columns to investigation_details table if they don't exist
        try:
            cursor.execute("ALTER TABLE investigation_details ADD COLUMN investigation_findings TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE investigation_details ADD COLUMN recommendations TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE investigation_details ADD COLUMN risk_assessment TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Achievement tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                tier TEXT NOT NULL DEFAULT 'bronze',
                points INTEGER NOT NULL DEFAULT 10,
                category TEXT NOT NULL DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users (username),
                FOREIGN KEY (achievement_id) REFERENCES achievements (id),
                UNIQUE(username, achievement_id)
            )
        ''')
        
        conn.commit()
        
        # Clean up old test users first
        test_users_to_remove = ["initiator", "reviewer", "approver", "legal", "closure", "actioner"]
        for user_id in test_users_to_remove:
            cursor.execute("DELETE FROM users WHERE username = ?", (user_id,))
        
        # Insert default users if they don't exist (all real users from the master list)
        default_users = [
            ("admin", "admin123", "Admin", "admin@abcl.com", "System Administrator", "IT", "System Admin", "Technical Team")
        ]
        
        for username, password, role, email, name, team, designation, referred_by in default_users:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] == 0:
                password_hash = get_password_hash(password)
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, email, name, team, 
                                     functional_designation, referred_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, role, email, name, team, designation, referred_by))
        
        # Initialize default achievements
        default_achievements = [
            ("first_case", "First Case", "Handle your first case", "🎯", "bronze", 10, "Getting Started"),
            ("cases_5", "Case Handler", "Successfully handle 5 cases", "📝", "bronze", 25, "Progress"),
            ("cases_10", "Case Expert", "Successfully handle 10 cases", "🏅", "silver", 50, "Progress"),
            ("cases_25", "Case Master", "Successfully handle 25 cases", "🎖️", "silver", 100, "Progress"),
            ("cases_50", "Case Champion", "Successfully handle 50 cases", "🏆", "gold", 250, "Progress"),
            ("cases_100", "Case Legend", "Successfully handle 100 cases", "👑", "gold", 500, "Progress"),
            ("speed_resolver", "Speed Demon", "Resolve cases quickly", "⚡", "silver", 75, "Performance"),
            ("quality_expert", "Quality Master", "Maintain high quality standards", "💎", "gold", 200, "Performance"),
            ("team_player", "Team Player", "Collaborate effectively", "🤝", "bronze", 30, "Collaboration"),
            ("mentor", "Mentor", "Help train new team members", "🎓", "gold", 150, "Leadership")
        ]
        
        for achievement_id, name, description, icon, tier, points, category in default_achievements:
            cursor.execute("SELECT COUNT(*) FROM achievements WHERE id = ?", (achievement_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO achievements (id, name, description, icon, tier, points, category) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (achievement_id, name, description, icon, tier, points, category))
        
        conn.commit()

def log_audit(case_id, action, details, performed_by):
    """Log audit trail"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (case_id, action, details, performed_by) VALUES (?, ?, ?, ?)",
            (case_id, action, details, performed_by)
        )
        conn.commit()

def update_case_status(case_id, new_status, updated_by, comments=None):
    """Update case status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update case status
        update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [new_status]
        
        # Add specific reviewer fields based on status
        if new_status == "Under Review":
            update_fields.append("reviewed_by = ?")
            update_fields.append("reviewed_at = CURRENT_TIMESTAMP")
            params.append(updated_by)
        elif new_status == "Approved":
            update_fields.append("approved_by = ?")
            update_fields.append("approved_at = CURRENT_TIMESTAMP")
            params.append(updated_by)
        elif new_status == "Legal Review":
            update_fields.append("legal_reviewed_by = ?")
            update_fields.append("legal_reviewed_at = CURRENT_TIMESTAMP")
            params.append(updated_by)
        elif new_status == "Closed":
            update_fields.append("closed_by = ?")
            update_fields.append("closed_at = CURRENT_TIMESTAMP")
            params.append(updated_by)
        
        params.append(case_id)
        
        cursor.execute(f'''
            UPDATE cases 
            SET {", ".join(update_fields)}
            WHERE case_id = ?
        ''', params)
        
        # Add comment if provided
        if comments:
            cursor.execute('''
                INSERT INTO case_comments (case_id, comment, comment_type, created_by)
                VALUES (?, ?, ?, ?)
            ''', (case_id, comments, f"Status Change to {new_status}", updated_by))
        
        conn.commit()
        
        # Log audit
        log_audit(case_id, "Status Update", f"Status changed to: {new_status}", updated_by)
        
        return True

def add_case_comment(case_id, comment, created_by, comment_type="General"):
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

def get_investigator_names():
    """Get all active user names for investigator assignment dropdowns"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM users 
            WHERE is_active = 1 AND name IS NOT NULL AND name != ''
            ORDER BY name ASC
        ''')
        users = cursor.fetchall()
        return [user['name'] for user in users]
