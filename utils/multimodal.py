"""
多模态处理模块 - 处理文本和图像输入
"""
import os
import base64
from typing import List, Dict, Optional
from PIL import Image
import io
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class MultimodalProcessor:
    """多模态处理器"""
    
    def __init__(self):
        """初始化多模态处理器"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vision_model = os.getenv("VISION_MODEL", "gpt-4-vision-preview")
    
    def encode_image(self, image_path: str) -> str:
        """
        将图像编码为base64
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            base64编码的图像字符串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(
        self, 
        image_path: str, 
        prompt: str,
        image_type: str = "医学影像"
    ) -> str:
        """
        分析单张医学图像
        
        Args:
            image_path: 图像路径
            prompt: 分析提示词
            image_type: 图像类型（如：X光片、CT、MRI等）
            
        Returns:
            图像分析结果
        """
        try:
            # 编码图像
            base64_image = self.encode_image(image_path)
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # 调用API
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"图像分析失败: {str(e)}"
    
    def analyze_multiple_images(
        self, 
        image_paths: List[str], 
        base_prompt: str
    ) -> List[Dict[str, str]]:
        """
        分析多张医学图像
        
        Args:
            image_paths: 图像路径列表
            base_prompt: 基础分析提示词
            
        Returns:
            每张图像的分析结果列表
        """
        results = []
        
        for i, image_path in enumerate(image_paths):
            # 尝试从文件名推断图像类型
            filename = os.path.basename(image_path).lower()
            
            if 'xray' in filename or 'x-ray' in filename or 'x光' in filename:
                image_type = "X光片"
            elif 'ct' in filename:
                image_type = "CT影像"
            elif 'mri' in filename:
                image_type = "MRI影像"
            elif 'ultrasound' in filename or '超声' in filename:
                image_type = "超声影像"
            elif 'ecg' in filename or '心电图' in filename:
                image_type = "心电图"
            else:
                image_type = "医学影像"
            
            prompt = f"{base_prompt}\n\n图像类型：{image_type}\n图像{i+1}/{len(image_paths)}"
            
            result = self.analyze_image(image_path, prompt, image_type)
            
            results.append({
                "image_path": image_path,
                "image_type": image_type,
                "analysis": result
            })
        
        return results
    
    def format_image_analysis(self, analyses: List[Dict[str, str]]) -> str:
        """
        格式化图像分析结果
        
        Args:
            analyses: 图像分析结果列表
            
        Returns:
            格式化后的分析文本
        """
        if not analyses:
            return ""
        
        formatted_text = "\n=== 影像学检查结果 ===\n\n"
        
        for i, analysis in enumerate(analyses, 1):
            formatted_text += f"图像 {i}: {analysis['image_type']}\n"
            formatted_text += f"文件: {os.path.basename(analysis['image_path'])}\n"
            formatted_text += f"分析结果:\n{analysis['analysis']}\n\n"
        
        return formatted_text
    
    def validate_image(self, image_path: str) -> bool:
        """
        验证图像文件是否有效
        
        Args:
            image_path: 图像路径
            
        Returns:
            图像是否有效
        """
        try:
            if not os.path.exists(image_path):
                print(f"图像文件不存在: {image_path}")
                return False
            
            # 尝试打开图像
            with Image.open(image_path) as img:
                img.verify()
            
            return True
        
        except Exception as e:
            print(f"图像验证失败 {image_path}: {str(e)}")
            return False
    
    def prepare_case_with_images(
        self, 
        case_data: Dict, 
        image_prompt: str
    ) -> Dict:
        """
        准备包含图像分析的病例数据
        
        Args:
            case_data: 原始病例数据
            image_prompt: 图像分析提示词
            
        Returns:
            包含图像分析结果的病例数据
        """
        # 复制原始数据
        enhanced_case = case_data.copy()
        
        # 如果有图像，进行分析
        if 'images' in case_data and case_data['images']:
            image_paths = case_data['images']
            
            # 验证图像
            valid_images = [path for path in image_paths if self.validate_image(path)]
            
            if valid_images:
                # 分析图像
                analyses = self.analyze_multiple_images(valid_images, image_prompt)
                
                # 将分析结果添加到病例数据
                enhanced_case['image_analyses'] = analyses
                enhanced_case['image_summary'] = self.format_image_analysis(analyses)
            else:
                enhanced_case['image_summary'] = "提供的图像文件无效或无法访问。"
        else:
            enhanced_case['image_summary'] = ""
        
        return enhanced_case
