# frontend_rental_peace.py
"""
RentalPeace - Modern Contract Assistant with Marketing Pages
Inspired by professional rental contract management platforms
"""

import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional, Any
import os
import time
from dotenv import load_dotenv
load_dotenv()
import pandas as pd

# Import backend classes
from backend import (
    DatabaseManager,
    UserManager,
    FileProcessor,
    CacheManager
)

# Use wrapper for delayed RAG system import
from langchain_rag_wrapper import create_rag_system

# ==================================================
# Custom CSS for RentalPeace Theme
# ==================================================

RENTAL_PEACE_CSS = """
<style>
    /* RentalPeace Color Scheme */
    :root {
        --primary-teal: #48C9B0;
        --light-teal: #E0F7F4;
        --teal-bg: #F0FFFE;
        --cream-bg: #FFFEF9;
        --text-dark: #2C3E50;
        --text-light: #7F8C8D;
        --accent-orange: #FF9A76;
    }
    
    /* Global background with gradient */
    .stApp {
        background: linear-gradient(135deg, 
            #F5F5DC 0%,      /* Light beige */
            #F0F0D0 30%,     /* More yellow-beige */
            #E8F4F8 50%,     /* Light blue-cyan */
            #D5F0F5 70%,     /* Cyan */
            #A8E6E3 85%,     /* Light teal */
            #7FDBDA 100%     /* Teal */
        );
        background-attachment: fixed;
        background-size: cover;
    }
    
    /* Make cards slightly transparent to show background */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Remove default padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Header styling */
    .rental-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 3rem;
        background: transparent;
        border-bottom: none;
    }
    
    .rental-logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-dark);
    }
    
    .rental-logo-underline {
        width: 100%;
        height: 2px;
        background: var(--text-dark);
        margin-top: 0.3rem;
    }
    
    /* Marketing page hero section */
    .hero-section {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6rem 3rem;
        gap: 4rem;
    }
    
    .hero-content {
        flex: 1;
        max-width: 650px;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        color: #2C3E50;
        line-height: 1.2;
        margin-bottom: 1.5rem;
    }
    
    .hero-title-accent {
        color: var(--primary-teal);
    }
    
    .hero-image-container {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .hero-image-container img {
        width: 100%;
        max-width: 500px;
        height: auto;
        border-radius: 20px;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-light);
        line-height: 1.8;
        margin-bottom: 2.5rem;
    }
    
    /* Buttons */
    .cta-button {
        display: inline-block;
        padding: 1.2rem 4rem;
        background: var(--primary-teal);
        color: white;
        font-size: 1.15rem;
        font-weight: 600;
        border-radius: 50px;
        text-decoration: none;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(72, 201, 176, 0.4);
        white-space: nowrap;
    }
    
    .cta-button:hover {
        background: #3AB89E;
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(72, 201, 176, 0.5);
    }
    
    /* Right-aligned button container */
    .button-container {
        text-align: right;
        margin-top: 2rem;
        padding-right: 3rem;
    }
    
    /* Streamlit button override for CTA */
    .stButton button[kind="primary"] {
        padding: 1.2rem 4rem !important;
        border-radius: 50px !important;
        font-size: 1.15rem !important;
        white-space: nowrap !important;
        min-width: 280px !important;
    }
    
    /* Role selection cards */
    .role-container {
        text-align: center;
        padding: 3rem 2rem;
    }
    
    .role-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2C3E50;
        margin-bottom: 1rem;
    }
    
    .role-subtitle {
        font-size: 1.1rem;
        color: var(--text-light);
        margin-bottom: 3rem;
    }
    
    .role-cards {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 2rem;
        flex-wrap: wrap;
    }
    
    .role-card {
        background: white;
        border-radius: 20px;
        padding: 3rem 2rem;
        width: 100%;
        max-width: 400px;
        border: 2px solid #E8E8E8;
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
    }
    
    .role-card h3 {
        text-align: center;
        color: #2C3E50;
    }
    
    .role-card p {
        text-align: center;
        color: var(--text-light);
    }
    
    .role-card:hover {
        border-color: var(--primary-teal);
        box-shadow: 0 8px 24px rgba(72, 201, 176, 0.15);
        transform: translateY(-5px);
    }
    
    .role-card:active {
        transform: translateY(-2px);
    }
    
    /* Hide the overlay buttons visually but keep them functional - ONLY for role selection */
    .role-card-container button[kind="secondary"] {
        display: none !important;
    }
    
    /* Hide primary buttons in role selection but keep functional */
    button[data-testid*="baseButton-primary"] {
        opacity: 0 !important;
        height: 400px !important;
    }
    
    /* Make the entire role card clickable using a wrapper approach */
    .role-card-wrapper {
        position: relative;
        cursor: pointer;
    }
    
    /* Adjust card position for clickability */
    .role-card {
        position: relative;
        z-index: 1;
        pointer-events: none;
    }
    
    /* Container positioning for role cards */
    .role-card-container {
        position: relative;
    }
    
    .role-icon {
        width: 80px;
        height: 80px;
        margin: 0 auto 1.5rem;
        background: var(--light-teal);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        border: 2px solid #E8E8E8;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 300px;
        display: flex;
        flex-direction: column;
    }
    
    .dashboard-card:hover {
        border-color: var(--primary-teal);
        box-shadow: 0 4px 16px rgba(72, 201, 176, 0.1);
    }
    
    .dashboard-card-icon {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .upload-card-icon {
        background: var(--light-teal);
        color: var(--primary-teal);
    }
    
    .qa-card-icon {
        background: #FFF9E6;
        color: #F9A825;
    }
    
    /* Document list */
    .document-item {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E8E8E8;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .document-item:hover {
        border-color: var(--primary-teal);
        box-shadow: 0 2px 8px rgba(72, 201, 176, 0.1);
    }
    
    .document-icon {
        width: 50px;
        height: 50px;
        background: var(--light-teal);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-teal);
        font-size: 1.5rem;
    }
    
    .document-info h4 {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-dark);
        margin: 0 0 0.3rem 0;
    }
    
    .document-info p {
        font-size: 0.9rem;
        color: var(--text-light);
        margin: 0;
    }
    
    .status-badge {
        background: var(--light-teal);
        color: var(--primary-teal);
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Chat interface */
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        border: 1px solid #E8E8E8;
        min-height: 400px;
    }
    
    .ai-ready-banner {
        background: var(--light-teal);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border-left: 4px solid var(--primary-teal);
    }
    
    .ai-ready-banner h4 {
        color: var(--primary-teal);
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    }
    
    .ai-ready-banner p {
        color: var(--text-light);
        margin: 0;
    }
    
    /* Chat message */
    .chat-message {
        background: #F8F9FA;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .chat-message-time {
        font-size: 0.85rem;
        color: var(--text-light);
        margin-top: 0.5rem;
    }
    
    /* Input styling */
    .stTextInput input, .stTextArea textarea {
        border: 2px solid #E8E8E8;
        border-radius: 10px;
        padding: 12px;
        background: white;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary-teal);
        box-shadow: 0 0 0 3px rgba(72, 201, 176, 0.1);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border: 3px dashed #E8E8E8;
        border-radius: 15px;
        padding: 3rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-teal);
        background: var(--teal-bg);
    }
    
    /* Buttons in Streamlit */
    .stButton button {
        background: var(--primary-teal);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(72, 201, 176, 0.2);
    }
    
    .stButton button:hover {
        background: #3AB89E;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(72, 201, 176, 0.3);
    }
    
    /* Back button */
    .back-button {
        color: var(--text-light);
        text-decoration: none;
        font-weight: 600;
        padding: 0.5rem 0;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .back-button:hover {
        color: var(--primary-teal);
    }
    
    /* Search box */
    .search-box {
        border: 2px solid #E8E8E8;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        width: 100%;
        background: white;
    }
    
    /* Welcome message */
    .welcome-section {
        padding: 2rem 0;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2C3E50;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: var(--text-light);
        margin-bottom: 2rem;
    }
    
    /* No documents message */
    .no-documents-message {
        color: #5A5A5A;
        font-size: 1rem;
        padding: 2rem;
        text-align: center;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F0F0F0;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-teal);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3AB89E;
    }
</style>
"""

