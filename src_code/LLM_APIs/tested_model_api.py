from openai import OpenAI

# 全局变量存储OpenAI客户端
_tested_model_client = None
_tested_model_name = "default-model"

def set_tested_model_config(api_key, base_url=None, model_name="default-model"):
    """
    设置被测模型API配置
    
    Args:
        api_key: OpenAI API密钥
        base_url: API基础URL（可选，用于自定义端点）
        model_name: 模型名称（可选，默认为"default-model"）
    """
    global _tested_model_client, _tested_model_name
    
    if base_url:
        _tested_model_client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        _tested_model_client = OpenAI(api_key=api_key)
    
    _tested_model_name = model_name

def call_tested_model(prompt):
    """调用被测模型API"""
    if _tested_model_client is None:
        raise ValueError("Tested model not configured. Please call set_tested_model_config() first.")

    try:
        # 如果prompt是列表，批量处理
        if isinstance(prompt, list):
            results = []
            for single_prompt in prompt:
                response = _tested_model_client.chat.completions.create(
                    model=_tested_model_name,
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
            response = _tested_model_client.chat.completions.create(
                model=_tested_model_name,
                messages=[
                    {"role": "system", "content": ""},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=8096,
                temperature=0.00,
                timeout=1800
            )
            return [response.choices[0].message.content.strip()]

    except Exception as e:
        raise Exception(f"API call failed: {e}")