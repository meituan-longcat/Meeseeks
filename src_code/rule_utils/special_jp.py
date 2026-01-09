import re

# 1
def jpn_mixed_ratio(texts, hiragana_ratio=None, katakana_ratio=None, kanji_ratio=None, tolerance=0.1):
    """检查平假名、片假名和汉字是否符合指定比例"""
    
    # cleaned_up_texts = [clean_up_text(text) for text in texts]
    error_messages = []
    
    # 对每个文本单独进行评测
    for i, text in enumerate(texts):
        if not text:
            continue
            
        hiragana_count = len(re.findall(r'[\u3040-\u309F]', text))
        katakana_count = len(re.findall(r'[\u30A0-\u30FF]', text))
        kanji_count = len(re.findall(r'[\u4E00-\u9FAF]', text))
        
        total_chars = hiragana_count + katakana_count + kanji_count
        
        if total_chars == 0:
            continue
            
        actual_hiragana_ratio = hiragana_count / total_chars
        actual_katakana_ratio = katakana_count / total_chars
        actual_kanji_ratio = kanji_count / total_chars
        
        # 检查指定的比例是否在容差范围内
        text_errors = []
        
        if hiragana_ratio is not None:
            if abs(actual_hiragana_ratio - hiragana_ratio) > tolerance:
                text_errors.append(f"平假名比例: 实际{actual_hiragana_ratio:.3f}({hiragana_count}字), 期望{hiragana_ratio:.3f}, 差值{abs(actual_hiragana_ratio - hiragana_ratio):.3f} > 容差{tolerance}")
        
        if katakana_ratio is not None:
            if abs(actual_katakana_ratio - katakana_ratio) > tolerance:
                text_errors.append(f"片假名比例: 实际{actual_katakana_ratio:.3f}({katakana_count}字), 期望{katakana_ratio:.3f}, 差值{abs(actual_katakana_ratio - katakana_ratio):.3f} > 容差{tolerance}")
        
        if kanji_ratio is not None:
            if abs(actual_kanji_ratio - kanji_ratio) > tolerance:
                text_errors.append(f"汉字比例: 实际{actual_kanji_ratio:.3f}({kanji_count}字), 期望{kanji_ratio:.3f}, 差值{abs(actual_kanji_ratio - kanji_ratio):.3f} > 容差{tolerance}")
        
        if text_errors:
            error_messages.append(f"文本{i+1}(总字数{total_chars}): {'; '.join(text_errors)}")
    
    is_valid = len(error_messages) == 0
    return (1 if is_valid else 0), ("; ".join(error_messages) if error_messages else "✅ 无问题")


