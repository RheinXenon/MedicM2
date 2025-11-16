"""
检索器模块 - 从向量存储中检索相关知识
"""
import os
from typing import List, Dict, Tuple
from utils.embeddings import CustomEmbeddings
from dotenv import load_dotenv

load_dotenv()


class KnowledgeRetriever:
    """知识检索器"""
    
    def __init__(self, vector_store):
        """
        初始化检索器
        
        Args:
            vector_store: VectorStore实例
        """
        self.vector_store = vector_store
        self.embeddings = CustomEmbeddings()
        self.top_k = int(os.getenv("TOP_K_RETRIEVAL", 5))
    
    def retrieve(
        self, 
        query: str, 
        department_id: str, 
        top_k: int = None
    ) -> List[Dict]:
        """
        检索相关知识
        
        Args:
            query: 查询文本
            department_id: 科室ID
            top_k: 返回的文档数量
            
        Returns:
            检索到的文档列表，每个文档包含content和metadata
        """
        if top_k is None:
            top_k = self.top_k
        
        try:
            # 获取科室的集合
            collection = self.vector_store.get_collection(department_id)
            
            # 生成查询嵌入
            query_embedding = self.embeddings.embed_query(query)
            
            # 执行检索
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # 格式化结果
            documents = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    documents.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return documents
        
        except Exception as e:
            print(f"检索失败: {str(e)}")
            return []
    
    def retrieve_with_scores(
        self, 
        query: str, 
        department_id: str, 
        top_k: int = None
    ) -> List[Tuple[str, float]]:
        """
        检索相关知识并返回相似度分数
        
        Args:
            query: 查询文本
            department_id: 科室ID
            top_k: 返回的文档数量
            
        Returns:
            (文档内容, 相似度分数)的列表
        """
        documents = self.retrieve(query, department_id, top_k)
        
        results = []
        for doc in documents:
            content = doc['content']
            # 将距离转换为相似度分数（距离越小，相似度越高）
            score = 1.0 / (1.0 + doc['distance']) if doc['distance'] is not None else 0.5
            results.append((content, score))
        
        return results
    
    def format_retrieved_knowledge(self, documents: List[Dict]) -> str:
        """
        格式化检索到的知识为上下文字符串
        
        Args:
            documents: 检索到的文档列表
            
        Returns:
            格式化后的知识文本
        """
        if not documents:
            return "未找到相关专业知识。"
        
        formatted_text = "参考专业知识：\n\n"
        
        for i, doc in enumerate(documents, 1):
            formatted_text += f"[{i}] {doc['content']}\n\n"
        
        return formatted_text
    
    def multi_query_retrieve(
        self,
        queries: List[str],
        department_id: str,
        top_k: int = None
    ) -> List[Dict]:
        """
        多查询检索，合并去重结果
        
        Args:
            queries: 查询文本列表
            department_id: 科室ID
            top_k: 每个查询返回的文档数量
            
        Returns:
            去重后的文档列表
        """
        all_docs = []
        seen_contents = set()
        
        for query in queries:
            docs = self.retrieve(query, department_id, top_k)
            
            for doc in docs:
                # 去重
                if doc['content'] not in seen_contents:
                    seen_contents.add(doc['content'])
                    all_docs.append(doc)
        
        return all_docs
