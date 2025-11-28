"""
Agent 基类 - 增强版，包含思考过程记录
"""
import os
import time
from typing import Dict, Optional, List
from openai import OpenAI
from dotenv import load_dotenv
import pathlib

# 强制从项目根目录加载 .env，覆盖系统环境变量
_project_root = pathlib.Path(__file__).parent.parent
load_dotenv(_project_root / ".env", override=True)


class BaseAgent:
    """Agent 基类 - 增强版"""
    
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
        
        # 思考过程记录
        self.thinking_process = []
    
    def add_thinking_step(self, step_name: str, content: str, metadata: Dict = None):
        """
        添加思考步骤
        
        Args:
            step_name: 步骤名称
            content: 步骤内容
            metadata: 元数据
        """
        step = {
            'step_name': step_name,
            'content': content,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        self.thinking_process.append(step)
    
    def clear_thinking_process(self):
        """清空思考过程记录"""
        self.thinking_process = []
    
    def get_thinking_process(self) -> List[Dict]:
        """获取思考过程记录"""
        return self.thinking_process
    
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
        
        # 记录请求
        self.add_thinking_step(
            "LLM请求",
            f"正在向{self.model}发送请求...",
            {"system_message": system_message[:100] if system_message else None}
        )
        
        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            end_time = time.time()
            
            # 检查响应是否有效
            if not response or not response.choices:
                error_msg = "API返回了空响应"
                self.add_thinking_step("错误", error_msg)
                print(error_msg)
                return f"无法生成诊断意见：{error_msg}"
            
            response_text = response.choices[0].message.content
            
            # 检查content是否为None
            if response_text is None:
                error_msg = "API返回的content为None"
                self.add_thinking_step("错误", error_msg)
                print(error_msg)
                return "无法生成诊断意见：API返回了空内容"
            
            # 记录响应
            self.add_thinking_step(
                "LLM响应",
                f"收到回复（耗时 {end_time - start_time:.2f}秒）",
                {
                    "response_length": len(response_text),
                    "model": self.model,
                    "temperature": self.temperature
                }
            )
            
            return response_text
        
        except Exception as e:
            error_msg = f"生成回复失败: {str(e)}"
            self.add_thinking_step("错误", error_msg)
            print(error_msg)
            return f"无法生成诊断意见：{error_msg}"
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
