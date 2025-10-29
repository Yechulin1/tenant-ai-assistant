# frontend_modern.py
"""
Modern Frontend Interface Layer with Enhanced UI
Built with Streamlit for user interface
Features: Light yellow theme, modern design, smooth interactions
"""

import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional, Any
import os
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
# Custom CSS for Modern UI with Light Yellow Theme
# ==================================================

CUSTOM_CSS = """
<style>
    /* Main color scheme - Light Yellow Theme */
    :root {
        --primary-yellow: #FFF9E6;
        --secondary-yellow: #FFECB3;
        --accent-yellow: #FFD54F;
        --dark-yellow: #F9A825;
        --text-dark: #4A4A4A;
        --text-light: #6B6B6B;
        --border-color: #FFE082;
        --shadow-color: rgba(255, 193, 7, 0.15);
    }
    
    /* Global background */
    .stApp {
        background: linear-gradient(135deg, #FFF9E6 0%, #FFFBF0 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFF4D6 0%, #FFE9B8 100%);
        border-right: 2px solid var(--border-color);
        box-shadow: 4px 0 15px var(--shadow-color);
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #FFD54F 0%, #FFCA28 100%);
        color: var(--text-dark);
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 4px 12px var(--shadow-color);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(135deg, #FFC107 0%, #FFB300 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px var(--shadow-color);
    }
    
    /* Main content area */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Title styling */
    h1 {
        color: var(--dark-yellow);
        font-weight: 700;
        text-shadow: 2px 2px 4px var(--shadow-color);
        padding: 1rem 0;
        border-bottom: 3px solid var(--accent-yellow);
        margin-bottom: 2rem;
    }
    
    h2, h3 {
        color: var(--text-dark);
        font-weight: 600;
    }
    
    /* Card-like containers */
    .stExpander {
        background: white;
        border: 2px solid var(--border-color);
        border-radius: 15px;
        box-shadow: 0 4px 12px var(--shadow-color);
        margin: 1rem 0;
    }
    
    .stExpander:hover {
        box-shadow: 0 6px 18px var(--shadow-color);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #FFD54F 0%, #FFCA28 100%);
        color: var(--text-dark);
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 600;
        box-shadow: 0 4px 12px var(--shadow-color);
        transition: all 0.3s ease;
        font-size: 16px;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #FFC107 0%, #FFB300 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 20px var(--shadow-color);
    }
    
    .stButton button:active {
        transform: translateY(-1px);
    }
    
    /* Primary button variant */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #F9A825 0%, #F57F17 100%);
        color: white;
        font-weight: 700;
    }
    
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #F57F17 0%, #E65100 100%);
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        border: 2px solid var(--border-color);
        border-radius: 10px;
        padding: 12px;
        background: white;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent-yellow);
        box-shadow: 0 0 0 3px var(--shadow-color);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border: 3px dashed var(--border-color);
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-yellow);
        background: var(--primary-yellow);
    }
    
    /* Success/Info/Warning/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 5px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
    }
    
    .stInfo {
        background: linear-gradient(135deg, #FFF9E6 0%, #FFECB3 100%);
        border-left: 5px solid var(--dark-yellow);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px var(--shadow-color);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-left: 5px solid #FF9800;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.2);
    }
    
    .stError {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border-left: 5px solid #F44336;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(244, 67, 54, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        border-radius: 15px;
        padding: 8px;
        box-shadow: 0 4px 12px var(--shadow-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        color: var(--text-dark);
        background: var(--primary-yellow);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--secondary-yellow);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FFD54F 0%, #FFCA28 100%);
        color: var(--text-dark);
        box-shadow: 0 4px 12px var(--shadow-color);
    }
    
    /* Chat messages */
    .stChatMessage {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px var(--shadow-color);
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        box-shadow: 0 6px 18px var(--shadow-color);
        transform: translateX(5px);
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px var(--shadow-color);
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px var(--shadow-color);
    }
    
    [data-testid="stMetricValue"] {
        color: var(--dark-yellow);
        font-weight: 700;
        font-size: 2rem;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px var(--shadow-color);
        border: 2px solid var(--border-color);
    }
    
    /* Select box */
    .stSelectbox > div > div {
        border: 2px solid var(--border-color);
        border-radius: 10px;
        background: white;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--dark-yellow) !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-yellow), transparent);
        margin: 2rem 0;
    }
    
    /* Form styling */
    .stForm {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 12px var(--shadow-color);
        border: 2px solid var(--border-color);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--primary-yellow);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-yellow);
        border-radius: 10px;
        border: 2px solid var(--primary-yellow);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--dark-yellow);
    }
    
    /* Animation for page load */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main .block-container > div {
        animation: fadeIn 0.5s ease-out;
    }
</style>
"""

