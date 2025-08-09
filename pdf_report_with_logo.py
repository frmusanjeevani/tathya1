from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import io
import os

def generate_customer_fraud_report_with_logo(report_data):
    """Generate PDF report with ABCL logo for customer fraud risk assessment"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Add ABCL Logo at the top
    logo_path = "static/images/abcl_logo.jpg"
    if os.path.exists(logo_path):
        try:
            logo = ReportLabImage(logo_path, width=2*inch, height=1*inch)
            story.append(logo)
            story.append(Spacer(1, 20))
        except Exception as e:
            # If logo fails to load, add company name instead
            story.append(Paragraph("ABCL - Aditya Birla Capital Limited", styles['Title']))
            story.append(Spacer(1, 20))
    else:
        # Fallback if logo not found
        story.append(Paragraph("ABCL - Aditya Birla Capital Limited", styles['Title']))
        story.append(Spacer(1, 20))
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        textColor=colors.darkblue
    )
    
    # Title
    story.append(Paragraph("CUSTOMER FRAUD RISK ASSESSMENT REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Generation info
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Customer Details
    story.append(Paragraph("CUSTOMER DETAILS", heading_style))
    customer_data = [
        ['Field', 'Value'],
        ['PAN Number', report_data['customer_details'].get('pan_number', 'Not Provided')],
        ['Aadhaar Number', report_data['customer_details'].get('aadhaar_number', 'Not Provided')],
        ['Mobile Number', report_data['customer_details'].get('mobile_number', 'Not Provided')],
        ['Email ID', report_data['customer_details'].get('email_id', 'Not Provided')]
    ]
    
    customer_table = Table(customer_data, colWidths=[2*inch, 3*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(customer_table)
    story.append(Spacer(1, 20))
    
    # Risk Assessment Summary
    story.append(Paragraph("FRAUD RISK ASSESSMENT", heading_style))
    risk_data = [
        ['Metric', 'Value'],
        ['Overall Risk Score', f"{report_data['risk_assessment']['overall_score']:.1f}%"],
        ['Risk Category', report_data['risk_assessment']['risk_category']],
        ['Recommendation', report_data['risk_assessment']['recommendation']]
    ]
    
    risk_table = Table(risk_data, colWidths=[2*inch, 3*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(risk_table)
    story.append(Spacer(1, 20))
    
    # Component Scores
    story.append(Paragraph("RISK COMPONENT BREAKDOWN", heading_style))
    component_data = [
        ['Component', 'Weight', 'Score'],
        ['Face Match & Dedupe', '20%', f"{report_data['risk_assessment']['component_scores'].get('face_match_score', 0)}%"],
        ['Document Authenticity', '20%', f"{report_data['risk_assessment']['component_scores'].get('document_authenticity', 0)}%"],
        ['Mobile Risk', '15%', f"{report_data['risk_assessment']['component_scores'].get('mobile_risk', 0)}%"],
        ['Credit Report Flags', '15%', f"{report_data['risk_assessment']['component_scores'].get('credit_report_flags', 0)}%"],
        ['Income Consistency', '10%', f"{report_data['risk_assessment']['component_scores'].get('income_consistency', 0)}%"],
        ['Location/Device Risk', '10%', f"{report_data['risk_assessment']['component_scores'].get('location_device_risk', 0)}%"],
        ['Application Metadata', '10%', f"{report_data['risk_assessment']['component_scores'].get('metadata_anomalies', 0)}%"]
    ]
    
    component_table = Table(component_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
    component_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(component_table)
    story.append(Spacer(1, 20))
    
    # Red Flags
    if report_data.get('red_flags'):
        story.append(Paragraph("RED FLAGS IDENTIFIED", heading_style))
        for flag in report_data['red_flags']:
            story.append(Paragraph(f"• {flag}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Document Analyses
    if report_data.get('document_analyses'):
        story.append(Paragraph("DOCUMENT ANALYSIS SUMMARY", heading_style))
        for doc_analysis in report_data['document_analyses']:
            doc_name = doc_analysis.get('document', 'Unknown Document')
            story.append(Paragraph(f"<b>{doc_name}:</b> Analysis completed with AI verification", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # API Verification Results
    if report_data.get('api_verifications'):
        story.append(Paragraph("API VERIFICATION RESULTS", heading_style))
        verifications = report_data['api_verifications']
        
        if verifications.get('pan_verification'):
            pan_data = verifications['pan_verification']
            story.append(Paragraph(f"<b>PAN Verification:</b> {'Valid' if pan_data.get('is_valid') else 'Invalid'}", styles['Normal']))
            if pan_data.get('name'):
                story.append(Paragraph(f"Registered Name: {pan_data['name']}", styles['Normal']))
        
        if verifications.get('aadhaar_verification'):
            aadhaar_data = verifications['aadhaar_verification']
            story.append(Paragraph(f"<b>Aadhaar Verification:</b> {'Valid' if aadhaar_data.get('is_valid') else 'Invalid'}", styles['Normal']))
        
        if verifications.get('mnrl_verification'):
            mnrl_data = verifications['mnrl_verification']
            story.append(Paragraph(f"<b>MNRL Check:</b> {'High Risk' if mnrl_data.get('is_revoked') else 'Clear'}", styles['Normal']))
            if mnrl_data.get('complaint_count', 0) > 0:
                story.append(Paragraph(f"Complaint Count: {mnrl_data['complaint_count']}", styles['Normal']))
        
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("This report is generated by Tathya Investigation Intelligence System", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, 
                                       textColor=colors.grey, alignment=1)))
    story.append(Paragraph("ABCL - Aditya Birla Capital Limited", 
                          ParagraphStyle('Footer2', parent=styles['Normal'], fontSize=10, 
                                       textColor=colors.grey, alignment=1)))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer