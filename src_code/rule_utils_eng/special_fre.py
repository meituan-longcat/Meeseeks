import re, ast, json, os, sys
from collections import Counter, defaultdict
from math import gcd


# import verbecc
# print(dir(verbecc))  # 查看模块内容



try:
    import verbecc
    verbecc_AVAILABLE = True
except ImportError:
    verbecc_AVAILABLE = False
    print("verbecc库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "verbecc"])
        print("verbecc库安装成功，正在导入...")
        import verbecc
        verbecc_AVAILABLE = True
        print("✅ verbecc库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install verbecc")
        verbecc_AVAILABLE = False


# 确保 verbecc 已成功导入后再执行后续代码
if verbecc_AVAILABLE:
    try:
        from verbecc import Conjugator
        print("✅ 所需Conjugator模块导入成功")
    except ImportError as e:
        print(f"❌ 导入Conjugator模块失败: {e}")
else:
    print("❌ verbecc 库未成功导入，无法继续执行后续代码")



try:
    import haspirater
    haspirater_AVAILABLE = True
except ImportError:
    haspirater_AVAILABLE = False
    print("haspirater库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "haspirater", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("haspirater库安装成功，正在导入...")
        import haspirater
        haspirater_AVAILABLE = True
        print("✅ haspirater库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install haspirater")
        haspirater_AVAILABLE = False



try:
    import frhyme
    frhyme_AVAILABLE = True
except ImportError:
    frhyme_AVAILABLE = False
    print("frhyme库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "frhyme", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("frhyme库安装成功，正在导入...")
        import frhyme
        frhyme_AVAILABLE = True
        print("✅ frhyme库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install frhyme")
        frhyme_AVAILABLE = False





from pathlib import Path
from typing import List, Dict, Set, Tuple

class VerbccIndex:
    """Verbcc 动词索引加载器"""
    
    def __init__(self, index_path='verb_index_optimized.json'):
        self.index_file = Path(index_path)
        self.reverse_index = self._load_index()
    
    def _load_index(self) -> Dict[str, List[str]]:
        """加载 Verbcc 索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  无法加载 Verbcc 索引: {e}")
                return {}
        else:
            print(f"⚠️  Verbcc 索引文件不存在: {self.index_file}")
            return {}
    
    def is_verb(self, word: str) -> bool:
        """判断是否是动词变位形式"""
        return word.lower() in self.reverse_index
    
    def get_infinitives(self, word: str) -> List[str]:
        """获取动词的原形列表"""
        return self.reverse_index.get(word.lower(), [])
    
########## 嘘音:哑音 ##########
def check_french_h_ratio(corresponding_parts, rule_params, mode="total"):
    
    def extract_french_words(text):
        """提取法语单词（包含法语特殊字符）"""
        pattern = r'\b[a-zA-ZàâäæçéèêëïîôùûüÿœÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ]+\b'
        words = re.findall(pattern, text)
        return [word.lower() for word in words]
    
    def get_haspirater_lookup():
        """
        获取 haspirater 的 lookup 函数
        """
        try:
            from haspirater import lookup
            return lookup
        except ImportError:
            error_msg = (
                "❌ 错误：未安装 haspirater 库\n"
                "   安装方法：pip install haspirater\n"
                "   项目地址：https://pypi.org/project/haspirater/"
            )
            raise ImportError(error_msg)
    
    CUSTOM_H_ASPIRE = {
        'hector', 'hé'      # 可以继续添加其他不在词库中的嘘音h词汇
    }
    
    def classify_h_words(words, lookup_func, debug_mode=False):
        """
        分类h开头的词汇
        
        haspirater.lookup() 返回值：
        - [True]: h aspiré (嘘音h)
        - [False]: h muet (哑音h)
        - []: 不在词典中
        
        返回:
        - h_muet_words: 哑音h词汇列表
        - h_aspire_words: 嘘音h词汇列表
        """
        h_muet_words = []
        h_aspire_words = []
        
        for word in words:
            word_lower = word.lower()
            
            # 只处理以h开头的词
            if not word_lower.startswith('h'):
                continue
            
            # ⭐ 排除单独的字母 "h"
            if len(word_lower) == 1:
                if debug_mode:
                    print(f"  ⊗ 跳过单个字母: '{word_lower}'")
                continue
            
            # ⭐ 优先检查自定义词汇表
            if word_lower in CUSTOM_H_ASPIRE:
                h_aspire_words.append({
                    'word': word,
                    'type': 'h aspiré',
                })
                if debug_mode:
                    print(f"  ✓ {word} → h aspiré (嘘音h) [自定义词汇表]")
                continue
            
            # 使用 haspirater.lookup() 判断
            try:
                result = lookup_func(word_lower)
                
                if debug_mode:
                    print(f"  lookup('{word_lower}') = {result}")
                
                # 处理返回值（列表格式）
                if isinstance(result, list) and len(result) > 0:
                    # 取列表第一个元素
                    is_h_aspire = result[0]
                    
                    if debug_mode:
                        h_type = "h aspiré (嘘音h)" if is_h_aspire else "h muet (哑音h)"
                        print(f"  → {h_type}")
                else:
                    # 空列表表示不在词典中，默认为哑音h
                    if debug_mode:
                        print(f"  ⚠️  {word} 不在词典中，默认为哑音h")
                    is_h_aspire = False
                
            except Exception as e:
                if debug_mode:
                    print(f"  ⚠️  {word} → 判断失败: {e}")
                # 判断失败时默认为哑音h
                is_h_aspire = False
            
            if is_h_aspire:
                h_aspire_words.append({
                    'word': word,
                    'type': 'h aspiré',
                })
                if debug_mode:
                    print(f"  ✓ {word} → h aspiré (嘘音h)")
            else:
                h_muet_words.append({
                    'word': word,
                    'type': 'h muet',
                })
                if debug_mode:
                    print(f"  ✓ {word} → h muet (哑音h)")
        
        return h_muet_words, h_aspire_words
    
    def format_word_list(words):
        """格式化词汇列表（显示重复次数）"""
        word_list = [w['word'] for w in words]
        word_counts = Counter(word_list)
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        formatted_lines = []
        for word, count in sorted_words:
            if count > 1:
                formatted_lines.append(f"  {word} ({count}次)")
            else:
                formatted_lines.append(f"  {word}")
        
        return "\n".join(formatted_lines) if formatted_lines else "  (无)"
    
    # ==================== 主逻辑 ====================
    try:
        params = ast.literal_eval(rule_params)
        
        if isinstance(params, list) and len(params) >= 2:
            # 注意顺序：第一个是嘘音h，第二个是哑音h
            h_aspire_ratio = params[0]  # ← 嘘音h比例（第一个参数）
            h_muet_ratio = params[1]    # ← 哑音h比例（第二个参数）
            debug_mode = params[2] if len(params) > 2 else False
        else:
            return 0, f"❌ 参数格式错误: 需要 [h_aspire_ratio, h_muet_ratio] 或更多参数"
    
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    # 获取 haspirater lookup 函数
    try:
        lookup_func = get_haspirater_lookup()
    except Exception as e:
        return 0, str(e)
    
    # 处理每一项文本
    results = []
    
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        
        if debug_mode:
            print(f"\n{'='*80}")
            print(f"处理第 {i+1} 项: {text[:50]}...")
            print(f"{'='*80}")
        
        # 提取所有法语单词
        all_words = extract_french_words(text)
        
        if debug_mode:
            h_words = [w for w in all_words if w.lower().startswith('h')]
            print(f"找到 {len(h_words)} 个h开头的词: {h_words}")
        
        # 分类h词汇
        h_muet_words, h_aspire_words = classify_h_words(all_words, lookup_func, debug_mode)
        
        result = {
            'index': i,
            'h_muet_words': h_muet_words,
            'h_aspire_words': h_aspire_words,
            'h_muet_count': len(h_muet_words),
            'h_aspire_count': len(h_aspire_words),
        }
        results.append(result)
    
    # ==================== 根据模式返回结果 ====================
    
    if mode == "total":
        total_h_muet = 0
        total_h_aspire = 0
        all_h_muet_words = []
        all_h_aspire_words = []
        
        for r in results:
            all_h_muet_words.extend(r['h_muet_words'])
            all_h_aspire_words.extend(r['h_aspire_words'])
            total_h_muet += r['h_muet_count']
            total_h_aspire += r['h_aspire_count']
        
        if total_h_muet == 0 and total_h_aspire == 0:
            return 0, "❌ 未找到任何h开头的词汇（不含单个字母h）"
        
        # 计算实际比例（化简）
        if total_h_aspire > 0 and total_h_muet > 0:
            common_divisor = gcd(total_h_aspire, total_h_muet)
            actual_h_aspire_ratio = total_h_aspire // common_divisor
            actual_h_muet_ratio = total_h_muet // common_divisor
        else:
            actual_h_aspire_ratio = total_h_aspire
            actual_h_muet_ratio = total_h_muet
        
        # 判断是否匹配（注意：嘘音在前，哑音在后）
        ratio_match = (actual_h_aspire_ratio == h_aspire_ratio and 
                      actual_h_muet_ratio == h_muet_ratio)
        
        # 格式化输出
        h_aspire_formatted = format_word_list(all_h_aspire_words)
        h_muet_formatted = format_word_list(all_h_muet_words)
        
        h_aspire_text = f"嘘音h（h aspiré）: {total_h_aspire}个\n{h_aspire_formatted}"
        h_muet_text = f"哑音h（h muet）: {total_h_muet}个\n{h_muet_formatted}"
        
        status = "✅" if ratio_match else "❌"
        ratio_status = (
            f"实际比例 {actual_h_aspire_ratio}:{actual_h_muet_ratio} (嘘音:哑音)" +
            ("✅" if ratio_match else f" ❌ 不符合要求比例 {h_aspire_ratio}:{h_muet_ratio}")
        )
        
        text = (
            f"{status} 法语h词汇比例检查结果（不含单个字母h）:\n"
            f"{h_aspire_text}\n\n"
            f"{h_muet_text}\n\n"
            f"{ratio_status}"
        )
        
        return (1 if ratio_match else 0), text
    
    else:
        failed = []
        details = []
        
        for r in results:
            h_muet_count = r['h_muet_count']
            h_aspire_count = r['h_aspire_count']
            
            if h_muet_count == 0 and h_aspire_count == 0:
                failed.append(r)
                details.append(f"第{r['index']+1}项: 未找到h开头的词汇（不含单个字母h）")
                continue
            
            # 计算实际比例（嘘音:哑音）
            if h_aspire_count > 0 and h_muet_count > 0:
                common_divisor = gcd(h_aspire_count, h_muet_count)
                actual_h_aspire_ratio = h_aspire_count // common_divisor
                actual_h_muet_ratio = h_muet_count // common_divisor
            else:
                actual_h_aspire_ratio = h_aspire_count
                actual_h_muet_ratio = h_muet_count
            
            # 判断是否匹配
            ratio_match = (actual_h_aspire_ratio == h_aspire_ratio and 
                          actual_h_muet_ratio == h_muet_ratio)
            
            if not ratio_match:
                failed.append(r)
            
            h_aspire_formatted = format_word_list(r['h_aspire_words'])
            h_muet_formatted = format_word_list(r['h_muet_words'])
            
            item_detail = (
                f"第{r['index']+1}项: 实际比例 {actual_h_aspire_ratio}:{actual_h_muet_ratio} (嘘音:哑音) "
                f"{'✅' if ratio_match else f'❌ 不符合 {h_aspire_ratio}:{h_muet_ratio}'}\n"
                f"嘘音h({h_aspire_count}个):\n{h_aspire_formatted}\n"
                f"哑音h({h_muet_count}个):\n{h_muet_formatted}"
            )
            
            details.append(item_detail)
        
        passed = len(failed) == 0
        
        status = (
            "✅ 所有项h词汇比例都正确" if passed 
            else f"❌ 有{len(failed)}项h词汇比例不符合要求 {h_aspire_ratio}:{h_muet_ratio} (嘘音:哑音)"
        )
        
        return (1 if passed else 0), status + "\n\n" + "\n\n".join(details)


def french_h_ratio_total(corresponding_parts, rule_params):
    """检查所有文本的总体h词汇比例（嘘音:哑音）"""
    return check_french_h_ratio(corresponding_parts, rule_params, mode="total")


def french_h_ratio_each(corresponding_parts, rule_params):
    """检查每一项文本的h词汇比例（嘘音:哑音）"""
    return check_french_h_ratio(corresponding_parts, rule_params, mode="each")


########## H词首 ##########
def french_h_word_count(corresponding_parts, rule_params):
    
    try:
        params = ast.literal_eval(rule_params)
        expected_count = int(params[0])
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    # 提取所有文本
    all_text = " ".join([str(item or "") for item in corresponding_parts])
    
    # 提取法语单词
    pattern = r'\b[a-zA-ZàâäæçéèêëïîôùûüÿœÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ]+\b'
    words = re.findall(pattern, all_text)
    
    # 统计以h开头的单词（排除单独的字母h）
    h_words = []
    for w in words:
        w_lower = w.lower()
        # 必须以h开头，且长度大于1（排除单独的'h'或'H'）
        if w_lower.startswith('h') and len(w_lower) > 1:
            h_words.append(w)
    
    actual_count = len(h_words)
    
    # 判断是否匹配
    match = actual_count == expected_count
    
    status = "✅" if match else "❌"
    result_text = (
        f"{status} h词数检测:\n"
        f"期望数量: {expected_count} 个\n"
        f"实际数量: {actual_count} 个\n"
        f"h词列表: {', '.join(h_words) if h_words else '(无)'}\n"
        f"注意: 单独的字母'h'不计入统计"
    )
    
    return (1 if match else 0), result_text


########## 闭音符和重音符单词总和 ##########
def check_french_accent_count(corresponding_parts, rule_params, mode="total"):
    
    def extract_french_words(text):
        """提取法语单词（包含法语特殊字符）"""
        pattern = r'\b[a-zA-ZàâäæçéèêëïîôùûüÿœÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ]+\b'
        words = re.findall(pattern, text)
        return words
    
    def has_accent_aigu(word):
        """检查单词是否包含闭音符 é"""
        return 'é' in word.lower() or 'É' in word
    
    def has_accent_grave(word):
        """检查单词是否包含重音符 à, è, ù"""
        word_lower = word.lower()
        return 'à' in word_lower or 'è' in word_lower or 'ù' in word_lower
    
    def classify_accent_words(words):
        accent_aigu_words = []
        accent_grave_words = []
        both_accents_words = []
        
        for word in words:
            has_aigu = has_accent_aigu(word)
            has_grave = has_accent_grave(word)
            
            if has_aigu and has_grave:
                both_accents_words.append(word)
            elif has_aigu:
                accent_aigu_words.append(word)
            elif has_grave:
                accent_grave_words.append(word)
        
        return accent_aigu_words, accent_grave_words, both_accents_words
    
    def format_word_list(words):
        """格式化词汇列表（显示重复次数，显示所有单词）"""
        word_counts = Counter(words)
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        formatted_lines = []
        for word, count in sorted_words:
            if count > 1:
                formatted_lines.append(f"  {word} ({count}次)")
            else:
                formatted_lines.append(f"  {word}")
        
        return "\n".join(formatted_lines) if formatted_lines else "  (无)"
    
    try:
        params = ast.literal_eval(rule_params)
        
        if isinstance(params, list) and len(params) >= 1:
            expected_count = params[0]
        elif isinstance(params, int):
            expected_count = params
        else:
            return 0, f"❌ 参数格式错误: 需要 [expected_count] 或 expected_count"
    
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    results = []
    
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        all_words = extract_french_words(text)
        
        accent_aigu_words, accent_grave_words, both_accents_words = classify_accent_words(all_words)
        
        result = {
            'index': i,
            'accent_aigu_words': accent_aigu_words,
            'accent_grave_words': accent_grave_words,
            'both_accents_words': both_accents_words,
            'accent_aigu_count': len(accent_aigu_words),
            'accent_grave_count': len(accent_grave_words),
            'both_accents_count': len(both_accents_words),
            'total_count': len(accent_aigu_words) + len(accent_grave_words) + len(both_accents_words)
        }
        results.append(result)
    
    if mode == "total":
        all_accent_aigu_words = []
        all_accent_grave_words = []
        all_both_accents_words = []
        
        for r in results:
            all_accent_aigu_words.extend(r['accent_aigu_words'])
            all_accent_grave_words.extend(r['accent_grave_words'])
            all_both_accents_words.extend(r['both_accents_words'])
        
        total_accent_aigu = len(all_accent_aigu_words)
        total_accent_grave = len(all_accent_grave_words)
        total_both_accents = len(all_both_accents_words)
        total_count = total_accent_aigu + total_accent_grave + total_both_accents
        
        if total_count == 0:
            return 0, "❌ 未找到任何包含闭音符或重音符的单词"
        
        count_match = (total_count == expected_count)
        
        accent_aigu_formatted = format_word_list(all_accent_aigu_words)
        accent_grave_formatted = format_word_list(all_accent_grave_words)
        
        status = "✅" if count_match else "❌"
        
        text_parts = [
            f"{status} 闭音符和重音符单词数量检查结果:\n",
            f"闭音符单词 (é): {total_accent_aigu}个\n{accent_aigu_formatted}\n",
            f"重音符单词 (à/è/ù): {total_accent_grave}个\n{accent_grave_formatted}\n"
        ]
        
        if total_both_accents > 0:
            both_accents_formatted = format_word_list(all_both_accents_words)
            text_parts.append(f"同时包含两种音符的单词: {total_both_accents}个\n{both_accents_formatted}\n")
        
        text_parts.append(
            f"总计: {total_count}个单词 "
            f"{'✅' if count_match else f'❌ 不符合要求数量 {expected_count}个'}"
        )
        
        text = "\n".join(text_parts)
        
        return (1 if count_match else 0), text
    
    else:
        failed = []
        details = []
        
        for r in results:
            count_match = (r['total_count'] == expected_count)
            
            if not count_match:
                failed.append(r)
            
            accent_aigu_formatted = format_word_list(r['accent_aigu_words'])
            accent_grave_formatted = format_word_list(r['accent_grave_words'])
            
            item_detail_parts = [
                f"第{r['index']+1}项: 总计 {r['total_count']}个单词 "
                f"{'✅' if count_match else f'❌ 不符合 {expected_count}个'}",
                f"  闭音符({r['accent_aigu_count']}个):\n{accent_aigu_formatted}",
                f"  重音符({r['accent_grave_count']}个):\n{accent_grave_formatted}"
            ]
            
            if r['both_accents_count'] > 0:
                both_accents_formatted = format_word_list(r['both_accents_words'])
                item_detail_parts.append(f"  同时包含({r['both_accents_count']}个):\n{both_accents_formatted}")
            
            item_detail = "\n".join(item_detail_parts)
            details.append(item_detail)
        
        passed = len(failed) == 0
        
        status = (
            f"✅ 所有项的音符单词总数都符合要求({expected_count}个)" if passed 
            else f"❌ 有{len(failed)}项的音符单词总数不符合要求({expected_count}个)"
        )
        
        return (1 if passed else 0), status + "\n\n" + "\n\n".join(details)


def french_accent_count_each(corresponding_parts, rule_params):
    """检查每一项文本的闭音符和重音符单词数量"""
    return check_french_accent_count(corresponding_parts, rule_params, mode="each")


###############分音符单词计数####################################
def check_french_circumflex_count(corresponding_parts, rule_params):
    """
    长音符包括: â, ê, ô, î, û
    
    Args:
        corresponding_parts: 待检查的文本列表
        rule_params: 参数，格式为字符串 "[expected_count]" 或 "[expected_count, mode]"
                    expected_count: 期望的长音符词汇数量
                    mode: 可选，"total"(总数检查，默认) 或 "each"(逐项检查)
    """
    
    def extract_french_words(text):
        """提取法语单词"""
        # 匹配法语单词（包括带重音符号的字符）
        pattern = r'\b[a-zA-ZàâäæçéèêëïîôùûüÿœÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ]+\b'
        words = re.findall(pattern, text)
        return words
    
    def has_circumflex(word):
        """检查单词是否包含长音符"""
        circumflex_chars = 'âêôîûÂÊÔÎÛ'
        return any(char in word for char in circumflex_chars)
    
    def format_word_list(words):
        """格式化词汇列表"""
        word_counts = Counter(words)
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        formatted_lines = []
        for word, count in sorted_words:
            if count > 1:
                formatted_lines.append(f"  {word} ({count}次)")
            else:
                formatted_lines.append(f"  {word}")
        
        return "\n".join(formatted_lines) if formatted_lines else "  (无)"
    
    try:
        params = ast.literal_eval(rule_params)
        if isinstance(params, list):
            expected_count = params[0]
            mode = params[1] if len(params) > 1 else "total"
        else:
            expected_count = params
            mode = "total"
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}\n正确格式: [111] 或 [111, 'total']"
    
    if mode == "total":
        # 总数模式：统计所有文本中的长音符词汇总数
        all_circumflex_words = []
        
        for text in corresponding_parts:
            text_str = str(text or "")
            words = extract_french_words(text_str)
            
            for word in words:
                if has_circumflex(word):
                    all_circumflex_words.append(word)
        
        actual_count = len(all_circumflex_words)
        passed = (actual_count == expected_count)
        
        # 格式化输出
        status = "✅" if passed else "❌"
        result_text = f"{status} 长音符词汇数量检查结果:\n"
        result_text += f"期望数量: {expected_count}个\n"
        result_text += f"实际数量: {actual_count}个 {'✅' if passed else '❌'}\n\n"
        
        # 检测到的词汇列表
        result_text += f"检测到的长音符词汇:\n"
        result_text += format_word_list(all_circumflex_words)
        
        return (1 if passed else 0), result_text
    
    elif mode == "each":
        # 逐项模式：每项文本都要有指定数量的长音符词汇
        failed_items = []
        all_details = []
        
        for index, text in enumerate(corresponding_parts):
            text_str = str(text or "")
            words = extract_french_words(text_str)
            
            circumflex_words = []
            for word in words:
                if has_circumflex(word):
                    circumflex_words.append(word)
            
            actual_count = len(circumflex_words)
            passed = (actual_count == expected_count)
            
            if not passed:
                failed_items.append(index + 1)
            
            # 格式化每项的详情
            item_detail = f"第{index + 1}项: "
            item_detail += f"期望{expected_count}个，实际{actual_count}个 "
            item_detail += "✅" if passed else "❌"
            
            if actual_count > 0:
                # 统计词频
                word_counts = Counter(circumflex_words)
                sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                
                item_detail += f"\n  词汇: "
                word_strs = []
                for word, count in sorted_words:
                    if count > 1:
                        word_strs.append(f"{word}({count}次)")
                    else:
                        word_strs.append(word)
                item_detail += ", ".join(word_strs)
            else:
                item_detail += "\n  词汇: (无)"
            
            all_details.append(item_detail)
        
        passed = len(failed_items) == 0
        
        status = "✅ 所有项的长音符词汇数量都正确" if passed else f"❌ 有{len(failed_items)}项不符合要求"
        result_text = status + f" (每项应有{expected_count}个)\n\n"
        result_text += "\n\n".join(all_details)
        
        return (1 if passed else 0), result_text
    
    else:
        return 0, f"❌ 不支持的模式: {mode}，请使用 'total' 或 'each'"


def french_circumflex_total(corresponding_parts, rule_params):
    return check_french_circumflex_count(corresponding_parts, rule_params)


def french_circumflex_each(corresponding_parts, rule_params):
    params = ast.literal_eval(rule_params)
    if isinstance(params, list):
        new_params = [params[0], "each"]
    else:
        new_params = [params, "each"]
    
    return check_french_circumflex_count(corresponding_parts, str(new_params))




###############分音符##################################

def check_french_diaeresis_count(corresponding_parts, rule_params):
    """
    检查法语分音符 (accent tréma) 词汇的数量
    分音符包括: ë, ï, ü
    
    Args:
        corresponding_parts: 待检查的文本列表
        rule_params: 参数，格式为字符串 "[expected_count]" 或 "[expected_count, mode]"
                    expected_count: 期望的分音符词汇数量
                    mode: 可选，"total"(总数检查，默认) 或 "each"(逐项检查)
    
    Returns:
        (pass_flag, message): (是否通过, 详细信息)
    """
    
    def extract_french_words(text):
        """提取法语单词"""
        # 匹配法语单词（包括带重音符号的字符）
        pattern = r'\b[a-zA-ZàâäæçéèêëïîôùûüÿœÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ]+\b'
        words = re.findall(pattern, text)
        return words
    
    def has_diaeresis(word):
        """检查单词是否包含分音符"""
        diaeresis_chars = 'ëïüËÏÜ'
        return any(char in word for char in diaeresis_chars)
    
    def format_word_list(words):
        """格式化词汇列表"""
        word_counts = Counter(words)
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        formatted_lines = []
        for word, count in sorted_words:
            if count > 1:
                formatted_lines.append(f"  {word} ({count}次)")
            else:
                formatted_lines.append(f"  {word}")
        
        return "\n".join(formatted_lines) if formatted_lines else "  (无)"
    
    try:
        params = ast.literal_eval(rule_params)
        if isinstance(params, list):
            expected_count = params[0]
            mode = params[1] if len(params) > 1 else "total"
        else:
            expected_count = params
            mode = "total"
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}\n正确格式: [50] 或 [50, 'total']"
    
    if mode == "total":
        # 总数模式：统计所有文本中的分音符词汇总数
        all_diaeresis_words = []
        
        for text in corresponding_parts:
            text_str = str(text or "")
            words = extract_french_words(text_str)
            
            for word in words:
                if has_diaeresis(word):
                    all_diaeresis_words.append(word)
        
        actual_count = len(all_diaeresis_words)
        passed = (actual_count == expected_count)
        
        # 格式化输出
        status = "✅" if passed else "❌"
        result_text = f"{status} 分音符词汇数量检查结果:\n"
        result_text += f"期望数量: {expected_count}个\n"
        result_text += f"实际数量: {actual_count}个 {'✅' if passed else '❌'}\n\n"
        
        # 检测到的词汇列表
        result_text += f"检测到的分音符词汇:\n"
        result_text += format_word_list(all_diaeresis_words)
        
        return (1 if passed else 0), result_text
    
    elif mode == "each":
        # 逐项模式：每项文本都要有指定数量的分音符词汇
        failed_items = []
        all_details = []
        
        for index, text in enumerate(corresponding_parts):
            text_str = str(text or "")
            words = extract_french_words(text_str)
            
            diaeresis_words = []
            for word in words:
                if has_diaeresis(word):
                    diaeresis_words.append(word)
            
            actual_count = len(diaeresis_words)
            passed = (actual_count == expected_count)
            
            if not passed:
                failed_items.append(index + 1)
            
            # 格式化每项的详情
            item_detail = f"第{index + 1}项: "
            item_detail += f"实际{actual_count}个 "
            
            if actual_count > 0:
                # 统计词频
                word_counts = Counter(diaeresis_words)
                sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                
                item_detail += f"\n  词汇: "
                word_strs = []
                for word, count in sorted_words:
                    if count > 1:
                        word_strs.append(f"{word}({count}次)")
                    else:
                        word_strs.append(word)
                item_detail += ", ".join(word_strs)
            else:
                item_detail += " "
            
            all_details.append(item_detail)
        
        passed = len(failed_items) == 0
        
        status = "✅ 所有项的分音符词汇数量都正确" if passed else f"❌ 有{len(failed_items)}项不符合要求"
        result_text = status + f" (每项应有{expected_count}个)\n\n"
        result_text += "\n\n".join(all_details)
        
        return (1 if passed else 0), result_text
    
    else:
        return 0, f"❌ 不支持的模式: {mode}，请使用 'total' 或 'each'"


def french_diaeresis_total(corresponding_parts, rule_params):
    return check_french_diaeresis_count(corresponding_parts, rule_params)


def french_diaeresis_each(corresponding_parts, rule_params):
    params = ast.literal_eval(rule_params)
    if isinstance(params, list):
        new_params = [params[0], "each"]
    else:
        new_params = [params, "each"]
    
    return check_french_diaeresis_count(corresponding_parts, str(new_params))


##############软音符词汇#############################
def check_french_cedilla_count(corresponding_parts, rule_params):
    def extract_french_words(text):
        """提取法语单词"""
        # 匹配法语单词（包括带重音符号的字符）
        pattern = r'\b[a-zA-ZàâäæçéèêëïîôùûüÿœÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ]+\b'
        words = re.findall(pattern, text)
        return words
    
    def has_cedilla(word):
        """检查单词是否包含软音符"""
        cedilla_chars = 'çÇ'
        return any(char in word for char in cedilla_chars)
    
    def format_word_list(words):
        """格式化词汇列表"""
        word_counts = Counter(words)
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        formatted_lines = []
        for word, count in sorted_words:
            if count > 1:
                formatted_lines.append(f"  {word} ({count}次)")
            else:
                formatted_lines.append(f"  {word}")
        
        return "\n".join(formatted_lines) if formatted_lines else "  (无)"
    
    try:
        params = ast.literal_eval(rule_params)
        if isinstance(params, list):
            expected_count = params[0]
            mode = params[1] if len(params) > 1 else "total"
        else:
            expected_count = params
            mode = "total"
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}\n正确格式: [20] 或 [20, 'total']"
    
    if mode == "total":
        # 总数模式：统计所有文本中的软音符词汇总数
        all_cedilla_words = []
        
        for text in corresponding_parts:
            text_str = str(text or "")
            words = extract_french_words(text_str)
            
            for word in words:
                if has_cedilla(word):
                    all_cedilla_words.append(word)
        
        actual_count = len(all_cedilla_words)
        passed = (actual_count == expected_count)
        
        # 格式化输出
        status = "✅" if passed else "❌"
        result_text = f"{status} 软音符词汇数量检查结果:\n"
        result_text += f"期望数量: {expected_count}个\n"
        result_text += f"实际数量: {actual_count}个 {'✅' if passed else '❌'}\n\n"
        
        # 检测到的词汇列表
        result_text += f"检测到的软音符词汇:\n"
        result_text += format_word_list(all_cedilla_words)
        
        return (1 if passed else 0), result_text
    
    elif mode == "each":
        # 逐项模式：每项文本都要有指定数量的软音符词汇
        failed_items = []
        all_details = []
        
        for index, text in enumerate(corresponding_parts):
            text_str = str(text or "")
            words = extract_french_words(text_str)
            
            cedilla_words = []
            for word in words:
                if has_cedilla(word):
                    cedilla_words.append(word)
            
            actual_count = len(cedilla_words)
            passed = (actual_count == expected_count)
            
            if not passed:
                failed_items.append(index + 1)
            
            # 格式化每项的详情
            item_detail = f"第{index + 1}项: "
            item_detail += f"期望{expected_count}个，实际{actual_count}个 "
            item_detail += "✅" if passed else "❌"
            
            if actual_count > 0:
                # 统计词频
                word_counts = Counter(cedilla_words)
                sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                
                item_detail += f"\n  词汇: "
                word_strs = []
                for word, count in sorted_words:
                    if count > 1:
                        word_strs.append(f"{word}({count}次)")
                    else:
                        word_strs.append(word)
                item_detail += ", ".join(word_strs)
            else:
                item_detail += "\n  词汇: (无)"
            
            all_details.append(item_detail)
        
        passed = len(failed_items) == 0
        
        status = "✅ 所有项的软音符词汇数量都正确" if passed else f"❌ 有{len(failed_items)}项不符合要求"
        result_text = status + f" (每项应有{expected_count}个)\n\n"
        result_text += "\n\n".join(all_details)
        
        return (1 if passed else 0), result_text
    
    else:
        return 0, f"❌ 不支持的模式: {mode}，请使用 'total' 或 'each'"


def french_cedilla_total(corresponding_parts, rule_params):
    
    return check_french_cedilla_count(corresponding_parts, rule_params)


def french_cedilla_each(corresponding_parts, rule_params):
   
    params = ast.literal_eval(rule_params)
    if isinstance(params, list):
        new_params = [params[0], "each"]
    else:
        new_params = [params, "each"]
    
    return check_french_cedilla_count(corresponding_parts, str(new_params))

######################韵律模式#######################

def check_french_rhyme_pattern(corresponding_parts, rule_params):
    try:
        import frhyme
    except ImportError:
        return 0, "缺少 frhyme 库，请运行: pip install frhyme"
    
    # 根据实际测试结果的 X-SAMPA 到 IPA 映射表
    XSAMPA_TO_IPA = {
        'a': 'a',
        'e': 'e',
        'E': 'ɛ',
        'i': 'i',
        'o': 'o',
        'O': 'ɔ',
        'u': 'u',
        'y': 'y',
        '2': 'ø',
        '9': 'œ',
        '@': 'ə',
        '$': 'ɔ̃',
        '#': 'ɑ̃',
        ')': 'ɛ̃',
        '(': 'œ̃',
        '8': 'ɥ',
        'w': 'w',
        'j': 'j',
        'p': 'p',
        'b': 'b',
        't': 't',
        'd': 'd',
        'k': 'k',
        'g': 'ɡ',
        'f': 'f',
        'v': 'v',
        's': 's',
        'z': 'z',
        'S': 'ʃ',
        'Z': 'ʒ',
        'm': 'm',
        'n': 'n',
        'l': 'l',
        'R': 'ʁ',
    }
    
    # 定义元音（包括鼻元音和半元音）
    VOWELS_XSAMPA = set(['a', 'e', 'E', 'i', 'o', 'O', 'u', 'y', '2', '9', '@', 
                         '$', '#', ')', '('])
    
    def xsampa_to_ipa(xsampa):
        if not xsampa:
            return ""
        ipa = ""
        for char in xsampa:
            if char in XSAMPA_TO_IPA:
                ipa += XSAMPA_TO_IPA[char]
            else:
                ipa += char
        return ipa
    
    def extract_last_syllable_rhyme(phoneme_xsampa):
        """
        提取最后一个音节的押韵部分（最后的元音及其后的所有音素）
        
        Args:
            phoneme_xsampa: X-SAMPA 格式的音素
        
        Returns:
            最后一个元音及其后的所有音素
        """
        if not phoneme_xsampa:
            return ""
        
        # 从后往前找最后一个元音
        last_vowel_pos = -1
        for i in range(len(phoneme_xsampa) - 1, -1, -1):
            if phoneme_xsampa[i] in VOWELS_XSAMPA:
                last_vowel_pos = i
                break
        
        if last_vowel_pos == -1:
            # 没找到元音，返回最后2个字符
            return phoneme_xsampa[-2:] if len(phoneme_xsampa) >= 2 else phoneme_xsampa
        
        # 返回最后一个元音及其后的所有音素
        return phoneme_xsampa[last_vowel_pos:]
    
    def extract_last_word(sentence):
        if not sentence:
            return ""
        sentence = sentence.strip()
        sentence = re.sub(r'[.,;:!?…"»""]+$', '', sentence)
        words = sentence.split()
        if not words:
            return ""
        last_word = words[-1].strip()
        last_word = re.sub(r'[.,;:!?…"»""]+$', '', last_word)
        return last_word.lower()
    
    def get_phoneme(word):
        if not word:
            return None, None, 0
        clean_word = word
        if "'" in word or "'" in word or "'" in word:
            parts = re.split(r"['']", word)
            if len(parts) > 1:
                clean_word = parts[-1]
        clean_word = re.sub(r'[^a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]', '', clean_word)
        if not clean_word:
            return None, None, 0
        try:
            results = frhyme.lookup(clean_word.lower(), 1)
            if results:
                confidence, phoneme_xsampa = results[0]
                phoneme_ipa = xsampa_to_ipa(phoneme_xsampa)
                return phoneme_xsampa, phoneme_ipa, confidence
        except:
            pass
        return None, None, 0
    
    def check_rhyme_match(word1, word2):
        """
        检查两个单词是否押韵
        
        法语押韵规则：最后的押韵部分（元音+辅音）必须完全相同
        """
        p1, _, _ = get_phoneme(word1)
        p2, _, _ = get_phoneme(word2)
        
        if not p1 or not p2:
            return False, 0
        
        # 提取最后的押韵部分（最后的元音及其后面的音素）
        rhyme1 = extract_last_syllable_rhyme(p1)
        rhyme2 = extract_last_syllable_rhyme(p2)
        
        if not rhyme1 or not rhyme2:
            return False, 0
        
        # 押韵部分完全相同才算押韵
        if rhyme1 == rhyme2:
            return True, len(rhyme1)
        
        return False, 0
    
    def extract_last_words(sentences):
        last_words = []
        for sentence in sentences:
            word = extract_last_word(sentence)
            last_words.append(word)
        return last_words
    
    def analyze_rhyme_pattern(words):
        pattern = []
        rhyme_groups = {}
        phonemes_xsampa = []
        phonemes_ipa = []
        rhyme_parts = []  # 存储押韵部分
        current_label = 'A'
        
        for i, word in enumerate(words):
            phoneme_x, phoneme_i, _ = get_phoneme(word)
            phonemes_xsampa.append(phoneme_x)
            phonemes_ipa.append(phoneme_i)
            
            if not phoneme_x:
                pattern.append('?')
                rhyme_parts.append("")
                continue
            
            # 提取押韵部分
            rhyme_part = extract_last_syllable_rhyme(phoneme_x)
            rhyme_parts.append(rhyme_part)
            
            # 检查是否与之前的词押韵
            found_match = False
            for label, group_indices in rhyme_groups.items():
                first_word = words[group_indices[0]]
                is_match, _ = check_rhyme_match(word, first_word)
                
                if is_match:
                    pattern.append(label)
                    rhyme_groups[label].append(i)
                    found_match = True
                    break
            
            if not found_match:
                pattern.append(current_label)
                rhyme_groups[current_label] = [i]
                current_label = chr(ord(current_label) + 1)
        
        return pattern, phonemes_xsampa, phonemes_ipa, rhyme_parts
    
    def check_pattern_match(actual_pattern, expected_pattern):
        if len(actual_pattern) != len(expected_pattern):
            return False
        mapping = {}
        reverse_mapping = {}
        for actual, expected in zip(actual_pattern, expected_pattern):
            if actual == '?':
                return False
            if expected in mapping:
                if mapping[expected] != actual:
                    return False
            else:
                if actual in reverse_mapping:
                    return False
                mapping[expected] = actual
                reverse_mapping[actual] = expected
        return True
    
    try:
        expected_pattern = rule_params.strip().upper()
        if not expected_pattern:
            return 0, "未指定押韵模式"
        if not all(c.isalpha() for c in expected_pattern):
            return 0, f"押韵模式格式错误: {expected_pattern}"
    except Exception as e:
        return 0, f"参数格式错误: {e}"
    
    sentences = [str(part or "") for part in corresponding_parts]
    last_words = extract_last_words(sentences)
    
    if not last_words or all(not w for w in last_words):
        return 0, "无法提取句尾单词"
    
    if len(last_words) != len(expected_pattern):
        return 0, f"诗句数量不符：期望 {len(expected_pattern)} 行，实际 {len(last_words)} 行"
    
    actual_pattern, phonemes_xsampa, phonemes_ipa, rhyme_parts = analyze_rhyme_pattern(last_words)
    is_match = check_pattern_match(actual_pattern, list(expected_pattern))
    
    pattern_names = {
        "ABBA": "环抱韵",
        "ABAB": "交叉韵",
        "AABB": "平韵",
        "AAAA": "一韵到底",
    }
    
    pattern_name = pattern_names.get(expected_pattern, expected_pattern)
    status = "✅" if is_match else "❌"
    
    result_text = f"{status} 法语押韵检查: 期望 {expected_pattern} ({pattern_name})，实际 {''.join(actual_pattern)}\n\n"
    
    # 显示每行的押韵信息（只显示完整音素和押韵部分）
    for i, (word, phoneme_ipa, rhyme_part, label) in enumerate(zip(last_words, phonemes_ipa, rhyme_parts, actual_pattern), 1):
        if phoneme_ipa:
            rhyme_ipa = xsampa_to_ipa(rhyme_part) if rhyme_part else ""
            result_text += f"第{i}行 ({label}): {word} -> 韵脚 [{phoneme_ipa}] (押韵: {rhyme_ipa})\n"
        else:
            result_text += f"第{i}行 ({label}): {word} -> 韵脚 [无法获取]\n"
    
    if not is_match:
        result_text += "\n不押韵的问题:\n"
        mismatches = []
        for i in range(len(expected_pattern)):
            for j in range(i + 1, len(expected_pattern)):
                if expected_pattern[i] == expected_pattern[j]:
                    if actual_pattern[i] != actual_pattern[j]:
                        word1 = last_words[i]
                        word2 = last_words[j]
                        mismatches.append(f"第{i+1}行 '{word1}' 与 第{j+1}行 '{word2}' 不押韵")
        for mismatch in mismatches:
            result_text += "• " + mismatch + "\n"
    
    return (1 if is_match else 0), result_text


def french_rhyme_pattern(corresponding_parts, rule_params):
    return check_french_rhyme_pattern(corresponding_parts, rule_params)


#############################法语数字#############################################

def contains_french_seven_digit_number(text):
    """
    判断句子中是否包含至少一个正好七位数的阿拉伯数字，并符合法语数字书写习惯
    
    返回:
        tuple: (bool, str) - (是否匹配, 详细解释)
    """
    # 处理 None
    if text is None:
        return False, "输入为 None"
    
    # 处理列表：检查每一项
    if isinstance(text, list):
        if len(text) == 0:
            return False, "列表为空"
        
        matched_items = []
        unmatched_items = []
        
        for i, item in enumerate(text, 1):
            result, explanation, failure_reason = check_single_item(item)
            
            item_preview = str(item)[:60] + ('...' if len(str(item)) > 60 else '')
            
            if result:
                matched_items.append(i)
            else:
                # 提取数字和失败原因
                unmatched_items.append((i, item_preview, failure_reason))
        
        total_items = len(text)
        matched_count = len(matched_items)
        
        # 如果全部匹配，简化输出
        if matched_count == total_items:
            return True, f"✅ 所有 {total_items} 项均满足七位数要求，且符合书写格式 (格式: d ddd ddd)"
        
        # 如果全部不匹配
        if matched_count == 0:
            details = []
            for i, preview, reason in unmatched_items:
                details.append(f"项 {i}: {reason}")
            explanation = "❌ 所有项均不符合要求，" + "；".join(details)
            return False, explanation
        
        # 部分匹配，列出不符合的项
        details = []
        for i, preview, reason in unmatched_items:
            details.append(f"项 {i}: {reason}")
        
        explanation = f"❌ 部分项不符合要求 (匹配 {matched_count}/{total_items})，" + "；".join(details)
        return True, explanation
    
    # 处理字符串
    result, explanation, failure_reason = check_single_item(text)
    return result, explanation


def check_single_item(text):
    text = str(text)
    
    if not text.strip():
        return False, "输入为空字符串", "空字符串"
    
    # 正确格式: d ddd ddd
    correct_pattern = r'\b\d\s\d{3}\s\d{3}\b'
    
    # 检查是否有正确格式的七位数
    correct_matches = re.findall(correct_pattern, text)
    
    if correct_matches:
        text_preview = text[:80] + ('...' if len(text) > 80 else '')
        if len(correct_matches) == 1:
            explanation = f"✅ {text_preview} 找到七位数: {correct_matches[0]}"
        else:
            numbers = ', '.join(correct_matches)
            explanation = f"✅ {text_preview} 找到 {len(correct_matches)} 个七位数: {numbers}"
        return True, explanation, None
    
    # 未找到正确格式，分析原因
    text_preview = text[:80] + ('...' if len(text) > 80 else '')
    
    # 检查是否有八位数 (有空格但位数不对)
    eight_digit_pattern = r'\b\d{1,2}\s\d{3}\s\d{3}\b'
    eight_digit_matches = re.findall(eight_digit_pattern, text)
    if eight_digit_matches:
        failure_reason = f"{eight_digit_matches[0]} 不符合位数要求（八位数）"
        explanation = f"❌ {text_preview} {failure_reason}"
        return False, explanation, failure_reason
    
    # 检查是否有六位数 (有空格但位数不对)
    six_digit_pattern = r'\b\d{3}\s\d{3}\b'
    six_digit_matches = re.findall(six_digit_pattern, text)
    if six_digit_matches:
        failure_reason = f"{six_digit_matches[0]} 不符合位数要求（六位数）"
        explanation = f"❌ {text_preview} {failure_reason}"
        return False, explanation, failure_reason
    
    # 检查是否有七位数但没有空格
    no_space_pattern = r'\b\d{7}\b'
    no_space_matches = re.findall(no_space_pattern, text)
    if no_space_matches:
        failure_reason = f"{no_space_matches[0]} 不符合书写格式要求（缺少空格）"
        explanation = f"❌ {text_preview} {failure_reason}"
        return False, explanation, failure_reason
    
    # 检查是否有七位数但空格位置错误
    wrong_space_patterns = [
        r'\b\d{2}\s\d{2}\s\d{3}\b',  # dd dd ddd
        r'\b\d{3}\s\d{4}\b',          # ddd dddd
        r'\b\d{4}\s\d{3}\b',          # dddd ddd
        r'\b\d\s\d\s\d{5}\b',         # d d ddddd
    ]
    
    for pattern in wrong_space_patterns:
        wrong_space_matches = re.findall(pattern, text)
        if wrong_space_matches:
            failure_reason = f"{wrong_space_matches[0]} 不符合书写格式要求（空格位置错误）"
            explanation = f"❌ {text_preview} {failure_reason}"
            return False, explanation, failure_reason
    
    # 没有找到任何七位数
    failure_reason = "未找到七位数"
    explanation = f"❌ {text_preview} 未找到符合格式的七位数 (正确格式: d ddd ddd)"
    return False, explanation, failure_reason


def is_vigesimal_number(text):
    """
    检测法语数字是否包含二十进制部分 (71-99)
    仅检查法语文字形式，不检查阿拉伯数字
    
    返回:
        tuple: (bool, str) - (是否包含二十进制, 详细解释)
    """
    # 处理 None
    if text is None:
        return False, "输入为 None"
    
    # 处理列表：检查每一项
    if isinstance(text, list):
        if len(text) == 0:
            return False, "列表为空"
        
        # 先检查是否有阿拉伯数字
        has_arabic_digit = False
        for item in text:
            if re.search(r'\d', str(item)):
                has_arabic_digit = True
                break
        
        if has_arabic_digit:
            return False, "❌ 所有项均不是法语文字形式（包含阿拉伯数字）"
        
        # 没有阿拉伯数字，检查二十进制
        matched_indices = []
        unmatched_indices = []
        
        for i, item in enumerate(text, 1):
            item_str = str(item).strip()
            result, _, _ = check_single_vigesimal(item_str)
            if result:
                matched_indices.append(i)
            else:
                unmatched_indices.append(i)
        
        total_items = len(text)
        matched_count = len(matched_indices)
        
        # 如果全部包含二十进制
        if matched_count == total_items:
            return True, f"✅ 所有 {total_items} 项均包含二十进制数字 (71-99)"
        
        # 如果全部不包含
        if matched_count == 0:
            return False, f"❌ 所有 {total_items} 项均不包含二十进制数字 (71-99)"
        
        # 部分包含，只列出不包含的项号
        unmatched_str = "、".join([f"项 {i}" for i in unmatched_indices])
        return True, f"❌ 部分项不包含二十进制 (匹配 {matched_count}/{total_items})，{unmatched_str} 不包含"
    
    # 处理字符串
    item_str = str(text).strip()
    
    # 先检查是否有阿拉伯数字
    if re.search(r'\d', item_str):
        return False, "❌ 不是法语文字形式（包含阿拉伯数字）"
    
    result, explanation, vigesimal_parts = check_single_vigesimal(item_str)
    return result, explanation


def check_single_vigesimal(text):
    text = str(text).lower().strip()
    
    # 移除标点符号
    text = re.sub(r'[.,!?;:]', '', text)
    
    if not text:
        return False, "输入为空字符串", []
    
    vigesimal_parts = []
    
    # 71-79: soixante et onze, soixante-douze, ..., soixante-dix-neuf
    pattern_71_79 = r'\b(soixante(?:-|\s+)(?:et\s+onze|onze|douze|treize|quatorze|quinze|seize|dix-sept|dix-huit|dix-neuf))\b'
    
    # 80: quatre-vingts 或 quatre-vingt (单独出现时)
    pattern_80 = r'\b(quatre-vingts?)\b(?!\s*(?:mille|million|milliard|un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix))'
    
    # 81-89: quatre-vingt-un, ..., quatre-vingt-neuf
    pattern_81_89 = r'\b(quatre-vingts?(?:-|\s+)(?:un|une|deux|trois|quatre|cinq|six|sept|huit|neuf))\b'
    
    # 90: quatre-vingt-dix (单独)
    pattern_90 = r'\b(quatre-vingt(?:-|\s+)dix)\b(?!\s*(?:un|deux|trois|quatre|cinq|six|sept|huit|neuf))'
    
    # 91-99: quatre-vingt-dix-un, ..., quatre-vingt-dix-neuf
    pattern_91_99 = r'\b(quatre-vingt(?:-|\s+)dix(?:-|\s+)(?:un|une|deux|trois|quatre|cinq|six|sept|huit|neuf))\b'
    
    # 检测 71-79
    for match in re.finditer(pattern_71_79, text):
        segment = match.group(1)
        vigesimal_parts.append({
            'segment': segment,
            'explanation': '71-79',
            'is_vigesimal': True
        })
    
    # 检测 80（单独）
    for match in re.finditer(pattern_80, text):
        segment = match.group(1)
        vigesimal_parts.append({
            'segment': segment,
            'explanation': '80',
            'is_vigesimal': True
        })
    
    # 检测 81-89
    for match in re.finditer(pattern_81_89, text):
        segment = match.group(1)
        vigesimal_parts.append({
            'segment': segment,
            'explanation': '81-89',
            'is_vigesimal': True
        })
    
    # 检测 90（单独）
    for match in re.finditer(pattern_90, text):
        segment = match.group(1)
        vigesimal_parts.append({
            'segment': segment,
            'explanation': '90',
            'is_vigesimal': True
        })
    
    # 检测 91-99
    for match in re.finditer(pattern_91_99, text):
        segment = match.group(1)
        vigesimal_parts.append({
            'segment': segment,
            'explanation': '91-99',
            'is_vigesimal': True
        })
    
    text_preview = text[:80] + ('...' if len(text) > 80 else '')
    
    if vigesimal_parts:
        parts_desc = []
        for part in vigesimal_parts:
            parts_desc.append(f"{part['segment']} ({part['explanation']})")
        
        parts_str = "、".join(parts_desc)
        explanation = f"✅ {text_preview} 包含二十进制: {parts_str}"
        return True, explanation, vigesimal_parts
    else:
        explanation = f"❌ {text_preview} 不包含二十进制数字"
        return False, explanation, []
    

###########################代词式动词###########################  
class PronominalVerbDetector:
    def __init__(self):
        # self.cg = Conjugator(Lang.fr)
        self.cg = Conjugator(lang='fr')
        self.reflexive = ['me', "m'", 'te', "t'", 'se', "s'", 'nous', 'vous']
        self.subjects = {
            'je': ['me', "m'"], "j'": ['me', "m'"],
            'tu': ['te', "t'"],
            'il': ['se', "s'"], 'elle': ['se', "s'"], 'on': ['se', "s'"],
            'nous': ['nous'], 'vous': ['vous'],
            'ils': ['se', "s'"], 'elles': ['se', "s'"],
            'cela': ['se', "s'"], 'objectif': ['se', "s'"],
            'ça': ['se', "s'"], 'ella': ['se', "s'"],
        }
        
        # ====== 新增：多词主语配置 ======
        self.multi_word_subjects = {
            # 所有格 + 名词
            'son but': ['se', "s'"],
            'son objectif': ['se', "s'"],
            'leur objectif': ['se', "s'"],
            'leur but': ['se', "s'"],
            'mon objectif': ['me', "m'"],
            'mon but': ['me', "m'"],
            'ton but': ['te', "t'"],
            'ton objectif': ['te', "t'"],
            'notre but': ['nous'],
            'notre objectif': ['nous'],
            'votre objectif': ['vous'],
            'votre but': ['vous'],
            
            # 指示形容词 + 名词
            'ce but': ['se', "s'"],
            'cet objectif': ['se', "s'"],
            'cette approche': ['se', "s'"],
            'cette méthode': ['se', "s'"],
            'ces objectifs': ['se', "s'"],
            
            # 冠词 + 名词（常见的）
            'le but': ['se', "s'"],
            "l'objectif": ['se', "s'"],
            'la méthode': ['se', "s'"],
            'les objectifs': ['se', "s'"],
            
            # 其他常见组合
            'chaque personne': ['se', "s'"],
            'tout le monde': ['se', "s'"],
        }
        # ====== 新增结束 ======
        
        self.stop_tokens = {
            '.', '!', '?', ';', ':',
            'que', "qu'", 'qui', 'où', 'dont', 'si', 'mais',
            'lequel', 'laquelle', 'lesquels', 'lesquelles',
            'auquel', 'auxquels', 'auxquelles',
            'duquel', 'desquels', 'desquelles',
        }
        
        self.prepositions = {
            'à', 'de', "d'", 'en', 'par', 'pour', 'avec', 'sans', 'sous', 'sur',
            'vers', 'chez', 'dans', 'entre', 'contre', 'depuis', 'pendant',
            'avant', 'après', 'devant', 'derrière', 'près', 'loin',
        }
        
        self.skip_adj_prep = {
            'prêt', 'prête', 'prêts', 'prêtes',
            'disposé', 'disposée', 'disposés', 'disposées',
            'décidé', 'décidée', 'décidés', 'décidées',
            'obligé', 'obligée', 'obligés', 'obligées',
            'content', 'contente', 'contents', 'contentes',
            'heureux', 'heureuse',
            'capable', 'capables',
        }
        
        self.skip_verbs = {
            'retourner', 'aller', 'venir', 'pouvoir', 'vouloir', 'devoir',
            'commencer', 'continuer', 'arrêter', 'finir', 'cesser',
            'essayer', 'tenter', 'chercher', 'espérer', 'décider',
            'aimer', 'préférer', 'détester', 'adorer', 'souhaiter',
        }
        
        self.etre_forms = self._get_etre_forms()
        self.b_class_forms = self._get_b_class_verb_forms()
        self.b_class_verbs_set = {
            'faire', 'laisser', 'envoyer', 'regarder',
            'entendre', 'écouter', 'sentir',
        }
        
        self.index_file = Path('verb_index_optimized.json')
        self.reverse_index = self._load_or_build_index()
    
    def _get_etre_forms(self) -> Set[str]:
        etre_forms = set()
        try:
            result = self.cg.conjugate('être')
            for mood_data in result['moods'].values():
                for forms in mood_data.values():
                    if isinstance(forms, list):
                        for form in forms:
                            if isinstance(form, str):
                                parts = form.split()
                                verb_part = parts[-1] if parts else form
                                verb_part = verb_part.lower().strip()
                                if verb_part:
                                    etre_forms.add(verb_part)
        except:
            pass
        return etre_forms
    
    def _get_b_class_verb_forms(self) -> Set[str]:
        b_class_verbs = [
            'faire', 'laisser', 'envoyer', 'regarder',
            'entendre', 'écouter', 'sentir',
        ]
        
        b_class_forms = set()
        for verb in b_class_verbs:
            try:
                result = self.cg.conjugate(verb)
                for mood_data in result['moods'].values():
                    for forms in mood_data.values():
                        if isinstance(forms, list):
                            for form in forms:
                                if isinstance(form, str):
                                    parts = form.split()
                                    verb_part = parts[-1] if parts else form
                                    verb_part = verb_part.lower().strip()
                                    if verb_part:
                                        b_class_forms.add(verb_part)
            except:
                pass
        
        return b_class_forms
    
    def _load_or_build_index(self) -> Dict[str, List[str]]:
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            index = self._build_index()
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            return index
    
    def _build_index(self) -> Dict[str, List[str]]:
        all_infinitives = self.cg.get_infinitives()
        base_verbs = []
        for inf in all_infinitives:
            cleaned = re.sub(r'^se\s+', '', inf)
            cleaned = re.sub(r"^s'\s*", '', cleaned)
            base_verbs.append(cleaned)
        
        base_verbs = list(set(base_verbs))
        reverse_index = {}
        
        for infinitive in base_verbs:
            try:
                result = self.cg.conjugate(infinitive)
                for mood_data in result['moods'].values():
                    for forms in mood_data.values():
                        if isinstance(forms, list):
                            for form in forms:
                                if isinstance(form, str):
                                    parts = form.split()
                                    verb_part = parts[-1] if parts else form
                                    verb_part = verb_part.lower().strip()
                                    if verb_part:
                                        if verb_part not in reverse_index:
                                            reverse_index[verb_part] = []
                                        if infinitive not in reverse_index[verb_part]:
                                            reverse_index[verb_part].append(infinitive)
            except:
                pass
        
        return reverse_index
    
    def tokenize(self, sentence: str) -> List[str]:
        apostrophe_variants = [
            '\u2018', '\u2019', '\u201B', '\u02BC', '\u02BB', 
            '\u2032', '\u2035', '\uFF07',
        ]
        
        for variant in apostrophe_variants:
            sentence = sentence.replace(variant, "'")
        
        sentence = re.sub(r'([.?!;:,])', r' \1 ', sentence)
        sentence = re.sub(r"'([a-zA-Zàâäéèêëïîôùûüÿœæç])", r"' \1", sentence)
        
        tokens = []
        for t in sentence.split():
            if t:
                tokens.append(t)
        return tokens
    
    def is_pronominal_verb(self, infinitive: str) -> bool:
        try:
            result = self.cg.conjugate(f'se {infinitive}')
            return 'moods' in result and bool(result['moods'])
        except:
            return False
    
    def _is_verb_infinitive(self, word: str) -> bool:
        if not (word.endswith('er') or word.endswith('ir') or 
                word.endswith('re') or word.endswith('oir')):
            return False
        
        non_verbs = {
            'pour', 'sur', 'hier', 'fier', 'cher', 'mer', 'ver', 'fer',
            'air', 'pair', 'chair', 'éclair',
            'être', 'mettre', 'lettre', 'maitre', 'titre',
        }
        if word in non_verbs:
            return False
        
        try:
            verb_obj = self.cg.find_verb_by_infinitive(word)
            return verb_obj is not None
        except:
            return False
    
    def _find_verb_after_pronoun(self, tokens: List[str], pronoun_index: int, max_lookforward: int = 4) -> tuple:
        green_tokens = {
            'finalement', 'déjà', 'enfin', 'bien', 'mal', 'mieux', 'toujours', 'souvent', 'parfois',
            'aussi', 'encore', 'peut-être','pourtant','beaucoup', 'peu', 'très', 'trop', 'assez','fois','quelque',
            'presque', 'jamais', 'rien', 'personne','ni','alors',
            'ne', "n'", 'pas', 'plus', 'point', 'guère',
            'moi-même', 'toi-même', 'lui-même', 'elle-même',
            'nous-mêmes', 'vous-mêmes', 'eux-mêmes', 'elles-mêmes',
        }
        
        stop_tokens = {
            '.', '!', '?', ';', ':', 
            'que', "qu'", 'qui', 'où', 'dont', 'si', 'mais',
        }
        
        end_pos = min(len(tokens), pronoun_index + 1 + max_lookforward)
        
        for j in range(pronoun_index + 1, end_pos):
            token = tokens[j].lower()
            
            if token in stop_tokens:
                break
            
            is_etre_inversion = False
            if '-' in token:
                match = re.match(r'^([a-zàâäéèêëïîôùûüÿœæç]+)-', token)
                if match:
                    base_form = match.group(1)
                    if base_form in self.etre_forms:
                        is_etre_inversion = True
            
            is_ment_adverb = token.endswith('ment') and len(token) > 4
            
            if token in self.etre_forms or is_etre_inversion or token in green_tokens or is_ment_adverb:
                continue
            
            if token in self.reverse_index:
                return (j, token)
            
            if token.startswith(('re', 'ré')) and len(token) > 2:
                token_without_re = token[2:]
                if token_without_re in self.reverse_index:
                    return (j, token)
            
            if self._is_verb_infinitive(token):
                return (j, token)
            
            verb_endings = ['e', 'es', 'ent', 'ons', 'ez', 'a', 'ont', 'ai', 'as', 'ait', 'aient',
                           'er', 'ir', 're', 'oir', 'é', 'és', 'ée', 'ées', 'ant']
            
            looks_like_verb = any(token.endswith(ending) for ending in verb_endings)
            
            if looks_like_verb and len(token) > 3:
                return (j, token)
            
            break
        
        return (None, None)
    
    def _check_nearby_verb_for_se(self, tokens: List[str], pronoun_index: int, max_lookback: int = 3) -> bool:
        stop_tokens = {
            '.', '!', '?', ';', ':',
            'que', "qu'", 'qui', 'où', 'dont','si','mais',
            'lequel', 'laquelle', 'lesquels', 'lesquelles',
        }
        
        clause_separators = {',', 'et', 'ou', 'donc', 'or', 'ni', 'car'}
        start_pos = max(0, pronoun_index - max_lookback)
        prev_has_reflexive = False
        
        for j in range(pronoun_index - 1, start_pos - 1, -1):
            if j < 0:
                break
                
            token = tokens[j].lower()
            
            if token in clause_separators:
                return True
            
            if token in stop_tokens:
                break
            
            if token in self.reflexive:
                prev_has_reflexive = True
                continue
            
            if token in ['ne', "n'", 'pas', 'plus', 'jamais', 'rien', 'de', "d'", 'à']:
                continue
            
            if token in self.reverse_index:
                if token in self.etre_forms:
                    prev_has_reflexive = False
                    continue
                
                if token.endswith('ant'):
                    prev_has_reflexive = False
                    continue
                
                if token in self.b_class_forms:
                    if prev_has_reflexive:
                        prev_has_reflexive = False
                        continue
                    else:
                        return False
                
                prev_has_reflexive = False
                continue
            
            prev_has_reflexive = False
        
        return True
    
    def _are_same_pronoun_group(self, p1: str, p2: str) -> bool:
        """判断两个反身代词是否属于同一组"""
        for subject_pronouns in self.subjects.values():
            if p1 in subject_pronouns and p2 in subject_pronouns:
                return True
        return False
    
    def _find_subject_or_reflexive_across_comma(self, tokens: List[str], pronoun_index: int, current_pronoun: str) -> str:
        """
        当反身代词前面有逗号或', et'时，优先查找最近的反身代词组，
        如果找不到则查找主语
        """
        # 如果是 se/s'，不需要检查主语
        if current_pronoun in ['se', "s'"]:
            return "se_pronoun"
        
        for j in range(pronoun_index - 1, max(0, pronoun_index - 15) - 1, -1):
            if j < 0:
                break
                
            token = tokens[j].lower()
            
            # ====== 新增：检查多词主语（优先检查）======
            if j > 0:
                two_word_subject = f"{tokens[j-1].lower()} {token}"
                
                if two_word_subject in self.multi_word_subjects:
                    # 检查前面是否有介词
                    if j > 1 and tokens[j-2].lower() in self.prepositions:
                        pass  # 跳过
                    else:
                        if current_pronoun in self.multi_word_subjects[two_word_subject]:
                            return two_word_subject
                        else:
                            return None
            # ====== 新增结束 ======
            
            # 如果找到反身代词，检查是否匹配
            if token in self.reflexive:
                if token == current_pronoun or self._are_same_pronoun_group(token, current_pronoun):
                    return "matched_reflexive"
                else:
                    return None
            
            # 如果找到主语，检查是否匹配
            if token in self.subjects:
                if j > 0 and tokens[j-1].lower() in self.prepositions:
                    continue
                
                if current_pronoun in self.subjects[token]:
                    return token
                else:
                    return None
            
            # 跳过这些词继续查找
            if token in ['en', ',', 'et']:
                continue
            
            if token in self.prepositions:
                continue
            
            if token in self.skip_adj_prep:
                continue
            
            # 如果遇到动词
            if token in self.reverse_index:
                # 如果是 être，继续查找
                if token in self.etre_forms:
                    continue
                
                # 检查这个动词前面是否有反身代词
                for k in range(j - 1, max(0, j - 4) - 1, -1):
                    if k < 0:
                        break
                    prev_token = tokens[k].lower()
                    
                    if prev_token in self.etre_forms or prev_token in ['ne', "n'", 'pas', 'plus', 'jamais']:
                        continue
                    
                    if prev_token in self.reflexive:
                        # 找到了代词式动词组，检查反身代词是否匹配
                        if self._are_same_pronoun_group(prev_token, current_pronoun):
                            return "matched_reflexive"
                        else:
                            return None
                    
                    break
                
                # 如果动词前面没有反身代词，继续向前查找
                continue
        
        return None
    
    def _find_subject(self, tokens: List[str], pronoun_index: int) -> str:
        current_pronoun = tokens[pronoun_index].lower()
        
        # 如果是 se/s'，不需要检查主语，直接返回特殊标记
        if current_pronoun in ['se', "s'"]:
            return "se_pronoun"
        
        # 检查反身代词前面是否有逗号或 ', et'
        allow_cross_comma = False
        if pronoun_index > 0 and tokens[pronoun_index - 1] == ',':
            allow_cross_comma = True
        elif pronoun_index > 1 and tokens[pronoun_index - 1].lower() == 'et' and tokens[pronoun_index - 2] == ',':
            allow_cross_comma = True
        
        # 如果允许跨越逗号，使用新的查找逻辑
        if allow_cross_comma:
            return self._find_subject_or_reflexive_across_comma(tokens, pronoun_index, current_pronoun)
        
        # 原有的查找逻辑（不跨逗号）
        for j in range(pronoun_index - 1, -1, -1):
            token = tokens[j].lower()
            
            # ====== 新增：检查多词主语（优先检查）======
            if j > 0:
                two_word_subject = f"{tokens[j-1].lower()} {token}"
                
                if two_word_subject in self.multi_word_subjects:
                    # 检查前面是否有介词（避免"pour son but"这种情况）
                    if j > 1 and tokens[j-2].lower() in self.prepositions:
                        pass  # 跳过，继续查找
                    else:
                        if current_pronoun in self.multi_word_subjects[two_word_subject]:
                            return two_word_subject
                        else:
                            return None
            # ====== 新增结束 ======
            
            if token in self.subjects:
                if j > 0 and tokens[j-1].lower() in self.prepositions:
                    continue
                
                if current_pronoun in self.subjects[token]:
                    return token
                else:
                    return None
            
            if token == 'en':
                continue
            
            # 不允许跨逗号时，遇到逗号就停止
            if token in self.stop_tokens or token == ',':
                break
            
            if token in self.reflexive:
                continue
            
            if token in self.reverse_index:
                continue
            
            if pronoun_index - j > 15:
                break
        
        return None

    def _find_subject_cross_comma(self, tokens: List[str], pronoun_index: int, current_pronoun: str) -> str:
        """保留用于现在分词的查找逻辑"""
        for j in range(pronoun_index - 1, -1, -1):
            token = tokens[j].lower()
            
            if token in self.subjects:
                if j > 0 and tokens[j-1].lower() in self.prepositions:
                    continue
                
                if current_pronoun in self.subjects[token]:
                    return token
                else:
                    return None
            
            if token == 'en':
                continue
            
            if token == ',':
                continue
            
            if token == 'et' and j > 0 and tokens[j - 1] == ',':
                return None
            
            if token in self.stop_tokens:
                break
            
            if token in self.reflexive:
                continue
            
            if token in self.reverse_index:
                continue
            
            if pronoun_index - j > 15:
                break
        
        return None

    def _is_present_participle(self, verb_form: str, possible_infinitives: List[str]) -> bool:
        return verb_form.endswith('ant')
    
    def _find_subject_forward(self, tokens: List[str], start_pos: int) -> str:
        end_pos = min(len(tokens), start_pos + 15)
        
        for j in range(start_pos + 1, end_pos):
            token = tokens[j].lower()
            
            if token in self.subjects:
                if j > 0 and tokens[j-1].lower() in self.prepositions:
                    continue
                return token
            
            if token in self.stop_tokens:
                break
            
            if token == ',':
                continue
            
            continue
        
        return None
    
    def _find_subject_or_reflexive(self, tokens: List[str], pronoun_index: int, current_pronoun: str, ignore_stop_tokens: bool = True) -> bool:
        # 如果是 se/s'，不需要检查主语
        if current_pronoun in ['se', "s'"]:
            return True
        
        for j in range(pronoun_index - 1, max(0, pronoun_index - 15) - 1, -1):
            if j < 0:
                break
                
            token = tokens[j].lower()
            
            # ====== 新增：检查多词主语（在所有检查之前）======
            if j > 0:
                two_word_subject = f"{tokens[j-1].lower()} {token}"
                
                if two_word_subject in self.multi_word_subjects:
                    # 检查前面是否有介词
                    if j > 1 and tokens[j-2].lower() in self.prepositions:
                        pass  # 跳过
                    else:
                        # 找到多词主语，检查是否匹配
                        if current_pronoun in self.multi_word_subjects[two_word_subject]:
                            return True
                        else:
                            return False
            # ====== 新增结束 ======
            
            if token in self.reflexive:
                if token == current_pronoun or self._are_same_pronoun_group(token, current_pronoun):
                    return True
                else:
                    return False
            
            if token in self.subjects:
                if j > 0 and tokens[j-1].lower() in self.prepositions:
                    continue
                
                if current_pronoun in self.subjects[token]:
                    return True
                else:
                    return False
            
            if token == 'en':
                continue
            
            if token == ',':
                continue
            
            if token in self.prepositions:
                continue
            
            if token in self.skip_adj_prep:
                continue
            
            if not ignore_stop_tokens:
                if token == 'et' and j > 0 and tokens[j - 1] == ',':
                    return False
            
            if not ignore_stop_tokens:
                if token in self.stop_tokens:
                    break
            
            if token in self.reverse_index:
                if token in self.etre_forms:
                    continue
                
                has_reflexive_before = False
                reflexive_before = None
                for k in range(j - 1, max(0, j - 4) - 1, -1):
                    if k < 0:
                        break
                    prev_token = tokens[k].lower()
                    
                    if prev_token in self.etre_forms or prev_token in ['ne', "n'", 'pas', 'plus', 'jamais']:
                        continue
                    
                    if prev_token in self.reflexive:
                        has_reflexive_before = True
                        reflexive_before = prev_token
                        break
                    
                    break
                
                if has_reflexive_before:
                    if self._are_same_pronoun_group(reflexive_before, current_pronoun):
                        return True
                    else:
                        return False
                
                continue
            
            continue
        
        return False
    
    def detect(self, text: str) -> List[str]:
        tokens = self.tokenize(text)
        results = []
        
        for i, token in enumerate(tokens):
            word = token.lower()
            
            if word in {'.', '!', '?', ';', ':', ','}:
                continue
            
            if word in self.reflexive:
                verb_pos, verb = self._find_verb_after_pronoun(tokens, i, max_lookforward=4)
                
                if verb_pos is None or verb in self.etre_forms:
                    continue
                
                if not self._check_nearby_verb_for_se(tokens, i, max_lookback=3):
                    continue
                
                if verb in self.reverse_index:
                    possible_infinitives = self.reverse_index[verb]
                else:
                    if verb.startswith('re') and len(verb) > 2:
                        verb_without_re = verb[2:]
                        if verb_without_re in self.reverse_index:
                            base_infinitives = self.reverse_index[verb_without_re]
                            possible_infinitives = ['re' + inf for inf in base_infinitives]
                        else:
                            possible_infinitives = [verb]
                    else:
                        possible_infinitives = [verb]
                
                is_present_participle = self._is_present_participle(verb, possible_infinitives)
                is_infinitive = self._is_verb_infinitive(verb)
                
                prepositions_short = {'à', 'de', 'pour', 'sans', 'après', 'avant', "d'"}
                
                # ====== 修改这里：向前查找介词，跳过否定词 ======
                has_preposition_before = False
                negation_words = {'ne', "n'", 'pas', 'plus', 'jamais', 'rien', 'point', 'guère'}
                
                # 向前查找最多4个位置，寻找介词
                for look_back in range(1, min(5, i + 1)):
                    if i - look_back < 0:
                        break
                    prev_token = tokens[i - look_back].lower()
                    
                    if prev_token in prepositions_short:
                        has_preposition_before = True
                        break
                    elif prev_token in negation_words:
                        # 跳过否定词，继续向前查找
                        continue
                    else:
                        # 遇到其他词，停止查找
                        break
                # ====== 修改结束 ======
                
                has_verb_before = False
                if i > 0 and not has_preposition_before:
                    prev_token = tokens[i-1].lower()
                    if prev_token in self.reverse_index and prev_token not in self.etre_forms:
                        has_verb_before = True
                
                is_en_participle = (i > 0 and tokens[i-1].lower() == 'en' and is_present_participle)
                is_prep_or_verb_infinitive = ((has_preposition_before or has_verb_before) and is_infinitive)
                
                should_skip = False
                
                if word in ['se', "s'"]:
                    if is_en_participle:
                        pass
                    elif is_prep_or_verb_infinitive:
                        pass
                    else:
                        pass
                else:
                    if is_en_participle:
                        pass
                    elif is_prep_or_verb_infinitive:
                        if not self._find_subject_or_reflexive(tokens, i, word, ignore_stop_tokens=True):
                            should_skip = True
                    else:
                        subject_result = self._find_subject(tokens, i)
                        
                        if subject_result is None:
                            should_skip = True
                        elif subject_result in ["matched_reflexive", "se_pronoun"]:
                            pass
                        else:
                            if word not in self.subjects.get(subject_result, []):
                                should_skip = True
                
                if should_skip:
                    continue
                
                for infinitive in possible_infinitives:
                    if self.is_pronominal_verb(infinitive):
                        results.append(f'se {infinitive}')
                        break
        
        return results


def check_pronominal_verbs(items: List[str], min_count: int, max_count: int) -> Tuple[bool, str]:
    detector = PronominalVerbDetector()
    results = []
    all_valid = True
    
    absolute_blacklist = {
        'être', 'devenir', 'paraître', 'sembler', 'rester', 'demeurer',
        'pleuvoir', 'neiger', 'geler', 'grêler', 'falloir',
        'naître', 'exister', 'dormir', 'venir', 'arriver', 'partir', 'entrer'
    }
    
    for i, item in enumerate(items, 1):
        verbs = detector.detect(item)
        
        filtered_verbs = []
        for verb in verbs:
            infinitive = verb.replace('se ', '').replace("s'", '').strip()
            if infinitive not in absolute_blacklist:
                filtered_verbs.append(verb)
        
        verbs = filtered_verbs
        count = len(verbs)
        
        is_valid = min_count <= count <= max_count
        if not is_valid:
            all_valid = False
        
        verb_counts = Counter(verbs)
        
        seen = set()
        unique_verbs = []
        for verb in verbs:
            if verb not in seen:
                unique_verbs.append(verb)
                seen.add(verb)
        
        result_line = f"第{i}项: 代词式动词{count}个"
        if verbs:
            result_line += ":\n"
            for verb in unique_verbs:
                verb_count = verb_counts[verb]
                if verb_count > 1:
                    result_line += f"  {verb} ({verb_count}次)\n"
                else:
                    result_line += f"  {verb}\n"
            result_line = result_line.rstrip()
        else:
            result_line += ": 无"
        
        results.append(result_line)
    
    if all_valid:
        header = f"✅ 所有项代词式动词数量都正确（要求{min_count}-{max_count}个）\n"
    else:
        header = f"❌ 部分项代词式动词数量不符合要求（要求{min_count}-{max_count}个）\n"
    
    explanation = header + "\n".join(results)
    
    return all_valid, explanation

##############################部分冠词##############################

class DELADictionary:
    """DELA 法语词典解析器"""
    
    def __init__(self, silent=True):
        self.dict_path = self._find_dict_path()
        self.entries = defaultdict(list)
        self.lemmas = defaultdict(set)
        self.silent = silent
        
        if self.dict_path:
            if not self.silent:
                print(f"📖 正在加载词典...")
            self._load_dictionary()
            if not self.silent:
                print(f"✅ 加载完成: {len(self.entries)} 个词形\n")
    
    def _find_dict_path(self):
        base_path = os.path.join(sys.prefix, 'share', 'dict')
        dict_file = os.path.join(base_path, 'dict-fr-AU-DELA')
        return dict_file if os.path.exists(dict_file) else None
    
    def _parse_entry(self, line):
        line = line.strip().replace('\\-', '-')
        if not line or line.startswith('#'):
            return None
        
        match = re.match(r'^([^,]+),([^.]+)\.([^:+]+)([\+:].*)?$', line)
        if match:
            return {
                'inflected': match.group(1),
                'lemma': match.group(2),
                'pos': match.group(3),
                'features': match.group(4) if match.group(4) else ''
            }
        
        match = re.match(r'^([^,]+),\.([^:+]+)([\+:].*)?$', line)
        if match:
            return {
                'inflected': match.group(1),
                'lemma': match.group(1),
                'pos': match.group(2),
                'features': match.group(3) if match.group(3) else ''
            }
        
        return None
    
    def _load_dictionary(self):
        with open(self.dict_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self._parse_entry(line)
                if entry:
                    inflected = entry['inflected'].lower()
                    lemma = entry['lemma'].lower()
                    self.entries[inflected].append(entry)
                    self.lemmas[lemma].add(inflected)
    
    def lookup(self, word):
        """查找词条（word已经是小写）"""
        return self.entries.get(word, [])
    
    def is_noun(self, word):
        """判断是否是名词（word已经是小写）"""
        return any(e['pos'] == 'N' for e in self.lookup(word))
    
    def is_plural(self, word):
        """判断是否是复数（word已经是小写）"""
        entries = self.lookup(word)
        for e in entries:
            if e['pos'] == 'N' and re.search(r':?[mf]p', e['features']):
                return True
        return False


class PartitiveArticleDetector:
    """法语部分冠词检测器（增强未知词处理版）"""
    
    def __init__(self, verbcc_index_path='verb_index_optimized.json'):
        self.dela = DELADictionary(silent=True)
        self.verbcc = VerbccIndex(verbcc_index_path)
        
        self.partitive_forms = ['du', 'de la', "de l'"]
        
        self.verb_de_infinitives = {
            'parler', 'venir', 'cesser', 'finir', 'essayer', 'décider',
            'oublier', 'refuser', 'accepter', 'rêver', 'manquer', 'profiter',
            'occuper', 'servir', 'souvenir', 'remercier', 'féliciter',
            'moquer', 'apercevoir', 'approcher', 'éloigner', 'passer',
            'méfier', 'douter', 'plaindre', 'dépendre',
        }
        
        self.adj_de_list = {
            'content', 'contente', 'contents', 'contentes',
            'fier', 'fière', 'fiers', 'fières',
            'heureux', 'heureuse', 'heureuses',
            'capable', 'capables',
            'sûr', 'sûre', 'sûrs', 'sûres',
            'certain', 'certaine', 'certains', 'certaines',
            'désolé', 'désolée', 'désolés', 'désolées',
            'ravi', 'ravie', 'ravis', 'ravies',
        }
        
        self.avoir_etre_phrases = {
            'besoin', 'envie', 'peur', 'honte', "l'habitude", "l'intention",
            'le temps', 'la chance', 'tort', 'raison',
        }
        
        self.de_phrase_triggers = {
            'côté', 'près', 'loin', 'autour', 'face', 
            'cause', 'lieu', 'suite', 'propos',
            'milieu', 'haut', 'bas', 'intérieur', 'extérieur',
        }
        
        self.de_fixed_phrase_patterns = [
            ['part', 'la', 'de'],
            ['nom', 'au'],
            ['faveur', 'en'],
            ['cause', 'à'],
            ['sujet', 'au'],
            ['fin', 'la', 'à'],
            ['début', 'au'],
            ['cours', 'au'],
            ['lieu', 'au'],
            ['place', 'la', 'à'],
            ['encontre', "l'", 'à'],
            ['égard', "l'", 'à'],
            ['sein', 'au'],
            ['profit', 'au'],
            ['détriment', 'au'],
            ['face', 'en'],
            ['côté', 'à'],
            ['au-dessus'],
            ['au-dessous'],
            ['dehors', 'en'],
            ['intérieur', "l'", 'à'],
            ['extérieur', "l'", 'à'],
            ['autour'],
            ['près'],
            ['loin'],
            ['propos', 'à'],
            ['travers', 'à'],
            ['milieu', 'au'],
            ['centre', 'au'],
            ['raison', 'en'],
            ['fonction', 'en'],
            ['termes', 'en'],
            ['niveau', 'au'],
            ['matière', 'en'],
            ['aide', "l'", 'à'],
            ['partir', 'à'],
        ]
        
        self.prepositions_with_partitive = {
            'avec', 'dans', 'sans', 'pour', 'par', 'entre', 'parmi',
        }
        
        self.prepositions_without_partitive = {
            'sur', 'sous', 'contre', 'vers', 'chez', 'pendant', 'durant',
        }
        
        self.conjunctions = {'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car'}
        
        self.negation_words = {
            'ne', "n'", 'pas', 'plus', 'jamais', 'rien', 'guère', 'point',
            'personne', 'aucun', 'aucune', 'nullement',
        }
        
        self.skip_words = {
            'y', 'en', 'me', "m'", 'te', "t'", 'se', "s'",
            'lui', 'leur', 'nous', 'vous',
        }
    
    def tokenize(self, sentence: str) -> List[str]:
        """分词并统一转小写"""
        sentence = sentence.replace(''', "'")
        sentence = sentence.replace(''', "'")
        sentence = sentence.replace('`', "'")
        
        sentence = re.sub(
            r"(?<=\s)([ldcjmntsLDCJMNTS])'([aeiouyhàâäéèêëïîôùûüÿœæAEIOUYHÀÂÄÉÈÊËÏÎÔÙÛÜŸŒÆ])",
            r"\1' \2",
            sentence
        )
        
        sentence = re.sub(
            r"^([ldcjmntsLDCJMNTS])'([aeiouyhàâäéèêëïîôùûüÿœæAEIOUYHÀÂÄÉÈÊËÏÎÔÙÛÜŸŒÆ])",
            r"\1' \2",
            sentence
        )
        
        sentence = re.sub(r'([,;:!?.…])', r' \1 ', sentence)
        
        tokens = sentence.lower().split()
        
        return tokens
    
    def _mark_fixed_phrase_positions(self, tokens: List[str]) -> set:
        """标记固定短语区域（tokens已经是小写）"""
        skip_positions = set()
        
        for i in range(len(tokens)):
            for pattern in self.de_fixed_phrase_patterns:
                reversed_pattern = list(reversed(pattern))
                
                match = True
                for j, required_word in enumerate(reversed_pattern):
                    if i + j >= len(tokens):
                        match = False
                        break
                    if tokens[i + j].rstrip('.,;:!?') != required_word:
                        match = False
                        break
                
                if match:
                    for j in range(len(reversed_pattern)):
                        skip_positions.add(i + j)
                    
                    next_pos = i + len(reversed_pattern)
                    if next_pos < len(tokens) and tokens[next_pos] in ['de', 'du', "d'"]:
                        skip_positions.add(next_pos)
                        if tokens[next_pos] == 'de' and next_pos + 1 < len(tokens):
                            if tokens[next_pos + 1] in ['la', "l'", 'les']:
                                skip_positions.add(next_pos + 1)
        
        return skip_positions
    
    def _looks_like_plural_noun(self, word: str) -> bool:
        """判断词形是否像复数名词"""
        # 以 -s, -x, -aux 结尾
        return (word.endswith('s') or word.endswith('x') or word.endswith('aux'))
    
    def _is_plural_article(self, word: str) -> bool:
        """判断是否是复数冠词"""
        return word in ['les', 'des']
    
    def _infer_noun_from_context(self, tokens: List[str], position: int) -> bool:
        """⭐⭐⭐ 通过上下文推断未知词是否是名词"""
        word = tokens[position].rstrip('.,;:!?')
        
        # 1. 检查词形
        if not self._looks_like_plural_noun(word):
            return False
        
        # 2. 检查前面是否有复数冠词
        if position > 0:
            prev_word = tokens[position - 1].rstrip('.,;:!?')
            if self._is_plural_article(prev_word):
                return True
        
        # 3. 检查前面两个词（可能是：冠词 + 形容词 + 名词）
        if position > 1:
            prev_prev_word = tokens[position - 2].rstrip('.,;:!?')
            if self._is_plural_article(prev_prev_word):
                # 检查中间的词是否是形容词
                prev_word = tokens[position - 1].rstrip('.,;:!?')
                prev_entries = self.dela.lookup(prev_word)
                is_adj = any(e['pos'] == 'A' for e in prev_entries)
                if is_adj:
                    return True
        
        return False
    
    def _is_noun_before(self, tokens: List[str], position: int) -> bool:
        """检查 de/du/de la/de l' 前面是否有名词（增强版）"""
        adj_count = 0
        found_comma = False
        
        for j in range(position - 1, max(0, position - 10) - 1, -1):
            if j < 0:
                break
            
            token = tokens[j]
            token_clean = token.rstrip('.,;:!?')
            
            if token in self.skip_words:
                continue
            
            if token in [':', '—', '«', '»', '"', '"', '(', ')']:
                continue
            
            if token == ',':
                found_comma = True
                continue
            
            if token in ['.', '!', '?', '...', ';']:
                return False
            
            # 并列连词检测
            if token in self.conjunctions:
                found_noun_de_structure = False
                
                for k in range(j - 1, max(0, j - 6) - 1, -1):
                    if k < 0:
                        break
                    
                    prev_token = tokens[k]
                    
                    is_partitive = False
                    search_start_pos = k
                    
                    if prev_token in ['du', "d'"]:
                        is_partitive = True
                        search_start_pos = k
                    elif prev_token == 'de':
                        if k + 1 < len(tokens):
                            next_after_de = tokens[k + 1]
                            if next_after_de in ['la', "l'"]:
                                is_partitive = True
                                search_start_pos = k
                    
                    if is_partitive:
                        for m in range(search_start_pos - 1, max(0, search_start_pos - 5) - 1, -1):
                            if m < 0:
                                break
                            
                            before_de = tokens[m].rstrip('.,;:!?')
                            
                            if before_de in ['le', 'la', "l'", 'les', 'un', 'une', 'des', 'du']:
                                continue
                            
                            before_entries = self.dela.lookup(before_de)
                            is_before_noun = any(e['pos'] == 'N' for e in before_entries)
                            is_before_verb = self.verbcc.is_verb(before_de) if self.verbcc.reverse_index else any(e['pos'] == 'V' for e in before_entries)
                            is_before_adj = any(e['pos'] == 'A' for e in before_entries)
                            
                            # ⭐⭐⭐ 未知词推断
                            if not before_entries and not is_before_verb:
                                is_before_noun = self._infer_noun_from_context(tokens, m)
                            
                            if is_before_adj and not is_before_noun:
                                continue
                            
                            if is_before_noun and is_before_verb:
                                if m > 0:
                                    article_check = tokens[m - 1].rstrip('.,;:!?')
                                    if article_check in ['le', 'la', "l'", 'les', 'une', 'un', 'des']:
                                        found_noun_de_structure = True
                                        break
                                continue
                            
                            if is_before_noun and not is_before_verb:
                                found_noun_de_structure = True
                                break
                            
                            break
                        
                        break
                
                if found_noun_de_structure:
                    return True
                
                if adj_count > 0:
                    continue
                else:
                    return False
            
            if token_clean in self.prepositions_without_partitive:
                continue
            
            if token_clean in self.prepositions_with_partitive:
                return False
            
            # 冠词后的词
            if token_clean in ['le', 'la', "l'", 'les', 'un', 'une', 'des', 'du']:
                if j + 1 < len(tokens):
                    next_token = tokens[j + 1].rstrip('.,;:!?')
                    entries = self.dela.lookup(next_token)
                    
                    is_noun = any(e['pos'] == 'N' for e in entries)
                    
                    # ⭐⭐⭐ 未知词推断
                    if not is_noun and not entries:
                        is_noun = self._infer_noun_from_context(tokens, j + 1)
                    
                    if is_noun:
                        if found_comma:
                            return False
                        return True
                    
                    is_adj = any(e['pos'] == 'A' for e in entries)
                    if is_adj and j + 2 < len(tokens):
                        next_next_token = tokens[j + 2].rstrip('.,;:!?')
                        next_next_entries = self.dela.lookup(next_next_token)
                        is_noun_2 = any(e['pos'] == 'N' for e in next_next_entries)
                        
                        # ⭐⭐⭐ 未知词推断
                        if not is_noun_2 and not next_next_entries:
                            is_noun_2 = self._infer_noun_from_context(tokens, j + 2)
                        
                        if is_noun_2:
                            if found_comma:
                                return False
                            return True
                    
                    is_verb = self.verbcc.is_verb(next_token) if self.verbcc.reverse_index else any(e['pos'] == 'V' for e in entries)
                    if is_verb:
                        return False
                
                continue
            
            entries = self.dela.lookup(token_clean)
            
            is_noun = any(e['pos'] == 'N' for e in entries)
            is_adj = any(e['pos'] == 'A' for e in entries)
            
            if self.verbcc.reverse_index:
                is_verb = self.verbcc.is_verb(token_clean)
            else:
                is_verb = any(e['pos'] == 'V' for e in entries)
            
            # ⭐⭐⭐ 未知词处理（增强版）
            if not entries and not is_verb:
                # 连字符词当作形容词
                if '-' in token_clean:
                    adj_count += 1
                    if adj_count > 3:
                        return False
                    continue
                
                # 尝试通过上下文推断是否是名词
                is_noun = self._infer_noun_from_context(tokens, j)
                if is_noun:
                    if found_comma:
                        return False
                    return True
                
                # 其他未知词跳过
                continue
            
            # 形容词（非名词）
            if is_adj and not is_noun:
                adj_count += 1
                if adj_count > 3:
                    return False
                continue
            
            # 名词+动词歧义
            if is_noun and is_verb:
                if j > 0:
                    prev_token = tokens[j - 1].rstrip('.,;:!?')
                    
                    if prev_token in ['le', 'la', "l'", 'les', 'un', 'une', 'des', 'du', 'cette', 'ce', 'cet', 'ces']:
                        if found_comma:
                            return False
                        return True
                    
                    prev_entries = self.dela.lookup(prev_token)
                    is_prev_adj = any(e['pos'] == 'A' for e in prev_entries)
                    
                    if is_prev_adj:
                        if j > 1:
                            prev_prev_token = tokens[j - 2].rstrip('.,;:!?')
                            
                            if prev_prev_token in ['le', 'la', "l'", 'les', 'un', 'une', 'des', 'du', 'cette', 'ce', 'cet', 'ces']:
                                if found_comma:
                                    return False
                                return True
                
                if found_comma:
                    return True
                
                return False
            
            # 纯动词
            if is_verb:
                if found_comma:
                    return True
                return False
            
            # 纯名词
            if is_noun:
                if found_comma:
                    return False
                return True
            
            return False
        
        return False
    
    def _is_verb_de_expression(self, verb_token: str) -> bool:
        """判断动词是否接 de（verb_token已经是小写）"""
        if self.verbcc.reverse_index:
            infinitives = self.verbcc.get_infinitives(verb_token)
            for inf in infinitives:
                if inf in self.verb_de_infinitives:
                    return True
        
        entries = self.dela.lookup(verb_token)
        for entry in entries:
            if entry['pos'] == 'V':
                lemma = entry['lemma'].lower()
                if lemma in self.verb_de_infinitives:
                    return True
        
        return False
    
    def _is_at_sentence_start(self, tokens: List[str], position: int) -> bool:
        """判断是否在句首（tokens已经是小写）"""
        if position == 0:
            return True
        
        for j in range(position - 1, -1, -1):
            token = tokens[j]
            
            if token in ['.', '!', '?', '...', ';']:
                return True
            
            if token in self.conjunctions:
                return True
            
            if token not in [',', ':', '—', '«', '»', '"', '"', '(', ')']:
                return False
        
        return True
    
    def _is_in_negation(self, tokens: List[str], position: int) -> bool:
        """判断是否在否定句中（tokens已经是小写）"""
        found_ne = False
        
        for j in range(position - 1, max(0, position - 8) - 1, -1):
            if j < 0:
                break
            
            token = tokens[j]
            
            if token in self.skip_words:
                continue
            
            if token in [',', ':', '—', '«', '»', '"', '"', '(', ')']:
                continue
            
            if token in ['.', '!', '?', '...', ';']:
                return False
            
            if token in self.conjunctions:
                return False
            
            if token in ['ne', "n'"]:
                found_ne = True
                continue
            
            if token in self.negation_words and token not in ['ne', "n'"]:
                if found_ne:
                    return True
                continue
            
            is_verb = self.verbcc.is_verb(token) if self.verbcc.reverse_index else any(e['pos'] == 'V' for e in self.dela.lookup(token))
            
            if is_verb:
                if found_ne:
                    return True
                return False
            
            if not found_ne:
                return False
        
        return False
    
    def _is_partitive_de_in_negation(self, tokens: List[str], position: int) -> bool:
        """判断否定句中的 de 是否是部分冠词（tokens已经是小写）"""
        if position + 1 >= len(tokens):
            return False
        
        next_token = tokens[position + 1]
        
        if next_token == "l'":
            if position + 2 >= len(tokens):
                return False
            next_word = tokens[position + 2].rstrip('.,;:!?')
        else:
            next_word = next_token.rstrip('.,;:!?')
        
        return self.dela.is_noun(next_word)
    
    def _is_verb_de_before(self, tokens: List[str], position: int) -> bool:
        """判断前面是否有接 de 的动词（tokens已经是小写）"""
        for j in range(position - 1, max(0, position - 5) - 1, -1):
            if j < 0:
                break
            
            token = tokens[j]
            
            if token in self.skip_words or token in [',', ':', '—', '«', '»', '"', '"']:
                continue
            
            if token in ['.', '!', '?', ';']:
                return False
            
            if self._is_verb_de_expression(token):
                return True
            
            if token in self.adj_de_list:
                return True
            
            if token in self.avoir_etre_phrases:
                return True
            
            return False
        
        return False
    
    def detect(self, text: str) -> List[Tuple[str, str]]:
        """检测部分冠词（入口方法）"""
        tokens = self.tokenize(text)
        
        skip_positions = self._mark_fixed_phrase_positions(tokens)
        
        results = []
        
        i = 0
        while i < len(tokens):
            if i in skip_positions:
                i += 1
                continue
            
            token = tokens[i]
            
            if token == 'du':
                if self._is_noun_before(tokens, i):
                    i += 1
                    continue
                
                if self._is_verb_de_before(tokens, i):
                    i += 1
                    continue
                
                next_word = tokens[i + 1] if i + 1 < len(tokens) else ""
                results.append((token, next_word))
                i += 1
            
            elif token == 'de' and i + 1 < len(tokens):
                next_token = tokens[i + 1]
                
                if next_token in ['la', "l'"]:
                    article = f"de {next_token}"
                    
                    if self._is_noun_before(tokens, i):
                        i += 2
                        continue
                    
                    noun_pos = i + 2
                    if noun_pos < len(tokens):
                        following_word_clean = tokens[noun_pos].rstrip('.,;:!?')
                        
                        should_add = False
                        
                        if self.dela.is_noun(following_word_clean):
                            should_add = True
                        elif '-' in tokens[noun_pos] or "d'" in tokens[noun_pos]:
                            should_add = True
                        
                        if should_add and not self._is_verb_de_before(tokens, i):
                            results.append((article, tokens[noun_pos]))
                    
                    i += 2
                
                elif self._is_in_negation(tokens, i):
                    if self._is_partitive_de_in_negation(tokens, i):
                        next_word = tokens[i + 1]
                        if next_word == "l'":
                            article = "de l'"
                            following_word = tokens[i + 2] if i + 2 < len(tokens) else ""
                            results.append((article, following_word))
                            i += 2
                        else:
                            results.append(("de", next_word))
                            i += 1
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return results
    
    def count_partitive_articles(self, text: str) -> int:
        """统计部分冠词数量"""
        return len(self.detect(text))


def check_partitive_articles(items: List[str], min_count: int, max_count: int) -> Tuple[bool, str]:
    """批量检查部分冠词"""
    detector = PartitiveArticleDetector()
    results = []
    all_valid = True
    
    for i, item in enumerate(items, 1):
        articles_with_context = detector.detect(item)
        count = len(articles_with_context)
        
        is_valid = min_count <= count <= max_count
        if not is_valid:
            all_valid = False
        
        result_line = f"第{i}项: 部分冠词{count}个"
        if articles_with_context:
            result_line += ":\n"
            for article, next_word in articles_with_context:
                context = f"{article} {next_word}".strip()
                result_line += f"  在「{context}」中发现「{article}」\n"
            result_line = result_line.rstrip()
        else:
            result_line += ": 无"
        
        results.append(result_line)
    
    if all_valid:
        header = f"✅ 所有项部分冠词数量都正确（要求{min_count}-{max_count}个）\n"
    else:
        header = f"❌ 部分项部分冠词数量不符合要求（要求{min_count}-{max_count}个）\n"
    
    explanation = header + "\n".join(results)
    
    return all_valid, explanation

#########################复合过去时#################################################
class PasseComposeDetector:
    """法语复合过去时检测器"""
    
    def __init__(self):
        self.cg = Conjugator(lang='fr')
        
        # avoir 的直陈式现在时变位
        self.avoir_present = {
            'ai', 'as', 'a', 'avons', 'avez', 'ont'
        }
        
        # être 的直陈式现在时变位
        self.etre_present = {
            'suis', 'es', 'est', 'sommes', 'êtes', 'sont'
        }
        
        # 获取所有être的变位形式（用于排除）
        self.all_etre_forms = self._get_etre_forms()
        
        # 加载或构建过去分词索引
        self.participe_index_file = Path('participe_index.json')
        self.participe_index = self._load_or_build_participe_index()
    
    def _get_etre_forms(self) -> Set[str]:
        """获取être的所有变位形式"""
        etre_forms = set()
        try:
            result = self.cg.conjugate('être')
            for mood_data in result['moods'].values():
                for forms in mood_data.values():
                    if isinstance(forms, list):
                        for form in forms:
                            if isinstance(form, str):
                                parts = form.split()
                                verb_part = parts[-1] if parts else form
                                verb_part = verb_part.lower().strip()
                                if verb_part:
                                    etre_forms.add(verb_part)
        except:
            pass
        return etre_forms
    
    def _load_or_build_participe_index(self) -> Dict[str, List[str]]:
        """加载或构建过去分词索引"""
        if self.participe_index_file.exists():
            with open(self.participe_index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            index = self._build_participe_index()
            with open(self.participe_index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            return index
    
    def _build_participe_index(self) -> Dict[str, List[str]]:
        """构建过去分词索引：过去分词形式 -> 原形动词列表"""
        all_infinitives = self.cg.get_infinitives()
        
        # 清理动词原形（去掉 se/s'）
        base_verbs = []
        for inf in all_infinitives:
            cleaned = re.sub(r'^se\s+', '', inf)
            cleaned = re.sub(r"^s'\s*", '', cleaned)
            base_verbs.append(cleaned)
        
        base_verbs = list(set(base_verbs))
        participe_index = {}
        
        print(f"正在构建过去分词索引，共 {len(base_verbs)} 个动词...")
        
        for i, infinitive in enumerate(base_verbs):
            if (i + 1) % 500 == 0:
                print(f"进度: {i + 1}/{len(base_verbs)}")
            
            try:
                result = self.cg.conjugate(infinitive)
                
                # 获取过去分词
                if 'participe' in result['moods'] and 'participe-passé' in result['moods']['participe']:
                    participes = result['moods']['participe']['participe-passé']
                    
                    for participe in participes:
                        participe = participe.lower().strip()
                        if participe:
                            if participe not in participe_index:
                                participe_index[participe] = []
                            if infinitive not in participe_index[participe]:
                                participe_index[participe].append(infinitive)
            except:
                pass
        
        print("过去分词索引构建完成！")
        return participe_index
    
    def tokenize(self, sentence: str) -> List[str]:
        """分词"""
        # 统一撇号格式
        sentence = sentence.replace(''', "'")
        sentence = sentence.replace(''', "'")
        
        # 为标点符号添加空格
        sentence = re.sub(r'([.?!;:,])', r' \1 ', sentence)
        sentence = re.sub(r"'([a-zA-Zàâäéèêëïîôùûüÿœæç])", r"' \1", sentence)
        
        # 分词
        tokens = []
        for t in sentence.split():
            if t:
                tokens.append(t)
        return tokens
    
    def detect(self, text: str, required_auxiliary: str) -> List[Tuple[str, str, str, str]]:
        """
        检测文本中的复合过去时
        
        参数:
            text: 待检测的法语文本
            required_auxiliary: 要求的助动词 'avoir' 或 'être'
        
        返回:
            List[Tuple[助动词类型, 助动词变位, 过去分词完整形式, 原形动词]]
        """
        tokens = self.tokenize(text)
        results = []
        
        for i, token in enumerate(tokens):
            word = token.lower()
            
            # 跳过标点符号
            if word in {'.', '!', '?', ';', ':', ','}:
                continue
            
            # 检查是否是助动词（avoir 或 être 的现在时变位）
            auxiliary_type = None
            auxiliary_form = word  # 保存助动词的实际变位形式
            
            if word in self.avoir_present:
                auxiliary_type = 'avoir'
            elif word in self.etre_present:
                auxiliary_type = 'être'
            
            if auxiliary_type is None:
                continue
            
            # 向后查找过去分词（最多查找5个词，因为可能有 été 在中间）
            participe_parts = []  # 用于保存完整的过去分词形式（可能包含 été）
            
            for j in range(i + 1, min(len(tokens), i + 6)):
                next_token = tokens[j].lower()
                
                # 跳过标点符号
                if next_token in {'.', '!', '?', ';', ':', ','}:
                    break
                
                # 跳过否定词和副词
                if next_token in {'ne', "n'", 'pas', 'plus', 'jamais', 'rien', 'déjà', 'encore', 'toujours'}:
                    continue
                
                # 检查是否是 été（可能是被动态标志）
                if next_token == 'été':
                    participe_parts.append(next_token)
                    continue
                
                # 检查是否是过去分词
                if next_token in self.participe_index:
                    infinitives = self.participe_index[next_token]
                    
                    # 如果已经收集了 été，这是被动态的复合过去时
                    if 'été' in participe_parts:
                        # 被动态：avoir/être + été + 过去分词
                        # 例如: "ai été invité" (inviter的被动语态复合过去时)
                        participe_parts.append(next_token)
                        full_participe = ' '.join(participe_parts)
                        
                        # 对于被动态，原形动词就是最后那个过去分词对应的动词
                        if infinitives:
                            infinitive = infinitives[0]
                            # 排除 être 本身
                            if infinitive != 'être':
                                results.append((auxiliary_type, auxiliary_form, full_participe, infinitive))
                        break
                    else:
                        # 普通复合过去时
                        # 例如: "ai mangé" (manger的复合过去时)
                        infinitives = [inf for inf in infinitives if inf != 'être']
                        
                        if infinitives:
                            infinitive = infinitives[0]
                            results.append((auxiliary_type, auxiliary_form, next_token, infinitive))
                        break
                else:
                    # 遇到非过去分词的词
                    if participe_parts:
                        # 如果已经有 été 但后面不是过去分词，这是 être 的复合过去时
                        # 例如: "ai été témoin", "ai été content"
                        results.append((auxiliary_type, auxiliary_form, 'été', 'être'))
                        break
                    # 遇到非过去分词的词，停止查找
                    break
        
        return results


def check_passe_compose_auxiliary(items: List[str], auxiliary: str, min_count: int = 1) -> Tuple[bool, str]:
    """
    检查文案中复合过去时的助动词是否都是指定的助动词，且至少出现指定次数
    
    参数:
        items: 文案列表
        auxiliary: 指定的助动词 'avoir' 或 'être'
        min_count: 最少出现次数，默认为1
    
    返回:
        (是否通过, 详细说明)
    """
    if auxiliary not in ['avoir', 'être']:
        return False, "❌ 助动词参数错误：必须是 'avoir' 或 'être'"
    
    if min_count < 1:
        return False, "❌ 最少次数参数错误：必须大于等于1"
    
    detector = PasseComposeDetector()
    results = []
    all_valid = True
    
    for i, item in enumerate(items, 1):
        detected = detector.detect(item, auxiliary)
        
        # 按助动词类型分组，保存完整信息
        avoir_verbs = []
        etre_verbs = []
        
        for aux_type, aux_form, participe, infinitive in detected:
            if aux_type == 'avoir':
                avoir_verbs.append((aux_form, participe))
            else:
                etre_verbs.append((aux_form, participe))
        
        # 判断是否符合要求
        has_passe_compose = len(detected) > 0
        
        if not has_passe_compose:
            # 没有复合过去时
            is_valid = False
            result_line = f"第{i}项: 未检测到复合过去时（要求至少{min_count}个{auxiliary}助动词）"
        elif auxiliary == 'avoir':
            # 要求：1. 全部是 avoir  2. 至少 min_count 个
            is_valid = len(avoir_verbs) >= min_count and len(etre_verbs) == 0
            result_line = f"第{i}项: "
            
            if len(avoir_verbs) >= min_count and len(etre_verbs) == 0:
                # 完全符合要求
                result_line += f"avoir助动词 {len(avoir_verbs)}个（符合要求 ≥{min_count}）:\n"
                full_form_counter = Counter([f"{aux} {part}" for aux, part in avoir_verbs])
                seen = set()
                for aux_form, participe in avoir_verbs:
                    full_form = f"{aux_form} {participe}"
                    if full_form not in seen:
                        count = full_form_counter[full_form]
                        if count > 1:
                            result_line += f"  {full_form} ({count}次)\n"
                        else:
                            result_line += f"  {full_form}\n"
                        seen.add(full_form)
                result_line = result_line.rstrip()
            else:
                # 不符合要求
                if len(avoir_verbs) > 0:
                    if len(avoir_verbs) < min_count:
                        result_line += f"avoir助动词 {len(avoir_verbs)}个（不足{min_count}个）:\n"
                    else:
                        result_line += f"avoir助动词 {len(avoir_verbs)}个:\n"
                    
                    full_form_counter = Counter([f"{aux} {part}" for aux, part in avoir_verbs])
                    seen = set()
                    for aux_form, participe in avoir_verbs:
                        full_form = f"{aux_form} {participe}"
                        if full_form not in seen:
                            count = full_form_counter[full_form]
                            if count > 1:
                                result_line += f"  {full_form} ({count}次)\n"
                            else:
                                result_line += f"  {full_form}\n"
                            seen.add(full_form)
                
                if len(etre_verbs) > 0:
                    # 只举第一个例子
                    aux_form, participe = etre_verbs[0]
                    example = f"{aux_form} {participe}"
                    result_line += f"  ⚠️ 出现être助动词，例如：{example}\n"
                
                result_line = result_line.rstrip()
            
        else:  # auxiliary == 'être'
            # 要求：1. 全部是 être  2. 至少 min_count 个
            is_valid = len(etre_verbs) >= min_count and len(avoir_verbs) == 0
            result_line = f"第{i}项: "
            
            if len(etre_verbs) >= min_count and len(avoir_verbs) == 0:
                # 完全符合要求
                result_line += f"être助动词 {len(etre_verbs)}个（符合要求 ≥{min_count}）:\n"
                full_form_counter = Counter([f"{aux} {part}" for aux, part in etre_verbs])
                seen = set()
                for aux_form, participe in etre_verbs:
                    full_form = f"{aux_form} {participe}"
                    if full_form not in seen:
                        count = full_form_counter[full_form]
                        if count > 1:
                            result_line += f"  {full_form} ({count}次)\n"
                        else:
                            result_line += f"  {full_form}\n"
                        seen.add(full_form)
                result_line = result_line.rstrip()
            else:
                # 不符合要求
                if len(etre_verbs) > 0:
                    if len(etre_verbs) < min_count:
                        result_line += f"être助动词 {len(etre_verbs)}个（不足{min_count}个）:\n"
                    else:
                        result_line += f"être助动词 {len(etre_verbs)}个:\n"
                    
                    full_form_counter = Counter([f"{aux} {part}" for aux, part in etre_verbs])
                    seen = set()
                    for aux_form, participe in etre_verbs:
                        full_form = f"{aux_form} {participe}"
                        if full_form not in seen:
                            count = full_form_counter[full_form]
                            if count > 1:
                                result_line += f"  {full_form} ({count}次)\n"
                            else:
                                result_line += f"  {full_form}\n"
                            seen.add(full_form)
                
                if len(avoir_verbs) > 0:
                    # 只举第一个例子
                    aux_form, participe = avoir_verbs[0]
                    example = f"{aux_form} {participe}"
                    result_line += f"  ⚠️ 出现avoir助动词，例如：{example}\n"
                
                result_line = result_line.rstrip()
        
        if not is_valid:
            all_valid = False
        
        results.append(result_line)
    
    if all_valid:
        header = f"✅ 所有项都至少使用{min_count}个{auxiliary}助动词，且全部使用{auxiliary}助动词\n\n"
    else:
        header = f"❌ 部分项不符合要求（要求至少{min_count}个{auxiliary}助动词，且全部使用{auxiliary}助动词）\n\n"
    
    explanation = header + "\n".join(results)
    
    return all_valid, explanation

################## 副代词en和y ###############################################
class AdverbialPronounDetector:
    """法语副代词检测器（完整版）"""
    
    def __init__(self, verbcc_index_path='verb_index_optimized.json'):
        self.verbcc = VerbccIndex(verbcc_index_path)
        
        # 需要排除的固定搭配（三词）
        self.fixed_expressions_y = {
            'il y a',
            'il y avait',
            'il y aura',
            'il y aurait',
            'il y eut',
        }
        
        # y 的固定短语排除（两词）
        self.y_fixed_phrases = {
            'y compris',
            'y inclus',
        }
        
        # en 的固定短语排除（两词）
        self.en_fixed_phrases = {
            'en fait',
            'en vérité',
            'en conclusion',
            'en définitive',
            'en somme',
            'en effet',
            'en général',
            'en particulier',
            'en principe',
            'en revanche',
            'en outre',
            'en plus',
            'en moins',
            'en tout',
            'en réalité',
            'en théorie',
            'en pratique',
            'en bref',
            'en résumé',
            'en fin',
        }
        
        # en 的固定短语排除（三词）
        self.en_fixed_phrases_three = {
            'en même temps',
            'en tout cas',
            'en fin de',
            'en tout genre',
        }
        
        # 反身代词列表
        self.reflexive_pronouns = {
            'me', 'te', 'se', 'nous', 'vous',
            'm', 't', 's'
        }
        
        # 宾语代词列表
        self.object_pronouns = {
            'le', 'la', 'les', 'lui', 'leur',
            'l'
        }
        
        # 句子终止标点
        self.sentence_endings = {'.', '!', '?', '…'}
    
    def tokenize(self, sentence: str) -> List[str]:
        """分词"""
        
        # ✅ 第一步：处理省略（兼容所有撇号类型）
        # 定义所有可能的撇号字符
        apostrophes = r"['''`´‘’]"
        
        # 1.1 处理 d'y, d'en 等特殊情况（单字母 + 撇号 + y/en）
        sentence = re.sub(
            rf"\b([ldcjmntsLDCJMNTS]){apostrophes}(y|en)\b",
            r"\1' \2",
            sentence,
            flags=re.IGNORECASE
        )
        
        # 1.2 处理普通省略（单字母 + 撇号 + 元音开头的词）
        sentence = re.sub(
            rf"\b([ldcjmntsLDCJMNTS]){apostrophes}([aeiouyhàâäéèêëïîôùûüÿœæAEIOUYHÀÂÄÉÈÊËÏÎÔÙÛÜŸŒÆ])",
            r"\1' \2",
            sentence
        )
        
        # ✅ 第二步：标点符号分离
        sentence = re.sub(r'([,;:!?.…])', r' \1 ', sentence)
        
        tokens = sentence.split()
        
        return tokens

    
    def _is_fixed_expression_en(self, tokens: List[str], position: int) -> bool:
        if position + 1 >= len(tokens):
            return False
        
        current_word = tokens[position].lower()
        next_word = tokens[position + 1].lower().rstrip('.,;:!?')
        
        # 检查两词组合
        two_words = f"{current_word} {next_word}"
        if two_words in self.en_fixed_phrases:
            return True
        
        # 检查三词组合
        if position + 2 < len(tokens):
            third_word = tokens[position + 2].lower().rstrip('.,;:!?')
            three_words = f"{current_word} {next_word} {third_word}"
            if three_words in self.en_fixed_phrases_three:
                return True
        
        return False
    
    def _is_gerondif(self, tokens: List[str], position: int) -> bool:
        if position + 1 >= len(tokens):
            return False
        
        # 检查 en 后面的词
        next_idx = position + 1
        next_word = tokens[next_idx].lower().rstrip('.,;:!?')
        
        # 情况1：en + 动词-ant (如 en mangeant)
        if next_word.endswith('ant'):
            return True
        
        # 情况2：en + 代词 + 动词-ant (如 en te promenant, en y réfléchissant)
        if next_word in self.reflexive_pronouns or \
           next_word in self.object_pronouns or \
           next_word in ['y', 'en']:
            # 检查代词后面是否是 -ant 动词
            if position + 2 < len(tokens):
                word_after_pronoun = tokens[position + 2].lower().rstrip('.,;:!?')
                if word_after_pronoun.endswith('ant'):
                    return True
        
        return False
    
    def _is_fixed_expression_y(self, tokens: List[str], position: int) -> bool:
        """检查 y 是否是固定搭配"""
        if position + 1 >= len(tokens):
            return False
        
        current_word = tokens[position].lower()
        next_word = tokens[position + 1].lower().rstrip('.,;:!?')
        
        # 检查两词组合（y compris, y inclus）
        two_words = f"{current_word} {next_word}"
        if two_words in self.y_fixed_phrases:
            return True
        
        # 检查三词组合（il y a）
        if position > 0:
            prev_word = tokens[position - 1].lower()
            three_words = f"{prev_word} {current_word} {next_word}"
            if three_words in self.fixed_expressions_y:
                return True
        
        return False
    
    def _has_verb_after(self, tokens: List[str], position: int, max_distance: int = 3) -> bool:
        """检查后面是否有动词"""
        for j in range(position + 1, min(position + max_distance + 1, len(tokens))):
            word = tokens[j].lower().rstrip('.,;:!?')
            
            # 跳过空字符串
            if not word:
                continue
            
            # 检查变位是否在索引中
            if word in self.verbcc.reverse_index:
                return True
        
        return False
    
    def _reconstruct_context(self, tokens: List[str], start: int, end: int, center_pos: int) -> str:
        if start >= end or start >= len(tokens):
            return ""
        
        # 向前找到句子开始（遇到句号停止）
        actual_start = start
        for i in range(center_pos - 1, start - 1, -1):
            if i < 0 or i >= len(tokens):
                break
            token = tokens[i].strip()
            if token in self.sentence_endings:
                actual_start = i + 1
                break
        
        # 向后找到句子结束（遇到句号停止）
        actual_end = end
        for i in range(center_pos + 1, min(end, len(tokens))):
            token = tokens[i].strip()
            if token in self.sentence_endings:
                actual_end = i + 1  # 包含句号
                break
        
        # 重建文本
        result = []
        for i in range(actual_start, actual_end):
            if i >= len(tokens):
                break
                
            token = tokens[i]
            
            # 标点符号直接添加（前面不加空格）
            if token in {',', ';', ':', '!', '?', '.', '…'}:
                result.append(token)
            # 引号也直接添加
            elif token in {'"', '"', '"', "'"}:
                result.append(token)
            # 如果上一个token以'结尾（省略号），不加空格
            elif result and result[-1].endswith("'"):
                result.append(token)
            # 正常情况，加空格
            else:
                if result:
                    result.append(" ")
                result.append(token)
        
        text = ''.join(result).strip()
        
        # 如果不是从句子开始，添加前省略号
        if actual_start > start:
            text = "..." + text
        
        # 如果不是在句子结束，添加后省略号
        if actual_end < end and actual_end < len(tokens):
            # 检查最后一个字符是否已经是句号
            if not text.endswith(('.', '!', '?', '…')):
                text = text + "..."
        
        return text
    
    def detect_en(self, text: str) -> List[Tuple[int, str]]:
        """检测所有副代词 en（排除副动词和固定短语）"""
        tokens = self.tokenize(text)
        results = []
        
        for i, token in enumerate(tokens):
            if token.lower() == 'en':
                # 排除固定短语（如 en fait, en vérité）
                if self._is_fixed_expression_en(tokens, i):
                    continue
                
                # 排除副动词形式
                if self._is_gerondif(tokens, i):
                    continue
                
                # 检查后面是否有动词
                if self._has_verb_after(tokens, i):
                    # 获取上下文
                    start = max(0, i - 5)
                    end = min(len(tokens), i + 6)
                    context = self._reconstruct_context(tokens, start, end, i)
                    results.append((i, context))
        
        return results
    
    def detect_y(self, text: str) -> List[Tuple[int, str]]:
        """检测所有副代词 y"""
        tokens = self.tokenize(text)
        results = []
        
        for i, token in enumerate(tokens):
            if token.lower() == 'y':
                # 排除固定搭配
                if self._is_fixed_expression_y(tokens, i):
                    continue
                
                # 检查后面是否有动词
                if self._has_verb_after(tokens, i):
                    # 获取上下文
                    start = max(0, i - 5)
                    end = min(len(tokens), i + 6)
                    context = self._reconstruct_context(tokens, start, end, i)
                    results.append((i, context))
        
        return results
    
    def count_pronouns(self, text: str) -> Dict[str, int]:
        """统计副代词数量"""
        en_count = len(self.detect_en(text))
        y_count = len(self.detect_y(text))
        
        return {
            'en': en_count,
            'y': y_count,
            'total': en_count + y_count
        }
    
    def check_ratio(self, text: str, en_ratio: int, y_ratio: int) -> Tuple[bool, str]:
        """检查副代词比例是否符合要求"""
        # 处理 list 类型输入
        if isinstance(text, list):
            text = ' '.join(str(item) for item in text)
        
        en_list = self.detect_en(text)
        y_list = self.detect_y(text)
        
        en_count = len(en_list)
        y_count = len(y_list)
        
        # 检查比例
        if en_count == 0 and y_count == 0:
            is_valid = False
            explanation = f"❌ 未检测到任何副代词 en 或 y\n"
            return is_valid, explanation
        
        # 计算实际比例（化简）
        if en_count == 0 or y_count == 0:
            actual_ratio_str = f"{en_count}:{y_count}"
        else:
            divisor = gcd(en_count, y_count)
            actual_ratio_str = f"{en_count//divisor}:{y_count//divisor}"
        
        expected_ratio_str = f"{en_ratio}:{y_ratio}"
        
        # 比例比较
        if en_count * y_ratio == y_count * en_ratio:
            is_valid = True
        else:
            is_valid = False
        
        # 构建说明
        explanation = ""
        
        if is_valid:
            explanation += f"✅ 副代词比例正确\n"
        else:
            explanation += f"❌ 副代词比例不符合要求\n"
        
        explanation += f"   en: {en_count} 个\n"
        explanation += f"   y: {y_count} 个\n"
        explanation += f"   实际比例: {actual_ratio_str}\n"
        explanation += f"   要求比例: {expected_ratio_str}\n"
        
        # 显示检出的副代词
        if en_list:
            explanation += f"\n⚠️检出的副代词 en:\n"
            for idx, (pos, context) in enumerate(en_list, 1):
                explanation += f"   {idx}. {context}\n"
        
        if y_list:
            explanation += f"\n⚠️检出的副代词 y:\n"
            for idx, (pos, context) in enumerate(y_list, 1):
                explanation += f"   {idx}. {context}\n"
        
        return is_valid, explanation


def check_adverbial_pronoun_ratio(text, en_ratio: int = 1, y_ratio: int = 2) -> Tuple[bool, str]:
    detector = AdverbialPronounDetector()
    return detector.check_ratio(text, en_ratio, y_ratio)

def check_adverbial_y_count(text, count_range: List[int]) -> Tuple[bool, str]:
    """
    检查副代词 y 的数量是否在指定范围内
    
    Args:
        text: 要检查的文本（可以是字符串或列表）
        count_range: 数量范围 [最小值, 最大值]
            - [3, 3]: 恰好3次
            - [3, 10000]: 至少3次
            - [0, 3]: 不超过3次
            - [5, 10]: 5到10次之间
    
    Returns:
        (is_valid, explanation): 布尔值表示是否符合要求，字符串为详细说明
    """
    detector = AdverbialPronounDetector()
    
    # 处理 list 类型输入
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    
    y_list = detector.detect_y(text)
    actual_count = len(y_list)
    
    min_count, max_count = count_range
    is_valid = (min_count <= actual_count <= max_count)
    
    # 构建说明
    if is_valid:
        if min_count == max_count:
            explanation = f"✅ 副代词 y 数量正确：恰好 {min_count} 次\n"
        elif max_count >= 10000:
            explanation = f"✅ 副代词 y 数量正确：至少 {min_count} 次（实际 {actual_count} 次）\n"
        else:
            explanation = f"✅ 副代词 y 数量正确：{min_count}-{max_count} 次范围内（实际 {actual_count} 次）\n"
    else:
        explanation = f"❌ 副代词 y 数量不符合要求\n"
        explanation += f"   实际: {actual_count} 次\n"
    
    # 显示所有检出的副代词 y
    if y_list:
        explanation += f"\n检出的副代词 y ({actual_count} 次):\n"
        for idx, (pos, context) in enumerate(y_list, 1):
            explanation += f"   {idx}. {context}\n"
    else:
        explanation += f"\n⚠️ 未检测到任何副代词 y\n"
    
    return is_valid, explanation


############### 赘词ne ###########################################

class NeDetector:
    """法语 ne 检测器 - 区分赘词和非赘词用法"""
    
    def __init__(self, verbcc_index_path='verb_index_optimized.json'):
        """初始化检测器"""
        self.verbcc = VerbccIndex(verbcc_index_path)
        
        # 否定词列表（非赘词标记）
        self.negation_words = {
            'pas', 'jamais', 'rien', 'personne', 'plus', 
            'guère', 'point', 'aucun', 'aucune', 'nul', 'nulle',
            'nullement', 'guères', 'ni'
        }
        
        # que（限制性，非赘词）
        self.restrictive_word = 'que'
        
        # ne 单独使用但表示否定的动词（原形）
        self.negative_verbs_infinitive = {
            'cesser',   # 停止
            'oser',     # 敢
            'pouvoir',  # 能够
            'savoir',   # 知道
        }
        
        # n'avoir + 名词的否定短语
        self.avoir_negative_nouns = {'crainte', 'cure', 'garde'}
        
        # ne 单独表示否定的固定表达（特殊变位或固定形式）
        self.negative_fixed_expressions = {
            'importe',  # n'importe
            'empêche',  # n'empêche
            'était',    # n'était (si ce n'était)
            'eût',      # n'eût été (si ce n'eût été)
        }
    
    def tokenize(self, text: str) -> List[str]:
        """分词（保留原始大小写）"""
        # 统一引号（单引号）
        text = text.replace(''', "'").replace(''', "'").replace('`', "'")
        
        # 分离双引号（中英文）
        text = text.replace('"', ' " ').replace('"', ' " ').replace('"', ' " ')
        
        # 处理所有缩略形式的省略号
        text = re.sub(
            r"\b([nldcjmtsqNLDCJMTSQ])'([aeiouyhàâäéèêëïîôùûüÿœæAEIOUYHÀÂÄÉÈÊËÏÎÔÙÛÜŸŒÆ])",
            r"\1' \2",
            text,
            flags=re.IGNORECASE
        )
        
        # 标点符号分离
        text = re.sub(r'([,;:!?.…])', r' \1 ', text)
        
        return text.split()
    
    def _extract_ne_context(self, tokens: List[str], position: int, context_size: int = 5) -> str:
        """提取 ne 周围的上下文（遇到分句标识时提前截断）"""
        clause_delimiters = {',', ';', '.', '!', '?', ':', '…'}
        
        # 向前查找
        start = position
        left_truncated = False
        for i in range(position - 1, max(-1, position - context_size - 1), -1):
            if i < 0:
                left_truncated = True
                start = 0
                break
            if tokens[i] in clause_delimiters:
                start = i + 1
                left_truncated = True
                break
            start = i
        
        # 向后查找
        end = position + 1
        right_truncated = False
        for i in range(position + 1, min(len(tokens), position + context_size + 1)):
            if i >= len(tokens):
                right_truncated = True
                end = len(tokens)
                break
            if tokens[i] in clause_delimiters:
                end = i
                right_truncated = True
                break
            end = i + 1
        
        context_tokens = tokens[start:end]
        context = ' '.join(context_tokens)
        
        # 清理多余空格
        context = re.sub(r'\s+([,;:!?.…])', r'\1', context)
        context = re.sub(r"(\w)'\s+(\w)", r"\1'\2", context)
        
        # 根据截断情况添加省略号
        if left_truncated and start > 0:
            context = '... ' + context
        if right_truncated and end < len(tokens):
            context = context + ' ...'
            
        return context
    
    def _is_negative_verb(self, word: str) -> Tuple[bool, str]:
        """检查是否是否定动词的变位形式（不区分大小写）"""
        word_lower = word.lower()
        
        # 先检查固定表达
        if word_lower in self.negative_fixed_expressions:
            return True, word_lower
        
        # 通过 Verbcc 索引查找原形
        infinitives = self.verbcc.get_infinitives(word_lower)
        
        # 检查是否有任何原形在否定动词列表中
        for inf in infinitives:
            if inf in self.negative_verbs_infinitive:
                return True, inf
        
        return False, ""
    
    def _check_negative_verb_phrase(self, tokens: List[str], position: int) -> Tuple[bool, str]:
        """检查是否是 ne 单独使用的否定动词短语（不区分大小写）"""
        
        # 向后查找动词（ne 后面紧跟动词，最多跳过2个词）
        for j in range(position + 1, min(len(tokens), position + 3)):
            word = tokens[j].lower().rstrip('.,;:!?…')
            
            if not word or word in {'de', 'à', 'd', "d'", 'y'}:
                continue
            
            # 检查是否是否定动词
            is_neg, infinitive = self._is_negative_verb(word)
            if is_neg:
                return True, f"ne {infinitive}"
        
        # 检查 n'avoir + crainte/cure/garde
        for j in range(position + 1, min(len(tokens), position + 3)):
            word = tokens[j].lower().rstrip('.,;:!?…')
            
            # ✅ 修复：先检查是否是动词，再检查原形
            if self.verbcc.is_verb(word):  # ← 只传一个参数
                # 获取所有可能的原形
                infinitives = self.verbcc.get_infinitives(word)
                
                # 检查是否是 avoir 的变位
                if 'avoir' in infinitives:
                    # 继续向后查找名词
                    for k in range(j + 1, min(len(tokens), j + 3)):
                        noun = tokens[k].lower().rstrip('.,;:!?…')
                        if noun in self.avoir_negative_nouns:
                            return True, f"n'avoir {noun}"
        
        return False, ""

    
    def _check_si_clause(self, tokens: List[str], position: int) -> bool:
        """检查是否在 si 引导的条件从句中（不区分大小写）"""
        # 向前查找 si（最多5个词）
        for i in range(max(0, position - 5), position):
            word = tokens[i].lower().rstrip('.,;:!?…')
            if word == 'si':
                return True
        return False
    
    def _check_autre_que(self, tokens: List[str], position: int) -> bool:
        """检查是否是 autre...ne...que 结构（不区分大小写）"""
        # 向前查找 autre
        has_autre = False
        for i in range(max(0, position - 8), position):
            word = tokens[i].lower().rstrip('.,;:!?…')
            if word.startswith('autre'):
                has_autre = True
                break
        
        if not has_autre:
            return False
        
        # 向后查找 que
        for j in range(position + 1, min(len(tokens), position + 8)):
            word = tokens[j].lower().rstrip('.,;:!?…')
            if word == 'que' or word.startswith("qu'"):
                return True
        
        return False
    
    def _check_depuis_il_y_a(self, tokens: List[str], position: int) -> bool:
        """检查是否在 depuis que, il y a...que, voici/voilà...que 之后（不区分大小写）"""
        # 向前查找这些结构
        text_before = ' '.join(tokens[max(0, position - 10):position]).lower()
        patterns = ['depuis que', 'il y a', 'voici', 'voilà']
        for pattern in patterns:
            if pattern in text_before:
                return True
        return False
    
    def _check_interrogative_que(self, tokens: List[str], position: int) -> bool:
        """检查是否是 Que ne...? 疑问句（不区分大小写）"""
        # 检查句首是否是 Que（向前最多3个词）
        for i in range(max(0, position - 3), position):
            word = tokens[i].lower().rstrip('.,;:!?…')
            if word == 'que' and i <= 3:  # 在句首位置
                # 检查是否有问号
                for j in range(position, min(len(tokens), position + 15)):
                    if tokens[j] == '?':
                        return True
        return False
    
    def _check_personne_rien_nul(self, tokens: List[str], position: int) -> bool:
        """检查是否与 personne, rien, nul 等泛指否定词一起使用（不区分大小写）"""
        # 向前查找（主语位置）
        for i in range(max(0, position - 5), position):
            word = tokens[i].lower().rstrip('.,;:!?…')
            if word in ['personne', 'rien', 'nul', 'nulle', 'aucun', 'aucune']:
                return True
        
        # 向后查找（宾语位置）- 但排除有 pas/jamais 等的情况
        has_other_negation = False
        for j in range(position + 1, min(len(tokens), position + 8)):
            word = tokens[j].lower().rstrip('.,;:!?…')
            if word in ['pas', 'jamais', 'plus', 'point', 'guère']:
                has_other_negation = True
                break
            if word in ['personne', 'rien', 'nul', 'nulle', 'aucun', 'aucune']:
                return not has_other_negation
        
        return False
    
    def _check_ni_ni(self, tokens: List[str], position: int) -> bool:
        """检查是否是 ne...ni...ni 结构（不区分大小写）"""
        ni_count = 0
        for j in range(position + 1, min(len(tokens), position + 15)):
            word = tokens[j].lower().rstrip('.,;:!?…')
            if word == 'ni':
                ni_count += 1
                if ni_count >= 2:
                    return True
        return False
    
    def _has_negation_word_after(self, tokens: List[str], position: int, search_range: int = 8) -> Tuple[bool, str]:
        """检查后面是否有否定词或 que（不区分大小写）"""
        clause_delimiters = {',', ';', '.', '!', '?', ':', '…'}
        
        for j in range(position + 1, min(position + search_range + 1, len(tokens))):
            if tokens[j] in clause_delimiters:
                break
            
            word = tokens[j].lower().rstrip('.,;:!?…')
            
            if not word:
                continue
            
            # 检查否定词
            if word in self.negation_words:
                return True, word
            
            # 检查 que 或 qu'
            if word == 'que' or word.startswith("qu'"):
                return True, 'que'
        
        return False, ""
    
    def detect_ne(self, text: str) -> List[Dict]:
        if isinstance(text, list):
            text = ' '.join(str(item) for item in text)
        
        tokens = self.tokenize(text)
        results = []
        
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            # 识别 ne 或 n' (省音形式) - 不区分大小写
            if token_lower in ['ne', "n'"]:
                ne_info = self._analyze_ne(tokens, i)
                if ne_info:
                    results.append(ne_info)
        
        return results
    
    def _analyze_ne(self, tokens: List[str], position: int) -> Dict:
        context = self._extract_ne_context(tokens, position, context_size=5)
        
        # 1. 检查是否是否定动词短语（优先级最高）
        is_neg_phrase, phrase = self._check_negative_verb_phrase(tokens, position)
        if is_neg_phrase:
            return {
                'position': position,
                'type': 'negation',
                'context': context,
                'reason': f'否定动词短语 ({phrase})',
                'negation_word': 'phrase'
            }
        
        # 2. 检查是否与 personne/rien/nul 等一起使用
        if self._check_personne_rien_nul(tokens, position):
            return {
                'position': position,
                'type': 'negation',
                'context': context,
                'reason': '与泛指否定词连用',
                'negation_word': 'indefinite'
            }
        
        # 3. 检查是否是 ne...ni...ni 结构
        if self._check_ni_ni(tokens, position):
            return {
                'position': position,
                'type': 'negation',
                'context': context,
                'reason': 'ne...ni...ni 结构',
                'negation_word': 'ni'
            }
        
        # 4. 检查是否有否定词或 que
        has_negation, neg_word = self._has_negation_word_after(tokens, position)
        if has_negation:
            if neg_word == 'que':
                return {
                    'position': position,
                    'type': 'negation',
                    'context': context,
                    'reason': '限制性 (ne...que)',
                    'negation_word': 'que'
                }
            else:
                return {
                    'position': position,
                    'type': 'negation',
                    'context': context,
                    'reason': f'真正否定 (ne...{neg_word})',
                    'negation_word': neg_word
                }
        
        # 5. 检查是否在 si 条件从句中
        if self._check_si_clause(tokens, position):
            return {
                'position': position,
                'type': 'negation',
                'context': context,
                'reason': 'si 条件从句中的否定',
                'negation_word': 'si_clause'
            }
        
        # 6. 检查是否是 autre...que 结构
        if self._check_autre_que(tokens, position):
            return {
                'position': position,
                'type': 'negation',
                'context': context,
                'reason': 'autre...ne...que 结构',
                'negation_word': 'autre_que'
            }
        
        # 7. 检查是否在 depuis que, il y a...que 等之后
        if self._check_depuis_il_y_a(tokens, position):
            return {
                'position': position,
                'type': 'negation',
                'context': context,
                'reason': 'depuis que/il y a...que 结构',
                'negation_word': 'time_clause'
            }
        
        # 8. 检查是否是 Que ne...? 疑问句
        if self._check_interrogative_que(tokens, position):
            return {
                'position': position,
                'type': 'negation',
                'context': context,
                'reason': 'Que ne...? 疑问句',
                'negation_word': 'interrogative'
            }
        
        # 9. 其他情况：赘词
        return {
            'position': position,
            'type': 'expletive',
            'context': context,
            'reason': '赘词 ne (无否定意义)'
        }
    
    def count_ne_types(self, text: str) -> Dict[str, int]:
        """统计 ne 的类型数量"""
        ne_list = self.detect_ne(text)
        
        expletive_count = sum(1 for ne in ne_list if ne['type'] == 'expletive')
        negation_count = sum(1 for ne in ne_list if ne['type'] == 'negation')
        
        return {
            'total': len(ne_list),
            'expletive': expletive_count,
            'negation': negation_count
        }
    
    def check_ne_requirement(
        self, 
        text: str, 
        min_count: int, 
        expletive_ratio: int, 
        negation_ratio: int
    ) -> Tuple[bool, str]:
    
        if isinstance(text, list):
            text = ' '.join(str(item) for item in text)
        
        ne_list = self.detect_ne(text)
        counts = self.count_ne_types(text)
        
        total = counts['total']
        expletive = counts['expletive']
        negation = counts['negation']
        
        meets_count = total >= min_count
        
        if expletive == 0 and negation == 0:
            meets_ratio = False
            actual_ratio_str = "0:0"
        elif expletive == 0 or negation == 0:
            actual_ratio_str = f"{expletive}:{negation}"
            meets_ratio = False
        else:
            divisor = gcd(expletive, negation)
            actual_exp = expletive // divisor
            actual_neg = negation // divisor
            actual_ratio_str = f"{actual_exp}:{actual_neg}"
            meets_ratio = (actual_exp == expletive_ratio and actual_neg == negation_ratio)
        
        expected_ratio_str = f"{expletive_ratio}:{negation_ratio}"
        
        is_valid = meets_count and meets_ratio
        
        explanation = ""
        if is_valid:
            explanation += "✅ ne 的使用符合要求\n"
        else:
            explanation += "❌ ne 的使用不符合要求\n"
        
        explanation += f"\n总体统计:\n"
        explanation += f"   总出现次数: {total} (要求 ≥ {min_count}) {'✓' if meets_count else '✗'}\n"
        explanation += f"   赘词 ne: {expletive} 个\n"
        explanation += f"   非赘词 ne: {negation} 个\n"
        explanation += f"   实际比例: {actual_ratio_str}\n"
        
        if ne_list:
            explanation += f"\n检出的 ne 详情:\n"
            
            expletive_list = [ne for ne in ne_list if ne['type'] == 'expletive']
            negation_list = [ne for ne in ne_list if ne['type'] == 'negation']
            
            if expletive_list:
                explanation += f"\n赘词 ne ({len(expletive_list)}个):\n"
                for idx, ne in enumerate(expletive_list, 1):
                    explanation += f"   {idx}. {ne['context']}\n"
            
            if negation_list:
                explanation += f"\n非赘词 ne ({len(negation_list)}个):\n"
                for idx, ne in enumerate(negation_list, 1):
                    explanation += f"   {idx}. {ne['context']}\n"
        
        return is_valid, explanation


def parse_ne_rule(rule: str) -> Tuple[int, int, int]:
    pattern = r'french_ne_usage(\d+):\[(\d+),(\d+)\]'
    match = re.match(pattern, rule)
    
    if not match:
        raise ValueError(f"规则格式错误: {rule}. 正确格式: french_ne_usage<min_count>:[<expletive_ratio>,<negation_ratio>]")
    
    min_count = int(match.group(1))
    expletive_ratio = int(match.group(2))
    negation_ratio = int(match.group(3))
    
    return min_count, expletive_ratio, negation_ratio


def check_ne_usage_from_rule(text, rule: str) -> Tuple[bool, str]:
    try:
        min_count, expletive_ratio, negation_ratio = parse_ne_rule(rule)
        detector = NeDetector()
        return detector.check_ne_requirement(text, min_count, expletive_ratio, negation_ratio)
    except Exception as e:
        return False, f"❌ 规则解析错误: {str(e)}"
    
######################## 空格规则 #############################

class FrenchPunctuationChecker:
    """法语标点符号空格规则检测器"""
    
    def __init__(self):
        pass
    
    def check_french_spacing(self, text: str) -> Tuple[bool, str]:
        """检查文本是否符合法语标点符号空格规则"""
        errors = []
        
        errors.extend(self._check_after_only(text))
        errors.extend(self._check_both_space(text))
        errors.extend(self._check_parentheses(text))
        errors.extend(self._check_guillemets(text))
        
        if not errors:
            explanation = "✅ 文本符合法语标点符号空格规则"
            return True, explanation
        else:
            explanation = f"❌ 文本不符合法语标点符号空格规则\n\n发现 {len(errors)} 个错误:\n"
            for i, error in enumerate(errors, 1):
                explanation += f"\n{i}. {error}"
            return False, explanation
    
    def _check_after_only(self, text: str) -> List[str]:
        """检查逗号和句号"""
        errors = []
        
        pattern = r'\s+,'
        for match in re.finditer(pattern, text):
            context = self._get_context(text, match.start(), match.end())
            errors.append(f"逗号前不应有空格: {context}")
        
        pattern = r',(?!\s)'
        for match in re.finditer(pattern, text):
            next_pos = match.end()
            if next_pos < len(text):
                next_char = text[next_pos]
                if next_char not in [' ', '\xa0', '\n', '\t', '"', "'", ')', ']', '}', '»', ',', ';', ':', '.', '!', '?', '…'] and not next_char.isdigit():
                    context = self._get_context(text, match.start(), match.end())
                    errors.append(f"逗号后应有空格: {context}")
        
        pattern = r'(?<![.\s])\s+\.(?!\.)'
        for match in re.finditer(pattern, text):
            context = self._get_context(text, match.start(), match.end())
            errors.append(f"句号前不应有空格: {context}")
        
        pattern = r'\.(?!\.)'
        for match in re.finditer(pattern, text):
            next_pos = match.end()
            if next_pos >= len(text):
                continue
            
            if next_pos > 0:
                prev_char = text[match.start() - 1] if match.start() > 0 else ''
                next_char = text[next_pos] if next_pos < len(text) else ''
                
                if prev_char.isdigit() and next_char.isdigit():
                    continue
                
                if prev_char.isalpha() and (next_char.isalpha() or next_char == '/'):
                    continue
                
                if next_char not in [' ', '\xa0', '\n', '\t', '"', "'", ')', ']', '}', '»', ',', ';', ':', '.', '!', '?', '…']:
                    context = self._get_context(text, match.start(), match.end())
                    errors.append(f"句号后应有空格: {context}")
        
        return errors
    
    def _check_both_space(self, text: str) -> List[str]:
        """检查分号、冒号、感叹号、问号、百分号"""
        errors = []
        
        double_puncts = [';', ':', '!', '?', '%']
        
        for punct in double_puncts:
            pattern = rf'(?<!["\'\(\[«\s\xa0\u3000]){re.escape(punct)}'
            for match in re.finditer(pattern, text):
                if match.start() > 0:
                    context = self._get_context(text, match.start(), match.end())
                    errors.append(f"标点 '{punct}' 前应有空格: {context}")
            
            for match in re.finditer(re.escape(punct), text):
                next_pos = match.end()
                if next_pos >= len(text):
                    continue
                
                next_char = text[next_pos] if next_pos < len(text) else ''
                if next_char not in [' ', '\xa0', '\n', '\t', ',', ';', ':', '.', '!', '?', '%', '"', "'", ')', ']', '}', '»', '…', '-']:
                    context = self._get_context(text, match.start(), match.end())
                    errors.append(f"标点 '{punct}' 后应有空格: {context}")
        
        return errors
    
    def _check_parentheses(self, text: str) -> List[str]:
        """检查括号"""
        errors = []
        
        open_brackets = ['(', '[', '{']
        close_brackets = [')', ']', '}']
        
        for bracket in open_brackets:
            pattern = rf'(?<!["\'\(\[«\s\xa0\u3000]){re.escape(bracket)}'
            for match in re.finditer(pattern, text):
                if match.start() > 0:
                    context = self._get_context(text, match.start(), match.end())
                    errors.append(f"左括号 '{bracket}' 前应有空格: {context}")
            
            pattern = rf'{re.escape(bracket)}\s+'
            for match in re.finditer(pattern, text):
                context = self._get_context(text, match.start(), match.end())
                errors.append(f"左括号 '{bracket}' 后不应有空格: {context}")
        
        for bracket in close_brackets:
            pattern = rf'\s+{re.escape(bracket)}'
            for match in re.finditer(pattern, text):
                context = self._get_context(text, match.start(), match.end())
                errors.append(f"右括号 '{bracket}' 前不应有空格: {context}")
            
            for match in re.finditer(re.escape(bracket), text):
                next_pos = match.end()
                if next_pos >= len(text):
                    continue
                
                next_char = text[next_pos] if next_pos < len(text) else ''
                if next_char not in [' ', '\xa0', '\n', '\t', ',', ';', ':', '.', '!', '?', '%', '"', "'", ')', ']', '}', '»', '…', '-']:
                    context = self._get_context(text, match.start(), match.end())
                    errors.append(f"右括号 '{bracket}' 后应有空格: {context}")
        
        return errors
    
    def _check_guillemets(self, text: str) -> List[str]:
        """检查法语引号"""
        errors = []
        
        pattern = r'(?<!["\'\s\xa0\u3000])«'
        for match in re.finditer(pattern, text):
            if match.start() > 0:
                context = self._get_context(text, match.start(), match.end())
                errors.append(f"左引号 « 前应有空格: {context}")
        
        pattern = r'«(?![\s\xa0\u3000])'
        for match in re.finditer(pattern, text):
            context = self._get_context(text, match.start(), match.end())
            errors.append(f"左引号 « 后应有空格: {context}")
        
        pattern = r'(?<![\s\xa0\u3000])»'
        for match in re.finditer(pattern, text):
            context = self._get_context(text, match.start(), match.end())
            errors.append(f"右引号 » 前应有空格: {context}")
        
        for match in re.finditer(r'»', text):
            next_pos = match.end()
            if next_pos >= len(text):
                continue
            
            next_char = text[next_pos] if next_pos < len(text) else ''
            if next_char not in [' ', '\xa0', '\n', '\t', ',', ';', ':', '.', '!', '?', '%', '…', '-']:
                context = self._get_context(text, match.start(), match.end())
                errors.append(f"右引号 » 后应有空格: {context}")
        
        return errors
    
    def _get_context(self, text: str, start: int, end: int, size: int = 20) -> str:
        """获取错误位置的上下文"""
        ctx_start = max(0, start - size)
        ctx_end = min(len(text), end + size)
        
        before = text[ctx_start:start]
        error = text[start:end]
        after = text[end:ctx_end]
        
        if ctx_start > 0:
            before = '...' + before
        if ctx_end < len(text):
            after = after + '...'
        
        return f'"{before}【{error}】{after}"'
    
    def fix_french_spacing(self, text: str) -> str:
        """自动修复法语标点符号空格"""
        for punct in [';', ':', '!', '?', '%']:
            text = re.sub(rf'(?<!\s){re.escape(punct)}', f' {punct}', text)
            text = re.sub(rf'{re.escape(punct)}(?!\s)', f'{punct} ', text)
        
        text = re.sub(r',(?!\s)', ', ', text)
        text = re.sub(r'\.(?!\.|[\s\d])', '. ', text)
        
        text = re.sub(r'\s+,', ',', text)
        text = re.sub(r'\s+\.(?!\.)', '.', text)
        
        text = re.sub(r'(?<!\s)«', ' «', text)
        text = re.sub(r'«(?!\s)', '« ', text)
        text = re.sub(r'(?<!\s)»', ' »', text)
        text = re.sub(r'»(?!\s)', '» ', text)
        
        for open_br, close_br in [('(', ')'), ('[', ']'), ('{', '}')]:
            text = re.sub(rf'(?<!\s){re.escape(open_br)}', f' {open_br}', text)
            text = re.sub(rf'{re.escape(open_br)}\s+', open_br, text)
            text = re.sub(rf'\s+{re.escape(close_br)}', close_br, text)
            text = re.sub(rf'{re.escape(close_br)}(?!\s)', f'{close_br} ', text)
        
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'\s+([,.])', r'\1', text)
        
        return text.strip()


def check_french_punctuation_from_rule(text, rule: str = "french_punctuation_spacing") -> Tuple[int, str]:
    """
    从规则检查法语标点空格
    
    Args:
        text: 文本或文本列表
        rule: 规则名称
    
    Returns:
        (score, explanation): 0或1表示是否通过，以及详细说明
    """
    if rule != "french_punctuation_spacing":
        return 0, f"❌ 不支持的规则: {rule}"
    
    checker = FrenchPunctuationChecker()
    
    # 处理列表输入 - 逐项检查
    if isinstance(text, list):
        all_passed = True
        failed_items = []
        all_results = []
        
        for item_index, item_text in enumerate(text):
            text_str = str(item_text)
            is_valid, explanation = checker.check_french_spacing(text_str)
            
            if is_valid:
                all_results.append(f"第{item_index + 1}项: ✅ 符合规则")
            else:
                all_passed = False
                failed_items.append(item_index + 1)
                all_results.append(f"第{item_index + 1}项:\n{explanation}")
        
        if all_passed:
            result_summary = f"✅ 所有 {len(text)} 项都符合法语标点符号空格规则"
            return 1, result_summary
        else:
            result_summary = f"❌ 有 {len(failed_items)} 项不符合法语标点符号空格规则（第 {', '.join(map(str, failed_items))} 项）\n\n"
            result_summary += "\n\n".join(all_results)
            return 0, result_summary
    
    # 处理字符串输入
    if not isinstance(text, str):
        text = str(text)
    
    is_valid, explanation = checker.check_french_spacing(text)
    return (1 if is_valid else 0), explanation



######################检查特定标点 列表版########################
def check_special_notations(model_response, rule):
    _, _, notation_string = rule.partition(":")
    
    if not notation_string:
        return 0, "❌ 规则格式错误: 未指定要检查的符号"
    
    # 分割多个符号（支持逗号分隔）
    target_notations = [symbol.strip() for symbol in notation_string.split(",")]
    
    # 检查每个符号
    detected_notations = {}
    missing_notations = []
    
    for target_symbol in target_notations:
        if not target_symbol:
            continue
            
        occurrence_list = []
        for response_index, response_text in enumerate(model_response):
            text_content = str(response_text)
            if target_symbol in text_content:
                # 找出符号出现的位置
                match_positions = [match.start() for match in re.finditer(re.escape(target_symbol), text_content)]
                occurrence_list.append({
                    'response_index': response_index,
                    'text_content': text_content,
                    'match_positions': match_positions,
                    'occurrence_count': len(match_positions)
                })
        
        if occurrence_list:
            detected_notations[target_symbol] = occurrence_list
        else:
            missing_notations.append(target_symbol)
    
    # 构建结果
    if missing_notations:
        missing_symbols_display = "、".join([f"'{symbol}'" for symbol in missing_notations])
        return 0, f"❌ 以下标点符号未在文本中出现: {missing_symbols_display}"
    else:
        result_message_parts = ["✅ 所有要求的标点符号都已出现:\n"]
        
        for detected_symbol, occurrence_list in detected_notations.items():
            total_occurrence_count = sum(item['occurrence_count'] for item in occurrence_list)
            affected_response_count = len(occurrence_list)
            result_message_parts.append(
                f"\n符号 '{detected_symbol}': 出现了 {total_occurrence_count} 次，"
                f"在 {affected_response_count} 个位置"
            )
            
            for occurrence_item in occurrence_list:
                # 获取上下文
                full_text = occurrence_item['text_content']
                response_idx = occurrence_item['response_index']
                symbol_count = occurrence_item['occurrence_count']
                
                # 显示第一个出现位置的上下文
                first_position = occurrence_item['match_positions'][0]
                context_start_pos = max(0, first_position - 20)
                context_end_pos = min(len(full_text), first_position + 20)
                context_snippet = full_text[context_start_pos:context_end_pos]
                
                if context_start_pos > 0:
                    context_snippet = '...' + context_snippet
                if context_end_pos < len(full_text):
                    context_snippet = context_snippet + '...'
                
                result_message_parts.append(
                    f"  第{response_idx + 1}项 ({symbol_count}次): {context_snippet}"
                )
        
        return 1, "\n".join(result_message_parts)


if __name__ == "__main__":
    rule = "french_special_notation:;,...,?,!"
    model_response = [
"As-tu déjà imaginé que le temps puisse être comme une grande boucle ; qu’il ne s’écoule pas simplement du passé vers le futur, mais qu’il tourne et se replie sur lui-même ? C’est ce que des scientifiques viennent de découvrir grâce à une nouvelle étude quantique… Fascinant, n’est-ce pas ! Pour comprendre cette idée, il faut d’abord penser à l’espace-temps, une sorte de toile géante où tout ce qui existe – toi, moi, les planètes, les étoiles – se trouve. Imagine que tu poses une bille sur un trampoline ; la toile s’enfonce là où la bille est posée. Si tu ajoutes une autre bille, la toile se déforme encore plus. Eh bien, l’espace-temps fonctionne un peu comme ça ; les objets lourds, comme la Terre ou le Soleil, courbent cette toile invisible. Mais alors, où est le temps dans tout ça ? Le temps, c’est comme une direction sur cette toile ; on pense souvent qu’il va tout droit, du passé vers le futur. Pourtant, les chercheurs ont observé que, dans le monde minuscule des particules, le temps peut faire des choses étranges… Parfois, il semble tourner en rond, comme une roue de vélo ; parfois, il se replie sur lui-même, comme un serpent qui se mord la queue ! Imagine une horloge dont les aiguilles ne font pas que tourner ; elles pourraient revenir en arrière ou même s’arrêter un instant avant de repartir. C’est un peu ce que les scientifiques ont vu dans leurs expériences. Pour rendre cela plus concret, pense à un jeu vidéo où tu peux remonter le temps ; tu fais une erreur, tu appuies sur un bouton, et hop, tu reviens quelques secondes en arrière. Dans la vraie vie, on ne peut pas faire ça… ou du moins, c’est ce qu’on croyait ! Les expériences quantiques montrent que, pour certaines particules, le temps n’est pas une ligne droite ; il peut être une boucle, un zigzag, ou même un tourbillon. Cela veut-il dire que nous pourrions un jour voyager dans le temps ? Les scientifiques ne le savent pas encore ; mais ils sont sûrs d’une chose : le temps est bien plus mystérieux qu’on ne le pensait. Pour t’aider à imaginer, prends une feuille de papier et plie-la en deux ; le point où les deux côtés se touchent, c’est comme si le passé et le futur se rencontraient. Ou bien, dessine une spirale ; chaque tour représente un moment différent, mais tous sont reliés. Les chercheurs utilisent des machines très puissantes pour observer ces phénomènes ; ils envoient des particules dans des tunnels et regardent comment elles réagissent. Parfois, elles semblent “sauter” d’un moment à l’autre, comme si elles jouaient à cache-cache avec le temps ! Ce n’est pas facile à croire, mais c’est ce que la science nous montre. Alors, la prochaine fois que tu regarderas l’horloge, demande-toi : le temps avance-t-il vraiment… ou tourne-t-il en rond ? Peut-être qu’un jour, tu seras le scientifique qui découvrira encore plus de secrets sur le temps et l’espace-temps ; qui sait !"]


    check_special_notations(model_response,rule)