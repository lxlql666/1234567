"""
四川方言视频生成工具使用 Wan2.6 文生视频模型生成四川话话剧视频
"""
import os
import time
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SichuanVideoGenerator:
    """
    四川方言视频生成器类
    使用阿里云百炼平台的Wan2.6-text to vedio文生视频模型生成视频
    """
    
    def __init__(self, api_key=None, region=None, host=None):
        """
        初始化视频生成器
        
        Args:
            api_key: 百炼平台API密钥，如果不提供则从环境变量读取
            region: API地域，如果不提供则从环境变量读取
            host: API主机地址，如果不提供则根据地域自动选择
        """
        # 读取API密钥
        self.api_key = api_key or \
                     os.getenv('BAILIAN_API_KEY') or \
                     os.getenv('DASHSCOPE_API_KEY') or \
                     os.getenv('BAILIAN_ACCESS_KEY_SECRET')
        
        # 读取并初始化地域配置
        self.region = region or os.getenv('BAILIAN_REGION') or os.getenv('DASHSCOPE_REGION', 'cn-beijing')
        
        # 读取并初始化主机地址
        self.host = host or os.getenv('BAILIAN_HOST') or os.getenv('DASHSCOPE_HOST')
        
        # 如果没有手动指定主机地址，则根据地域自动选择
        if not self.host:
            # 默认地域映射
            region_host_map = {
                'cn-beijing': 'dashscope.aliyuncs.com',
                'cn-shanghai': 'dashscope.aliyuncs.com',
                'cn-shenzhen': 'dashscope.aliyuncs.com',
                'ap-southeast-1': 'dashscope.ap-southeast-1.aliyuncs.com',
                'us-west-1': 'dashscope.us-west-1.aliyuncs.com',
            }
            self.host = region_host_map.get(self.region, 'dashscope.aliyuncs.com')
        
        if not self.api_key:
            raise ValueError("未配置API密钥，请设置BAILIAN_API_KEY或DASHSCOPE_API_KEY环境变量")
        
        # API配置（根据官网文档）
        self.synthesis_path = "/api/v1/services/aigc/video-generation/video-synthesis"
        self.task_path_template = "/api/v1/tasks/{task_id}"

        print(f"\n=== 视频生成器配置 ===")
        print(f"地域: {self.region}")
        print(f"API主机: {self.host}")
        print(f"API密钥: {'已配置' if self.api_key else '未配置'}")

        # 通用请求头（异步任务模式）
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable",  # 必须启用异步模式
        }
    
    def generate_video(self, prompt, duration=10, prompt_extend=True,
                      shot_type="multi", audio=True, retry_interval=5,
                      progress_callback=None):
        """
        生成四川方言话剧视频

        Args:
            prompt: 视频生成提示词
            duration: 视频时长（秒），默认10秒
            prompt_extend: 是否扩展提示词，默认True
            shot_type: 镜头类型，multi/single，默认multi
            audio: 是否添加音频，默认True
            max_retries: 最大轮询次数，默认30次
            retry_interval: 轮询间隔（秒），默认10秒

        Returns:
            tuple: (success, result)，success为布尔值，result为视频URL或错误信息
        """
        try:
            # 固定视频参数为1280*720
            fixed_parameters = {
                "size": "1280*720",  # 固定分辨率为1280*720 (16:9)
                "prompt_extend": bool(prompt_extend),
                "duration": int(duration),
                "shot_type": str(shot_type),
                "audio": bool(audio)
            }
            
            print("=== 视频生成参数 ===")
            print(f"模型名称: wan2.6-t2v")
            print(f"提示词: {prompt}")
            print(f"参数: {fixed_parameters}")

            # 统一使用 HTTP 请求调用百炼视频生成（避免 SDK 版本差异问题）
            print("\n=== 使用 HTTP 请求生成视频 ===")
            payload = {
                "model": "wan2.6-t2v",
                "input": {
                    "prompt": str(prompt),
                },
                "parameters": fixed_parameters,
            }

            # 发送创建任务请求
            create_url = f"https://{self.host}{self.synthesis_path}"
            response = requests.post(create_url, headers=self.headers, data=json.dumps(payload), timeout=60)

            # 异步创建通常返回 200 或 202，都视为成功受理
            if response.status_code not in (200, 202):
                return False, f"任务提交失败，状态码：{response.status_code}，错误信息：{response.text}"

            task_data = response.json()
            # 有的版本在顶层返回 task_id，有的在 output 里返回
            task_id = task_data.get("task_id") or task_data.get("output", {}).get("task_id")
            if not task_id:
                return False, f"任务创建失败，响应格式异常：{task_data}"

            print(f"任务创建成功！Task ID: {task_id}")

            # 轮询任务状态
            task_url = f"https://{self.host}{self.task_path_template.format(task_id=task_id)}"
            poll_index = 0
            while True:
                poll_index += 1
                status_resp = requests.get(task_url, headers=self.headers, timeout=30)
                if status_resp.status_code != 200:
                    return False, f"查询任务状态失败，状态码：{status_resp.status_code}，响应：{status_resp.text}"

                status_data = status_resp.json()
                # 不同版本字段可能不同：优先使用 output.task_status，其次顶层 status
                status = (
                    status_data.get("output", {}).get("task_status")
                    or status_data.get("status")
                )
                print(f"\n=== 任务状态查询 ({poll_index}) ===")
                print(f"状态: {status}")

                # 通知前端更新进度显示（基于轮询次数和状态）
                if progress_callback is not None:
                    try:
                        progress_callback(poll_index, status)
                    except Exception:
                        # 前端回调失败不影响后端轮询
                        pass

                if status == "SUCCEEDED":
                    output = status_data.get("output", {})
                    # 常见返回为 output.video_url；如有变更，可在这里扩展
                    video_url = output.get("video_url")
                    if video_url:
                        print(f"✅ 视频生成成功！视频URL: {video_url}")
                        return True, video_url
                    else:
                        return False, f"视频URL获取失败，响应：{status_data}"
                elif status == "FAILED":
                    error_msg = status_data.get("message", "未知错误")
                    error_details = status_data.get("error_details", "无详细错误信息")
                    return False, f"视频生成失败：{error_msg}\n详细错误：{error_details}"

                # 处理中间状态，等待一段时间后继续轮询
                print(f"⏳ 视频生成中，当前状态：{status}，已等待 {poll_index * retry_interval} 秒...")
                time.sleep(retry_interval)
                
        except Exception as e:
            import traceback
            return False, f"视频生成异常：{str(e)}\n堆栈信息：{traceback.format_exc()}"
    
    def generate_sichuan_video(self, prompt_content, duration=10, progress_callback=None):
        """
        生成四川方言话剧视频的简化接口
        
        Args:
            prompt_content: 视频主题、角色和剧情要求
            duration: 视频时长（秒）
            
        Returns:
            tuple: (success, result)，success为布尔值，result为视频URL或错误信息
        """
        # 构建完整提示词，明确要求四川方言音频
        full_prompt = f"请生成一段关于{prompt_content}的四川方言话剧视频，" \
                     f"所有对话和旁白必须使用地道的四川方言，" \
                     f"音频清晰，四川话发音标准，画面风格生动有趣，适合舞台表演。"
        
        return self.generate_video(full_prompt, duration=duration, progress_callback=progress_callback)

# 使用示例
if __name__ == "__main__":
    try:
        # 初始化视频生成器
        generator = SichuanVideoGenerator()
        
        # 生成四川方言视频
        prompt = "四川人的日常对话，角色是火锅老板和顾客"
        print(f"开始生成视频：{prompt}")
        
        success, result = generator.generate_sichuan_video(prompt)
        
        if success:
            print(f"✅ 视频生成成功！")
            print(f"📺 视频URL：{result}")
        else:
            print(f"❌ 视频生成失败：{result}")
            
    except Exception as e:
        print(f"❌ 初始化失败：{str(e)}")
