"""
Agent 基类
"""
import os
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class BaseAgent:
    """Agent 基类"""
    
    def __init__(
        self, 
        name: str, 
        role: str,
        model: str = None,
        temperature: float = None
    ):
        """
        初始化 Agent
        
        Args:
            name: Agent 名称
            role: Agent 角色描述
            model: 使用的模型名称
            temperature: 生成温度
        """
        self.name = name
        self.role = role
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.temperature = temperature or float(os.getenv("DOCTOR_TEMPERATURE", 0.7))
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        
        self.max_retries = int(os.getenv("MAX_RETRIES", 3))
        self.timeout = int(os.getenv("TIMEOUT", 60))
    
    def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None
    ) -> str:
        """
        生成回复
        
        Args:
            prompt: 用户提示词
            system_message: 系统消息
            
        Returns:
            生成的回复文本
        """
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            error_msg = f"生成回复失败: {str(e)}"
            print(error_msg)
            return error_msg
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