# ==================================================
# Frontend Interface Class
# ==================================================

class ContractAssistantApp:
    """Main application class with modern UI"""
    
    def __init__(self):
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.user_manager = UserManager(self.db_manager)
        self.file_processor = FileProcessor(self.db_manager)
        self.cache_manager = CacheManager(self.db_manager)
        
        # Initialize session state
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
    
    def login_page(self):
        """Login page with modern design"""
        # Inject CSS first
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Title with emoji
            st.markdown("""
                <div style='text-align: center; padding: 2rem 0;'>
                    <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>📄</h1>
                    <h1 style='color: #F9A825; margin-top: 0;'>Contract Assistant</h1>
                    <p style='color: #6B6B6B; font-size: 1.2rem;'>Your Smart Contract Management System</p>
                </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🔐 Login", "✨ Register"])
            
            with tab1:
                with st.form("login_form"):
                    st.markdown("### Welcome Back!")
                    username = st.text_input("👤 Username", placeholder="Enter your username")
                    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                    
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    with col_b:
                        submitted = st.form_submit_button("🚀 Login", use_container_width=True)
                    
                    if submitted:
                        if not username or not password:
                            st.error("⚠️ Please fill in all fields")
                        else:
                            result = self.user_manager.login(username, password)
                            if result["success"]:
                                st.session_state.authenticated = True
                                st.session_state.user_id = result["user_id"]
                                st.session_state.username = result["username"]
                                st.success("✅ Login successful! Redirecting...")
                                st.rerun()
                            else:
                                st.error("❌ Invalid username or password")
            
            with tab2:
                with st.form("register_form"):
                    st.markdown("### Create Your Account")
                    new_username = st.text_input("👤 Username", placeholder="Choose a username")
                    new_email = st.text_input("📧 Email", placeholder="your.email@example.com")
                    new_password = st.text_input("🔒 Password", type="password", placeholder="Min. 6 characters")
                    confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password")
                    
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    with col_b:
                        submitted = st.form_submit_button("✨ Create Account", use_container_width=True)
                    
                    if submitted:
                        if not all([new_username, new_email, new_password, confirm_password]):
                            st.error("⚠️ Please fill in all fields")
                        elif new_password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif len(new_password) < 6:
                            st.error("⚠️ Password must be at least 6 characters")
                        else:
                            result = self.user_manager.register_user(
                                new_username, new_email, new_password
                            )
                            if result["success"]:
                                st.success("🎉 Registration successful! Please login")
                            else:
                                st.error(f"❌ {result.get('message', 'Registration failed')}")
    
    def init_user_rag_system(self):
        """Initialize user's RAG system"""
        if st.session_state.rag_system is None:
            try:
                # Get API key
                api_key = os.getenv("OPENAI_API_KEY")
                
                # Check if API key exists
                if not api_key:
                    st.error("⚠️ OpenAI API Key not found!")
                    st.info("""
                    **Please follow these steps to set up API Key:**
                    
                    1. Create a `.env` file in project root directory
                    2. Add the following content:
                    ```
                    OPENAI_API_KEY=your_api_key_here
                    OPENAI_MODEL=gpt-3.5-turbo
                    ```
                    3. Restart the Streamlit application
                    """)
                    st.session_state.rag_init_failed = True
                    st.stop()
                
                # Use wrapper to create RAG instance with delay
                st.session_state.rag_system = create_rag_system(
                    api_key=api_key,
                    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
                )
                # Set user-specific cache directory
                user_cache_dir = Path(f"user_data/{st.session_state.user_id}/cache")
                user_cache_dir.mkdir(parents=True, exist_ok=True)
                st.session_state.rag_system.cache_dir = user_cache_dir
            except Exception as e:
                st.error(f"⚠️ Failed to initialize RAG system: {e}")
                import traceback
                st.code(traceback.format_exc())
                st.session_state.rag_init_failed = True
                st.stop()
        
        if st.session_state.get('rag_init_failed', False):
            st.error("⚠️ RAG system initialization failed. Please check configuration or contact administrator")
            st.stop()
    
    def main_app(self):
        """Main application interface with modern design"""
        # Inject custom CSS
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        
        # Initialize RAG system
        self.init_user_rag_system()
        
        # Sidebar
        with st.sidebar:
            st.markdown(f"""
                <div style='text-align: center; padding: 1rem; background: white; border-radius: 15px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(255, 193, 7, 0.15);'>
                    <h2 style='margin: 0; color: #F9A825;'>👤</h2>
                    <h3 style='margin: 0.5rem 0; color: #4A4A4A;'>{st.session_state.username}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", use_container_width=True):
                if st.session_state.rag_system:
                    st.session_state.rag_system.clear_all_documents()
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            
            st.divider()
            
            # Display recent files
            st.markdown("### 📁 Recent Files")
            recent_files = self.file_processor.get_recent_files(st.session_state.user_id)
            
            if recent_files:
                for file in recent_files:
                    with st.container():
                        st.markdown(f"""
                            <div style='background: white; padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; 
                                        border: 2px solid #FFE082; transition: all 0.3s ease;'>
                                <p style='margin: 0; color: #4A4A4A; font-weight: 600;'>📄 {file['filename'][:25]}...</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📂 Load", key=f"load_{file['file_id']}", use_container_width=True):
                                if self.file_processor.load_processed_file(
                                    st.session_state.user_id,
                                    file['file_id'],
                                    st.session_state.rag_system
                                ):
                                    st.session_state.current_file_id = file['file_id']
                                    st.session_state.messages = []
                                    st.success("✅ Loaded!")
                                    st.rerun()
                        
                        with col2:
                            with st.expander("ℹ️"):
                                st.write(f"📄 Pages: {file['num_pages']}")
                                st.write(f"🔢 Chunks: {file['num_chunks']}")
                                st.write(f"🕒 {file['upload_time'][:16]}")
            else:
                st.info("📭 No files uploaded yet")
        
        # Main interface
        st.markdown("""
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h1 style='font-size: 2.5rem; color: #F9A825; text-shadow: 2px 2px 4px rgba(255, 193, 7, 0.2);'>
                    📄 Smart Contract Assistant
                </h1>
                <p style='color: #6B6B6B; font-size: 1.1rem;'>AI-Powered Contract Analysis & Management</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Current file information bar
        current_file_info = None
        if st.session_state.current_file_id:
            for file in recent_files:
                if file['file_id'] == st.session_state.current_file_id:
                    current_file_info = file
                    break
            
            if current_file_info:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); 
                                    padding: 1rem; border-radius: 10px; border-left: 5px solid #4CAF50;'>
                            <p style='margin: 0; color: #2E7D32; font-weight: 600;'>
                                📄 Current file: <strong>{current_file_info['filename']}</strong>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.metric("📄 Pages", current_file_info['num_pages'])
                with col3:
                    st.metric("🔢 Chunks", current_file_info['num_chunks'])
                with col4:
                    if st.button("🔄 Switch", use_container_width=True):
                        st.session_state.current_file_id = None
                        st.session_state.messages = []
                        st.session_state.rag_system.clear_all_documents()
                        st.rerun()
        else:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); 
                            padding: 1.5rem; border-radius: 15px; text-align: center; 
                            border: 2px dashed #FFE082; margin-bottom: 2rem;'>
                    <h3 style='color: #F57F17; margin: 0;'>📂 Please upload or select a file to get started</h3>
                </div>
            """, unsafe_allow_html=True)
        
        # Tabs with icons
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📤 Upload", "💬 Q&A", "📝 Summary", "🔍 Extract", "📊 Compare"
        ])
        
        # Tab1: Upload
        with tab1:
            st.markdown("### 📤 Upload Your Contract")
            
            uploaded_file = st.file_uploader(
                "Choose a PDF contract file",
                type=['pdf'],
                help="Upload a PDF contract for analysis"
            )
            
            if uploaded_file:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🚀 Process File", type="primary", use_container_width=True):
                        with st.spinner("⏳ Processing your contract..."):
                            result = self.file_processor.process_and_save_file(
                                st.session_state.user_id,
                                uploaded_file,
                                st.session_state.rag_system
                            )
                            
                            if result["success"]:
                                st.session_state.current_file_id = result["file_id"]
                                st.session_state.messages = []
                                st.success("🎉 File processed successfully!")
                                
                                # Display statistics with modern cards
                                stats = result.get("stats", {})
                                st.markdown("### 📊 Processing Results")
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("📄 Pages", stats.get("pages", 0))
                                with col_b:
                                    st.metric("🔢 Chunks", stats.get("chunks", 0))
                                with col_c:
                                    st.metric("📝 Characters", f"{stats.get('characters', 0):,}")
                            else:
                                st.error(f"❌ {result.get('error', 'Processing failed')}")
        
        # Tab2: Q&A
        with tab2:
            if not st.session_state.current_file_id:
                st.markdown("""
                    <div style='text-align: center; padding: 3rem;'>
                        <h2 style='color: #F9A825;'>💬 Q&A System</h2>
                        <p style='color: #6B6B6B; font-size: 1.2rem;'>Please upload or load a file first to start asking questions</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Display current contract information
                if current_file_info:
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); 
                                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem; 
                                    border-left: 5px solid #2196F3;'>
                            <p style='margin: 0; color: #1565C0; font-weight: 600;'>
                                🎯 Current Q&A context: <strong>{current_file_info['filename']}</strong>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Display message history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                        if message.get("sources"):
                            with st.expander("📚 View Sources"):
                                for source in message["sources"]:
                                    st.write(f"• {source}")
                
                # Input box
                if prompt := st.chat_input("💭 Ask about the contract..."):
                    # Verify document status
                    try:
                        current_docs = st.session_state.rag_system.get_current_documents_info()
                        if not current_docs or current_docs == "No documents loaded":
                            st.error("❌ No documents loaded, please reload contract")
                            st.stop()
                    except Exception as e:
                        st.error(f"❌ Document verification failed: {e}")
                        st.stop()
                    
                    # Display user question
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.write(prompt)
                    
                    # Show assistant response
                    with st.chat_message("assistant"):
                        with st.spinner("🤔 Thinking..."):
                            response = st.session_state.rag_system.ask_question(prompt)
                            
                            # Save to history
                            self.cache_manager.save_qa_history(
                                st.session_state.user_id,
                                st.session_state.current_file_id,
                                prompt,
                                response["answer"],
                                response.get("sources", [])
                            )
                            
                            st.write(response["answer"])
                            
                            # Display sources
                            if response.get("sources"):
                                with st.expander("📚 Source References", expanded=True):
                                    for i, source in enumerate(response["sources"], 1):
                                        st.markdown(f"**📄 Source {i} - Page {source.get('page', 'N/A')}**")
                                        
                                        content = source.get('content', '')
                                        preview_length = 500
                                        
                                        if len(content) <= preview_length:
                                            st.text_area(
                                                f"Source content_{i}",
                                                content,
                                                height=150,
                                                key=f"source_preview_{i}",
                                                label_visibility="collapsed"
                                            )
                                        else:
                                            st.text_area(
                                                f"Source preview_{i}",
                                                content[:preview_length] + "...",
                                                height=150,
                                                key=f"source_preview_{i}",
                                                label_visibility="collapsed"
                                            )
                                            
                                            with st.expander(f"🔍 View Full Content ({len(content)} chars)"):
                                                st.text_area(
                                                    f"Full content_{i}",
                                                    content,
                                                    height=300,
                                                    key=f"source_full_{i}",
                                                    label_visibility="collapsed"
                                                )
                                        
                                        if i < len(response["sources"]):
                                            st.divider()
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response["answer"],
                                "sources": response.get("sources", [])
                            })
                
                # Clear chat button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("🗑️ Clear Chat", use_container_width=True):
                        st.session_state.messages = []
                        if hasattr(st.session_state.rag_system, 'memory'):
                            st.session_state.rag_system.memory.clear()
                        st.rerun()
        
        # Tab3: Summary
        with tab3:
            if not st.session_state.current_file_id:
                st.markdown("""
                    <div style='text-align: center; padding: 3rem;'>
                        <h2 style='color: #F9A825;'>📝 Contract Summary</h2>
                        <p style='color: #6B6B6B; font-size: 1.2rem;'>Please upload or load a file first</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("### 📝 Generate Contract Summary")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    summary_type = st.selectbox(
                        "Choose summary type",
                        ["brief", "comprehensive", "key_points"],
                        format_func=lambda x: {
                            "brief": "📋 Brief Summary",
                            "comprehensive": "📖 Comprehensive Analysis",
                            "key_points": "🎯 Key Points"
                        }[x]
                    )
                
                with col2:
                    if st.button("✨ Generate", type="primary", use_container_width=True):
                        # Check cache
                        cached = self.cache_manager.get_cached_summary(
                            st.session_state.current_file_id,
                            summary_type
                        )
                        
                        if cached:
                            st.success("✅ Using cached summary")
                            st.markdown(f"""
                                <div style='background: white; padding: 2rem; border-radius: 15px; 
                                            border: 2px solid #FFE082; box-shadow: 0 4px 12px rgba(255, 193, 7, 0.15);'>
                                    {cached}
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            with st.spinner("⏳ Generating summary..."):
                                summary = st.session_state.rag_system.summarize_contract(
                                    summary_type=summary_type
                                )
                                
                                self.cache_manager.save_summary(
                                    st.session_state.current_file_id,
                                    st.session_state.user_id,
                                    summary_type,
                                    summary
                                )
                                
                                st.markdown(f"""
                                    <div style='background: white; padding: 2rem; border-radius: 15px; 
                                                border: 2px solid #FFE082; box-shadow: 0 4px 12px rgba(255, 193, 7, 0.15);'>
                                        {summary}
                                    </div>
                                """, unsafe_allow_html=True)
        
        # Tab4: Information Extraction
        with tab4:
            if not st.session_state.current_file_id:
                st.markdown("""
                    <div style='text-align: center; padding: 3rem;'>
                        <h2 style='color: #F9A825;'>🔍 Information Extraction</h2>
                        <p style='color: #6B6B6B; font-size: 1.2rem;'>Please upload or load a file first</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("### 📋 Extract Key Contract Information")
                with col2:
                    if st.button("🔄 Re-extract", help="Clear cache and extract again"):
                        import sqlite3
                        conn = sqlite3.connect(self.db_manager.db_path)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM extracted_info_cache WHERE file_id = ?", 
                                     (st.session_state.current_file_id,))
                        conn.commit()
                        conn.close()
                        st.success("✅ Cache cleared")
                        st.rerun()
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    if st.button("🔍 Extract Key Information", type="primary", use_container_width=True):
                        cached = self.cache_manager.get_cached_extraction(
                            st.session_state.current_file_id
                        )
                        
                        if cached:
                            st.success("✅ Using cached extraction result")
                            key_info = cached
                        else:
                            with st.spinner("⏳ Extracting information... (~10-15 seconds)"):
                                key_info = st.session_state.rag_system.extract_key_information()
                                
                                if "error" not in key_info:
                                    self.cache_manager.save_extraction(
                                        st.session_state.current_file_id,
                                        st.session_state.user_id,
                                        key_info
                                    )
                                    st.success("✅ Extraction complete!")
                                else:
                                    st.error(f"❌ {key_info['error']}")
                        
                        # Display results
                        if key_info and "error" not in key_info:
                            field_names = {
                                "rent_amount": "💰 Rent Amount",
                                "lease_duration": "📅 Lease Duration",
                                "security_deposit": "🔒 Security Deposit",
                                "payment_due_date": "📆 Payment Due Date",
                                "late_fee": "⏰ Late Fee",
                                "pet_policy": "🐾 Pet Policy",
                                "maintenance": "🔧 Maintenance",
                                "termination": "⚠️ Early Termination",
                                "utilities": "💡 Utilities",
                                "parking": "🚗 Parking"
                            }
                            
                            df = pd.DataFrame([
                                {"Key Information": field_names.get(k, k), "Details": v} 
                                for k, v in key_info.items()
                            ])
                            
                            st.markdown("### 📊 Extracted Information")
                            st.dataframe(
                                df, 
                                use_container_width=True,
                                height=400,
                                hide_index=True
                            )
        
        # Tab5: Compare
        with tab5:
            st.markdown("### 📊 Compare Contracts")
            st.info("🚧 Load two files to compare their contents")
            
            all_files = self.file_processor.get_recent_files(st.session_state.user_id, limit=20)
            
            if len(all_files) < 2:
                st.warning("⚠️ At least 2 files required for comparison")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    file1_options = {f['file_id']: f['filename'] for f in all_files}
                    file1_id = st.selectbox(
                        "📄 Select File 1",
                        options=list(file1_options.keys()),
                        format_func=lambda x: file1_options[x]
                    )
                
                with col2:
                    file2_options = {f['file_id']: f['filename'] for f in all_files if f['file_id'] != file1_id}
                    if file2_options:
                        file2_id = st.selectbox(
                            "📄 Select File 2",
                            options=list(file2_options.keys()),
                            format_func=lambda x: file2_options[x]
                        )
                    else:
                        st.warning("Please select different files")
                        file2_id = None
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    if file1_id and file2_id and st.button("🔄 Start Comparison", type="primary", use_container_width=True):
                        st.info("🚧 Comparison feature under development...")
    
    def run(self):
        """Run application"""
        # Must be the first Streamlit command
        st.set_page_config(
            page_title="Contract Assistant",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        if st.session_state.authenticated:
            self.main_app()
        else:
            self.login_page()


# ==================================================
# Application Entry Point
# ==================================================

if __name__ == "__main__":
    app = ContractAssistantApp()
    app.run()
