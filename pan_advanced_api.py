import requests
import json
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import secrets

class PANAdvancedAPI:
    def __init__(self):
        self.base_url = "https://www.timbleglance.com/api/pan_advance_enc"
        self.api_key = os.environ.get('TIMBLE_GLANCE_API_KEY')
        self.encryption_key = os.environ.get('TIMBLE_GLANCE_ENCRYPTION_KEY')
        
    def encrypt_data(self, data):
        """Encrypt data using AES-256-GCM"""
        try:
            if not self.encryption_key:
                raise ValueError("Encryption key not configured")
            
            # Convert key to bytes if it's a string
            key = self.encryption_key.encode('utf-8')[:32]  # Ensure 32 bytes for AES-256
            
            # Generate a random IV
            iv = secrets.token_bytes(12)  # 12 bytes for GCM
            
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # Encrypt the data
            plaintext = json.dumps(data).encode('utf-8')
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # Combine IV + tag + ciphertext and encode to base64
            encrypted_data = base64.b64encode(iv + encryptor.tag + ciphertext).decode('utf-8')
            
            return encrypted_data
            
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return None
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data using AES-256-GCM"""
        try:
            if not self.encryption_key:
                raise ValueError("Encryption key not configured")
            
            # Convert key to bytes
            key = self.encryption_key.encode('utf-8')[:32]
            
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Extract IV (12 bytes), tag (16 bytes), and ciphertext
            iv = encrypted_bytes[:12]
            tag = encrypted_bytes[12:28]
            ciphertext = encrypted_bytes[28:]
            
            # Create cipher and decrypt
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return json.loads(plaintext.decode('utf-8'))
            
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return None
    
    def validate_pan(self, pan_number):
        """Validate PAN using Timble Glance API"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'API key not configured',
                'code': 'CONFIG_ERROR'
            }
        
        try:
            # Prepare request payload
            request_data = {
                "pan": pan_number,
                "timestamp": "2024-01-01T00:00:00Z"  # You might want to use current timestamp
            }
            
            # Encrypt the request data
            encrypted_request = self.encrypt_data(request_data)
            
            if not encrypted_request:
                return {
                    'success': False,
                    'error': 'Failed to encrypt request',
                    'code': 'ENCRYPTION_ERROR'
                }
            
            # Prepare API payload
            payload = {
                "encryptedReq": encrypted_request
            }
            
            # Set headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            }
            
            # Make API call
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if response contains encrypted data
                if 'encryptedRes' in response_data:
                    # Decrypt the response
                    decrypted_data = self.decrypt_data(response_data['encryptedRes'])
                    
                    if decrypted_data:
                        return self.format_response(decrypted_data)
                    else:
                        return {
                            'success': False,
                            'error': 'Failed to decrypt response',
                            'code': 'DECRYPTION_ERROR'
                        }
                else:
                    # Handle unencrypted response (if any)
                    return self.format_response(response_data)
            else:
                return {
                    'success': False,
                    'error': f'API request failed with status {response.status_code}',
                    'code': 'API_ERROR',
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'code': 'NETWORK_ERROR'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'code': 'UNKNOWN_ERROR'
            }
    
    def format_response(self, data):
        """Format API response for UI display"""
        try:
            # Extract response code and message
            code = data.get('code', 'UNKNOWN')
            message = data.get('message', 'No message provided')
            
            # Handle different response codes
            if code == 101:  # Success
                pan_details = data.get('data', {})
                return {
                    'success': True,
                    'code': code,
                    'message': message,
                    'data': {
                        'FULLNAME': pan_details.get('FULLNAME', 'N/A'),
                        'DOB': pan_details.get('DOB', 'N/A'),
                        'EMAIL': pan_details.get('EMAIL', 'N/A'),
                        'MOBILE': pan_details.get('MOBILE', 'N/A'),
                        'PAN_TYPE': pan_details.get('PAN_TYPE', 'N/A'),
                        'AADHAAR_LINKAGE': pan_details.get('AADHAAR_LINKAGE', 'N/A'),
                        'ADDRESS': pan_details.get('ADDRESS', 'N/A'),
                        'GENDER': pan_details.get('GENDER', 'N/A'),
                        'CATEGORY': pan_details.get('CATEGORY', 'N/A'),
                        'PAN_STATUS': pan_details.get('PAN_STATUS', 'N/A')
                    },
                    'transaction_id': data.get('transaction_id'),
                    'request_timestamp': data.get('request_timestamp'),
                    'response_timestamp': data.get('response_timestamp')
                }
            elif code == 102:  # Invalid ID or input
                return {
                    'success': False,
                    'code': code,
                    'message': 'Invalid PAN number or input format',
                    'error': 'INVALID_INPUT'
                }
            elif code == 103:  # No record found
                return {
                    'success': False,
                    'code': code,
                    'message': 'No record found for the provided PAN',
                    'error': 'NO_RECORD'
                }
            elif code == 110:  # Source unavailable
                return {
                    'success': False,
                    'code': code,
                    'message': 'Service temporarily unavailable',
                    'error': 'SERVICE_DOWN'
                }
            else:
                return {
                    'success': False,
                    'code': code,
                    'message': message,
                    'error': 'UNKNOWN_RESPONSE'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to format response: {str(e)}',
                'code': 'FORMAT_ERROR'
            }

# Utility functions for testing
def test_pan_validation(pan_number):
    """Test function for PAN validation"""
    api = PANAdvancedAPI()
    result = api.validate_pan(pan_number)
    return result

def get_response_message(code):
    """Get user-friendly message for response codes"""
    messages = {
        101: "✅ PAN validation successful",
        102: "❌ Invalid PAN number or format",
        103: "⚠️ No record found for this PAN",
        110: "🔧 Service temporarily unavailable",
        'CONFIG_ERROR': "⚙️ API configuration missing",
        'ENCRYPTION_ERROR': "🔐 Encryption failed",
        'DECRYPTION_ERROR': "🔓 Decryption failed",
        'API_ERROR': "🌐 API request failed",
        'NETWORK_ERROR': "📡 Network connection error",
        'UNKNOWN_ERROR': "❓ Unexpected error occurred"
    }
    return messages.get(code, "❓ Unknown response")