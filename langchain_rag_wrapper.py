# langchain_rag_wrapper.py
"""
延迟加载包装器 - 避免在模块导入时触发 langchain 的复杂依赖树
只在实例化 AdvancedContractRAG 时才导入 langchain 相关模块
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_rag_system import AdvancedContractRAG as _AdvancedContractRAG

def get_rag_class():
    """
    延迟导入并返回 AdvancedContractRAG 类
    
    只在第一次调用时导入 langchain_rag_system 模块，
    避免在应用启动时触发 aiohttp/typing 导入错误
    
    Returns:
        AdvancedContractRAG 类（未实例化）
    
    Raises:
        ImportError: 如果导入失败
    """
    try:
        from langchain_rag_system import AdvancedContractRAG
        return AdvancedContractRAG
    except Exception as e:
        raise ImportError(f"Failed to import AdvancedContractRAG: {e}") from e


def create_rag_system(api_key: str, model: str = "gpt-3.5-turbo", language: str = "en"):
    """
    创建 AdvancedContractRAG 实例的便捷函数
    
    Args:
        api_key: OpenAI API 密钥
        model: 模型名称
        language: 语言设置
    
    Returns:
        AdvancedContractRAG 实例
    
    Raises:
        ImportError: 如果导入失败
        Exception: 如果实例化失败
    """
    RAGClass = get_rag_class()
    return RAGClass(api_key=api_key, model=model, language=language)
