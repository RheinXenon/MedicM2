"""
自定义嵌入模块 - 支持多种API提供商的嵌入服务
"""
import os
import requests
from typing import List
from langchain_core.embeddings import Embeddings
from dotenv import load_dotenv

load_dotenv()


class CustomEmbeddings(Embeddings):
    """
    自定义嵌入类，支持配置独立的嵌入API端点
    
    可以使用与主模型不同的API提供商（如 SiliconFlow）来获取嵌入向量
    """
    
    def __init__(
        self,
        model: str = None,
        api_key: str = None,
        api_base: str = None
    ):
        """
        初始化自定义嵌入
        
        Args:
            model: 嵌入模型名称
            api_key: API密钥
            api_base: API基础URL
        """
        self.model = model or os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
        self.api_key = api_key or os.getenv("EMBEDDING_API_KEY", "")
        self.api_base = api_base or os.getenv("EMBEDDING_API_BASE", "https://api.siliconflow.cn/v1")
        
        # 确保API基础URL以/v1结尾
        if not self.api_base.endswith('/v1'):
            self.api_base = self.api_base.rstrip('/') + '/v1'
        
        self.embeddings_url = f"{self.api_base}/embeddings"
        
        if not self.api_key:
            raise ValueError(
                "未找到嵌入API密钥。请在.env文件中设置 EMBEDDING_API_KEY"
            )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        对文档列表生成嵌入向量
        
        Args:
            texts: 文档文本列表
            
        Returns:
            嵌入向量列表
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": texts
        }
        
        try:
            response = requests.post(
                self.embeddings_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取嵌入向量
            embeddings = []
            for item in result['data']:
                embeddings.append(item['embedding'])
            
            return embeddings
            
        except requests.exceptions.RequestException as e:
            print(f"嵌入API请求失败: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        对单个查询文本生成嵌入向量
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        embeddings = self.embed_documents([text])
        return embeddings[0]
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        异步版本的 embed_documents
        
        Args:
            texts: 文档文本列表
            
        Returns:
            嵌入向量列表
        """
        # 暂时使用同步版本
        return self.embed_documents(texts)
    
    async def aembed_query(self, text: str) -> List[float]:
        """
        异步版本的 embed_query
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        # 暂时使用同步版本
        return self.embed_query(text)
