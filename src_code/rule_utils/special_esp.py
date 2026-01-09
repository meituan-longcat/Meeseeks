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


def has_complete_exclamations(texts, times):
    """检查每条评论是否都包含指定数量的完整西班牙语感叹句（¡...!)"""
    
    if not texts:
        return 0, f"❌ No comments provided"
    
    # 确保 texts 是列表格式
    if isinstance(texts, str):
        comments = [texts]
    elif isinstance(texts, list):
        comments = texts
    else:
        comments = [str(texts)]
    
    # 完整感叹句的正则模式：¡开头，!结尾
    complete_exclamation_pattern = r'¡[^¡!]*!'
    
    comment_details = []
    all_match = True
    
    # 检查每个评论
    for i, comment in enumerate(comments):
        comment_text = str(comment).strip()
        
        # 查找完整的感叹句
        matches = re.findall(complete_exclamation_pattern, comment_text, re.DOTALL)
        exclamation_count = len(matches)
        
        print(f"Debug - Comment {i+1} 找到的感叹句: {matches}")
        
        # 检查是否符合要求
        matches_requirement = (exclamation_count == times)
        if not matches_requirement:
            all_match = False
        
        # 记录详情
        status = "✅" if matches_requirement else "❌"
        if matches:
            display_exclamations = [exc[:30] + "..." if len(exc) > 30 else exc for exc in matches[:3]]
            comment_details.append(f"Comment {i+1}: {exclamation_count} exclamations {status} ({', '.join(display_exclamations)})")
        else:
            comment_details.append(f"Comment {i+1}: {exclamation_count} exclamations {status}")
    
    detail_info = " | ".join(comment_details)
    
    # 返回结果
    if all_match:
        return 1, f"✅ All {len(comments)} comments have exactly {times} exclamations: {detail_info}"
    else:
        return 0, f"❌ Some comments do NOT have exactly {times} exclamations: {detail_info}"


def has_spanish_word_count(texts, min_count, max_count):
    """检查每条西班牙语评论的单词数量是否都在指定范围内"""
    
    # texts 参数实际上是 corresponding_parts 提取出的评论列表
    # 应该已经是一个包含各个评论的列表
    
    if not texts:
        return 0, f"❌ No comments provided"
    
    # 确保 texts 是列表格式
    if isinstance(texts, str):
        # 如果是单个字符串，可能需要分割
        comments = [texts]
    elif isinstance(texts, list):
        comments = texts
    else:
        comments = [str(texts)]
    
    # 调试信息
    print(f"Debug - 收到 {len(comments)} 条评论")
    for i, comment in enumerate(comments):
        print(f"Debug - 评论 {i+1}: {str(comment)[:100]}...")
    
    # 西班牙语单词的正则模式
    spanish_word_pattern = r'\b[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+\b'
    
    comment_details = []
    all_in_range = True
    
    for i, comment in enumerate(comments):
        # 转换为字符串并清理
        comment_text = str(comment).strip()
        
        # 统计单词数
        words = re.findall(spanish_word_pattern, comment_text)
        word_count = len(words)
        
        print(f"Debug - 评论 {i+1} 单词数: {word_count}")
        
        # 检查是否在范围内
        in_range = min_count <= word_count <= max_count
        if not in_range:
            all_in_range = False
        
        # 记录详情
        status = "✅" if in_range else "❌"
        comment_details.append(f"Comment {i+1}: {word_count} words {status}")
    
    detail_info = " | ".join(comment_details)
    
    # 返回结果
    if all_in_range:
        return 1, f"✅ All {len(comments)} comments within range [{min_count}, {max_count}]: {detail_info}"
    else:
        return 0, f"❌ Some of {len(comments)} comments NOT within range [{min_count}, {max_count}]: {detail_info}"


def has_spanish_accent_count(texts, num):
    """检查每个文本是否都包含指定数量的西班牙语重音符号"""
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    def count_spanish_accent_marks(text):
        """统计文本中西班牙语重音符号的数量"""
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
        
        # 直接在整个文本中查找所有重音符号
        accent_matches = re.findall(r'[áéíóúüñÁÉÍÓÚÜÑ]', text)
        total_accent_count = len(accent_matches)
        
        # 查找包含重音符号的单词
        words_with_accents = []
        words = re.findall(r'\b[\w\u00C0-\u017F]+\b', text)
        
        for word in words:
            if any(char in spanish_accented_chars for char in word):
                words_with_accents.append(word)
        
        # 统计每种重音符号的数量
        accent_distribution = {}
        for accent in accent_matches:
            accent_distribution[accent] = accent_distribution.get(accent, 0) + 1
        
        return total_accent_count, words_with_accents, accent_matches, accent_distribution
    
    # 检查每个文本
    for text in cleaned_up_texts:
        accent_count, accented_words, accent_list, accent_dist = count_spanish_accent_marks(text)
        
        # 构建详细的重音符号信息
        accent_detail = []
        for accent, count in accent_dist.items():
            accent_detail.append(f"{accent}×{count}")
        
        accent_summary = f"[{', '.join(accent_list)}]" if accent_list else "[]"
        accent_breakdown = f"({', '.join(accent_detail)})" if accent_detail else "(无)"
        
        if accent_count < num:
            return 0, f"❌ Text contains {accent_count} spanish accent marks (required: {num}). Found accents: {accent_summary} {accent_breakdown}. Words with accents: {accented_words}. Does not meet the requirement."
    
    # 如果所有文本都满足要求，返回最后一个文本的详细信息
    final_accent_summary = f"[{', '.join(accent_list)}]" if accent_list else "[]"
    final_accent_breakdown = f"({', '.join(accent_detail)})" if accent_detail else "(无)"
    
    return 1, f"✅ Each text contains sufficient spanish accent marks (required: {num}). Found {accent_count} accents: {final_accent_summary} {final_accent_breakdown}. Words with accents: {accented_words}. Requirement met."

def clean_up_text(text):
    """清理文本，保留重音符号"""
    if text is None:
        return ""
    # 保留所有重音符号，只规范化空白字符
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

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




if __name__ == "__main__":
    text = [ "Oficina 1ª1 – $120,000  Espaciosa, luminosa, con ventanales y acceso directo al vestíbulo.",
 "Oficina 1ª2 – $115,000  Moderna, con sala de juntas, aire acondicionado y excelente ubicación.",
 "Oficina 2ª1 – $130,000  Amplia, vista panorámica, baño privado y excelente iluminación natural.",
 "Oficina 2ª2 – $125,000  Funcional, con recepción, dos despachos y conexión a internet rápida."
]
    print(has_spanish_accent_count(text,[8,8]))







