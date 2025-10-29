# backend.py
"""
后端业务逻辑层
包含数据库管理、用户认证、文件处理、缓存管理等核心业务逻辑
不包含任何前端代码，可复用到其他项目
"""

"""
完整的合同管理系统
集成用户认证、文件管理、智能缓存
"""

import sqlite3
import hashlib
import hmac
import secrets
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Any
import shutil
import os
from dotenv import load_dotenv
load_dotenv()

# LangChain相关导入 - 延迟导入以避免在模块加载时触发复杂依赖导入错误
# (在 FileProcessor 类方法中实际使用时再导入)
# 使用 TYPE_CHECKING 和 forward references 以保持类型提示
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from langchain_rag_system import AdvancedContractRAG

# ==================================================
# 后端业务逻辑类
# ==================================================

class DatabaseManager:
    """统一的数据库管理"""
    
    def __init__(self, db_path: str = "contract_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化所有数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                tier TEXT DEFAULT 'free'
            )
        """)
        
        # 处理过的文件表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_files (
                file_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                processed_path TEXT NOT NULL,
                vector_store_path TEXT,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                file_hash TEXT,
                num_chunks INTEGER,
                num_pages INTEGER,
                processing_status TEXT DEFAULT 'pending',
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # 缓存的总结表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_summaries (
                summary_id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                summary_type TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER,
                cost REAL,
                FOREIGN KEY (file_id) REFERENCES processed_files (file_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # 问答历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qa_history (
                qa_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                file_id TEXT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # 提取的信息缓存表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_info_cache (
                cache_id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                extracted_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES processed_files (file_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        conn.commit()
        conn.close()

# ===========================
# 用户管理类
# ===========================

class UserManager:
    """用户认证和管理"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def register_user(self, username: str, email: str, password: str) -> Dict:
        """注册新用户"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查用户名和邮箱
            cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", 
                         (username, email))
            if cursor.fetchone():
                return {"success": False, "message": "用户名或邮箱已存在"}
            
            # 创建用户
            user_id = hashlib.md5(f"{username}_{datetime.now()}".encode()).hexdigest()[:16]
            # 使用 PBKDF2 (sha256) 生成密码哈希，格式: pbkdf2_sha256$iterations$salt$hexhash
            def _hash_password(pw: str) -> str:
                iterations = 200_000
                salt = secrets.token_hex(16)
                dk = hashlib.pbkdf2_hmac('sha256', pw.encode('utf-8'), salt.encode('utf-8'), iterations)
                return f"pbkdf2_sha256${iterations}${salt}${dk.hex()}"

            password_hash = _hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (user_id, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, email, password_hash))
            
            # 创建用户目录结构
            user_dir = Path(f"user_data/{user_id}")
            user_dir.mkdir(parents=True, exist_ok=True)
            (user_dir / "contracts").mkdir(exist_ok=True)
            (user_dir / "vector_stores").mkdir(exist_ok=True)
            (user_dir / "cache").mkdir(exist_ok=True)
            
            conn.commit()
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            conn.close()
    
    def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT user_id, password_hash, email 
                FROM users 
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            user = cursor.fetchone()
            if not user:
                return {"success": False}
            
            user_id, password_hash, email = user

            # 验证 PBKDF2 密码哈希
            def _verify_password(pw: str, stored: str) -> bool:
                try:
                    algo, iterations, salt, hexhash = stored.split('$')
                    if algo != 'pbkdf2_sha256':
                        return False
                    iterations = int(iterations)
                    dk = hashlib.pbkdf2_hmac('sha256', pw.encode('utf-8'), salt.encode('utf-8'), iterations)
                    return hmac.compare_digest(dk.hex(), hexhash)
                except Exception:
                    return False

            if _verify_password(password, password_hash):
                # 更新登录时间和使用次数
                cursor.execute("""
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP, 
                        usage_count = usage_count + 1
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "username": username,
                    "email": email
                }
            
            return {"success": False}
            
        finally:
            conn.close()

# ===========================
# 文件处理和缓存管理
# ===========================

