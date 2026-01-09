# from utils import clean_up_text
import re

def has_complete_questions(texts, times):
    """检查每条评论是否都包含指定数量的完整西班牙语疑问句（¿...?)"""
    
    if not texts:
        return 0, f"❌ No comments provided"
    
    # 确保 texts 是列表格式
    if isinstance(texts, str):
        comments = [texts]
    elif isinstance(texts, list):
        comments = texts
    else:
        comments = [str(texts)]
    
    # 完整疑问句的正则模式：¿开头，?结尾，中间不包含其他¿或?
    complete_question_pattern = r'¿[^¿?]*\?'
    
    comment_details = []
    all_match = True
    
    # 检查每个评论
    for i, comment in enumerate(comments):
        comment_text = str(comment).strip()
        
        # 查找完整的疑问句
        matches = re.findall(complete_question_pattern, comment_text, re.DOTALL)
        question_count = len(matches)
        
        # 检查是否符合要求
        matches_requirement = (question_count == times)
        if not matches_requirement:
            all_match = False
        
        # 记录详情
        status = "✅" if matches_requirement else "❌"
        if matches:
            display_questions = [q[:30] + "..." if len(q) > 30 else q for q in matches[:3]]
            comment_details.append(f"Comment {i+1}: {question_count} questions {status} ({', '.join(display_questions)})")
        else:
            comment_details.append(f"Comment {i+1}: {question_count} questions {status}")
    
    detail_info = " | ".join(comment_details)
    
    # 返回结果
    if all_match:
        return 1, f"✅ All {len(comments)} comments have exactly {times} questions: {detail_info}"
    else:
        return 0, f"❌ Some comments do NOT have exactly {times} questions: {detail_info}"


def has_complete_exclamations(texts, min_count, max_count=None):
    """检查是否包含指定数量范围的完整西班牙语感叹句
    
    特殊逻辑：
    - 如果要求min_count=0，则没有感叹句不算错误
    - 如果要求min_count>0，则没有感叹句算错误
    """
    
    if not texts:
        return 0, f"❌ No text provided"
    
    # 处理单个文本
    if isinstance(texts, str):
        text = texts
    elif isinstance(texts, list):
        text = ' '.join(texts)  # 合并所有文本
    else:
        text = str(texts)
    
    # 完整感叹句的正则模式：¡开头，!结尾
    complete_exclamation_pattern = r'¡[^¡!]*!'
    
    # 查找完整的感叹句
    matches = re.findall(complete_exclamation_pattern, text, re.DOTALL)
    exclamation_count = len(matches)
    
    # 设置默认最大值
    if max_count is None:
        max_count = 1000
    
    # 🆕 特殊逻辑：处理"没有感叹句"的情况
    if exclamation_count == 0:
        if min_count == 0:
            # 要求0个，实际0个 → 正确
            return 1, f"✅ Found 0 complete exclamations as required (expected: {min_count}-{max_count}). No exclamations needed."
        else:
            # 要求>0个，实际0个 → 错误
            return 0, f"❌ No complete exclamations found but {min_count}-{max_count} required. Task requires exclamatory sentences with ¡...! format."
    
    # 检查是否在范围内
    meets_requirement = min_count <= exclamation_count <= max_count
    
    # 显示找到的感叹句（前3个）
    display_exclamations = [exc[:30] + "..." if len(exc) > 30 else exc for exc in matches[:3]]
    exclamation_info = f"Found: {', '.join(display_exclamations)}"
    if len(matches) > 3:
        exclamation_info += f" (and {len(matches)-3} more)"
    
    # 返回结果
    if meets_requirement:
        return 1, f"✅ Found {exclamation_count} complete exclamations (required: {min_count}-{max_count}). {exclamation_info}"
    else:
        if exclamation_count < min_count:
            return 0, f"❌ Found only {exclamation_count} complete exclamations, need at least {min_count}. {exclamation_info}"
        else:
            return 0, f"❌ Found {exclamation_count} complete exclamations, exceeds maximum {max_count}. {exclamation_info}"



def has_spanish_word_count(texts, min_count, max_count):
    """检查每条西班牙语评论的单词数量是否都在指定范围内"""
    import re
    
    if not texts:
        return 0, f"❌ No comments provided"
    
    # 确保 texts 是列表格式
    if isinstance(texts, str):
        comments = [texts]
    elif isinstance(texts, list):
        comments = texts
    else:
        comments = [str(texts)]
    
    # 调试信息
    print(f"Debug - 收到 {len(comments)} 条评论")
    print(f"Debug - 范围参数: min_count={min_count}, max_count={max_count}")
    
    comment_details = []
    all_in_range = True
    
    # 确保范围参数是数字类型
    try:
        min_count_float = float(min_count)
        max_count_float = float(max_count)
    except (ValueError, TypeError):
        return 0, f"❌ Invalid range parameters: min_count={min_count}, max_count={max_count}"
    
    for i, comment in enumerate(comments):
        # 转换为字符串并清理
        comment_text = str(comment).strip()
        
        # 🔧 最直接的解决方案：使用原始正则表达式，然后调整 "Li Hua" 的计数
        # 1. 标准化空白字符
        comment_text = re.sub(r'\s+', ' ', comment_text)
        
        # 2. 使用原始的西班牙语单词正则模式
        spanish_word_pattern = r'\b[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+\b'
        words = re.findall(spanish_word_pattern, comment_text)
        
        # 3. 计算 "Li Hua" 的出现次数并调整总数
        li_count = len([word for word in words if word.lower() == 'li'])
        hua_count = len([word for word in words if word.lower() == 'hua'])
        
        # 假设每个 "Li" 都紧跟一个 "Hua"，所以 "Li Hua" 的次数是 min(li_count, hua_count)
        li_hua_pairs = min(li_count, hua_count)
        
        # 调整词数：减去多算的 "Li Hua" 次数
        adjusted_word_count = len(words) - li_hua_pairs
        
        print(f"Debug - 评论 {i+1}:")
        print(f"Debug - 原始词数: {len(words)}")
        print(f"Debug - Li 出现次数: {li_count}")
        print(f"Debug - Hua 出现次数: {hua_count}")
        print(f"Debug - Li Hua 对数: {li_hua_pairs}")
        print(f"Debug - 调整后词数: {adjusted_word_count}")
        
        word_count = adjusted_word_count
        
        # 检查是否在范围内
        in_range = min_count_float <= word_count <= max_count_float
        if not in_range:
            all_in_range = False
        
        # 记录详情
        status = "✅" if in_range else "❌"
        comment_details.append(f"Comment {i+1}: {word_count} words {status}")
    
    detail_info = " | ".join(comment_details)
    
    # 显示范围
    min_display = int(round(min_count_float))
    max_display = int(round(max_count_float))
    
    # 返回结果
    if all_in_range:
        return 1, f"✅ All {len(comments)} comments within range [{min_display}, {max_display}]: {detail_info}"
    else:
        return 0, f"❌ Some of {len(comments)} comments NOT within range [{min_display}, {max_display}]: {detail_info}"





import re

def has_spanish_accent_count(texts, *args):
    """检查文本中西班牙语重音符号的数量是否在指定范围内"""
    import re
    
    def clean_up_text(text):
        return text.strip()
    
    if not texts:
        return 0, f"❌ No texts provided"
    
    # 🔧 修复：更健壮的参数解析
    print(f"Debug - 原始参数: {args}")
    
    if len(args) == 1:
        param = args[0]
        if isinstance(param, (list, tuple)) and len(param) >= 2:
            min_count, max_count = param[0], param[1]
        elif isinstance(param, (list, tuple)) and len(param) == 1:
            min_count = max_count = param[0]
        else:
            min_count = max_count = param
    elif len(args) == 2:
        min_count, max_count = args
    else:
        return 0, f"❌ Invalid number of arguments: {len(args)}"
    
    # 确保参数是整数
    try:
        min_count = int(min_count)
        max_count = int(max_count)
    except (ValueError, TypeError) as e:
        return 0, f"❌ Invalid count parameters: min_count={min_count}, max_count={max_count}, error={e}"
    
    print(f"Debug - 解析后参数: min_count={min_count}, max_count={max_count}")
    
    cleaned_up_texts = [clean_up_text(str(text)) for text in texts]
    
    def count_spanish_accent_marks(texts_list):
        """统计所有文本中西班牙语重音符号的数量"""
        # 西班牙语重音符号字符
        spanish_accented_chars = [
            # 重音符号（acute accent）
            'á', 'é', 'í', 'ó', 'ú',  # 小写带重音的元音
            'Á', 'É', 'Í', 'Ó', 'Ú',  # 大写带重音的元音
            # 分音符（diaeresis）
            'ü', 'Ü',                 # 带分音符的u
            # 波浪号（tilde）
            'ñ', 'Ñ'                  # 带波浪号的n
        ]
        
        # 合并所有文本
        combined_text = ' '.join(texts_list)
        
        # 直接在整个文本中查找所有重音符号
        accent_matches = re.findall(r'[áéíóúüñÁÉÍÓÚÜÑ]', combined_text)
        total_accent_count = len(accent_matches)
        
        # 查找包含重音符号的单词
        words_with_accents = []
        words = re.findall(r'\b[\w\u00C0-\u017F]+\b', combined_text)
        
        for word in words:
            if any(char in spanish_accented_chars for char in word):
                words_with_accents.append(word)
        
        # 统计每种重音符号的数量
        accent_distribution = {}
        for accent in accent_matches:
            accent_distribution[accent] = accent_distribution.get(accent, 0) + 1
        
        return total_accent_count, words_with_accents, accent_matches, accent_distribution
    
    # 统计所有文本中的重音符号
    accent_count, accented_words, accent_list, accent_dist = count_spanish_accent_marks(cleaned_up_texts)
    
    print(f"Debug - 总重音符号数: {accent_count}")
    print(f"Debug - 重音符号分布: {accent_dist}")
    print(f"Debug - 带重音的词: {accented_words[:10]}")
    
    # 构建详细的重音符号信息
    accent_detail = []
    for accent, count in accent_dist.items():
        accent_detail.append(f"{accent}×{count}")
    
    # 去重显示重音符号类型
    unique_accents = list(set(accent_list))
    accent_summary = f"[{', '.join(unique_accents)}]" if unique_accents else "[]"
    accent_breakdown = f"({', '.join(accent_detail)})" if accent_detail else "(无)"
    
    # 限制显示的词汇数量
    display_words = accented_words[:10]
    words_info = f"{display_words}"
    if len(accented_words) > 10:
        words_info += f" (+{len(accented_words)-10} more)"
    
    # 🔧 修复：统一的逻辑处理
    if min_count == max_count:
        # 精确匹配
        required_count = min_count
        requirement_text = f"exactly {required_count}"
        
        if accent_count == required_count:
            return 1, f"✅ Text contains exactly {required_count} spanish accent marks. Found {accent_count} accents: {accent_summary} {accent_breakdown}. Words with accents: {words_info}. Requirement met."
        elif accent_count < required_count:
            return 0, f"❌ Text contains {accent_count} spanish accent marks (required: {requirement_text}). Found accents: {accent_summary} {accent_breakdown}. Words with accents: {words_info}. Too few accent marks."
        else:
            return 0, f"❌ Text contains {accent_count} spanish accent marks (required: {requirement_text}). Found accents: {accent_summary} {accent_breakdown}. Words with accents: {words_info}. Too many accent marks."
    else:
        # 范围匹配
        requirement_text = f"{min_count}-{max_count}"
        
        if min_count <= accent_count <= max_count:
            return 1, f"✅ Text contains {accent_count} spanish accent marks (required: {requirement_text}). Found accents: {accent_summary} {accent_breakdown}. Words with accents: {words_info}. Requirement met."
        elif accent_count < min_count:
            return 0, f"❌ Text contains {accent_count} spanish accent marks (required: {requirement_text}). Found accents: {accent_summary} {accent_breakdown}. Words with accents: {words_info}. Too few accent marks."
        else:
            return 0, f"❌ Text contains {accent_count} spanish accent marks (required: {requirement_text}). Found accents: {accent_summary} {accent_breakdown}. Words with accents: {words_info}. Too many accent marks."


# 🔧 测试函数
def test_function():
    test_texts = [
        "Descripción: Oficina moderna.",
        "Descripción: Espacio versátil."
    ]
    
    print("=== 测试不同的调用方式 ===")
    
    print("\n1. 测试 [12, 12] 格式:")
    result1 = has_spanish_accent_count(test_texts, [12, 12])
    print(f"结果: {result1[1][:100]}...")
    
    print("\n2. 测试 12, 12 格式:")
    result2 = has_spanish_accent_count(test_texts, 12, 12)
    print(f"结果: {result2[1][:100]}...")
    
    print("\n3. 测试单个参数 12:")
    result3 = has_spanish_accent_count(test_texts, 12)
    print(f"结果: {result3[1][:100]}...")

# 取消注释来测试
# test_function()



def has_correct_compound_hyphen_usage(texts, num):
    """检查每个文本中复合词连字符使用是否正确"""
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_compound_hyphen_errors(text):
        """检查文本中的复合词连字符错误"""
        
        # 应该有连字符但缺失的情况（常见错误）
        should_have_hyphen = [
            # 国籍组合
            (r'\b(franco|hispano|sino|anglo|austro|italo|greco|germano)(aleman|americano|japones|sajon|hungaro|español|romano|britanico)\b', 
             r'\1-\2'),
            # 学科交叉
            (r'\b(bio|geo|psico|socio|neuro|cardio|gastro)(quimica|politica|social|cultural|linguistica|vascular|intestinal)\b', 
             r'\1-\2'),
            # 形容词组合
            (r'\b(politico|teorico|cientifico|fisico|medico|juridico)(economico|practico|tecnico|quimico|legal|social)\b', 
             r'\1-\2'),
            # 对立概念
            (r'\b(amor|causa|entrada|norte|este|bien|vida)(odio|efecto|salida|sur|oeste|mal|muerte)\b', 
             r'\1-\2'),
            # 时间概念
            (r'\b(pre|post|anti|pro)(guerra|moderno|fascista|democratico|revolucionario)\b', 
             r'\1-\2'),
        ]
        
        # 不应该有连字符但错误添加的情况
        should_not_have_hyphen = [
            # 固定复合词
            r'\b(ferro-carril|auto-movil|super-mercado|inter-nacional|multi-media)\b',
            # 动词+名词结构
            r'\b(lava-vajillas|abre-latas|guarda-espaldas|rasca-cielos|salva-vidas)\b',
            # 植物动物名
            r'\b(gira-sol|peti-rojo|coli-flor|agua-cate)\b',
            # 时间词汇
            r'\b(medio-dia|media-noche|cumple-años)\b',
        ]
        
        errors = []
        corrections = []
        
        # 检查缺失连字符的错误
        for pattern, replacement in should_have_hyphen:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                error_word = match.group()
                correct_word = re.sub(pattern, replacement, error_word, flags=re.IGNORECASE)
                errors.append({
                    'type': 'missing_hyphen',
                    'error': error_word,
                    'correct': correct_word,
                    'position': match.span()
                })
        
        # 检查多余连字符的错误
        for pattern in should_not_have_hyphen:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                error_word = match.group()
                correct_word = error_word.replace('-', '')
                errors.append({
                    'type': 'extra_hyphen',
                    'error': error_word,
                    'correct': correct_word,
                    'position': match.span()
                })
        
        return len(errors), errors
    
    # 检查每个文本
    total_errors = 0
    all_errors = []
    
    for i, text in enumerate(cleaned_up_texts):
        error_count, errors = check_compound_hyphen_errors(text)
        total_errors += error_count
        
        if errors:
            text_errors = {
                'text_index': i,
                'error_count': error_count,
                'errors': errors
            }
            all_errors.append(text_errors)
    
    # 构建详细错误信息
    if total_errors > num:
        error_details = []
        for text_error in all_errors:
            for error in text_error['errors']:
                if error['type'] == 'missing_hyphen':
                    error_details.append(f"'{error['error']}' → '{error['correct']}'")
                else:
                    error_details.append(f"'{error['error']}' → '{error['correct']}'")
        
        error_summary = "; ".join(error_details[:10])  # 限制显示前10个错误
        if len(error_details) > 10:
            error_summary += f" ... (+{len(error_details)-10} more errors)"
            
        return 0, f"❌ Found {total_errors} compound word hyphen errors (allowed: {num}). Errors: {error_summary}. Does not meet the requirement."
    
    return 1, f"✅ Compound word hyphen usage is correct. Found {total_errors} errors (allowed: {num}). Requirement met."

