import os
import sys
# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..utils import clean_up_text
try:
    import char_similar
    char_similar_AVAILABLE = True
except ImportError:
    char_similar_AVAILABLE = False
    print("char_similar库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "char_similar", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("char_similar库安装成功，正在导入...")
        import char_similar
        char_similar_AVAILABLE = True
        print("✅ char_similar库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install char_similar")
        char_similar_AVAILABLE = False

def model_jielong(chengyu_list):
    for i in range(len(chengyu_list)):
        chengyu_list[i] = clean_up_text(chengyu_list[i])

    for i in range(len(chengyu_list) - 1):
        last_char = chengyu_list[i][-1]
        next_first_char = chengyu_list[i + 1][0]
        if last_char != next_first_char:
            return 0, f"❌ 不匹配，词语：{str(chengyu_list[i])}的最后一个字和词语：{str(chengyu_list[i + 1])}的第一个字不一致"
    return 1, f"✅ 匹配，词语：{str(chengyu_list)}"

def model_jielong2(chengyu_list):
    # 清理文本
    for i in range(len(chengyu_list)):
        chengyu_list[i] = clean_up_text(chengyu_list[i])
    
    # 数字映射
    number_chars = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    
    # 检查每个成语是否以正确的数字开头
    for i in range(len(chengyu_list)):
        if i >= len(number_chars):
            return 0, f"❌ 不匹配，超出支持的数字范围（最多支持到十）"
        
        expected_number = number_chars[i]
        if not chengyu_list[i].startswith(expected_number):
            return 0, f"❌ 不匹配，成语：{str(chengyu_list[i])}应该以'{expected_number}'开头"
    
    return 1, f"✅ 匹配，成语：{str(chengyu_list)}"

def model_jielong3(chengyu_list):
    # 清理文本
    for i in range(len(chengyu_list)):
        chengyu_list[i] = clean_up_text(chengyu_list[i])
    
    # 检查逆接龙规则：下一个词语的字尾接上一个词语的字头
    for i in range(len(chengyu_list) - 1):
        current_first_char = chengyu_list[i][0]  # 当前词语的第一个字
        next_last_char = chengyu_list[i + 1][-1]  # 下一个词语的最后一个字
        
        if current_first_char != next_last_char:
            return 0, f"❌ 不匹配，词语：【{str(chengyu_list[i])}】的第一个字 和词语：【{str(chengyu_list[i + 1])}】的最后一个字不一致"
    
    return 1, f"✅ 匹配，词语：{str(chengyu_list)}"

def model_jielong4(word_list):
    # 清理文本
    for i in range(len(word_list)):
        word_list[i] = clean_up_text(word_list[i])
    
    # 检查按位置取字的接龙规则
    for i in range(len(word_list) - 1):
        # 计算当前词应该取第几个字（从0开始计数）
        current_pos = i % len(word_list[i])
        # 计算下一个词应该取第几个字
        next_pos = (i + 1) % len(word_list[i + 1])
        
        # 获取对应位置的字符
        current_char = word_list[i][current_pos]
        next_char = word_list[i + 1][next_pos]
        
        if current_char != next_char:
            return 0, f"❌ 不匹配，词语：{str(word_list[i])}的第{current_pos + 1}个字和词语：{str(word_list[i + 1])}的第{next_pos + 1}个字不一致"
    
    return 1, f"✅ 匹配，词语：{str(word_list)}"


def word_structure(word_list, structure):
    # 清理词汇列表
    for i in range(len(word_list)):
        word_list[i] = clean_up_text(word_list[i])
    
    valid_words = []
    invalid_words = []
    
    # 定义各种格式的验证规则
    def validate_pattern(word, pattern):
        if len(word) != len(pattern):
            return False, f"长度不匹配：词汇长度 {len(word)}，结构长度 {len(pattern)}"
        
        chars = list(word)
        
        # 定义验证规则字典
        rules = {
            "ABA": lambda c: c[0] == c[2] and c[0] != c[1],
            "AAB": lambda c: c[0] == c[1] and c[0] != c[2],
            "ABB": lambda c: c[1] == c[2] and c[0] != c[1],
            "AABB": lambda c: c[0] == c[1] and c[2] == c[3] and c[0] != c[2],
            "ABAB": lambda c: c[0] == c[2] and c[1] == c[3] and c[0] != c[1],
            "AABC": lambda c: c[0] == c[1] and c[0] != c[2] and c[0] != c[3] and c[2] != c[3],
            "ABAC": lambda c: c[0] == c[2] and c[0] != c[1] and c[0] != c[3] and c[1] != c[3],
            "ABCC": lambda c: c[2] == c[3] and c[0] != c[2] and c[1] != c[2] and c[0] != c[1]
        }
        
        if pattern in rules:
            if rules[pattern](chars):
                return True, f"符合 {pattern} 格式"
            else:
                return False, f"不符合 {pattern} 格式"
        else:
            # 通用映射方法处理其他格式
            char_map = {}
            for i, (pattern_char, current_char) in enumerate(zip(pattern, chars)):
                if pattern_char in char_map:
                    if char_map[pattern_char] != current_char:
                        return False, f"位置 {i}: '{current_char}' 应该对应 '{pattern_char}' (已映射为 '{char_map[pattern_char]}')"
                else:
                    # 检查字符是否已被其他模式字符映射
                    for existing_pattern, existing_char in char_map.items():
                        if existing_char == current_char and existing_pattern != pattern_char:
                            return False, f"位置 {i}: '{current_char}' 已经被映射到模式 '{existing_pattern}'"
                    char_map[pattern_char] = current_char
            return True, f"符合 {pattern} 格式"
    
    # 验证每个词汇
    for word in word_list:
        is_valid, message = validate_pattern(word, structure)
        print(f"检查词汇：{word} - {message}")
        
        if is_valid:
            valid_words.append(word)
        else:
            invalid_words.append(word)
    
    # 返回最终结果
    if len(invalid_words) == 0:
        # 全部匹配
        return 1, f"✅ 匹配，所有词汇都符合 {structure} 格式：{valid_words}"
    elif len(valid_words) == 0:
        # 全部不匹配
        return 0, f"❌ 全部不匹配，所有词汇都不符合 {structure} 格式：{invalid_words}"
    else:
        # 部分匹配
        result_msg = f"❌ 部分匹配，{structure} 格式检查结果：\n"
        result_msg += f"  符合格式的词汇：{valid_words}\n"
        result_msg += f"  不符合格式的词汇：{invalid_words}"
        return 0, result_msg


##########回文结构##########
def has_palindrome(corresponding_parts):
    """
    判断每个对联是否为回文结构
    第一个字和最后一个字相同，第二个字和倒数第二个字相同，以此类推
    """
    import re
    
    item_results = []
    all_palindrome = True
    
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        # 去除空格和标点，只保留汉字
        clean_text = re.sub(r'[^\u4e00-\u9fff]', '', item.strip())
        char_count = len(clean_text)
        
        # 检查回文结构
        result = False
        if char_count > 0:
            result = True
            for j in range(char_count // 2):
                if clean_text[j] != clean_text[char_count - 1 - j]:
                    result = False
                    break
        
        if not result:
            all_palindrome = False
        
        item_results.append({
            'index': i,
            'text': clean_text,
            'char_count': char_count,
            'is_palindrome': result
        })
    
    # 构建详细信息
    if len(corresponding_parts) == 1:
        item = item_results[0]
        if item['char_count'] == 0:
            return 0, f"❌ 内容为空"
        elif item['is_palindrome']:
            return 1, f"✅ 回文结构：{item['text']}"
        else:
            return 0, f"❌ 非回文结构：{item['text']}"
    else:
        item_details = []
        for item in item_results:
            if item['char_count'] == 0:
                item_details.append(f"❌第{item['index']+1}项，内容为空")
            elif item['is_palindrome']:
                item_details.append(f"✅第{item['index']+1}项，回文：{item['text']}")
            else:
                item_details.append(f"❌第{item['index']+1}项，非回文：{item['text']}")
        
        if all_palindrome:
            return 1, f"✅ 全部为回文结构，{' '.join(item_details)}"
        else:
            return 0, f"❌ 存在非回文结构，{' '.join(item_details)}"


#######笔画统计的两个rule：总笔画、单字笔画#######
def stroke_count_total(corresponding_parts, target_total):
    """
    检查每个对应部分的总笔画数
    """
    try:
        import strokes
    except ImportError:
        return 0, "❌ 需要安装 strokes 库：pip install strokes"
    
    import re
    
    item_results = []
    all_correct = True
    
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        # 去除空格和标点，只保留汉字
        clean_text = re.sub(r'[^\u4e00-\u9fff]', '', item.strip())
        
        if len(clean_text) == 0:
            item_results.append({
                'index': i,
                'text': clean_text,
                'error': '内容为空'
            })
            all_correct = False
            continue
        
        # 获取每个字的笔画数
        char_strokes = []
        total_strokes = 0
        unknown_chars = []
        
        for char in clean_text:
            try:
                stroke_count = strokes.strokes(char)
                char_strokes.append((char, stroke_count))
                total_strokes += stroke_count
            except Exception as e:
                char_strokes.append((char, -1))
                unknown_chars.append(char)
        
        if unknown_chars:
            item_results.append({
                'index': i,
                'text': clean_text,
                'char_strokes': char_strokes,
                'error': f'无法识别字符的笔画数: {", ".join(unknown_chars)}',
                'correct': False
            })
            all_correct = False
            continue
        
        # 检查总笔画数
        correct = (total_strokes == target_total)
        
        item_results.append({
            'index': i,
            'text': clean_text,
            'char_strokes': char_strokes,
            'total_strokes': total_strokes,
            'expected_total': target_total,
            'correct': correct
        })
        
        if not correct:
            all_correct = False
    
    # 生成结果信息
    if len(corresponding_parts) == 1:
        item = item_results[0]
        
        if 'error' in item:
            return 0, f"❌ {item['error']}"
        elif item['correct']:
            stroke_details = [f"{char}({count}画)" for char, count in item['char_strokes']]
            return 1, f"✅ 总笔画数正确：{item['text']}，详情：{' '.join(stroke_details)}，总计{item['total_strokes']}画"
        else:
            stroke_details = [f"{char}({count}画)" for char, count in item['char_strokes']]
            return 0, f"❌ 期望{item['expected_total']}画，总笔画数错误：{item['text']}，详情：{' '.join(stroke_details)}，总共{item['total_strokes']}画"
    else:
        # 多项处理
        details = []
        for item in item_results:
            if 'error' in item:
                details.append(f"❌第{item['index']+1}项：{item['error']}")
            elif item['correct']:
                details.append(f"✅第{item['index']+1}项：{item['text']}({item['total_strokes']}画)")
            else:
                details.append(f"❌第{item['index']+1}项：{item['text']}(总共{item['total_strokes']}画)")
        
        if all_correct:
            return 1, f"✅ 全部总笔画数正确，{' '.join(details)}"
        else:
            return 0, f"❌ 期望{item['expected_total']}画，存在总笔画数错误，{' '.join(details)}"

def stroke_count_each(corresponding_parts, stroke_range):
    """
    检查每个对应部分中每个字的笔画数是否在指定范围内
    
    Args:
        corresponding_parts: 文本列表
        stroke_range: 笔画数范围，如[3,8]表示每个字的笔画数要在3-8画之间
        
    Returns:
        tuple: (结果码, 详细信息)
    """
    try:
        import strokes
    except ImportError:
        return 0, "❌ 需要安装 strokes 库：pip install strokes"
    
    import re
    
    if not isinstance(stroke_range, list) or len(stroke_range) != 2:
        return 0, "❌ 笔画范围格式错误，应为[最小值,最大值]"
    
    min_strokes, max_strokes = stroke_range
    
    item_results = []
    all_correct = True
    
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        # 去除空格和标点，只保留汉字
        clean_text = re.sub(r'[^\u4e00-\u9fff]', '', item.strip())
        
        if len(clean_text) == 0:
            item_results.append({
                'index': i,
                'text': clean_text,
                'reason': '内容为空',
                'correct': False
            })
            all_correct = False
            continue
        
        # 获取每个字的笔画数
        unknown_chars = []
        out_of_range_chars = []
        item_correct = True
        
        for char in clean_text:
            try:
                stroke_count = strokes.strokes(char)
                
                # 检查是否在范围内
                if not (min_strokes <= stroke_count <= max_strokes):
                    out_of_range_chars.append(f"'{char}'{stroke_count}画")
                    item_correct = False
                    
            except Exception as e:
                unknown_chars.append(char)
                item_correct = False
        
        # 生成这一项的结果
        if unknown_chars:
            item_results.append({
                'index': i,
                'text': clean_text,
                'reason': f'无法识别: {", ".join(unknown_chars)}',
                'correct': False
            })
            all_correct = False
        elif out_of_range_chars:
            item_results.append({
                'index': i,
                'text': clean_text,
                'reason': f'超出范围: {", ".join(out_of_range_chars)}',
                'correct': False
            })
            all_correct = False
        else:
            item_results.append({
                'index': i,
                'text': clean_text,
                'correct': True
            })
    
    # 生成结果信息
    if len(corresponding_parts) == 1:
        item = item_results[0]
        if item['correct']:
            return 1, f"✅ 检查通过：{item['text']}"
        else:
            return 0, f"❌ 检查失败：{item['text']} - {item['reason']}"
    else:
        # 多项处理 - 详细格式
        success_count = sum(1 for item in item_results if item['correct'])
        total_count = len(item_results)
        
        if all_correct:
            # 全部正确时的简洁显示
            success_texts = [item['text'] for item in item_results]
            result_text = f"✅ 检查全部通过 ({success_count}/{total_count}项)\n"
            result_text += "、".join(success_texts)
            return 1, result_text
        else:
            # 有错误时的详细显示
            details_lines = []
            details_lines.append(f"❌ 检查结果: {success_count}/{total_count}项通过")
            details_lines.append("")  # 空行分隔
            
            # 按状态分组显示
            success_items = [item for item in item_results if item['correct']]
            error_items = [item for item in item_results if not item['correct']]
            
            # 显示错误项 - 简化格式
            if error_items:
                details_lines.append("【错误项】")
                for item in error_items:
                    details_lines.append(f"第{item['index']+1}项: {item['text']} - {item['reason']}")
                
                if success_items:
                    details_lines.append("")  # 空行分隔
            
            # 显示成功项 - 用顿号连接
            if success_items:
                success_texts = [item['text'] for item in success_items]
                details_lines.append("【正确项】")
                details_lines.append("、".join(success_texts))
            
            return 0, "\n".join(details_lines)


def check_pinyin_order(corresponding_parts):
    """
    检查corresponding_parts列表是否按照拼音顺序排列
    """
    try:
        from pinyin_order import pinyin_sorted
    except ImportError:
        return 0, "❌ 需要安装 pinyin-order 库：pip install pinyin-order"
    
    import re
    
    if len(corresponding_parts) < 2:
        return 0, "❌ 需要至少2个项目才能判断顺序"
    
    # 清理每个项目，只保留汉字
    cleaned_parts = []
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        # 去除空格和标点，只保留汉字
        clean_text = re.sub(r'[^\u4e00-\u9fff]', '', item.strip())
        
        if len(clean_text) == 0:
            return 0, f"❌ 第{i+1}项内容为空或无汉字"
        
        cleaned_parts.append(clean_text)
    
    try:
        # 使用pinyin_sorted对整个列表排序
        sorted_parts = pinyin_sorted(cleaned_parts)
        
        # 检查原列表是否已经按拼音顺序排列
        is_ordered = cleaned_parts == sorted_parts
        
        if is_ordered:
            # 显示每项的首字符拼音信息
            items_display = "、".join(cleaned_parts)
            return 1, f"✅ 拼音顺序正确 ({len(cleaned_parts)}项): {items_display}"
        else:
            # 找出顺序错误的详细信息
            details_lines = []
            details_lines.append(f"❌ 拼音顺序错误")
            details_lines.append("")
            
            details_lines.append("【当前顺序】")
            for i, item in enumerate(cleaned_parts):
                details_lines.append(f"第{i+1}项: {item}")
            
            details_lines.append("")
            details_lines.append("【正确顺序】")
            for i, item in enumerate(sorted_parts):
                original_pos = cleaned_parts.index(item) + 1 if item in cleaned_parts else -1
                details_lines.append(f"第{i+1}项: {item} (原第{original_pos}项)")
            
            return 0, "\n".join(details_lines)
            
    except Exception as e:
        return 0, f"❌ 拼音处理错误: {str(e)}"
    

#####################汉字结构（左右结构上下结构等等）##################
def check_hanzi_structure_count(corresponding_parts, rule_params):
    """
    检查对应部分中每一项的某种汉字结构字符数量是否都在指定范围内
    rule_params: "结构类型:[min,max]" 格式，如 "左右结构:[5,5]"
    """
    try:
        from char_similar.const_dict import dict_char_struct
    except ImportError:
        return 0, "❌ 需要安装 char-similar 库：pip install char-similar"
    
    import re
    import ast
    
    # 解析规则参数
    try:
        if ':' not in rule_params:
            return 0, "❌ 规则格式错误，应为 '结构类型:[min,max]'"
        
        structure_type, range_str = rule_params.split(':', 1)
        range_list = ast.literal_eval(range_str)
        
        if not isinstance(range_list, list) or len(range_list) != 2:
            return 0, "❌ 范围格式错误，应为 [min,max]"
        
        min_count, max_count = range_list
        
    except Exception as e:
        return 0, f"❌ 参数解析错误: {str(e)}"
    
    # 完整的结构代码映射
    structure_map = {
        "独体字": ["0"],
        "左右结构": ["1"], 
        "上下结构": ["2"],
        "左中右结构": ["3"],
        "上中下结构": ["4"],
        "右上包围结构": ["5"],
        "左上包围结构": ["6"],
        "左下包围结构": ["7"],
        "上三包围结构": ["8"],
        "下三包围结构": ["9"],
        "左三包围结构": ["10"],
        "全包围结构": ["11"],
        "镶嵌结构": ["12"],
        "品字结构": ["13"],
        "半包围结构": ["5", "6", "7", "8", "9", "10"]
    }
    
    if structure_type not in structure_map:
        return 0, f"❌ 不支持的结构类型: {structure_type}。支持的类型: {list(structure_map.keys())}"
    
    target_codes = structure_map[structure_type]
    
    # 检查每一项是否都满足范围
    item_results = []
    all_passed = True
    
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        # 去除空格和标点，只保留汉字
        clean_text = re.sub(r'[^\u4e00-\u9fff]', '', item.strip())
        
        if len(clean_text) == 0:
            item_results.append({
                'index': i,
                'text': clean_text,
                'target_count': 0,
                'target_chars': [],
                'passed': min_count <= 0 <= max_count
            })
            if not (min_count <= 0 <= max_count):
                all_passed = False
            continue
        
        # 统计该项中的目标结构字符
        item_target_chars = []
        
        for char in clean_text:
            if char in dict_char_struct:
                char_code = dict_char_struct[char]
                if char_code in target_codes:
                    item_target_chars.append(char)
        
        # 检查该项是否满足范围
        item_count = len(item_target_chars)
        item_passed = min_count <= item_count <= max_count
        
        if not item_passed:
            all_passed = False
        
        item_results.append({
            'index': i,
            'text': clean_text,
            'target_count': item_count,
            'target_chars': item_target_chars,
            'passed': item_passed
        })
    
    # 生成结果信息
    if all_passed:
        if len(corresponding_parts) == 1:
            # 只有一项时
            item = item_results[0]
            if item['target_chars']:
                char_list = '、'.join(item['target_chars'])
                result_text = f"✅ {structure_type}字符数量正确: {item['target_count']}个 : {char_list}"
            else:
                result_text = f"✅ {structure_type}字符数量正确: {item['target_count']}个"
        else:
            # 多项时
            result_text = f"✅ 所有项{structure_type}字符数量都正确"
            
            # 显示每项的详情
            details = []
            for item in item_results:
                if item['target_chars']:
                    char_list = '、'.join(item['target_chars'])
                    details.append(f"第{item['index']+1}项: {item['target_count']}个 ({char_list})")
                else:
                    details.append(f"第{item['index']+1}项: {item['target_count']}个")
            
            if details:
                result_text += f"\n" + "\n".join(details)
        
        return 1, result_text
    else:
        # 有项目不满足要求
        if len(corresponding_parts) == 1:
            # 只有一项时
            item = item_results[0]
            if item['target_count'] == 0:
                result_text = f"❌ 未发现{structure_type}字符"
            else:
                if item['target_chars']:
                    char_list = '、'.join(item['target_chars'])
                    result_text = f"❌ {structure_type}字符数量不符合范围[{min_count},{max_count}]: {item['target_count']}个 : {char_list}"
                else:
                    result_text = f"❌ {structure_type}字符数量不符合范围[{min_count},{max_count}]: {item['target_count']}个"
        else:
            # 多项时
            details_lines = []
            details_lines.append(f"❌ {structure_type}字符数量不符合范围[{min_count},{max_count}]")
            
            # 显示失败的项
            failed_items = [item for item in item_results if not item['passed']]
            if failed_items:
                details_lines.append("【失败项】")
                for item in failed_items:
                    if item['target_chars']:
                        char_list = '、'.join(item['target_chars'])
                        details_lines.append(f"第{item['index']+1}项: 数量{item['target_count']} ({char_list})")
                    else:
                        details_lines.append(f"第{item['index']+1}项: 数量{item['target_count']}")
            
            # 显示通过的项
            passed_items = [item for item in item_results if item['passed']]
            if passed_items:
                details_lines.append("【通过项】")
                for item in passed_items:
                    if item['target_chars']:
                        char_list = '、'.join(item['target_chars'])
                        details_lines.append(f"第{item['index']+1}项: {item['target_count']}个 ({char_list})")
                    else:
                        details_lines.append(f"第{item['index']+1}项: {item['target_count']}个")
            
            result_text = "\n".join(details_lines)
        
        return 0, result_text

def get_structure_name(code):
    """根据结构代码获取结构名称"""
    code_to_name = {
        "0": "独体字",
        "1": "左右结构",
        "2": "上下结构", 
        "3": "左中右结构",
        "4": "上中下结构",
        "5": "右上包围结构",
        "6": "左上包围结构",
        "7": "左下包围结构",
        "8": "上左右包围结构",
        "9": "下三包围结构",
        "10": "上左下包围结构",
        "11": "全包围结构",
        "12": "镶嵌结构",
        "13": "品字结构"
    }


###############汉字部件###############
def check_component_count(corresponding_parts, rule_params):
    """
    检查对应部分中包含某种部件的字符数量是否在指定范围内
    rule_params: "部件:[min,max]" 格式，如 "氵:[3,8]"
    """
    try:
        from char_similar.const_dict import dict_char_component
    except ImportError:
        return 0, "❌ 需要安装 char-similar 库：pip install char-similar"
    
    import re
    import ast
    
    # 解析规则参数
    try:
        if ':' not in rule_params:
            return 0, "❌ 规则格式错误，应为 '部件:[min,max]'"
        
        target_component, range_str = rule_params.split(':', 1)
        range_list = ast.literal_eval(range_str)
        
        if not isinstance(range_list, list) or len(range_list) != 2:
            return 0, "❌ 范围格式错误，应为 [min,max]"
        
        min_count, max_count = range_list
        
    except Exception as e:
        return 0, f"❌ 参数解析错误: {str(e)}"
    
    # 检查每一项是否都满足范围
    item_results = []
    all_passed = True
    
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        # 去除空格和标点，只保留汉字
        clean_text = re.sub(r'[^\u4e00-\u9fff]', '', item.strip())
        
        if len(clean_text) == 0:
            item_results.append({
                'index': i,
                'text': clean_text,
                'target_count': 0,
                'target_chars': [],
                'passed': min_count <= 0 <= max_count
            })
            if not (min_count <= 0 <= max_count):
                all_passed = False
            continue
        
        # 统计该项中包含目标部件的字符
        item_target_chars = []
        
        for char in clean_text:
            if char in dict_char_component:
                char_component = dict_char_component[char]
                if char_component == target_component:  # 精确匹配部件
                    item_target_chars.append(char)
        
        # 检查该项是否满足范围
        item_count = len(item_target_chars)
        item_passed = min_count <= item_count <= max_count
        
        if not item_passed:
            all_passed = False
        
        item_results.append({
            'index': i,
            'text': clean_text,
            'target_count': item_count,
            'target_chars': item_target_chars,
            'passed': item_passed
        })
    
    # 生成结果信息
    if all_passed:
        if len(corresponding_parts) == 1:
            # 只有一项时
            item = item_results[0]
            if item['target_chars']:
                char_list = '、'.join(item['target_chars'])
                result_text = f"✅ 部件'{target_component}'字符数量正确: {item['target_count']}个 : {char_list}"
            else:
                result_text = f"✅ 部件'{target_component}'字符数量正确: {item['target_count']}个"
        else:
            # 多项时
            result_text = f"✅ 所有项部件'{target_component}'字符数量都正确"
            
            # 显示每项的详情
            details = []
            for item in item_results:
                if item['target_chars']:
                    char_list = '、'.join(item['target_chars'])
                    details.append(f"第{item['index']+1}项: {item['target_count']}个 ({char_list})")
                else:
                    details.append(f"第{item['index']+1}项: {item['target_count']}个")
            
            if details:
                result_text += f"\n" + "\n".join(details)
        
        return 1, result_text
    else:
        # 有项目不满足要求
        if len(corresponding_parts) == 1:
            # 只有一项时
            item = item_results[0]
            if item['target_count'] == 0:
                result_text = f"❌ 未发现部件'{target_component}'字符"
            else:
                if item['target_chars']:
                    char_list = '、'.join(item['target_chars'])
                    result_text = f"❌ 部件'{target_component}'字符数量不符合范围[{min_count},{max_count}]: {item['target_count']}个 : {char_list}"
                else:
                    result_text = f"❌ 部件'{target_component}'字符数量不符合范围[{min_count},{max_count}]: {item['target_count']}个"
        else:
            # 多项时
            details_lines = []
            details_lines.append(f"❌ 部件'{target_component}'字符数量不符合范围[{min_count},{max_count}]")
            
            # 显示失败的项
            failed_items = [item for item in item_results if not item['passed']]
            if failed_items:
                details_lines.append("【失败项】")
                for item in failed_items:
                    if item['target_chars']:
                        char_list = '、'.join(item['target_chars'])
                        details_lines.append(f"第{item['index']+1}项: 数量{item['target_count']} ({char_list})")
                    else:
                        details_lines.append(f"第{item['index']+1}项: 数量{item['target_count']}")
            
            # 显示通过的项
            passed_items = [item for item in item_results if item['passed']]
            if passed_items:
                details_lines.append("【通过项】")
                for item in passed_items:
                    if item['target_chars']:
                        char_list = '、'.join(item['target_chars'])
                        details_lines.append(f"第{item['index']+1}项: {item['target_count']}个 ({char_list})")
                    else:
                        details_lines.append(f"第{item['index']+1}项: {item['target_count']}个")
            
            result_text = "\n".join(details_lines)
        
        return 0, result_text
    

###########尾字声调#########
def check_hanzi_tone_position(corresponding_parts, rule_params, position="end"):
    """
    检查对应部分中每一项指定位置字符的声调是否符合要求
    
    Args:
        corresponding_parts: 文本列表
        rule_params: "声调" 格式，如 "1" 表示一声
        position: "start" 或 "end"，表示检查首字还是尾字
        
    Returns:
        tuple: (结果码, 详细信息)
    """
    try:
        from char_similar.const_dict import dict_char_pinyin
    except ImportError:
        return 0, "❌ 需要安装 char-similar 库：pip install char-similar"
    
    import re
    
    # 解析规则参数
    target_tone = rule_params.strip()
    
    if target_tone not in ["1", "2", "3", "4"]:
        return 0, f"❌ 不支持的声调: {target_tone}。支持的声调: 1, 2, 3, 4"
    
    def extract_tone(pinyin_data):
        """从拼音数据中提取声调"""
        if isinstance(pinyin_data, list) and len(pinyin_data) >= 4:
            tone = pinyin_data[3]
            return tone if tone.isdigit() else None
        return None
    
    def extract_full_pinyin(pinyin_data):
        """提取完整拼音"""
        if isinstance(pinyin_data, list) and len(pinyin_data) >= 1:
            return pinyin_data[0]
        return None
    
    def format_tone_display(tone):
        """格式化声调显示"""
        if tone is None:
            return "轻声"
        else:
            return f"{tone}声"
    
    # 设置位置相关的参数
    pos_name = "首字" if position == "start" else "尾字"
    char_key = "first_char" if position == "start" else "last_char"
    
    # 检查每一项的指定位置字符声调
    item_results = []
    all_passed = True
    
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        # 去除空格和标点，只保留汉字
        clean_text = re.sub(r'[^\u4e00-\u9fff]', '', item.strip())
        
        if len(clean_text) == 0:
            item_results.append({
                'index': i,
                'text': clean_text,
                char_key: None,
                'tone': None,
                'pinyin': None,
                'passed': False,
                'reason': '内容为空'
            })
            all_passed = False
            continue
        
        # 获取指定位置的字符
        target_char = clean_text[0] if position == "start" else clean_text[-1]
        
        if target_char in dict_char_pinyin:
            pinyin_data = dict_char_pinyin[target_char]
            detected_tone = extract_tone(pinyin_data)
            full_pinyin = extract_full_pinyin(pinyin_data)
            
            item_passed = detected_tone == target_tone
            
            if not item_passed:
                all_passed = False
            
            item_results.append({
                'index': i,
                'text': clean_text,
                char_key: target_char,
                'tone': detected_tone,
                'pinyin': full_pinyin,
                'passed': item_passed,
                'reason': f'声调为{format_tone_display(detected_tone)}，不是{target_tone}声' if not item_passed else ''
            })
        else:
            item_results.append({
                'index': i,
                'text': clean_text,
                char_key: target_char,
                'tone': None,
                'pinyin': None,
                'passed': False,
                'reason': '未找到拼音数据'
            })
            all_passed = False
    
    # 生成结果信息
    if all_passed:
        if len(corresponding_parts) == 1:
            # 只有一项时
            item = item_results[0]
            result_text = f"✅ {pos_name}声调正确: '{item[char_key]}'({item['pinyin']}) 为{target_tone}声"
        else:
            # 多项时
            result_text = f"✅ 所有项{pos_name}都是{target_tone}声"
            
            # 显示每项的详情
            details = []
            for item in item_results:
                if item[char_key]:
                    tone_display = format_tone_display(item['tone'])
                    details.append(f"第{item['index']+1}项: '{item[char_key]}'({item['pinyin']}) {tone_display}")
                else:
                    details.append(f"第{item['index']+1}项: 无{pos_name}")
            
            if details:
                result_text += f"\n" + "\n".join(details)
        
        return 1, result_text
    else:
        # 有项目不满足要求
        if len(corresponding_parts) == 1:
            # 只有一项时
            item = item_results[0]
            if item['tone'] is not None:
                result_text = f"❌ {pos_name}声调不正确: '{item[char_key]}'({item['pinyin']}) 为{format_tone_display(item['tone'])}，要求{target_tone}声"
            else:
                result_text = f"❌ {pos_name}声调检测失败: '{item[char_key]}' - {item['reason']}"
        else:
            # 多项时
            details_lines = []
            details_lines.append(f"❌ {pos_name}声调不符合{target_tone}声要求")
            
            # 显示失败的项
            failed_items = [item for item in item_results if not item['passed']]
            if failed_items:
                details_lines.append("【失败项】")
                for item in failed_items:
                    if item['pinyin']:  # 有拼音数据
                        tone_display = format_tone_display(item['tone'])
                        details_lines.append(f"第{item['index']+1}项: '{item[char_key]}'({item['pinyin']}) {tone_display}")
                    else:  # 没有拼音数据
                        details_lines.append(f"第{item['index']+1}项: '{item[char_key]}' - {item['reason']}")
            
            # 显示通过的项
            passed_items = [item for item in item_results if item['passed']]
            if passed_items:
                details_lines.append("【通过项】")
                for item in passed_items:
                    tone_display = format_tone_display(item['tone'])
                    details_lines.append(f"第{item['index']+1}项: '{item[char_key]}'({item['pinyin']}) {tone_display}")
            
            result_text = "\n".join(details_lines)
        
        return 0, result_text

def check_end_hanzi_tone(corresponding_parts, rule_params):
    """检查尾字声调"""
    return check_hanzi_tone_position(corresponding_parts, rule_params, position="end")

def check_start_hanzi_tone(corresponding_parts, rule_params):
    """检查首字声调"""
    return check_hanzi_tone_position(corresponding_parts, rule_params, position="start")

if __name__ == "__main__":
    # check_hanzi_structure_count("aa","左中右结构:[6,6]")
    word_structure(["你看你吗"],"ABAC")