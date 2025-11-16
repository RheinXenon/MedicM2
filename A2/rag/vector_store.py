"""
向量存储模块 - 使用 ChromaDB 管理科室知识库
"""
import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.embeddings import CustomEmbeddings
from dotenv import load_dotenv

load_dotenv()


class VectorStore:
    """向量存储管理类"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        初始化向量存储
        
        Args:
            persist_directory: 持久化目录路径
        """
        self.persist_directory = persist_directory
        self.embeddings = CustomEmbeddings()
        
        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(os.getenv("CHUNK_SIZE", 500)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 50)),
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
    
    def create_collection(self, department_id: str) -> chromadb.Collection:
        """
        为特定科室创建或获取集合
        
        Args:
            department_id: 科室ID
            
        Returns:
            ChromaDB Collection对象
        """
        collection_name = f"dept_{department_id}"
        
        # 获取或创建集合
        try:
            collection = self.client.get_collection(name=collection_name)
            print(f"已加载科室 {department_id} 的知识库")
        except:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"department": department_id}
            )
            print(f"已创建科室 {department_id} 的知识库")
        
        return collection
    
    def load_documents_from_directory(
        self, 
        directory: str, 
        department_id: str
    ) -> int:
        """
        从目录加载文档到向量存储
        
        Args:
            directory: 文档目录路径
            department_id: 科室ID
            
        Returns:
            加载的文档块数量
        """
        if not os.path.exists(directory):
            print(f"警告: 目录不存在 - {directory}")
            return 0
        
        collection = self.create_collection(department_id)
        
        # 检查集合是否已有数据
        if collection.count() > 0:
            print(f"科室 {department_id} 的知识库已包含 {collection.count()} 个文档块")
            return collection.count()
        
        documents = []
        metadatas = []
        ids = []
        
        # 遍历目录中的所有文本文件
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                filepath = os.path.join(directory, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分割文档
                chunks = self.text_splitter.split_text(content)
                
                for i, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({
                        "source": filename,
                        "department": department_id,
                        "chunk_id": i
                    })
                    ids.append(f"{department_id}_{filename}_{i}")
        
        if documents:
            # 生成嵌入并添加到集合
            embeddings = self.embeddings.embed_documents(documents)
            
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"已为科室 {department_id} 加载 {len(documents)} 个文档块")
        
        return len(documents)
    
    def initialize_all_departments(self, knowledge_base_path: str, departments: List[Dict]):
        """
        初始化所有科室的知识库
        
        Args:
            knowledge_base_path: 知识库根目录
            departments: 科室配置列表
        """
        print("\n=== 初始化知识库 ===")
        total_chunks = 0
        
        for dept in departments:
            dept_id = dept['id']
            dept_path = os.path.join(knowledge_base_path, dept_id)
            
            chunks = self.load_documents_from_directory(dept_path, dept_id)
            total_chunks += chunks
        
        print(f"\n知识库初始化完成，共加载 {total_chunks} 个文档块\n")
    
    def get_collection(self, department_id: str) -> chromadb.Collection:
        """
        获取指定科室的集合
        
        Args:
            department_id: 科室ID
            
        Returns:
            ChromaDB Collection对象
        """
        collection_name = f"dept_{department_id}"
        return self.client.get_collection(name=collection_name)
    
    def delete_collection(self, department_id: str):
        """
        删除指定科室的集合
        
        Args:
            department_id: 科室ID
        """
        collection_name = f"dept_{department_id}"
        try:
            self.client.delete_collection(name=collection_name)
            print(f"已删除科室 {department_id} 的知识库")
        except:
            print(f"科室 {department_id} 的知识库不存在")