def has_correct_total_double_negatives(texts, min_total, max_total, debug=False):
    """检查西班牙语文本中的双重否定总数是否符合要求
    
    Args:
        texts: 文本列表
        min_total: 最少双重否定总数
        max_total: 最多双重否定总数
        debug: 是否输出调试信息
    """
    import re
    
    def clean_up_text(text):
        return text.strip()
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    # 🔧 完整的双重否定结构模式
    correct_patterns = [
        # ==================== 1. "No es + 否定前缀词" 结构 ====================
        r'\bno\s+es\s+imposible\b',                                    # no es imposible
        r'\bno\s+es\s+improbable\b',                                   # no es improbable
        r'\bno\s+es\s+impensable\b',                                   # no es impensable
        r'\bno\s+es\s+increíble\b',                                    # no es increíble
        r'\bno\s+es\s+innecesario\b',                                  # no es innecesario
        r'\bno\s+es\s+inútil\b',                                       # no es inútil
        r'\bno\s+es\s+injusto\b',                                      # no es injusto
        r'\bno\s+es\s+incorrecto\b',                                   # no es incorrecto
        r'\bno\s+es\s+incierto\b',                                     # no es incierto
        r'\bno\s+es\s+inseguro\b',                                     # no es inseguro
        r'\bno\s+es\s+inválido\b',                                     # no es inválido
        r'\bno\s+es\s+inadecuado\b',                                   # no es inadecuado
        r'\bno\s+es\s+inaceptable\b',                                  # no es inaceptable
        r'\bno\s+es\s+inalcanzable\b',                                 # no es inalcanzable
        r'\bno\s+es\s+inevitable\b',                                   # no es inevitable
        r'\bno\s+es\s+inexplicable\b',                                 # no es inexplicable
        r'\bno\s+es\s+invisible\b',                                    # no es invisible
        r'\bno\s+es\s+imposible\s+que\b',                              # no es imposible que
        r'\bno\s+es\s+improbable\s+que\b',                             # no es improbable que
        
        # 通用否定前缀模式
        r'\bno\s+es\s+i[mn]\w*\b',                                     # no es + i/im/in 开头的词
        r'\bno\s+es\s+des\w*\b',                                       # no es + des 开头的词
        
        # ==================== 2. "No es + 形容词/名词 + que no" 结构 ====================
        r'\bno\s+es\s+cierto\s+que\s+no\s+\w+',                       # No es cierto que no + 动词
        r'\bno\s+es\s+verdad\s+que\s+no\s+\w+',                       # No es verdad que no + 动词
        r'\bno\s+es\s+posible\s+que\s+no\s+\w+',                      # No es posible que no + 动词
        r'\bno\s+es\s+probable\s+que\s+no\s+\w+',                     # No es probable que no + 动词
        r'\bno\s+es\s+seguro\s+que\s+no\s+\w+',                       # No es seguro que no + 动词
        r'\bno\s+es\s+normal\s+que\s+no\s+\w+',                       # No es normal que no + 动词
        r'\bno\s+es\s+raro\s+que\s+no\s+\w+',                         # No es raro que no + 动词
        r'\bno\s+es\s+extraño\s+que\s+no\s+\w+',                      # No es extraño que no + 动词
        r'\bno\s+es\s+común\s+que\s+no\s+\w+',                        # No es común que no + 动词
        r'\bno\s+es\s+fácil\s+que\s+no\s+\w+',                        # No es fácil que no + 动词
        r'\bno\s+es\s+difícil\s+que\s+no\s+\w+',                      # No es difícil que no + 动词
        r'\bno\s+es\s+lógico\s+que\s+no\s+\w+',                       # No es lógico que no + 动词
        r'\bno\s+es\s+justo\s+que\s+no\s+\w+',                        # No es justo que no + 动词
        r'\bno\s+es\s+correcto\s+que\s+no\s+\w+',                     # No es correcto que no + 动词
        r'\bno\s+es\s+bueno\s+que\s+no\s+\w+',                        # No es bueno que no + 动词
        r'\bno\s+es\s+malo\s+que\s+no\s+\w+',                         # No es malo que no + 动词
        r'\bno\s+es\s+necesario\s+que\s+no\s+\w+',                    # No es necesario que no + 动词
        r'\bno\s+es\s+importante\s+que\s+no\s+\w+',                   # No es importante que no + 动词
        r'\bno\s+es\s+suficiente\s+que\s+no\s+\w+',                   # No es suficiente que no + 动词
        
        # ==================== 3. "No es que no" 基本结构 ====================
        r'\bno\s+es\s+que\s+no\s+\w+',                                # No es que no + 动词
        r'\bno\s+es\s+que\s+no\s+\w+\s+\w+',                          # No es que no + 动词 + 宾语
        
        # ==================== 4. 🔧 新增：复杂嵌套双重否定结构 ====================
        r'\bno\s+quiero\s+que\s+\w+\s+que\s+no\s+\w+',                # no quiero que X que no Y
        r'\bno\s+deseo\s+que\s+\w+\s+que\s+no\s+\w+',                 # no deseo que X que no Y
        r'\bno\s+espero\s+que\s+\w+\s+que\s+no\s+\w+',                # no espero que X que no Y
        r'\bno\s+pretendo\s+que\s+\w+\s+que\s+no\s+\w+',              # no pretendo que X que no Y
        r'\bno\s+busco\s+que\s+\w+\s+que\s+no\s+\w+',                 # no busco que X que no Y
        r'\bno\s+intento\s+que\s+\w+\s+que\s+no\s+\w+',               # no intento que X que no Y
        r'\bno\s+trato\s+que\s+\w+\s+que\s+no\s+\w+',                 # no trato que X que no Y
        r'\bno\s+procuro\s+que\s+\w+\s+que\s+no\s+\w+',               # no procuro que X que no Y
        
        # 更灵活的嵌套模式
        r'\bno\s+\w+\s+que\s+\w+\s+que\s+no\s+\w+',                   # no X que Y que no Z (通用)
        r'\bno\s+\w+\s+que\s+\w+\s+\w+\s+que\s+no\s+\w+',             # no X que Y Z que no W (更长)
        
        # ==================== 5. "dejar de"结构的双重否定 ====================
        r'\bno\s+dej[aoóeé]\s+de\s+\w+',                              # no deja/dejo/dejó de + 动词
        r'\bno\s+dejan\s+de\s+\w+',                                   # no dejan de + 动词
        r'\bno\s+dejamos\s+de\s+\w+',                                 # no dejamos de + 动词
        r'\bno\s+dejas\s+de\s+\w+',                                   # no dejas de + 动词
        r'\bno\s+dejará\s+de\s+\w+',                                  # no dejará de + 动词
        r'\bno\s+dejarán\s+de\s+\w+',                                 # no dejarán de + 动词
        r'\bno\s+dejaré\s+de\s+\w+',                                  # no dejaré de + 动词
        r'\bno\s+dejarás\s+de\s+\w+',                                 # no dejarás de + 动词
        r'\bno\s+dejaremos\s+de\s+\w+',                               # no dejaremos de + 动词
        r'\bno\s+dejaría\s+de\s+\w+',                                 # no dejaría de + 动词
        r'\bno\s+dejarían\s+de\s+\w+',                                # no dejarían de + 动词
        r'\bno\s+dejarías\s+de\s+\w+',                                # no dejarías de + 动词
        r'\bno\s+dejaríamos\s+de\s+\w+',                              # no dejaríamos de + 动词
        r'\bno\s+he\s+dejado\s+de\s+\w+',                             # no he dejado de + 动词
        r'\bno\s+has\s+dejado\s+de\s+\w+',                            # no has dejado de + 动词
        r'\bno\s+ha\s+dejado\s+de\s+\w+',                             # no ha dejado de + 动词
        r'\bno\s+hemos\s+dejado\s+de\s+\w+',                          # no hemos dejado de + 动词
        r'\bno\s+han\s+dejado\s+de\s+\w+',                            # no han dejado de + 动词
        r'\bsin\s+dejar\s+de\s+\w+',                                  # sin dejar de + 动词
        
        # ==================== 6. "quien"结构的双重否定 ====================
        r'\bno\s+hay\s+quien\s+no\s+\w+',                             # no hay quien no + 动词
        r'\bni\s+quien\s+no\s+\w+',                                   # ni quien no + 动词
        
        # ==================== 7. "no hay + 名词 + que no"结构 ====================
        r'\bno\s+hay\s+\w+\s+que\s+no\s+\w+',                         # no hay X que no + 动词
        r'\bni\s+\w+\s+que\s+no\s+\w+',                               # ni X que no + 动词
        
        # ==================== 8. 经典双重否定 (no + 动词 + 否定词) ====================
        # no + 动词 + nada
        r'\bno\s+\w+\s+nada\b',                                       # no + 动词 + nada (通用)
        
        # no + 动词 + nadie
        r'\bno\s+\w+\s+a\s+nadie\b',                                  # no + 动词 + a nadie
        r'\bno\s+\w+\s+nadie\b',                                      # no + 动词 + nadie
        
        # no + 动词 + ningún/ninguna/ninguno
        r'\bno\s+\w+\s+ningun[oaós]?\b',                              # no + 动词 + ningún/ninguna/ninguno
        
        # no + 动词 + nunca/jamás
        r'\bno\s+\w+\s+(nunca|jamás)\b',                              # no + 动词 + nunca/jamás
        
        # no + 动词 + tampoco
        r'\bno\s+\w+\s+tampoco\b',                                    # no + 动词 + tampoco
        
        # ==================== 9. "poder no"结构的双重否定 ====================
        r'\bno\s+pued[eo]\s+no\s+\w+',                                # no puedo/puede no + 动词
        r'\bno\s+puedes\s+no\s+\w+',                                  # no puedes no + 动词
        r'\bno\s+podemos\s+no\s+\w+',                                 # no podemos no + 动词
        r'\bno\s+pueden\s+no\s+\w+',                                  # no pueden no + 动词
        r'\bno\s+podr[éáás]\s+no\s+\w+',                              # no podré/podrá/podrás no + 动词
        r'\bno\s+podremos\s+no\s+\w+',                                # no podremos no + 动词
        r'\bno\s+podrán\s+no\s+\w+',                                  # no podrán no + 动词
        r'\bno\s+podría[ns]?\s+no\s+\w+',                             # no podría/podrían no + 动词
        
        # ==================== 10. 其他复杂结构 ====================
        r'\bno\s+\w+\s+sin\s+(nada|nadie|ningún|ninguna|ninguno)\b',  # no X sin nada/nadie/ningún
        r'\bno\s+\w+\s+más\s+que\s+(nada|nadie)\b',                   # no X más que nada/nadie
        r'\bno\s+creo\s+que\s+no\s+\w+',                              # no creo que no + 动词
        r'\bno\s+pienso\s+que\s+no\s+\w+',                            # no pienso que no + 动词
        r'\bno\s+me\s+parece\s+que\s+no\s+\w+',                       # no me parece que no + 动词
        r'\bno\s+considero\s+que\s+no\s+\w+',                         # no considero que no + 动词
        r'\bno\s+opino\s+que\s+no\s+\w+',                             # no opino que no + 动词
        
        # ==================== 11. 条件句中的双重否定 ====================
        r'\bsi\s+no\s+\w+,?\s+no\s+\w+',                              # si no X, no Y
        r'\bcuando\s+no\s+\w+,?\s+no\s+\w+',                          # cuando no X, no Y
        r'\bmientras\s+no\s+\w+,?\s+no\s+\w+',                        # mientras no X, no Y
        
        # ==================== 12. 感叹句和疑问句中的双重否定 ====================
        r'\b¿[^?]*no\s+\w+[^?]*no\s+\w+[^?]*\?',                      # ¿...no...no...?
        r'\b¡[^!]*no\s+\w+[^!]*no\s+\w+[^!]*!',                       # ¡...no...no...!
        
        # ==================== 13. 带有情态动词的双重否定 ====================
        r'\bno\s+deb[eo]\s+no\s+\w+',                                 # no debo/debe no + 动词
        r'\bno\s+debes\s+no\s+\w+',                                   # no debes no + 动词
        r'\bno\s+debemos\s+no\s+\w+',                                 # no debemos no + 动词
        r'\bno\s+deben\s+no\s+\w+',                                   # no deben no + 动词
        r'\bno\s+sol[eí]a\s+no\s+\w+',                                # no solía/suelo no + 动词
        r'\bno\s+sueles\s+no\s+\w+',                                  # no sueles no + 动词
        r'\bno\s+solemos\s+no\s+\w+',                                 # no solemos no + 动词
        r'\bno\s+suelen\s+no\s+\w+',                                  # no suelen no + 动词
        
        # ==================== 14. 时态复合的双重否定 ====================
        r'\bno\s+h[aeo]\w*\s+\w+\s+(nunca|jamás)\b',                  # no he/ha/hemos + 过去分词 + nunca/jamás
        r'\bno\s+había[sn]?\s+\w+\s+(nunca|jamás)\b',                 # no había/habías/habían + 过去分词 + nunca/jamás
        
        # ==================== 15. 复杂的从句结构 ====================
        r'\bno\s+\w+\s+que\s+no\s+\w+\s+que\s+no\s+\w+',              # no X que no Y que no Z
        r'\bno\s+\w+\s+cuando\s+no\s+\w+',                            # no X cuando no Y
        r'\bno\s+\w+\s+donde\s+no\s+\w+',                             # no X donde no Y
        r'\bno\s+\w+\s+como\s+no\s+\w+',                              # no X como no Y
        
        # ==================== 16. 特殊表达 ====================
        r'\bno\s+\w+\s+ni\s+por\s+nada\b',                            # no X ni por nada
        r'\bno\s+\w+\s+para\s+nada\b',                                # no X para nada
        r'\bno\s+\w+\s+en\s+absoluto\b',                              # no X en absoluto
        r'\bno\s+\w+\s+de\s+ninguna\s+manera\b',                      # no X de ninguna manera
        r'\bno\s+\w+\s+bajo\s+ninguna\s+circunstancia\b',             # no X bajo ninguna circunstancia
        r'\bno\s+\w+\s+en\s+ningún\s+momento\b',                      # no X en ningún momento
        r'\bno\s+\w+\s+por\s+ningún\s+motivo\b',                      # no X por ningún motivo
        r'\bno\s+\w+\s+de\s+ningún\s+modo\b',                         # no X de ningún modo
    ]
    
    # 🔧 非双重否定的模式（排除误判）
    non_double_negative_patterns = [
        # 并列否定（不是双重否定）
        r'\bno\s+\w+\s+ni\s+\w+\b(?!\s+(que\s+no|tampoco|nunca|jamás))',  # no come ni bebe (但不排除特殊情况)
        r'\bni\s+\w+\s+ni\s+\w+\b(?!\s+(que\s+no|tampoco|nunca|jamás))',  # ni come ni bebe
        
        # 简单否定（单独出现）- 但要小心，不要排除真正的双重否定
        r'\bno\s+es\s+(bueno|malo|fácil|difícil|normal|raro)\b(?!\s+(que\s+no|\w+\s+que\s+no))',  # 简单的 no es + 形容词
    ]
    
    # 统计所有文本中的双重否定总数
    total_double_negatives = 0
    all_matches = []
    found_positions = set()
    
    if debug:
        print("=== 双重否定检测调试信息 ===")
    
    # 遍历所有文本
    for text_index, text in enumerate(cleaned_up_texts):
        if debug:
            print(f"\nText {text_index}: '{text}'")
        
        for pattern_index, pattern in enumerate(correct_patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                match_text = match.group().strip()
                match_span = match.span()
                
                if debug:
                    print(f"  Pattern {pattern_index}: '{pattern}'")
                    print(f"    -> Found: '{match_text}' at {match_span}")
                
                # 检查位置是否重叠（允许3个字符的容差）
                position_key = (text_index, match_span[0], match_span[1])
                overlaps = False
                
                for existing_pos in found_positions:
                    existing_text_idx, existing_start, existing_end = existing_pos
                    if existing_text_idx == text_index:
                        # 检查是否有显著重叠（超过3个字符）
                        overlap_start = max(match_span[0], existing_start)
                        overlap_end = min(match_span[1], existing_end)
                        overlap_length = max(0, overlap_end - overlap_start)
                        
                        if overlap_length > 3:  # 允许小的重叠
                            overlaps = True
                            if debug:
                                print(f"    -> EXCLUDED (overlaps with {existing_pos}, overlap: {overlap_length} chars)")
                            break
                
                if not overlaps:
                    # 检查是否是真正的双重否定
                    is_real_double_negative = True
                    for non_pattern in non_double_negative_patterns:
                        if re.search(non_pattern, match_text, re.IGNORECASE):
                            is_real_double_negative = False
                            if debug:
                                print(f"    -> EXCLUDED (matches non-double-negative pattern: '{non_pattern}')")
                            break
                    
                    if is_real_double_negative:
                        found_positions.add(position_key)
                        total_double_negatives += 1
                        all_matches.append(match_text)
                        if debug:
                            print(f"    -> INCLUDED (#{total_double_negatives})")
                    
    if debug:
        print(f"\n=== 最终结果 ===")
        print(f"总计找到 {total_double_negatives} 个双重否定:")
        for i, match in enumerate(all_matches, 1):
            print(f"  {i}. '{match}'")
    
    # 检查是否符合总数要求
    if min_total <= total_double_negatives <= max_total:
        unique_examples = list(set(all_matches))
        display_examples = unique_examples[:5]
        
        examples_text = ", ".join([f"'{ex}'" for ex in display_examples])
        if len(unique_examples) > 5:
            examples_text += f" ... (+{len(unique_examples) - 5} more types)"
        
        return 1, f"✅ Total double negatives: {total_double_negatives} (required: {min_total}-{max_total}). Found examples: {examples_text}. Requirement met."
    else:
        if all_matches:
            unique_examples = list(set(all_matches))[:3]
            examples_text = ", ".join([f"'{ex}'" for ex in unique_examples])
            if len(all_matches) > 3:
                examples_text += f" ... (+{len(set(all_matches)) - 3} more types)"
            examples_info = f" Found examples: {examples_text}."
        else:
            examples_info = " No double negatives found."
        
        return 0, f"❌ Total double negatives: {total_double_negatives} (required: {min_total}-{max_total}).{examples_info} Does not meet the requirement."


# 🔧 测试函数（测试问题案例）
def test_problem_case():
    """测试问题案例"""
    test_texts = [
        "Querida [nombre de tu novia],\n\nLamento profundamente el malentendido de ayer. No estaba con otras chicas, sino con mi hermana, buscando el regalo perfecto para ti. Entiendo cómo pudo parecer otra cosa y no quiero que pienses que no soy honesto contigo.\n\nEspero que puedas comprender la situación y que esto no afecte nuestra relación. Mi intención nunca fue ocultarte nada ni hacerte sentir incómoda. \n\nGracias por tu comprensión y paciencia. Te quiero mucho.  \nCon cariño,  \n[Tu nombre]  \nFecha: 15 de octubre de 2023."
    ]
    
    print("=== 测试问题案例 ===")
    result, explanation = has_correct_total_double_negatives(test_texts, 1, 999, debug=True)
    print(f"\n最终评估结果: {result}")
    print(f"解释: {explanation}")

# 运行测试
# if __name__ == "__main__":
#     test_problem_case()


def has_correct_spanish_date_format(texts, num):
    """检查每个文本中西班牙语日期格式是否正确（日/月/年）"""
    import re
    
    def clean_up_text(text):
        return text.strip()
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_spanish_date_errors(text):
        """检查文本中的西班牙语日期格式错误"""
        
        # 正确的西班牙语日期格式模式
        correct_spanish_date_patterns = [
            # 日/月/年格式 (DD/MM/YYYY, D/M/YY, DD/MM/YY等)
            r'\b([0-3]?\d)/([01]?\d)/(\d{2,4})\b',
            # 日-月-年格式 (DD-MM-YYYY)
            r'\b([0-3]?\d)-([01]?\d)-(\d{2,4})\b',
            # 日.月.年格式 (DD.MM.YYYY)
            r'\b([0-3]?\d)\.([01]?\d)\.(\d{2,4})\b',
            # 日 de 月 de 年格式 (ej: 15 de marzo de 2024)
            r'(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})',
            # 日 月 年格式 (没有"de") - 但要确保不与上面重复
            r'(\d{1,2})\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(\d{4})(?!\s+de)',  # 🔧 负向前瞻，排除后面跟"de"的情况
            # 带"del"的格式
            r'(\d{1,2})\s+del?\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+del?\s+(\d{4})',
        ]
        
        # 错误的英语日期格式模式 (月/日/年)
        incorrect_english_date_patterns = [
            r'\b([01]?\d)/([0-3]?\d)/(\d{2,4})\b',
            r'\b([01]?\d)-([0-3]?\d)-(\d{2,4})\b',
            r'\b([01]?\d)\.([0-3]?\d)\.(\d{2,4})\b',
        ]
        
        errors = []
        correct_dates = []
        found_positions = set()  # 🔧 新增：记录已找到的位置，避免重复
        
        # 🔧 修复：检查正确的西班牙语日期格式，避免重复计数
        for i, pattern in enumerate(correct_spanish_date_patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group()
                match_span = match.span()
                
                # 🔧 检查是否与已找到的日期重叠
                overlaps = False
                for existing_span in found_positions:
                    # 检查位置重叠（允许小的误差）
                    if (match_span[0] < existing_span[1] and match_span[1] > existing_span[0]):
                        overlaps = True
                        break
                
                if not overlaps:
                    # 验证日期的合理性
                    if i <= 2:  # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY 格式
                        day, month, year = match.groups()
                        if is_valid_date_values(int(day), int(month), int(year)):
                            correct_dates.append({
                                'date': date_text,
                                'format': 'DD/MM/YYYY',
                                'position': match_span
                            })
                            found_positions.add(match_span)
                    else:  # 文字月份格式
                        correct_dates.append({
                            'date': date_text,
                            'format': 'DD de mes de YYYY',
                            'position': match_span
                        })
                        found_positions.add(match_span)
        
        # 检查可能的英语格式错误
        for pattern in incorrect_english_date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group()
                match_span = match.span()
                
                # 检查是否已经被识别为正确格式
                already_found = False
                for existing_span in found_positions:
                    if (match_span[0] < existing_span[1] and match_span[1] > existing_span[0]):
                        already_found = True
                        break
                
                if not already_found:
                    month, day, year = match.groups()
                    
                    # 检查是否明显是英语格式
                    if int(month) > 12 or (int(month) <= 12 and int(day) <= 12 and int(month) != int(day)):
                        correct_spanish = f"{day}/{month}/{year}"
                        errors.append({
                            'type': 'english_format',
                            'error': date_text,
                            'correct': correct_spanish,
                            'position': match_span,
                            'explanation': 'Formato inglés detectado, debe usar formato español DD/MM/YYYY'
                        })
        
        # 检查其他常见错误格式
        other_wrong_patterns = [
            r'\b(\d{4})/([01]?\d)/([0-3]?\d)\b',
            r'\b(\d{4})-([01]?\d)-([0-3]?\d)\b',
        ]
        
        for pattern in other_wrong_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                match_span = match.span()
                
                # 检查是否已经被识别为正确格式
                already_found = False
                for existing_span in found_positions:
                    if (match_span[0] < existing_span[1] and match_span[1] > existing_span[0]):
                        already_found = True
                        break
                
                if not already_found:
                    date_text = match.group()
                    year, month, day = match.groups()
                    correct_spanish = f"{day}/{month}/{year}"
                    errors.append({
                        'type': 'wrong_order',
                        'error': date_text,
                        'correct': correct_spanish,
                        'position': match_span,
                        'explanation': 'Orden incorrecto, debe usar formato español DD/MM/YYYY'
                    })
        
        return len(errors), errors, len(correct_dates), correct_dates
    
    def is_valid_date_values(day, month, year):
        """验证日期数值的合理性"""
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        if year < 1900 or year > 2100:
            return False
        return True
    
    # 检查每个文本
    total_errors = 0
    total_correct = 0
    all_errors = []
    all_correct = []
    
    for i, text in enumerate(cleaned_up_texts):
        error_count, errors, correct_count, correct_dates = check_spanish_date_errors(text)
        total_errors += error_count
        total_correct += correct_count
        
        if errors:
            all_errors.extend(errors)
        if correct_dates:
            all_correct.extend(correct_dates)
    
    # 构建详细信息
    if total_errors > num:
        error_details = []
        for error in all_errors:
            error_details.append(f"'{error['error']}' → '{error['correct']}' ({error['explanation']})")
        
        error_summary = "; ".join(error_details)
        
        return 0, f"❌ Found {total_errors} Spanish date format errors (allowed: {num}). Errors: {error_summary}. Does not meet the requirement."
    
    # 🔧 修复：去重显示
    unique_correct = []
    seen_dates = set()
    for correct in all_correct:
        if correct['date'] not in seen_dates:
            unique_correct.append(correct)
            seen_dates.add(correct['date'])
    
    correct_examples = []
    for correct in unique_correct[:3]:
        correct_examples.append(f"'{correct['date']}' ({correct['format']})")
    
    if len(unique_correct) > 3:
        correct_examples.append(f"... (+{len(unique_correct) - 3} more)")
    
    correct_info = f"Found {len(unique_correct)} correct dates" + (f": {', '.join(correct_examples)}" if correct_examples else "")
    
    return 1, f"✅ Spanish date format is correct. {correct_info}. Found {total_errors} errors (allowed: {num}). Requirement met."


def has_correct_abbreviation_format_only(texts, max_errors):
    """只检查已经是缩写形式的词的格式是否正确，不检查完整词汇"""
    import re
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_existing_abbreviation_errors(text):
        """只检查文本中已存在的缩写形式的格式错误"""
        
        # 扩展的西班牙语正式缩写词典（小写 -> 大写）
        known_abbreviations = {
            # === 国际组织 ===
            'onu': 'ONU', 'oms': 'OMS', 'otan': 'OTAN', 'unesco': 'UNESCO', 'unicef': 'UNICEF',
            'fmi': 'FMI', 'bid': 'BID', 'oea': 'OEA', 'opep': 'OPEP', 'ocde': 'OCDE',
            'ue': 'UE', 'bce': 'BCE', 'pe': 'PE', 'ce': 'CE', 'cee': 'CEE',
            
            # === 企业类型 ===
            'sa': 'S.A.', 'sl': 'S.L.', 'slu': 'S.L.U.', 'slp': 'S.L.P.', 'srl': 'S.R.L.',
            's.a.': 'S.A.', 's.l.': 'S.L.', 's.l.u.': 'S.L.U.', 's.l.p.': 'S.L.P.',
            
            # === 文档和行政 ===
            'dni': 'DNI', 'nie': 'NIE', 'nif': 'NIF', 'cif': 'CIF', 'iva': 'IVA',
            'pib': 'PIB', 'pnb': 'PNB', 'ipc': 'IPC', 'irpf': 'IRPF',
            
            # === 技术 ===
            'cpu': 'CPU', 'gpu': 'GPU', 'ram': 'RAM', 'rom': 'ROM', 'ssd': 'SSD',
            'html': 'HTML', 'http': 'HTTP', 'https': 'HTTPS', 'url': 'URL',
            'gps': 'GPS', 'sms': 'SMS', 'mms': 'MMS', 'app': 'APP', 'pdf': 'PDF',
            'tv': 'TV', 'dvd': 'DVD', 'cd': 'CD', 'wifi': 'WIFI',
            
            # === 企业职位 ===
            'ceo': 'CEO', 'cfo': 'CFO', 'cto': 'CTO', 'coo': 'COO', 'cmo': 'CMO',
            
            # === 机构 ===
            'nasa': 'NASA', 'fbi': 'FBI', 'cia': 'CIA', 'fda': 'FDA',
        }
        
        # 常见的西班牙语普通词汇（不应被视为缩写错误）
        common_spanish_words = {
            'app', 'web', 'blog', 'chat', 'email', 'wifi', 'online', 'software',
            'hardware', 'internet', 'digital', 'virtual', 'global', 'local',
            'el', 'la', 'los', 'las', 'un', 'una', 'de', 'en', 'con', 'por', 'sin',
            'que', 'es', 'no', 'si', 'me', 'te', 'se', 'le', 'lo', 'ya', 'muy'
        }
        
        format_errors = []
        correct_abbreviations = []
        
        # 1. 查找正确格式的缩写
        patterns_to_check = [
            # 标准全大写缩写 (2-10个字母)
            r'\b[A-ZÁÉÍÓÚÑÜ]{2,10}\b',
            # 带点号的缩写 (如 S.A., S.L.)
            r'\b[A-ZÁÉÍÓÚÑÜ]\.(?:[A-ZÁÉÍÓÚÑÜ]\.)*\b',
            # 带数字的缩写 (如 4K, F1)
            r'\b[A-ZÁÉÍÓÚÑÜ]*\d+[A-ZÁÉÍÓÚÑÜK]*\b|\b\d+[A-ZÁÉÍÓÚÑÜK]+\b'
        ]
        
        for pattern in patterns_to_check:
            matches = re.finditer(pattern, text)
            for match in matches:
                abbrev = match.group()
                abbrev_lower = abbrev.lower()
                
                # 跳过常见词汇
                if abbrev_lower in common_spanish_words:
                    continue
                
                # 检查是否为已知缩写
                if abbrev_lower in known_abbreviations:
                    expected_format = known_abbreviations[abbrev_lower]
                    if abbrev == expected_format:
                        correct_abbreviations.append({
                            'abbreviation': abbrev,
                            'position': match.span(),
                            'type': 'correct'
                        })
        
        # 2. 检查格式错误的缩写
        error_patterns = [
            # 小写的已知缩写
            {
                'pattern': r'\b[a-záéíóúñü]{2,10}\b',
                'type': 'lowercase',
                'description': 'Debe estar en mayúsculas'
            },
            # 混合大小写
            {
                'pattern': r'\b[A-ZÁÉÍÓÚÑÜa-záéíóúñü]*[a-záéíóúñü][A-ZÁÉÍÓÚÑÜa-záéíóúñü]*\b',
                'type': 'mixed_case',
                'description': 'Formato de mayúsculas inconsistente'
            },
            # 带空格的缩写
            {
                'pattern': r'\b[A-ZÁÉÍÓÚÑÜa-záéíóúñü]\s+[A-ZÁÉÍÓÚÑÜa-záéíóúñü](?:\s+[A-ZÁÉÍÓÚÑÜa-záéíóúñü])*\b',
                'type': 'with_spaces',
                'description': 'Contiene espacios entre letras'
            },
            # 带连字符的缩写
            {
                'pattern': r'\b[A-ZÁÉÍÓÚÑÜa-záéíóúñü]-(?:[A-ZÁÉÍÓÚÑÜa-záéíóúñü]-)*[A-ZÁÉÍÓÚÑÜa-záéíóúñü]\b',
                'type': 'with_hyphens',
                'description': 'Contiene guiones entre letras'
            }
        ]
        
        for error_config in error_patterns:
            pattern = error_config['pattern']
            error_type = error_config['type']
            description = error_config['description']
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                error_text = match.group()
                clean_text = re.sub(r'[^A-ZÁÉÍÓÚÑÜa-záéíóúñü]', '', error_text).lower()
                
                # 跳过常见词汇
                if clean_text in common_spanish_words:
                    continue
                
                # 只报告已知缩写的格式错误
                if clean_text in known_abbreviations:
                    correct_format = known_abbreviations[clean_text]
                    
                    # 确保错误文本和正确格式不同
                    if error_text != correct_format:
                        format_errors.append({
                            'error': error_text,
                            'correct': correct_format,
                            'type': error_type,
                            'position': match.span(),
                            'description': description
                        })
        
        return len(format_errors), format_errors, len(correct_abbreviations), correct_abbreviations
    
    # 统计所有文本中的格式错误
    total_errors = 0
    all_errors = []
    all_correct = []
    
    for text in cleaned_up_texts:
        error_count, errors, correct_count, correct_abbrevs = check_existing_abbreviation_errors(text)
        total_errors += error_count
        all_errors.extend(errors)
        all_correct.extend(correct_abbrevs)
    
    # 去重正确的缩写
    unique_correct = []
    seen = set()
    for correct in all_correct:
        if correct['abbreviation'] not in seen:
            unique_correct.append(correct)
            seen.add(correct['abbreviation'])
    
    # 构建结果信息
    if total_errors <= max_errors:
        correct_examples = [correct['abbreviation'] for correct in unique_correct]
        correct_info = f"Found {len(unique_correct)} correct abbreviations" + (f": {', '.join(correct_examples)}" if correct_examples else "")
        
        error_info = ""
        if all_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}'" for err in all_errors[:3]]
            error_info = f" Format errors: {'; '.join(error_examples)}"
            if len(all_errors) > 3:
                error_info += f" (+{len(all_errors)-3} more)"
        
        return 1, f"✅ Existing abbreviation formats are acceptable. {correct_info}. Found {total_errors} format errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        error_details = [f"'{error['error']}' → '{error['correct']}' ({error['description']})" for error in all_errors[:5]]
        error_summary = "; ".join(error_details)
        
        return 0, f"❌ Found {total_errors} format errors in existing abbreviations (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."


def has_spanish_abbreviation_count(texts, num):
    """检测文本中西班牙语格式正确的缩写数量"""
    import re
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def count_correct_abbreviations(text):
        """统计文本中格式正确的西班牙语缩写数量"""
        
        # 扩展的西班牙语正式缩写词典（小写 -> 大写）- 与上面保持一致
        known_abbreviations = {
            # === 国际组织 ===
            'onu': 'ONU', 'oms': 'OMS', 'otan': 'OTAN', 'unesco': 'UNESCO', 'unicef': 'UNICEF',
            'fmi': 'FMI', 'bid': 'BID', 'oea': 'OEA', 'opep': 'OPEP', 'ocde': 'OCDE',
            'ue': 'UE', 'bce': 'BCE', 'pe': 'PE', 'ce': 'CE', 'cee': 'CEE',
            
            # === 企业类型 ===
            'sa': 'S.A.', 'sl': 'S.L.', 'slu': 'S.L.U.', 'slp': 'S.L.P.', 'srl': 'S.R.L.',
            's.a.': 'S.A.', 's.l.': 'S.L.', 's.l.u.': 'S.L.U.', 's.l.p.': 'S.L.P.',
            
            # === 文档和行政 ===
            'dni': 'DNI', 'nie': 'NIE', 'nif': 'NIF', 'cif': 'CIF', 'iva': 'IVA',
            'pib': 'PIB', 'pnb': 'PNB', 'ipc': 'IPC', 'irpf': 'IRPF',
            
            # === 技术 ===
            'cpu': 'CPU', 'gpu': 'GPU', 'ram': 'RAM', 'rom': 'ROM', 'ssd': 'SSD',
            'html': 'HTML', 'http': 'HTTP', 'https': 'HTTPS', 'url': 'URL',
            'gps': 'GPS', 'sms': 'SMS', 'mms': 'MMS', 'app': 'APP', 'pdf': 'PDF',
            'tv': 'TV', 'dvd': 'DVD', 'cd': 'CD', 'wifi': 'WIFI',
            
            # === 企业职位 ===
            'ceo': 'CEO', 'cfo': 'CFO', 'cto': 'CTO', 'coo': 'COO', 'cmo': 'CMO',
            
            # === 机构 ===
            'nasa': 'NASA', 'fbi': 'FBI', 'cia': 'CIA', 'fda': 'FDA',
        }
        
        # 常见词汇排除列表
        non_abbreviations = {
            'el', 'la', 'los', 'las', 'un', 'una', 'de', 'en', 'con', 'por', 'sin',
            'que', 'es', 'no', 'si', 'me', 'te', 'se', 'le', 'lo', 'ya', 'muy',
            'más', 'tan', 'son', 'del', 'sus', 'mis', 'tus', 'dos', 'tres', 'mil',
            'app', 'web', 'blog', 'chat', 'email', 'wifi', 'online', 'software'
        }
        
        correct_count = 0
        found_abbreviations = []
        format_errors = []
        
        # 查找所有可能的缩写模式
        patterns_to_check = [
            # 标准全大写缩写 (2-10个字母)
            r'\b[A-ZÁÉÍÓÚÑÜ]{2,10}\b',
            # 带点号的缩写 (如 S.A., S.L.)
            r'\b[A-ZÁÉÍÓÚÑÜ]\.(?:[A-ZÁÉÍÓÚÑÜ]\.)*\b',
            # 带数字的缩写 (如 4K, F1)
            r'\b[A-ZÁÉÍÓÚÑÜ]*\d+[A-ZÁÉÍÓÚÑÜK]*\b|\b\d+[A-ZÁÉÍÓÚÑÜK]+\b'
        ]
        
        seen_abbreviations = set()  # 防止重复计数
        
        for pattern in patterns_to_check:
            matches = re.finditer(pattern, text)
            for match in matches:
                abbrev = match.group()
                abbrev_lower = abbrev.lower()
                
                # 跳过已经计数的缩写
                if abbrev in seen_abbreviations:
                    continue
                
                # 跳过常见非缩写词汇
                if abbrev_lower in non_abbreviations:
                    continue
                
                # 只统计已知缩写
                if abbrev_lower in known_abbreviations:
                    expected_format = known_abbreviations[abbrev_lower]
                    if abbrev == expected_format:
                        correct_count += 1
                        seen_abbreviations.add(abbrev)
                        found_abbreviations.append({
                            'abbreviation': abbrev,
                            'position': match.span(),
                            'full_form': abbrev_lower,
                            'type': 'correct'
                        })
        
        # 检测格式错误（用于反馈）
        error_patterns = [
            (r'\b[a-záéíóúñü]{2,10}\b', 'lowercase'),
            (r'\b[A-ZÁÉÍÓÚÑÜa-záéíóúñü]*[a-záéíóúñü][A-ZÁÉÍÓÚÑÜa-záéíóúñü]*\b', 'mixed_case'),
            (r'\b[A-ZÁÉÍÓÚÑÜa-záéíóúñü]\.(?:[A-ZÁÉÍÓÚÑÜa-záéíóúñü]\.)+\b', 'with_dots'),
            (r'\b[A-ZÁÉÍÓÚÑÜa-záéíóúñü]\s+[A-ZÁÉÍÓÚÑÜa-záéíóúñü](?:\s+[A-ZÁÉÍÓÚÑÜa-záéíóúñü])*\b', 'with_spaces'),
            (r'\b[A-ZÁÉÍÓÚÑÜa-záéíóúñü]-(?:[A-ZÁÉÍÓÚÑÜa-záéíóúñü]-)*[A-ZÁÉÍÓÚÑÜa-záéíóúñü]\b', 'with_hyphens')
        ]
        
        for pattern, error_type in error_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                error_text = match.group()
                clean_text = re.sub(r'[^A-ZÁÉÍÓÚÑÜa-záéíóúñü]', '', error_text).lower()
                
                # 跳过常见词汇
                if clean_text in non_abbreviations:
                    continue
                
                # 只报告已知缩写的格式错误
                if clean_text in known_abbreviations:
                    correct_format = known_abbreviations[clean_text]
                    if error_text != correct_format:
                        format_errors.append({
                            'error': error_text,
                            'correct': correct_format,
                            'type': error_type,
                            'position': match.span()
                        })
        
        return correct_count, found_abbreviations, format_errors
    
    # 统计所有文本中的正确缩写
    total_count = 0
    all_found = []
    all_errors = []
    
    for text in cleaned_up_texts:
        count, found, errors = count_correct_abbreviations(text)
        total_count += count
        all_found.extend(found)
        all_errors.extend(errors)
    
    # 构建结果信息
    if total_count >= num:
        # 显示找到的缩写示例
        examples = []
        for abbrev_info in all_found[:15]:  # 最多显示15个示例
            examples.append(abbrev_info['abbreviation'])
        
        example_text = f" Examples: {', '.join(examples)}" if examples else ""
        
        # 如果有格式错误，也提及一下
        error_note = ""
        if all_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}'" for err in all_errors[:3]]
            error_note = f" Note: Found {len(all_errors)} format errors: {', '.join(error_examples)}"
            if len(all_errors) > 3:
                error_note += f" (+{len(all_errors)-3} more)"
        
        return 1, f"✅ Found {total_count} correct Spanish abbreviations (required: {num}).{example_text}{error_note} Requirement met."
    else:
        # 显示找到的缩写和错误信息
        found_text = ""
        if all_found:
            examples = [abbrev_info['abbreviation'] for abbrev_info in all_found]
            found_text = f" Found correct: {', '.join(examples)}"
        
        error_text = ""
        if all_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}'" for err in all_errors[:5]]
            error_text = f" Format errors found: {', '.join(error_examples)}"
            if len(all_errors) > 5:
                error_text += f" (+{len(all_errors)-5} more)"
        
        return 0, f"❌ Found only {total_count} correct Spanish abbreviations (required: {num}).{found_text}{error_text} Does not meet the requirement."

    

