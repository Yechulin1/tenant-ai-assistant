# frontend.py
"""
Frontend Interface Layer
Built with Streamlit for user interface
Handles all page rendering and user interactions
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
# Frontend Interface Class
# ==================================================

class ContractAssistantApp:
    """Main application class"""
    
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
    
    def apply_custom_css(self):
        """Apply custom CSS for better UI"""
        st.markdown("""
        <style>
        /* Main color scheme */
        :root {
            --primary-color: #4A90E2;
            --secondary-color: #50C878;
            --accent-color: #FF6B6B;
            --background-light: #F8F9FA;
            --text-dark: #2C3E50;
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Card styling */
        .info-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid #4A90E2;
            margin-bottom: 1rem;
        }
        
        /* Button styling enhancement */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #F8F9FA;
            padding: 0.5rem;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* Metric styling */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #4A90E2;
            font-weight: 700;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Success/Error message styling */
        .stSuccess {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            border-radius: 8px;
        }
        
        .stError {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            border-radius: 8px;
        }
        
        .stWarning {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 8px;
        }
        
        .stInfo {
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            border-radius: 8px;
        }
        
        /* Chat message styling */
        .stChatMessage {
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        /* Input styling */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 2px solid #e9ecef;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #4A90E2;
            box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.25);
        }
        
        /* File uploader styling */
        [data-testid="stFileUploader"] {
            border: 2px dashed #4A90E2;
            border-radius: 10px;
            padding: 2rem;
            background-color: #f8f9fa;
        }
        
        /* Quick question buttons */
        .quick-question-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0.25rem;
        }
        
        /* DataFrame styling */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 8px;
            font-weight: 500;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def login_page(self):
        """Login page"""
        # Apply custom CSS
        self.apply_custom_css()
        
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Header with gradient background
            st.markdown("""
            <div class="main-header">
                <h1>📄 Contract Assistant</h1>
                <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">
                    AI-Powered Contract Analysis Platform
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🔐 Login", "✨ Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    result = self.user_manager.login(username, password)
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user_id = result["user_id"]
                        st.session_state.username = result["username"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Register")
                
                if submitted:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        result = self.user_manager.register_user(
                            new_username, new_email, new_password
                        )
                        if result["success"]:
                            st.success("Registration successful! Please login")
                        else:
                            st.error(result.get("message", "Registration failed"))
    
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
                    
                    **Or set temporarily (PowerShell):**
                    ```powershell
                    $env:OPENAI_API_KEY="your_api_key_here"
                    streamlit run app.py
                    ```
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
                # Mark initialization as failed
                st.session_state.rag_init_failed = True
                st.stop()
        
        # Check if previous initialization failed
        if st.session_state.get('rag_init_failed', False):
            st.error("⚠️ RAG system initialization failed. Please check configuration or contact administrator")
            st.stop()
    
    def main_app(self):
        """Main application interface"""
        st.set_page_config(page_title="Contract Assistant", page_icon="📄", layout="wide")
        
        # Apply custom CSS
        self.apply_custom_css()
        
        # Initialize RAG system
        self.init_user_rag_system()
        
        # Sidebar with enhanced styling
        with st.sidebar:
            # User info card
            st.markdown(f"""
            <div class="info-card">
                <h3 style="margin: 0; color: #667eea;">👤 {st.session_state.username}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 0.9rem;">
                    ID: {st.session_state.user_id}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", use_container_width=True, type="primary"):
                # Clean up RAG system on logout
                if st.session_state.rag_system:
                    st.session_state.rag_system.clear_all_documents()
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            
            st.divider()
            
            # Display recent files with enhanced styling
            st.markdown("### 📁 Recent Files")
            recent_files = self.file_processor.get_recent_files(st.session_state.user_id)
            
            if recent_files:
                for file in recent_files:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"""
                            <div style="padding: 0.5rem; background: white; border-radius: 8px; margin-bottom: 0.5rem;">
                                <p style="margin: 0; font-weight: 500; color: #2c3e50;">📄 {file['filename'][:25]}...</p>
                                <p style="margin: 0; font-size: 0.8rem; color: #6c757d;">
                                    {file['num_pages']} pages • {file['num_chunks']} chunks
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            if st.button("📂", key=f"load_{file['file_id']}", help="Load this file", use_container_width=True):
                                if self.file_processor.load_processed_file(
                                    st.session_state.user_id,
                                    file['file_id'],
                                    st.session_state.rag_system
                                ):
                                    st.session_state.current_file_id = file['file_id']
                                # Clear chat history when switching files
                                st.session_state.messages = []
                                st.success("File loaded successfully")
                                st.rerun()
                    
                    # Display file info
                    with st.expander(f"Details"):
                        st.write(f"Pages: {file['num_pages']}")
                        st.write(f"Chunks: {file['num_chunks']}")
                        st.write(f"Upload time: {file['upload_time']}")
            else:
                st.info("📭 No files uploaded yet")
        
        # Main interface with enhanced header
        st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0;">📄 Smart Contract Assistant</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
                AI-powered contract analysis and Q&A system
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current file information bar with enhanced styling
        current_file_info = None
        if st.session_state.current_file_id:
            # Get current file details
            for file in recent_files:
                if file['file_id'] == st.session_state.current_file_id:
                    current_file_info = file
                    break
            
            if current_file_info:
                st.markdown(f"""
                <div class="info-card" style="background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border-left: 4px solid #4CAF50;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0; color: #2E7D32;">📄 {current_file_info['filename']}</h3>
                            <p style="margin: 0.5rem 0 0 0; color: #558B2F;">
                                {current_file_info['num_pages']} pages • {current_file_info['num_chunks']} chunks
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🔄 Switch File", type="secondary"):
                    st.session_state.current_file_id = None
                    st.session_state.messages = []
                    # Clean RAG system when switching files
                    st.session_state.rag_system.clear_all_documents()
                    st.rerun()
            else:
                st.info(f"Current file ID: {st.session_state.current_file_id}")
        else:
            st.warning("📂 Please select or upload a file from the sidebar")
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📤 Upload", "💬 Q&A", "📝 Summary", "🔍 Extract", "📊 Compare"
        ])
        
        # Tab1: Upload with enhanced styling
        with tab1:
            st.markdown("### 📤 Upload Contract Document")
            st.markdown("Upload your PDF contract file for AI-powered analysis")
            
            uploaded_file = st.file_uploader(
                "Choose a PDF file", 
                type=['pdf'],
                help="Supported format: PDF (max 200MB)"
            )
            
            if uploaded_file:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.info(f"📄 Selected: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
                with col2:
                    process_btn = st.button("🚀 Process File", type="primary", use_container_width=True)
                
                if process_btn:
                    with st.spinner("🔄 Processing your contract..."):
                        result = self.file_processor.process_and_save_file(
                            st.session_state.user_id,
                            uploaded_file,
                            st.session_state.rag_system
                        )
                        
                        if result["success"]:
                            st.session_state.current_file_id = result["file_id"]
                            # Clear chat history when uploading new file
                            st.session_state.messages = []
                            st.balloons()
                            st.success("✅ File processed successfully!")
                            
                            # Display statistics with enhanced cards
                            st.markdown("### 📊 Processing Statistics")
                            stats = result.get("stats", {})
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📄 Pages", stats.get("pages", 0), delta="Analyzed")
                            with col2:
                                st.metric("🧩 Chunks", stats.get("chunks", 0), delta="Indexed")
                            with col3:
                                st.metric("📝 Characters", f"{stats.get('characters', 0):,}", delta="Processed")
                        else:
                            st.error(result.get("error", "Processing failed"))
        
        # Tab2: Q&A
        with tab2:
            if not st.session_state.current_file_id:
                st.warning("Please upload or load a file first")
            else:
                # Display current contract information
                if current_file_info:
                    st.info(f"🎯 Current Q&A context: **{current_file_info['filename']}**")
                
                # Display RAG system status (for debugging)
                if st.checkbox("🔍 Show System Status (Debug)", value=False):
                    try:
                        rag_info = st.session_state.rag_system.get_current_documents_info()
                        st.code(rag_info)
                        
                        # Display statistics
                        stats = st.session_state.rag_system.get_statistics()
                        st.json(stats)
                    except Exception as e:
                        st.error(f"Cannot retrieve system status: {e}")
                
                # Quick question buttons - Classic rental contract questions
                st.markdown("#### 💡 Quick Questions")
                st.markdown("<p style='color: #6c757d; margin-bottom: 1rem;'>Click any question to get instant answers</p>", unsafe_allow_html=True)
                
                quick_questions = [
                    ("💰 Rent Amount", "What is the monthly rent amount?"),
                    ("📅 Lease Duration", "What is the lease duration and start date?"),
                    ("🔒 Security Deposit", "How much is the security deposit?"),
                    ("🐾 Pet Policy", "What are the pet policies?"),
                    ("🔧 Maintenance", "Who is responsible for maintenance and repairs?"),
                    ("⚠️ Termination", "What are the conditions for early termination?")
                ]
                
                # Display buttons in 2 rows of 3 columns with enhanced styling
                col1, col2, col3 = st.columns(3)
                cols = [col1, col2, col3]
                
                for idx, (label, question) in enumerate(quick_questions):
                    with cols[idx % 3]:
                        if st.button(label, key=f"quick_q_{idx}", use_container_width=True, help=question, type="secondary"):
                            # Store the clicked question to be processed
                            st.session_state.quick_question = question
                            st.rerun()
                
                st.divider()
                
                # Process quick question if clicked
                if st.session_state.get('quick_question'):
                    prompt = st.session_state.quick_question
                    del st.session_state.quick_question  # Clear after retrieving
                    
                    # Verify document status
                    try:
                        current_docs = st.session_state.rag_system.get_current_documents_info()
                        if not current_docs or current_docs == "No documents loaded":
                            st.error("❌ System error: No documents loaded, please reload contract")
                        else:
                            # Add user question to messages
                            st.session_state.messages.append({"role": "user", "content": prompt})
                            
                            # Get answer
                            with st.spinner("Thinking..."):
                                response = st.session_state.rag_system.ask_question(prompt)
                                
                                # Save to history
                                self.cache_manager.save_qa_history(
                                    st.session_state.user_id,
                                    st.session_state.current_file_id,
                                    prompt,
                                    response["answer"],
                                    response.get("sources", [])
                                )
                                
                                # Save assistant message to history
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": response["answer"],
                                    "sources": response.get("sources", [])
                                })
                            
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error processing question: {e}")
                
                # Chat interface - display message history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                        # Display sources if available
                        if message.get("sources"):
                            with st.expander("📚 Sources"):
                                for source in message["sources"]:
                                    st.write(f"• {source}")
                
                # Input box
                if prompt := st.chat_input("Ask about the contract..."):
                    # Verify document status before answering
                    try:
                        current_docs = st.session_state.rag_system.get_current_documents_info()
                        if not current_docs or current_docs == "No documents loaded":
                            st.error("❌ System error: No documents loaded, please reload contract")
                            st.stop()
                    except Exception as e:
                        st.error(f"❌ Document verification failed: {e}")
                        st.stop()
                    
                    # Display user question immediately
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.write(prompt)
                    
                    # Show assistant thinking
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = st.session_state.rag_system.ask_question(prompt)
                            
                            # Save to history
                            self.cache_manager.save_qa_history(
                                st.session_state.user_id,
                                st.session_state.current_file_id,
                                prompt,
                                response["answer"],
                                response.get("sources", [])
                            )
                            
                            # Display answer
                            st.write(response["answer"])
                            
                            # Display sources
                            if response.get("sources"):
                                with st.expander("📚 Source References", expanded=True):
                                    for i, source in enumerate(response["sources"], 1):
                                        st.markdown(f"**📄 Source {i} - Page {source.get('page', 'N/A')}**")
                                        
                                        content = source.get('content', '')
                                        
                                        # Display preview (first 500 chars)
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
                                            # Display preview
                                            st.text_area(
                                                f"Source preview_{i}",
                                                content[:preview_length] + "...",
                                                height=150,
                                                key=f"source_preview_{i}",
                                                label_visibility="collapsed"
                                            )
                                            
                                            # Provide option to view full content
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
                            
                            # Save assistant message to history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response["answer"],
                                "sources": response.get("sources", [])
                            })
                
                # Clear chat history button
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Clear Chat"):
                        st.session_state.messages = []
                        # Also clear RAG system memory
                        if hasattr(st.session_state.rag_system, 'memory'):
                            st.session_state.rag_system.memory.clear()
                        st.rerun()
        
        # Tab3: Summary
        with tab3:
            if not st.session_state.current_file_id:
                st.warning("Please upload or load a file first")
            else:
                summary_type = st.selectbox(
                    "Summary Type",
                    ["brief", "comprehensive", "key_points"]
                )
                
                if st.button("Generate Summary"):
                    # Check cache first
                    cached = self.cache_manager.get_cached_summary(
                        st.session_state.current_file_id,
                        summary_type
                    )
                    
                    if cached:
                        st.success("Using cached summary")
                        # Escape $ symbols to prevent LaTeX rendering
                        escaped_cached = cached.replace('$', r'\$')
                        st.markdown(escaped_cached)
                    else:
                        with st.spinner("Generating summary..."):
                            summary = st.session_state.rag_system.summarize_contract(
                                summary_type=summary_type
                            )
                            
                            # Save to cache
                            self.cache_manager.save_summary(
                                st.session_state.current_file_id,
                                st.session_state.user_id,
                                summary_type,
                                summary
                            )
                            
                            # Escape $ symbols to prevent LaTeX rendering
                            escaped_summary = summary.replace('$', r'\$')
                            st.markdown(escaped_summary)
        
        # Tab4: Information Extraction
        with tab4:
            if not st.session_state.current_file_id:
                st.warning("Please upload or load a file first")
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader("📋 Contract Key Information Extraction")
                with col2:
                    if st.button("🔄 Re-extract", help="Clear cache and extract again"):
                        # Clear extraction cache for this file
                        import sqlite3
                        conn = sqlite3.connect(self.db_manager.db_path)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM extracted_info_cache WHERE file_id = ?", 
                                     (st.session_state.current_file_id,))
                        conn.commit()
                        conn.close()
                        st.success("Cache cleared")
                        st.rerun()
                
                if st.button("🔍 Extract Key Information", type="primary"):
                    # Check cache
                    cached = self.cache_manager.get_cached_extraction(
                        st.session_state.current_file_id
                    )
                    
                    if cached:
                        st.info("✅ Using cached extraction result (faster)")
                        key_info = cached
                    else:
                        with st.spinner("⏳ Extracting key information... (optimized, ~10-15 seconds)"):
                            key_info = st.session_state.rag_system.extract_key_information()
                            
                            # Check for errors
                            if "error" not in key_info:
                                # Save to cache
                                self.cache_manager.save_extraction(
                                    st.session_state.current_file_id,
                                    st.session_state.user_id,
                                    key_info
                                )
                                st.success("✅ Extraction complete! Result cached")
                            else:
                                st.error(f"Extraction failed: {key_info['error']}")
                    
                    # Display result - optimized table display
                    if key_info and "error" not in key_info:
                        # English field mapping
                        field_names = {
                            "rent_amount": "Rent Amount",
                            "lease_duration": "Lease Duration",
                            "security_deposit": "Security Deposit",
                            "payment_due_date": "Payment Due Date",
                            "late_fee": "Late Fee",
                            "pet_policy": "Pet Policy",
                            "maintenance": "Maintenance",
                            "termination": "Early Termination",
                            "utilities": "Utilities",
                            "parking": "Parking"
                        }
                        
                        df = pd.DataFrame([
                            {"Key Information": field_names.get(k, k), "Details": v} 
                            for k, v in key_info.items()
                        ])
                        
                        st.dataframe(
                            df, 
                            width='stretch',
                            height=400,
                            hide_index=True
                        )
        
        # Tab5: Compare (simplified)
        with tab5:
            st.info("Load two files to compare")
            
            # Get all processed files
            all_files = self.file_processor.get_recent_files(st.session_state.user_id, limit=20)
            
            if len(all_files) < 2:
                st.warning("At least 2 files required for comparison")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    file1_options = {f['file_id']: f['filename'] for f in all_files}
                    file1_id = st.selectbox("Select File 1", options=list(file1_options.keys()), 
                                           format_func=lambda x: file1_options[x])
                
                with col2:
                    file2_options = {f['file_id']: f['filename'] for f in all_files if f['file_id'] != file1_id}
                    if file2_options:
                        file2_id = st.selectbox("Select File 2", options=list(file2_options.keys()), 
                                               format_func=lambda x: file2_options[x])
                    else:
                        st.warning("Please select different files")
                        file2_id = None
                
                if file1_id and file2_id and st.button("Start Comparison"):
                    st.info("Comparison feature under development...")
    
    def run(self):
        """Run application"""
        if st.session_state.authenticated:
            self.main_app()
        else:
            self.login_page()
