"""
System Design Module - Visual Architecture and Workflow Diagrams
Provides comprehensive system architecture visualization with interactive diagrams
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

def show():
    """Display System Design page with architecture diagrams"""
    
    # Professional header styling
    st.markdown("""
    <style>
    .system-design-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    .architecture-section {
        background: #f8f9ff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e1e8f0;
    }
    .workflow-box {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="system-design-header">
        <h1>🏗️ System Design & Architecture</h1>
        <p>Comprehensive visualization of Tathya platform architecture, data flow, and integration points</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏛️ System Architecture", 
        "🔄 Data Flow", 
        "📋 Workflow Stages", 
        "🔗 Integration Map"
    ])
    
    with tab1:
        show_system_architecture()
    
    with tab2:
        show_data_flow_diagram()
    
    with tab3:
        show_workflow_stages()
    
    with tab4:
        show_integration_map()

def show_system_architecture():
    """Display high-level system architecture diagram"""
    
    st.markdown("""
    <div class="architecture-section">
        <h2>🏗️ High-Level System Architecture</h2>
        <p>Core components and their relationships in the Tathya platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create system architecture diagram using Plotly
    fig = go.Figure()
    
    # Define component positions and connections
    components = {
        'Frontend': {'x': 2, 'y': 8, 'color': '#4285f4', 'size': 60},
        'Auth System': {'x': 1, 'y': 6, 'color': '#34a853', 'size': 50},
        'Case Management': {'x': 3, 'y': 6, 'color': '#ea4335', 'size': 55},
        'Investigation': {'x': 5, 'y': 6, 'color': '#fbbc04', 'size': 55},
        'Workflow Engine': {'x': 2, 'y': 4, 'color': '#ff6d00', 'size': 50},
        'AI Services': {'x': 4, 'y': 4, 'color': '#9c27b0', 'size': 50},
        'Database': {'x': 1, 'y': 2, 'color': '#607d8b', 'size': 45},
        'File Storage': {'x': 3, 'y': 2, 'color': '#795548', 'size': 45},
        'External APIs': {'x': 5, 'y': 2, 'color': '#009688', 'size': 45}
    }
    
    # Add component nodes
    for name, props in components.items():
        fig.add_trace(go.Scatter(
            x=[props['x']], y=[props['y']],
            mode='markers+text',
            marker=dict(
                size=props['size'], 
                color=props['color'], 
                opacity=0.9,
                line=dict(width=3, color='white')
            ),
            text=name,
            textposition="bottom center",
            textfont=dict(color='#2c3e50', size=14, family='Arial Black'),
            showlegend=False,
            hovertemplate=f"<b>{name}</b><br>Core System Component<extra></extra>"
        ))
    
    # Add connections between components
    connections = [
        ('Frontend', 'Auth System'),
        ('Frontend', 'Case Management'),
        ('Frontend', 'Investigation'),
        ('Case Management', 'Workflow Engine'),
        ('Investigation', 'AI Services'),
        ('Workflow Engine', 'Database'),
        ('AI Services', 'External APIs'),
        ('Case Management', 'File Storage'),
        ('Auth System', 'Database')
    ]
    
    for source, target in connections:
        source_pos = components[source]
        target_pos = components[target]
        fig.add_trace(go.Scatter(
            x=[source_pos['x'], target_pos['x']],
            y=[source_pos['y'], target_pos['y']],
            mode='lines',
            line=dict(color='rgba(100,100,100,0.4)', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        title=dict(
            text="Tathya System Architecture - Core Components",
            font=dict(size=20, family='Arial Black', color='#2c3e50')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 6]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.5, 9]),
        plot_bgcolor='#f8f9ff',
        paper_bgcolor='white',
        height=600,
        font=dict(size=14)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Component descriptions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="workflow-box">
        <h4>🎯 Frontend Layer</h4>
        <ul>
        <li>Streamlit Web Interface</li>
        <li>Role-based Navigation</li>
        <li>Interactive Dashboards</li>
        <li>Real-time Updates</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="workflow-box">
        <h4>🔐 Authentication & Authorization</h4>
        <ul>
        <li>Secure Login System</li>
        <li>Role-based Access Control</li>
        <li>Session Management</li>
        <li>Audit Logging</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="workflow-box">
        <h4>⚙️ Core Business Logic</h4>
        <ul>
        <li>Case Management Engine</li>
        <li>Investigation Workflows</li>
        <li>Approval Processes</li>
        <li>Document Management</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="workflow-box">
        <h4>🤖 AI & External Services</h4>
        <ul>
        <li>Google Gemini AI</li>
        <li>PAN Verification APIs</li>
        <li>Face Recognition</li>
        <li>Document Analysis</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def show_data_flow_diagram():
    """Display data flow across the system"""
    
    st.markdown("""
    <div class="architecture-section">
        <h2>🔄 Data Flow Architecture</h2>
        <p>How data moves through the Tathya platform from case creation to resolution</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create data flow diagram
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=["Case Data Journey Through System"]
    )
    
    # Data flow stages
    stages = [
        "Case Registration", "Data Validation", "Case Allocation", 
        "Investigation", "Primary Review", "Approval L1", 
        "Approval L2", "Legal Review", "Final Resolution"
    ]
    
    # Create flow visualization
    fig.add_trace(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=stages,
            color=["#4285f4", "#34a853", "#ea4335", "#fbbc04", "#ff6d00", 
                   "#9c27b0", "#607d8b", "#795548", "#009688"]
        ),
        link=dict(
            source=[0, 1, 2, 3, 4, 5, 6, 7],
            target=[1, 2, 3, 4, 5, 6, 7, 8],
            value=[100, 90, 85, 80, 70, 60, 55, 50],
            color=["rgba(66,133,244,0.3)", "rgba(52,168,83,0.3)", 
                   "rgba(234,67,53,0.3)", "rgba(251,188,4,0.3)",
                   "rgba(255,109,0,0.3)", "rgba(156,39,176,0.3)",
                   "rgba(96,125,139,0.3)", "rgba(121,85,72,0.3)"]
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="Data Flow Through Case Management Lifecycle",
            font=dict(size=18, family='Arial Black', color='#2c3e50')
        ),
        font=dict(size=14),
        height=500,
        plot_bgcolor='#f8f9ff',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Data flow details
    st.markdown("""
    <div class="workflow-box">
    <h4>📊 Key Data Flow Patterns</h4>
    <ul>
    <li><strong>Input Validation:</strong> All case data validated at entry point</li>
    <li><strong>Progressive Enhancement:</strong> Data enriched at each workflow stage</li>
    <li><strong>Audit Trail:</strong> Complete history maintained throughout lifecycle</li>
    <li><strong>Real-time Updates:</strong> Status changes propagated instantly</li>
    <li><strong>Document Attachment:</strong> Files linked and tracked at each stage</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

def show_workflow_stages():
    """Display detailed workflow stages and transitions"""
    
    st.markdown("""
    <div class="architecture-section">
        <h2>📋 Workflow Stage Architecture</h2>
        <p>Detailed view of each workflow stage, roles, and decision points</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create colorful workflow diagram with different shapes
    create_workflow_diagram()
    
    # Workflow stage data
    workflow_data = {
        'Stage': ['Case Registration', 'Case Allocation', 'Agency Investigation', 
                 'Regional Investigation', 'Primary Review', 'Final Review',
                 'Approval L1', 'Approval L2', 'Legal Review', 'Case Resolution'],
        'Role': ['Initiator', 'Admin/Investigator', 'External Agency', 
                'Regional Team', 'Reviewer', 'Final Reviewer',
                'Approver L1', 'Approver L2', 'Legal Reviewer', 'Actioner'],
        'Duration_Days': [1, 2, 7, 5, 3, 2, 1, 1, 3, 2],
        'Status': ['Active', 'Active', 'Active', 'Active', 'Active', 'Active',
                  'Active', 'Active', 'Active', 'Active'],
        'Complexity': [2, 3, 8, 6, 5, 4, 2, 2, 6, 3]
    }
    
    df = pd.DataFrame(workflow_data)
    
    # Create workflow timeline
    fig = go.Figure()
    
    # Add workflow stages as timeline
    fig.add_trace(go.Scatter(
        x=df['Duration_Days'],
        y=df['Stage'],
        mode='markers+text',
        marker=dict(
            size=df['Complexity']*5,
            color=df['Duration_Days'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Duration (Days)")
        ),
        text=df['Role'],
        textposition="middle right",
        textfont=dict(size=12, family='Arial', color='#2c3e50'),
        hovertemplate="<b>%{y}</b><br>Role: %{text}<br>Duration: %{x} days<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text="Workflow Stages Timeline & Complexity",
            font=dict(size=18, family='Arial Black', color='#2c3e50')
        ),
        xaxis=dict(
            title=dict(text="Average Duration (Days)", font=dict(size=14)),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(text="Workflow Stage", font=dict(size=14)),
            categoryorder='array', 
            categoryarray=df['Stage'][::-1],
            tickfont=dict(size=12)
        ),
        height=550,
        plot_bgcolor='#f8f9ff',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Stage details table
    st.markdown("### 📋 Workflow Stage Details")
    st.dataframe(
        df[['Stage', 'Role', 'Duration_Days', 'Complexity']].rename(columns={
            'Duration_Days': 'Avg Duration (Days)',
            'Complexity': 'Complexity Score (1-10)'
        }),
        use_container_width=True
    )

def create_workflow_diagram():
    """Create a colorful workflow diagram with different shapes for different node types"""
    
    st.markdown("### 🎨 Complete Workflow Process Flow")
    
    # Create the workflow diagram using Plotly
    fig = go.Figure()
    
    # Define workflow nodes with lighter colors, proper shapes, and better spacing
    workflow_nodes = {
        # Start node (circle) - Light green
        'START': {'x': 1, 'y': 11, 'shape': 'circle', 'color': '#81C784', 'size': 50, 'type': 'start'},
        
        # Process nodes (rectangles) - Light blue family
        'Case Registration': {'x': 1, 'y': 9.5, 'shape': 'square', 'color': '#64B5F6', 'size': 45, 'type': 'process'},
        'Data Validation': {'x': 1, 'y': 8.5, 'shape': 'square', 'color': '#64B5F6', 'size': 45, 'type': 'process'},
        
        # Decision node (diamond) - Light orange
        'Auto-Assign?': {'x': 1, 'y': 7.5, 'shape': 'diamond', 'color': '#FFB74D', 'size': 40, 'type': 'decision'},
        
        # Parallel process paths - Similar light blue
        'Case Allocation': {'x': 2.5, 'y': 6.5, 'shape': 'square', 'color': '#64B5F6', 'size': 45, 'type': 'process'},
        'Manual Assignment': {'x': -0.5, 'y': 6.5, 'shape': 'square', 'color': '#64B5F6', 'size': 45, 'type': 'process'},
        
        # Investigation paths - Light purple family (similar shades)
        'Agency Investigation': {'x': 3.5, 'y': 5.5, 'shape': 'square', 'color': '#BA68C8', 'size': 45, 'type': 'process'},
        'Regional Investigation': {'x': 0.5, 'y': 5.5, 'shape': 'square', 'color': '#BA68C8', 'size': 45, 'type': 'process'},
        
        # Review stages - Light coral family (similar shades)
        'Primary Review': {'x': 2, 'y': 4.5, 'shape': 'square', 'color': '#FF8A65', 'size': 45, 'type': 'process'},
        
        # Decision point - Same light orange as first decision
        'Review Pass?': {'x': 2, 'y': 3.5, 'shape': 'diamond', 'color': '#FFB74D', 'size': 40, 'type': 'decision'},
        
        # Approval path - Similar light coral shades
        'Final Review': {'x': 2, 'y': 2.7, 'shape': 'square', 'color': '#FF8A65', 'size': 45, 'type': 'process'},
        'Approval L1': {'x': 3.5, 'y': 2.2, 'shape': 'square', 'color': '#90A4AE', 'size': 45, 'type': 'process'},
        'Approval L2': {'x': 3.5, 'y': 1.7, 'shape': 'square', 'color': '#90A4AE', 'size': 45, 'type': 'process'},
        
        # Final decision - Same light orange
        'Approved?': {'x': 3.5, 'y': 1.2, 'shape': 'diamond', 'color': '#FFB74D', 'size': 40, 'type': 'decision'},
        
        # Resolution paths - Light brown family (similar shades)
        'Legal Review': {'x': 4.5, 'y': 0.7, 'shape': 'square', 'color': '#A1887F', 'size': 45, 'type': 'process'},
        'Case Resolution': {'x': 2, 'y': 0.7, 'shape': 'square', 'color': '#A1887F', 'size': 45, 'type': 'process'},
        
        # End nodes - Light red family (similar shades)
        'CLOSED': {'x': 2, 'y': -0.3, 'shape': 'circle', 'color': '#E57373', 'size': 50, 'type': 'end'},
        'LEGAL ACTION': {'x': 4.5, 'y': -0.3, 'shape': 'circle', 'color': '#F06292', 'size': 50, 'type': 'end'},
        
        # Rejection path - Light pink (similar to end nodes)
        'Reject/Return': {'x': -0.5, 'y': 3.5, 'shape': 'square', 'color': '#F48FB1', 'size': 45, 'type': 'process'}
    }
    
    # Add workflow nodes with different shapes
    for name, props in workflow_nodes.items():
        symbol = 'circle' if props['shape'] == 'circle' else 'square' if props['shape'] == 'square' else 'diamond'
        
        fig.add_trace(go.Scatter(
            x=[props['x']], y=[props['y']],
            mode='markers+text',
            marker=dict(
                size=props['size'], 
                color=props['color'], 
                symbol=symbol,
                line=dict(width=3, color='white'),
                opacity=0.85
            ),
            text=name,
            textposition="bottom center",
            textfont=dict(color='#2c3e50', size=12, family='Arial Black'),
            showlegend=False,
            hovertemplate=f"<b>{name}</b><br>Type: {props['type'].title()}<extra></extra>"
        ))
    
    # Define workflow connections with different arrow styles
    connections = [
        ('START', 'Case Registration', 'solid'),
        ('Case Registration', 'Data Validation', 'solid'),
        ('Data Validation', 'Auto-Assign?', 'solid'),
        ('Auto-Assign?', 'Case Allocation', 'solid'),
        ('Auto-Assign?', 'Manual Assignment', 'dash'),
        ('Case Allocation', 'Agency Investigation', 'solid'),
        ('Manual Assignment', 'Regional Investigation', 'solid'),
        ('Agency Investigation', 'Primary Review', 'solid'),
        ('Regional Investigation', 'Primary Review', 'solid'),
        ('Primary Review', 'Review Pass?', 'solid'),
        ('Review Pass?', 'Final Review', 'solid'),
        ('Review Pass?', 'Reject/Return', 'dash'),
        ('Reject/Return', 'Case Registration', 'dot'),
        ('Final Review', 'Approval L1', 'solid'),
        ('Approval L1', 'Approval L2', 'solid'),
        ('Approval L2', 'Approved?', 'solid'),
        ('Approved?', 'Case Resolution', 'solid'),
        ('Approved?', 'Legal Review', 'dash'),
        ('Case Resolution', 'CLOSED', 'solid'),
        ('Legal Review', 'LEGAL ACTION', 'solid')
    ]
    
    # Add connection arrows
    for source, target, line_style in connections:
        source_pos = workflow_nodes[source]
        target_pos = workflow_nodes[target]
        
        # Choose lighter line colors based on connection type
        line_color = '#81C784' if line_style == 'solid' else '#FFB74D' if line_style == 'dash' else '#E57373'
        line_dash = 'solid' if line_style == 'solid' else 'dash' if line_style == 'dash' else 'dot'
        
        # Add arrow line
        fig.add_trace(go.Scatter(
            x=[source_pos['x'], target_pos['x']],
            y=[source_pos['y'], target_pos['y']],
            mode='lines',
            line=dict(color=line_color, width=4, dash=line_dash),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add arrow head
        # Calculate arrow head position
        dx = target_pos['x'] - source_pos['x']
        dy = target_pos['y'] - source_pos['y']
        if dx != 0 or dy != 0:
            import math
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                # Normalize and position arrow head
                dx_norm = dx / length * 0.1
                dy_norm = dy / length * 0.1
                arrow_x = target_pos['x'] - dx_norm
                arrow_y = target_pos['y'] - dy_norm
                
                fig.add_trace(go.Scatter(
                    x=[arrow_x], y=[arrow_y],
                    mode='markers',
                    marker=dict(
                        size=15, 
                        color=line_color, 
                        symbol='triangle-up',
                        line=dict(width=1, color='white')
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
    
    # Update layout for better visualization
    fig.update_layout(
        title=dict(
            text="Tathya Case Management Workflow - Complete Process Flow",
            font=dict(size=20, family='Arial Black', color='#2c3e50')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 12]),
        plot_bgcolor='#f8f9ff',
        paper_bgcolor='white',
        height=800,
        font=dict(size=12),
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend for workflow shapes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="workflow-box">
        <h5>🟢 Start/End Nodes</h5>
        <p><strong>Circle Shape:</strong> Entry and exit points</p>
        <ul>
        <li>Green: START</li>
        <li>Red: END states</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="workflow-box">
        <h5>🔵 Process Nodes</h5>
        <p><strong>Rectangle Shape:</strong> Processing stages</p>
        <ul>
        <li>Blue: Data processing</li>
        <li>Purple: Investigations</li>
        <li>Orange: Reviews</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="workflow-box">
        <h5>🔶 Decision Nodes</h5>
        <p><strong>Diamond Shape:</strong> Decision points</p>
        <ul>
        <li>Auto-assignment logic</li>
        <li>Review pass/fail</li>
        <li>Approval decisions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="workflow-box">
        <h5>➡️ Flow Types</h5>
        <p><strong>Different Lines:</strong> Flow paths</p>
        <ul>
        <li>Solid: Main flow</li>
        <li>Dashed: Alternative path</li>
        <li>Dotted: Return/loop</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Add exportable diagram section
    st.markdown("---")
    st.markdown("### 📊 Exportable Workflow Diagram")
    st.markdown("""
    <div class="workflow-box">
    <p><strong>Note:</strong> This editable version is for proposing/visualizing system changes only. 
    It does not affect the original workflow baseline reference.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create downloadable workflow data
    create_exportable_workflow_diagram()

def create_exportable_workflow_diagram():
    """Create an exportable version of the workflow diagram for external editing"""
    
    # Create structured workflow data for export
    workflow_export_data = {
        "diagram_title": "Tathya Case Management Workflow – Complete Process Flow",
        "nodes": [
            {"id": "START", "label": "START", "type": "start", "shape": "circle", "color": "light_green"},
            {"id": "case_reg", "label": "Case Registration", "type": "process", "shape": "rectangle", "color": "light_blue"},
            {"id": "data_val", "label": "Data Validation", "type": "process", "shape": "rectangle", "color": "light_blue"},
            {"id": "auto_assign", "label": "Auto-Assign?", "type": "decision", "shape": "diamond", "color": "light_orange"},
            {"id": "case_alloc", "label": "Case Allocation", "type": "process", "shape": "rectangle", "color": "light_blue"},
            {"id": "manual_assign", "label": "Manual Assignment", "type": "process", "shape": "rectangle", "color": "light_blue"},
            {"id": "agency_inv", "label": "Agency Investigation", "type": "process", "shape": "rectangle", "color": "light_purple"},
            {"id": "regional_inv", "label": "Regional Investigation", "type": "process", "shape": "rectangle", "color": "light_purple"},
            {"id": "primary_rev", "label": "Primary Review", "type": "process", "shape": "rectangle", "color": "light_coral"},
            {"id": "review_pass", "label": "Review Pass?", "type": "decision", "shape": "diamond", "color": "light_orange"},
            {"id": "final_rev", "label": "Final Review", "type": "process", "shape": "rectangle", "color": "light_coral"},
            {"id": "approval_l1", "label": "Approval L1", "type": "process", "shape": "rectangle", "color": "light_grey"},
            {"id": "approval_l2", "label": "Approval L2", "type": "process", "shape": "rectangle", "color": "light_grey"},
            {"id": "approved", "label": "Approved?", "type": "decision", "shape": "diamond", "color": "light_orange"},
            {"id": "legal_rev", "label": "Legal Review", "type": "process", "shape": "rectangle", "color": "light_brown"},
            {"id": "case_res", "label": "Case Resolution", "type": "process", "shape": "rectangle", "color": "light_brown"},
            {"id": "closed", "label": "CLOSED", "type": "end", "shape": "circle", "color": "light_red"},
            {"id": "legal_action", "label": "LEGAL ACTION", "type": "end", "shape": "circle", "color": "light_pink"},
            {"id": "reject", "label": "Reject/Return", "type": "process", "shape": "rectangle", "color": "light_pink"}
        ],
        "connections": [
            {"from": "START", "to": "case_reg", "type": "solid"},
            {"from": "case_reg", "to": "data_val", "type": "solid"},
            {"from": "data_val", "to": "auto_assign", "type": "solid"},
            {"from": "auto_assign", "to": "case_alloc", "type": "solid", "label": "Yes"},
            {"from": "auto_assign", "to": "manual_assign", "type": "dashed", "label": "No"},
            {"from": "case_alloc", "to": "agency_inv", "type": "solid"},
            {"from": "manual_assign", "to": "regional_inv", "type": "solid"},
            {"from": "agency_inv", "to": "primary_rev", "type": "solid"},
            {"from": "regional_inv", "to": "primary_rev", "type": "solid"},
            {"from": "primary_rev", "to": "review_pass", "type": "solid"},
            {"from": "review_pass", "to": "final_rev", "type": "solid", "label": "Pass"},
            {"from": "review_pass", "to": "reject", "type": "dashed", "label": "Fail"},
            {"from": "reject", "to": "case_reg", "type": "dotted"},
            {"from": "final_rev", "to": "approval_l1", "type": "solid"},
            {"from": "approval_l1", "to": "approval_l2", "type": "solid"},
            {"from": "approval_l2", "to": "approved", "type": "solid"},
            {"from": "approved", "to": "case_res", "type": "solid", "label": "Approved"},
            {"from": "approved", "to": "legal_rev", "type": "dashed", "label": "Legal Required"},
            {"from": "case_res", "to": "closed", "type": "solid"},
            {"from": "legal_rev", "to": "legal_action", "type": "solid"}
        ],
        "color_legend": {
            "light_green": "#81C784 (Start)",
            "light_blue": "#64B5F6 (Data Processing)",
            "light_purple": "#BA68C8 (Investigation)",
            "light_coral": "#FF8A65 (Review)",
            "light_orange": "#FFB74D (Decision)",
            "light_grey": "#90A4AE (Approval)",
            "light_brown": "#A1887F (Resolution)",
            "light_red": "#E57373 (Closure)",
            "light_pink": "#F48FB1 (Rejection/Legal)"
        }
    }
    
    # Display export instructions
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Export Instructions for External Editing:**
        
        1. **For Miro/Lucidchart/Eraser:**
           - Use the structured data below to recreate the workflow
           - Apply the color scheme and shapes as specified
           - Maintain the connection types (solid/dashed/dotted)
        
        2. **For Microsoft Word:**
           - Use SmartArt Process diagrams
           - Insert shapes manually following the node specifications
           - Apply consistent formatting using the color legend
        
        3. **Key Design Principles:**
           - Circles for Start/End nodes
           - Rectangles for Process nodes  
           - Diamonds for Decision points
           - Consistent spacing to avoid overlaps
           - Text labels outside shapes for readability
        """)
    
    with col2:
        # Download structured data
        import json
        workflow_json = json.dumps(workflow_export_data, indent=2)
        st.download_button(
            label="📥 Download Workflow Data (JSON)",
            data=workflow_json,
            file_name="tathya_workflow_export.json",
            mime="application/json"
        )
        
        # Create simple text version for Word
        text_format = f"""TATHYA CASE MANAGEMENT WORKFLOW - COMPLETE PROCESS FLOW

WORKFLOW STAGES:
{chr(10).join([f"• {node['label']} ({node['type'].title()} - {node['shape'].title()})" for node in workflow_export_data['nodes']])}

CONNECTIONS:
{chr(10).join([f"• {conn['from']} → {conn['to']} ({conn['type']})" for conn in workflow_export_data['connections']])}

COLOR SCHEME:
{chr(10).join([f"• {color}: {desc}" for color, desc in workflow_export_data['color_legend'].items()])}
        """
        
        st.download_button(
            label="📄 Download Text Format",
            data=text_format,
            file_name="tathya_workflow_export.txt",
            mime="text/plain"
        )
    
    # Display the structured workflow data
    with st.expander("📋 View Detailed Workflow Structure", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Workflow Nodes:**")
            for node in workflow_export_data['nodes']:
                st.markdown(f"• **{node['label']}** - {node['type'].title()} ({node['shape']}, {node['color']})")
        
        with col2:
            st.markdown("**Workflow Connections:**")
            for conn in workflow_export_data['connections']:
                label = f" - {conn['label']}" if 'label' in conn else ""
                st.markdown(f"• {conn['from']} → {conn['to']} ({conn['type']}){label}")

def show_integration_map():
    """Display external integrations and API connections"""
    
    st.markdown("""
    <div class="architecture-section">
        <h2>🔗 Integration Architecture Map</h2>
        <p>External services, APIs, and third-party integrations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Integration mapping
    integrations = {
        'AI Services': {
            'Google Gemini': {'status': 'Active', 'purpose': 'Document Analysis, Smart Suggestions'},
            'DeepFace': {'status': 'Active', 'purpose': 'Facial Recognition, Identity Verification'},
            'Face++': {'status': 'Active', 'purpose': 'Advanced Face Matching'}
        },
        'Verification APIs': {
            'Timble Glance': {'status': 'Active', 'purpose': 'PAN Verification, Risk Assessment'},
            'MNRL API': {'status': 'Active', 'purpose': 'Mobile Number Verification'},
            'Aadhaar Verification': {'status': 'Planned', 'purpose': 'Identity Document Validation'}
        },
        'Communication': {
            'Gmail SMTP': {'status': 'Active', 'purpose': 'Email Notifications, Account Requests'},
            'Twilio': {'status': 'Active', 'purpose': 'SMS Notifications, Alerts'},
            'WhatsApp Business': {'status': 'Planned', 'purpose': 'Case Updates, Notifications'}
        },
        'Storage & Database': {
            'SQLite': {'status': 'Active', 'purpose': 'Case Data, User Management'},
            'File System': {'status': 'Active', 'purpose': 'Document Storage, Uploads'},
            'Cloud Storage': {'status': 'Planned', 'purpose': 'Backup, Scalability'}
        }
    }
    
    # Create integration network diagram
    fig = go.Figure()
    
    # Center node (Tathya Platform)
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers+text',
        marker=dict(
            size=120, 
            color='#1976D2',
            line=dict(width=4, color='white'),
            opacity=0.9
        ),
        text='Tathya<br>Platform',
        textposition="bottom center",
        textfont=dict(color='#2c3e50', size=16, family='Arial Black'),
        showlegend=False
    ))
    
    # Add integration categories
    import math
    
    category_positions = {
        'AI Services': {'angle': 0, 'radius': 3, 'color': '#ea4335'},
        'Verification APIs': {'angle': 90, 'radius': 3, 'color': '#34a853'},
        'Communication': {'angle': 180, 'radius': 3, 'color': '#fbbc04'},
        'Storage & Database': {'angle': 270, 'radius': 3, 'color': '#ff6d00'}
    }
    
    for category, pos in category_positions.items():
        x = pos['radius'] * math.cos(math.radians(pos['angle']))
        y = pos['radius'] * math.sin(math.radians(pos['angle']))
        
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=80, 
                color=pos['color'],
                line=dict(width=3, color='white'),
                opacity=0.9
            ),
            text=category,
            textposition="bottom center",
            textfont=dict(color='#2c3e50', size=12, family='Arial Black'),
            showlegend=False
        ))
        
        # Add connection line
        fig.add_trace(go.Scatter(
            x=[0, x], y=[0, y],
            mode='lines',
            line=dict(color='rgba(100,100,100,0.3)', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        title=dict(
            text="Integration Network Map",
            font=dict(size=20, family='Arial Black', color='#2c3e50')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4, 4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4, 4]),
        plot_bgcolor='#f8f9ff',
        paper_bgcolor='white',
        height=600,
        font=dict(size=14)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Integration details
    st.markdown("### 🔌 Integration Details")
    
    for category, services in integrations.items():
        with st.expander(f"{category} ({len(services)} services)"):
            for service, details in services.items():
                status_color = "🟢" if details['status'] == 'Active' else "🟡"
                st.markdown(f"""
                **{status_color} {service}**  
                Status: {details['status']}  
                Purpose: {details['purpose']}
                """)
    
    # Architecture best practices
    st.markdown("""
    <div class="workflow-box">
    <h4>🏆 Architecture Best Practices Implemented</h4>
    <ul>
    <li><strong>Microservices Pattern:</strong> Modular components with clear boundaries</li>
    <li><strong>API-First Design:</strong> All integrations through well-defined APIs</li>
    <li><strong>Security by Design:</strong> Role-based access and secure authentication</li>
    <li><strong>Scalability:</strong> Horizontal scaling capability with cloud readiness</li>
    <li><strong>Monitoring & Audit:</strong> Comprehensive logging and audit trails</li>
    <li><strong>Error Handling:</strong> Graceful degradation and error recovery</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)