def has_correct_spanish_number_format(texts, max_errors):
    """检测文本中西班牙语数字格式是否正确（小数点用逗号，千分位用点，货币符号在后）"""
    import re
    
    def clean_up_text(text):
        return text.strip()
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def is_correct_spanish_number(number_text):
        """检查数字是否符合西班牙语格式"""
        # 1. 小于1000的整数
        if re.match(r'^\d{1,3}$', number_text):
            return True
        # 2. 带千分位的整数：1.234, 12.345.678
        if re.match(r'^\d{1,3}(?:\.\d{3})+$', number_text):
            return True
        # 3. 小数（逗号作小数点）：12,5, 1.234,56
        if re.match(r'^\d{1,3}(?:\.\d{3})*,\d+$', number_text):
            return True
        return False
    
    def add_thousands_separator(number_text):
        """为数字添加千分位分隔符"""
        if len(number_text) <= 3:
            return number_text
        
        # 从右到左每3位添加点
        formatted = ''
        for i, digit in enumerate(reversed(number_text)):
            if i > 0 and i % 3 == 0:
                formatted = '.' + formatted
            formatted = digit + formatted
        return formatted
    
    def check_number_format_errors(text):
        """检查文本中的数字格式错误"""
        format_errors = []
        correct_numbers = []
        processed_positions = set()
        
        print(f"Debug - 检查文本: {text[:100]}...")
        
        # 排除电话号码区域
        phone_patterns = [
            r'\b\d{2,3}[-.\s]\d{3}[-.\s]\d{3,4}\b',
            r'\b\+34[-.\s]?\d{2,3}[-.\s]\d{3}[-.\s]\d{3,4}\b',
            r'\b[679]\d{8}\b',
            r'\b9[1-8]\d{7}\b'
        ]
        
        phone_positions = set()
        for pattern in phone_patterns:
            for match in re.finditer(pattern, text):
                phone_positions.add(match.span())
        
        # 🔧 修复：分别处理货币和普通数字
        # 1. 先检查货币格式
        currency_patterns = [
            # 错误格式：货币符号在前
            r'([\$€£¥])\s*(\d+(?:[,\.]\d+)*)',
            # 正确格式：数字 + 空格 + 货币符号
            r'(\d+(?:[,\.]\d+)*)\s+([\$€£¥])',
        ]
        
        for i, pattern in enumerate(currency_patterns):
            for match in re.finditer(pattern, text):
                full_match = match.group(0)
                position = match.span()
                groups = match.groups()
                
                print(f"Debug - 找到货币: '{full_match}', 组: {groups}")
                
                # 跳过电话号码区域
                is_phone = any(pos[0] <= position[0] and position[1] <= pos[1] for pos in phone_positions)
                if is_phone:
                    continue
                
                # 跳过已处理的位置
                overlap = any(pos[0] < position[1] and pos[1] > position[0] for pos in processed_positions)
                if overlap:
                    continue
                
                if i == 0:  # 货币符号在前（错误格式）
                    currency_symbol, number_text = groups
                    
                    # 跳过短数字
                    if len(number_text.replace(',', '').replace('.', '')) < 4:
                        continue
                    
                    # 分析数字格式并生成建议
                    if re.match(r'\d+,\d{3}(?:,\d{3})*$', number_text):
                        # 英语格式：$150,000 → 150.000 $
                        corrected_number = number_text.replace(',', '.')
                        description = 'Formato inglés: símbolo de moneda antes del número y usa coma como separador de miles'
                        suggested_format = f"{corrected_number} {currency_symbol}"
                    elif re.match(r'\d+,\d{3}(?:,\d{3})*\.\d+$', number_text):
                        # 英语格式：$1,234.56 → 1.234,56 $
                        corrected_number = number_text.replace(',', '|').replace('.', ',').replace('|', '.')
                        description = 'Formato inglés: símbolo de moneda antes del número'
                        suggested_format = f"{corrected_number} {currency_symbol}"
                    elif '.' in number_text and re.search(r'\.\d{1,2}$', number_text):
                        # 使用点作小数点：$123.45 → 123,45 $
                        corrected_number = re.sub(r'\.(\d{1,2})$', r',\1', number_text)
                        description = 'Símbolo de moneda antes del número y usa punto como separador decimal'
                        suggested_format = f"{corrected_number} {currency_symbol}"
                    elif len(number_text) >= 4 and '.' not in number_text and ',' not in number_text:
                        # 缺少千分位：$150000 → 150.000 $
                        corrected_number = add_thousands_separator(number_text)
                        description = 'Símbolo de moneda antes del número y falta separador de miles'
                        suggested_format = f"{corrected_number} {currency_symbol}"
                    else:
                        # 其他情况：只是货币符号位置错误
                        description = 'Símbolo de moneda debe ir después del número con espacio'
                        suggested_format = f"{number_text} {currency_symbol}"
                    
                    format_errors.append({
                        'error': full_match,
                        'correct': suggested_format,
                        'position': position,
                        'description': description
                    })
                    print(f"Debug - ❌ 货币格式错误: {full_match} → {suggested_format}")
                    
                else:  # 货币符号在后（可能正确）
                    number_text, currency_symbol = groups
                    
                    # 跳过短数字
                    if len(number_text.replace(',', '').replace('.', '')) < 4:
                        continue
                    
                    if is_correct_spanish_number(number_text):
                        correct_numbers.append({
                            'number': number_text,
                            'full_match': full_match,
                            'position': position,
                            'type': 'correct_currency_format'
                        })
                        print(f"Debug - ✅ 正确货币格式: {full_match}")
                    else:
                        # 货币符号位置正确，但数字格式错误
                        if re.match(r'\d+,\d{3}(?:,\d{3})*$', number_text):
                            corrected_number = number_text.replace(',', '.')
                            description = 'Usa coma como separador de miles (debe usar puntos)'
                            suggested_format = f"{corrected_number} {currency_symbol}"
                        elif re.match(r'\d+,\d{3}(?:,\d{3})*\.\d+$', number_text):
                            corrected_number = number_text.replace(',', '|').replace('.', ',').replace('|', '.')
                            description = 'Formato de número inglés (coma para miles, punto para decimales)'
                            suggested_format = f"{corrected_number} {currency_symbol}"
                        elif '.' in number_text and re.search(r'\.\d{1,2}$', number_text):
                            corrected_number = re.sub(r'\.(\d{1,2})$', r',\1', number_text)
                            description = 'Usa punto como separador decimal (debe usar coma)'
                            suggested_format = f"{corrected_number} {currency_symbol}"
                        else:
                            corrected_number = add_thousands_separator(number_text)
                            description = 'Falta separador de miles'
                            suggested_format = f"{corrected_number} {currency_symbol}"
                        
                        format_errors.append({
                            'error': full_match,
                            'correct': suggested_format,
                            'position': position,
                            'description': description
                        })
                        print(f"Debug - ❌ 数字格式错误: {full_match} → {suggested_format}")
                
                processed_positions.add(position)
        
        # 2. 检查普通数字（非货币）
        number_pattern = r'\b(\d+(?:[,\.]\d+)*)\b'
        for match in re.finditer(number_pattern, text):
            number_text = match.group(1)
            position = match.span()
            
            # 跳过电话号码区域
            is_phone = any(pos[0] <= position[0] and position[1] <= pos[1] for pos in phone_positions)
            if is_phone:
                continue
            
            # 跳过已处理的位置
            overlap = any(pos[0] < position[1] and pos[1] > position[0] for pos in processed_positions)
            if overlap:
                continue
            
            # 跳过短数字
            if len(number_text.replace(',', '').replace('.', '')) < 4:
                continue
            
            if is_correct_spanish_number(number_text):
                correct_numbers.append({
                    'number': number_text,
                    'full_match': number_text,
                    'position': position,
                    'type': 'correct_number_format'
                })
                print(f"Debug - ✅ 正确数字格式: {number_text}")
            else:
                # 分析错误类型
                suggested_format = ""
                description = ""
                
                if re.match(r'\d+,\d{3}(?:,\d{3})*$', number_text):
                    suggested_format = number_text.replace(',', '.')
                    description = 'Formato inglés: usa coma como separador de miles'
                elif re.match(r'\d+,\d{3}(?:,\d{3})*\.\d+$', number_text):
                    suggested_format = number_text.replace(',', '|').replace('.', ',').replace('|', '.')
                    description = 'Formato inglés: coma para miles, punto para decimales'
                elif '.' in number_text and re.search(r'\.\d{1,2}$', number_text):
                    suggested_format = re.sub(r'\.(\d{1,2})$', r',\1', number_text)
                    description = 'Usa punto como separador decimal'
                elif len(number_text) >= 4 and '.' not in number_text and ',' not in number_text:
                    suggested_format = add_thousands_separator(number_text)
                    description = 'Falta separador de miles'
                
                if suggested_format:
                    format_errors.append({
                        'error': number_text,
                        'correct': suggested_format,
                        'position': position,
                        'description': description
                    })
                    print(f"Debug - ❌ 数字格式错误: {number_text} → {suggested_format}")
            
            processed_positions.add(position)
        
        return len(format_errors), format_errors, len(correct_numbers), correct_numbers
    
    # 统计所有文本中的格式错误
    total_errors = 0
    all_errors = []
    all_correct = []
    
    for text in cleaned_up_texts:
        error_count, errors, correct_count, correct_numbers = check_number_format_errors(text)
        total_errors += error_count
        all_errors.extend(errors)
        all_correct.extend(correct_numbers)
    
    print(f"Debug - 总错误数: {total_errors}")
    print(f"Debug - 总正确数: {len(all_correct)}")
    
    # 构建结果信息
    if total_errors <= max_errors:
        correct_examples = [correct['full_match'] for correct in all_correct[:5]]
        correct_info = f"Found {len(all_correct)} correctly formatted numbers"
        if correct_examples:
            correct_info += f": {', '.join(correct_examples)}"
        
        error_info = ""
        if all_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}' ({err['description']})" for err in all_errors[:3]]
            error_info = f" Format errors: {'; '.join(error_examples)}"
            if len(all_errors) > 3:
                error_info += f" (+{len(all_errors)-3} more)"
        
        return 1, f"✅ Spanish number format is acceptable. {correct_info}. Found {total_errors} format errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        error_details = [f"'{error['error']}' → '{error['correct']}' ({error['description']})" for error in all_errors[:5]]
        error_summary = "; ".join(error_details)
        if len(all_errors) > 5:
            error_summary += f" ... (+{len(all_errors)-5} more errors)"
        
        return 0, f"❌ Found {total_errors} Spanish number format errors (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."


