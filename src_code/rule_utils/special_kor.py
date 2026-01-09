from ..utils import clean_up_text
import re

# 1
import re

def has_double_consonants(texts, times):
    """检查是否刚好包含指定数量的韩语双辅音（된소리）"""
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    # 包含双辅音的韩文字符（ㄲ, ㄸ, ㅃ, ㅆ, ㅉ）
    double_consonant_chars = ['ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ']
    
    # 包含双辅音的完整音节范围
    double_consonant_pattern = r'[까-낗따-띻빠-삫싸-앃짜-찧]'
    
    total_count = 0
    found_consonants = []
    
    # 统计每个文本中的双辅音
    for text in cleaned_up_texts:
        text_consonants = []
        
        # 检查双辅音字符
        for char in double_consonant_chars:
            count = text.count(char)
            if count > 0:
                text_consonants.extend([char] * count)
                total_count += count
        
        # 检查包含双辅音的完整音节
        matches = re.findall(double_consonant_pattern, text)
        if matches:
            text_consonants.extend(matches)
            total_count += len(matches)
        
        if text_consonants:
            found_consonants.append(text_consonants)
        else:
            found_consonants.append([])
    
    # 格式化双辅音列表显示
    consonant_display = []
    for i, consonants in enumerate(found_consonants):
        if consonants:
            consonant_display.append(f"Text {i+1}: {', '.join(consonants)}")
        else:
            consonant_display.append(f"Text {i+1}: None")
    
    consonant_info = " | ".join(consonant_display)
    
    # 检查是否刚好等于指定次数
    if total_count == times:
        return 1, f"✅ ({consonant_info}) perfectly matches the expected count of {times}"
    else:
        return 0, f"❌ ({consonant_info}) does NOT match the expected count of {times} (found {total_count})"
    
def each_has_double_consonants(texts, times):
    """检查每个文本是否都刚好包含指定数量的韩语双辅音（된소리）"""
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    # 包含双辅音的韩文字符（ㄲ, ㄸ, ㅃ, ㅆ, ㅉ）
    double_consonant_chars = ['ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ']
    
    # 包含双辅音的完整音节范围
    double_consonant_pattern = r'[까-낗따-띻빠-삫싸-앃짜-찧]'
    
    text_results = []
    all_match = True
    
    # 检查每个文本中的双辅音
    for i, text in enumerate(cleaned_up_texts):
        text_consonants = []
        text_count = 0
        
        # 检查双辅音字符
        for char in double_consonant_chars:
            count = text.count(char)
            if count > 0:
                text_consonants.extend([char] * count)
                text_count += count
        
        # 检查包含双辅音的完整音节
        matches = re.findall(double_consonant_pattern, text)
        if matches:
            text_consonants.extend(matches)
            text_count += len(matches)
        
        # 检查当前文本是否匹配
        text_matches = text_count == times
        if not text_matches:
            all_match = False
        
        # 格式化当前文本的结果
        consonant_str = ', '.join(text_consonants) if text_consonants else 'None'
        status = "✅" if text_matches else "❌"
        text_results.append(f"Text {i+1}: {status} ({consonant_str}) - found {text_count}")
    
    # 生成最终结果信息
    result_info = " | ".join(text_results)
    
    if all_match:
        return 1, f"✅ All texts match the expected count of {times}: {result_info}"
    else:
        return 0, f"❌ Not all texts match the expected count of {times}: {result_info}"

def has_korean_abbreviation(texts, abbreviation):
    """检查每个文本是否都符合指定的韩语缩写模式"""
    
    # 添加调试输出
    print(f"原始文本: {texts}")
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    print(f"清理后文本: {cleaned_up_texts}")
    
    # 将缩写转换为正则表达式模式
    # 例如 "ㅇㅂ" -> 每个字符对应一个韩语音节的初声
    consonant_map = {
        'ㄱ': '[가-깋]', 'ㄴ': '[나-닣]', 'ㄷ': '[다-딯]', 'ㄹ': '[라-맇]',
        'ㅁ': '[마-밓]', 'ㅂ': '[바-빟]', 'ㅅ': '[사-싷]', 'ㅇ': '[아-잏]',
        'ㅈ': '[자-짛]', 'ㅊ': '[차-칳]', 'ㅋ': '[카-킿]', 'ㅌ': '[타-팋]',
        'ㅍ': '[파-핗]', 'ㅎ': '[하-힣]',
        # 双辅音
        'ㄲ': '[까-낗]', 'ㄸ': '[따-띻]', 'ㅃ': '[빠-삫]', 'ㅆ': '[싸-앃]', 'ㅉ': '[짜-찧]'
    }
    
    # 构建正则表达式模式
    pattern_parts = []
    for char in abbreviation:
        if char in consonant_map:
            pattern_parts.append(consonant_map[char])
        else:
            return 0, f"❌ 无效的韩语辅音: {char}"
    
    # 创建完整的正则表达式模式
    full_pattern = ''.join(pattern_parts)
    print(f"生成的正则表达式模式: {full_pattern}")
    
    results = []
    all_match = True
    
    # 检查每个文本
    for i, text in enumerate(cleaned_up_texts):
        if re.fullmatch(full_pattern, text):
            results.append(f"Text {i+1}: '{text}' ✅")
        else:
            results.append(f"Text {i+1}: '{text}' ❌")
            all_match = False
    
    result_info = " | ".join(results)
    
    if all_match:
        return 1, f"✅ ({result_info}) 所有文本都符合缩写 '{abbreviation}'"
    else:
        return 0, f"❌ ({result_info}) 不是所有文本都符合缩写 '{abbreviation}'"