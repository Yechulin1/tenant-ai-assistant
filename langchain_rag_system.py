# advanced_rag_system.py
"""
Advanced Contract Management System - Implemented with LangChain
Supports PDF parsing, contract summarization, intelligent Q&A, and more
"""

import os
from typing import List, Dict, Optional, Tuple
import hashlib
import pickle
from datetime import datetime

# LangChain Core Components - Updated to langchain 0.3+ API
from langchain_community.document_loaders.pdf import PyMuPDFLoader, PDFPlumberLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import (
    RetrievalQA, 
    ConversationalRetrievalChain,
    LLMChain
)
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain

from langchain.retrievers.contextual_compression import ContextualCompressionRetriever

from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.callbacks.manager import get_openai_callback

# Utilities
import numpy as np
from pathlib import Path
import json
from dotenv import load_dotenv
load_dotenv()

class AdvancedContractRAG:
    """
    Advanced Contract RAG System
    Features:
    - Robust PDF parsing (supports complex formats)
    - Intelligent document chunking
    - Semantic vector search
    - Automatic contract summarization
    - Conversational memory
    - Multi-language support
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", language: str = "en"):
        """
        Initialize advanced RAG system
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-3.5-turbo, gpt-4, etc.)
            language: Language setting (en, zh, etc.)
        """
        self.api_key = api_key
        self.model = model
        self.language = language
        
        # Set proxy if needed
        proxies = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        if proxies:
            os.environ["OPENAI_PROXY"] = proxies

        # Initialize OpenAI components - Adapted for langchain 0.3+ API
        self.llm = ChatOpenAI(
            temperature=0.01,
            model=model,  # langchain 0.3+ uses 'model' parameter
            api_key=api_key,  # langchain 0.3+ uses 'api_key' parameter
            max_tokens=500,
            timeout=60
        )
        
        self.embeddings = OpenAIEmbeddings(
            api_key=api_key  # langchain 0.3+ uses 'api_key' parameter
        )
        
        # Text splitter - Intelligent chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000,        # Chunk size
            chunk_overlap=200,       # Overlap to maintain context
            length_function=len,
            separators=["\n\n", "\n", "。", ".", " ", ""]  # Supports Chinese and English
        )
        
        # Vector store
        self.vectorstore = None
        self.retriever = None
        
        # Conversation memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            input_key="question",   # Input field is named 'question'
            output_key="answer",
            return_messages=True,
            k=5  # Remember last 5 conversation rounds
        )
        
        # Store loaded documents
        self.documents = {}
        self.contract_metadata = {}
        
        # Cache directory
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
    def load_pdf(self, pdf_path: str, use_cache: bool = True) -> Dict:
        """
        Load and parse PDF file
        
        Args:
            pdf_path: PDF file path
            use_cache: Whether to use cache
            
        Returns:
            Dictionary containing parsing results
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"success": False, "error": f"File not found: {pdf_path}"}
        
        # Ensure only one document is loaded
        if self.ensure_single_document(str(pdf_path)):
            # If same file already loaded, return directly
            return {
                "success": True, 
                "message": "Document already loaded",
                "stats": self.contract_metadata.get(str(pdf_path), {})
            }
    
        
        # Check cache
        cache_key = self._get_cache_key(pdf_path)
        cache_path = self.cache_dir / f"{cache_key}.pkl"
        
        if use_cache and cache_path.exists():
            print(f"📂 Loading from cache: {cache_path}")
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
                self.documents[str(pdf_path)] = cached_data['documents']
                self._rebuild_vectorstore()
                return {"success": True, "message": "Loaded from cache", "stats": cached_data['stats']}
        
        print(f"📄 Loading PDF: {pdf_path}")
        
        # Try multiple PDF loaders
        documents = None
        loader_used = None
        
        # Method 1: PDFPlumber (best table support)
        try:
            loader = PDFPlumberLoader(str(pdf_path))
            documents = loader.load()
            loader_used = "PDFPlumber"
            print(f"✅ Successfully loaded with PDFPlumber")
        except Exception as e:
            print(f"⚠️ PDFPlumber failed: {e}")
        
        # Method 2: PyMuPDF (most accurate text extraction)
        if documents is None or len(documents) == 0:
            try:
                loader = PyMuPDFLoader(str(pdf_path))
                documents = loader.load()
                loader_used = "PyMuPDF"
                print(f"✅ Successfully loaded with PyMuPDF")
            except Exception as e:
                print(f"⚠️ PyMuPDF failed: {e}")
        
        if documents is None or len(documents) == 0:
            return {"success": False, "error": "Failed to extract text from PDF"}
        
        # Extract metadata
        total_pages = len(documents)
        total_text = " ".join([doc.page_content for doc in documents])
        total_chars = len(total_text)
        
        # Intelligent document chunking
        split_documents = self.text_splitter.split_documents(documents)
        
        # Add metadata to each chunk
        for i, doc in enumerate(split_documents):
            doc.metadata.update({
                "source": str(pdf_path),
                "chunk_id": i,
                "loader": loader_used,
                "timestamp": datetime.now().isoformat()
            })
        
        # Store documents
        self.documents[str(pdf_path)] = split_documents
        
        # Update vector store
        self._rebuild_vectorstore()
        
        # Statistics
        stats = {
            "file": pdf_path.name,
            "pages": total_pages,
            "characters": total_chars,
            "chunks": len(split_documents),
            "loader": loader_used,
            "avg_chunk_size": total_chars // len(split_documents) if split_documents else 0
        }
        
        # Cache processing results
        if use_cache:
            cache_data = {
                "documents": split_documents,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            print(f"💾 Cached to: {cache_path}")
        
        # Store contract metadata
        self.contract_metadata[str(pdf_path)] = stats
        
        return {"success": True, "message": f"Successfully loaded {pdf_path.name}", "stats": stats}
    
    def _get_cache_key(self, file_path: Path) -> str:
        """Generate file cache key"""
        stat = file_path.stat()
        unique_str = f"{file_path}_{stat.st_size}_{stat.st_mtime}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def _rebuild_vectorstore(self):
        """Rebuild vector store"""
        all_documents = []
        for docs in self.documents.values():
            all_documents.extend(docs)
        
        if all_documents:
            print(f"🔄 Building vector store with {len(all_documents)} chunks...")
            self.vectorstore = FAISS.from_documents(
                all_documents,
                self.embeddings
            )
            
            # Create enhanced retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="mmr",  # Maximum Marginal Relevance
                search_kwargs={
                    "k": 5,  # Return 5 most relevant chunks
                    "fetch_k": 10  # First fetch 10 candidates
                }
            )
            print(f"✅ Vector store ready")
    
    def summarize_contract(self, pdf_path: Optional[str] = None, 
                          summary_type: str = "comprehensive") -> str:
        """
        Generate contract summary
        
        Args:
            pdf_path: Specific PDF path, None to summarize all loaded documents
            summary_type: Summary type
                - "brief": Short summary (1-2 paragraphs)
                - "comprehensive": Comprehensive summary (includes all key terms)
                - "key_points": Key points list
                
        Returns:
            Summary text
        """
        if not self.documents:
            return "No documents loaded. Please load a contract first."
        
        # Get documents to summarize
        if pdf_path and pdf_path in self.documents:
            docs_to_summarize = self.documents[pdf_path]
        else:
            # Most recent document
            last_key = next(reversed(self.documents.keys()))
            docs_to_summarize = self.documents[last_key]

        # Choose prompt template based on type
        if summary_type == "brief":
            prompt_template = """
            Provide a brief 1-2 paragraph summary of this rental contract.
            Focus on the most important terms: rent amount, duration, and key obligations.
            
            Contract content:
            {text}
            
            Brief Summary:
            """
        elif summary_type == "key_points":
            prompt_template = """
            Extract and list the key points from this rental contract.
            Format as a numbered list covering:
            1. Rental amount and payment terms
            2. Lease duration and dates
            3. Security deposit details
            4. Maintenance responsibilities
            5. Termination conditions
            6. Important restrictions or rules
            7. Any special clauses
            
            Contract content:
            {text}
            
            Key Points:
            """
        else:  # comprehensive
            prompt_template = """
            Provide a comprehensive summary of this rental contract.
            Include all important sections:
            - Parties and Property Details
            - Financial Terms (rent, deposits, fees)
            - Lease Period and Renewal
            - Responsibilities (tenant vs landlord)
            - Rules and Restrictions
            - Termination and Penalties
            - Special Conditions
            
            Contract content:
            {text}
            
            Comprehensive Summary:
            """
        
        # Create summarization chain
        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
        
        with get_openai_callback() as cb:
            if len(docs_to_summarize) > 20:
                # Long document uses map_reduce strategy
                chain = load_summarize_chain(
                    self.llm,
                    chain_type="map_reduce",
                    map_prompt=prompt,
                    combine_prompt=prompt
                )
            else:
                # Short document uses stuff strategy
                chain = load_summarize_chain(
                    self.llm,
                    chain_type="stuff",
                    prompt=prompt
                )
            
            summary = chain.run(docs_to_summarize)
            
            print(f"📊 Summary generated - Tokens used: {cb.total_tokens}, Cost: ${cb.total_cost:.4f}")
        
        return summary
    
    def ask_question(self, question: str, use_compression: bool = True) -> Dict:
        """
        Ask questions about the contract
        
        Args:
            question: User question
            use_compression: Whether to use context compression
            
        Returns:
            Dictionary containing answer and sources
        """
        if not self.vectorstore:
            return {
                "answer": "No contract loaded. Please upload a PDF contract first.",
                "sources": []
            }

        # Select retriever (with or without compression)
        if use_compression:
            compressor = LLMChainExtractor.from_llm(self.llm)
            retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=self.retriever
            )
        else:
            retriever = self.retriever

        # Don't pass memory to chain; manually pass chat_history
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=True,
            verbose=False,
            output_key="answer"  # Main output is 'answer'
        )

        # Get history from local memory and pass to chain
        try:
            history_vars = self.memory.load_memory_variables({})
            chat_history = history_vars.get("chat_history", [])
        except Exception:
            chat_history = []

        # Execute
        with get_openai_callback() as cb:
            result = qa_chain.invoke({
                "question": question,
                "chat_history": chat_history
            })

        # Manually save this round of Q&A to memory (only store question/answer)
        try:
            self.memory.save_context({"question": question}, {"answer": result.get("answer", "")})
        except Exception:
            pass

        # Format sources
        sources = []
        for doc in result.get("source_documents", []):
            sources.append({
                "content": doc.page_content if doc.page_content else "",
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "Unknown")
            })

        return {
            "answer": result.get("answer", ""),
            "sources": sources,
            "tokens_used": cb.total_tokens if "cb" in locals() else 0
        }
    
    def compare_contracts(self, pdf_path1: str, pdf_path2: str) -> str:
        """
        Compare differences between two contracts
        
        Args:
            pdf_path1: First contract path
            pdf_path2: Second contract path
            
        Returns:
            Comparison results
        """
        if pdf_path1 not in self.documents or pdf_path2 not in self.documents:
            return "Both contracts must be loaded first."
        
        prompt = PromptTemplate(
            template="""
            Compare these two rental contracts and highlight the key differences:
            
            Contract 1:
            {contract1}
            
            Contract 2:
            {contract2}
            
            Provide a detailed comparison covering:
            1. Rent amount differences
            2. Lease term differences
            3. Deposit variations
            4. Different rules or restrictions
            5. Maintenance responsibility changes
            6. Any other significant differences
            
            Comparison:
            """,
            input_variables=["contract1", "contract2"]
        )
        
        # Get summaries of both contracts
        summary1 = self.summarize_contract(pdf_path1, "comprehensive")
        summary2 = self.summarize_contract(pdf_path2, "comprehensive")
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        comparison = chain.run(contract1=summary1, contract2=summary2)
        
        return comparison
    
    def extract_key_information(self) -> Dict:
        """
        Extract contract key information to structured format - Optimized version (batch extraction)
        
        Returns:
            Dictionary containing key information
        """
        if not self.vectorstore:
            return {"error": "No contract loaded"}
        
        # Optimized: Use a concise prompt to extract all key information at once
        extraction_prompt = """IMPORTANT: You must respond in ENGLISH only, regardless of the contract language.

Please extract the following key information from the contract and answer concisely in ENGLISH (if information not found, answer "Not mentioned"):

1. Rent Amount: What is the monthly rent?
2. Lease Duration: Lease term or duration?
3. Security Deposit: How much is the deposit?
4. Payment Due Date: When is monthly rent due?
5. Late Fee: Penalty or fee for late payment?
6. Pet Policy: Are pets allowed? Any restrictions?
7. Maintenance: Who is responsible for repairs and maintenance?
8. Early Termination: Conditions for early contract termination?
9. Utilities: Who pays for utilities?
10. Parking: Parking space or garage arrangements?

CRITICAL: Answer in ENGLISH ONLY using this exact format (one item per line, answer directly after colon):
Rent Amount: xxx
Lease Duration: xxx
Security Deposit: xxx
Payment Due Date: xxx
Late Fee: xxx
Pet Policy: xxx
Maintenance: xxx
Early Termination: xxx
Utilities: xxx
Parking: xxx"""
        
        # Get MORE relevant document chunks to ensure comprehensive coverage
        try:
            # Increase chunks from 8 to 15 for better coverage
            docs = self.vectorstore.similarity_search(extraction_prompt, k=15)
            # Increase context limit from 4000 to 8000 characters
            context = "\n\n".join([doc.page_content for doc in docs])[:8000]
            
            # Use more concise prompt with explicit English instruction
            final_prompt = f"""Based on the following contract content:

{context}

{extraction_prompt}

Remember: You MUST answer in ENGLISH, not in any other language. Translate any information from the contract into English.
IMPORTANT: Read the ENTIRE contract content carefully. If information exists but is mentioned indirectly or in different sections, still extract it. Only say "Not mentioned" if you truly cannot find ANY related information."""
            
            # Use dedicated LLM with higher max_tokens for extraction
            extraction_llm = ChatOpenAI(
                temperature=0.01,
                model=self.model,
                api_key=self.api_key,
                max_tokens=1000,  # Increased from 500 to ensure complete responses
                timeout=90
            )
            
            # Call LLM with extended token limit
            response = extraction_llm.predict(final_prompt)
            
            print(f"🔍 Extraction response length: {len(response)} characters")
            
            # Parse response and convert to dictionary
            extracted_info = {}
            field_mapping = {
                "Rent Amount": "rent_amount",
                "Lease Duration": "lease_duration", 
                "Security Deposit": "security_deposit",
                "Payment Due Date": "payment_due_date",
                "Late Fee": "late_fee",
                "Pet Policy": "pet_policy",
                "Maintenance": "maintenance",
                "Early Termination": "termination",
                "Utilities": "utilities",
                "Parking": "parking"
            }
            
            # Parse response
            for line in response.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key_en = parts[0].strip()
                        value = parts[1].strip()
                        if key_en in field_mapping:
                            extracted_info[field_mapping[key_en]] = value
            
            # If parsing fails, return default structure
            if not extracted_info:
                extracted_info = {key: "Extracting..." for key in field_mapping.values()}
            
            return extracted_info
            
        except Exception as e:
            print(f"❌ Error extracting information: {e}")
            return {"error": f"Extraction failed: {str(e)}"}
    
    def clear_memory(self):
        """Clear conversation history"""
        self.memory.clear()
        print("🧹 Conversation memory cleared")
    
    def save_vectorstore(self, path: str = "vectorstore"):
        """Save vector store to disk"""
        if self.vectorstore:
            self.vectorstore.save_local(path)
            print(f"💾 Vector store saved to {path}")
    
    def load_vectorstore(self, path: str = "vectorstore", allow_dangerous_deserialization: bool = False):
        """Load vector store from disk
        
        Args:
            path: Vector store path
            allow_dangerous_deserialization: Allow loading pickle files (only when file is trusted)
        """
        if os.path.exists(path):
            # New version LangChain requires explicitly allowing deserialization
            self.vectorstore = FAISS.load_local(
                path, 
                self.embeddings,
                allow_dangerous_deserialization=allow_dangerous_deserialization
            )
            self.retriever = self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": 5,
                    "fetch_k": 10
                }
            )
            print(f"📂 Vector store loaded from {path}")
        else:
            print(f"⚠️ Vector store path not found: {path}")

    def get_statistics(self) -> Dict:
        """Get system statistics"""
        total_chunks = sum(len(docs) for docs in self.documents.values())
        
        return {
            "loaded_contracts": len(self.documents),
            "total_chunks": total_chunks,
            "vector_store_size": self.vectorstore.index.ntotal if self.vectorstore else 0,
            "memory_size": len(self.memory.buffer) if hasattr(self.memory, 'buffer') else 0,
            "contracts": list(self.contract_metadata.values())
        }
    
    def clear_all_documents(self):
        """Clear all loaded documents and vector store
        Call before loading new files to ensure no mixing of different contracts
        """
        # Clear documents
        self.documents.clear()
        self.contract_metadata.clear()
        
        # Clear vector store
        self.vectorstore = None
        self.retriever = None
        
        # Clear conversation memory
        if hasattr(self, 'memory') and self.memory:
            self.memory.clear()
        
        print("🧹 Cleared all documents and vector stores")

    def get_current_documents_info(self):
        """Get current loaded documents information"""
        if not self.documents:
            return "No documents loaded"
        
        info = []
        for doc_path, chunks in self.documents.items():
            info.append(f"📄 {Path(doc_path).name}: {len(chunks)} chunks")
        
        return "\n".join(info)

    def ensure_single_document(self, file_path: str):
        """Ensure only one document is loaded
        
        Args:
            file_path: File path to load
        """
        # Check if same file
        if len(self.documents) == 1 and str(file_path) in self.documents:
            print(f"✅ Same document already loaded: {Path(file_path).name}")
            return True
        
        # If different file, clear previous data
        if self.documents and str(file_path) not in self.documents:
            print(f"🔄 Different document detected, clearing previous data...")
            self.clear_all_documents()
        
        return False


# Usage example
if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Initialize system
    rag = AdvancedContractRAG(api_key, model)
    

    # Load PDF
    result = rag.load_pdf("documents/contract.pdf")
    print(result)
    
    # Generate summary
    summary = rag.summarize_contract(summary_type="key_points")
    print("\n📝 Contract Summary:")
    print(summary)
    
    # Q&A
    question = "What is the monthly rent and when is it due?"
    answer = rag.ask_question(question)
    print(f"\n❓ Q: {question}")
    print(f"💡 A: {answer['answer']}")
    
    # Extract key information
    key_info = rag.extract_key_information()
    print("\n📊 Key Information:")
    for key, value in key_info.items():
        print(f"  {key}: {value}")