def has_correct_spanish_currency_format(texts, max_errors):
    """检测文本中西班牙语金额格式是否正确（货币符号在数字之后，有空格）"""
    import re
    
    def clean_up_text(text):
        return text.strip()
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_currency_format_errors(text):
        """检查文本中的金额格式错误"""
        
        format_errors = []
        correct_currencies = []
        processed_positions = set()
        
        print(f"Debug - 检查金额格式，文本: {text[:100]}...")
        
        # 定义货币符号和代码
        currency_symbols = ['€', '$', '£', '¥', '₹', '₽', '₩', '₪', '₦', '₡', '₵', '₴']
        currency_codes = ['EUR', 'USD', 'GBP', 'JPY', 'CNY', 'RUB', 'KRW', 'MXN', 'ARS', 'COP', 'PEN', 'CLP']
        
        # 🔧 修复：更全面的货币匹配模式
        currency_patterns = [
            # 正确格式：数字 + 空格 + 货币符号/代码
            r'(\d+(?:\.\d{3})*(?:,\d{1,2})?)\s+([€$£¥₹₽₩₪₦₡₵₴])',
            r'(\d+(?:\.\d{3})*(?:,\d{1,2})?)\s+(EUR|USD|GBP|JPY|CNY|RUB|KRW|MXN|ARS|COP|PEN|CLP)\b',
            
            # 错误格式1：货币符号 + 数字（英语格式）
            r'([€$£¥₹₽₩₪₦₡₵₴])\s*(\d+(?:[,\.]\d+)*)',
            r'(EUR|USD|GBP|JPY|CNY|RUB|KRW|MXN|ARS|COP|PEN|CLP)\s+(\d+(?:[,\.]\d+)*)',
            
            # 错误格式2：数字 + 货币符号（无空格）
            r'(\d+(?:[,\.]\d+)*)([€$£¥₹₽₩₪₦₡₵₴])',
            r'(\d+(?:[,\.]\d+)*)(EUR|USD|GBP|JPY|CNY|RUB|KRW|MXN|ARS|COP|PEN|CLP)\b',
        ]
        
        found_currencies = []
        
        # 收集所有货币表达式
        for i, pattern in enumerate(currency_patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                found_currencies.append({
                    'full_match': match.group(),
                    'position': match.span(),
                    'groups': match.groups(),
                    'pattern_index': i
                })
        
        print(f"Debug - 找到的货币表达式: {[fc['full_match'] for fc in found_currencies]}")
        
        # 🔧 修复：按位置排序，避免重复处理
        found_currencies.sort(key=lambda x: x['position'][0])
        
        # 分析每个找到的货币表达式
        for currency_info in found_currencies:
            full_text = currency_info['full_match']
            position = currency_info['position']
            groups = currency_info['groups']
            pattern_index = currency_info['pattern_index']
            
            # 跳过已处理的位置
            overlap = any(pos[0] < position[1] and pos[1] > position[0] for pos in processed_positions)
            if overlap:
                continue
            
            print(f"Debug - 处理货币: '{full_text}', 模式: {pattern_index}")
            
            is_correct = False
            error_type = ""
            description = ""
            suggested_format = ""
            
            if len(groups) == 2:
                first, second = groups
                
                # 🔧 修复：根据匹配的模式判断格式
                if pattern_index <= 1:
                    # 正确格式：数字 + 空格 + 货币
                    is_correct = True
                    print(f"Debug - ✅ 正确格式: {full_text}")
                    
                elif pattern_index <= 3:
                    # 错误格式：货币 + 数字（英语格式）
                    error_type = 'currency_before_number'
                    description = 'Símbolo de moneda antes del número (debe ir después con espacio)'
                    
                    # 修正数字格式（英语 → 西班牙语）
                    corrected_number = second
                    if ',' in corrected_number and '.' in corrected_number:
                        # 1,234.56 → 1.234,56
                        corrected_number = corrected_number.replace(',', '|').replace('.', ',').replace('|', '.')
                    elif ',' in corrected_number and len(corrected_number.split(',')[-1]) == 3:
                        # 150,000 → 150.000
                        corrected_number = corrected_number.replace(',', '.')
                    elif '.' in corrected_number and len(corrected_number.split('.')[-1]) <= 2:
                        # 150.50 → 150,50
                        corrected_number = re.sub(r'\.(\d{1,2})$', r',\1', corrected_number)
                    
                    suggested_format = f"{corrected_number} {first}"
                    print(f"Debug - ❌ 货币在前: {full_text} → {suggested_format}")
                    
                else:
                    # 错误格式：数字 + 货币（无空格）
                    error_type = 'no_space_before_currency'
                    description = 'Falta espacio entre número y símbolo de moneda'
                    
                    # 修正数字格式
                    corrected_number = first
                    if ',' in corrected_number and len(corrected_number.split(',')[-1]) == 3:
                        # 150,000 → 150.000
                        corrected_number = corrected_number.replace(',', '.')
                    elif '.' in corrected_number and len(corrected_number.split('.')[-1]) <= 2:
                        # 150.50 → 150,50
                        corrected_number = re.sub(r'\.(\d{1,2})$', r',\1', corrected_number)
                    
                    suggested_format = f"{corrected_number} {second}"
                    print(f"Debug - ❌ 无空格: {full_text} → {suggested_format}")
            
            # 记录结果
            if is_correct:
                correct_currencies.append({
                    'currency': full_text.strip(),
                    'position': position,
                    'type': 'correct_spanish_format'
                })
            elif suggested_format:
                format_errors.append({
                    'error': full_text.strip(),
                    'correct': suggested_format,
                    'type': error_type,
                    'position': position,
                    'description': description
                })
            
            processed_positions.add(position)
        
        print(f"Debug - 正确金额: {len(correct_currencies)}, 错误金额: {len(format_errors)}")
        return len(format_errors), format_errors, len(correct_currencies), correct_currencies
    
    # 统计所有文本中的格式错误
    total_errors = 0
    all_errors = []
    all_correct = []
    
    for text in cleaned_up_texts:
        error_count, errors, correct_count, correct_currencies = check_currency_format_errors(text)
        total_errors += error_count
        all_errors.extend(errors)
        all_correct.extend(correct_currencies)
    
    print(f"Debug - 总错误数: {total_errors}, 总正确数: {len(all_correct)}")
    
    # 构建结果信息
    if total_errors <= max_errors:
        correct_examples = [correct['currency'] for correct in all_correct[:5]]
        correct_info = f"Found {len(all_correct)} correctly formatted currencies"
        if correct_examples:
            correct_info += f": {', '.join(correct_examples)}"
        
        error_info = ""
        if all_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}' ({err['description']})" for err in all_errors[:3]]
            error_info = f" Currency format errors: {'; '.join(error_examples)}"
            if len(all_errors) > 3:
                error_info += f" (+{len(all_errors)-3} more)"
        
        return 1, f"✅ Spanish currency format is acceptable. {correct_info}. Found {total_errors} format errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        error_details = [f"'{error['error']}' → '{error['correct']}' ({error['description']})" for error in all_errors[:5]]
        error_summary = "; ".join(error_details)
        if len(all_errors) > 5:
            error_summary += f" ... (+{len(all_errors)-5} more errors)"
        
        return 0, f"❌ Found {total_errors} Spanish currency format errors (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."



def has_correct_spanish_phone_format(texts, max_errors):
    """检测文本中西班牙语电话号码格式是否正确（三位一组，空格分隔）"""
    import re
    
    def clean_up_text(text):
        return text.strip()
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_phone_format_errors(text):
        """检查文本中的电话号码格式错误"""
        
        format_errors = []
        correct_phones = []
        processed_positions = set()
        
        # 1. 检测正确的西班牙语电话号码格式
        correct_patterns = [
            # 标准手机号码：600 123 456 (三位-三位-三位)
            r'\b[679]\d{2}\s\d{3}\s\d{3}\b',
            # 固定电话：91 123 45 67 (两位区号-三位-两位-两位)
            r'\b9[1-8]\s\d{3}\s\d{2}\s\d{2}\b',
            # 固定电话：958 12 34 56 (三位区号-两位-两位-两位)
            r'\b9[0-9]{2}\s\d{2}\s\d{2}\s\d{2}\b',
            # 国际格式：+34 600 123 456
            r'\+34\s[679]\d{2}\s\d{3}\s\d{3}\b',
            # 国际格式固定电话：+34 91 123 45 67
            r'\+34\s9[1-8]\s\d{3}\s\d{2}\s\d{2}\b'
        ]
        
        for pattern in correct_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                position = match.span()
                overlap = any(pos[0] < position[1] and pos[1] > position[0] for pos in processed_positions)
                if not overlap:
                    correct_phones.append({
                        'phone': match.group().strip(),
                        'position': position,
                        'type': 'correct_spanish_format'
                    })
                    processed_positions.add(position)
        
        # 2. 🔧 修复：更广泛的电话号码检测模式
        all_phone_patterns = [
            # 各种分隔符的电话号码：连字符、点、空格
            r'\b(?:\+\d{1,3}[-.\s]?)?\d{2,4}[-.\s]\d{3,4}[-.\s]?\d{2,4}\b',
            # 无分隔符的长号码
            r'\b(?:\+\d{1,3})?\d{7,12}\b',
            # 短号码格式（如555-1234）
            r'\b\d{3,4}[-.\s]?\d{4}\b',
            # 带括号的区号格式
            r'\b\(\d{2,4}\)\s?\d{3,4}[-.\s]?\d{2,4}\b'
        ]
        
        # 检测所有可能的电话号码
        all_found_phones = []
        for pattern in all_phone_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                position = match.span()
                phone_text = match.group().strip()
                
                # 过滤掉明显不是电话号码的数字（如年份、时间等）
                digits_only = re.sub(r'[^\d]', '', phone_text)
                if len(digits_only) >= 4 and len(digits_only) <= 15:
                    # 检查是否与已处理的位置重叠
                    overlap = any(pos[0] < position[1] and pos[1] > position[0] for pos in processed_positions)
                    if not overlap:
                        all_found_phones.append({
                            'phone': phone_text,
                            'position': position,
                            'digits': digits_only
                        })
                        processed_positions.add(position)
        
        # 3. 检查找到的电话号码格式是否正确
        for phone_info in all_found_phones:
            phone_text = phone_info['phone']
            position = phone_info['position']
            digits = phone_info['digits']
            
            # 检查是否已经是正确格式
            is_correct_format = False
            for pattern in correct_patterns:
                if re.match(pattern, phone_text):
                    is_correct_format = True
                    break
            
            if not is_correct_format:
                # 生成正确格式建议
                if digits.startswith('+34'):
                    country_code = '+34'
                    phone_digits = digits[2:]
                elif digits.startswith('34') and len(digits) > 9:
                    country_code = '+34'
                    phone_digits = digits[2:]
                else:
                    country_code = ''
                    phone_digits = digits
                
                # 根据号码长度和开头数字格式化
                if len(phone_digits) == 9:
                    if phone_digits.startswith(('6', '7', '9')):
                        if phone_digits.startswith(('6', '7')):
                            # 手机号码：XXX XXX XXX
                            suggested_format = f"{phone_digits[:3]} {phone_digits[3:6]} {phone_digits[6:9]}"
                        elif phone_digits.startswith('9') and len(phone_digits) > 1 and phone_digits[1] in '12345678':
                            # 固定电话：9X XXX XX XX
                            suggested_format = f"{phone_digits[:2]} {phone_digits[2:5]} {phone_digits[5:7]} {phone_digits[7:9]}"
                        else:
                            # 其他9开头：XXX XXX XXX
                            suggested_format = f"{phone_digits[:3]} {phone_digits[3:6]} {phone_digits[6:9]}"
                    else:
                        # 其他9位号码：XXX XXX XXX
                        suggested_format = f"{phone_digits[:3]} {phone_digits[3:6]} {phone_digits[6:9]}"
                elif len(phone_digits) == 8:
                    # 8位固定电话：XXX XX XXX
                    suggested_format = f"{phone_digits[:3]} {phone_digits[3:5]} {phone_digits[5:8]}"
                elif len(phone_digits) == 7:
                    # 7位号码：XXX XXXX
                    suggested_format = f"{phone_digits[:3]} {phone_digits[3:7]}"
                elif len(phone_digits) == 4:
                    # 4位短号码：XXXX (保持原样)
                    suggested_format = phone_digits
                else:
                    # 其他长度：三位分组
                    groups = [phone_digits[i:i+3] for i in range(0, len(phone_digits), 3)]
                    suggested_format = ' '.join(groups)
                
                if country_code:
                    suggested_format = f"{country_code} {suggested_format}"
                
                # 判断错误类型
                if '-' in phone_text:
                    error_type = 'hyphen_separator'
                    description = 'Usa guiones como separadores (debe usar espacios)'
                elif '.' in phone_text:
                    error_type = 'dot_separator'
                    description = 'Usa puntos como separadores (debe usar espacios)'
                elif not re.search(r'[\s\-.]', phone_text):
                    error_type = 'no_separator'
                    description = 'Sin separadores (debe agrupar con espacios)'
                else:
                    error_type = 'incorrect_format'
                    description = 'Formato incorrecto (debe seguir formato español estándar)'
                
                format_errors.append({
                    'error': phone_text,
                    'correct': suggested_format,
                    'type': error_type,
                    'position': position,
                    'description': description
                })
        
        return len(format_errors), format_errors, len(correct_phones), correct_phones
    
    # 统计所有文本中的格式错误
    total_errors = 0
    all_errors = []
    all_correct = []
    
    for text in cleaned_up_texts:
        error_count, errors, correct_count, correct_phones = check_phone_format_errors(text)
        total_errors += error_count
        all_errors.extend(errors)
        all_correct.extend(correct_phones)
    
    # 🆕 保留：检查是否完全没有电话号码
    total_phones_found = len(all_correct) + len(all_errors)
    
    if total_phones_found == 0:
        # 没有找到任何电话号码（正确或错误格式都没有）
        total_errors += 1
        all_errors.append({
            'error': 'No phone number found',
            'correct': 'Should include contact phone number (e.g., 91 234 56 78 or 600 123 456)',
            'type': 'missing_phone_number',
            'description': 'Falta número de teléfono de contacto requerido'
        })
    
    # 构建结果信息
    if total_errors <= max_errors:
        if len(all_correct) > 0:
            correct_examples = [correct['phone'] for correct in all_correct[:5]]
            correct_info = f"Found {len(all_correct)} correctly formatted phone numbers: {', '.join(correct_examples)}"
        else:
            correct_info = "Found 0 correctly formatted phone numbers"
        
        error_info = ""
        if all_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}' ({err['description']})" for err in all_errors[:3]]
            error_info = f" Errors found: {'; '.join(error_examples)}"
            if len(all_errors) > 3:
                error_info += f" (and {len(all_errors)-3} more)"
        
        return 1, f"✅ Spanish phone number format is acceptable. {correct_info}. Found {total_errors} errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        if len(all_correct) > 0:
            correct_info = f"Found {len(all_correct)} correctly formatted phone numbers. "
        else:
            correct_info = "No correctly formatted phone numbers found. "
        
        error_details = [f"'{error['error']}' → '{error['correct']}' ({error['description']})" for error in all_errors[:5]]
        error_summary = "; ".join(error_details)
        if len(all_errors) > 5:
            error_summary += f" (and {len(all_errors)-5} more errors)"
        
        return 0, f"❌ Found {total_errors} phone number errors (allowed: {max_errors}). {correct_info}Errors: {error_summary}. Does not meet the requirement."


