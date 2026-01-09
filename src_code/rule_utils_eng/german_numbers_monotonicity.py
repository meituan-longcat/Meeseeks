
import re

# 全局缓存，避免重复转换
_german_number_cache = {}

def _normalize_german_number(text):
    """规范化德语数字文本"""
    # 保留 'und'，因为解析器需要它
    return text.lower().strip()

def _parse_german_number(text):
    """
    解析德语数字文本
    按照从大到小的顺序处理：million -> tausend -> hundert -> und
    """
    text = text.lower().strip()
    
    # 德语基本数字
    units = {
        'null': 0, 'eins': 1, 'ein': 1, 'eine': 1, 'zwei': 2, 'drei': 3, 'vier': 4,
        'fünf': 5, 'sechs': 6, 'sieben': 7, 'acht': 8, 'neun': 9
    }
    
    teens = {
        'zehn': 10, 'elf': 11, 'zwölf': 12, 'dreizehn': 13, 'vierzehn': 14,
        'fünfzehn': 15, 'sechzehn': 16, 'siebzehn': 17, 'achtzehn': 18, 'neunzehn': 19
    }
    
    tens = {
        'zwanzig': 20, 'dreißig': 30, 'vierzig': 40, 'fünfzig': 50,
        'sechzig': 60, 'siebzig': 70, 'achtzig': 80, 'neunzig': 90
    }
    
    # 简单情况
    if text in units:
        return units[text]
    if text in teens:
        return teens[text]
    if text in tens:
        return tens[text]
    
    # 复杂解析 - 按照从大到小的顺序处理
    # 1. 处理百万
    if 'million' in text:
        parts = text.replace('millionen', 'million').split('million', 1)
        multiplier = _parse_german_number(parts[0]) if parts[0] else 1
        remainder = _parse_german_number(parts[1]) if len(parts) > 1 and parts[1] else 0
        if multiplier is not None:
            return (multiplier if multiplier > 0 else 1) * 1000000 + (remainder if remainder else 0)
    
    # 2. 处理千位 (例如: einundzwanzigtausend = 21 * 1000)
    if 'tausend' in text:
        parts = text.split('tausend', 1)
        multiplier = _parse_german_number(parts[0]) if parts[0] else 1
        remainder = _parse_german_number(parts[1]) if len(parts) > 1 and parts[1] else 0
        if multiplier is not None:
            return (multiplier if multiplier > 0 else 1) * 1000 + (remainder if remainder else 0)
    
    # 3. 处理百位 (例如: dreihundert = 3 * 100)
    if 'hundert' in text:
        parts = text.split('hundert', 1)
        multiplier = _parse_german_number(parts[0]) if parts[0] else 1
        remainder = _parse_german_number(parts[1]) if len(parts) > 1 and parts[1] else 0
        if multiplier is not None:
            return (multiplier if multiplier > 0 else 1) * 100 + (remainder if remainder else 0)
    
    # 4. 处理 "und" 连接的数字 (例如: fünfundvierzig = 5 + 40 = 45)
    # 注意：德语中 "und" 只用于个位和十位之间
    if 'und' in text:
        parts = text.split('und', 1)
        if len(parts) == 2:
            # 递归解析两部分
            left = _parse_german_number(parts[0]) if parts[0] else 0
            right = _parse_german_number(parts[1]) if parts[1] else 0
            # 如果左边为空或为None，说明是 "undeins" 这种情况，只返回右边
            if left is None or left == 0:
                return right
            if right is None:
                return left
            if left is not None and right is not None:
                return left + right
    
    return None

def _find_number_value(num_str):
    """
    使用自定义德语数字解析器和缓存查找德语数字对应的数值
    """
    num_str_cleaned = _normalize_german_number(num_str)
    
    # 检查缓存
    if num_str_cleaned in _german_number_cache:
        return _german_number_cache[num_str_cleaned]
    
    try:
        # 使用自定义解析器
        num_value = _parse_german_number(num_str_cleaned)
        
        if num_value is not None:
            # 缓存结果
            _german_number_cache[num_str_cleaned] = num_value
            return num_value
    except Exception as e:
        pass
    
    return None

def check_number_monotonicity(model_response):
    """
    检查模型输出的数字的单调性是否符合要求（递增或递减）。

    :param model_response: 模型输出的数字书写形式（列表）
    :return: (True/False, 消息)
    """
    if not model_response:
        return False, "❌ 输入列表为空。"
    
    if len(model_response) == 1:
        return True, "✅ 单个数字默认满足单调性要求。"
    
    # 将所有模型输出转换为数字
    numbers = []
    for idx, num_str in enumerate(model_response):
        num_value = _find_number_value(num_str)
        
        if num_value is None:
            return False, f"❌ 第 {idx + 1} 个数字 '{num_str}' 无法识别或转换。"
        numbers.append(num_value)

    # 判断单调性（提前终止优化）
    is_increasing = True
    is_decreasing = True
    
    for i in range(len(numbers) - 1):
        if numbers[i] >= numbers[i + 1]:
            is_increasing = False
        if numbers[i] <= numbers[i + 1]:
            is_decreasing = False
        
        # 如果两个都不满足，可以提前终止
        if not is_increasing and not is_decreasing:
            break

    # 返回结果
    if is_increasing:
        return True, f"✅ 数字是严格递增的：{numbers}"
    elif is_decreasing:
        return True, f"✅ 数字是严格递减的：{numbers}"
    else:
        # 提供更详细的错误信息
        return False, f"❌ 数字既不是递增也不是递减。序列为：{numbers}"

# 示例：模型输出的数字书写形式列表
# # (递增)
model_response1 = [
    "einunddreißig",  # 31 
    "einundzwanzigtausenddreihundertfünfundvierzig", # 21345 
    "einhunderteinundzwanzigtausenddreihundertneunundsechzig"  # 121369
]

# 递减
model_response2 = [
    "Einhunderteinundzwanzigtausenddreihundertneunundsechzig",  # 121369 
    "einundzwanzigtausenddreihundertfünfundvierzig",  # 21345 
    "einunddreißig"  # 31
]

# 不单调
model_response3 = [
    "einunddreißig",  # 31
    "Einhunderteinundzwanzigtausenddreihundertneunundsechzig",  # 121369 
    "einundzwanzigtausenddreihundertfünfundvierzig",  # 21345
    "neunhunderteinsundzwanzigtausendsechshundertachtundzwanzig" 
]

# 调用函数进行单调性检查
is_monotonic1 = check_number_monotonicity(model_response1)
is_monotonic2 = check_number_monotonicity(model_response2)
is_monotonic3 = check_number_monotonicity(model_response3)

print("检查结果1:", is_monotonic1)
print("检查结果2:", is_monotonic2)
print("检查结果3:", is_monotonic3)
