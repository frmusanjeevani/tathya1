import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

def send_account_request_notification(request_data):
    """Send email notification for new account request"""
    
    # Email configuration - using Gmail SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    admin_email = "suneel.r.vishwakarma@gmail.com"
    
    # Get email credentials from environment variables
    sender_email = os.environ.get('GMAIL_EMAIL')
    sender_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not sender_email or not sender_password:
        print("Email credentials not configured. Skipping email notification.")
        return False
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"New Account Request - {request_data['full_name']}"
        message["From"] = sender_email
        message["To"] = admin_email
        
        # Create HTML content
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px 8px 0 0;">
              <h2 style="color: white; margin: 0;">🔐 New Account Request</h2>
              <p style="color: #f0f0f0; margin: 5px 0 0 0;">Tathya Case Management System</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px;">
              <h3 style="color: #333; margin-top: 0;">Account Request Details</h3>
              
              <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: white;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Full Name:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{request_data['full_name']}</td>
                </tr>
                <tr style="background: #f8f9fa;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Email:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{request_data['email']}</td>
                </tr>
                <tr style="background: white;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Phone:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{request_data.get('phone', 'Not provided')}</td>
                </tr>
                <tr style="background: #f8f9fa;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Organization:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{request_data.get('organization', 'Not provided')}</td>
                </tr>
                <tr style="background: white;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Designation:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{request_data.get('designation', 'Not provided')}</td>
                </tr>
                <tr style="background: #f8f9fa;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Requested Role:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{request_data['requested_role']}</td>
                </tr>
                <tr style="background: white;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Manager Name:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{request_data.get('manager_name', 'Not provided')}</td>
                </tr>
                <tr style="background: #f8f9fa;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Manager Email:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{request_data.get('manager_email', 'Not provided')}</td>
                </tr>
                <tr style="background: white;">
                  <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Request Date:</td>
                  <td style="padding: 12px; border: 1px solid #dee2e6;">{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</td>
                </tr>
              </table>
              
              <h4 style="color: #333; margin-top: 20px;">Business Justification:</h4>
              <div style="background: white; padding: 15px; border-radius: 4px; border-left: 4px solid #667eea;">
                <p style="margin: 0; line-height: 1.6;">{request_data['business_justification']}</p>
              </div>
              
              <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 4px;">
                <p style="margin: 0; color: #1976d2; font-weight: bold;">
                  🔗 Please log into the Tathya Admin Panel to review and approve this request.
                </p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
        New Account Request - Tathya Case Management System
        
        Account Request Details:
        Full Name: {request_data['full_name']}
        Email: {request_data['email']}
        Phone: {request_data.get('phone', 'Not provided')}
        Organization: {request_data.get('organization', 'Not provided')}
        Designation: {request_data.get('designation', 'Not provided')}
        Requested Role: {request_data['requested_role']}
        Manager Name: {request_data.get('manager_name', 'Not provided')}
        Manager Email: {request_data.get('manager_email', 'Not provided')}
        Request Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
        
        Business Justification:
        {request_data['business_justification']}
        
        Please log into the Tathya Admin Panel to review and approve this request.
        """
        
        # Attach parts
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, admin_email, message.as_string())
        
        print(f"Account request notification sent successfully to {admin_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        return False

def send_account_approval_notification(user_data, approved=True):
    """Send notification to user about account approval/rejection"""
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    sender_email = os.environ.get('GMAIL_EMAIL')
    sender_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not sender_email or not sender_password:
        return False
    
    try:
        message = MIMEMultipart("alternative")
        subject = "Account Approved - Tathya Access" if approved else "Account Request Update - Tathya"
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = user_data.get('email') if hasattr(user_data, 'get') else user_data['email']
        
        # Get values safely from user_data (could be sqlite3.Row or dict)
        full_name = user_data.get('full_name') if hasattr(user_data, 'get') else user_data['full_name']
        requested_role = user_data.get('requested_role') if hasattr(user_data, 'get') else user_data['requested_role']
        username = user_data.get('username', 'Will be provided separately') if hasattr(user_data, 'get') else user_data.get('username', 'Will be provided separately')
        
        if approved:
            html_content = f"""
            <html>
              <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 20px; border-radius: 8px 8px 0 0;">
                  <h2 style="color: white; margin: 0;">✅ Account Approved!</h2>
                  <p style="color: #f0f0f0; margin: 5px 0 0 0;">Tathya Case Management System</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px;">
                  <p>Dear {full_name},</p>
                  
                  <p>Your account request has been approved! You can now access the Tathya Case Management System.</p>
                  
                  <div style="background: #d4edda; padding: 15px; border-radius: 4px; border-left: 4px solid #28a745;">
                    <p style="margin: 0;"><strong>Your Login Credentials:</strong></p>
                    <p style="margin: 5px 0;">Username: {username}</p>
                    <p style="margin: 5px 0;">Role: {requested_role}</p>
                  </div>
                  
                  <p>You will receive your login credentials separately for security purposes.</p>
                  
                  <p>Welcome to the Tathya team!</p>
                </div>
              </body>
            </html>
            """
        else:
            html_content = f"""
            <html>
              <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 20px; border-radius: 8px 8px 0 0;">
                  <h2 style="color: white; margin: 0;">Account Request Update</h2>
                  <p style="color: #f0f0f0; margin: 5px 0 0 0;">Tathya Case Management System</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px;">
                  <p>Dear {full_name},</p>
                  
                  <p>Thank you for your interest in accessing the Tathya Case Management System.</p>
                  
                  <p>After review, we are unable to approve your account request at this time.</p>
                  
                  <p>If you have any questions or would like to discuss this further, please contact the system administrator.</p>
                  
                  <p>Thank you for your understanding.</p>
                </div>
              </body>
            </html>
            """
        
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            recipient_email = user_data.get('email') if hasattr(user_data, 'get') else user_data['email']
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        return True
        
    except Exception as e:
        print(f"Failed to send user notification: {str(e)}")
        return False