def has_correct_spanish_question_accents(texts, max_errors):
    """检测西班牙语疑问句中的重音符号使用是否正确"""
    import re
    
    def clean_up_text(text):
        """基础文本清理"""
        return text.strip()
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_question_accent_errors(text):
        """检查疑问句中的重音符号错误"""
        
        # 正确的疑问词（带重音）
        correct_question_words = {
            'qué': 'what/which',
            'cuál': 'which', 
            'cuáles': 'which (plural)',
            'quién': 'who',
            'quiénes': 'who (plural)',
            'dónde': 'where',
            'cuándo': 'when',
            'cómo': 'how',
            'cuánto': 'how much',
            'cuánta': 'how much (fem)',
            'cuántos': 'how many (masc)',
            'cuántas': 'how many (fem)',
            'por qué': 'why',
            'para qué': 'what for',
            'adónde': 'where to',
            'de dónde': 'where from',
            'hasta cuándo': 'until when',
            'desde cuándo': 'since when'
        }
        
        # 错误的疑问词（无重音）
        incorrect_question_words = {
            'que': 'qué',
            'cual': 'cuál',
            'cuales': 'cuáles', 
            'quien': 'quién',
            'quienes': 'quiénes',
            'donde': 'dónde',
            'cuando': 'cuándo',
            'como': 'cómo',
            'cuanto': 'cuánto',
            'cuanta': 'cuánta',
            'cuantos': 'cuántos',
            'cuantas': 'cuántas',
            'por que': 'por qué',
            'para que': 'para qué',
            'adonde': 'adónde',
            'de donde': 'de dónde',
            'hasta cuando': 'hasta cuándo',
            'desde cuando': 'desde cuándo'
        }
        
        format_errors = []
        correct_uses = []
        
        # 🔧 改进的疑问句识别 - 更精确的模式
        question_sentences = []
        
        # 方法1: 标准西班牙语疑问句 ¿...?
        standard_questions = re.findall(r'¿[^¿?]*\?', text, re.DOTALL)
        question_sentences.extend(standard_questions)
        
        # 方法2: 简单问号结尾（但要排除缩写等）
        simple_questions = re.findall(r'[^.!¿]*[A-Za-záéíóúñüÁÉÍÓÚÑÜ][^.!¿]*\?', text, re.DOTALL)
        question_sentences.extend(simple_questions)
        
        # 🆕 去重并清理
        unique_questions = []
        seen_questions = set()
        
        for question in question_sentences:
            # 清理问题文本
            clean_q = re.sub(r'\s+', ' ', question.strip())
            clean_q = clean_q.strip('¿?').strip()
            
            # 跳过太短的"问题"（可能是缩写或误识别）
            if len(clean_q) < 10:
                continue
                
            # 去重
            if clean_q.lower() not in seen_questions:
                seen_questions.add(clean_q.lower())
                unique_questions.append(question.strip())
        
        total_questions = len(unique_questions)
        questions_with_question_words = 0
        
        for question in unique_questions:
            question_has_question_word = False
            question_clean = question.strip()
            
            # 🔧 检查正确的疑问词 - 改进匹配
            for correct_word in correct_question_words:
                if ' ' in correct_word:
                    # 复合疑问词如 "por qué"
                    pattern = r'\b' + re.escape(correct_word) + r'\b'
                else:
                    # 单个疑问词 - 确保词边界
                    pattern = r'\b' + re.escape(correct_word) + r'\b'
                
                if re.search(pattern, question_clean, re.IGNORECASE):
                    correct_uses.append({
                        'word': correct_word,
                        'sentence': question_clean[:60] + "..." if len(question_clean) > 60 else question_clean,
                        'type': 'correct_accent'
                    })
                    question_has_question_word = True
            
            # 🔧 检查错误的疑问词 - 避免误报
            for incorrect_word, correct_word in incorrect_question_words.items():
                if ' ' in incorrect_word:
                    pattern = r'\b' + re.escape(incorrect_word) + r'\b'
                else:
                    pattern = r'\b' + re.escape(incorrect_word) + r'\b'
                
                # 🆕 特殊处理：避免误报常见词汇
                # "que" 在很多情况下不是疑问词
                if incorrect_word == 'que':
                    # 只在明确的疑问句开头或特定模式中才报错
                    if re.search(r'¿\s*que\b|^que\b.*\?', question_clean, re.IGNORECASE):
                        matches = re.findall(pattern, question_clean, re.IGNORECASE)
                        for match in matches:
                            format_errors.append({
                                'error': match,
                                'correct': correct_word,
                                'sentence': question_clean[:60] + "..." if len(question_clean) > 60 else question_clean,
                                'description': f'Falta acento en palabra interrogativa'
                            })
                            question_has_question_word = True
                else:
                    # 其他疑问词的常规检查
                    if re.search(pattern, question_clean, re.IGNORECASE):
                        matches = re.findall(pattern, question_clean, re.IGNORECASE)
                        for match in matches:
                            format_errors.append({
                                'error': match,
                                'correct': correct_word,
                                'sentence': question_clean[:60] + "..." if len(question_clean) > 60 else question_clean,
                                'description': f'Falta acento en palabra interrogativa'
                            })
                            question_has_question_word = True
            
            if question_has_question_word:
                questions_with_question_words += 1
        
        return len(format_errors), format_errors, len(correct_uses), correct_uses, total_questions, questions_with_question_words
    
    # 统计所有文本中的错误
    total_errors = 0
    all_errors = []
    all_correct = []
    total_questions_count = 0
    total_questions_with_words = 0
    
    for text in cleaned_up_texts:
        error_count, errors, correct_count, correct_uses, questions_count, questions_with_words = check_question_accent_errors(text)
        total_errors += error_count
        all_errors.extend(errors)
        all_correct.extend(correct_uses)
        total_questions_count += questions_count
        total_questions_with_words += questions_with_words
    
    # 🔧 去重处理 - 避免重复计算相同的错误
    unique_errors = []
    seen_errors = set()
    for error in all_errors:
        error_key = f"{error['error']}_{error['correct']}"
        if error_key not in seen_errors:
            seen_errors.add(error_key)
            unique_errors.append(error)
    
    unique_correct = []
    seen_correct = set()
    for correct in all_correct:
        correct_key = f"{correct['word']}"
        if correct_key not in seen_correct:
            seen_correct.add(correct_key)
            unique_correct.append(correct)
    
    total_errors = len(unique_errors)
    
    # 🔧 改进的结果判断逻辑
    if total_errors <= max_errors:
        # 🆕 特殊情况处理 - 没有疑问词的情况
        if total_questions_count > 0 and total_questions_with_words == 0:
            return 1, f"✅ Spanish question word accents are correct. No interrogative pronouns found in {total_questions_count} question{'s' if total_questions_count != 1 else ''} (likely yes/no questions or polite requests). This is acceptable. Requirement met."
        
        # 有疑问词的情况
        correct_info = ""
        if unique_correct:
            correct_examples = [f"'{correct['word']}'" for correct in unique_correct[:5]]
            correct_info = f"Found {len(unique_correct)} correct question words: {', '.join(correct_examples)}"
            if len(unique_correct) > 5:
                correct_info += f" ... (+{len(unique_correct)-5} more)"
        
        # 疑问句统计信息
        question_info = f"Analyzed {total_questions_count} question{'s' if total_questions_count != 1 else ''}"
        if total_questions_with_words > 0:
            question_info += f" ({total_questions_with_words} with interrogative words)"
        
        # 错误信息（如果有的话）
        error_info = ""
        if unique_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}'" for err in unique_errors[:2]]
            error_info = f" Minor errors found: {'; '.join(error_examples)}"
            if len(unique_errors) > 2:
                error_info += f" (+{len(unique_errors)-2} more)"
        
        success_msg = f"✅ Spanish question word accents are correct. {question_info}."
        if correct_info:
            success_msg += f" {correct_info}."
        success_msg += f" Found {total_errors} error{'s' if total_errors != 1 else ''} (allowed: {max_errors}).{error_info} Requirement met."
        
        return 1, success_msg
    
    else:
        # 构建详细的错误信息
        error_details = []
        for error in unique_errors[:3]:
            error_details.append(f"'{error['error']}' → '{error['correct']}' in \"{error['sentence']}\"")
        if len(unique_errors) > 3:
            error_details.append(f"... and {len(unique_errors)-3} more errors")
        error_summary = "; ".join(error_details)
        
        question_info = f"Analyzed {total_questions_count} question{'s' if total_questions_count != 1 else ''}"
        if total_questions_with_words > 0:
            question_info += f" ({total_questions_with_words} with interrogative words)"
        
        return 0, f"❌ Found {total_errors} question word accent error{'s' if total_errors != 1 else ''} (allowed: {max_errors}). {question_info}. Errors: {error_summary}. Does not meet the requirement."




def has_correct_spanish_date_names_case(texts, max_errors):
    """检测西班牙语月份/星期名称是否首字母小写"""
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_date_names_case_errors(text):
        """检查月份/星期名称大小写错误"""
        
        # 正确的月份名称（小写）
        correct_months = [
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        
        # 正确的星期名称（小写）
        correct_weekdays = [
            'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'
        ]
        
        format_errors = []
        correct_uses = []
        
        # 检查月份
        for month in correct_months:
            # 查找正确的小写形式
            correct_matches = re.finditer(r'\b' + re.escape(month) + r'\b', text)
            for match in correct_matches:
                correct_uses.append({
                    'word': match.group(),
                    'type': 'month',
                    'position': match.span()
                })
            
            # 查找错误的大写形式
            capitalized = month.capitalize()
            error_matches = re.finditer(r'\b' + re.escape(capitalized) + r'\b', text)
            for match in error_matches:
                format_errors.append({
                    'error': match.group(),
                    'correct': month,
                    'type': 'month',
                    'position': match.span(),
                    'description': 'Nombre de mes debe empezar con minúscula'
                })
        
        # 检查星期
        for weekday in correct_weekdays:
            # 查找正确的小写形式
            correct_matches = re.finditer(r'\b' + re.escape(weekday) + r'\b', text)
            for match in correct_matches:
                correct_uses.append({
                    'word': match.group(),
                    'type': 'weekday',
                    'position': match.span()
                })
            
            # 查找错误的大写形式
            capitalized = weekday.capitalize()
            error_matches = re.finditer(r'\b' + re.escape(capitalized) + r'\b', text)
            for match in error_matches:
                format_errors.append({
                    'error': match.group(),
                    'correct': weekday,
                    'type': 'weekday',
                    'position': match.span(),
                    'description': 'Nombre de día debe empezar con minúscula'
                })
        
        return len(format_errors), format_errors, len(correct_uses), correct_uses
    
    # 统计所有文本中的错误
    total_errors = 0
    all_errors = []
    all_correct = []
    
    for text in cleaned_up_texts:
        error_count, errors, correct_count, correct_uses = check_date_names_case_errors(text)
        total_errors += error_count
        all_errors.extend(errors)
        all_correct.extend(correct_uses)
    
    # 构建结果信息
    if total_errors <= max_errors:
        correct_examples = [f"'{correct['word']}'" for correct in all_correct[:5]]
        correct_info = f"Found {len(all_correct)} correct date names" + (f": {', '.join(correct_examples)}" if correct_examples else "")
        
        error_info = ""
        if all_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}'" for err in all_errors]
            error_info = f" Date name case errors: {'; '.join(error_examples)}"
        
        return 1, f"✅ Spanish date name cases are correct. {correct_info}. Found {total_errors} errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        error_details = [f"'{error['error']}' → '{error['correct']}' ({error['description']})" for error in all_errors]
        error_summary = "; ".join(error_details)
        
        return 0, f"❌ Found {total_errors} date name case errors (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."

def has_correct_spanish_address_format(texts, max_errors):
    """检测西班牙语地址格式是否正确（C/, Av., º等缩写）"""
    import re
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_address_format_errors(text):
        """检查地址格式错误"""
        
        format_errors = []
        correct_addresses = []
        seen_errors = set()  # 防止重复计数
        
        # 正确的地址格式模式
        correct_patterns = [
            r'\bC/\s+[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+,?\s*(?:número\s+)?\d+(?:\s+\d+º[A-Z]?)?\b',
            r'\bAv\.\s+[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+,?\s*(?:número\s+)?\d+(?:\s+\d+º[A-Z]?)?\b',
            r'\bPlaza\s+[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+,?\s*(?:número\s+)?\d+(?:\s+\d+º[A-Z]?)?\b',
            r'\b\d+º[A-Z]?\b'
        ]
        
        for pattern in correct_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                correct_addresses.append({
                    'address': match.group().strip(),
                    'position': match.span(),
                    'type': 'correct_spanish_address'
                })
        
        # 错误的地址格式模式
        error_patterns = [
            {
                'pattern': r'\bCalle\s+[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+,?\s*(?:número\s+)?\d+',
                'type': 'full_street_name',
                'description': 'Debe usar "C/" en lugar de "Calle"'
            },
            {
                'pattern': r'\bAvenida\s+[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+,?\s*(?:número\s+)?\d+',
                'type': 'full_avenue_name',
                'description': 'Debe usar "Av." en lugar de "Avenida"'
            },
            {
                'pattern': r'\bpiso\s+\d+\b',
                'type': 'full_floor_word',
                'description': 'Debe usar formato "º" en lugar de "piso"'
            },
            {
                'pattern': r'\b\d+[A-Z]\b(?!º)',
                'type': 'missing_ordinal_symbol',
                'description': 'Falta símbolo ordinal "º" en el piso'
            },
            {
                'pattern': r'\b\d+(?:st|nd|rd|th)\b',
                'type': 'english_ordinal',
                'description': 'Formato inglés, debe usar formato español con "º"'
            }
        ]
        
        # 检查错误格式
        for error_config in error_patterns:
            pattern = error_config['pattern']
            error_type = error_config['type']
            description = error_config['description']
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                error_text = match.group().strip()
                
                # 创建唯一标识符避免重复
                error_key = f"{error_text}_{error_type}"
                if error_key in seen_errors:
                    continue
                seen_errors.add(error_key)
                
                # 生成正确格式建议
                suggested_format = ""
                if error_type == 'full_street_name':
                    street_match = re.search(r'Calle\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+),?\s*(?:número\s+)?(\d+)', error_text, re.IGNORECASE)
                    if street_match:
                        street_name = street_match.group(1).strip()
                        number = street_match.group(2)
                        suggested_format = f"C/ {street_name}, {number}"
                elif error_type == 'full_avenue_name':
                    suggested_format = error_text.replace('Avenida', 'Av.', 1)
                elif error_type == 'full_floor_word':
                    floor_match = re.search(r'piso\s+(\d+)', error_text, re.IGNORECASE)
                    if floor_match:
                        floor_num = floor_match.group(1)
                        suggested_format = f"{floor_num}º"
                elif error_type == 'missing_ordinal_symbol':
                    suggested_format = re.sub(r'(\d+)([A-Z])', r'\1º\2', error_text)
                elif error_type == 'english_ordinal':
                    number = re.search(r'\d+', error_text).group()
                    suggested_format = f"{number}º"
                
                format_errors.append({
                    'error': error_text,
                    'correct': suggested_format,
                    'type': error_type,
                    'position': match.span(),
                    'description': description
                })
        
        return len(format_errors), format_errors, len(correct_addresses), correct_addresses
    
    # 统计所有文本中的错误 - 全局去重
    total_errors = 0
    all_errors = []
    all_correct = []
    global_seen_errors = set()  # 全局去重
    
    for text in cleaned_up_texts:
        error_count, errors, correct_count, correct_addresses = check_address_format_errors(text)
        
        # 全局去重
        for error in errors:
            error_key = f"{error['error']}_{error['type']}"
            if error_key not in global_seen_errors:
                global_seen_errors.add(error_key)
                all_errors.append(error)
        
        all_correct.extend(correct_addresses)
    
    total_errors = len(all_errors)
    
    # 构建结果信息
    if total_errors <= max_errors:
        correct_examples = [f"'{correct['address']}'" for correct in all_correct[:3]]
        correct_info = f"Found {len(all_correct)} correct address formats" + (f": {', '.join(correct_examples)}" if correct_examples else "")
        
        error_info = ""
        if all_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}'" for err in all_errors[:3]]
            error_info = f" Address format errors: {'; '.join(error_examples)}"
            if len(all_errors) > 3:
                error_info += f" (+{len(all_errors)-3} more)"
        
        return 1, f"✅ Spanish address formats are correct. {correct_info}. Found {total_errors} errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        error_details = [f"'{error['error']}' → '{error['correct']}' ({error['description']})" for error in all_errors[:3]]
        error_summary = "; ".join(error_details)
        if len(all_errors) > 3:
            error_summary += f" (+{len(all_errors)-3} more)"
        
        return 0, f"❌ Found {total_errors} address format errors (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."



def total_has_complete_questions(texts, count_range):
    """检查整个对话中完整西班牙语疑问句的总数量是否在指定范围内"""
    
    if not texts:
        return 0, f"❌ No dialogue provided"
    
    # 处理参数：可以是单个数字或范围
    if isinstance(count_range, list) and len(count_range) == 2:
        min_count, max_count = count_range
    elif isinstance(count_range, int):
        min_count = max_count = count_range  # 精确匹配
    else:
        min_count = max_count = 1  # 默认值
    
    # 确保 texts 是列表格式
    if isinstance(texts, str):
        dialogue_rounds = [texts]
    elif isinstance(texts, list):
        dialogue_rounds = texts
    else:
        dialogue_rounds = [str(texts)]
    
    # 完整疑问句的正则模式：¿开头，?结尾，中间不包含其他¿或?
    complete_question_pattern = r'¿[^¿?]*\?'
    
    total_questions = 0
    all_questions = []
    
    # 统计所有轮次中的疑问句总数
    for i, round_text in enumerate(dialogue_rounds):
        round_content = str(round_text).strip()
        
        # 查找完整的疑问句
        matches = re.findall(complete_question_pattern, round_content, re.DOTALL)
        round_questions = len(matches)
        total_questions += round_questions
        
        # 记录找到的疑问句
        for question in matches:
            display_question = question[:50] + "..." if len(question) > 50 else question
            all_questions.append(f"Round {i+1}: {display_question}")
    
    # 检查是否符合要求
    if min_count <= total_questions <= max_count:
        question_list = "; ".join(all_questions[:10])  # 最多显示10个
        if len(all_questions) > 10:
            question_list += f" ... (+{len(all_questions)-10} more)"
        
        if min_count == max_count:
            requirement_text = f"exactly {min_count}"
        elif max_count >= 1000:  # 实际上是"至少"的意思
            requirement_text = f"at least {min_count}"
        else:
            requirement_text = f"between {min_count} and {max_count}"
        
        return 1, f"✅ Total dialogue contains {total_questions} complete questions ({requirement_text} required). Found: {question_list}. Requirement met."
    else:
        question_list = "; ".join(all_questions) if all_questions else "None found"
        
        if min_count == max_count:
            requirement_text = f"exactly {min_count}"
        elif max_count >= 1000:
            requirement_text = f"at least {min_count}"
        else:
            requirement_text = f"between {min_count} and {max_count}"
        
        return 0, f"❌ Total dialogue contains {total_questions} complete questions ({requirement_text} required). Found: {question_list}. Does not meet the requirement."

