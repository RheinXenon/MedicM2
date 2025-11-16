"""
测试API连接和配置
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_api_connection():
    """测试API连接"""
    print("=" * 60)
    print("🔧 测试API配置")
    print("=" * 60)
    
    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    model = os.getenv("OPENAI_MODEL")
    
    print(f"\n📋 配置信息:")
    print(f"  API Base: {api_base}")
    print(f"  Model: {model}")
    print(f"  API Key: {api_key[:20]}..." if api_key else "  API Key: 未设置")
    
    if not api_key:
        print("\n❌ 错误: OPENAI_API_KEY 未设置!")
        return False
    
    if not api_base:
        print("\n❌ 错误: OPENAI_API_BASE 未设置!")
        return False
    
    if not model:
        print("\n❌ 错误: OPENAI_MODEL 未设置!")
        return False
    
    # 测试API调用
    print(f"\n🔄 正在测试API连接...")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请回复'连接成功'"}
            ],
            temperature=0.7,
            timeout=30
        )
        
        if not response or not response.choices:
            print("\n❌ API返回了空响应!")
            return False
        
        response_text = response.choices[0].message.content
        
        if response_text is None:
            print("\n❌ API返回的content为None!")
            print("   这可能是因为:")
            print("   1. 模型不支持chat.completions格式")
            print("   2. API配置错误")
            print("   3. 余额不足或权限问题")
            return False
        
        print(f"\n✅ API连接成功!")
        print(f"   响应内容: {response_text[:100]}")
        
        # 测试嵌入模型
        print(f"\n🔄 正在测试嵌入模型...")
        embedding_key = os.getenv("EMBEDDING_API_KEY")
        embedding_base = os.getenv("EMBEDDING_API_BASE")
        embedding_model = os.getenv("EMBEDDING_MODEL")
        
        if not embedding_key or not embedding_base or not embedding_model:
            print("⚠️ 嵌入模型配置不完整，跳过测试")
        else:
            embedding_client = OpenAI(
                api_key=embedding_key,
                base_url=embedding_base
            )
            
            try:
                embed_response = embedding_client.embeddings.create(
                    model=embedding_model,
                    input="测试文本"
                )
                
                if embed_response and embed_response.data:
                    print(f"✅ 嵌入模型连接成功!")
                    print(f"   向量维度: {len(embed_response.data[0].embedding)}")
                else:
                    print("❌ 嵌入模型返回了空响应")
            except Exception as e:
                print(f"❌ 嵌入模型测试失败: {e}")
        
        print("\n" + "=" * 60)
        print("✅ 配置测试完成!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ API连接失败: {e}")
        print(f"\n💡 可能的原因:")
        print(f"   1. API密钥无效或已过期")
        print(f"   2. API地址错误")
        print(f"   3. 模型名称错误")
        print(f"   4. 网络连接问题")
        print(f"   5. API服务暂时不可用")
        return False


if __name__ == '__main__':
    success = test_api_connection()
    
    if not success:
        print("\n⚠️ 请检查.env文件中的API配置")
        print("   确保:")
        print("   - OPENAI_API_KEY 正确")
        print("   - OPENAI_API_BASE 正确")
        print("   - OPENAI_MODEL 正确")
    
    input("\n按回车键退出...")
