"""
API 连接测试脚本
用于诊断 "API返回了空响应" 问题
"""
import os
import sys

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
from openai import OpenAI

# 强制从项目根目录加载 .env 文件，覆盖系统环境变量
env_path = os.path.join(PROJECT_ROOT, ".env")
print(f"📁 .env 文件路径: {env_path}")
print(f"📁 .env 文件存在: {os.path.exists(env_path)}")
load_dotenv(env_path, override=True)


def test_api_connection():
    """测试基本 API 连接"""
    print("=" * 60)
    print("🔍 API 连接测试")
    print("=" * 60)
    
    # 1. 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    print("\n📋 环境变量配置:")
    print(f"  • OPENAI_API_KEY: {'已设置 (' + api_key[:8] + '...' + api_key[-4:] + ')' if api_key else '❌ 未设置'}")
    print(f"  • OPENAI_API_BASE: {api_base or '❌ 未设置 (使用默认)'}")
    print(f"  • OPENAI_MODEL: {model}")
    
    if not api_key:
        print("\n❌ 错误: OPENAI_API_KEY 未设置!")
        return False
    
    # 2. 创建客户端
    print("\n🔗 正在创建 OpenAI 客户端...")
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        print("  ✓ 客户端创建成功")
    except Exception as e:
        print(f"  ❌ 客户端创建失败: {e}")
        return False
    
    # 3. 测试简单请求
    print("\n📤 发送测试请求...")
    test_prompt = "请回复'测试成功'"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": test_prompt}
            ],
            temperature=0.7,
            timeout=30
        )
        
        print(f"  ✓ 收到响应对象: {type(response)}")
        print(f"  ✓ response.choices: {response.choices}")
        
        if not response or not response.choices:
            print("\n❌ API返回了空响应!")
            print(f"  完整响应: {response}")
            return False
        
        content = response.choices[0].message.content
        print(f"  ✓ 响应内容: {content}")
        
        if content is None:
            print("\n❌ API返回的content为None!")
            return False
        
        print("\n✅ API 连接测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ API 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_symptom_check_prompt():
    """测试症状校验的具体提示词（模拟 SymptomConsistencyInspector）"""
    print("\n" + "=" * 60)
    print("🔍 症状校验 API 测试 (SymptomConsistencyInspector)")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    if not api_key:
        print("❌ OPENAI_API_KEY 未设置")
        return False
    
    client = OpenAI(api_key=api_key, base_url=api_base)
    
    # 模拟症状校验的提示词
    from utils.prompt_templates import SYMPTOM_SANITY_CHECK_TEMPLATE
    
    test_symptoms = ["头痛", "发热", "咳嗽", "乏力"]
    symptom_text = "\n".join(f"- {s}" for s in test_symptoms)
    prompt = SYMPTOM_SANITY_CHECK_TEMPLATE.format(symptom_list=symptom_text)
    
    print(f"\n📋 测试症状: {test_symptoms}")
    print(f"📝 提示词长度: {len(prompt)} 字符")
    
    try:
        print("\n📤 发送症状校验请求...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位负责把关症状可信度的医学专家"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            timeout=60
        )
        
        if not response or not response.choices:
            print("❌ API返回了空响应!")
            print(f"  完整响应: {response}")
            return False
        
        content = response.choices[0].message.content
        
        if content is None:
            print("❌ API返回的content为None!")
            return False
        
        print(f"✓ 响应内容:\n{content[:500]}...")
        print("\n✅ 症状校验 API 测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_list():
    """测试获取可用模型列表"""
    print("\n" + "=" * 60)
    print("🔍 获取可用模型列表")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    
    if not api_key:
        print("❌ OPENAI_API_KEY 未设置")
        return False
    
    client = OpenAI(api_key=api_key, base_url=api_base)
    
    try:
        models = client.models.list()
        print("\n可用模型:")
        for model in list(models)[:10]:
            print(f"  • {model.id}")
        if len(list(models)) > 10:
            print(f"  ... 共 {len(list(models))} 个模型")
        return True
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        print("  (某些 API 提供商可能不支持此接口)")
        return True  # 不影响主要功能


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" " * 15 + "🧪 API 诊断测试")
    print("=" * 60)
    
    # 运行测试
    results = []
    
    results.append(("基本连接测试", test_api_connection()))
    results.append(("模型列表测试", test_model_list()))
    results.append(("症状校验测试", test_symptom_check_prompt()))
    
    # 总结
    print("\n" + "=" * 60)
    print(" " * 20 + "📊 测试总结")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("✅ 所有测试通过!" if all_passed else "❌ 部分测试失败，请检查上方错误信息"))
