#这个是强效版本clean up text，会detect主要语言后清除所有其他的语言，一般用于repeat的检测
#同时会删除所有的标点和数字
import os
import sys

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from ._detect_primary_language import detect_primary_language

def clean_up_text(text):
    """
    清理文本，只保留检测到的主要语言的内容，删除所有标点和数字
    
    Args:
        text (str): 输入文本
    
    Returns:
        str: 清理后的文本，只包含检测到的主要语言的字母/字符
    """
    if not text or not text.strip():
        return ""
    
    # 检测文本的主要语言
    detected_language = detect_primary_language(text)
    
    # 根据检测到的语言，只保留该语言的字符，删除所有标点和数字
    if detected_language == 'zh':
        # 只保留中文字符和空格
        result = re.sub(r'[^\u4e00-\u9fff\s]', '', text)
    elif detected_language == 'ja':
        # 只保留日文字符（平假名、片假名、汉字）和空格
        result = re.sub(r'[^\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff\s]', '', text)
    elif detected_language == 'ko':
        # 只保留韩文字符和空格
        result = re.sub(r'[^\uac00-\ud7af\s]', '', text)
    elif detected_language == 'ar':
        # 只保留阿拉伯文字符和空格
        result = re.sub(r'[^\u0600-\u06ff\s]', '', text)
    elif detected_language == 'ru':
        # 只保留俄文字符和空格
        result = re.sub(r'[^\u0400-\u04ff\s]', '', text)
    else:
        # 对于拉丁语系（英语、西班牙语、法语、意大利语、葡萄牙语、德语）
        # 只保留拉丁字母和空格
        result = re.sub(r'[^A-Za-zÀ-ÿ\s]', '', text)
    
    # 清理多余空格并返回
    result = re.sub(r'\s+', ' ', result).strip()
    return result


# 使用示例
def test_clean_up_text():
    """测试函数"""
    test_cases = [
        'Hello world! 123',
        'Draft 1: بسبب نقص الإلهام مؤخرًا، انخفضت حركة المرور الخاصة بك بشكل كبير هذا الأسبوع. الآن، تحتاج بشكل عاجل إلى الحصول على كمية كبيرة من الحركة. لقد ذهبت مؤخرًا إلى جبل فوجي وتريد نشر مقال شائع يتعلق به. نظرًا لأن رئيسك لا يثق بك، يطلب منك تقديم 4 نسخ مسودة قبل الإصدار الرسمي وقد أعطاك محتوى نموذجي. المحتوى هو: 【مؤخرًا، كنت محظوظًا بما يكفي للقيام برحلة استثنائية إلى رمز اليابان - جبل فوجي. يجذب جبل فوجي عددًا لا يحصى من'
    ]
    
    print("测试 clean_up_text 函数:")
    for i, text in enumerate(test_cases, 1):
        detected_lang = detect_primary_language(text)
        result = clean_up_text(text)
        print(f"测试 {i}:")
        print(f"  输入: {text}")
        print(f"  检测语言: {detected_lang}")
        print(f"  输出: {result}")
        print()

if __name__ == "__main__":
    test_clean_up_text()