# ==================================================
# Frontend Interface Class
# ==================================================

class RentalPeaceApp:
    """RentalPeace Application with Marketing Pages"""
    
    def __init__(self):
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.user_manager = UserManager(self.db_manager)
        self.file_processor = FileProcessor(self.db_manager)
        self.cache_manager = CacheManager(self.db_manager)
        
        # Initialize session state
        if 'page' not in st.session_state:
            st.session_state.page = 'marketing'  # marketing, role_select, login, main_app
        if 'user_role' not in st.session_state:
            st.session_state.user_role = None  # tenant or landlord
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'rag_system' not in st.session_state:
            st.session_state.rag_system = None
        if 'current_file_id' not in st.session_state:
            st.session_state.current_file_id = None
        if 'messages' not in st.session_state:
            st.session_state.messages = []
    
    def marketing_page(self):
        """Landing/Marketing Page"""
        st.markdown(RENTAL_PEACE_CSS, unsafe_allow_html=True)
        
        # Header - transparent with underline
        st.markdown("""
            <div class="rental-header">
                <div>
                    <div class="rental-logo">
                        <span>📄</span>
                        <span>RentalPeace</span>
                    </div>
                    <div class="rental-logo-underline"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Sign In button at top right
        col_space, col_signin = st.columns([9, 2])
        with col_signin:
            st.markdown("""
                <style>
                button[key="signin_marketing"] {
                    white-space: nowrap !important;
                    min-width: 100px !important;
                }
                </style>
            """, unsafe_allow_html=True)
            if st.button("Sign In", key="signin_marketing", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()
        
        # Hero Section - better spacing and layout
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1.3, 1], gap="large")
        
        with col1:
            st.markdown("""
                <div style="padding: 2rem 3rem;">
                    <h1 style="font-size: 4rem; font-weight: 700; color: #2C3E50; line-height: 1.2; margin-bottom: 1.5rem;">
                        Less Argument,<br>
                        <span style="color: #48C9B0;">More Peace of Mind</span>
                    </h1>
                    <p style="font-size: 1.25rem; color: #7F8C8D; line-height: 1.8; margin-bottom: 2.5rem;">
                        Upload your rental contract and get instant answers, summaries, 
                        and suggestions. Save time, reduce disputes, and make rental terms 
                        crystal clear.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # CTA Button - aligned to match text above
            st.markdown("<div style='padding: 0 3rem;'>", unsafe_allow_html=True)
            if st.button("Get Started Free", type="primary", key="cta_main", use_container_width=False):
                st.session_state.page = 'role_select'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Display the handshake image
            import base64
            from pathlib import Path
            
            # Try to load custom image
            image_path = Path("assets/handshake.jpg")
            if image_path.exists():
                with open(image_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                    st.markdown(f"""
                        <div style="padding: 2rem 2rem 2rem 0;">
                            <img src="data:image/jpeg;base64,{img_data}" 
                                 alt="Handshake illustration" 
                                 style="width: 100%; max-width: 500px; height: auto; border-radius: 20px; 
                                        box-shadow: 0 10px 30px rgba(72, 201, 176, 0.25);">
                        </div>
                    """, unsafe_allow_html=True)
            else:
                # Use gradient illustration
                st.markdown("""
                    <div style="padding: 2rem 2rem 2rem 0;">
                        <div style="background: linear-gradient(135deg, #5FA99C 0%, #48C9B0 50%, #BFDC7A 100%); 
                                    border-radius: 20px; padding: 3rem; position: relative; overflow: hidden;
                                    box-shadow: 0 10px 30px rgba(72, 201, 176, 0.25); height: 450px; display: flex;
                                    align-items: center; justify-content: center;">
                            <div style="text-align: center; z-index: 2;">
                                <div style="font-size: 10rem; margin-bottom: 1rem;">🤝</div>
                                <div style="font-size: 3.5rem;">📄</div>
                            </div>
                            <div style="position: absolute; bottom: 30px; left: 40px; font-size: 2.5rem;">🏢</div>
                            <div style="position: absolute; bottom: 30px; left: 120px; font-size: 2rem;">🌳</div>
                            <div style="position: absolute; bottom: 40px; right: 100px; font-size: 2.5rem;">🌳</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    def role_selection_page(self):
        """Role Selection Page"""
        st.markdown(RENTAL_PEACE_CSS, unsafe_allow_html=True)
        
        # Additional CSS for this page
        st.markdown("""
            <style>
            /* 标题为黑色 */
            .role-title {
                color: #2C3E50 !important;
            }
            /* 绿色按钮样式 */
            .role-button-container .stButton > button {
                background-color: #48C9B0 !important;
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 0.9rem 2rem !important;
                font-size: 1.1rem !important;
                font-weight: 600 !important;
                width: 100% !important;
                transition: all 0.3s ease !important;
            }
            .role-button-container .stButton > button:hover {
                background-color: #3DB89E !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(72, 201, 176, 0.3) !important;
            }
            /* 白色卡片和按钮之间的距离 */
            .button-spacing {
                margin-top: 2rem;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Back button
        col_back, col_space = st.columns([1, 5])
        with col_back:
            if st.button("← Back", key="back_to_marketing"):
                st.session_state.page = 'marketing'
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Title
        st.markdown("""
            <div class="role-container">
                <h1 class="role-title">I am a...</h1>
                <p class="role-subtitle">Choose your role to get started</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Role cards
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Tenant and Landlord cards side by side
            card_col1, card_col2 = st.columns(2)
            
            # Tenant Card
            with card_col1:
                # Display card
                st.markdown("""
                    <div class="role-card">
                        <div class="role-icon">👤</div>
                        <h3>Tenant</h3>
                        <p>I'm renting a property and need help understanding my tenancy agreement</p>
                    </div>
                    <div class="button-spacing"></div>
                """, unsafe_allow_html=True)
                
                # Button below card with spacing
                st.markdown('<div class="role-button-container">', unsafe_allow_html=True)
                if st.button("Continue as Tenant", key="tenant_btn", use_container_width=True):
                    st.session_state.user_role = 'tenant'
                    st.session_state.page = 'login'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Landlord Card
            with card_col2:
                # Display card
                st.markdown("""
                    <div class="role-card">
                        <div class="role-icon">🏠</div>
                        <h3>Landlord</h3>
                        <p>I manage rental properties and want to streamline contract management</p>
                    </div>
                    <div class="button-spacing"></div>
                """, unsafe_allow_html=True)
                
                # Button below card with spacing
                st.markdown('<div class="role-button-container">', unsafe_allow_html=True)
                if st.button("Continue as Landlord", key="landlord_btn", use_container_width=True):
                    st.session_state.user_role = 'landlord'
                    st.session_state.page = 'login'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
    def _ensure_demo_user(self):
        """Ensure demo user exists and auto-login"""
        role = st.session_state.user_role
        username = f"demo_{role}"
        
        # Try to login first
        result = self.user_manager.login(username, "demo123")
        
        if not result["success"]:
            # Register demo user
            result = self.user_manager.register_user(
                username, 
                f"{username}@rentalpeace.com", 
                "demo123"
            )
            # Login after registration
            result = self.user_manager.login(username, "demo123")
        
        if result["success"]:
            st.session_state.authenticated = True
            st.session_state.user_id = result["user_id"]
            st.session_state.username = result["username"]
    
    def login_page(self):
        """Login/Register Page"""
        st.markdown(RENTAL_PEACE_CSS, unsafe_allow_html=True)
        
        # Additional CSS for login page
        st.markdown("""
            <style>
            /* Login page specific styles */
            .login-container {
                max-width: 500px;
                margin: 0 auto;
                padding: 2rem 0;
            }
            .login-card {
                background: white;
                border-radius: 20px;
                padding: 2.5rem;
                box-shadow: 0 8px 24px rgba(0,0,0,0.1);
                border: 2px solid #F0F0D0;
            }
            .login-title {
                text-align: center;
                font-size: 2rem;
                font-weight: 700;
                color: #2C3E50;
                margin-bottom: 0.5rem;
            }
            .login-subtitle {
                text-align: center;
                color: #7F8C8D;
                margin-bottom: 2rem;
            }
            .login-header {
                text-align: center;
                padding: 2rem 0;
            }
            .login-header h1 {
                font-size: 2.5rem;
                color: #F9A825;
                margin-bottom: 0.5rem;
            }
            .login-header p {
                color: #7F8C8D;
            }
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 0;
                background: #F8F9FA;
                border-radius: 10px;
                padding: 0.25rem;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px;
                padding: 0.75rem 2rem;
                background: transparent;
                font-weight: 600;
                color: #7F8C8D;
            }
            .stTabs [aria-selected="true"] {
                background: #F9A825 !important;
                color: white !important;
            }
            /* Create Account button styling */
            [data-testid="stForm"] button[kind="secondary"] {
                background: var(--primary-teal) !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                padding: 0.75rem 2rem !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }
            [data-testid="stForm"] button[kind="secondary"]:hover {
                background: #3AB89E !important;
                transform: translateY(-2px) !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Back button
        col_back, col_space = st.columns([1, 5])
        with col_back:
            if st.button("← Back", key="back_from_login"):
                st.session_state.page = 'role_select'
                st.rerun()
        
        # Logo and title
        st.markdown("""
            <div class="login-header">
                <h1>📄</h1>
                <h1 style="color: #2C3E50; font-size: 2.5rem;">RentalPeace</h1>
                <p>Your Smart Contract Management System</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Login/Register tabs
            tab1, tab2 = st.tabs(["🔐 Login", "✨ Register"])
            
            with tab1:
                st.markdown('<h3 class="login-title">Welcome Back!</h3>', unsafe_allow_html=True)
                
                with st.form("login_form"):
                    st.text_input("👤 Username", key="login_username", placeholder="Enter your username")
                    st.text_input("🔒 Password", type="password", key="login_password", placeholder="Enter your password")
                    
                    submitted = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
                    
                    if submitted:
                        username = st.session_state.login_username
                        password = st.session_state.login_password
                        
                        if not username or not password:
                            st.error("❌ Please fill in all fields")
                        else:
                            with st.spinner("🔄 Verifying..."):
                                result = self.user_manager.login(username, password)
                                if result["success"]:
                                    st.session_state.authenticated = True
                                    st.session_state.user_id = result["user_id"]
                                    st.session_state.username = result["username"]
                                    st.session_state.page = 'main_app'
                                    st.success(f"✅ Welcome back, {result['username']}!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid username or password")
            
            with tab2:
                st.markdown('<h3 class="login-title">Create Your Account</h3>', unsafe_allow_html=True)
                
                with st.form("register_form"):
                    st.text_input("👤 Username", key="reg_username", placeholder="Choose a username")
                    st.text_input("📧 Email", key="reg_email", placeholder="your.email@example.com")
                    st.text_input("🔒 Password", type="password", key="reg_password", placeholder="Min. 6 characters")
                    st.text_input("🔒 Confirm Password", type="password", key="reg_confirm_password", placeholder="Re-enter password")
                    
                    submitted = st.form_submit_button("✨ Create Account", use_container_width=True)
                    
                    if submitted:
                        username = st.session_state.reg_username
                        email = st.session_state.reg_email
                        password = st.session_state.reg_password
                        confirm = st.session_state.reg_confirm_password
                        
                        if not all([username, email, password, confirm]):
                            st.error("❌ Please fill in all fields")
                        elif password != confirm:
                            st.error("❌ Passwords do not match")
                        elif len(password) < 6:
                            st.error("❌ Password must be at least 6 characters")
                        else:
                            with st.spinner("🔄 Creating account..."):
                                result = self.user_manager.register_user(username, email, password)
                                if result["success"]:
                                    # Auto login after registration
                                    login_result = self.user_manager.login(username, password)
                                    if login_result["success"]:
                                        st.session_state.authenticated = True
                                        st.session_state.user_id = login_result["user_id"]
                                        st.session_state.username = login_result["username"]
                                        st.session_state.page = 'main_app'
                                        st.success("✅ Account created successfully!")
                                        st.rerun()
                                else:
                                    st.error(f"❌ {result.get('message', 'Registration failed')}")
    
    def init_user_rag_system(self):
        """Initialize user's RAG system"""
        if st.session_state.rag_system is None:
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                
                if not api_key:
                    st.error("⚠️ OpenAI API Key not found!")
                    st.info("Please set up your API key in the .env file")
                    st.session_state.rag_init_failed = True
                    st.stop()
                
                st.session_state.rag_system = create_rag_system(
                    api_key=api_key,
                    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
                )
                
                user_cache_dir = Path(f"user_data/{st.session_state.user_id}/cache")
                user_cache_dir.mkdir(parents=True, exist_ok=True)
                st.session_state.rag_system.cache_dir = user_cache_dir
            except Exception as e:
                st.error(f"⚠️ Failed to initialize RAG system: {e}")
                st.session_state.rag_init_failed = True
                st.stop()
        
        if st.session_state.get('rag_init_failed', False):
            st.error("⚠️ RAG system initialization failed")
            st.stop()
    
    def main_dashboard(self):
        """Main Dashboard Page"""
        st.markdown(RENTAL_PEACE_CSS, unsafe_allow_html=True)
        
        # Initialize RAG system
        self.init_user_rag_system()
        
        # Header with back button
        col_back, col_h1, col_h2 = st.columns([1, 5, 1])
        
        with col_back:
            if st.button("← Back", key="back_to_role"):
                st.session_state.page = 'role_select'
                st.rerun()
        
        with col_h1:
            st.markdown("""
                <div class="rental-logo" style="padding: 1rem 0;">
                    <span>📄</span>
                    <span>RentalPeace</span>
                </div>
            """, unsafe_allow_html=True)
        
        with col_h2:
            role_display = st.session_state.username if st.session_state.username else "User"
            st.markdown(f"""
                <div style="padding: 1rem 0; text-align: right;">
                    <span style="background: var(--light-teal); color: var(--primary-teal); 
                                 padding: 0.75rem 2rem; border-radius: 20px; font-weight: 600;
                                 font-size: 1.1rem;">
                        👤 {role_display}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            # Log out button below username - smaller and semi-transparent white
            st.markdown("""
                <style>
                div[data-testid="column"]:last-child button[kind="secondary"] {
                    background: rgba(255, 255, 255, 0.5) !important;
                    color: #2C3E50 !important;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    padding: 0.4rem 1rem !important;
                    font-size: 0.9rem !important;
                }
                </style>
            """, unsafe_allow_html=True)
            if st.button("🚪 Log Out", key="logout_dashboard"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.page = 'marketing'
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Welcome section
        st.markdown(f"""
            <div class="welcome-section">
                <h1 class="welcome-title" style="color: #2C3E50;">Welcome back! 👋</h1>
                <p class="welcome-subtitle">Manage your rental contracts and get instant answers</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Additional CSS for equal height cards
        st.markdown("""
            <style>
            /* Equal height cards - make them flatter */
            .dashboard-card {
                min-height: 220px !important;
                height: 220px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 1.5rem;
            }
            /* Make Ask Question card clickable */
            .clickable-card {
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .clickable-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Action cards - equal height
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Simple file uploader card - same size as Ask Question card
            uploaded_file = st.file_uploader(
                "Drag and drop file here", 
                type=['pdf', 'docx'], 
                key="main_upload",
                help="Limit 200MB per file • PDF, DOCX"
            )
            
            if uploaded_file:
                if st.button("🚀 Process Contract", type="primary", use_container_width=True, key="process_btn"):
                    with st.spinner("⏳ Processing your contract..."):
                        result = self.file_processor.process_and_save_file(
                            st.session_state.user_id,
                            uploaded_file,
                            st.session_state.rag_system
                        )
                        
                        if result["success"]:
                            st.session_state.current_file_id = result["file_id"]
                            st.session_state.messages = []
                            st.success("✅ Contract processed successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result.get('error', 'Processing failed')}")
        
        with col2:
            # Create a container that always has the same height
            if st.session_state.current_file_id:
                # Create a clickable card using a styled button
                st.markdown("""
                    <style>
                    /* Style the Q&A button to look exactly like a white card */
                    button[key="qa_card_btn"] {
                        width: 100% !important;
                        height: 220px !important;
                        background: white !important;
                        border: 1px solid #e0e0e0 !important;
                        border-radius: 15px !important;
                        padding: 3rem 2.5rem !important;
                        transition: all 0.3s ease !important;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
                        cursor: pointer !important;
                        display: flex !important;
                        flex-direction: column !important;
                        align-items: center !important;
                        justify-content: center !important;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
                        margin: 0 !important;
                    }
                    button[key="qa_card_btn"]:hover {
                        box-shadow: 0 8px 16px rgba(0,0,0,0.15) !important;
                        transform: translateY(-5px) !important;
                        border-color: #7FDBDA !important;
                        background: white !important;
                    }
                    button[key="qa_card_btn"]:active {
                        background: white !important;
                    }
                    button[key="qa_card_btn"] > div {
                        display: flex !important;
                        flex-direction: column !important;
                        align-items: center !important;
                        justify-content: center !important;
                        width: 100% !important;
                        height: 100% !important;
                    }
                    button[key="qa_card_btn"] p {
                        margin: 0 !important;
                        padding: 0 !important;
                        color: #000000 !important;
                        text-align: center !important;
                        line-height: 2 !important;
                        white-space: pre-line !important;
                    }
                    /* Style for the icon emoji */
                    button[key="qa_card_btn"] p:first-child {
                        font-size: 3rem !important;
                        margin-bottom: 1.2rem !important;
                        display: block !important;
                        line-height: 1 !important;
                    }
                    /* Style for the title */
                    button[key="qa_card_btn"] p:nth-child(2) {
                        font-size: 1.35rem !important;
                        font-weight: 600 !important;
                        margin-bottom: 0.6rem !important;
                        color: #2c3e50 !important;
                    }
                    /* Style for the description */
                    button[key="qa_card_btn"] p:nth-child(3) {
                        font-size: 1rem !important;
                        color: #000000 !important;
                        opacity: 0.8 !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Button with all content inside - using line breaks
                if st.button("💬\n\nAsk a Question\n\nGet instant AI-powered answers", key="qa_card_btn", use_container_width=True):
                    st.session_state.show_qa = True
                    st.rerun()
            else:
                # Non-clickable card when no file uploaded
                st.markdown("""
                    <div class="dashboard-card" style="margin: 0;">
                        <div class="dashboard-card-icon qa-card-icon">💬</div>
                        <h3 style="color: var(--text-dark); margin-bottom: 0.5rem;">Ask a Question</h3>
                        <p style="color: var(--text-light);">Get instant AI-powered answers</p>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Your Documents section
        col_title, col_search = st.columns([2, 1])
        with col_title:
            st.markdown('<h2 style="color: var(--text-dark);">Your Documents</h2>', unsafe_allow_html=True)
        with col_search:
            st.text_input("🔍 Search documents...", key="search_docs", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Document list
        recent_files = self.file_processor.get_recent_files(st.session_state.user_id, limit=10)
        
        if recent_files:
            for file in recent_files:
                col_doc1, col_doc2, col_doc3, col_doc4 = st.columns([0.5, 3, 1, 1])
                
                with col_doc1:
                    st.markdown("""
                        <div class="document-icon">📄</div>
                    """, unsafe_allow_html=True)
                
                with col_doc2:
                    st.markdown(f"""
                        <div class="document-info">
                            <h4>{file['filename']}</h4>
                            <p>Uploaded on {file['upload_time'][:10]}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_doc3:
                    st.markdown('<div class="status-badge">active</div>', unsafe_allow_html=True)
                
                with col_doc4:
                    if st.button("Open Q&A", key=f"open_qa_{file['file_id']}", use_container_width=True):
                        if self.file_processor.load_processed_file(
                            st.session_state.user_id,
                            file['file_id'],
                            st.session_state.rag_system
                        ):
                            st.session_state.current_file_id = file['file_id']
                            st.session_state.show_qa = True
                            st.session_state.messages = []
                            st.rerun()
                
                st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="no-documents-message">
                    📭 No documents uploaded yet. Upload your first contract to get started!
                </div>
            """, unsafe_allow_html=True)
    
    def qa_interface(self):
        """Q&A Chat Interface"""
        st.markdown(RENTAL_PEACE_CSS, unsafe_allow_html=True)
        
        # Initialize RAG system
        self.init_user_rag_system()
        
        # Get current file info
        recent_files = self.file_processor.get_recent_files(st.session_state.user_id)
        current_file_info = None
        for file in recent_files:
            if file['file_id'] == st.session_state.current_file_id:
                current_file_info = file
                break
        
        # Header with back button
        col_back, col_title, col_view = st.columns([1, 4, 1])
        
        with col_back:
            if st.button("← Back", key="back_to_dashboard"):
                st.session_state.show_qa = False
                st.rerun()
        
        with col_title:
            if current_file_info:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">📄</span>
                        <span style="font-size: 1.2rem; font-weight: 600; color: var(--text-dark);">
                            {current_file_info['filename'][:50]}...
                        </span>
                    </div>
                """, unsafe_allow_html=True)
        
        with col_view:
            # Display username and logout button
            username_display = st.session_state.username if st.session_state.username else "User"
            st.markdown(f"""
                <div style="text-align: right; margin-bottom: 0.5rem;">
                    <span style="background: var(--light-teal); color: var(--primary-teal); 
                                 padding: 0.75rem 2rem; border-radius: 20px; font-weight: 600;
                                 font-size: 1.1rem; display: inline-block;">
                        👤 {username_display}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            # Smaller semi-transparent white logout button - right aligned
            st.markdown("""
                <style>
                div[data-testid="column"]:nth-child(3) button {
                    background: rgba(255, 255, 255, 0.5) !important;
                    color: #2C3E50 !important;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    padding: 0.3rem 0.8rem !important;
                    font-size: 0.8rem !important;
                    float: right !important;
                    width: auto !important;
                    min-width: 80px !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            col_space, col_logout = st.columns([1, 1])
            with col_logout:
                if st.button("🚪 Log Out", key="logout_qa"):
                    # Clear all session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state.page = 'marketing'
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # AI Ready banner
        st.markdown("""
            <div class="ai-ready-banner">
                <h4>✨ AI Assistant Ready</h4>
                <p>I've analyzed your contract and can answer questions with citations. Ask me anything!</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Chat messages
        if not st.session_state.messages:
            # Initial greeting
            st.markdown("""
                <div class="chat-message">
                    <div style="display: flex; align-items: flex-start; gap: 1rem;">
                        <div style="font-size: 1.5rem;">🤖</div>
                        <div style="flex: 1;">
                            <p style="margin: 0; color: var(--text-dark);">
                                Hello! I've analyzed your tenancy agreement. Feel free to ask me any questions about 
                                rent increases, maintenance responsibilities, deposit terms, or any other clauses in 
                                your contract.
                            </p>
                            <div class="chat-message-time">18:42:21</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
                        <div style="background: var(--primary-teal); color: white; 
                                    border-radius: 12px; padding: 1rem; max-width: 70%;">
                            {message["content"]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message">
                        <div style="display: flex; align-items: flex-start; gap: 1rem;">
                            <div style="font-size: 1.5rem;">🤖</div>
                            <div style="flex: 1;">
                                <p style="margin: 0; color: var(--text-dark);">{message["content"]}</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        col_input, col_send = st.columns([5, 1])
        
        with col_input:
            user_question = st.text_input(
                "Ask a question about your tenancy agreement...",
                key="chat_input",
                label_visibility="collapsed",
                placeholder="Ask a question about your tenancy agreement..."
            )
        
        with col_send:
            send_button = st.button("➤", key="send_btn", use_container_width=True)
        
        if send_button and user_question:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_question})
            
            # Get AI response
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.rag_system.ask_question(user_question)
                
                # Save to history
                self.cache_manager.save_qa_history(
                    st.session_state.user_id,
                    st.session_state.current_file_id,
                    user_question,
                    response["answer"],
                    response.get("sources", [])
                )
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"]
                })
            
            st.rerun()
        
        # Footer note
        st.markdown("""
            <div style="text-align: center; color: var(--text-light); 
                        font-size: 0.9rem; margin-top: 2rem; padding-top: 1rem; 
                        border-top: 1px solid #E8E8E8;">
                AI responses include relevant contract clauses with citations
            </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run application"""
        st.set_page_config(
            page_title="RentalPeace - Smart Contract Assistant",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Route to appropriate page
        if st.session_state.page == 'marketing':
            self.marketing_page()
        elif st.session_state.page == 'role_select':
            self.role_selection_page()
        elif st.session_state.page == 'login':
            self.login_page()
        elif st.session_state.page == 'main_app':
            if st.session_state.get('show_qa', False):
                self.qa_interface()
            else:
                self.main_dashboard()


# ==================================================
# Application Entry Point
# ==================================================

if __name__ == "__main__":
    app = RentalPeaceApp()
    app.run()
