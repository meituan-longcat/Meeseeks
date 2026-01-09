import re
from .utils import txt_to_json_og
from .rule_utils.keywords import model_keywords, model_non_keywords, model_keywords_any, model_word_freq, model_non_word_freq, model_word_freq_any,model_startword
from .rule_utils.cjk_eng_ratio import chinese_english_ratio, count_mixed_chinese_english_words, korean_english_ratio, count_mixed_korean_english_words, japanese_english_ratio, count_mixed_japanese_english_words
from .rule_utils.len_and_numbers import model_each_length, model_total_length, model_item_count, model_repeat_each, model_no_word_repeat, model_no_word_eachrepeat, model_non_very_similar, model_each_no_word_repeat
from .rule_utils.regex import model_non_regex, model_regex
from .rule_utils.end_start_with import model_no_end_with_punctuation, model_endswith_each, model_startswith_each, endswithany_each
from .rule_utils.rhyme_chn import  yayun, pingze, lvshi_yayun, fanti, has_heteronym, first_line_rhyme, chinese_odd_lines_no_rhyme, jin_tui_yun, lu_lu_yun
from .rule_utils.rhyme_jpn import jpn_yayun, jpn_waka_yayun, jpn_shigin_jielong, jpn_kana_type
from .rule_utils.rhyme_kor import kor_yayun, korean_lvshi_yayun
from .rule_utils.schema import model_schema, json_schema, list_schema
from .rule_utils.special_kor import has_double_consonants, has_korean_abbreviation, each_has_double_consonants
from .rule_utils.special_jp import jpn_mixed_ratio, has_small_kana, has_furigana_pattern, has_kanji_okurigana_pattern, jpn_starts_with_kana_row, has_honorific_prefix_each,  has_dakuten_count,has_handakuten_count, has_dakuten_count_range, has_handakuten_count_range, has_dakuten_by_type, has_handakuten_by_type, has_handakuten_minimum
from .rule_utils.special_esp import has_complete_questions , has_complete_exclamations , has_spanish_word_count ,  has_spanish_accent_count , has_correct_compound_hyphen_usage
from .rule_utils.special_chn import check_start_hanzi_tone, check_end_hanzi_tone, model_jielong, model_jielong2, model_jielong3, model_jielong4, word_structure, has_palindrome, stroke_count_total, stroke_count_each, check_pinyin_order, check_hanzi_structure_count, check_component_count
def rule_based_evaluate(item, rule, model_response):
    try:
        print("rule now:",rule)
        # print("item now:",item)
        # 0. 是否出现所有["关键词", "关键词2", ...]
        if rule.startswith("keyword"):
            return model_keywords(txt_to_json_og(rule), model_response)
        
        # 1. 是否出现["关键词", "关键词2", ...]中的任意n个，比如: model_any_keywords2的意思是必须出现两个关键词
        if rule.startswith("any_keywords"):
            match = re.search(r'any_keywords(\d+)', rule)  # 匹配'any_keywords'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_keywords_any(num, txt_to_json_og(rule), model_response)
        
        # 2. 是否不出现["关键词", "关键词2", ...]
        elif rule.startswith("non_keyword") or rule.startswith("non_keyword"):
            return model_non_keywords(txt_to_json_og(rule), model_response)
        
        # 3. 统计["xxxx", "ccccc", "aaaaa", ...]每个信息的长度是否满足rule的要求
        elif rule.startswith("each_length"):
            return model_each_length(txt_to_json_og(rule), model_response)

        # 4. 统计["xxxx", "ccccc", "aaaaa", ...]的总长度是否满足rule的要求
        elif rule.startswith("total_length"):
            return model_total_length(txt_to_json_og(rule), model_response)
        
        # 5. 统计len(["xxxx", "ccccc", "aaaaa", ...])，看提供数量是否满足rule的要求
        elif rule.startswith("item_count"):
            return model_item_count(txt_to_json_og(rule), model_response)
        
        # 6. 判断是否不存在此正则表达式匹配
        elif rule.startswith("non_regex"):
            return model_non_regex(rule, model_response)
        
        # 6.1. 判断是否满足此正则表达式匹配
        elif rule.startswith("regex"):
            return model_regex(rule, model_response)
        
        # 7. 统计["xxxx", "ccccc", "aaaaa", ...]看是否有element是重复的
        elif rule.startswith("repeat_each"):
            return model_repeat_each(model_response)
        
        # 8. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以rule[0]指定的信息结尾
        elif rule.startswith("endswith_each"):
            return model_endswith_each(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("endswithany_each"):
            return endswithany_each(txt_to_json_og(rule), model_response)

        # 9. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以rule[0]指定的信息开头
        elif rule.startswith("startswith_each"):
            return model_startswith_each(txt_to_json_og(rule), model_response)
        
        # 11. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否满足押韵，押韵比例是否超过60%
        elif rule.startswith("yayun"):
            return yayun(model_response)
        
        elif rule.startswith("jpn_yayun"):
            return jpn_yayun(model_response)
        
        elif rule.startswith("kor_yayun"):
            return kor_yayun(model_response)
        
        # 12. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以标点结尾
        elif rule.startswith("no_end_with_punctuation"):
            return model_no_end_with_punctuation(model_response)
        
        # 13. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否满足中英比例
        elif rule.startswith("chinese_english_ratio"):
            return chinese_english_ratio(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("korean_english_ratio"):
            return korean_english_ratio(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("japanese_english_ratio"):
            return japanese_english_ratio(txt_to_json_og(rule), model_response)
        
        # 14. 判断是否是xxx schema
        elif rule.startswith("SCHEMA"):
            return model_schema(item, rule.split(":")[1], model_response)

        # 15. 判断平仄情况
        elif rule.startswith("pingze"):
            return pingze(model_response)
        
        # 16. 所有element内没有任何文字是一样的
        elif rule.startswith("no_word_repeat"):
            return model_no_word_repeat(model_response)
        
        elif rule.startswith("no_word_eachrepeat"):
            return model_no_word_eachrepeat(model_response)
        
        # 是否有75%以上的字有重复
        elif rule.startswith("non_very_similar"):
            return model_non_very_similar(model_response)
        
        elif rule.startswith("lvshi_yayun"):
            return lvshi_yayun(model_response)
        
        elif rule.startswith("count_mixed_chinese_english_words"):
            return count_mixed_chinese_english_words(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("count_mixed_korean_english_words"):
            return count_mixed_korean_english_words(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("count_mixed_japanese_english_words"):
            return count_mixed_japanese_english_words(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("word_freq"):
            match = re.search(r'word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_word_freq(num, txt_to_json_og(rule), model_response)
        
        elif rule.startswith("any_word_freq"):
            match = re.search(r'any_word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_word_freq_any(num, txt_to_json_og(rule), model_response)
        

        elif rule.startswith("double_consonants"):
            match = re.search(r'double_consonants:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_double_consonants(model_response, num)

        elif rule.startswith("each_has_double_consonants"):
            match = re.search(r'each_has_double_consonants:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return each_has_double_consonants(model_response, num)

        elif rule.startswith("has_heteronym"):
            match = re.search(r'has_heteronym:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_heteronym(model_response, num)
        
        elif rule.startswith("non_word_freq"):
            match = re.search(r'non_word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_non_word_freq(num, txt_to_json_og(rule), model_response)

        elif rule.startswith("fanti"):
            return fanti(model_response)
        
        elif rule.startswith("non_special_notation"):
            _, _, notation = rule.partition(":")
            for i in model_response:
                if notation in i:
                    return 0, f"{notation} detected in model response: {i}"
            return 1, f"{notation} not detected in any of model responses"
        
        elif rule.startswith("notation_freq"):
            # print(rule)
            match = re.search(r'notation_freq(\d+)', rule)  # 匹配'notation_freq'后面的数字
            
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            # print("detected_nums: ", num)
            notations = txt_to_json_og(rule)
            
            # 检查每个model_response中的内容
            for response_idx, response in enumerate(model_response):
                # 检查每个notation是否都出现了num次
                all_correct = True
                actual_counts = []
                
                for notation in notations:
                    actual_count = response.count(notation)
                    actual_counts.append(actual_count)
                    if actual_count != num:
                        all_correct = False
                
                if not all_correct:
                    # 构建详细的错误信息
                    details = []
                    for i, notation in enumerate(notations):
                        details.append(f"{notation}: {actual_counts[i]}次")
                    return 0, f"❌ 第{response_idx+1}个回答中，{notations}中每个符号理应出现{num}次，实际出现次数: [{', '.join(details)}]"
            
            # 所有回答都满足条件
            return 1, f"✅ 所有回答中每个符号都出现{num}次"


        elif rule.startswith("has_korean_abbreviation"):
            _, _, abbreviation = rule.partition(":")
            return has_korean_abbreviation(model_response, abbreviation)
            
        elif rule.startswith("jpn_mixed_ratio"):
            ratio = txt_to_json_og(rule)
            hiragana_ratio = ratio[0]
            katakana_ratio = ratio[1]
            kanji_ratio = ratio[2]

            return jpn_mixed_ratio(model_response, hiragana_ratio, katakana_ratio, kanji_ratio)
    
        elif rule.startswith("has_small_kana"):
            match = re.search(r'has_small_kana(\d+)', rule) 
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_small_kana(model_response, num)
        
        elif rule.startswith("has_furigana_pattern"):
            match = re.search(r'has_furigana_pattern:(\d+)', rule) 
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_furigana_pattern(model_response, num)
        
        elif rule.startswith("has_kanji_okurigana_pattern"):
            match = re.search(r'has_kanji_okurigana_pattern:(\d+)', rule) 
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_kanji_okurigana_pattern(model_response, num)
        
        
        
        #接龙是否以某个关键词开始
        elif rule.startswith("startword"):
            return model_startword(txt_to_json_og(rule), model_response)
        
        

        elif rule.startswith("has_complete_questions"):
            match = re.search(r'has_complete_questions:(\d+)', rule) 
            if match:
                times = int(match.group(1))  # 转换为整数
            else:
                times = 1  # 默认值为1
            return has_complete_questions(model_response, times)

        elif rule.startswith("has_complete_exclamations"):
            match = re.search(r'has_complete_exclamations:(\d+)', rule) 
            if match:
                times = int(match.group(1))  # 转换为整数
            else:
                times = 1  # 默认值为1
            return has_complete_exclamations(model_response, times)
        
        elif rule.startswith("has_spanish_word_count"):
            # 解析范围格式，例如：has_spanish_word_count:[61.2,74.8]
            match = re.search(r'has_spanish_word_count:\[([0-9.]+),([0-9.]+)\]', rule)
            if match:
                min_count = int(float(match.group(1)))  # 转换为整数
                max_count = int(float(match.group(2)))  # 转换为整数
            else:
                min_count = 1  # 默认最小值
                max_count = 100  # 默认最大值
            return has_spanish_word_count(model_response, min_count, max_count)

        elif rule.startswith("has_spanish_accent_count"):
            # 解析数量格式，例如：has_spanish_accent_count:5
            match = re.search(r'has_spanish_accent_count:(\d+)', rule)
            if match:
                required_count = int(match.group(1))
            else:
                required_count = 1  # 默认最小值
            return has_spanish_accent_count(model_response, required_count)

        elif rule.startswith("has_correct_compound_hyphen_usage"):
            # 解析允许错误数量格式，例如：has_correct_compound_hyphen_usage:0
            match = re.search(r'has_correct_compound_hyphen_usage:(\d+)', rule)
            if match:
                max_allowed_errors = int(match.group(1))
            else:
                max_allowed_errors = 0  # 默认不允许任何错误
            return has_correct_compound_hyphen_usage(model_response, max_allowed_errors)
        
        elif rule.startswith("jpn_starts_with_kana_row"):
            # 解析五十音行格式，例如：jpn_starts_with_kana_row:あ行
            match = re.search(r'jpn_starts_with_kana_row:(.+)', rule)
            if match:
                kana_row = match.group(1)
            else:
                return 0, "❌ 规则格式错误"
            return jpn_starts_with_kana_row(model_response, kana_row)

        elif rule.startswith("has_honorific_prefix_each"):
            return has_honorific_prefix_each(model_response)
        
        elif rule.startswith("start_hanzi_tone"):
            match = re.search(r'start_hanzi_tone:(\d+)', rule)
            if match:
                tone = match.group(1)  # 获取声调参数
            else:
                return 0, "❌ 规则格式错误，应为 'start_hanzi_tone:数字'"

            # 确保 model_response 是列表格式
            if isinstance(model_response, str):
                model_response_list = [model_response]
            else:
                model_response_list = model_response

            return check_start_hanzi_tone(model_response_list, tone)

        elif rule.startswith("end_hanzi_tone"):
            match = re.search(r'end_hanzi_tone:(\d+)', rule)
            if match:
                tone = match.group(1)  # 获取声调参数
            else:
                return 0, "❌ 规则格式错误，应为 'end_hanzi_tone:数字'"

            # 确保 model_response 是列表格式
            if isinstance(model_response, str):
                model_response_list = [model_response]
            else:
                model_response_list = model_response

            return check_end_hanzi_tone(model_response_list, tone)

        elif rule.startswith("has_dakuten_count"):
            match = re.search(r'has_dakuten_count:(\d+)', rule)
            if match:
                num = int(match.group(1))  # 转换为整数返回
            else:
                num = 1  # 默认值为1
            return has_dakuten_count(model_response, num)

        elif rule.startswith("has_handakuten_count"):
            match = re.search(r'has_handakuten_count:(\d+)', rule)
            if match:
                num = int(match.group(1))  # 转换为整数返回
            else:
                num = 1  # 默认值为1
            return has_handakuten_count(model_response, num)

        # special_chn 模块的其他规则
        # 注意：必须先匹配更具体的规则（jielong2、jielong3、jielong4），再匹配通用规则（jielong）
        elif rule.startswith("jielong4"):
            return model_jielong4(model_response)
        
        elif rule.startswith("jielong3"):
            return model_jielong3(model_response)
        
        elif rule.startswith("jielong2"):
            return model_jielong2(model_response)
        
        elif rule.startswith("jielong"):
            return model_jielong(model_response)
        
        elif rule.startswith("word_structure"):
            # 提取结构字符串，格式: word_structure:ABAC
            match = re.search(r'word_structure:(.+)', rule)
            if match:
                structure = match.group(1).strip()
            else:
                return 0, "❌ 规则格式错误，应为 'word_structure:XXXX'"
            return word_structure(model_response, structure)
        
        elif rule.startswith("has_palindrome"):
            return has_palindrome(model_response)
        
        elif rule.startswith("stroke_count_total"):
            # 提取总笔画数，格式: stroke_count_total:100
            match = re.search(r'stroke_count_total:(\d+)', rule)
            if match:
                target_total = int(match.group(1))
            else:
                return 0, "❌ 规则格式错误，应为 'stroke_count_total:100'"
            return stroke_count_total(model_response, target_total)
        
        elif rule.startswith("stroke_count_each"):
            stroke_range = txt_to_json_og(rule)
            return stroke_count_each(model_response, stroke_range)
        
        elif rule.startswith("check_pinyin_order"):
            return check_pinyin_order(model_response)
        
        elif rule.startswith("hanzi_structure"):
            rule_params = rule
            return check_hanzi_structure_count(model_response, rule_params)
        
        elif rule.startswith("hanzi_component"):
            # 提取部件和范围，格式: hanzi_component部件:[min,max]，如 hanzi_component日:[7,10000]
            match = re.search(r'hanzi_component(.+)', rule)
            if match:
                rule_params = match.group(1)  # 提取 "日:[7,10000]"
            else:
                return 0, "❌ 规则格式错误，应为 'hanzi_component部件:[min,max]'"
            return check_component_count(model_response, rule_params)

        # rhyme_chn 模块的其他规则
        elif rule.startswith("first_line_rhyme"):
            match = re.search(r'first_line_rhyme:(.+)', rule)
            if match:
                requirement = match.group(1)
            else:
                requirement = "入韵"
            return first_line_rhyme(model_response, requirement)
        
        elif rule.startswith("chinese_odd_lines_no_rhyme"):
            return chinese_odd_lines_no_rhyme(model_response)
        
        elif rule.startswith("jin_tui_yun"):
            return jin_tui_yun(model_response)
        
        elif rule.startswith("lu_lu_yun"):
            return lu_lu_yun(model_response)

        # rhyme_jpn 模块的其他规则
        elif rule.startswith("jpn_waka_yayun"):
            return jpn_waka_yayun(model_response)
        
        elif rule.startswith("jpn_shigin_jielong"):
            return jpn_shigin_jielong(model_response)
        
        elif rule.startswith("jpn_kana_type"):
            return jpn_kana_type(model_response)

        # rhyme_kor 模块的其他规则
        elif rule.startswith("korean_lvshi_yayun"):
            return korean_lvshi_yayun(model_response)

        # len_and_numbers 模块的其他规则
        elif rule.startswith("each_no_word_repeat"):
            return model_each_no_word_repeat(model_response)

        # special_jp 模块的其他规则
        elif rule.startswith("has_dakuten_count_range"):
            match = re.search(r'has_dakuten_count_range:(\d+),(\d+)', rule)
            if match:
                min_num = int(match.group(1))
                max_num = int(match.group(2))
            else:
                return 0, "❌ 规则格式错误，应为 'has_dakuten_count_range:最小值,最大值'"
            return has_dakuten_count_range(model_response, min_num, max_num)
        
        elif rule.startswith("has_handakuten_count_range"):
            match = re.search(r'has_handakuten_count_range:(\d+),(\d+)', rule)
            if match:
                min_num = int(match.group(1))
                max_num = int(match.group(2))
            else:
                return 0, "❌ 规则格式错误，应为 'has_handakuten_count_range:最小值,最大值'"
            return has_handakuten_count_range(model_response, min_num, max_num)
        
        elif rule.startswith("has_dakuten_by_type"):
            match = re.search(r'has_dakuten_by_type:(\w+):(\d+)', rule)
            if match:
                dakuten_type = match.group(1)
                num = int(match.group(2))
            else:
                return 0, "❌ 规则格式错误，应为 'has_dakuten_by_type:类型:数量'"
            return has_dakuten_by_type(model_response, dakuten_type, num)
        
        elif rule.startswith("has_handakuten_by_type"):
            match = re.search(r'has_handakuten_by_type:(\w+):(\d+)', rule)
            if match:
                handakuten_type = match.group(1)
                num = int(match.group(2))
            else:
                return 0, "❌ 规则格式错误，应为 'has_handakuten_by_type:类型:数量'"
            return has_handakuten_by_type(model_response, handakuten_type, num)
        
        elif rule.startswith("has_handakuten_minimum"):
            match = re.search(r'has_handakuten_minimum:(\d+)', rule)
            if match:
                min_num = int(match.group(1))
            else:
                return 0, "❌ 规则格式错误，应为 'has_handakuten_minimum:最小数量'"
            return has_handakuten_minimum(model_response, min_num)

        # schema 模块的其他规则
        elif rule.startswith("json_schema"):
            return json_schema(item, model_response)
        
        elif rule.startswith("list_schema"):
            return list_schema(model_response)

        else:
            # 未找到匹配的规则，返回详细的错误信息
            error_msg = f"❌ 未识别的规则: '{rule}'\n"
            print(f"\n{error_msg}\n")
            return 0, error_msg
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"❌ 规则评估异常\n"
        error_msg += f"规则: {rule}\n"
        error_msg += f"错误类型: {type(e).__name__}\n"
        error_msg += f"错误信息: {str(e)}\n"
        error_msg += f"详细堆栈:\n{error_details}"
        print(f"\n{error_msg}\n")
        return 0, error_msg