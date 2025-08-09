"""Check existing data in the system"""
import sqlite3
from database import get_db_connection

def check_existing_data():
    """Check what cases exist and their status"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            print("=== Checking Cases Simplified Table ===")
            cursor.execute("SELECT case_id, status, category, case_type FROM cases_simplified ORDER BY created_at DESC LIMIT 10")
            cases = cursor.fetchall()
            
            if cases:
                print("Available cases:")
                for case in cases:
                    print(f"  Case ID: {case[0]}, Status: {case[1]}, Category: {case[2]}, Type: {case[3]}")
            else:
                print("No cases found in cases_simplified table")
            
            print("\n=== Checking Case Allocations Table ===")
            cursor.execute("SELECT case_id, assigned_investigator, priority_level FROM case_allocations ORDER BY created_at DESC LIMIT 5")
            allocations = cursor.fetchall()
            
            if allocations:
                print("Existing allocations:")
                for alloc in allocations:
                    print(f"  Case ID: {alloc[0]}, Investigator: {alloc[1]}, Priority: {alloc[2]}")
            else:
                print("No allocations found")
            
            print("\n=== Creating Sample Case for Testing ===")
            # Create a sample case if none exist
            cursor.execute("SELECT COUNT(*) FROM cases_simplified")
            case_count = cursor.fetchone()[0]
            
            if case_count == 0:
                sample_case_data = {
                    'case_id': 'TC001',
                    'category': 'Fraud Suspect',
                    'referred_by': 'Internal Team',
                    'case_type': 'Customer Complaint',
                    'case_date': '2025-01-08',
                    'case_description': 'Sample case for testing Case Allocation system',
                    'created_by': 'admin',
                    'created_at': '2025-01-08 10:00:00',
                    'status': 'Registered'
                }
                
                cursor.execute('''
                    INSERT INTO cases_simplified (
                        case_id, category, referred_by, case_type, case_date,
                        case_description, created_by, created_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sample_case_data['case_id'], sample_case_data['category'],
                    sample_case_data['referred_by'], sample_case_data['case_type'],
                    sample_case_data['case_date'], sample_case_data['case_description'],
                    sample_case_data['created_by'], sample_case_data['created_at'],
                    sample_case_data['status']
                ))
                
                conn.commit()
                print(f"Created sample case: {sample_case_data['case_id']}")
                
    except Exception as e:
        print(f"Error checking data: {e}")

if __name__ == "__main__":
    check_existing_data()