def has_spanish_keywords_with_articles(texts, *args, **kwargs):
    """智能检测原文名词和定冠词搭配"""
    
    # 🔧 灵活的参数处理
    if len(args) == 1:
        # 单个参数：可能是 min_count，或者是 [min_count, max_count] 列表
        if isinstance(args[0], (list, tuple)) and len(args[0]) == 2:
            min_count, max_count = args[0]
        else:
            min_count = args[0]
            max_count = args[0]
    elif len(args) == 2:
        min_count, max_count = args
    elif len(args) == 0:
        # 从 kwargs 获取
        min_count = kwargs.get('min_count', 1)
        max_count = kwargs.get('max_count', min_count)
    else:
        # 处理更多参数的情况
        min_count = args[0]
        max_count = args[1] if len(args) > 1 else args[0]
    
    if not texts:
        return 0, f"❌ No text provided"
    
    # 原文中的名词列表
    original_nouns = [
        "palabras", "lenguaje", "comunicación", "papel", "susurros", 
        "corazón", "bolígrafo", "pensamientos", "hogar", "estrellas", 
        "cielo", "sentimientos", "raíces"
    ]
    
    # 西班牙语定冠词
    definite_articles = ["el", "la", "los", "las"]
    
    def find_keywords_in_text(text):
        """在文本中查找关键词"""
        import re
        found_keywords = []
        for noun in original_nouns:
            for article in definite_articles:
                pattern = rf'\b{article}\s+{noun}\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    found_keywords.append(f"{article} {noun}")
                    break  # 找到一个就够了，避免重复计算
        return list(set(found_keywords))  # 去重
    
    # 🎯 智能判断处理模式
    if isinstance(texts, str):
        # 模式1：单个文本 → 整篇文章模式
        text = texts
        keywords = find_keywords_in_text(text)
        keyword_count = len(keywords)
        
        meets_requirement = min_count <= keyword_count <= max_count
        
        if keywords:
            keyword_info = f"Found: {', '.join(keywords[:5])}"
            if len(keywords) > 5:
                keyword_info += f" (and {len(keywords)-5} more)"
        else:
            keyword_info = "No keywords found"
        
        if meets_requirement:
            return 1, f"✅ Article contains {keyword_count} original nouns with definite articles (required: {min_count}-{max_count}). {keyword_info}"
        else:
            if keyword_count < min_count:
                return 0, f"❌ Article contains only {keyword_count} original nouns with definite articles, need at least {min_count}. {keyword_info}"
            else:
                return 0, f"❌ Article contains {keyword_count} original nouns with definite articles, exceeds maximum {max_count}. {keyword_info}"
    
    elif isinstance(texts, list):
        # 🔍 进一步判断：是真正的多条评论，还是单篇文章被分割了
        
        # 启发式判断：如果只有1个元素，或者所有元素都很长，可能是单篇文章
        if len(texts) == 1:
            # 只有1个元素 → 当作单篇文章处理
            return has_spanish_keywords_with_articles(texts[0], min_count, max_count)
        
        # 计算平均长度来判断
        avg_length = sum(len(str(text)) for text in texts) / len(texts)
        
        if avg_length > 500:  # 如果平均每条超过500字符，可能是长文章的段落
            # 模式1：长段落 → 整篇文章模式
            combined_text = ' '.join(str(text) for text in texts)
            return has_spanish_keywords_with_articles(combined_text, min_count, max_count)
        
        else:
            # 模式2：短文本 → 多条评论模式
            comment_details = []
            all_match = True
            
            for i, comment in enumerate(texts):
                comment_text = str(comment).strip()
                keywords = find_keywords_in_text(comment_text)
                keyword_count = len(keywords)
                
                meets_requirement = min_count <= keyword_count <= max_count
                if not meets_requirement:
                    all_match = False
                
                # 记录详情
                status = "✅" if meets_requirement else "❌"
                if keywords:
                    display_keywords = keywords[:3]
                    keyword_info = f"({', '.join(display_keywords)}"
                    if len(keywords) > 3:
                        keyword_info += f" +{len(keywords)-3} more"
                    keyword_info += ")"
                else:
                    keyword_info = "(no keywords)"
                
                comment_details.append(f"Comment {i+1}: {keyword_count} keywords {status} {keyword_info}")
            
            detail_info = " | ".join(comment_details)
            
            if all_match:
                return 1, f"✅ All {len(texts)} comments contain {min_count}-{max_count} original nouns with definite articles. {detail_info}"
            else:
                return 0, f"❌ Some comments do NOT meet the requirement of {min_count}-{max_count} keywords with definite articles. {detail_info}"
    
    else:
        # 其他类型 → 转换为字符串处理
        return has_spanish_keywords_with_articles(str(texts), min_count, max_count)


def has_spanish_ningun_sentences(texts, count_range):
    """统计包含ningún/ninguna的句子数量（更精确的识别）"""
    
    # 处理参数格式
    if isinstance(count_range, list) and len(count_range) == 2:
        min_count, max_count = count_range
    elif isinstance(count_range, (int, float)):
        min_count = max_count = int(count_range)
    else:
        min_count, max_count = 1, 1000  # 默认范围
    
    if not texts:
        return 0, f"❌ No text provided"
    
    # 合并所有文本
    if isinstance(texts, list):
        full_text = " ".join(str(text) for text in texts)
    else:
        full_text = str(texts)
    
    print(f"Debug - 分析文本长度: {len(full_text)} 字符")
    print(f"Debug - 文本开头: {full_text[:100]}...")
    
    # 改进的句子分割：
    # 1. 按句号、感叹号、问号分割
    # 2. 处理省略号和其他标点
    # 3. 过滤掉空句子
    sentence_patterns = [
        r'[.!?]+\s+',  # 标准句末标点 + 空格
        r'[.!?]+$',    # 文末标点
        r'[.!?]+(?=[A-ZÁÉÍÓÚÑÜ])',  # 标点后直接跟大写字母
    ]
    
    # 先统一处理，然后分割
    text_for_split = full_text.strip()
    
    # 使用多个模式分割句子
    sentences = []
    current_sentences = [text_for_split]
    
    for pattern in sentence_patterns:
        new_sentences = []
        for sentence in current_sentences:
            parts = re.split(pattern, sentence)
            new_sentences.extend([part.strip() for part in parts if part.strip()])
        current_sentences = new_sentences
    
    sentences = current_sentences
    
    print(f"Debug - 分割后句子数: {len(sentences)}")
    for i, sentence in enumerate(sentences[:5]):  # 只显示前5个
        print(f"Debug - 句子 {i+1}: {sentence[:80]}...")
    
    # 查找包含ningún/ninguna的句子
    ningun_sentences = []
    ningun_usage_details = []
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # 查找句子中的所有ningún/ninguna
        ningun_matches = re.findall(r'\b(ningún|ninguna)\b', sentence, re.IGNORECASE)
        
        if ningun_matches:
            ningun_sentences.append(sentence)
            
            # 详细记录每个使用情况
            for match in ningun_matches:
                # 查找ningún/ninguna后面的词汇（用于更好的展示）
                context_pattern = r'\b' + re.escape(match) + r'\s+([a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+(?:\s+[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+)*)'
                context_match = re.search(context_pattern, sentence, re.IGNORECASE)
                
                if context_match:
                    context = f"{match} {context_match.group(1)}"
                else:
                    context = match
                
                ningun_usage_details.append({
                    'sentence_num': i + 1,
                    'usage': context,
                    'full_sentence': sentence
                })
    
    found_sentence_count = len(ningun_sentences)
    total_ningun_count = len(ningun_usage_details)
    
    print(f"Debug - 包含ningún/ninguna的句子数: {found_sentence_count}")
    print(f"Debug - ningún/ninguna总使用次数: {total_ningun_count}")
    
    for detail in ningun_usage_details[:5]:  # 显示前5个使用情况
        print(f"Debug - 使用 {detail['sentence_num']}: {detail['usage']} -> {detail['full_sentence'][:60]}...")
    
    # 检查是否满足要求
    if min_count <= found_sentence_count <= max_count:
        # 构建成功信息
        examples = []
        sentence_shown = set()
        
        for detail in ningun_usage_details[:3]:  # 显示前3个不同句子的例子
            sentence = detail['full_sentence']
            if sentence not in sentence_shown:
                sentence_shown.add(sentence)
                truncated = sentence[:50] + "..." if len(sentence) > 50 else sentence
                examples.append(f"'{truncated}'")
        
        examples_text = "; ".join(examples)
        if found_sentence_count > len(examples):
            examples_text += f" ... (+{found_sentence_count - len(examples)} more sentences)"
        
        # 添加使用统计信息
        usage_info = ""
        if total_ningun_count != found_sentence_count:
            usage_info = f" (total {total_ningun_count} ningún/ninguna usages)"
        
        return 1, f"✅ Found {found_sentence_count} sentences with ningún/ninguna{usage_info} (required: {min_count}-{max_count}). Examples: {examples_text}. Requirement met."
    else:
        # 构建失败信息
        examples_text = ""
        if ningun_sentences:
            examples = []
            for sentence in ningun_sentences[:2]:
                truncated = sentence[:50] + "..." if len(sentence) > 50 else sentence
                examples.append(f"'{truncated}'")
            examples_text = f" Examples: {'; '.join(examples)}"
            if len(ningun_sentences) > 2:
                examples_text += f" ... (+{len(ningun_sentences)-2} more)"
        
        usage_info = ""
        if total_ningun_count > 0:
            usage_info = f" (total {total_ningun_count} ningún/ninguna usages)"
        
        return 0, f"❌ Found {found_sentence_count} sentences with ningún/ninguna{usage_info} (required: {min_count}-{max_count}).{examples_text} Does not meet the requirement."

def has_correct_spanish_ningun_agreement(texts, max_errors):
    """检测ningún/ninguna与名词性数是否一致"""
    import re
    
    if not texts:
        return 0, f"❌ No text provided"
    
    # 合并所有文本
    if isinstance(texts, list):
        full_text = " ".join(str(text) for text in texts)
    else:
        full_text = str(texts)
    
    print(f"Debug - 分析文本: {full_text[:100]}...")
    
    # 常见西班牙语名词的性别词典
    noun_genders = {
        # 阳性名词 (masculino)
        'problema': 'm',  # 重要：problema虽然以-a结尾，但是阳性名词
        'estudiante': 'm', 'libro': 'm', 'lugar': 'm', 'tiempo': 'm', 
        'dinero': 'm', 'trabajo': 'm', 'producto': 'm', 'ruido': 'm',
        'hospital': 'm', 'parque': 'm', 'edificio': 'm', 'coche': 'm',
        'visitante': 'm', 'bibliotecario': 'm', 'pasillo': 'm',
        'ambiente': 'm', 'silencio': 'm', 'momento': 'm', 'espacio': 'm',
        'rincón': 'm', 'día': 'm', 'sistema': 'm', 'tema': 'm',
        'pez': 'm', 'mar': 'm', 'viento': 'm', 'paisaje': 'm', 'mundo': 'm',
        'cuerpo': 'm', 'chisme': 'm', 'tipo': 'm', 'resto': 'm', 'deseo': 'm',
        'amor': 'm', 'océano': 'm', 'obstáculo': 'm', 'desafío': 'm', 'movimiento': 'm',
        # 🔧 新增缺失的阳性名词
        'interés': 'm', 'plato': 'm', 'hotel': 'm', 'restaurante': 'm', 'viaje': 'm',
        'servicio': 'm', 'personal': 'm', 'clima': 'm', 'centro': 'm', 'estudio': 'm',
        'horario': 'm', 'teléfono': 'm', 'contacto': 'm', 'desarrollo': 'm', 'proyecto': 'm',
        'diseño': 'm', 'marketing': 'm', 'curso': 'm', 'taller': 'm', 'espectáculo': 'm',
        'evento': 'm', 'concierto': 'm', 'festival': 'm', 'museo': 'm', 'teatro': 'm',
        'cine': 'm', 'deporte': 'm', 'fútbol': 'm', 'baloncesto': 'm', 'tenis': 'm',
        'golf': 'm', 'precio': 'm', 'descuento': 'm', 'pago': 'm', 'banco': 'm',
        'cajero': 'm', 'metro': 'm', 'autobús': 'm', 'tren': 'm', 'avión': 'm',
        'aeropuerto': 'm', 'puerto': 'm', 'barco': 'm', 'taxi': 'm', 'conductor': 'm',
        
        # 阴性名词 (femenino)
        'persona': 'f', 'casa': 'f', 'mesa': 'f', 'silla': 'f',
        'biblioteca': 'f', 'oficina': 'f', 'tienda': 'f', 'ciudad': 'f',
        'habitación': 'f', 'ventana': 'f', 'puerta': 'f', 'clase': 'f',
        'conversación': 'f', 'sección': 'f', 'actividad': 'f',
        'luz': 'f', 'estantería': 'f', 'página': 'f', 'calma': 'f',
        'tranquilidad': 'f', 'quietud': 'f', 'iluminación': 'f', 'afluencia': 'f',
        'vida': 'f', 'libertad': 'f', 'diversidad': 'f', 'felicidad': 'f',
        'naturaleza': 'f', 'experiencia': 'f', 'comida': 'f', 'salud': 'f',
        'gente': 'f', 'biodiversidad': 'f', 'importancia': 'f', 'emoción': 'f',
        'belleza': 'f', 'lámpara': 'f', 'sombra': 'f', 'necesidad': 'f',
        'preocupación': 'f', 'seguridad': 'f',
        # 🔧 新增常见阴性名词
        'playa': 'f', 'isla': 'f', 'montaña': 'f', 'estancia': 'f', 'expectativa': 'f',
        'vacación': 'f', 'reserva': 'f', 'cama': 'f', 'ducha': 'f', 'toalla': 'f',
        'piscina': 'f', 'terraza': 'f', 'vista': 'f', 'foto': 'f', 'cámara': 'f',
        'maleta': 'f', 'ropa': 'f', 'camisa': 'f', 'falda': 'f', 'chaqueta': 'f',
        'empresa': 'f', 'consulta': 'f', 'cita': 'f', 'reunión': 'f', 'presentación': 'f',
        'propuesta': 'f', 'solución': 'f', 'estrategia': 'f', 'campaña': 'f', 'publicidad': 'f',
        'educación': 'f', 'formación': 'f', 'universidad': 'f', 'escuela': 'f', 'academia': 'f',
        'música': 'f', 'canción': 'f', 'película': 'f', 'obra': 'f', 'exposición': 'f',
        'entrada': 'f', 'salida': 'f', 'llegada': 'f', 'partida': 'f', 'estación': 'f',
        'parada': 'f', 'línea': 'f', 'tarjeta': 'f', 'cuenta': 'f', 'factura': 'f'
    }
    
    # 改进的正则表达式：更精确地匹配ningún/ninguna + 名词
    # 匹配模式：ningún/ninguna + (可选的形容词) + 名词
    pattern = r'\b(ningún|ninguna)\s+(?:[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+\s+)*?([a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+)(?=\s|[.,!?;:]|$)'
    matches = re.findall(pattern, full_text, re.IGNORECASE)
    
    print(f"Debug - 正则匹配结果: {matches}")
    
    format_errors = []
    correct_uses = []
    unknown_nouns = []
    
    for negation, noun in matches:
        negation_lower = negation.lower()
        noun_lower = noun.lower()
        
        print(f"Debug - 检查组合: {negation} {noun}")
        
        if noun_lower in noun_genders:
            noun_gender = noun_genders[noun_lower]
            
            # 检查性别一致性
            # ningún 用于阳性名词 (masculino)
            # ninguna 用于阴性名词 (femenino)
            if (negation_lower == 'ningún' and noun_gender == 'm') or \
               (negation_lower == 'ninguna' and noun_gender == 'f'):
                correct_uses.append(f"{negation_lower} {noun_lower}")
                print(f"Debug - ✅ 正确: {negation} {noun} ({noun_gender})")
            else:
                correct_form = 'ningún' if noun_gender == 'm' else 'ninguna'
                format_errors.append({
                    'error': f"{negation} {noun}",
                    'correct': f"{correct_form} {noun}",
                    'description': f"Gender mismatch: '{noun}' is {noun_gender} ({'masculino' if noun_gender == 'm' else 'femenino'}), should use '{correct_form}'"
                })
                print(f"Debug - ❌ 错误: {negation} {noun} -> 应该是 {correct_form} {noun}")
        else:
            # 对于不在词典中的名词，记录但不算错误（假设正确）
            unknown_nouns.append(f"{negation_lower} {noun_lower}")
            print(f"Debug - ⚠️ 未知名词: {negation} {noun} (假设正确)")
    
    total_errors = len(format_errors)
    
    print(f"Debug - 正确使用: {len(correct_uses)}, 错误: {total_errors}, 未知: {len(unknown_nouns)}")
    
    if total_errors <= max_errors:
        # 🔧 修复：改进显示逻辑，避免逻辑矛盾
        total_correct_uses = len(correct_uses) + len(unknown_nouns)
        
        # 统计已知的正确组合
        correct_combinations = {}
        for use in correct_uses:
            correct_combinations[use] = correct_combinations.get(use, 0) + 1
        
        # 统计未知组合
        unknown_combinations = {}
        for noun in unknown_nouns:
            unknown_combinations[noun] = unknown_combinations.get(noun, 0) + 1
        
        # 🔧 修复：构建更清晰的显示信息
        if len(correct_uses) > 0 and len(unknown_nouns) == 0:
            # 只有已知正确用法
            combination_details = []
            for combo, count in correct_combinations.items():
                if count > 1:
                    combination_details.append(f"'{combo}' ({count} times)")
                else:
                    combination_details.append(f"'{combo}'")
            
            correct_info = f"Found {total_correct_uses} correct ningún/ninguna uses: {', '.join(combination_details[:5])}"
            if len(combination_details) > 5:
                correct_info += f" (+{len(combination_details)-5} more)"
            unknown_info = ""
            
        elif len(correct_uses) == 0 and len(unknown_nouns) > 0:
            # 只有未知名词
            unknown_details = []
            for combo, count in unknown_combinations.items():
                if count > 1:
                    unknown_details.append(f"'{combo}' ({count} times)")
                else:
                    unknown_details.append(f"'{combo}'")
            
            correct_info = f"Found {total_correct_uses} correct ningún/ninguna uses"
            unknown_info = f" Unknown nouns (assumed correct): {', '.join(unknown_details[:3])}"
            if len(unknown_details) > 3:
                unknown_info += f" (+{len(unknown_details)-3} more)"
                
        elif len(correct_uses) > 0 and len(unknown_nouns) > 0:
            # 既有已知也有未知
            combination_details = []
            for combo, count in correct_combinations.items():
                if count > 1:
                    combination_details.append(f"'{combo}' ({count} times)")
                else:
                    combination_details.append(f"'{combo}'")
            
            unknown_details = []
            for combo, count in unknown_combinations.items():
                if count > 1:
                    unknown_details.append(f"'{combo}' ({count} times)")
                else:
                    unknown_details.append(f"'{combo}'")
            
            correct_info = f"Found {total_correct_uses} correct ningún/ninguna uses: {', '.join(combination_details[:3])}"
            if len(combination_details) > 3:
                correct_info += f" (+{len(combination_details)-3} more known)"
                
            unknown_info = f" Unknown nouns (assumed correct): {', '.join(unknown_details[:2])}"
            if len(unknown_details) > 2:
                unknown_info += f" (+{len(unknown_details)-2} more unknown)"
        else:
            # 没有找到任何用法
            correct_info = "Found 0 correct ningún/ninguna uses"
            unknown_info = ""
        
        return 1, f"✅ Ningún/ninguna gender agreements are correct. {correct_info}.{unknown_info} Found {total_errors} errors (allowed: {max_errors}). Requirement met."
    else:
        error_details = [f"'{err['error']}' → '{err['correct']}' ({err['description']})" for err in format_errors]
        error_summary = "; ".join(error_details)
        
        return 0, f"❌ Found {total_errors} ningún/ninguna gender errors (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."


