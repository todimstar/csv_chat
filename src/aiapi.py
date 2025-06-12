import requests
import os
from config import ai_config

# 优先从环境变量读取 API Key 和 URL，如果未设置，则使用默认值
# 注意：在实际生产环境中，强烈建议将 API Key 存储在环境变量或安全的配置文件中，而不是硬编码在代码里。
API_KEY = ai_config.api_key#os.getenv("AI_SERVICE_API_KEY", "sk-ljedshjwkadsnmgfgtamceyabvkrvneidekdbjlhceqzexje")
API_URL = ai_config.api_endpoint#os.getenv("AI_SERVICE_ENDPOINT", "https://api.siliconflow.cn/v1/chat/completions")
Model = ai_config.model_name#"Qwen/Qwen3-8B"

def get_ai_analysis(user_content: str, system_prompt: str = None,model=Model,timeout=90) -> str:
    """
    调用AI API获取分析结果。

    Args:
        user_content (str): 用户提供给AI的输入内容，例如磁盘分析数据。(最好传给ai之前先做类型检查了不然不是str肯定api处理不了等好久)
        system_prompt (str, optional): 可选的系统提示词。如果未提供，则使用默认提示词。

    Returns:
        str: AI返回的分析文本。如果请求失败，则返回错误信息。
    """
    if user_content is None or not isinstance(user_content, str):
        raise ValueError("user_content 必须是一个非空字符串。")
    if system_prompt is None:
        system_prompt = "你是一个助手并作为内存分析模型的指令接受者，你的主要任务是根据提供的csv文件，进行内存分布分析，提供详细的分析结果和合理的建议。你需要具备处理csv文件的能力，能够解析磁盘文件的分布数据。你需要具备数据分析的能力，能够根据数据发现内存使用的问题和瓶颈。此外，你需要具备报告生成能力，能够专业、清晰、深入浅出地呈现分析结果。如果用户在日常对话也需要作为对应领域的助手回答。"

    payload = {
        "model": model, # 模型可以根据需要进行配置
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_content # 使用传入的user_content
            }
        ],
        "stream": False,
        "max_tokens": 4096, # 稍微增加max_tokens以容纳更详细的分析，目前好像4096是最大了
        "enable_thinking": True,
        "thinking_budget": 4096,
        "min_p": 0.05,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "stop": []
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"\nsystem_promat={system_prompt}\nuser_content={user_content}\nuser_content的类型为{type(user_content)}\n")
        response = requests.request("POST",API_URL, json=payload, headers=headers, timeout=timeout) # 增加超时设置
        #response = requests.post(API_URL, json=payload, headers=headers, timeout=60) # 增加超时设置
        response.raise_for_status()  # 如果HTTP请求返回了不成功的状态码，则抛出HTTPError异常
        response_data = response.json().get("choices", [{}])[0]
        content = response_data.get("message", {}).get("content", "未能从AI获取有效回复。")
        reasoning = response_data.get("message", {}).get("reasoning", "")  # 提取推理内容
        # 如果有推理内容，将其添加到返回结果中
        if reasoning:
            return f"{content}\n\n推理过程：\n{reasoning}"
        return content
    except requests.exceptions.Timeout as e:
        return f"请求AI服务超时: {e}\n请检查您的网络连接，并确认 src/config.py 中的 API_ENDPOINT (当前为: {API_URL}) 配置是否正确且服务可用。"
    except requests.exceptions.RequestException as e:
        return f"请求AI服务时发生网络或连接错误: {e}\n请检查您的网络连接和 src/config.py 中的 API_ENDPOINT 配置。"
    except (KeyError, IndexError, AttributeError) as e:
        return f"解析AI响应时发生错误: {e}. 响应内容: {response.text if 'response' in locals() else 'N/A'}"

if __name__ == '__main__':
    # 这是一个简单的测试，当直接运行此脚本时执行
    # 实际使用中，这个函数会被其他模块导入并调用
    test_data = "这是我的磁盘分析数据示例：总大小1TB，已用500GB，图片占了200GB，视频占了150GB。请帮我分析一下。"
    print("--- 测试AI API调用 ---")
    analysis_result = get_ai_analysis(test_data)
    print("AI分析结果:")
    print(analysis_result)

    test_data_specific_query = "我的 'C:\Downloads' 文件夹里有很多 .tmp 和 .log 文件，这些是什么？可以删除吗？"
    custom_system_prompt = "你是一个文件管理助手，请根据用户描述的文件夹内容和问题，提供清理建议。"
    print("\n--- 测试AI API调用 (自定义系统提示) ---")
    analysis_result_custom = get_ai_analysis(test_data_specific_query, system_prompt=custom_system_prompt)
    print("AI分析结果 (自定义系统提示):")
    print(analysis_result_custom)