import streamlit as st
import os
from datetime import datetime

def show():
    """Download page for Excel workflow analysis"""
    
    st.markdown("""
    <div style='
        text-align: center;
        margin: 15px 0 25px 0;
        padding: 10px;
    '>
        <h1 style='
            font-size: 2.4rem;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 8px;
            letter-spacing: 0.5px;
            font-family: "Segoe UI", Arial, sans-serif;
        '>📊 Excel Workflow Analysis</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Download Complete Workflow Analysis")
    
    # Find the Excel file
    excel_files = [f for f in os.listdir('.') if f.startswith('Tathya_Case_Management_Workflow_Analysis') and f.endswith('.xlsx')]
    
    if excel_files:
        latest_file = sorted(excel_files)[-1]  # Get the most recent file
        
        st.markdown(f"""
        **📋 Complete Tathya Case Management System Analysis**
        
        This Excel file contains comprehensive analysis of all workflow stages:
        
        **📑 12 Worksheets Included:**
        1. **Case Entry/Registration** - 28 fields across 5 sections
        2. **Case Allocation** - 7 fields for case assignment
        3. **Investigation Module** - 27 fields for comprehensive investigation
        4. **Primary Review** - 6 fields for quality assessment
        5. **Final Review** - 8 fields with AI enhancement
        6. **Approver Modules** - 6 fields for dual approval process
        7. **Legal Panel** - 7 fields for legal actions
        8. **Closure/Actioner** - 11 fields for case closure
        9. **Database Tables** - 8 tables summary
        10. **File Formats** - Supported document types
        11. **Status Transitions** - Complete workflow flow
        12. **Summary Statistics** - Project overview
        
        **🔍 Analysis Details:**
        - **150+ Fields** documented with specifications
        - **9 Major Workflow Stages** with complete field mapping
        - **Field Types, Validation Rules, and Requirements** for each field
        - **Document Upload Specifications** for all modules
        - **Database Schema Overview** with 8 main tables
        - **AI Integration Features** and interaction channels
        
        **📈 Ready for:**
        - Excel analysis and pivot tables
        - Data import/export planning
        - Development specifications
        - Business requirement documentation
        
        **File:** `{latest_file}`  
        **Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """)
        
        # Read file for download
        try:
            with open(latest_file, 'rb') as file:
                file_data = file.read()
            
            st.download_button(
                label="📥 Download Excel Analysis",
                data=file_data,
                file_name=latest_file,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                type="primary"
            )
            
            st.success("✅ Excel file ready for download!")
            
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.warning("⚠️ Excel file not found. Please generate the analysis first.")
        
        if st.button("🔄 Generate Excel Analysis"):
            try:
                # Import and run the generator
                import sys
                sys.path.append('.')
                from generate_excel_workflow import create_workflow_excel
                
                filename = create_workflow_excel()
                st.success(f"✅ Excel file generated: {filename}")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating Excel file: {e}")
    
    st.markdown("---")
    st.markdown("""
    **📝 Usage Instructions:**
    1. Click the download button above
    2. Open in Microsoft Excel, Google Sheets, or LibreOffice Calc
    3. Each worksheet contains detailed field specifications
    4. Use for development planning, data modeling, or business analysis
    
    **💡 Pro Tip:** The Excel file is structured for easy filtering, sorting, and pivot table creation for advanced analysis.
    """)

if __name__ == "__main__":
    show()