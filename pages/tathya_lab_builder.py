"""
Tathya Lab Builder - No-Code Drag & Drop Workflow Designer
Advanced visual workflow builder with API integration
"""

import streamlit as st
import json
from auth import is_authenticated, get_current_user

def show():
    """Display the no-code workflow builder"""
    
    # Enhanced CSS for drag-and-drop interface
    st.markdown("""
    <style>
    .builder-header {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #1e3c72 100%);
        color: white;
        text-align: center;
        padding: 30px 20px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .builder-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(45deg, #fff, #a0c4ff, #bdb2ff, #ffc6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 1px;
    }
    
    .builder-subtitle {
        font-size: 1.2rem;
        margin: 10px 0 0 0;
        color: rgba(255,255,255,0.9);
        font-weight: 300;
    }
    
    .toolbox-container {
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .canvas-container {
        background: white;
        border: 3px dashed #a0c4ff;
        border-radius: 15px;
        min-height: 600px;
        padding: 30px;
        position: relative;
        box-shadow: inset 0 0 20px rgba(160, 196, 255, 0.1);
    }
    
    .api-block {
        background: linear-gradient(145deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 5px;
        cursor: grab;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        display: inline-block;
        min-width: 150px;
        text-align: center;
    }
    
    .api-block:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .api-block:active {
        cursor: grabbing;
        transform: scale(0.95);
    }
    
    .workflow-node {
        background: white;
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 20px;
        margin: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        position: relative;
        cursor: move;
        min-width: 200px;
        transition: all 0.3s ease;
    }
    
    .workflow-node:hover {
        border-color: #a0c4ff;
        box-shadow: 0 8px 25px rgba(160, 196, 255, 0.3);
    }
    
    .node-connector {
        width: 15px;
        height: 15px;
        background: #667eea;
        border-radius: 50%;
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .node-connector.input {
        left: -7px;
        background: #28a745;
    }
    
    .node-connector.output {
        right: -7px;
        background: #dc3545;
    }
    
    .node-connector:hover {
        transform: translateY(-50%) scale(1.3);
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
    }
    
    .config-panel {
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .section-header {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .api-category {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .canvas-placeholder {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-top: 200px;
        opacity: 0.7;
    }
    
    .workflow-actions {
        background: linear-gradient(145deg, #fff 0%, #f8f9fa 100%);
        border: 2px solid #dee2e6;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .action-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 8px;
        margin: 5px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
    }
    
    .template-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        margin: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    
    .template-card:hover {
        border-color: #667eea;
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="builder-header">
        <h1 class="builder-title">🔧 Tathya Lab Builder</h1>
        <p class="builder-subtitle">No-Code Drag & Drop Workflow Designer</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not is_authenticated():
        st.error("Please log in to access Tathya Lab Builder")
        return
    
    # Initialize session state
    if 'workflow_nodes' not in st.session_state:
        st.session_state.workflow_nodes = []
    if 'workflow_connections' not in st.session_state:
        st.session_state.workflow_connections = []
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None
    
    # Main layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        show_toolbox()
        show_templates()
    
    with col2:
        show_canvas()
        show_workflow_actions()

def show_toolbox():
    """Display the API blocks toolbox"""
    
    st.markdown('<div class="section-header">🧰 API Toolbox</div>', unsafe_allow_html=True)
    
    # Identity & KYC APIs
    with st.expander("🆔 Identity & KYC APIs", expanded=True):
        api_blocks = [
            {"name": "PAN Verification", "icon": "🏦", "category": "identity"},
            {"name": "Aadhaar Validation", "icon": "🆔", "category": "identity"},
            {"name": "Face Match AI", "icon": "🧬", "category": "identity"},
            {"name": "Voter ID Check", "icon": "🗳️", "category": "identity"},
            {"name": "Passport Verify", "icon": "📘", "category": "identity"}
        ]
        
        for block in api_blocks:
            if st.button(f"{block['icon']} {block['name']}", key=f"add_{block['name']}", use_container_width=True):
                add_node_to_canvas(block)
    
    # Financial APIs
    with st.expander("💰 Financial APIs"):
        financial_blocks = [
            {"name": "Bank Statement AI", "icon": "📊", "category": "financial"},
            {"name": "UPI Verification", "icon": "💳", "category": "financial"},
            {"name": "Credit Analysis", "icon": "📈", "category": "financial"},
            {"name": "CIBIL Score", "icon": "📋", "category": "financial"},
            {"name": "GST Validation", "icon": "🧾", "category": "financial"}
        ]
        
        for block in financial_blocks:
            if st.button(f"{block['icon']} {block['name']}", key=f"add_{block['name']}", use_container_width=True):
                add_node_to_canvas(block)
    
    # Digital Intelligence APIs
    with st.expander("🌐 Digital Intelligence APIs"):
        digital_blocks = [
            {"name": "Mobile Intelligence", "icon": "📱", "category": "digital"},
            {"name": "Email Analytics", "icon": "📧", "category": "digital"},
            {"name": "IP Geolocation", "icon": "🌍", "category": "digital"},
            {"name": "Device Fingerprint", "icon": "🖥️", "category": "digital"},
            {"name": "Social Media Check", "icon": "📲", "category": "digital"}
        ]
        
        for block in digital_blocks:
            if st.button(f"{block['icon']} {block['name']}", key=f"add_{block['name']}", use_container_width=True):
                add_node_to_canvas(block)
    
    # Advanced Analytics
    with st.expander("⚡ Advanced Analytics"):
        analytics_blocks = [
            {"name": "Fraud Scoring", "icon": "🧠", "category": "analytics"},
            {"name": "Risk Assessment", "icon": "⚠️", "category": "analytics"},
            {"name": "Behavioral Analysis", "icon": "🎭", "category": "analytics"},
            {"name": "Predictive ML", "icon": "🔮", "category": "analytics"},
            {"name": "Anomaly Detection", "icon": "🔍", "category": "analytics"}
        ]
        
        for block in analytics_blocks:
            if st.button(f"{block['icon']} {block['name']}", key=f"add_{block['name']}", use_container_width=True):
                add_node_to_canvas(block)

def show_templates():
    """Display workflow templates"""
    
    st.markdown('<div class="section-header">📋 Workflow Templates</div>', unsafe_allow_html=True)
    
    templates = [
        {
            "name": "Customer Onboarding",
            "description": "Complete KYC + Identity verification workflow",
            "nodes": ["PAN Verification", "Aadhaar Validation", "Face Match AI", "Risk Assessment"]
        },
        {
            "name": "Fraud Detection",
            "description": "Multi-layer fraud detection pipeline",
            "nodes": ["Mobile Intelligence", "Device Fingerprint", "Fraud Scoring", "Behavioral Analysis"]
        },
        {
            "name": "Financial Assessment",
            "description": "Comprehensive financial verification",
            "nodes": ["Bank Statement AI", "CIBIL Score", "UPI Verification", "Credit Analysis"]
        },
        {
            "name": "Digital Identity",
            "description": "Digital footprint analysis",
            "nodes": ["Email Analytics", "Social Media Check", "IP Geolocation", "Anomaly Detection"]
        }
    ]
    
    for template in templates:
        with st.container():
            st.markdown(f"""
            <div class="template-card">
                <h4 style="margin: 0 0 8px 0; color: #667eea;">{template['name']}</h4>
                <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 0.9rem;">{template['description']}</p>
                <small style="color: #495057;">Nodes: {len(template['nodes'])}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Load {template['name']}", key=f"template_{template['name']}", use_container_width=True):
                load_template(template)

def show_canvas():
    """Display the workflow canvas"""
    
    st.markdown('<div class="section-header">🎨 Workflow Canvas</div>', unsafe_allow_html=True)
    
    canvas_container = st.container()
    
    with canvas_container:
        if not st.session_state.workflow_nodes:
            st.markdown("""
            <div class="canvas-container">
                <div class="canvas-placeholder">
                    <p>🎯 Drag API blocks here to build your workflow</p>
                    <p style="font-size: 1rem; margin-top: 10px;">Select blocks from the toolbox or use a template to get started</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
            
            # Display workflow nodes
            cols = st.columns(min(len(st.session_state.workflow_nodes), 3))
            for idx, node in enumerate(st.session_state.workflow_nodes):
                col_idx = idx % 3
                with cols[col_idx]:
                    show_workflow_node(node, idx)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Node configuration panel
    if st.session_state.selected_node is not None:
        show_node_configuration()

def show_workflow_node(node, idx):
    """Display a workflow node"""
    
    node_key = f"node_{idx}"
    
    # Node container
    st.markdown(f"""
    <div class="workflow-node" id="{node_key}">
        <div class="node-connector input" title="Input"></div>
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">{node['icon']}</div>
            <div style="font-weight: 600; color: #2c3e50; margin-bottom: 5px;">{node['name']}</div>
            <div style="font-size: 0.8rem; color: #6c757d;">Category: {node['category'].title()}</div>
        </div>
        <div class="node-connector output" title="Output"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Node actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⚙️", key=f"config_{idx}", help="Configure"):
            st.session_state.selected_node = idx
            st.rerun()
    with col2:
        if st.button("📋", key=f"copy_{idx}", help="Duplicate"):
            duplicate_node(node)
    with col3:
        if st.button("🗑️", key=f"delete_{idx}", help="Delete"):
            remove_node(idx)

def show_node_configuration():
    """Display node configuration panel"""
    
    selected_idx = st.session_state.selected_node
    if selected_idx < len(st.session_state.workflow_nodes):
        node = st.session_state.workflow_nodes[selected_idx]
        
        st.markdown("---")
        st.markdown('<div class="section-header">⚙️ Node Configuration</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown(f"**Configuring: {node['icon']} {node['name']}**")
            
            # API Configuration
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("API Endpoint", key=f"endpoint_{selected_idx}", 
                             placeholder="https://api.example.com/verify")
                st.selectbox("HTTP Method", ["POST", "GET", "PUT"], key=f"method_{selected_idx}")
                st.text_input("API Key", type="password", key=f"apikey_{selected_idx}")
            
            with col2:
                st.number_input("Timeout (seconds)", min_value=1, max_value=300, 
                               value=30, key=f"timeout_{selected_idx}")
                st.number_input("Retry Attempts", min_value=0, max_value=5, 
                               value=2, key=f"retry_{selected_idx}")
                st.selectbox("Response Format", ["JSON", "XML", "Text"], key=f"format_{selected_idx}")
            
            # Input/Output Configuration
            st.markdown("**Input Parameters:**")
            if st.button("+ Add Parameter", key=f"add_param_{selected_idx}"):
                if 'node_params' not in st.session_state:
                    st.session_state.node_params = {}
                if selected_idx not in st.session_state.node_params:
                    st.session_state.node_params[selected_idx] = []
                st.session_state.node_params[selected_idx].append({"name": "", "type": "string", "required": True})
            
            # Display parameters
            if 'node_params' in st.session_state and selected_idx in st.session_state.node_params:
                for pidx, param in enumerate(st.session_state.node_params[selected_idx]):
                    pcol1, pcol2, pcol3, pcol4 = st.columns([3, 2, 1, 1])
                    with pcol1:
                        param['name'] = st.text_input("Parameter Name", value=param['name'], 
                                                     key=f"param_name_{selected_idx}_{pidx}")
                    with pcol2:
                        param['type'] = st.selectbox("Type", ["string", "number", "boolean", "file"], 
                                                    index=["string", "number", "boolean", "file"].index(param['type']),
                                                    key=f"param_type_{selected_idx}_{pidx}")
                    with pcol3:
                        param['required'] = st.checkbox("Required", value=param['required'], 
                                                       key=f"param_req_{selected_idx}_{pidx}")
                    with pcol4:
                        if st.button("🗑️", key=f"del_param_{selected_idx}_{pidx}"):
                            st.session_state.node_params[selected_idx].pop(pidx)
                            st.rerun()
            
            # Save configuration
            if st.button("💾 Save Configuration", key=f"save_config_{selected_idx}"):
                st.success("Node configuration saved!")
                st.session_state.selected_node = None
                st.rerun()

def show_workflow_actions():
    """Display workflow action buttons"""
    
    st.markdown("""
    <div class="workflow-actions">
        <h4 style="margin: 0 0 15px 0; color: #2c3e50;">Workflow Actions</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ Test Workflow", use_container_width=True, type="primary"):
            test_workflow()
    
    with col2:
        if st.button("💾 Save Workflow", use_container_width=True):
            save_workflow()
    
    with col3:
        if st.button("📤 Export JSON", use_container_width=True):
            export_workflow()
    
    with col4:
        if st.button("🗑️ Clear Canvas", use_container_width=True):
            clear_canvas()

def add_node_to_canvas(block):
    """Add a new node to the canvas"""
    st.session_state.workflow_nodes.append(block.copy())
    st.success(f"Added {block['name']} to workflow!")
    st.rerun()

def duplicate_node(node):
    """Duplicate a node"""
    new_node = node.copy()
    new_node['name'] = f"{node['name']} (Copy)"
    st.session_state.workflow_nodes.append(new_node)
    st.success(f"Duplicated {node['name']}!")
    st.rerun()

def remove_node(idx):
    """Remove a node from the canvas"""
    if 0 <= idx < len(st.session_state.workflow_nodes):
        removed_node = st.session_state.workflow_nodes.pop(idx)
        st.success(f"Removed {removed_node['name']} from workflow!")
        if st.session_state.selected_node == idx:
            st.session_state.selected_node = None
        st.rerun()

def load_template(template):
    """Load a workflow template"""
    st.session_state.workflow_nodes = []
    
    # Map template nodes to actual blocks
    block_mapping = {
        "PAN Verification": {"name": "PAN Verification", "icon": "🏦", "category": "identity"},
        "Aadhaar Validation": {"name": "Aadhaar Validation", "icon": "🆔", "category": "identity"},
        "Face Match AI": {"name": "Face Match AI", "icon": "🧬", "category": "identity"},
        "Risk Assessment": {"name": "Risk Assessment", "icon": "⚠️", "category": "analytics"},
        "Mobile Intelligence": {"name": "Mobile Intelligence", "icon": "📱", "category": "digital"},
        "Device Fingerprint": {"name": "Device Fingerprint", "icon": "🖥️", "category": "digital"},
        "Fraud Scoring": {"name": "Fraud Scoring", "icon": "🧠", "category": "analytics"},
        "Behavioral Analysis": {"name": "Behavioral Analysis", "icon": "🎭", "category": "analytics"},
        "Bank Statement AI": {"name": "Bank Statement AI", "icon": "📊", "category": "financial"},
        "CIBIL Score": {"name": "CIBIL Score", "icon": "📋", "category": "financial"},
        "UPI Verification": {"name": "UPI Verification", "icon": "💳", "category": "financial"},
        "Credit Analysis": {"name": "Credit Analysis", "icon": "📈", "category": "financial"},
        "Email Analytics": {"name": "Email Analytics", "icon": "📧", "category": "digital"},
        "Social Media Check": {"name": "Social Media Check", "icon": "📲", "category": "digital"},
        "IP Geolocation": {"name": "IP Geolocation", "icon": "🌍", "category": "digital"},
        "Anomaly Detection": {"name": "Anomaly Detection", "icon": "🔍", "category": "analytics"}
    }
    
    for node_name in template['nodes']:
        if node_name in block_mapping:
            st.session_state.workflow_nodes.append(block_mapping[node_name])
    
    st.success(f"Loaded template: {template['name']}!")
    st.rerun()

def test_workflow():
    """Test the current workflow"""
    if not st.session_state.workflow_nodes:
        st.warning("Please add some nodes to test the workflow!")
        return
    
    with st.spinner("Testing workflow..."):
        # Simulate workflow testing
        import time
        time.sleep(2)
        
        results = []
        for node in st.session_state.workflow_nodes:
            results.append({
                "node": node['name'],
                "status": "✅ Success",
                "response_time": f"{(hash(node['name']) % 500 + 100)}ms",
                "result": "Mock response data"
            })
        
        st.success("Workflow test completed!")
        
        # Display results
        for result in results:
            with st.expander(f"{result['node']} - {result['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"Response Time: {result['response_time']}")
                with col2:
                    st.info(f"Result: {result['result']}")

def save_workflow():
    """Save the current workflow"""
    if not st.session_state.workflow_nodes:
        st.warning("No workflow to save!")
        return
    
    workflow_name = st.text_input("Enter workflow name:", key="save_workflow_name")
    if workflow_name and st.button("💾 Confirm Save"):
        # Save workflow to session state or database
        if 'saved_workflows' not in st.session_state:
            st.session_state.saved_workflows = {}
        
        st.session_state.saved_workflows[workflow_name] = {
            "nodes": st.session_state.workflow_nodes.copy(),
            "connections": st.session_state.workflow_connections.copy(),
            "created_at": str(st.session_state.get('current_time', 'Unknown'))
        }
        
        st.success(f"Workflow '{workflow_name}' saved successfully!")

def export_workflow():
    """Export workflow as JSON"""
    if not st.session_state.workflow_nodes:
        st.warning("No workflow to export!")
        return
    
    workflow_data = {
        "workflow_name": "Tathya_Lab_Workflow",
        "nodes": st.session_state.workflow_nodes,
        "connections": st.session_state.workflow_connections,
        "metadata": {
            "created_by": get_current_user(),
            "node_count": len(st.session_state.workflow_nodes),
            "version": "1.0"
        }
    }
    
    json_str = json.dumps(workflow_data, indent=2)
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name="tathya_workflow.json",
        mime="application/json"
    )

def clear_canvas():
    """Clear the workflow canvas"""
    if st.button("⚠️ Confirm Clear All", type="secondary"):
        st.session_state.workflow_nodes = []
        st.session_state.workflow_connections = []
        st.session_state.selected_node = None
        if 'node_params' in st.session_state:
            st.session_state.node_params = {}
        st.success("Canvas cleared!")
        st.rerun()