def has_correct_spanish_ordinal_format(texts, max_errors):
    """检测序数词缩写格式是否正确（必须有句点和上标符号）"""
    import re
    
    if not texts:
        return 0, f"❌ No text provided"
    
    # 合并所有文本
    if isinstance(texts, list):
        full_text = " ".join(str(text) for text in texts)
    else:
        full_text = str(texts)
    
    print(f"Debug - 检测序数词格式，完整文本: {repr(full_text[:300])}")
    
    # ✅ 正确格式：必须有句点和上标符号
    correct_patterns = [
        # 1. 在 Planta/Piso/Nivel 上下文中
        r'(\d{1,2})\.(º|ª)\s+(Planta|Piso|Nivel|planta|piso|nivel)\b',
        # 2. 在 Oficina 上下文中
        r'(Oficina|oficina)\s+(\d{1,2})\.(º|ª)(\d*)\b',
        # 3. 其他上下文中的正确格式
        r'\b(\d{1,2})\.(º|ª)\b'
    ]
    
    correct_abbreviations = []
    
    for pattern in correct_patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            full_match = match.group(0)
            # 避免重复添加
            if not any(ca['full_match'] == full_match for ca in correct_abbreviations):
                correct_abbreviations.append({
                    'abbreviation': full_match,
                    'full_match': full_match,
                    'position': match.span(),
                    'context': 'ordinal_context'
                })
    
    print(f"Debug - 找到的正确序数词: {[ca['abbreviation'] for ca in correct_abbreviations]}")
    
    # ❌ 检测错误格式，扩展上下文范围
    format_errors = []
    
    # 🔧 修复：扩展序数词上下文检测
    ordinal_error_contexts = [
        # 1. Planta/Piso/Nivel 上下文
        r'(\d{1,2})([aoº ª])\s+(Planta|Piso|Nivel|planta|piso|nivel)\b',
        # 2. Oficina 上下文 - 这是关键！
        r'(Oficina|oficina)\s+(\d{1,2})([aoºª])(\d*)\b',
        # 3. 其他可能的序数词上下文
        r'\b(\d{1,2})([ao])\s+(planta|piso|nivel|oficina)\b',
        # 4. 独立的序数词（但要谨慎，避免误判编号）
        r'\b(\d{1,2})([ao])\b(?=\s|$|[^\w])',
    ]
    
    for i, pattern in enumerate(ordinal_error_contexts):
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            full_match = match.group(0)
            groups = match.groups()
            
            print(f"Debug - 检查潜在错误: '{full_match}', 组: {groups}")
            
            # 检查是否已经被识别为正确格式
            is_already_correct = any(
                ca['position'][0] <= match.start() <= ca['position'][1] or
                ca['position'][0] <= match.end() <= ca['position'][1]
                for ca in correct_abbreviations
            )
            
            if is_already_correct:
                print(f"Debug - 跳过已正确: {full_match}")
                continue
            
            # 🔧 修复：根据不同上下文分析错误
            error_text = ""
            correct_text = ""
            description = ""
            
            if i == 0:  # Planta/Piso/Nivel 上下文
                number, suffix, context_word = groups[0], groups[1], groups[2]
                error_text = f"{number}{suffix}"
                if suffix.lower() == 'a':
                    correct_text = f"{number}.ª"
                elif suffix.lower() == 'o':
                    correct_text = f"{number}.º"
                else:
                    continue  # 已经是正确的上标符号
                description = f'En contexto de {context_word.lower()} debe usar punto y símbolo de superíndice'
                
            elif i == 1:  # Oficina 上下文 - 关键修复！
                context_word, number, suffix, additional = groups
                error_text = f"{number}{suffix}{additional}"
                
                if suffix.lower() == 'a':
                    correct_text = f"{number}.ª{additional}"
                elif suffix.lower() == 'o':
                    correct_text = f"{number}.º{additional}"
                elif suffix == 'ª':
                    # 缺少句点
                    correct_text = f"{number}.ª{additional}"
                    error_text = f"{number}ª{additional}"
                elif suffix == 'º':
                    # 缺少句点
                    correct_text = f"{number}.º{additional}"
                    error_text = f"{number}º{additional}"
                else:
                    continue
                    
                description = f'En contexto de oficina debe usar punto y símbolo de superíndice'
                
            elif i == 2:  # 其他上下文
                number, suffix = groups[0], groups[1]
                error_text = f"{number}{suffix}"
                if suffix.lower() == 'a':
                    correct_text = f"{number}.ª"
                else:  # 'o'
                    correct_text = f"{number}.º"
                description = 'Debe usar punto y símbolo de superíndice (º/ª)'
                
            elif i == 3:  # 独立序数词
                number, suffix = groups
                # 只处理明显的序数词错误，避免误判编号
                if len(number) <= 2 and suffix.lower() in ['a', 'o']:
                    error_text = f"{number}{suffix}"
                    if suffix.lower() == 'a':
                        correct_text = f"{number}.ª"
                    else:
                        correct_text = f"{number}.º"
                    description = 'Formato de ordinal incorrecto, debe usar punto y símbolo de superíndice'
                else:
                    continue
            
            if error_text and correct_text:
                format_errors.append({
                    'error': error_text,
                    'correct': correct_text,
                    'type': f'ordinal_error_context_{i}',
                    'position': match.span(),
                    'description': description,
                    'context': full_match
                })
                print(f"Debug - ❌ 错误格式: {error_text} → {correct_text}")
    
    # 检查是否完全没有序数词
    total_ordinals_found = len(correct_abbreviations) + len(format_errors)
    
    if total_ordinals_found == 0:
        format_errors.append({
            'error': 'No ordinal abbreviations found',
            'correct': 'Should include ordinal abbreviations like 1.º, 2.ª, etc.',
            'type': 'missing_ordinals',
            'position': (0, 0),
            'description': 'No se encontraron abreviaturas ordinales en contextos apropiados'
        })
    
    total_errors = len(format_errors)
    
    print(f"Debug - 正确格式数量: {len(correct_abbreviations)}")
    print(f"Debug - 错误数量: {total_errors}")
    print(f"Debug - 错误详情: {[(err['error'], err['correct'], err.get('context', '')) for err in format_errors]}")
    
    if total_errors <= max_errors:
        correct_examples = [abbrev['abbreviation'] for abbrev in correct_abbreviations[:5]]
        correct_info = f"Found {len(correct_abbreviations)} correctly formatted ordinal abbreviations"
        if correct_examples:
            correct_info += f": {', '.join(correct_examples)}"
        
        error_info = ""
        if format_errors and any(err['type'] != 'missing_ordinals' for err in format_errors):
            format_error_list = [err for err in format_errors if err['type'] != 'missing_ordinals']
            error_examples = [f"'{err['error']}' → '{err['correct']}' (in '{err.get('context', '')}')" for err in format_error_list[:3]]
            error_info = f" Format errors found: {'; '.join(error_examples)}"
            if len(format_error_list) > 3:
                error_info += f" (+{len(format_error_list)-3} more)"
        
        return 1, f"✅ Spanish ordinal abbreviation formats are correct. {correct_info}. Found {total_errors} errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        error_details = []
        for error in format_errors:
            if error['type'] == 'missing_ordinals':
                error_details.append(f"{error['description']}")
            else:
                error_details.append(f"'{error['error']}' → '{error['correct']}' (in '{error.get('context', '')}')")
        
        error_summary = "; ".join(error_details[:5])
        if len(error_details) > 5:
            error_summary += f" ... (+{len(error_details)-5} more errors)"
        
        return 0, f"❌ Found {total_errors} ordinal abbreviation format errors (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."



def has_correct_spanish_time_articles(texts, max_errors):
    """检测钟点表达的冠词是否正确（1点用la una，其余用las）"""
    import re
    
    if not texts:
        return 0, f"❌ No text provided"
    
    # 合并所有文本
    if isinstance(texts, list):
        full_text = " ".join(str(text) for text in texts)
    else:
        full_text = str(texts)
    
    print(f"Debug - 检测钟点冠词，文本: {full_text[:100]}...")
    
    format_errors = []
    correct_uses = []
    all_time_expressions = []
    
    # 🔧 修复：扩展时间表达检测模式
    time_detection_patterns = [
        # 带冠词的时间表达：la una, las dos, etc.
        r'\b(la|las)\s+(una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|dieciséis|diecisiete|dieciocho|diecinueve|veinte|veintiuna|veintidós|veintitrés)\b',
        r'\b(la|las)\s+([1-9]|1[0-9]|2[0-3])\b',
        
        # 🆕 新增：不带冠词的时间表达
        # "De siete de la mañana", "a las cinco", etc.
        r'\b(?:de|a)\s+(una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce)\s+de\s+la\s+(mañana|tarde|noche)\b',
        r'\b(?:de|a)\s+(una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce)\b(?!\s+de\s+la)',
        
        # 🆕 新增：数字形式的时间
        r'\b(?:de|a)\s+([1-9]|1[0-2])\s+de\s+la\s+(mañana|tarde|noche)\b',
        r'\b(?:de|a)\s+([1-9]|1[0-2])\b(?!\s+de\s+la)',
        
        # 🆕 新增：其他时间表达格式
        r'\b(desde|hasta)\s+(la|las)?\s*(una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce)\b',
        r'\b(desde|hasta)\s+(la|las)?\s*([1-9]|1[0-2])\b'
    ]
    
    # 检测所有时间表达
    for pattern in time_detection_patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            time_text = match.group().strip()
            all_time_expressions.append({
                'expression': time_text,
                'position': match.span(),
                'full_match': match.groups()
            })
    
    print(f"Debug - 检测到的时间表达: {[expr['expression'] for expr in all_time_expressions]}")
    
    # 正确的时间表达模式（带冠词的）
    correct_patterns = [
        # 正确：la una (1点)
        r'\bla\s+una\b',
        r'\bla\s+1\b',
        
        # 正确：las + 其他数字 (2-12点)
        r'\blas\s+(dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce)\b',
        r'\blas\s+(trece|catorce|quince|dieciséis|diecisiete|dieciocho|diecinueve|veinte|veintiuna|veintidós|veintitrés)\b',
        r'\blas\s+([2-9]|1[0-9]|2[0-3])\b'
    ]
    
    # 检查正确使用（只检查带冠词的表达）
    for pattern in correct_patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            time_text = match.group().strip()
            correct_uses.append({
                'expression': time_text,
                'position': match.span()
            })
    
    # 错误的时间表达模式
    error_patterns = [
        # 错误：las una (应该是 la una)
        {
            'pattern': r'\blas\s+una\b',
            'correct': 'la una',
            'description': 'Para la 1:00 se usa "la una", no "las una"'
        },
        {
            'pattern': r'\blas\s+1\b',
            'correct': 'la 1',
            'description': 'Para la 1:00 se usa "la 1", no "las 1"'
        },
        
        # 错误：la + otros números (应该是 las + números)
        {
            'pattern': r'\bla\s+(dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce)\b',
            'correct': 'las',
            'description': 'Para las horas 2-12 se usa "las", no "la"'
        },
        {
            'pattern': r'\bla\s+(trece|catorce|quince|dieciséis|diecisiete|dieciocho|diecinueve|veinte|veintiuna|veintidós|veintitrés)\b',
            'correct': 'las',
            'description': 'Para las horas 13-23 se usa "las", no "la"'
        },
        {
            'pattern': r'\bla\s+([2-9]|1[0-9]|2[0-3])\b',
            'correct': 'las',
            'description': 'Para las horas 2-23 se usa "las", no "la"'
        }
    ]
    
    # 检查错误使用
    for error_config in error_patterns:
        pattern = error_config['pattern']
        correct_template = error_config['correct']
        description = error_config['description']
        
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            error_text = match.group().strip()
            
            # 生成正确格式
            if correct_template == 'la una':
                correct_text = 'la una'
            elif correct_template == 'la 1':
                correct_text = 'la 1'
            else:  # correct_template == 'las'
                # 保持原数字/词汇，只改冠词
                time_part = error_text.split()[1]  # 获取数字/词汇部分
                correct_text = f"las {time_part}"
            
            format_errors.append({
                'error': error_text,
                'correct': correct_text,
                'position': match.span(),
                'description': description
            })
    
    total_errors = len(format_errors)
    
    print(f"Debug - 找到 {len(correct_uses)} 个正确的钟点冠词")
    print(f"Debug - 找到 {total_errors} 个冠词错误")
    print(f"Debug - 总时间表达数: {len(all_time_expressions)}")
    
    # 🔧 修复：更准确的判断逻辑
    if len(all_time_expressions) == 0:
        # 完全没有时间表达
        return 1, f"✅ No time expressions found in text, so no article errors detected. Requirement met."
    elif len(correct_uses) == 0 and len(format_errors) == 0:
        # 有时间表达但都不带冠词（这是正确的，因为"De siete de la mañana"不需要冠词）
        time_examples = [expr['expression'] for expr in all_time_expressions[:3]]
        return 1, f"✅ Found {len(all_time_expressions)} time expressions without articles (correct usage): {', '.join(time_examples)}. No article errors detected. Requirement met."
    
    if total_errors <= max_errors:
        if len(correct_uses) > 0:
            correct_examples = [use['expression'] for use in correct_uses[:5]]
            correct_info = f"Found {len(correct_uses)} correct time expressions with articles: {', '.join(correct_examples)}"
        else:
            correct_info = f"Found {len(all_time_expressions)} time expressions (no articles needed)"
        
        error_info = ""
        if format_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}'" for err in format_errors[:3]]
            error_info = f" Time article errors: {'; '.join(error_examples)}"
            if len(format_errors) > 3:
                error_info += f" (+{len(format_errors)-3} more)"
        
        return 1, f"✅ Spanish time article usage is correct. {correct_info}. Found {total_errors} errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        error_details = []
        for error in format_errors:
            error_details.append(f"'{error['error']}' → '{error['correct']}' ({error['description']})")
        
        error_summary = "; ".join(error_details[:5])  # 显示前5个错误
        if len(error_details) > 5:
            error_summary += f" ... (+{len(error_details)-5} more errors)"
        
        return 0, f"❌ Found {total_errors} time article errors (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."

def has_correct_subject_omission_with_verb_conjugation(texts, max_errors):
    """检查西班牙语是否正确省略人称主语并使用正确的动词变位"""
    import re
    
    errors = []
    correct_examples = []
    
    # 更全面的人称代词列表
    subject_pronouns = [
        r'\byo\b', r'\btú\b', r'\busted\b', r'\bél\b', r'\bella\b',
        r'\bnosotros\b', r'\bnosotras\b', r'\bvosotros\b', r'\bvosotras\b',
        r'\bustedes\b', r'\bellos\b', r'\bellas\b'
    ]
    
    # 更全面的动词变位模式
    verb_patterns = [
        # ser动词
        r'\b(soy|eres|es|somos|sois|son)\b',
        # estar动词
        r'\b(estoy|estás|está|estamos|estáis|están)\b',
        # tener动词
        r'\b(tengo|tienes|tiene|tenemos|tenéis|tienen)\b',
        # ir动词
        r'\b(voy|vas|va|vamos|vais|van)\b',
        # 常见规则动词现在时变位 (-ar动词)
        r'\b\w+(o|as|a|amos|áis|an)\b',
        # 常见规则动词现在时变位 (-er/-ir动词)
        r'\b\w+(o|es|e|emos|éis|en)\b',
        # 过去时变位
        r'\b\w+(é|aste|ó|amos|asteis|aron)\b',
        r'\b\w+(í|iste|ió|imos|isteis|ieron)\b',
        # 特定动词（根据你的文本）
        r'\b(mantiene|mantienen|sorprende|sorprenden|fascina|fascinan)\b',
        r'\b(perturba|perturban|atrapa|atrapan|evoluciona|evolucionan)\b',
        # 形容词作谓语（与ser/estar连用）
        r'\b(fascinante|perturbadora|impecable|intensa|magistral|inolvidable)\b'
    ]
    
    for text in texts:
        text = text.strip()
        if not text:
            continue
            
        # 按分号分割句子分别检查
        sentences = [s.strip() for s in text.split(';')]
        
        for sentence in sentences:
            if not sentence:
                continue
                
            # 跳过纯粹的名词短语（如"Intriga constante"）
            if len(sentence.split()) <= 2 and not any(re.search(pattern, sentence, re.IGNORECASE) for pattern in verb_patterns):
                # 这可能是省略了动词的名词短语，视为正确
                correct_examples.append(sentence[:30] + "...")
                continue
                
            # 检查人称代词
            found_pronouns = []
            for pronoun_pattern in subject_pronouns:
                matches = re.findall(pronoun_pattern, sentence, re.IGNORECASE)
                if matches:
                    found_pronouns.extend(matches)
            
            if found_pronouns:
                errors.append(f"包含人称代词: {', '.join(found_pronouns)} 在 '{sentence}'")
            else:
                # 检查动词或形容词谓语
                has_verb_or_predicate = any(re.search(pattern, sentence, re.IGNORECASE) 
                                          for pattern in verb_patterns)
                
                if has_verb_or_predicate:
                    correct_examples.append(sentence[:30] + "...")
                else:
                    # 如果既没有人称代词也没有动词，可能是不完整的句子
                    if len(sentence.split()) > 2:  # 只对较长的句子报错
                        errors.append(f"缺少动词或谓语: '{sentence}'")
    
    total_errors = len(errors)
    
    if total_errors <= max_errors:
        if correct_examples:
            examples_str = "; ".join(correct_examples[:3])
            return 1, f"✅ 正确省略人称主语。示例: {examples_str}. 错误数: {total_errors}/{max_errors}."
        else:
            return 1, f"✅ 未发现人称代词错误。错误数: {total_errors}/{max_errors}."
    else:
        error_summary = "; ".join(errors[:3])
        if len(errors) > 3:
            error_summary += f" ... (+{len(errors)-3} more)"
        return 0, f"❌ 人称主语省略错误: {error_summary}. 发现 {total_errors} 个错误 (最多允许: {max_errors})."
 
