import streamlit as st
import json
import sqlite3
from datetime import datetime
import os
from typing import Dict, List, Any


def load_verification_config():
    """Load verification configuration from database or create default"""
    try:
        conn = sqlite3.connect('case_management.db')
        cursor = conn.cursor()

        # Create verification_config table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_type TEXT NOT NULL,
                config_name TEXT NOT NULL,
                config_value TEXT NOT NULL,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL,
                created_by TEXT NOT NULL,
                UNIQUE(config_type, config_name)
            )
        ''')

        # Load existing configurations
        cursor.execute(
            'SELECT config_type, config_name, config_value FROM verification_config'
        )
        results = cursor.fetchall()

        config = {}
        for config_type, config_name, config_value in results:
            if config_type not in config:
                config[config_type] = {}
            try:
                config[config_type][config_name] = json.loads(config_value)
            except:
                config[config_type][config_name] = config_value

        conn.close()
        return config
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return get_default_config()


def save_verification_config(config_type: str, config_name: str,
                             config_value: Any, user_id: str):
    """Save verification configuration to database"""
    try:
        conn = sqlite3.connect('case_management.db')
        cursor = conn.cursor()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        value_json = json.dumps(config_value) if isinstance(
            config_value, (dict, list)) else str(config_value)

        cursor.execute(
            '''
            INSERT OR REPLACE INTO verification_config 
            (config_type, config_name, config_value, created_date, modified_date, created_by)
            VALUES (?, ?, ?, 
                COALESCE((SELECT created_date FROM verification_config 
                         WHERE config_type = ? AND config_name = ?), ?),
                ?, ?)
        ''', (config_type, config_name, value_json, config_type, config_name,
              current_time, current_time, user_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving configuration: {str(e)}")
        return False


def get_default_config():
    """Return default verification configuration"""
    return {
        "risk_parameters": {
            "face_match_weight": 20,
            "document_authenticity_weight": 20,
            "mobile_risk_weight": 15,
            "credit_report_weight": 15,
            "income_consistency_weight": 10,
            "location_device_risk_weight": 10,
            "application_metadata_weight": 10
        },
        "api_endpoints": {
            "face_plus_plus_api":
            "https://api-us.faceplusplus.com/facepp/v3/compare",
            "mnrl_verification_api": "https://api.example.com/mnrl/verify",
            "pan_verification_api": "https://api.example.com/pan/verify",
            "aadhaar_verification_api":
            "https://api.example.com/aadhaar/verify",
            "gst_verification_api": "https://api.example.com/gst/verify"
        },
        "verification_fields": {
            "pan_card": {
                "required": True,
                "validation_regex": "[A-Z]{5}[0-9]{4}[A-Z]{1}",
                "max_length": 10,
                "min_length": 10
            },
            "aadhaar_card": {
                "required": True,
                "validation_regex": "[0-9]{12}",
                "max_length": 12,
                "min_length": 12,
                "masking": True
            },
            "mobile_number": {
                "required": True,
                "validation_regex": "[6-9][0-9]{9}",
                "max_length": 10,
                "min_length": 10
            },
            "email": {
                "required": False,
                "validation_regex":
                "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                "max_length": 100
            }
        },
        "document_types": {
            "identity_documents": [
                "PAN Card", "Aadhaar Card", "Voter ID", "Passport",
                "Driving License"
            ],
            "address_documents": [
                "Utility Bill", "Bank Statement", "Rent Agreement",
                "Property Documents"
            ],
            "income_documents": [
                "Salary Slip", "Bank Statement", "ITR", "Form 16",
                "Business Documents"
            ],
            "other_documents": [
                "Property Documents", "Business License",
                "Additional Supporting Documents"
            ]
        },
        "fraud_types": {
            "customer_fraud": {
                "enabled":
                True,
                "description":
                "Intentional misrepresentation or deceit by the customer",
                "parameters": [
                    "identity_verification", "document_authenticity",
                    "income_verification"
                ]
            },
            "employee_fraud": {
                "enabled":
                False,
                "description":
                "Internal fraud by employees or agents",
                "parameters":
                ["process_compliance", "authorization_checks", "audit_trail"]
            },
            "vendor_fraud": {
                "enabled":
                False,
                "description":
                "Fraud involving external vendors or partners",
                "parameters": [
                    "vendor_verification", "contract_compliance",
                    "service_delivery"
                ]
            }
        }
    }


def show_field_configuration():
    """Show field configuration interface"""
    st.subheader("🔧 Field Configuration")

    config = load_verification_config()
    field_config = config.get("verification_fields",
                              get_default_config()["verification_fields"])

    # Add new field
    with st.expander("➕ Add New Field", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_field_name = st.text_input("Field Name")
            field_required = st.checkbox("Required Field")
            field_masking = st.checkbox("Enable Masking")

        with col2:
            field_validation = st.text_input("Validation Regex")
            field_min_length = st.number_input("Minimum Length",
                                               min_value=0,
                                               value=0)
            field_max_length = st.number_input("Maximum Length",
                                               min_value=1,
                                               value=50)

        if st.button("Add Field", use_container_width=True):
            if new_field_name:
                new_field_config = {
                    "required": field_required,
                    "validation_regex": field_validation,
                    "min_length": field_min_length,
                    "max_length": field_max_length,
                    "masking": field_masking
                }
                if save_verification_config(
                        "verification_fields", new_field_name,
                        new_field_config,
                        st.session_state.get('user_id', 'admin')):
                    st.success(f"Field '{new_field_name}' added successfully!")
                    st.rerun()

    # Edit existing fields
    st.subheader("📝 Edit Existing Fields")

    for field_name, field_data in field_config.items():
        with st.expander(f"🔧 {field_name.replace('_', ' ').title()}",
                         expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                required = st.checkbox("Required",
                                       value=field_data.get("required", False),
                                       key=f"req_{field_name}")
                masking = st.checkbox("Enable Masking",
                                      value=field_data.get("masking", False),
                                      key=f"mask_{field_name}")

            with col2:
                validation = st.text_input("Validation Regex",
                                           value=field_data.get(
                                               "validation_regex", ""),
                                           key=f"val_{field_name}")
                min_len = st.number_input("Min Length",
                                          value=field_data.get(
                                              "min_length", 0),
                                          key=f"min_{field_name}")

            with col3:
                max_len = st.number_input("Max Length",
                                          value=field_data.get(
                                              "max_length", 50),
                                          key=f"max_{field_name}")

                col_update, col_delete = st.columns(2)
                with col_update:
                    if st.button("Update",
                                 key=f"update_{field_name}",
                                 use_container_width=True):
                        updated_config = {
                            "required": required,
                            "validation_regex": validation,
                            "min_length": min_len,
                            "max_length": max_len,
                            "masking": masking
                        }
                        if save_verification_config(
                                "verification_fields", field_name,
                                updated_config,
                                st.session_state.get('user_id', 'admin')):
                            st.success(f"Field '{field_name}' updated!")
                            st.rerun()

                with col_delete:
                    if st.button("Delete",
                                 key=f"delete_{field_name}",
                                 use_container_width=True,
                                 type="secondary"):
                        try:
                            conn = sqlite3.connect('case_management.db')
                            cursor = conn.cursor()
                            cursor.execute(
                                'DELETE FROM verification_config WHERE config_type = ? AND config_name = ?',
                                ("verification_fields", field_name))
                            conn.commit()
                            conn.close()
                            st.success(f"Field '{field_name}' deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting field: {str(e)}")


def show_api_configuration():
    """Show API configuration interface"""
    st.subheader("🌐 API Configuration")

    config = load_verification_config()
    api_config = config.get("api_endpoints",
                            get_default_config()["api_endpoints"])

    # Add new API endpoint
    with st.expander("➕ Add New API Endpoint", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_api_name = st.text_input("API Name")
            new_api_method = st.selectbox("HTTP Method",
                                          ["GET", "POST", "PUT", "DELETE"])

        with col2:
            new_api_url = st.text_input("API URL")
            new_api_timeout = st.number_input("Timeout (seconds)",
                                              min_value=1,
                                              value=30)

        new_api_headers = st.text_area(
            "Headers (JSON format)",
            value='{"Content-Type": "application/json"}')

        if st.button("Add API Endpoint", use_container_width=True):
            if new_api_name and new_api_url:
                try:
                    headers = json.loads(
                        new_api_headers) if new_api_headers else {}
                    new_api_config = {
                        "url": new_api_url,
                        "method": new_api_method,
                        "timeout": new_api_timeout,
                        "headers": headers
                    }
                    if save_verification_config(
                            "api_endpoints", new_api_name, new_api_config,
                            st.session_state.get('user_id', 'admin')):
                        st.success(
                            f"API endpoint '{new_api_name}' added successfully!"
                        )
                        st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON format in headers")

    # Edit existing API endpoints
    st.subheader("📝 Edit Existing API Endpoints")

    for api_name, api_data in api_config.items():
        with st.expander(f"🌐 {api_name.replace('_', ' ').title()}",
                         expanded=False):
            if isinstance(api_data, str):
                # Legacy format - just URL
                api_url = st.text_input("API URL",
                                        value=api_data,
                                        key=f"url_{api_name}")
                api_method = st.selectbox("HTTP Method",
                                          ["GET", "POST", "PUT", "DELETE"],
                                          key=f"method_{api_name}")
                api_timeout = st.number_input("Timeout (seconds)",
                                              min_value=1,
                                              value=30,
                                              key=f"timeout_{api_name}")
                api_headers = st.text_area(
                    "Headers (JSON)",
                    value='{"Content-Type": "application/json"}',
                    key=f"headers_{api_name}")

                if st.button("Update",
                             key=f"update_api_{api_name}",
                             use_container_width=True):
                    try:
                        headers = json.loads(api_headers)
                        updated_config = {
                            "url": api_url,
                            "method": api_method,
                            "timeout": api_timeout,
                            "headers": headers
                        }
                        if save_verification_config(
                                "api_endpoints", api_name, updated_config,
                                st.session_state.get('user_id', 'admin')):
                            st.success(f"API endpoint '{api_name}' updated!")
                            st.rerun()
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format in headers")
            else:
                # New format - full configuration
                col1, col2 = st.columns(2)
                with col1:
                    api_url = st.text_input("API URL",
                                            value=api_data.get("url", ""),
                                            key=f"url_{api_name}")
                    api_method = st.selectbox(
                        "HTTP Method", ["GET", "POST", "PUT", "DELETE"],
                        index=["GET", "POST", "PUT",
                               "DELETE"].index(api_data.get("method", "POST")),
                        key=f"method_{api_name}")

                with col2:
                    api_timeout = st.number_input("Timeout (seconds)",
                                                  min_value=1,
                                                  value=api_data.get(
                                                      "timeout", 30),
                                                  key=f"timeout_{api_name}")

                api_headers = st.text_area("Headers (JSON)",
                                           value=json.dumps(api_data.get(
                                               "headers", {}),
                                                            indent=2),
                                           key=f"headers_{api_name}")

                col_update, col_delete = st.columns(2)
                with col_update:
                    if st.button("Update",
                                 key=f"update_api_{api_name}",
                                 use_container_width=True):
                        try:
                            headers = json.loads(api_headers)
                            updated_config = {
                                "url": api_url,
                                "method": api_method,
                                "timeout": api_timeout,
                                "headers": headers
                            }
                            if save_verification_config(
                                    "api_endpoints", api_name, updated_config,
                                    st.session_state.get('user_id', 'admin')):
                                st.success(
                                    f"API endpoint '{api_name}' updated!")
                                st.rerun()
                        except json.JSONDecodeError:
                            st.error("Invalid JSON format in headers")

                with col_delete:
                    if st.button("Delete",
                                 key=f"delete_api_{api_name}",
                                 use_container_width=True,
                                 type="secondary"):
                        try:
                            conn = sqlite3.connect('case_management.db')
                            cursor = conn.cursor()
                            cursor.execute(
                                'DELETE FROM verification_config WHERE config_type = ? AND config_name = ?',
                                ("api_endpoints", api_name))
                            conn.commit()
                            conn.close()
                            st.success(f"API endpoint '{api_name}' deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting API endpoint: {str(e)}")


def show_risk_parameter_configuration():
    """Show risk parameter configuration interface"""
    st.subheader("⚖️ Risk Parameter Configuration")

    config = load_verification_config()
    risk_config = config.get("risk_parameters",
                             get_default_config()["risk_parameters"])

    st.info(
        "Configure the weightage for different risk parameters. Total should equal 100%."
    )

    total_weight = 0
    updated_params = {}

    for param_name, current_weight in risk_config.items():
        display_name = param_name.replace('_', ' ').title()
        weight = st.slider(f"{display_name} (%)",
                           min_value=0,
                           max_value=100,
                           value=current_weight,
                           key=f"weight_{param_name}")
        updated_params[param_name] = weight
        total_weight += weight

    # Color coding for total weight
    if total_weight == 100:
        st.success(f"✅ Total Weight: {total_weight}% (Perfect)")
    elif total_weight < 100:
        st.warning(f"⚠️ Total Weight: {total_weight}% (Under-weighted)")
    else:
        st.error(f"❌ Total Weight: {total_weight}% (Over-weighted)")

    # Add new risk parameter
    with st.expander("➕ Add New Risk Parameter", expanded=False):
        new_param_name = st.text_input("Parameter Name")
        new_param_weight = st.number_input("Weight (%)",
                                           min_value=0,
                                           max_value=100,
                                           value=0)

        if st.button("Add Parameter", use_container_width=True):
            if new_param_name:
                param_key = new_param_name.lower().replace(' ',
                                                           '_') + '_weight'
                if save_verification_config(
                        "risk_parameters", param_key, new_param_weight,
                        st.session_state.get('user_id', 'admin')):
                    st.success(
                        f"Risk parameter '{new_param_name}' added successfully!"
                    )
                    st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Configuration",
                     use_container_width=True,
                     type="primary"):
            success = True
            for param_name, weight in updated_params.items():
                if not save_verification_config(
                        "risk_parameters", param_name, weight,
                        st.session_state.get('user_id', 'admin')):
                    success = False
                    break

            if success:
                st.success("Risk parameters updated successfully!")
                st.rerun()
            else:
                st.error("Error updating risk parameters")

    with col2:
        if st.button("🔄 Reset to Default",
                     use_container_width=True,
                     type="secondary"):
            default_params = get_default_config()["risk_parameters"]
            success = True
            for param_name, weight in default_params.items():
                if not save_verification_config(
                        "risk_parameters", param_name, weight,
                        st.session_state.get('user_id', 'admin')):
                    success = False
                    break

            if success:
                st.success("Risk parameters reset to default!")
                st.rerun()
            else:
                st.error("Error resetting risk parameters")


def show_document_type_configuration():
    """Show document type configuration interface"""
    st.subheader("📄 Document Type Configuration")

    config = load_verification_config()
    doc_config = config.get("document_types",
                            get_default_config()["document_types"])

    for category, documents in doc_config.items():
        with st.expander(f"📁 {category.replace('_', ' ').title()}",
                         expanded=False):
            # Show existing documents
            st.write("**Current Documents:**")
            for i, doc in enumerate(documents):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {doc}")
                with col2:
                    if st.button("🗑️",
                                 key=f"delete_doc_{category}_{i}",
                                 help="Delete document type"):
                        documents.remove(doc)
                        if save_verification_config(
                                "document_types", category, documents,
                                st.session_state.get('user_id', 'admin')):
                            st.success(f"Document type '{doc}' removed!")
                            st.rerun()

            # Add new document type
            col1, col2 = st.columns([3, 1])
            with col1:
                new_doc = st.text_input("Add new document type",
                                        key=f"new_doc_{category}")
            with col2:
                if st.button("➕ Add", key=f"add_doc_{category}"):
                    if new_doc and new_doc not in documents:
                        documents.append(new_doc)
                        if save_verification_config(
                                "document_types", category, documents,
                                st.session_state.get('user_id', 'admin')):
                            st.success(f"Document type '{new_doc}' added!")
                            st.rerun()
                    elif new_doc in documents:
                        st.warning("Document type already exists!")


def show_fraud_type_configuration():
    """Show fraud type configuration interface"""
    st.subheader("🚨 Fraud Type Configuration")

    config = load_verification_config()
    fraud_config = config.get("fraud_types",
                              get_default_config()["fraud_types"])

    # Add new fraud type
    with st.expander("➕ Add New Fraud Type", expanded=False):
        new_fraud_name = st.text_input("Fraud Type Name")
        new_fraud_desc = st.text_area("Description")
        new_fraud_enabled = st.checkbox("Enable by default", value=True)
        new_fraud_params = st.multiselect("Select Parameters", [
            "identity_verification", "document_authenticity",
            "income_verification", "process_compliance",
            "authorization_checks", "audit_trail", "vendor_verification",
            "contract_compliance", "service_delivery"
        ])

        if st.button("Add Fraud Type", use_container_width=True):
            if new_fraud_name:
                fraud_key = new_fraud_name.lower().replace(' ', '_')
                new_fraud_config = {
                    "enabled": new_fraud_enabled,
                    "description": new_fraud_desc,
                    "parameters": new_fraud_params
                }
                if save_verification_config(
                        "fraud_types", fraud_key, new_fraud_config,
                        st.session_state.get('user_id', 'admin')):
                    st.success(
                        f"Fraud type '{new_fraud_name}' added successfully!")
                    st.rerun()

    # Edit existing fraud types
    for fraud_type, fraud_data in fraud_config.items():
        with st.expander(f"🚨 {fraud_type.replace('_', ' ').title()}",
                         expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                enabled = st.checkbox("Enabled",
                                      value=fraud_data.get("enabled", True),
                                      key=f"enabled_{fraud_type}")
                description = st.text_area("Description",
                                           value=fraud_data.get(
                                               "description", ""),
                                           key=f"desc_{fraud_type}")

            with col2:
                parameters = st.multiselect("Parameters", [
                    "identity_verification", "document_authenticity",
                    "income_verification", "process_compliance",
                    "authorization_checks", "audit_trail",
                    "vendor_verification", "contract_compliance",
                    "service_delivery"
                ],
                                            default=fraud_data.get(
                                                "parameters", []),
                                            key=f"params_{fraud_type}")

            col_update, col_delete = st.columns(2)
            with col_update:
                if st.button("Update",
                             key=f"update_fraud_{fraud_type}",
                             use_container_width=True):
                    updated_config = {
                        "enabled": enabled,
                        "description": description,
                        "parameters": parameters
                    }
                    if save_verification_config(
                            "fraud_types", fraud_type, updated_config,
                            st.session_state.get('user_id', 'admin')):
                        st.success(f"Fraud type '{fraud_type}' updated!")
                        st.rerun()

            with col_delete:
                if st.button("Delete",
                             key=f"delete_fraud_{fraud_type}",
                             use_container_width=True,
                             type="secondary"):
                    try:
                        conn = sqlite3.connect('case_management.db')
                        cursor = conn.cursor()
                        cursor.execute(
                            'DELETE FROM verification_config WHERE config_type = ? AND config_name = ?',
                            ("fraud_types", fraud_type))
                        conn.commit()
                        conn.close()
                        st.success(f"Fraud type '{fraud_type}' deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting fraud type: {str(e)}")


def show_configuration_export_import():
    """Show configuration export/import interface"""
    st.subheader("📥📤 Configuration Export/Import")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Export Configuration**")
        if st.button("📤 Export All Configurations", use_container_width=True):
            config = load_verification_config()
            config_json = json.dumps(config, indent=2)

            st.download_button(
                label="💾 Download Configuration",
                data=config_json,
                file_name=
                f"configuration_panel_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True)

    with col2:
        st.write("**Import Configuration**")
        uploaded_config = st.file_uploader("Choose configuration file",
                                           type=['json'])

        if uploaded_config is not None:
            try:
                config_data = json.load(uploaded_config)

                if st.button("📥 Import Configuration",
                             use_container_width=True):
                    success = True
                    user_id = st.session_state.get('user_id', 'admin')

                    for config_type, config_items in config_data.items():
                        for config_name, config_value in config_items.items():
                            if not save_verification_config(
                                    config_type, config_name, config_value,
                                    user_id):
                                success = False
                                break
                        if not success:
                            break

                    if success:
                        st.success("Configuration imported successfully!")
                        st.rerun()
                    else:
                        st.error("Error importing configuration")

            except json.JSONDecodeError:
                st.error("Invalid JSON file")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")


def show():
    """Main function to display Configuration Panel"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem;">
            ⚙️ Configuration Panel
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            No-Code Configuration Management for Verification System
        </p>
    </div>
    """,
                unsafe_allow_html=True)

    # Check if user is logged in - allow all users
    if not st.session_state.get('logged_in', False):
        st.error("🔒 Please log in to access the Configuration Panel")
        return

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔧 Field Config", "🌐 API Config", "⚖️ Risk Parameters",
        "📄 Document Types", "🚨 Fraud Types", "📥📤 Import/Export"
    ])

    with tab1:
        show_field_configuration()

    with tab2:
        show_api_configuration()

    with tab3:
        show_risk_parameter_configuration()

    with tab4:
        show_document_type_configuration()

    with tab5:
        show_fraud_type_configuration()

    with tab6:
        show_configuration_export_import()

    # Configuration summary
    st.markdown("---")
    st.subheader("📊 Configuration Summary")

    config = load_verification_config()

    col1, col2, col3 = st.columns(3)

    with col1:
        field_count = len(config.get("verification_fields", {}))
        st.metric("Verification Fields", field_count)

        api_count = len(config.get("api_endpoints", {}))
        st.metric("API Endpoints", api_count)

    with col2:
        risk_count = len(config.get("risk_parameters", {}))
        st.metric("Risk Parameters", risk_count)

        doc_categories = len(config.get("document_types", {}))
        st.metric("Document Categories", doc_categories)

    with col3:
        fraud_types = len(config.get("fraud_types", {}))
        st.metric("Fraud Types", fraud_types)

        total_docs = sum(
            len(docs) for docs in config.get("document_types", {}).values())
        st.metric("Total Document Types", total_docs)

    # Recent changes log
    st.subheader("📝 Recent Changes")
    try:
        conn = sqlite3.connect('case_management.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT config_type, config_name, modified_date, created_by 
            FROM verification_config 
            ORDER BY modified_date DESC 
            LIMIT 10
        ''')
        recent_changes = cursor.fetchall()

        if recent_changes:
            for config_type, config_name, modified_date, created_by in recent_changes:
                st.write(
                    f"• **{config_type}** → {config_name} (Modified: {modified_date} by {created_by})"
                )
        else:
            st.write("No recent changes found.")

        conn.close()
    except Exception as e:
        st.write("Unable to load recent changes.")


if __name__ == "__main__":
    show()
