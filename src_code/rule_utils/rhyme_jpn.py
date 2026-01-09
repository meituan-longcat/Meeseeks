import os
import sys

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from collections import Counter


# 尝试导入pykakasi库（用于日文处理）
try:
    import hanziconv
    hanziconv_AVAILABLE = True
except ImportError:
    hanziconv_AVAILABLE = False
    print("hanziconv库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "hanziconv", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("hanziconv库安装成功，正在导入...")
        import hanziconv
        hanziconv_AVAILABLE = True
        print("✅ hanziconv库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install hanziconv")
        hanziconv_AVAILABLE = False


from hanziconv import HanziConv

# 尝试导入pykakasi库（用于日文处理）
try:
    import pykakasi
    pykakasi_AVAILABLE = True
except ImportError:
    pykakasi_AVAILABLE = False
    print("pykakasi库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pykakasi"])
        print("pykakasi库安装成功，正在导入...")
        import pykakasi
        pykakasi_AVAILABLE = True
        print("✅ pykakasi库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install pykakasi")
        pykakasi_AVAILABLE = False

# 尝试导入jaconv库（用于假名转换）
try:
    import jaconv
    jaconv_AVAILABLE = True
except ImportError:
    jaconv_AVAILABLE = False
    print("jaconv库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "jaconv"])
        print("jaconv库安装成功，正在导入...")
        import jaconv
        jaconv_AVAILABLE = True
        print("✅ jaconv库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install jaconv")
        jaconv_AVAILABLE = False


def convert_to_hiragana(text):
    """将文本转换为平假名（包括汉字转换）"""
    if not pykakasi_AVAILABLE:
        print("❌ pykakasi库不可用，无法转换汉字")
        return text
    
    # 使用pykakasi将汉字转换为平假名
    kks = pykakasi.kakasi()
    result = kks.convert(text)
    
    # 提取平假名读音
    hiragana_text = ''.join([item['hira'] for item in result])
    
    # 如果有片假名，转换为平假名
    if jaconv_AVAILABLE:
        hiragana_text = jaconv.kata2hira(hiragana_text)
    
    return hiragana_text


def extract_japanese_rhyme(words):
    """提取日文单词的韵脚（基于最后音节的元音）- 改进版支持汉字"""
    rhyme_elements = []
    
    # 日文元音映射
    vowel_map = {
        'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
        'か': 'a', 'き': 'i', 'く': 'u', 'け': 'e', 'こ': 'o',
        'が': 'a', 'ぎ': 'i', 'ぐ': 'u', 'げ': 'e', 'ご': 'o',
        'さ': 'a', 'し': 'i', 'す': 'u', 'せ': 'e', 'そ': 'o',
        'ざ': 'a', 'じ': 'i', 'ず': 'u', 'ぜ': 'e', 'ぞ': 'o',
        'た': 'a', 'ち': 'i', 'つ': 'u', 'て': 'e', 'と': 'o',
        'だ': 'a', 'ぢ': 'i', 'づ': 'u', 'で': 'e', 'ど': 'o',
        'な': 'a', 'に': 'i', 'ぬ': 'u', 'ね': 'e', 'の': 'o',
        'は': 'a', 'ひ': 'i', 'ふ': 'u', 'へ': 'e', 'ほ': 'o',
        'ば': 'a', 'び': 'i', 'ぶ': 'u', 'べ': 'e', 'ぼ': 'o',
        'ぱ': 'a', 'ぴ': 'i', 'ぷ': 'u', 'ぺ': 'e', 'ぽ': 'o',
        'ま': 'a', 'み': 'i', 'む': 'u', 'め': 'e', 'も': 'o',
        'や': 'a', 'ゆ': 'u', 'よ': 'o',
        'ら': 'a', 'り': 'i', 'る': 'u', 'れ': 'e', 'ろ': 'o',
        'わ': 'a', 'を': 'o', 'ん': 'n',
        # 长音和特殊字符
        'ー': '-', 'っ': 'tsu'
    }
    
    for word in words:
        if word:  # 确保不是空字符串
            # 先转换为平假名（包括汉字）
            hiragana = convert_to_hiragana(word)
            # print(f"原文: {word} -> 平假名: {hiragana}")  # 调试信息
            
            # 获取最后的音节
            last_chars = []
            if len(hiragana) >= 2 and hiragana[-1] == 'ー':  # 长音符号
                last_chars = [hiragana[-2], hiragana[-1]]
            elif len(hiragana) >= 2 and hiragana[-1] in ['ゃ', 'ゅ', 'ょ']:  # 拗音
                last_chars = [hiragana[-2], hiragana[-1]]
            elif len(hiragana) >= 1 and hiragana[-1] == 'ん':  # 拨音
                # 如果以ん结尾，取前面的音节
                if len(hiragana) >= 2:
                    last_chars = [hiragana[-2], hiragana[-1]]
                else:
                    last_chars = [hiragana[-1]]
            else:
                last_chars = [hiragana[-1]]
            
            # 提取韵脚元音
            rhyme = ''
            for char in last_chars:
                if char in vowel_map:
                    rhyme += vowel_map[char]
                else:
                    # 如果字符不在映射表中，尝试直接使用
                    rhyme += char
            
            if rhyme:
                rhyme_elements.append(rhyme)
                # print(f"韵脚: {rhyme}")  # 调试信息
    
    return rhyme_elements


def calculate_rhyme_proportion(rhyme_elements):
    """统计韵脚比例"""
    rhyme_count = Counter(rhyme_elements)
    total_rhymes = sum(rhyme_count.values())
    
    if total_rhymes == 0:
        return {}
    
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    return rhyme_proportion


def jpn_yayun(text):
    """日文押韵检测函数 - 改进版支持汉字"""
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    rhyme_elements = extract_japanese_rhyme(text)
    
    if not rhyme_elements:
        return 0, "❌ 未检测到日文字符或无法提取韵脚"
    
    rhyme_proportion = calculate_rhyme_proportion(rhyme_elements)
    
    if max(rhyme_proportion.values()) > 0.5:
        return 1, f"✅ 匹配，韵脚比例详情为：{str(rhyme_proportion)}"
    else:
        return 0, f"❌ 不匹配，韵脚比例详情为：{str(rhyme_proportion)}，没有一个韵脚比例超过50%，韵脚比例超过50%视为押韵"


def extract_japanese_even_rhyme(text):
    """提取日文偶数句的韵脚（用于和歌、俳句等）- 改进版支持汉字"""
    rhyme_elements = []
    
    # 日文元音映射
    vowel_map = {
        'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
        'か': 'a', 'き': 'i', 'く': 'u', 'け': 'e', 'こ': 'o',
        'が': 'a', 'ぎ': 'i', 'ぐ': 'u', 'げ': 'e', 'ご': 'o',
        'さ': 'a', 'し': 'i', 'す': 'u', 'せ': 'e', 'そ': 'o',
        'ざ': 'a', 'じ': 'i', 'ず': 'u', 'ぜ': 'e', 'ぞ': 'o',
        'た': 'a', 'ち': 'i', 'つ': 'u', 'て': 'e', 'と': 'o',
        'だ': 'a', 'ぢ': 'i', 'づ': 'u', 'で': 'e', 'ど': 'o',
        'な': 'a', 'に': 'i', 'ぬ': 'u', 'ね': 'e', 'の': 'o',
        'は': 'a', 'ひ': 'i', 'ふ': 'u', 'へ': 'e', 'ほ': 'o',
        'ば': 'a', 'び': 'i', 'ぶ': 'u', 'べ': 'e', 'ぼ': 'o',
        'ぱ': 'a', 'ぴ': 'i', 'ぷ': 'u', 'ぺ': 'e', 'ぽ': 'o',
        'ま': 'a', 'み': 'i', 'む': 'u', 'め': 'e', 'も': 'o',
        'や': 'a', 'ゆ': 'u', 'よ': 'o',
        'ら': 'a', 'り': 'i', 'る': 'u', 'れ': 'e', 'ろ': 'o',
        'わ': 'a', 'を': 'o', 'ん': 'n',
        'ー': '-', 'っ': 'tsu'
    }
    
    # 遍历偶数句
    for i in range(1, len(text), 2):  # 从第二句开始，步长为2
        word = text[i]
        if word:  # 确保不是空字符串
            # 转换为平假名（包括汉字）
            hiragana = convert_to_hiragana(word)
            
            # 获取最后的音节
            last_chars = []
            if len(hiragana) >= 2 and hiragana[-1] == 'ー':  # 长音符号
                last_chars = [hiragana[-2], hiragana[-1]]
            elif len(hiragana) >= 2 and hiragana[-1] in ['ゃ', 'ゅ', 'ょ']:  # 拗音
                last_chars = [hiragana[-2], hiragana[-1]]
            elif len(hiragana) >= 1 and hiragana[-1] == 'ん':  # 拨音
                if len(hiragana) >= 2:
                    last_chars = [hiragana[-2], hiragana[-1]]
                else:
                    last_chars = [hiragana[-1]]
            else:
                last_chars = [hiragana[-1]]
            
            # 提取韵脚元音
            rhyme = ''
            for char in last_chars:
                if char in vowel_map:
                    rhyme += vowel_map[char]
                else:
                    rhyme += char
            
            if rhyme:
                rhyme_elements.append(rhyme)
    
    return rhyme_elements


def jpn_waka_yayun(text):
    """日文和歌押韵检测（偶数句押韵）- 改进版支持汉字"""
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    # 提取偶数句的韵脚
    rhyme_elements = extract_japanese_even_rhyme(text)
    
    if not rhyme_elements:
        return 0, "❌ 未检测到日文字符或无法提取韵脚"
    
    # 判断偶数句的韵脚是否一致
    if len(set(rhyme_elements)) == 1:  # 如果集合长度为1，说明韵脚一致
        return 1, f"✅ 偶数句韵脚一致，偶数句韵脚为：{rhyme_elements}"
    else:
        return 0, f"❌ 偶数句韵脚不一致，偶数句韵脚为：{rhyme_elements}"


def jpn_shigin_jielong(text_list):
    """日文诗吟接龙（类似成语接龙）- 改进版支持汉字"""
    for i in range(len(text_list)):
        text_list[i] = clean_up_text(text_list[i])

    for i in range(len(text_list) - 1):
        # 转换为平假名后比较
        current_hiragana = convert_to_hiragana(text_list[i])
        next_hiragana = convert_to_hiragana(text_list[i + 1])
        
        # 将最后一个字符转换为平假名
        last_char = current_hiragana[-1]
        next_first_char = next_hiragana[0]
        
        if last_char != next_first_char:
            return 0, f"❌ 不匹配，句子：{str(text_list[i])}({current_hiragana})的最后一个字和句子：{str(text_list[i + 1])}({next_hiragana})的第一个字不一致"
    return 1, f"✅ 匹配，句子：{str(text_list)}"


def jpn_kana_type(text):
    """检测日文是否为单一假名类型（全平假名或全片假名）"""
    text = clean_up_text(text[0])
    
    has_hiragana = False
    has_katakana = False
    has_kanji = False
    
    for char in text:
        if '\u3040' <= char <= '\u309F':  # 平假名范围
            has_hiragana = True
        elif '\u30A0' <= char <= '\u30FF':  # 片假名范围
            has_katakana = True
        elif '\u4E00' <= char <= '\u9FAF':  # 汉字范围
            has_kanji = True
    
    if has_hiragana and not has_katakana and not has_kanji:
        return 1, "✅ 内容全是平假名"
    elif has_katakana and not has_hiragana and not has_kanji:
        return 1, "✅ 内容全是片假名"
    elif has_kanji and not has_hiragana and not has_katakana:
        return 1, "✅ 内容全是汉字"
    else:
        types = []
        if has_hiragana:
            types.append("平假名")
        if has_katakana:
            types.append("片假名")
        if has_kanji:
            types.append("汉字")
        return 0, f"❌ 内容包含混合文字类型：{', '.join(types)}"


if __name__ == "__main__":
    # 测试用例1: 基本押韵 - 相同元音结尾
    print("=== 测试用例1: 基本押韵 ===")
    test1 = ["さくら", "あした", "ゆめ", "そら"]  # 都以 'a' 元音结尾
    result1, msg1 = jpn_yayun(test1)
    print(f"测试1结果: {result1}, 消息: {msg1}")
    
    # 测试用例2: 不押韵 - 不同元音结尾
    print("\n=== 测试用例2: 不押韵 ===")
    test2 = ["はる", "なつ", "あき", "ふゆ"]  # 不同元音结尾
    result2, msg2 = jpn_yayun(test2)
    print(f"测试2结果: {result2}, 消息: {msg2}")
    
    # 测试用例3: 和歌押韵 - 偶数句押韵
    print("\n=== 测试用例3: 和歌偶数句押韵 ===")
    test3 = ["春が来て", "花が咲く", "鳥が鳴き", "風が吹く"]  # 偶数句押韵
    result3, msg3 = jpn_waka_yayun(test3)
    print(f"测试3结果: {result3}, 消息: {msg3}")
    
    # 测试用例4: 和歌不押韵 - 偶数句不押韵
    print("\n=== 测试用例4: 和歌偶数句不押韵 ===")
    test4 = ["空は青い", "海は深い", "山は高い", "川は長い"]  # 偶数句不押韵
    result4, msg4 = jpn_waka_yayun(test4)
    print(f"测试4结果: {result4}, 消息: {msg4}")
    
    # 测试用例5: 相同元音押韵（う段）
    print("\n=== 测试用例5: 相同元音押韵（う段）===")
    test5 = ["つき", "ゆき", "かぜ", "あめ"]  # 都以 'i' 元音结尾
    result5, msg5 = jpn_yayun(test5)
    print(f"测试5结果: {result5}, 消息: {msg5}")
    
    # 测试用例6: 诗吟接龙
    print("\n=== 测试用例6: 诗吟接龙 ===")
    test6 = ["さくら", "らくだ", "だいこん", "こんにちは"]  # 接龙
    result6, msg6 = jpn_shigin_jielong(test6)
    print(f"测试6结果: {result6}, 消息: {msg6}")
    
    # 测试用例7: 片假名押韵
    print("\n=== 测试用例7: 片假名押韵 ===")
    test7 = ["コーヒー", "ケーキ", "クッキー", "キャンディー"]  # 长音押韵
    result7, msg7 = jpn_yayun(test7)
    print(f"测试7结果: {result7}, 消息: {msg7}")
    
    # 测试用例8: 假名类型检测 - 平假名
    print("\n=== 测试用例8: 假名类型检测（平假名）===")
    test8 = ["ひらがなのぶんしょう"]  # 全平假名
    result8, msg8 = jpn_kana_type(test8)
    print(f"测试8结果: {result8}, 消息: {msg8}")
    
    # 测试用例9: 假名类型检测 - 片假名
    print("\n=== 测试用例9: 假名类型检测（片假名）===")
    test9 = ["カタカナノブンショウ"]  # 全片假名
    result9, msg9 = jpn_kana_type(test9)
    print(f"测试9结果: {result9}, 消息: {msg9}")
    
    # 测试用例10: 俳句示例
    print("\n=== 测试用例10: 俳句示例 ===")
    test10 = ["古池や", "蛙飛び込む", "水の音"]  # 著名俳句
    result10, msg10 = jpn_yayun(test10)
    print(f"测试10结果: {result10}, 消息: {msg10}")
    
    # 新增测试用例11: 汉字押韵测试
    print("\n=== 测试用例11: 汉字押韵测试 ===")
    test11 = ["学校", "友達", "先生", "教室"]  # 汉字结尾
    result11, msg11 = jpn_yayun(test11)
    print(f"测试11结果: {result11}, 消息: {msg11}")
    
    # 新增测试用例12: 混合文字押韵测试
    print("\n=== 测试用例12: 混合文字押韵测试 ===")
    test12 = ["桜", "さくら", "サクラ", "花見"]  # 混合文字
    result12, msg12 = jpn_yayun(test12)
    print(f"测试12结果: {result12}, 消息: {msg12}")
    
    # 新增测试用例13: 汉字接龙测试
    print("\n=== 测试用例13: 汉字接龙测试 ===")
    test13 = ["学校", "海", "雨", "雪"]  # 汉字接龙
    result13, msg13 = jpn_shigin_jielong(test13)
    print(f"测试13结果: {result13}, 消息: {msg13}")
    
    print("\n=== 日文押韵测试完成 ===")