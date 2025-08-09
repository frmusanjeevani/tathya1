import os
from twilio.rest import Client

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def send_investigation_sms(to_phone_number: str, case_id: str, agency_name: str):
    """
    Send SMS notification for investigation assignment
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create SMS message
        message_body = f"Investigation Assignment Alert: Case {case_id} has been assigned to {agency_name}. Please check your email for detailed instructions."
        
        # Send the SMS message
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        
        print(f"SMS sent successfully. Message SID: {message.sid}")
        return message.sid
        
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        raise e

def send_case_update_sms(to_phone_number: str, case_id: str, status: str):
    """
    Send SMS notification for case status updates
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create SMS message
        message_body = f"Case Update: Case {case_id} status changed to {status}. Please check the system for details."
        
        # Send the SMS message
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        
        print(f"SMS sent successfully. Message SID: {message.sid}")
        return message.sid
        
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        raise e