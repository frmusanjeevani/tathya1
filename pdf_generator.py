import io
import streamlit as st
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from models import get_case_comments

def generate_final_review_pdf(case_details):
    """Generate comprehensive PDF report for Final Review Panel"""
    
    # Create a buffer to store PDF
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for elements
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue,
        borderWidth=1,
        borderColor=colors.darkblue,
        borderPadding=5,
        backColor=colors.lightgrey
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Title
    elements.append(Paragraph("FINAL REVIEW REPORT", title_style))
    elements.append(Paragraph("Tathya Case Management System", styles['Normal']))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Case Information Section
    elements.append(Paragraph("CASE INFORMATION", header_style))
    
    case_data = [
        ['Case ID:', case_details.get('case_id', 'N/A')],
        ['LAN:', case_details.get('lan', 'N/A')],
        ['Customer Name:', case_details.get('customer_name', 'N/A')],
        ['Case Type:', case_details.get('case_type', 'N/A')],
        ['Product:', case_details.get('product', 'N/A')],
        ['Region:', case_details.get('region', 'N/A')],
        ['Status:', case_details.get('status', 'N/A')],
        ['Case Date:', case_details.get('case_date', 'N/A')],
        ['Created By:', case_details.get('created_by', 'N/A')],
        ['Reviewed By:', case_details.get('reviewed_by', 'N/A')],
    ]
    
    case_table = Table(case_data, colWidths=[2*inch, 4*inch])
    case_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(case_table)
    elements.append(Spacer(1, 20))
    
    # Customer Information Section
    elements.append(Paragraph("CUSTOMER INFORMATION", header_style))
    
    customer_data = [
        ['Mobile Number:', case_details.get('mobile_number', 'N/A')],
        ['Email ID:', case_details.get('email_id', 'N/A')],
        ['PAN:', case_details.get('pan', 'N/A')],
        ['Date of Birth:', case_details.get('date_of_birth', 'N/A')],
        ['Loan Amount:', f"₹{case_details.get('loan_amount', 'N/A')}"],
        ['Branch/Location:', case_details.get('branch_location', 'N/A')],
        ['Disbursement Date:', case_details.get('disbursement_date', 'N/A')],
        ['Referred By:', case_details.get('referred_by', 'N/A')],
    ]
    
    customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(customer_table)
    elements.append(Spacer(1, 20))
    
    # Case Description Section
    elements.append(Paragraph("CASE DESCRIPTION", header_style))
    case_description = case_details.get('case_description', 'No description available')
    elements.append(Paragraph(case_description, normal_style))
    elements.append(Spacer(1, 15))
    
    # Case History/Comments Section
    elements.append(Paragraph("CASE HISTORY & COMMENTS", header_style))
    
    try:
        case_comments = get_case_comments(case_details.get('case_id'))
        if case_comments:
            comment_data = [['Date/Time', 'User', 'Action', 'Comments']]
            for comment in case_comments:
                comment_data.append([
                    comment.get('created_at', 'N/A'),
                    comment.get('created_by', 'N/A'),
                    comment.get('action', 'N/A'),
                    comment.get('comment', 'N/A')[:100] + ('...' if len(comment.get('comment', '')) > 100 else '')
                ])
            
            comment_table = Table(comment_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2.5*inch])
            comment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            elements.append(comment_table)
        else:
            elements.append(Paragraph("No case history available.", normal_style))
    except Exception as e:
        elements.append(Paragraph("Unable to retrieve case history.", normal_style))
    
    elements.append(Spacer(1, 20))
    
    # Investigation Summary Section
    elements.append(Paragraph("INVESTIGATION SUMMARY", header_style))
    
    # Add investigation findings if available
    investigation_summary = case_details.get('investigation_summary', 'Investigation pending or not available')
    elements.append(Paragraph(investigation_summary, normal_style))
    elements.append(Spacer(1, 15))
    
    # Risk Assessment Section
    elements.append(Paragraph("RISK ASSESSMENT", header_style))
    risk_level = case_details.get('risk_level', 'Not assessed')
    risk_factors = case_details.get('risk_factors', 'Not available')
    
    risk_data = [
        ['Risk Level:', risk_level],
        ['Risk Factors:', risk_factors],
    ]
    
    risk_table = Table(risk_data, colWidths=[2*inch, 4*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(risk_table)
    elements.append(Spacer(1, 20))
    
    # Recommendations Section
    elements.append(Paragraph("RECOMMENDATIONS", header_style))
    recommendations = case_details.get('recommendations', 'No specific recommendations available')
    elements.append(Paragraph(recommendations, normal_style))
    elements.append(Spacer(1, 15))
    
    # Next Steps Section
    elements.append(Paragraph("NEXT STEPS", header_style))
    next_steps = case_details.get('next_steps', 'To be determined based on final review')
    elements.append(Paragraph(next_steps, normal_style))
    elements.append(Spacer(1, 20))
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    elements.append(Paragraph("--- End of Report ---", footer_style))
    elements.append(Paragraph("Generated by Tathya Case Management System", footer_style))
    elements.append(Paragraph("Aditya Birla Capital Ltd.", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get buffer value
    buffer.seek(0)
    return buffer

def show_pdf_download_button(case_details, button_text="📄 Download PDF Report"):
    """Show download button for PDF report"""
    
    case_id = case_details.get('case_id', 'unknown') if hasattr(case_details, 'get') else getattr(case_details, 'case_id', 'unknown')
    
    if st.button(button_text, use_container_width=True, key=f"pdf_btn_{case_id}"):
        try:
            pdf_buffer = generate_final_review_pdf(case_details)
            
            st.download_button(
                label="📥 Download Final Review Report",
                data=pdf_buffer.getvalue(),
                file_name=f"Final_Review_Report_{case_details.get('case_id', 'Unknown')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            st.success("✅ PDF report generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error generating PDF: {str(e)}")