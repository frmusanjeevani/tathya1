"""Initialize database tables for Case Allocation system"""
import sqlite3
from database import get_db_connection

def initialize_case_allocation_table():
    """Create case_allocations table if it doesn't exist"""
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
            
            conn.commit()
            print("Case allocations table created successfully")
            return True
            
    except Exception as e:
        print(f"Error creating case allocations table: {e}")
        return False

if __name__ == "__main__":
    initialize_case_allocation_table()