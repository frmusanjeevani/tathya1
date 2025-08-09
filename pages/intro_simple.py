"""
Simple CSS-based intro animation as fallback
Lightweight alternative to Three.js version
"""
import streamlit as st
import time

def show():
    """Display simple animated intro with CSS"""
    
    # Hide Streamlit elements
    st.markdown("""
    <style>
    .stApp > header {visibility: hidden;}
    .stApp > div:first-child {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        margin: 0px;
        padding: 0px;
    }
    .block-container {
        padding: 0px;
        margin: 0px;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Simple CSS animation
    intro_html = """
    <div style="
        width: 100vw;
        height: 100vh;
        background: radial-gradient(ellipse at center, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 9999;
        animation: fadeIn 0.5s ease-in;
    ">
        <div style="
            text-align: center;
            animation: slideUp 1s ease-out 0.3s both;
        ">
            <h1 style="
                font-size: clamp(2.5rem, 6vw, 5rem);
                font-weight: 600;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 0 0 20px 0;
                letter-spacing: 3px;
                text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
            ">
                🕵️‍♂️ TATHYA
            </h1>
            <p style="
                font-size: clamp(1.2rem, 3vw, 2rem);
                color: rgba(255, 255, 255, 0.9);
                font-weight: 300;
                margin: 0;
                letter-spacing: 1px;
            ">
                Investigation Intelligence
            </p>
        </div>
        
        <div style="
            margin-top: 50px;
            animation: pulse 2s infinite;
        ">
            <div style="
                width: 60px;
                height: 60px;
                border: 3px solid transparent;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
        </div>
        
        <div style="
            position: absolute;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
            animation: fadeIn 1s ease-in 1.5s both;
        ">
            Loading...
        </div>
    </div>
    
    <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            h1 {
                font-size: 3rem !important;
            }
            p {
                font-size: 1.3rem !important;
            }
        }
    </style>
    
    <script>
        // Auto fade out after 2.5 seconds
        setTimeout(() => {
            document.body.style.animation = 'fadeOut 0.5s ease-out forwards';
        }, 2500);
    </script>
    """
    
    st.markdown(intro_html, unsafe_allow_html=True)
    
    # Auto-redirect timing
    if "intro_start_time" not in st.session_state:
        st.session_state.intro_start_time = time.time()
    
    # Check if 9 seconds have passed (extended duration)
    elapsed = time.time() - st.session_state.intro_start_time
    if elapsed >= 9.0:
        st.session_state.show_intro = False
        if "intro_start_time" in st.session_state:
            del st.session_state.intro_start_time
        st.rerun()
    
    # Small delay and rerun to check timing
    time.sleep(0.1)
    st.rerun()