class FileProcessor:
    """文件处理和缓存管理"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def process_and_save_file(self, user_id: str, uploaded_file, rag_system: "AdvancedContractRAG") -> Dict:
        """处理并保存上传的文件"""
        
        # ⭐ 关键修改1: 在处理新文件前,先清理旧数据
        print(f"🧹 Clearing previous contract data before processing new file...")
        rag_system.clear_all_documents()
        
        # 生成文件ID
        file_id = hashlib.md5(
            f"{user_id}_{uploaded_file.name}_{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        # 用户目录
        user_dir = Path(f"user_data/{user_id}")
        contracts_dir = user_dir / "contracts"
        vector_dir = user_dir / "vector_stores"
        
        contracts_dir.mkdir(parents=True, exist_ok=True)
        vector_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存原始文件
        file_path = contracts_dir / f"{file_id}_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 计算文件哈希
        file_hash = hashlib.md5(uploaded_file.getbuffer()).hexdigest()
        
        # 使用RAG系统处理文件
        result = rag_system.load_pdf(str(file_path), use_cache=True)
        
        # ⭐ 修复: 检查result是否为None
        if result is None:
            return {"success": False, "error": "load_pdf returned None - check RAG system"}
        
        if result.get("success", False):
            # 保存向量存储
            vector_store_path = vector_dir / f"{file_id}_vectors"
            rag_system.save_vectorstore(str(vector_store_path))
            
            # ⭐ 验证当前加载的文档
            current_docs = rag_system.get_current_documents_info()
            print(f"📋 Current documents after processing:\n{current_docs}")
            
            # 保存到数据库
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            stats = result.get("stats", {})
            cursor.execute("""
                INSERT INTO processed_files 
                (file_id, user_id, original_filename, processed_path, vector_store_path,
                 file_hash, num_chunks, num_pages, processing_status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?)
            """, (
                file_id,
                user_id,
                uploaded_file.name,
                str(file_path),
                str(vector_store_path),
                file_hash,
                stats.get("chunks", 0),
                stats.get("pages", 0),
                json.dumps(stats)
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "file_id": file_id,
                "stats": stats
            }
        
        return {"success": False, "error": result.get("error", "Processing failed")}
    
    def get_recent_files(self, user_id: str, limit: int = 5) -> List[Dict]:
        """获取最近的文件"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT file_id, original_filename, upload_time, num_chunks, num_pages, 
                   processing_status, last_accessed
            FROM processed_files
            WHERE user_id = ? AND processing_status = 'completed'
            ORDER BY COALESCE(last_accessed, upload_time) DESC
            LIMIT ?
        """, (user_id, limit))
        
        files = []
        for row in cursor.fetchall():
            files.append({
                "file_id": row[0],
                "filename": row[1],
                "upload_time": row[2],
                "num_chunks": row[3],
                "num_pages": row[4],
                "status": row[5],
                "last_accessed": row[6]
            })
        
        conn.close()
        return files
    
    def load_processed_file(self, user_id: str, file_id: str, rag_system: "AdvancedContractRAG") -> bool:
        """加载已处理的文件到RAG系统"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT processed_path, vector_store_path, original_filename
            FROM processed_files
            WHERE file_id = ? AND user_id = ?
        """, (file_id, user_id))
        
        result = cursor.fetchone()
        if result:
            processed_path, vector_store_path, filename = result
            
            # 更新访问时间
            cursor.execute("""
                UPDATE processed_files 
                SET last_accessed = CURRENT_TIMESTAMP 
                WHERE file_id = ?
            """, (file_id,))
            conn.commit()
            
            try:
                # ⭐ 关键修改2: 彻底清理之前的所有数据
                print(f"🧹 Clearing all previous data before loading new contract...")
                rag_system.clear_all_documents()  # 使用专门的清理方法
                
                # ⭐ 关键修改3: 强制清空对话记忆,避免上下文混淆
                if hasattr(rag_system, 'memory') and rag_system.memory:
                    rag_system.memory.clear()
                    print(f"🧹 Cleared conversation memory")
                
                # 加载新的向量存储
                if vector_store_path and Path(vector_store_path).exists():
                    print(f"📂 Loading vector store for: {filename}")
                    # 这是安全的,因为我们加载的是自己创建的文件
                    rag_system.load_vectorstore(vector_store_path, allow_dangerous_deserialization=True)
                    
                    # ⭐ 关键修改4: 重新加载文档到内存(确保文档列表正确)
                    load_result = rag_system.load_pdf(processed_path, use_cache=True)
                    if load_result["success"]:
                        # ⭐ 关键修改5: 验证当前加载的文档
                        current_docs = rag_system.get_current_documents_info()
                        print(f"✅ Successfully loaded: {filename}")
                        print(f"📋 Current documents:\n{current_docs}")
                        conn.close()
                        return True
                    else:
                        print(f"⚠️ Failed to load document: {load_result.get('error')}")
                else:
                    # 如果没有向量存储,重新处理文件
                    print(f"🔄 No vector store found, reprocessing file...")
                    load_result = rag_system.load_pdf(processed_path, use_cache=False)
                    if load_result["success"]:
                        rag_system.save_vectorstore(vector_store_path)
                        print(f"✅ Reprocessed and loaded: {filename}")
                        conn.close()
                        return True
                    
            except Exception as e:
                print(f"❌ Error loading file: {e}")
                # 尝试重新处理
                try:
                    print(f"🔄 Attempting to reprocess from scratch...")
                    rag_system.clear_all_documents()  # 确保清理
                    rag_system.load_pdf(processed_path, use_cache=False)
                    rag_system.save_vectorstore(vector_store_path)
                    print(f"✅ Successfully reprocessed: {filename}")
                    conn.close()
                    return True
                except Exception as e2:
                    print(f"❌ Failed to reprocess: {e2}")
        
        conn.close()
        return False

# ===========================
# 缓存管理
# ===========================

class CacheManager:
    """管理各种缓存"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_cached_summary(self, file_id: str, summary_type: str) -> Optional[str]:
        """获取缓存的总结"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT summary_text 
            FROM cached_summaries
            WHERE file_id = ? AND summary_type = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (file_id, summary_type))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def save_summary(self, file_id: str, user_id: str, summary_type: str, 
                     summary_text: str, tokens_used: int = 0) -> None:
        """保存总结到缓存"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        summary_id = hashlib.md5(
            f"{file_id}_{summary_type}_{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        # 删除旧的同类型总结
        cursor.execute("""
            DELETE FROM cached_summaries
            WHERE file_id = ? AND summary_type = ?
        """, (file_id, summary_type))
        
        # 保存新总结
        cursor.execute("""
            INSERT INTO cached_summaries
            (summary_id, file_id, user_id, summary_type, summary_text, tokens_used)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (summary_id, file_id, user_id, summary_type, summary_text, tokens_used))
        
        conn.commit()
        conn.close()
    
    def get_cached_extraction(self, file_id: str) -> Optional[Dict]:
        """获取缓存的信息提取结果"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT extracted_data
            FROM extracted_info_cache
            WHERE file_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (file_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return json.loads(result[0]) if result else None
    
    def save_extraction(self, file_id: str, user_id: str, extracted_data: Dict) -> None:
        """保存信息提取结果"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cache_id = hashlib.md5(
            f"{file_id}_extraction_{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        # 删除旧的提取结果
        cursor.execute("DELETE FROM extracted_info_cache WHERE file_id = ?", (file_id,))
        
        # 保存新结果
        cursor.execute("""
            INSERT INTO extracted_info_cache
            (cache_id, file_id, user_id, extracted_data)
            VALUES (?, ?, ?, ?)
        """, (cache_id, file_id, user_id, json.dumps(extracted_data)))
        
        conn.commit()
        conn.close()
    
    def save_qa_history(self, user_id: str, file_id: str, question: str, 
                       answer: str, sources: List = None) -> None:
        """保存问答历史"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        qa_id = hashlib.md5(
            f"{user_id}_{question}_{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        cursor.execute("""
            INSERT INTO qa_history
            (qa_id, user_id, file_id, question, answer, sources)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (qa_id, user_id, file_id, question, answer, json.dumps(sources)))
        
        conn.commit()
        conn.close()

# ===========================
# 主应用类
# ===========================

