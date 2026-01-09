import os
import sys

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import Counter
from ..utils import clean_up_text

try:
    import hgtk
    hgtk_AVAILABLE = True
except ImportError:
    hgtk_AVAILABLE = False
    print("hgtk库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "hgtk"])
        print("hgtk库安装成功，正在导入...")
        import hgtk
        hgtk_AVAILABLE = True
        print("✅ hgtk库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install hgtk")
        hgtk_AVAILABLE = False

import hgtk  # 한글 toolkit for Korean text processing


def extract_korean_rhyme(words):
    """提取韩文单词的韵脚（基于最后一个音节的元音和韵尾）"""
    rhyme_elements = []
    
    for word in words:
        if word:  # 确保不是空字符串
            # 获取最后一个字符
            last_char = word[-1]
            
            # 检查是否为韩文字符
            if hgtk.checker.is_hangul(last_char):
                try:
                    # 分解韩文字符为初声、中声、终声
                    decomposed = hgtk.letter.decompose(last_char)
                    
                    # 提取中声（元音）和终声（韵尾）作为韵脚
                    vowel = decomposed[1] if len(decomposed) > 1 else ''
                    final = decomposed[2] if len(decomposed) > 2 else ''
                    
                    # 组合元音和韵尾作为韵脚特征
                    rhyme = vowel + final
                    rhyme_elements.append(rhyme)
                except:
                    # 如果分解失败，跳过该字符
                    continue
    
    return rhyme_elements


def calculate_rhyme_proportion(rhyme_vowels):
    # 统计每个韵母出现的次数
    rhyme_count = Counter(rhyme_vowels)
    total_rhymes = sum(rhyme_count.values())
    
    # 计算每个韵母的比例
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    return rhyme_proportion


def kor_yayun(text):
    """韩文押韵检测函数"""
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    rhyme_elements = extract_korean_rhyme(text)
    
    if not rhyme_elements:
        return 0, "❌ 未检测到韩文字符或无法提取韵脚"
    
    rhyme_proportion = calculate_rhyme_proportion(rhyme_elements)
    
    if max(rhyme_proportion.values()) > 0.5:
        return 1, f"✅ 匹配，韵脚比例详情为：{str(rhyme_proportion)}"
    else:
        return 0, f"❌ 不匹配，韵脚比例详情为：{str(rhyme_proportion)}，没有一个韵脚比例超过50%，韵脚比例超过50%视为押韵"


def extract_korean_even_rhyme(text):
    """提取韩文偶数句的韵脚"""
    rhyme_elements = []
    
    # 遍历偶数句
    for i in range(1, len(text), 2):  # 从第二句开始，步长为2
        word = text[i]
        if word:  # 确保不是空字符串
            # 获取最后一个字符
            last_char = word[-1]
            
            # 检查是否为韩文字符
            if hgtk.checker.is_hangul(last_char):
                try:
                    # 分解韩文字符为初声、中声、终声
                    decomposed = hgtk.letter.decompose(last_char)
                    
                    # 提取中声（元音）和终声（韵尾）作为韵脚
                    vowel = decomposed[1] if len(decomposed) > 1 else ''
                    final = decomposed[2] if len(decomposed) > 2 else ''
                    
                    # 组合元音和韵尾作为韵脚特征
                    rhyme = vowel + final
                    rhyme_elements.append(rhyme)
                except:
                    # 如果分解失败，跳过该字符
                    continue
    
    return rhyme_elements


def korean_lvshi_yayun(text):
    """韩文律诗押韵检测（偶数句押韵）"""
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    # 提取偶数句的韵母
    rhyme_elements = extract_korean_even_rhyme(text)
    
    if not rhyme_elements:
        return 0, "❌ 未检测到韩文字符或无法提取韵脚"
    
    # 判断偶数句的韵母是否一致
    if len(set(rhyme_elements)) == 1:  # 如果集合长度为1，说明韵母一致
        return 1, f"✅ 偶数句韵母一致，偶数句韵母为：{rhyme_elements}"
    else:
        return 0, f"❌ 偶数句韵母不一致，偶数句韵母为：{rhyme_elements}"


if __name__ == "__main__":
    # 测试用例1: 基本押韵 - 相同韵尾
    print("=== 测试用例1: 基本押韵 ===")
    test1 = ["사랑", "희망", "꿈장", "마음"]  # 都以 'ㅏㅇ' 韵脚结尾
    result1, msg1 = korean_yayun(test1)
    print(f"测试1结果: {result1}, 消息: {msg1}")
    
    # 测试用例2: 不押韵 - 不同韵尾
    print("\n=== 测试用例2: 不押韵 ===")
    test2 = ["사람", "하늘", "바다", "산"]  # 不同韵脚
    result2, msg2 = korean_yayun(test2)
    print(f"测试2结果: {result2}, 消息: {msg2}")
    
    # 测试用例3: 律诗押韵 - 偶数句押韵
    print("\n=== 测试用例3: 律诗偶数句押韵 ===")
    test3 = ["봄이 온다", "꽃이 핀다", "새가 운다", "바람 분다"]  # 偶数句(2,4句)押韵
    result3, msg3 = korean_lvshi_yayun(test3)
    print(f"测试3结果: {result3}, 消息: {msg3}")
    
    # 测试用例4: 律诗不押韵 - 偶数句不押韵
    print("\n=== 测试용례4: 律诗偶数句不押韵 ===")
    test4 = ["하늘이 높다", "바다가 깊다", "산이 크다", "강이 길다"]  # 偶数句不押韵
    result4, msg4 = korean_lvshi_yayun(test4)
    print(f"测试4结果: {result4}, 消息: {msg4}")
    
    # 测试用例5: 相同元音押韵
    print("\n=== 测试용례5: 相同元音押韵 ===")
    test5 = ["나무", "바구", "가루", "다루"]  # 都以 'ㅜ' 元音结尾
    result5, msg5 = korean_yayun(test5)
    print(f"测试5结果: {result5}, 消息: {msg5}")
    
    # 测试用例6: 混合中韩文
    print("\n=== 测试용례6: 混合中韩文 ===")
    test6 = ["안녕", "你好", "사랑", "爱情"]  # 混合文字
    result6, msg6 = korean_yayun(test6)
    print(f"测试6结果: {result6}, 消息: {msg6}")
    
    # 测试用例7: 空字符串处理
    print("\n=== 测试용례7: 空字符串处理 ===")
    test7 = ["", "안녕", "", "사랑"]  # 包含空字符串
    result7, msg7 = korean_yayun(test7)
    print(f"测试7结果: {result7}, 消息: {msg7}")
    
    # 测试用例8: 单字韩文
    print("\n=== 测试용례8: 单字韩文 ===")
    test8 = ["강", "장", "방", "상"]  # 单字押韵
    result8, msg8 = korean_yayun(test8)
    print(f"测试8结果: {result8}, 消息: {msg8}")
    
    # 测试用例9: 完全不同的韵脚
    print("\n=== 测试용례9: 完全不同韵脚 ===")
    test9 = ["고양이", "강아지", "토끼", "새"]  # 完全不同的韵脚
    result9, msg9 = korean_yayun(test9)
    print(f"测试9结果: {result9}, 消息: {msg9}")
    
    # 测试用例10: 韩文诗歌示例
    print("\n=== 测试용례10: 韩文诗歌示例 ===")
    test10 = ["봄바람 불어오네", "꽃잎이 흩날리네", "새소리 들려오네", "마음이 설레이네"]  # 诗歌格式
    result10, msg10 = korean_yayun(test10)
    print(f"测试10结果: {result10}, 消息: {msg10}")
    
    print("\n=== 韩文押韵测试完成 ===")