def has_small_kana(texts, exact_count):
    """检查小假名数量是否满足要求
    - 如果是带序号的内容，分别检查每个序号中的内容
    - 如果是整篇文章或多个自然段，检查整篇文章
    """
    import re
    
    # 处理输入参数
    if isinstance(texts, str):
        texts = [texts]
    elif not isinstance(texts, list):
        texts = [str(texts)]
    
    def clean_up_text(text):
        """清理文本，移除不必要的符号"""
        if not text:
            return ""
        # 移除常见的格式符号
        cleaned = re.sub(r'[#\[\]【】()（）\n\r\t]', '', str(text))
        return cleaned.strip()
    
    def detect_content_type(text):
        """检测内容类型：序号内容 vs 整篇文章"""
        # 检查是否包含序号格式
        numbered_patterns = [
            r'^\s*\d+[.．)\)]\s*',  # 1. 或 1） 开头
            r'^\s*[①②③④⑤⑥⑦⑧⑨⑩]\s*',  # 圆圈数字
            r'^\s*[一二三四五六七八九十][.．)\)]\s*',  # 中文数字
            r'^\s*[ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ][.．)\)]\s*',  # 罗马数字
        ]
        
        lines = text.split('\n')
        numbered_lines = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            for pattern in numbered_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    numbered_lines += 1
                    break
        
        # 如果有2个或以上的序号行，认为是序号内容
        return numbered_lines >= 2
    
    def extract_numbered_items(text):
        """提取序号内容"""
        items = []
        lines = text.split('\n')
        current_item = ""
        
        numbered_patterns = [
            r'^\s*\d+[.．)\)]\s*',
            r'^\s*[①②③④⑤⑥⑦⑧⑨⑩]\s*',
            r'^\s*[一二三四五六七八九十][.．)\)]\s*',
            r'^\s*[ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ][.．)\)]\s*',
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是新的序号行
            is_numbered = False
            for pattern in numbered_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    # 保存前一个项目
                    if current_item.strip():
                        items.append(current_item.strip())
                    # 开始新项目，去掉序号部分
                    current_item = re.sub(pattern, '', line).strip()
                    is_numbered = True
                    break
            
            if not is_numbered and current_item:
                # 继续当前项目
                current_item += " " + line
        
        # 保存最后一个项目
        if current_item.strip():
            items.append(current_item.strip())
        
        return items
    
    # 小假名正则表达式
    small_kana_pattern = r'[ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮ]'
    
    # 合并所有文本进行类型检测
    combined_text = '\n'.join(texts)
    
    # 检测内容类型
    is_numbered_content = detect_content_type(combined_text)
    
    if is_numbered_content:
        # 序号内容：分别检查每个序号项
        all_items = []
        for text in texts:
            items = extract_numbered_items(text)
            all_items.extend(items)
        
        if not all_items:
            return 0, "❌ 未检测到有效的序号内容"
        
        failed_items = []
        success_items = []
        
        for i, item in enumerate(all_items, 1):
            cleaned_item = clean_up_text(item)
            matches = re.findall(small_kana_pattern, cleaned_item)
            count = len(matches)
            
            if count == exact_count:
                success_items.append(f"项目{i}: {count}个小假名 ✅")
            else:
                failed_items.append(f"项目{i}: 实际{count}个 (要求={exact_count}个), 找到: {matches}")
        
        if failed_items:
            return 0, f"❌ 部分序号项小假名数量不符合要求: {'; '.join(failed_items)}"
        else:
            return 1, f"✅ 所有序号项小假名数量都符合要求: {'; '.join(success_items)}"
    
    else:
        # 整篇文章：检查全文
        cleaned_texts = [clean_up_text(text) for text in texts]
        combined_text = ''.join(cleaned_texts)
        
        matches = re.findall(small_kana_pattern, combined_text)
        count = len(matches)
        
        if count == exact_count:
            return 1, f"✅ 整篇文章小假名数量符合要求: {count}个 (要求={exact_count}个), 找到: {matches}"
        else:
            return 0, f"❌ 整篇文章小假名数量不符合要求: 实际{count}个 (要求={exact_count}个), 找到: {matches}"



import re

try:
    from janome.tokenizer import Tokenizer
    JANOME_AVAILABLE = True
except ImportError:
    JANOME_AVAILABLE = False
    Tokenizer = None

# --- 辅助函数 (保持不变) ---
def clean_up_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return text.strip()

# --- 辅助函数：判断动词连用形是否被用作名词 ---
def is_used_as_noun(token_list, index):
    """
    检查一个动词连用形是否在当前上下文中被用作名词。
    
    Args:
        token_list (list): Janome分词后的完整列表。
        index (int): 当前token在列表中的索引。
        
    Returns:
        bool: 如果被用作名词，返回True，否则False。
    """
    # 如果是列表中的最后一个词，很难判断，保守起见认为是名词
    if index + 1 >= len(token_list):
        return True

    next_token = token_list[index + 1]
    
    # 后面跟着助词 (Particle) 或 系动词 (Copula)，很可能是名词
    # 助词: の, は, が, を, も, と, に, へ, で
    # 系动词: です, だ
    noun_indicators = {'の', 'は', 'が', 'を', 'も', 'と', 'に', 'へ', 'で', 'です', 'だ'}
    if next_token.surface in noun_indicators:
        return True
    
    # 后面跟着特定助词，也表明是名词
    # '助詞,格助詞', '助詞,係助詞', '助詞,副助詞', '助詞,終助詞'
    if next_token.part_of_speech.startswith('助詞'):
        return True

    # 后面跟着逗号、ます、ながら、或另一个动词，很可能仍然是动词
    verb_indicators = {',', '、', 'ます', 'ながら'}
    if next_token.surface in verb_indicators:
        return False
    if next_token.part_of_speech.startswith('動詞'): # e.g., 考え-始める
        return False
        
    # 其他情况，例如后面是名词（构成复合名词，如「逆さま走り」），则认为是名词
    # 如果无法确定，采用保守策略，默认不认为是名词化用法，除非有明确指标。
    # 这里我们默认返回False，只在有明确名词指标时返回True。
    return False


# --- 最终修正后的规则函数 ---
def has_kanji_okurigana_pattern(texts, min_count=None, max_count=None, exact_count=None):
    """
    检查文本中符合“汉字+平假名”模式的名词数量是否满足要求。
    (V3 精确修正版: 区分动词连用形的名词用法和动词用法)
    """
    # 1. 输入处理
    if isinstance(texts, str):
        texts = [texts]
    elif not isinstance(texts, list):
        texts = list(texts)
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    combined_text = ''.join(cleaned_up_texts)
    
    found_patterns = []
    if combined_text:
        # 2. 分词
        t = Tokenizer()
        # Janome返回的是生成器，需要转换为列表以进行索引访问
        tokens = list(t.tokenize(combined_text))
        
        okurigana_pattern = re.compile(r'^[\u4e00-\u9faf]+[\u3040-\u309f]+$')

        for i, token in enumerate(tokens):
            # 必须先满足表面模式
            if not okurigana_pattern.match(token.surface):
                continue

            # 条件A: 本身就是名词
            if token.part_of_speech.startswith('名詞'):
                # 额外检查，排除一些被错误识别为名词的助词，如「向け」
                if token.surface == '向け' and token.part_of_speech.startswith('名詞,接尾'):
                    continue # 这是助词用法，跳过
                found_patterns.append(token.surface)
                continue

            # 条件B: 是动词连用形，且在上下文中被用作名词
            is_verb_renyoukei = (token.part_of_speech.startswith('動詞') and 
                                 token.infl_form == '連用形')
            
            if is_verb_renyoukei and is_used_as_noun(tokens, i):
                found_patterns.append(token.surface)

    # 3. 统计和格式化输出 (逻辑不变)
    count = len(found_patterns)
    # ... (此部分代码与之前版本相同，故省略以保持简洁)
    # ...
    # 4. 判断结果 (逻辑不变)
    # ...
    
    # 为了演示，直接返回找到的列表
    # 在实际使用中，您应恢复完整的统计和返回逻辑
    
    # 构造要求描述字符串 (从旧代码复制)
    if exact_count is not None:
        min_count = max_count = exact_count
    req_parts = []
    if min_count is not None and max_count is not None and min_count == max_count:
        req_str = f"要求={min_count}个"
    else:
        if min_count is not None:
            req_parts.append(f"最少{min_count}个")
        if max_count is not None:
            req_parts.append(f"最多{max_count}个")
        if not req_parts:
            req_str = "无数量要求"
        else:
            req_str = f"要求: {' / '.join(req_parts)}"

    # 判断结果 (从旧代码复制)
    result = True
    if min_count is not None and count < min_count:
        result = False
    if max_count is not None and count > max_count:
        result = False
        
    if result:
        return 1, f"✅ 送假名名词数量符合要求: 实际{count}个 ({req_str}), 找到: {found_patterns}"
    else:
        return 0, f"❌ 送假名名词数量不符合要求: 实际{count}个 ({req_str}), 找到: {found_patterns}"








def has_furigana_pattern(texts, num):
    """检查每个文本是否都包含指定数量的振假名模式（汉字后紧跟小括号内的假名）"""
    # 合并所有文本为一个大字符串进行检测
    all_text = ""
    for text in texts:
        if isinstance(text, list):
            all_text += " ".join(str(item) for item in text) + " "
        else:
            all_text += str(text) + " "
    
    # 修正：同时支持全角和半角括号
    furigana_pattern = r'[\u4E00-\u9FAF]+[（(][\u3040-\u309F\u30A0-\u30FF]+[）)]'
    
    # 在合并后的文本中查找所有振假名模式
    all_matches = re.findall(furigana_pattern, all_text)
    
    # 修正：检查精确数量（不去重，因为可能需要总数量）
    if len(all_matches) != num:
        return 0, f"❌ 振假名模式数量不符合要求: 实际{len(all_matches)}个 (要求={num}个), 检测到: {all_matches}"
    
    return 1, f"✅ 振假名模式数量正确: {len(all_matches)}个, 检测到: {all_matches}"




def jpn_starts_with_kana_row(content_list, kana_row):
    """
    检测日语词汇是否以指定的五十音行开头
    """
    if not isinstance(content_list, list):
        return 0, "❌ content is not a list format"
    
    if not content_list:
        return 0, "❌ content list is empty"
    
    # 定义五十音行的对应关系
    kana_rows = {
    "あ行": ["あ", "い", "う", "え", "お"],
    "か行": ["か", "き", "く", "け", "こ", "が", "ぎ", "ぐ", "げ", "ご"],
    "さ行": ["さ", "し", "す", "せ", "そ", "ざ", "じ", "ず", "ぜ", "ぞ"],
    "た行": ["た", "ち", "つ", "て", "と", "だ", "ぢ", "づ", "で", "ど"],
    "だ行": ["だ", "ぢ", "づ", "で", "ど"],  
    "な行": ["な", "に", "ぬ", "ね", "の"],
    "は行": ["は", "ひ", "ふ", "へ", "ほ", "ば", "び", "ぶ", "べ", "ぼ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ"],
    "ば行": ["ば", "び", "ぶ", "べ", "ぼ"],  
    "ぱ行": ["ぱ", "ぴ", "ぷ", "ぺ", "ぽ"],  
    "ざ行": ["ざ", "じ", "ず", "ぜ", "ぞ"],  
    "ま行": ["ま", "み", "む", "め", "も"],
    "や行": ["や", "ゆ", "よ"],
    "ら行": ["ら", "り", "る", "れ", "ろ"],
    "わ行": ["わ", "ゐ", "ゑ", "を", "ん"]
}

    
    if kana_row not in kana_rows:
        return 0, f"❌ 未知的五十音行: {kana_row}"
    
    target_kanas = kana_rows[kana_row]
    non_matching_items = []
    matching_readings = []
    
    for i, item in enumerate(content_list):
        # 提取读音部分
        reading = extract_japanese_reading(item)
        
        if not reading:
            non_matching_items.append(f"item {i+1}: {item} (无法提取读音)")
            continue
        
        # 检查是否以目标五十音行开头
        first_char = reading[0] if reading else ""
        if first_char not in target_kanas:
            non_matching_items.append(f"item {i+1}: {item} -> {reading} (首字符'{first_char}'不属于{kana_row})")
        else:
            matching_readings.append(reading)
    
    if non_matching_items:
        return 0, f"❌ {len(non_matching_items)} items do not start with {kana_row}: {non_matching_items}"
    
    return 1, f"✅ All {len(content_list)} items start with {kana_row}: {matching_readings}"

def extract_japanese_reading(text):
    """
    从日语词汇中提取读音
    支持格式：
    1. 明るい（あかるい） -> あかるい
    2. あかるい -> あかるい
    3. 明るい -> 明るい (如果没有括号，返回原文)
    """
    # 匹配括号内的读音
    parentheses_match = re.search(r'（([^）]+)）', text)
    if parentheses_match:
        return parentheses_match.group(1)
    
    # 匹配英文括号内的读音
    parentheses_match = re.search(r'\(([^)]+)\)', text)
    if parentheses_match:
        return parentheses_match.group(1)
    
    # 如果没有括号，检查是否全是假名
    hiragana_katakana = re.findall(r'[\u3040-\u309F\u30A0-\u30FF]', text)
    if hiragana_katakana:
        return ''.join(hiragana_katakana)
    
    # 如果都没有，返回原文
    return text

def has_honorific_prefix_each(texts):
    """检查每个文本是否都包含敬语前缀「お/ご + 漢字」"""
    
    if not isinstance(texts, list):
        return 0, "❌ content is not a list format"
    
    if not texts:
        return 0, "❌ content list is empty"
    
    # 匹配「お + 漢字」和「ご + 漢字」模式
    honorific_pattern = r'[おご][\u4E00-\u9FAF]+'
    
    missing_items = []
    found_prefixes = []
    
    for i, text in enumerate(texts):
        if not text:
            missing_items.append(f"item {i+1}: (empty)")
            continue
            
        matches = re.findall(honorific_pattern, str(text))
        
        if not matches:
            missing_items.append(f"item {i+1}: {text[:50]}..." if len(str(text)) > 50 else f"item {i+1}: {text}")
        else:
            # 去重并记录找到的敬语前缀
            unique_matches = list(set(matches))
            found_prefixes.extend(unique_matches)
    
    if missing_items:
        return 0, f"❌ {len(missing_items)} items do not contain honorific prefixes: {missing_items}"
    
    # 去重所有找到的敬语前缀
    all_unique_prefixes = list(set(found_prefixes))
    return 1, f"✅ All {len(texts)} items contain honorific prefixes. Found: {all_unique_prefixes}"

def has_dakuten_count(texts, num):
    """检查文本中浊音字符的总数量是否满足要求"""
    
    def count_dakuten_characters(text):
        """统计文本中的浊音字符数量"""
        import re
        
        # 浊音字符：带゛符号的平假名和片假名
        dakuten_chars = [
            # 平假名浊音
            'が', 'ぎ', 'ぐ', 'げ', 'ご',  # が行
            'ざ', 'じ', 'ず', 'ぜ', 'ぞ',  # ざ行  
            'だ', 'ぢ', 'づ', 'で', 'ど',  # だ行
            'ば', 'び', 'ぶ', 'べ', 'ぼ',  # ば行
            # 片假名浊音
            'ガ', 'ギ', 'グ', 'ゲ', 'ゴ',  # ガ行
            'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ',  # ザ行
            'ダ', 'ヂ', 'ヅ', 'デ', 'ド',  # ダ行
            'バ', 'ビ', 'ブ', 'ベ', 'ボ',  # バ行
            'ヴ'  # 特殊浊音
        ]
        
        # 统计每个浊音字符的出现次数
        total_count = 0
        found_chars = []
        
        for char in dakuten_chars:
            count = text.count(char)
            if count > 0:
                total_count += count
                found_chars.extend([char] * count)
        
        return total_count, found_chars
    
    # 统计所有文本的浊音总数
    total_dakuten_count = 0
    all_found_chars = []
    
    for i, text in enumerate(texts):
        if not text:
            continue
        
        count, found_chars = count_dakuten_characters(text)
        total_dakuten_count += count
        all_found_chars.extend(found_chars)
    
    # 检查是否满足要求
    if total_dakuten_count != num:
        return 0, f"❌ 浊音字符总数不符合要求: 实际{total_dakuten_count}个 (要求={num}个), 检测到: {all_found_chars}"
    
    return 1, f"✅ 浊音字符总数正确: {total_dakuten_count}个, 检测到: {all_found_chars}"


def has_dakuten_count_range(texts, min_num, max_num):
    """检查文本中浊音字符的数量是否在指定范围内"""
    
    def count_dakuten_characters(text):
        """统计文本中的浊音字符数量"""
        dakuten_pattern = r'[が-ぢづ-どば-ぼガ-ヂヅ-ドバ-ボヴ]'
        import re
        matches = re.findall(dakuten_pattern, text)
        return len(matches), matches
    
    # 统计所有文本的浊音总数
    total_count = 0
    all_matches = []
    
    for text in texts:
        if text:
            count, matches = count_dakuten_characters(text)
            total_count += count
            all_matches.extend(matches)
    
    # 检查是否在范围内
    if not (min_num <= total_count <= max_num):
        return 0, f"❌ 浊音字符数量不在范围内: 实际{total_count}个 (要求{min_num}-{max_num}个), 检测到: {all_matches}"
    
    return 1, f"✅ 浊音字符数量在范围内: {total_count}个, 检测到: {all_matches}"


def has_dakuten_by_type(texts, dakuten_type, num):
    """检查特定类型浊音的数量"""
    
    dakuten_patterns = {
        'が行': r'[がぎぐげごガギグゲゴ]',
        'ざ行': r'[ざじずぜぞザジズゼゾ]', 
        'だ行': r'[だぢづでどダヂヅデド]',
        'ば行': r'[ばびぶべぼバビブベボ]',
        '平假名': r'[が-ぢづ-どば-ぼ]',
        '片假名': r'[ガ-ヂヅ-ドバ-ボヴ]',
        '全部': r'[が-ぢづ-どば-ぼガ-ヂヅ-ドバ-ボヴ]'
    }
    
    if dakuten_type not in dakuten_patterns:
        return 0, f"❌ 不支持的浊音类型: {dakuten_type}，支持的类型: {list(dakuten_patterns.keys())}"
    
    import re
    pattern = dakuten_patterns[dakuten_type]
    
    # 统计指定类型的浊音
    total_count = 0
    all_matches = []
    
    for text in texts:
        if text:
            matches = re.findall(pattern, text)
            total_count += len(matches)
            all_matches.extend(matches)
    
    if total_count != num:
        return 0, f"❌ {dakuten_type}浊音数量不符合要求: 实际{total_count}个 (要求={num}个), 检测到: {all_matches}"
    
    return 1, f"✅ {dakuten_type}浊音数量正确: {total_count}个, 检测到: {all_matches}"


def analyze_dakuten_distribution(texts):
    """分析浊音字符的分布情况（用于调试）"""
    
    import re
    
    distribution = {
        'が行': {'pattern': r'[がぎぐげごガギグゲゴ]', 'count': 0, 'chars': []},
        'ざ行': {'pattern': r'[ざじずぜぞザジズゼゾ]', 'count': 0, 'chars': []},
        'だ行': {'pattern': r'[だぢづでどダヂヅデド]', 'count': 0, 'chars': []},
        'ば行': {'pattern': r'[ばびぶべぼバビブベボ]', 'count': 0, 'chars': []},
    }
    
    for text in texts:
        if not text:
            continue
            
        for gyou, info in distribution.items():
            matches = re.findall(info['pattern'], text)
            info['count'] += len(matches)
            info['chars'].extend(matches)
    
    # 计算总数
    total = sum(info['count'] for info in distribution.values())
    
    result = {
        '总计': total,
        '分布': {gyou: {'数量': info['count'], '字符': info['chars']} 
                for gyou, info in distribution.items()}
    }
    
    return result


def has_handakuten_count(texts, num):
    """检查文本中半浊音字符的总数量是否满足要求"""
    
    def count_handakuten_characters(text):
        """统计文本中的半浊音字符数量"""
        import re
        
        # 半浊音字符：带゜符号的平假名和片假名（只有ぱ行/パ行）
        handakuten_chars = [
            # 平假名半浊音
            'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ',  # ぱ行
            # 片假名半浊音
            'パ', 'ピ', 'プ', 'ペ', 'ポ'   # パ行
        ]
        
        # 统计每个半浊音字符的出现次数
        total_count = 0
        found_chars = []
        
        for char in handakuten_chars:
            count = text.count(char)
            if count > 0:
                total_count += count
                found_chars.extend([char] * count)
        
        return total_count, found_chars
    
    # 统计所有文本的半浊音总数
    total_handakuten_count = 0
    all_found_chars = []
    
    for i, text in enumerate(texts):
        if not text:
            continue
        
        count, found_chars = count_handakuten_characters(text)
        total_handakuten_count += count
        all_found_chars.extend(found_chars)
    
    # 检查是否满足要求
    if total_handakuten_count != num:
        return 0, f"❌ 半浊音字符总数不符合要求: 实际{total_handakuten_count}个 (要求={num}个), 检测到: {all_found_chars}"
    
    return 1, f"✅ 半浊音字符总数正确: {total_handakuten_count}个, 检测到: {all_found_chars}"


def has_handakuten_count_range(texts, min_num, max_num):
    """检查文本中半浊音字符的数量是否在指定范围内"""
    
    def count_handakuten_characters(text):
        """统计文本中的半浊音字符数量"""
        handakuten_pattern = r'[ぱ-ぽパ-ポ]'
        import re
        matches = re.findall(handakuten_pattern, text)
        return len(matches), matches
    
    # 统计所有文本的半浊音总数
    total_count = 0
    all_matches = []
    
    for text in texts:
        if text:
            count, matches = count_handakuten_characters(text)
            total_count += count
            all_matches.extend(matches)
    
    # 检查是否在范围内
    if not (min_num <= total_count <= max_num):
        return 0, f"❌ 半浊音字符数量不在范围内: 实际{total_count}个 (要求{min_num}-{max_num}个), 检测到: {all_matches}"
    
    return 1, f"✅ 半浊音字符数量在范围内: {total_count}个, 检测到: {all_matches}"


def has_handakuten_by_type(texts, handakuten_type, num):
    """检查特定类型半浊音的数量"""
    
    handakuten_patterns = {
        'ぱ': r'[ぱパ]',
        'ぴ': r'[ぴピ]', 
        'ぷ': r'[ぷプ]',
        'ぺ': r'[ぺペ]',
        'ぽ': r'[ぽポ]',
        'ぱ行': r'[ぱ-ぽパ-ポ]',
        '平假名': r'[ぱ-ぽ]',
        '片假名': r'[パ-ポ]',
        '全部': r'[ぱ-ぽパ-ポ]'
    }
    
    if handakuten_type not in handakuten_patterns:
        return 0, f"❌ 不支持的半浊音类型: {handakuten_type}，支持的类型: {list(handakuten_patterns.keys())}"
    
    import re
    pattern = handakuten_patterns[handakuten_type]
    
    # 统计指定类型的半浊音
    total_count = 0
    all_matches = []
    
    for text in texts:
        if text:
            matches = re.findall(pattern, text)
            total_count += len(matches)
            all_matches.extend(matches)
    
    if total_count != num:
        return 0, f"❌ {handakuten_type}半浊音数量不符合要求: 实际{total_count}个 (要求={num}个), 检测到: {all_matches}"
    
    return 1, f"✅ {handakuten_type}半浊音数量正确: {total_count}个, 检测到: {all_matches}"


def has_handakuten_minimum(texts, min_num):
    """检查文本中半浊音字符数量是否达到最小要求"""
    
    import re
    handakuten_pattern = r'[ぱ-ぽパ-ポ]'
    
    total_count = 0
    all_matches = []
    
    for text in texts:
        if text:
            matches = re.findall(handakuten_pattern, text)
            total_count += len(matches)
            all_matches.extend(matches)
    
    if total_count < min_num:
        return 0, f"❌ 半浊音字符数量不足: 实际{total_count}个 (最少需要{min_num}个), 检测到: {all_matches}"
    
    return 1, f"✅ 半浊音字符数量满足最小要求: {total_count}个 (≥{min_num}个), 检测到: {all_matches}"


def analyze_handakuten_distribution(texts):
    """分析半浊音字符的分布情况（用于调试）"""
    
    import re
    
    distribution = {
        'ぱ': {'pattern': r'[ぱパ]', 'count': 0, 'chars': []},
        'ぴ': {'pattern': r'[ぴピ]', 'count': 0, 'chars': []},
        'ぷ': {'pattern': r'[ぷプ]', 'count': 0, 'chars': []},
        'ぺ': {'pattern': r'[ぺペ]', 'count': 0, 'chars': []},
        'ぽ': {'pattern': r'[ぽポ]', 'count': 0, 'chars': []},
    }
    
    for text in texts:
        if not text:
            continue
            
        for sound, info in distribution.items():
            matches = re.findall(info['pattern'], text)
            info['count'] += len(matches)
            info['chars'].extend(matches)
    
    # 计算总数和分类统计
    total = sum(info['count'] for info in distribution.values())
    hiragana_total = sum(len([c for c in info['chars'] if 'ぁ' <= c <= 'ん']) 
                        for info in distribution.values())
    katakana_total = sum(len([c for c in info['chars'] if 'ァ' <= c <= 'ン']) 
                        for info in distribution.values())
    
    result = {
        '总计': total,
        '平假名半浊音': hiragana_total,
        '片假名半浊音': katakana_total,
        '分布': {sound: {'数量': info['count'], '字符': info['chars']} 
                for sound, info in distribution.items()}
    }
    
    return result


def extract_words_with_handakuten(texts, min_length=2):
    """提取包含半浊音的词汇"""
    
    import re
    
    handakuten_words = []
    
    for text in texts:
        if not text:
            continue
        
        # 查找包含半浊音的假名序列
        hiragana_sequences = re.findall(r'[あ-ん]+', text)
        katakana_sequences = re.findall(r'[ア-ン]+', text)
        
        # 查找包含半浊音的汉字+假名组合
        kanji_kana_sequences = re.findall(r'[\u4E00-\u9FAF]+[あ-ん]+', text)
        
        all_sequences = hiragana_sequences + katakana_sequences + kanji_kana_sequences
        
        for seq in all_sequences:
            # 检查是否包含半浊音字符且长度符合要求
            if (len(seq) >= min_length and 
                re.search(r'[ぱ-ぽパ-ポ]', seq)):
                handakuten_words.append(seq)
    
    # 去重并返回
    return list(set(handakuten_words))


# if __name__ == "__main__":
    # print("=" * 80)
    # print("测试用例：歌词感想文评测")
    # print("=" * 80)
    
    # # 测试数据
    # model_response = "もういちどあなたをみさせてということばからは、なつかしさとせつなさがつたわってくる。みなみからきたまで、まちのひろがりをかんじさせるようなひょうげんが、きおくのなかのふうけいを【美しい】とおもわせる。はこをかかえたしょうじょや、あせをぬぐうおとこのすがたは、せいしゅんのひとこまを【美しい】とおもいださせる。あのなつはもどらないとしりつつ、かわりのゆめをむりやりでもえらばなければならないというきもちが、じんせいのふこうさや、きぼうのはかなさをかんじさせる。ふいたゆめも、せいしゅんとともにわらいとばすしかないということばには、じぶんをなぐさめるようなやさしさがある。このまちにとじこめられて、あなたをおもいだすというさいごのくだりは、きおくのなかの【美しい】じかんをたいせつにしているようにおもえた。"
    
    # extraction_results = {
    #     "感悟": [model_response]
    # }
    
    # print("\n【测试1】字符数检查 (270-330字)")
    # print("-" * 80)
    # text_length = len(model_response)
    # print(f"实际字符数: {text_length}")
    # if 270 <= text_length <= 330:
    #     print("✅ 字符数在范围内")
    # else:
    #     print(f"❌ 字符数不在范围内 (要求: 270-330)")
    
    # print("\n【测试2】平假名、片假名、汉字比例检查 (1:0:0)")
    # print("-" * 80)
    # result, message = jpn_mixed_ratio(
    #     extraction_results["感悟"],
    #     hiragana_ratio=1.0,
    #     katakana_ratio=0.0,
    #     kanji_ratio=0.0,
    #     tolerance=0.1
    # )
    # print(f"评测结果: {'✅ 通过' if result == 1 else '❌ 失败'}")
    # print(f"详细信息: {message}")
    
    # print("\n【测试3】关键词频率检查 (\"美しい\" 出现3次)")
    # print("-" * 80)
    # keyword = "美しい"
    # # 使用【】包裹的关键词
    # keyword_with_brackets = f"【{keyword}】"
    # count = model_response.count(keyword_with_brackets)
    # print(f"关键词 \"{keyword_with_brackets}\" 出现次数: {count}")
    # if count == 3:
    #     print("✅ 关键词出现次数正确")
    # else:
    #     print(f"❌ 关键词出现次数不正确 (要求: 3次, 实际: {count}次)")
    
    # print("\n【测试4】详细字符统计")
    # print("-" * 80)
    # hiragana_count = len(re.findall(r'[\u3040-\u309F]', model_response))
    # katakana_count = len(re.findall(r'[\u30A0-\u30FF]', model_response))
    # kanji_count = len(re.findall(r'[\u4E00-\u9FAF]', model_response))
    # other_count = text_length - hiragana_count - katakana_count - kanji_count
    
    # print(f"平假名: {hiragana_count} 字")
    # print(f"片假名: {katakana_count} 字")
    # print(f"汉字: {kanji_count} 字")
    # print(f"其他字符: {other_count} 字")
    # print(f"总字符数: {text_length} 字")
    
    # if hiragana_count + katakana_count + kanji_count > 0:
    #     total_chars = hiragana_count + katakana_count + kanji_count
    #     hiragana_ratio = hiragana_count / total_chars
    #     katakana_ratio = katakana_count / total_chars
    #     kanji_ratio = kanji_count / total_chars
        
    #     print(f"\n实际比例:")
    #     print(f"  平假名: {hiragana_ratio:.3f} ({hiragana_ratio*100:.1f}%)")
    #     print(f"  片假名: {katakana_ratio:.3f} ({katakana_ratio*100:.1f}%)")
    #     print(f"  汉字: {kanji_ratio:.3f} ({kanji_ratio*100:.1f}%)")
    
    # print("\n" + "=" * 80)
    # print("测试完成")
    # print("=" * 80)