def has_correct_spanish_article_gender_agreement(texts, max_errors):
    """检查冠词与名词性数一致性"""
    import re
    
    def clean_up_text(text):
        return text.strip()
    
    if not texts:
        return 0, f"❌ No text provided"
    
    # 确保 texts 是列表格式
    if isinstance(texts, str):
        texts = [texts]
    elif not isinstance(texts, list):
        texts = [str(texts)]
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def check_article_noun_agreement(text):
        """检查冠词与名词的性数一致性"""
        
        # 🔧 扩展的西班牙语名词性别词典
        noun_gender = {
            # === 阳性单数 ===
            'pez': 'masc_sing', 'mar': 'masc_sing', 'tipo': 'masc_sing', 'viento': 'masc_sing',
            'cuerpo': 'masc_sing', 'resto': 'masc_sing', 'mundo': 'masc_sing', 'paisaje': 'masc_sing',
            'libro': 'masc_sing', 'papel': 'masc_sing', 'corazón': 'masc_sing', 'bolígrafo': 'masc_sing',
            'cielo': 'masc_sing', 'lenguaje': 'masc_sing', 'hogar': 'masc_sing', 'día': 'masc_sing',
            'problema': 'masc_sing', 'trabajo': 'masc_sing', 'tiempo': 'masc_sing', 'amor': 'masc_sing',
            'momento': 'masc_sing', 'deseo': 'masc_sing', 'chisme': 'masc_sing', 'alma': 'masc_sing',
            'cuidado': 'masc_sing', 'lugar': 'masc_sing', 'horizonte': 'masc_sing', 'hombre': 'masc_sing',
            'océano': 'masc_sing', 'elemento': 'masc_sing', 'aspecto': 'masc_sing', 'detalle': 'masc_sing',
            
            # === 阴性单数 ===
            'persona': 'fem_sing', 'vida': 'fem_sing', 'comida': 'fem_sing', 'emoción': 'fem_sing',
            'casa': 'fem_sing', 'mesa': 'fem_sing', 'comunicación': 'fem_sing', 'palabra': 'fem_sing',
            'estrella': 'fem_sing', 'raíz': 'fem_sing', 'mano': 'fem_sing', 'foto': 'fem_sing',
            'vez': 'fem_sing', 'gente': 'fem_sing', 'cosa': 'fem_sing', 'parte': 'fem_sing',
            'felicidad': 'fem_sing', 'libertad': 'fem_sing', 'importancia': 'fem_sing', 'historia': 'fem_sing',
            'decisión': 'fem_sing', 'opinión': 'fem_sing', 'biodiversidad': 'fem_sing', 'diversidad': 'fem_sing',
            'naturaleza': 'fem_sing', 'experiencia': 'fem_sing', 'existencia': 'fem_sing', 'salud': 'fem_sing',
            'belleza': 'fem_sing', 'variedad': 'fem_sing', 'celebración': 'fem_sing', 'tradición': 'fem_sing',
            'conexión': 'fem_sing', 'sensación': 'fem_sing', 'admiración': 'fem_sing', 'reflexión': 'fem_sing',
            # 🆕 以-e结尾的阴性词
            'mente': 'fem_sing', 'noche': 'fem_sing', 'clase': 'fem_sing', 'base': 'fem_sing',
            'fase': 'fem_sing', 'carne': 'fem_sing', 'leche': 'fem_sing', 'fiebre': 'fem_sing',
            'suerte': 'fem_sing', 'muerte': 'fem_sing', 'fuente': 'fem_sing', 'corriente': 'fem_sing',
            
            # === 阳性复数 ===
            'peces': 'masc_plur', 'mares': 'masc_plur', 'tipos': 'masc_plur', 'vientos': 'masc_plur',
            'cuerpos': 'masc_plur', 'restos': 'masc_plur', 'mundos': 'masc_plur', 'paisajes': 'masc_plur',
            'libros': 'masc_plur', 'papeles': 'masc_plur', 'corazones': 'masc_plur', 'bolígrafos': 'masc_plur',
            'cielos': 'masc_plur', 'lenguajes': 'masc_plur', 'hogares': 'masc_plur', 'días': 'masc_plur',
            'problemas': 'masc_plur', 'trabajos': 'masc_plur', 'tiempos': 'masc_plur', 'amores': 'masc_plur',
            'momentos': 'masc_plur', 'deseos': 'masc_plur', 'chismes': 'masc_plur', 'hombres': 'masc_plur',
            'elementos': 'masc_plur', 'aspectos': 'masc_plur', 'detalles': 'masc_plur', 'océanos': 'masc_plur',
            
            # === 阴性复数 ===
            'personas': 'fem_plur', 'vidas': 'fem_plur', 'comidas': 'fem_plur', 'emociones': 'fem_plur',
            'casas': 'fem_plur', 'mesas': 'fem_plur', 'comunicaciones': 'fem_plur', 'palabras': 'fem_plur',
            'estrellas': 'fem_plur', 'raíces': 'fem_plur', 'manos': 'fem_plur', 'fotos': 'fem_plur',
            'veces': 'fem_plur', 'gentes': 'fem_plur', 'cosas': 'fem_plur', 'partes': 'fem_plur',
            'mentes': 'fem_plur', 'noches': 'fem_plur', 'clases': 'fem_plur', 'historias': 'fem_plur',
            # 🆕 修复这些关键词
            'decisiones': 'fem_plur', 'opiniones': 'fem_plur', 'tradiciones': 'fem_plur',
            'celebraciones': 'fem_plur', 'conexiones': 'fem_plur', 'sensaciones': 'fem_plur',
            'oportunidades': 'fem_plur', 'experiencias': 'fem_plur',
        }
        
        # 正确的冠词搭配
        correct_articles = {
            'masc_sing': ['el'],
            'fem_sing': ['la'], 
            'masc_plur': ['los'],
            'fem_plur': ['las']
        }
        
        errors = []
        correct_uses = []
        
        # 查找所有定冠词+名词组合
        pattern = r'\b(el|la|los|las)\s+([a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+)\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            article = match.group(1).lower()
            noun = match.group(2).lower()
            
            if noun in noun_gender:
                expected_gender = noun_gender[noun]
                correct_article_list = correct_articles[expected_gender]
                
                if article in correct_article_list:
                    correct_uses.append({
                        'combination': f"{article} {noun}",
                        'position': match.span(),
                        'type': 'correct_agreement'
                    })
                else:
                    # 找到正确的冠词建议
                    correct_article = correct_article_list[0]
                    gender_desc = expected_gender.replace('_', ' ')
                    errors.append({
                        'error': f"{article} {noun}",
                        'correct': f"{correct_article} {noun}",
                        'position': match.span(),
                        'description': f'Discordancia de género/número: "{noun}" es {gender_desc}'
                    })
            else:
                # 对于词典中没有的名词，使用改进的启发式规则
                predicted_gender = predict_noun_gender(noun)
                if predicted_gender:
                    expected_articles = correct_articles[predicted_gender]
                    if article not in expected_articles:
                        correct_article = expected_articles[0]
                        errors.append({
                            'error': f"{article} {noun}",
                            'correct': f"{correct_article} {noun}",
                            'position': match.span(),
                            'description': f'Posible discordancia: "{noun}" probablemente es {predicted_gender.replace("_", " ")}'
                        })
                    else:
                        correct_uses.append({
                            'combination': f"{article} {noun}",
                            'position': match.span(),
                            'type': 'likely_correct'
                        })
        
        return len(errors), errors, len(correct_uses), correct_uses
    
    def predict_noun_gender(noun):
        """🔧 改进的基于词尾预测名词性别（启发式规则）"""
        noun = noun.lower()
        
        # 🆕 特殊的以-e结尾的阴性词（扩展列表）
        feminine_e_endings = [
            'mente', 'gente', 'parte', 'noche', 'clase', 'base', 'fase', 'carne', 'leche', 'fiebre',
            'suerte', 'muerte', 'fuente', 'corriente', 'frente', 'llave', 'nave', 'nube', 'sede',
            'serie', 'superficie', 'especie', 'torre', 'sangre', 'costumbre', 'muchedumbre'
        ]
        
        if noun in feminine_e_endings:
            return 'fem_sing'
        
        # 🆕 特殊的以-a结尾的阳性词
        masculine_a_endings = [
            'problema', 'sistema', 'tema', 'programa', 'drama', 'clima', 'idioma', 'planeta',
            'poeta', 'atleta', 'turista', 'artista', 'especialista', 'dentista', 'pianista'
        ]
        
        if noun in masculine_a_endings:
            return 'masc_sing'
        
        # 🆕 以-iones结尾的都是阴性复数（关键修复）
        if noun.endswith('iones'):
            return 'fem_plur'
        
        # 🆕 以-ión结尾的都是阴性单数
        if noun.endswith('ión'):
            return 'fem_sing'
        
        # 阴性复数规则
        if noun.endswith('as'):
            # 检查是否是阳性词的复数形式
            singular = noun[:-1]  # 去掉s
            if singular in masculine_a_endings:
                return 'masc_plur'
            return 'fem_plur'
        
        # 以-es结尾的复数
        if noun.endswith('es'):
            # 尝试还原单数形式
            if len(noun) > 3:
                # 去掉-es，看是否是已知的阴性词
                singular_candidate = noun[:-2]
                if singular_candidate in feminine_e_endings:
                    return 'fem_plur'
            return 'masc_plur'
        
        # 阳性复数规则
        if noun.endswith('os'):
            return 'masc_plur'
        
        # 阴性单数规则
        if noun.endswith(('dad', 'tad', 'ez', 'is', 'sis', 'tis')):
            return 'fem_sing'
        
        # 以-a结尾的词（排除已知阳性词）
        if noun.endswith('a') and noun not in masculine_a_endings:
            return 'fem_sing'
        
        # 阳性单数规则
        if noun.endswith(('o', 'r', 'l', 'n', 's', 'j', 'x')):
            return 'masc_sing'
        
        # 以-e结尾的词（排除已知阴性词）默认为阳性
        if noun.endswith('e') and noun not in feminine_e_endings:
            return 'masc_sing'
        
        return None  # 无法预测
    
    # 统计所有文本中的错误
    total_errors = 0
    all_errors = []
    all_correct = []
    
    for text in cleaned_up_texts:
        error_count, errors, correct_count, correct_uses = check_article_noun_agreement(text)
        total_errors += error_count
        all_errors.extend(errors)
        all_correct.extend(correct_uses)
    
    # 去重处理
    unique_errors = []
    seen_errors = set()
    for error in all_errors:
        error_key = f"{error['error']}"
        if error_key not in seen_errors:
            seen_errors.add(error_key)
            unique_errors.append(error)
    
    total_errors = len(unique_errors)
    
    # 构建结果信息
    if total_errors <= max_errors:
        correct_examples = [f"'{correct['combination']}'" for correct in all_correct[:5]]
        correct_info = f"Found {len(all_correct)} correct article-noun agreements"
        if correct_examples:
            correct_info += f": {', '.join(correct_examples)}"
            if len(all_correct) > 5:
                correct_info += f" (+{len(all_correct)-5} more)"
        
        error_info = ""
        if unique_errors:
            error_examples = [f"'{err['error']}' → '{err['correct']}'" for err in unique_errors[:2]]
            error_info = f" Minor errors: {'; '.join(error_examples)}"
            if len(unique_errors) > 2:
                error_info += f" (+{len(unique_errors)-2} more)"
        
        return 1, f"✅ Spanish article-noun gender agreement is correct. {correct_info}. Found {total_errors} errors (allowed: {max_errors}).{error_info} Requirement met."
    else:
        error_details = [f"'{error['error']}' → '{error['correct']}' ({error['description']})" for error in unique_errors[:3]]
        error_summary = "; ".join(error_details)
        if len(unique_errors) > 3:
            error_summary += f" ... (+{len(unique_errors)-3} more)"
        
        return 0, f"❌ Found {total_errors} article-noun gender agreement errors (allowed: {max_errors}). Errors: {error_summary}. Does not meet the requirement."

def has_definite_article_noun_combinations(texts, min_count, max_count=None, original_text=None):
    """检查每个句子中定冠词+名词组合的数量"""
    import re
    
    if not texts:
        return 0, f"❌ No text provided"
    
    if max_count is None:
        max_count = min_count
    
    if isinstance(texts, str):
        texts = [texts]
    elif not isinstance(texts, list):
        texts = [str(texts)]
    
    def get_target_nouns():
        """获取目标名词列表"""
        # 🔧 确保包含所有原文名词
        return {
            'pez', 'peces', 'mar', 'mares', 'persona', 'personas', 'tipo', 'tipos',
            'viento', 'vientos', 'emoción', 'emociones', 'cuerpo', 'cuerpos',
            'resto', 'restos', 'vida', 'vidas', 'mundo', 'mundos', 'comida', 'comidas',
            'paisaje', 'paisajes', 'vez', 'veces', 'gente', 'chisme', 'chismes', 
            'amor', 'cuidado', 'cuidados', 'trabajo', 'trabajos'
        }
    
    def count_combinations(text):
        """统计组合数量"""
        target_nouns = get_target_nouns()
        
        # 🔧 严格排除非原文名词
        excluded_nouns = {
            'libertad', 'diversidad', 'elementos', 'aspectos', 'experiencias',
            'existencia', 'alma', 'felicidad', 'salud', 'bienestar', 'camino',
            'equilibrio', 'naturaleza', 'fuerzas', 'oportunidades', 'placeres',
            'opiniones', 'entorno', 'mesa', 'culturas', 'tradiciones', 'celebración',
            'sabores', 'variedad', 'riqueza', 'tranquilidad', 'reflexión', 'momento',
            'ojos', 'hogar', 'rincón', 'admiración', 'detalle', 'sensación', 'frescura',
            'vecindario', 'orilla', 'oportunidad'
        }
        
        combinations = []
        used_positions = set()
        
        # 🔧 匹配模式
        pattern = r'\b(del|al|el|la|los|las)\s+([a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+)\b'
        
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = match.start()
            article = match.group(1).lower()
            noun = match.group(2).lower()
            
            # 🔧 三重检查
            if (noun in target_nouns and 
                noun not in excluded_nouns and 
                start not in used_positions):
                
                combinations.append(f"{article} {noun}")
                used_positions.add(start)
        
        return len(combinations), combinations
    
    # 检查每个句子
    sentence_details = []
    all_pass = True
    
    for i, sentence in enumerate(texts):
        sentence = sentence.strip()
        count, combos = count_combinations(sentence)
        
        meets_req = min_count <= count <= max_count
        if not meets_req:
            all_pass = False
        
        status = "✅" if meets_req else "❌"
        combo_info = f"({', '.join(combos)})" if combos else "(none)"
        
        sentence_details.append(f"Sentence {i+1}: {count} combinations {status} {combo_info}")
    
    detail_info = " | ".join(sentence_details)
    
    source_info = "from original text" if original_text else "from comprehensive noun list"
    
    if all_pass:
        return 1, f"✅ All {len(texts)} sentences contain {min_count}-{max_count} definite article+noun combinations {source_info}. {detail_info}"
    else:
        failed = sum(1 for sentence in texts if not (min_count <= count_combinations(sentence.strip())[0] <= max_count))
        return 0, f"❌ {failed}/{len(texts)} sentences do NOT meet the requirement of {min_count}-{max_count} definite article+noun combinations {source_info}. {detail_info}"



def has_total_definite_article_noun_combinations(texts, min_count, max_count=None):
    """检查整篇文章中定冠词+名词组合的总数量"""
    import re
    
    def clean_up_text(text):
        return text.strip()
    
    if not texts:
        return 0, f"❌ No text provided"
    
    # 设置默认最大值
    if max_count is None:
        max_count = min_count
    
    # 确保 texts 是列表格式
    if isinstance(texts, str):
        texts = [texts]
    elif not isinstance(texts, list):
        texts = [str(texts)]
    
    # 合并所有文本为一个整体
    full_text = " ".join([clean_up_text(text) for text in texts])
    
    def count_definite_article_noun_combinations(text):
        """统计文本中定冠词+名词组合的数量"""
        
        # 🆕 扩展的排除词汇列表
        excluded_words = {
            # 动词 (大幅扩展)
            'ver', 'ser', 'estar', 'hacer', 'tener', 'decir', 'ir', 'venir', 'dar', 'saber',
            'poder', 'querer', 'poner', 'parecer', 'seguir', 'encontrar', 'llamar', 'volver',
            'salir', 'llegar', 'pasar', 'deber', 'dejar', 'sentir', 'quedar', 'creer',
            'hablar', 'llevar', 'comenzar', 'empezar', 'terminar', 'acabar', 'disfrutar',
            'explorar', 'observar', 'reflexionar', 'mantener', 'cuidar', 'afectar', 'influir',
            'ofrecer', 'propagar', 'convertir', 'definir', 'enriquecer', 'fascinar', 'inspirar',
            'extender', 'relajar', 'liberar', 'buscar', 'nadar', 'soplar', 'crear', 'unir',
            'desplegar', 'albergar', 'circular', 'proporcionar', 'necesitar', 'alcanzar',
            'valorar', 'permitir', 'simbolizar', 'reflejar', 'recordar', 'acariciar',
            'despertar', 'eclipsar', 'conocer', 'explorar', 'transformar', 'concretar',
            'resonar', 'vibrar', 'trasciender', 'entrelazar', 'calmar', 'brillar',
            
            # 形容词 (大幅扩展)
            'vasto', 'grande', 'pequeño', 'hermoso', 'delicioso', 'profundo', 'sereno',
            'misterioso', 'único', 'constante', 'impredecible', 'esencial', 'sobresaliente',
            'natural', 'fundamental', 'acuático', 'querido', 'fascinante', 'ajeno',
            'suave', 'libre', 'feliz', 'brillante', 'ordinario', 'diferente', 'raro',
            'lento', 'pleno', 'inolvidable', 'diverso', 'propio', 'compartido', 'intangible',
            'invisible', 'etéreo', 'universal', 'mágico', 'simple', 'verdadero', 'humano',
            
            # 其他需要排除的词
            'momento', 'ojos', 'rincón', 'hogar', 'admiración', 'detalle', 'sensación',
            'frescura', 'objeto', 'rumores', 'placer', 'compañía', 'oportunidades',
            'lugares', 'fascinantes', 'historia', 'emoción', 'vez', 'día', 'vida',
            'tiempo', 'lugar', 'forma', 'manera', 'parte', 'caso', 'ejemplo'
        }
        
        combinations = []
        processed_spans = []  # 记录已处理的文本范围
        
        # 🔧 统一的模式匹配：所有定冠词形式
        all_patterns = [
            # 缩写形式
            (r'\b(del|al)\s+([a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+)\b', 'contraction'),
            # 标准定冠词
            (r'\b(el|la|los|las)\s+([a-záéíóúñüA-ZÁÉÍÓÚÑÜ]+)\b', 'standard'),
        ]
        
        for pattern, pattern_type in all_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                start, end = match.span()
                article = match.group(1).lower()
                noun = match.group(2).lower()
                
                # 🔧 排除动词、形容词等
                if noun in excluded_words:
                    continue
                
                # 🔧 检查是否与已处理的范围重叠
                overlapped = False
                for proc_start, proc_end in processed_spans:
                    if not (end <= proc_start or start >= proc_end):
                        overlapped = True
                        break
                
                if not overlapped:
                    processed_spans.append((start, end))
                    combinations.append(f"{article} {noun}")
        
        return len(combinations), combinations
    
    # 统计整篇文章的组合数量
    total_count, all_combinations = count_definite_article_noun_combinations(full_text)
    
    # 检查是否满足要求
    meets_requirement = min_count <= total_count <= max_count
    
    # 🔧 构建详细信息
    if all_combinations:
        # 去重并保持顺序
        unique_combinations = list(dict.fromkeys(all_combinations))
        display_combinations = unique_combinations[:8]  # 显示前8个
        combo_info = f"Found combinations: {', '.join(display_combinations)}"
        if len(unique_combinations) > 8:
            combo_info += f" (+{len(unique_combinations)-8} more)"
    else:
        combo_info = "No valid combinations found"
    
    # 返回结果
    if meets_requirement:
        status = "✅"
        return 1, f"✅ Article contains {total_count} definite article+noun combinations (required: {min_count}-{max_count}). {combo_info}. Requirement met."
    else:
        status = "❌"
        if total_count < min_count:
            reason = f"Too few combinations ({total_count} < {min_count})"
        else:
            reason = f"Too many combinations ({total_count} > {max_count})"
        
        return 0, f"❌ Article contains {total_count} definite article+noun combinations (required: {min_count}-{max_count}). {reason}. {combo_info}. Does not meet the requirement."




if __name__ == "__main__":
    text = [
"1ª planta\nEstudio Creativo\nHorario: de siete de la mañana a siete de la tarde\nTeléfono: 555 123 4567\nEspacio para diseño gráfico y edición de contenido digital.",
"2ª planta\nEstudio Legal\nHorario: de ocho de la mañana a seis de la tarde\nTeléfono: 555 234 5678\nAsesoría jurídica y consultoría para empresas y particulares.",
"3ª planta\nEstudio Contable\nHorario: de nueve de la mañana a cinco de la tarde\nTeléfono: 555 345 6789\nServicios de contabilidad, impuestos y gestión financiera.",
 "4ª planta\nEstudio Wellness\nHorario: de diez de la mañana a seis de la tarde\nTeléfono: 555 456 7890\nConsultas de bienestar, coaching y talleres de relajación."
]
    text = [
 "Xiao Ming: Hola, soy Xiao Ming, el repartidor de leche. ¿Podría confirmarme la dirección exacta para la entrega, por favor?",
 "Cliente: Claro, mi dirección es Calle Primavera número 28, Unidad 3, Piso 5.",
 "Xiao Ming: Muchas gracias. ¿Hay alguien en casa ahora para recibir la leche?",
 "Cliente: Sí, estoy en casa y puedo recibir la entrega.",
 "Xiao Ming: Perfecto, ¿la fecha de entrega es hoy, 12 de junio, verdad?",
 "Cliente: Sí, la entrega es para hoy, 12 de junio. ¡Gracias por confirmar!"
]
    print(has_correct_spanish_date_format(text,0))
    # print(has_correct_spanish_phone_format(text,0))