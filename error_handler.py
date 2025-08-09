"""
Error Handler Module
Provides comprehensive error handling with formatted error boxes for the Tathya Case Management System
"""

import streamlit as st
import traceback
import logging
from datetime import datetime

def show_error_box(error_title, error_message, error_type="error", show_details=False, details=None):
    """
    Display a formatted error box with consistent styling
    
    Args:
        error_title (str): Title of the error
        error_message (str): Main error message
        error_type (str): Type of error - "error", "warning", "info"
        show_details (bool): Whether to show detailed error information
        details (str): Additional error details
    """
    
    # Choose appropriate Streamlit method based on error type
    if error_type == "error":
        st.error(f"🚫 **{error_title}**\n\n{error_message}")
    elif error_type == "warning":
        st.warning(f"⚠️ **{error_title}**\n\n{error_message}")
    elif error_type == "info":
        st.info(f"ℹ️ **{error_title}**\n\n{error_message}")
    
    # Show detailed error information if requested
    if show_details and details:
        with st.expander("🔍 Technical Details"):
            st.code(details, language="text")

def handle_database_error(operation_name, exception):
    """
    Handle database-related errors with specific messaging
    
    Args:
        operation_name (str): Name of the database operation that failed
        exception (Exception): The exception that occurred
    """
    error_details = f"""
Operation: {operation_name}
Error Type: {type(exception).__name__}
Error Message: {str(exception)}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    show_error_box(
        error_title="Database Operation Failed",
        error_message=f"An error occurred while performing the {operation_name} operation. Please try again or contact system administrator if the problem persists.",
        error_type="error",
        show_details=True,
        details=error_details.strip()
    )
    
    # Log the error for system administrators
    logging.error(f"Database Error in {operation_name}: {exception}")

def handle_file_operation_error(operation_name, filename, exception):
    """
    Handle file operation errors
    
    Args:
        operation_name (str): Type of file operation (upload, download, delete)
        filename (str): Name of the file
        exception (Exception): The exception that occurred
    """
    error_details = f"""
Operation: {operation_name}
File: {filename}
Error Type: {type(exception).__name__}
Error Message: {str(exception)}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    show_error_box(
        error_title=f"File {operation_name.title()} Failed",
        error_message=f"Unable to {operation_name} the file '{filename}'. Please check the file and try again.",
        error_type="error",
        show_details=True,
        details=error_details.strip()
    )

def handle_validation_error(field_name, validation_message):
    """
    Handle form validation errors
    
    Args:
        field_name (str): Name of the field that failed validation
        validation_message (str): Specific validation error message
    """
    show_error_box(
        error_title="Validation Error",
        error_message=f"**{field_name}**: {validation_message}",
        error_type="warning"
    )

def handle_permission_error(action_name, required_role):
    """
    Handle permission/authorization errors
    
    Args:
        action_name (str): The action the user tried to perform
        required_role (str): The role required for this action
    """
    show_error_box(
        error_title="Access Denied",
        error_message=f"You don't have permission to {action_name}. This action requires {required_role} role.",
        error_type="warning"
    )

def handle_api_error(service_name, exception, endpoint=None):
    """
    Handle API/external service errors
    
    Args:
        service_name (str): Name of the external service
        exception (Exception): The exception that occurred
        endpoint (str): API endpoint if applicable
    """
    error_details = f"""
Service: {service_name}
Endpoint: {endpoint or 'N/A'}
Error Type: {type(exception).__name__}
Error Message: {str(exception)}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    show_error_box(
        error_title=f"{service_name} Service Error",
        error_message=f"Unable to connect to {service_name} service. Please check your internet connection and try again.",
        error_type="error",
        show_details=True,
        details=error_details.strip()
    )

def handle_unexpected_error(operation_name, exception):
    """
    Handle unexpected/general errors
    
    Args:
        operation_name (str): Name of the operation that failed
        exception (Exception): The exception that occurred
    """
    error_details = f"""
Operation: {operation_name}
Error Type: {type(exception).__name__}
Error Message: {str(exception)}
Traceback: {traceback.format_exc()}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    show_error_box(
        error_title="Unexpected Error",
        error_message=f"An unexpected error occurred during {operation_name}. Please contact system administrator with the error details.",
        error_type="error",
        show_details=True,
        details=error_details.strip()
    )
    
    # Log the error for debugging
    logging.error(f"Unexpected Error in {operation_name}: {exception}\n{traceback.format_exc()}")

def success_message(title, message):
    """
    Display a formatted success message
    
    Args:
        title (str): Success title
        message (str): Success message
    """
    st.success(f"✅ **{title}**\n\n{message}")

def info_message(title, message):
    """
    Display a formatted info message
    
    Args:
        title (str): Info title
        message (str): Info message
    """
    st.info(f"ℹ️ **{title}**\n\n{message}")

def warning_message(title, message):
    """
    Display a formatted warning message
    
    Args:
        title (str): Warning title
        message (str): Warning message
    """
    st.warning(f"⚠️ **{title}**\n\n{message}")

# Decorator for handling exceptions in functions
def handle_exceptions(operation_name):
    """
    Decorator to automatically handle exceptions in functions
    
    Args:
        operation_name (str): Name of the operation for error reporting
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_unexpected_error(operation_name, e)
                return None
        return wrapper
    return decorator

def handle_streamlit_session_error(error, context="session operation"):
    """Handle Streamlit session state errors with simple messages"""
    st.error("⚠️ Backend Error")
    logging.error(f"Streamlit session error in {context}: {str(error)}")

def quick_error_handler(func):
    """Quick decorator for simple error handling without technical details"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Simple error handling based on error type
            error_msg = str(e).lower()
            
            if "streamlit" in error_msg and ("session_state" in error_msg or "cannot be modified" in error_msg):
                st.error("⚠️ Backend Error")
            elif "sqlite" in error_msg or "database" in error_msg:
                st.error("⚠️ Backend Error")
            elif "file" in error_msg or "permission" in error_msg:
                st.error("⚠️ Backend Error")
            elif "validation" in error_msg or "invalid" in error_msg:
                st.error("⚠️ Input Error - Please check your data")
            elif "api" in error_msg or "request" in error_msg:
                st.error("⚠️ Service Error")
            else:
                st.error("⚠️ Backend Error")
            
            # Log for debugging
            logging.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper