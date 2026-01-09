from openai import OpenAI

# 全局变量存储OpenAI客户端
_qwen_coder_client = None
_qwen_coder_model_name = "qwen-coder-model"

def set_qwen_coder_config(api_key, base_url=None, model_name="qwen-coder-model"):
    """
    设置Qwen Coder API配置
    
    Args:
        api_key: OpenAI API密钥
        base_url: API基础URL（可选，用于自定义端点）
        model_name: 模型名称（可选，默认为"qwen-coder-model"）
    """
    global _qwen_coder_client, _qwen_coder_model_name
    
    if base_url:
        _qwen_coder_client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        _qwen_coder_client = OpenAI(api_key=api_key)
    
    _qwen_coder_model_name = model_name

def call_coder_model(prompts):
    """调用Qwen Coder模型API"""
    if _qwen_coder_client is None:
        raise ValueError("Qwen Coder not configured. Please call set_qwen_coder_config() first.")

    try:
        # 如果prompts是列表，批量处理
        if isinstance(prompts, list):
            results = []
            for single_prompt in prompts:
                response = _qwen_coder_client.chat.completions.create(
                    model=_qwen_coder_model_name,
                    messages=[
                        {"role": "system", "content": ""},
                        {"role": "user", "content": single_prompt},
                    ],
                    max_tokens=8096,
                    temperature=0.00,
                    timeout=1800
                )
                results.append(response.choices[0].message.content.strip())
            return results
        else:
            # 单个prompt
            response = _qwen_coder_client.chat.completions.create(
                model=_qwen_coder_model_name,
                messages=[
                    {"role": "system", "content": ""},
                    {"role": "user", "content": prompts},
                ],
                max_tokens=8096,
                temperature=0.00,
                timeout=1800
            )
            return [response.choices[0].message.content.strip()]

    except Exception as e:
        raise Exception(f"API call failed: {e}")