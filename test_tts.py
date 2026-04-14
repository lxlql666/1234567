# bailian_test.py - 专门针对阿里云百炼平台的测试脚本
import os
import sys
import json
import base64
import requests
from dotenv import load_dotenv

# 加载环境变量
print("1. 加载环境变量...")
load_dotenv()

# 获取百炼平台API密钥 - 确保变量名正确
BAILIAN_ACCESS_KEY_ID = os.getenv('BAILIAN_ACCESS_KEY_ID')
BAILIAN_ACCESS_KEY_SECRET = os.getenv('BAILIAN_ACCESS_KEY_SECRET')

# 也检查原来的变量名，避免配置错误
OLD_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID')
OLD_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET')

print(f"\n=== 检查API密钥配置 ===\n")
print(f"BAILIAN_ACCESS_KEY_ID: {BAILIAN_ACCESS_KEY_ID}")
print(f"BAILIAN_ACCESS_KEY_SECRET: {'已配置' if BAILIAN_ACCESS_KEY_SECRET else '未配置'}")
print(f"OLD_ACCESS_KEY_ID: {OLD_ACCESS_KEY_ID}")
print(f"OLD_ACCESS_KEY_SECRET: {'已配置' if OLD_ACCESS_KEY_SECRET else '未配置'}")

# 决定使用哪个API密钥 - 可根据实际情况切换
USE_OLD_KEYS = False  # 切换为True尝试旧密钥，False尝试新的百炼密钥

if USE_OLD_KEYS and OLD_ACCESS_KEY_ID:
    access_key_id = OLD_ACCESS_KEY_ID
    access_key_secret = OLD_ACCESS_KEY_SECRET
    print("\n使用旧的API密钥...")
elif BAILIAN_ACCESS_KEY_ID:
    access_key_id = BAILIAN_ACCESS_KEY_ID
    access_key_secret = BAILIAN_ACCESS_KEY_SECRET
    print("\n使用百炼平台API密钥...")
else:
    print("\n❌ 错误: 未配置任何API密钥")
    sys.exit(1)

# 测试配置
test_text = "巴适"
output_file = "test_bailian.mp3"

# 尝试不同的API端点组合
API_ENDPOINTS = [
    "https://bailian.aliyuncs.com/api/v1/services/audio/tts/generate",  # 百炼平台端点
    "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/generate"   # 兼容旧端点
]

# 尝试不同的认证方式
AUTH_METHODS = [
    f"Bearer {access_key_id}",  # 方式1: Bearer Token
    f"AccessKey {access_key_id}:{access_key_secret}"  # 方式2: AccessKey认证
]

# 测试所有可能的组合
success = False

for endpoint in API_ENDPOINTS:
    if success:
        break
        
    for auth_method in AUTH_METHODS:
        if success:
            break
            
        print(f"\n=== 测试组合 ===\n")
        print(f"API端点: {endpoint}")
        print(f"认证方式: {auth_method[:20]}...")
        
        # API请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_method
        }
        
        # API请求体
        payload = {
            "model": "qwen-tts-v1",
            "input": {"text": test_text},
            "parameters": {"voice": "Sunny", "format": "mp3"}
        }
        
        try:
            print("\n2. 发送API请求...")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            print(f"3. 收到响应")
            print(f"   状态码: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"   响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"   响应内容: {response.text}")
            
            if response.status_code == 200:
                print(f"\n🎉 成功！API调用返回200状态码")
                
                data = response.json()
                if "output" in data and "audio_binary" in data["output"]:
                    audio_data = base64.b64decode(data["output"]["audio_binary"])
                    
                    with open(output_file, "wb") as f:
                        f.write(audio_data)
                    
                    print(f"\n✅ 音频文件保存成功！")
                    print(f"   文件: {output_file}")
                    print(f"   大小: {len(audio_data)} bytes")
                    
                    success = True
                    sys.exit(0)
                else:
                    print(f"\n❌ 响应中缺少必要的音频数据")
                    
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()

# 所有组合都尝试失败
print(f"\n=== 测试结束 ===\n")
print(f"❌ 所有测试组合都失败了")
print(f"\n可能的原因:")
print(f"1. API密钥格式不正确或已过期")
print(f"2. 百炼平台Qwen-TTS服务未开通")
print(f"3. 网络连接问题或防火墙限制")
print(f"4. API调用参数有误")
