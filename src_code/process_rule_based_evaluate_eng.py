import re
import ast
from .utils_eng import txt_to_json_og
from .rule_utils_eng.keywords import model_keywords, model_non_keywords, model_keywords_any, model_word_freq, each_word_freq, model_non_word_freq, model_non_very_similar
from .rule_utils_eng.word_count import model_each_length, model_total_length, arabic_each_length, portuguese_each_length, portuguese_total_length,  arabic_total_length, count_chinese_words, mixed_language_each_length,russian_each_length,russian_total_length,french_each_length,french_total_length,spanish_each_length, spanish_total_length,indonesian_each_length,indonesian_total_length,indonesian_each_length,indonesian_total_length,german_each_length, german_total_length
from .rule_utils_eng.item_count import model_item_count
from .rule_utils_eng.detect_repeat_for_space_split_language import model_repeat_each, model_no_word_repeat, model_no_char_repeat
from .rule_utils_eng.regex import model_non_regex, model_regex
from .rule_utils_eng.end_start_with import model_no_end_with_punctuation, model_endswith_each, model_startswith_each
from .rule_utils_eng.yayun import model_jielong, yayun, portuguese_yayun, arabic_yayun, german_yayun, spanish_yayun, indonesian_yayun, russian_yayun, french_yayun
from .rule_utils_eng.schema import model_schema
from .rule_utils_eng.special_eng import count_cap_num, count_low_num, compound_word_num, no_character_repeat, character_freq
from .rule_utils_eng.special_por import has_nasal_vowel,has_acute_accent,each_has_acute_accent,has_circumflex_accent,each_has_circumflex_accent,portuguese_double_negation,portuguese_date_format,portuguese_number_spelling,portuguese_starts_with_nao,portuguese_ordinal_abbreviation,has_nasal_and_cedilla_words,portuguese_address_abbreviation,portuguese_euro_format,has_cedilla_words
from .rule_utils_eng.special_ara import arabic_dual_noun_total,arabic_dual_noun_each,athlete_masc_plural_total,athlete_masc_plural_each,arabic_definite_article_total,arabic_definite_article_each,ar_independent_pronoun_total,ar_independent_pronoun_each,arabic_present_third_masc_verb_total,arabic_present_third_masc_verb_each,arabic_broken_plurals_total,arabic_broken_plurals_each,ar_repeat_each,check_ar_feminine_noun_forms,arabic_idafa_structure_total,arabic_idafa_structure_each,arabic_gender_ratio_total,arabic_gender_ratio_each,arabic_english_ratio,ar_no_word_repeat
from .rule_utils_eng.special_fre import french_h_word_count,french_h_ratio_total,french_h_ratio_each,french_accent_count_each,french_circumflex_total,french_circumflex_each,  french_diaeresis_total, french_diaeresis_each,french_rhyme_pattern,french_cedilla_each,french_cedilla_total,contains_french_seven_digit_number,is_vigesimal_number,check_pronominal_verbs,check_partitive_articles,check_passe_compose_auxiliary,check_adverbial_pronoun_ratio,check_ne_usage_from_rule,check_french_punctuation_from_rule,check_special_notations,check_adverbial_y_count
from .rule_utils_eng.special_esp import has_complete_questions , has_complete_exclamations , has_spanish_word_count ,  has_spanish_accent_count , has_correct_compound_hyphen_usage ,  has_correct_spanish_date_format ,  has_spanish_abbreviation_count , has_correct_abbreviation_format_only , has_correct_spanish_number_format , has_correct_spanish_currency_format , has_correct_spanish_phone_format ,has_correct_spanish_question_accents , has_correct_spanish_date_names_case , has_correct_spanish_address_format , total_has_complete_questions , has_spanish_ningun_sentences, has_correct_spanish_ningun_agreement , has_correct_spanish_ordinal_format , has_correct_spanish_time_articles, has_correct_total_double_negatives, has_total_definite_article_noun_combinations , has_correct_subject_omission_with_verb_conjugation , has_definite_article_noun_combinations , has_correct_spanish_article_gender_agreement , has_spanish_keywords_with_articles
from .rule_utils_eng.special_ru import  rus_stress_homonym_usage, detect_russian_evaluative_nouns_contextual, detect_russian_time_expression_4th_case, detect_russian_time_expression_6th_case, detect_russian_single_meter, detect_russian_singular_plural_semantic_pairs, detect_russian_multiple_plural_forms_enhanced, check_russian_derived_words, check_russian_gender_agreement, check_russian_participle_usage,check_keyword_inflections_each, check_hyphenated_words_count,check_russian_verb_temporal_relation,russian_adjective_type_count,russian_english_ratio
from .rule_utils_eng.special_ind import check_indonesian_loanwords, check_indonesian_plurals,check_indonesian_negation_keyword,check_indonesian_abbreviations,check_se_usage,check_active_voice,check_passive_voice,check_exact_colloquial_count,check_formal_honorifics,check_polite_imperatives,check_si_usage,check_sang_usage,check_fronted_emphasis,check_indonesian_loanwords_each
from .rule_utils_eng.german_conjunctions import check_conjunctions_per_sentence, check_conjunctions_order
from .rule_utils_eng.german_profession_order import order_profession1_check, order_profession2_check 
from rule_utils_eng.german_numbers_length import check_number_length
from rule_utils_eng.german_numbers_parity import check_number_parity
from rule_utils_eng.german_numbers_monotonicity import check_number_monotonicity
from rule_utils_eng.german_words_case import check_words_case
from rule_utils_eng.german_text_diminutive_words import check_text_diminutive_words
from rule_utils_eng.german_imperative_sentence import check_imperative_sentence, check_formal_imperative_sentence, check_informal_imperative_sentence, check_sentence_length_monotonicity
from rule_utils_eng.german_declarative_sentence import german_total_sentences, check_declarative_sentence_modal_verbs, check_declarative_sentence_length_monotonicity
from rule_utils_eng.german_clause import check_three_conjunctions, german_clause_conjunction, german_clause_verb
from rule_utils_eng.german_artical import german_article_count, german_article_der, german_article_das, german_article_die, check_three_articles
from rule_utils_eng.german_modal_verbs import check_modal_verbs_count
from rule_utils_eng.german_numbers import check_numbers_count, check_numbers_length
from rule_utils_eng.german_sentences import german_clause_monotonicity, german_clause_odd_even, check_word_counts_even, check_word_counts_odd, check_even_decrease, check_odd_increase


def rule_based_evaluate(item, rule, model_response):
    print("rulenow:",rule)
    try:
        # 0. 是否出现所有["关键词", "关键词2", ...]
        if rule.startswith("keyword"):
            return model_keywords(txt_to_json_og(rule), model_response, item["question"])
        
        # 1. 是否出现["关键词", "关键词2", ...]中的任意n个，比如: model_any_keywords2的意思是必须出现两个关键词
        if rule.startswith("any_keywords"):
            match = re.search(r'any_keywords(\d+)', rule)  # 匹配'any_keywords'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_keywords_any(num, txt_to_json_og(rule), model_response, item["question"])
        
        # 2. 是否不出现["关键词", "关键词2", ...]
        elif rule.startswith("non_keyword") or rule.startswith("non_keyword"):
            return model_non_keywords(txt_to_json_og(rule), model_response, item["question"])
    
        elif rule.startswith("non_special_notation"):
            _, _, notation = rule.partition(":")
            for i in model_response:
                if notation in i:
                    return 0, f"{notation} detected in model response: {i}"
            return 1, f"{notation} not detected in any of model responses"

        
        # 3. 统计["xxxx", "ccccc", "aaaaa", ...]每个信息的长度是否满足rule的要求
        elif rule.startswith("each_length"):
            flag, detail, _ = model_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        
        # 3. 统计阿拉伯语字数
        elif rule.startswith("arabic_each_length"):
            flag, detail, _ = arabic_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        
        elif rule.lower().startswith("portuguese_each_length"):
            flag, detail, _ =  portuguese_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        
        # 4. 统计["xxxx", "ccccc", "aaaaa", ...]的总长度是否满足rule的要求
        elif rule.startswith("total_length"):
            return model_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("arabic_total_length"):
            return arabic_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("portuguese_total_length"):
            return portuguese_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("russian_each_length"):
            flag, detail, _ = russian_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("russian_total_length"):
            return russian_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("french_each_length"):
            flag, detail, _ = french_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("french_total_length"):
            return french_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("spanish_each_length"):
            flag, detail, _ = spanish_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("spanish_total_length"):
            return spanish_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("indonesian_each_length"):
            flag, detail, _ = indonesian_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("indonesian_total_length"):
            return indonesian_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("german_each_length"):
            flag, detail, _ = german_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("german_total_length"):
            return german_total_length(txt_to_json_og(rule), model_response)

        elif rule.startswith("mixed_language_each_length"):
            language = rule.split(":")[1]
            word_range = rule.split(":")[2]
            flag, exp, _,_  = mixed_language_each_length(txt_to_json_og(word_range), model_response, language)
            return flag, exp
        
        elif rule.startswith("language_ratio"):
            language = rule.split(":")[1]
            ratio = rule.split(":")[2]
            ratio = txt_to_json_og(rule)

            for i in model_response:
                chinese_count = count_chinese_words(i)
                _, _, _, language_word_count = mixed_language_each_length(txt_to_json_og(rule), model_response, language)
                real_ratio = 1 if language_word_count == 0 else chinese_count / language_word_count
                expected_ratio = ratio[0] / ratio[1]
                
                # 四舍五入到小数点后两位进行比较
                if round(real_ratio, 2) != round(expected_ratio, 2):
                    return 0, f"❌ 不匹配: 中文字符数：{str(chinese_count)}，{language}单词数：{str(language_word_count)}，比例：{real_ratio:.4f}, 期望比例为：{str(ratio[0])} / {str(ratio[1])} = {expected_ratio:.4f}，至少确保小数点后两位是一致的"

            return 1, "✅ 匹配"
        
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
        
        elif rule.startswith("ar_repeat_each"):
            return ar_repeat_each(model_response)
        

        # 8. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以rule[0]指定的信息结尾
        elif rule.startswith("endswith_each"):
            return model_endswith_each(txt_to_json_og(rule), model_response)

        # 9. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以rule[0]指定的信息开头
        elif rule.startswith("startswith_each"):
            return model_startswith_each(txt_to_json_og(rule), model_response)
        
        # 10. ["xxxx", "ccccc", "aaaaa", ...]每个element是否满足成语接龙，前一个结尾字=后一个开头字
        elif rule.startswith("jielong"):
            return model_jielong(model_response)
        
        # 11. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否满足押韵，押韵比例是否超过60%
        elif rule.startswith("yayun"):
            return yayun(model_response)
        
        elif rule.startswith("portuguese_yayun"):
            return portuguese_yayun(model_response)
        
        elif rule.startswith("arabic_yayun"):
            return arabic_yayun(model_response)
        
        elif rule.startswith("german_yayun"):
            return german_yayun(model_response)
        
        elif rule.startswith("french_yayun"):
            return french_yayun(model_response)
        
        elif rule.startswith("russian_yayun"):
            return russian_yayun(model_response)
        
        elif rule.startswith("spanish_yayun"):
            return spanish_yayun(model_response)
        
        elif rule.startswith("indonesian_yayun"):
            return indonesian_yayun(model_response)
        
        # 12. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以标点结尾
        elif rule.startswith("no_end_with_punctuation"):
            return model_no_end_with_punctuation(model_response)
        
        # 14. 判断是否是xxx schema
        elif rule.startswith("SCHEMA"):
            return model_schema(item, rule.split(":")[1], model_response)
        
        # 16. 所有element内没有任何文字是一样的
        elif rule.startswith("no_word_repeat"):
            return model_no_word_repeat(model_response)
        
        elif rule.startswith("ar_no_word_repeat"):
            return ar_no_word_repeat(model_response)

        # 是否有75%以上的字有重复
        elif rule.startswith("non_very_similar"):
            return model_non_very_similar(model_response, item["question"])
        
        elif rule.startswith("word_freq"):
            match = re.search(r'word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return each_word_freq(num, txt_to_json_og(rule), model_response, item["question"])
        
        elif rule.startswith("each_word_freq"):
            match = re.search(r'word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return each_word_freq(num, txt_to_json_og(rule), model_response, item["question"])
        
        elif rule.startswith("non_word_freq"):
            match = re.search(r'non_word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_non_word_freq(num, txt_to_json_og(rule), model_response, item["question"])

        elif rule.startswith("ENG_cap_num"):
            match = re.search(r'ENG_cap_num:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return count_cap_num(num, model_response)
        
        elif rule.startswith("ENG_low_num"):
            match = re.search(r'ENG_low_num:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return count_low_num(num, model_response)
        
        elif rule.startswith("compound_word_num"):
            return compound_word_num(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("no_character_repeat"):
            return no_character_repeat(model_response)

        elif rule.startswith("character_freq_"):
            # 修正正则表达式
            # 一行解决
            match = re.search(r'character_freq_([a-zA-Z]):\[([\d,\s]+)\]', rule)

            letter = match.group(1)
            range_list = [int(x.strip()) for x in match.group(2).split(',')]
            return character_freq(letter, range_list, model_response)
        
        
        elif rule.startswith("has_nasal_vowel"):
             return has_nasal_vowel(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("has_acute_accent"):
             return has_acute_accent(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("each_has_acute_accent"):
             return each_has_acute_accent(txt_to_json_og(rule), model_response)

        elif rule.startswith("has_circumflex_accent"):
             return has_circumflex_accent(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("each_has_circumflex_accent"):
             return each_has_circumflex_accent(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("portuguese_double_negation"):
            flag, detail, _ = portuguese_double_negation(txt_to_json_og(rule), model_response)
            return flag, detail
        
        elif rule.startswith("portuguese_date_format"):
            flag, detail, _ = portuguese_date_format(model_response)
            return flag, detail

        elif rule.startswith("portuguese_number_spelling"):
            return portuguese_number_spelling(txt_to_json_og(rule), model_response)

        
        elif rule.startswith("portuguese_starts_with_nao"):
            flag, detail = portuguese_starts_with_nao(model_response)
            return flag, detail

        elif rule.startswith("portuguese_ordinal_abbreviation"):
            range_param = eval(rule.split(":")[1])  
            flag, detail, _ = portuguese_ordinal_abbreviation(range_param, model_response)
            return flag, detail

        elif rule.startswith("has_nasal_and_cedilla_words"):
                    return has_nasal_and_cedilla_words(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("portuguese_address_abbreviation"):
            return portuguese_address_abbreviation(model_response)
        
        elif rule.startswith("portuguese_euro_format"):
             return portuguese_euro_format(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("has_cedilla_words"):
             return has_cedilla_words(txt_to_json_og(rule), model_response)
        
# Arabic
        elif rule.startswith("arabic_dual_noun_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_dual_noun_total(model_response, params)
        elif rule.startswith("arabic_dual_noun_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_dual_noun_each(model_response, params)
        
        elif rule.startswith("athlete_masc_plural_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return athlete_masc_plural_total(model_response, params)
        elif rule.startswith("athlete_masc_plural_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return athlete_masc_plural_each(model_response, params)


        elif rule.startswith("arabic_definite_article_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_definite_article_total(model_response, params)
        elif rule.startswith("arabic_definite_article_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_definite_article_each(model_response, params)
        
        elif rule.startswith("ar_independent_pronoun_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return ar_independent_pronoun_total(model_response, params)
        elif rule.startswith("ar_independent_pronoun_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return ar_independent_pronoun_each(model_response, params)
        
        elif rule.startswith("arabic_ptm_verb_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_present_third_masc_verb_total(model_response, params)
        elif rule.startswith("arabic_ptm_verb_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_present_third_masc_verb_each(model_response, params)
        
        elif rule.startswith("arabic_broken_plurals_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_broken_plurals_total(model_response, params)
        elif rule.startswith("arabic_broken_plurals_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_broken_plurals_each(model_response, params)
        
        elif rule.startswith("arabic_feminine_indefinite_total"):
            parts = rule.split(":", 1)
            base_params = parts[1] if len(parts) > 1 else ""
            min_val, max_val = ast.literal_eval(base_params)
            full_params = f"[{min_val}, {max_val}, 'indefinite']"
            return check_ar_feminine_noun_forms(model_response, full_params)

        elif rule.startswith("arabic_feminine_definite_total"):
            parts = rule.split(":", 1)
            base_params = parts[1] if len(parts) > 1 else ""
            min_val, max_val = ast.literal_eval(base_params)
            full_params = f"[{min_val}, {max_val}, 'definite']"
            return check_ar_feminine_noun_forms(model_response, full_params)
                
        elif rule.startswith("arabic_idafa_structure_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_idafa_structure_total(model_response, params)
        elif rule.startswith("arabic_idafa_structure_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_idafa_structure_each(model_response, params)

        elif rule.startswith("arabic_gender_ratio_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_gender_ratio_total(model_response, params)

        elif rule.startswith("arabic_gender_ratio_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return arabic_gender_ratio_each(model_response, params)
        
        elif rule.startswith("arabic_english_ratio"):
            return arabic_english_ratio(txt_to_json_og(rule), model_response)
        
        # 法语h词数检测
        elif rule.startswith("french_h_word_count:"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_h_word_count(model_response, params)
        
        # 法语h词比例检测（总体）
        elif rule.startswith("french_h_ratio_total:"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_h_ratio_total(model_response, params)
        
        # 法语h词比例检测（逐项）
        elif rule.startswith("french_h_ratio_each:"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_h_ratio_each(model_response, params)
        
        elif rule.startswith("french_accent_count_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_accent_count_each(model_response, params)
        
        # 长音符 (accent circonflexe) - 总数模式
        elif rule.startswith("french_circumflex_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_circumflex_total(model_response, params)

        # 长音符 (accent circonflexe) - 逐项模式
        elif rule.startswith("french_circumflex_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_circumflex_each(model_response, params)

        # 分音符 (accent tréma) - 总数模式
        elif rule.startswith("french_diaeresis_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_diaeresis_total(model_response, params)

        # 分音符 (accent tréma) - 逐项模式
        elif rule.startswith("french_diaeresis_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_diaeresis_each(model_response, params)
        
        elif rule.startswith("french_cedilla_total"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_cedilla_total(model_response, params)

        elif rule.startswith("french_cedilla_each"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_cedilla_each(model_response, params)
        
        elif rule.startswith("french_rhyme_pattern:"):
            parts = rule.split(":", 1)
            params = parts[1] if len(parts) > 1 else ""
            return french_rhyme_pattern(model_response, params)
        
        elif rule.startswith("french_seven_digit_number"):
            return contains_french_seven_digit_number(model_response)

        elif rule.startswith("is_vigesimal_number"):
            return is_vigesimal_number(model_response)
        
        elif rule.startswith("french_pronominal_verbs"):
            params = rule.split(":")[1].strip("[]")
            min_count, max_count = map(int, params.split(','))
            return check_pronominal_verbs(model_response, min_count, max_count)
        
        elif rule.startswith("french_partitive_articles"):
            params = rule.split(":")[1].strip("[]")
            min_count, max_count = map(int, params.split(','))
            return check_partitive_articles(model_response, min_count, max_count)
        
        elif rule.startswith("french_passe_compose"):
            parts = rule.split(":")
            rule_name = parts[0]
            params = parts[1].strip("[]")
            auxiliary = params.strip()
            match = re.search(r'french_passe_compose(\d+)', rule_name)
            if match:
                min_count = int(match.group(1))
            else:
                min_count = 1  # 默认至少1次
            if auxiliary not in ['avoir', 'être']:
                return False, f"❌ 规则参数错误：助动词必须是 'avoir' 或 'être'，当前为 '{auxiliary}'"
            return check_passe_compose_auxiliary(model_response, auxiliary, min_count)
        
        elif rule.startswith("french_adverbial_pronoun"):
            params = rule.split(":")[1].strip("[]")
            en_ratio, y_ratio = map(int, params.split(','))
            # 将 list 转换为字符串
            response_text = ' '.join(model_response) if isinstance(model_response, list) else model_response
            return check_adverbial_pronoun_ratio(response_text, en_ratio, y_ratio)
        
        elif rule.startswith("french_adverbial_y:"):
            range_str = rule.split(":", 1)[1]  
            count_range = ast.literal_eval(range_str)  
            return check_adverbial_y_count(model_response, count_range)

        elif rule.startswith("french_ne_usage"):
            # 规则格式: french_ne_usage444:[555,666]    
            # 表示：ne 至少出现 444 次，赘词:非赘词 = 555:666
            return check_ne_usage_from_rule(model_response, rule)

        elif rule.startswith("french_punctuation_spacing"):
            return check_french_punctuation_from_rule(model_response, rule)
        
               
        elif rule.startswith("french_special_notation:"):
            return check_special_notations(model_response, rule)
        

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
            # 解析数量格式，支持两种格式：
            # 1. has_spanish_accent_count:5
            # 2. has_spanish_accent_count:[5,10]
            if ':' in rule:
                param_part = rule.split(':', 1)[1]
                try:
                    if param_part.startswith('[') and param_part.endswith(']'):
                        # 范围格式：[min,max]，取第一个数字
                        count_range = txt_to_json_og(param_part)
                        required_count = count_range[0]
                    else:
                        # 单个数字格式
                        required_count = int(param_part)
                except:
                    required_count = 1  # 默认值
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

        elif rule.startswith("has_correct_spanish_date_format"):
            # 解析允许错误数量格式，例如：has_correct_spanish_date_format:0
            match = re.search(r'has_correct_spanish_date_format:(\d+)', rule)
            if match:
                max_allowed_errors = int(match.group(1))
            else:
                max_allowed_errors = 0  # 默认不允许任何错误
            return has_correct_spanish_date_format(model_response, max_allowed_errors)


        elif rule.startswith("has_correct_abbreviation_format_only"):
            # 解析允许的最大错误数量
            match = re.search(r'has_correct_abbreviation_format_only:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            return has_correct_abbreviation_format_only(model_response, max_errors)

        elif rule.startswith("has_spanish_abbreviation_count"):
            match = re.search(r'has_spanish_abbreviation_count:(\d+)', rule)
            if match:
                required_count = int(match.group(1))
            else:
                required_count = 1
            return has_spanish_abbreviation_count(model_response, required_count)
        
        elif rule.startswith("has_correct_spanish_number_format"):
            match = re.search(r'has_correct_spanish_number_format:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            return has_correct_spanish_number_format(model_response, max_errors)

        elif rule.startswith("has_correct_spanish_currency_format"):
            match = re.search(r'has_correct_spanish_currency_format:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            return has_correct_spanish_currency_format(model_response, max_errors)

        elif rule.startswith("has_correct_spanish_phone_format"):
            match = re.search(r'has_correct_spanish_phone_format:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            return has_correct_spanish_phone_format(model_response, max_errors)

        elif rule.startswith("has_correct_spanish_question_accents"):
            match = re.search(r'has_correct_spanish_question_accents:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            return has_correct_spanish_question_accents(model_response, max_errors)

        elif rule.startswith("has_correct_spanish_date_names_case"):
            match = re.search(r'has_correct_spanish_date_names_case:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            return has_correct_spanish_date_names_case(model_response, max_errors)

        elif rule.startswith("has_correct_spanish_address_format"):
            match = re.search(r'has_correct_spanish_address_format:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            return has_correct_spanish_address_format(model_response, max_errors)

        elif rule.startswith("total_has_complete_questions"):
            # 支持两种格式：
            # total_has_complete_questions:3 (精确匹配)
            # total_has_complete_questions:[2,1000] (范围匹配)
            if ':' in rule:
                param_part = rule.split(':', 1)[1]
                try:
                    if param_part.startswith('[') and param_part.endswith(']'):
                        # 范围格式：[min,max]
                        count_range = txt_to_json_og(param_part)
                    else:
                        # 单个数字格式
                        count_range = int(param_part)
                except:
                    count_range = 1  # 默认值
            else:
                count_range = 1
            
            return total_has_complete_questions(model_response, count_range)
        
        elif rule.startswith("has_complete_exclamations"):
            # 解析参数：[min_count, max_count] 或 [min_count]
            match = re.search(r'has_complete_exclamations:\[(\d+)(?:,(\d+))?\]', rule)
            if match:
                min_count = int(match.group(1))
                max_count = int(match.group(2)) if match.group(2) else 1000
            else:
                min_count = 1
                max_count = 1000
            
            return has_complete_exclamations(model_response, min_count, max_count)



        
        elif rule.startswith("has_spanish_ningun_sentences"):
            # 解析参数
            if ':' in rule:
                param_part = rule.split(':', 1)[1]
                try:
                    if param_part.startswith('[') and param_part.endswith(']'):
                        # 范围格式：[min,max]
                        range_content = param_part[1:-1]
                        if ',' in range_content:
                            min_count, max_count = map(int, range_content.split(','))
                            count_range = [min_count, max_count]
                        else:
                            count_range = int(range_content)
                    else:
                        count_range = int(param_part)
                except:
                    count_range = [1, 1000]  # 默认范围
            else:
                count_range = [1, 1000]
            
            return has_spanish_ningun_sentences(model_response, count_range)

        elif rule.startswith("has_correct_spanish_ningun_agreement"):
            match = re.search(r'has_correct_spanish_ningun_agreement:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            return has_correct_spanish_ningun_agreement(model_response, max_errors)
        
        
        elif rule.startswith("has_correct_spanish_ordinal_format"):
            # 解析允许的最大错误数量：has_correct_spanish_ordinal_format:0
            match = re.search(r'has_correct_spanish_ordinal_format:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0  # 默认不允许任何错误
            return has_correct_spanish_ordinal_format(model_response, max_errors)


        elif rule.startswith("has_correct_spanish_time_articles"):
            # 解析允许的最大错误数量：has_correct_spanish_time_articles:0
            match = re.search(r'has_correct_spanish_time_articles:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0  # 默认不允许任何错误
            return has_correct_spanish_time_articles(model_response, max_errors)
        
        elif rule.startswith("has_correct_total_double_negatives"):
            # 解析双重否定总数格式，例如：has_correct_total_double_negatives:[6,999]
            match = re.search(r'has_correct_total_double_negatives:\[(\d+),(\d+)\]', rule)
            if match:
                min_total = int(match.group(1))
                max_total = int(match.group(2))
            else:
                min_total = 1  # 默认最少1个
                max_total = 999  # 默认最多999个
            return has_correct_total_double_negatives(model_response, min_total, max_total)
        
        elif rule.startswith("has_correct_subject_omission_with_verb_conjugation"):
            # 解析允许的最大错误数量：has_correct_subject_omission_with_verb_conjugation:0
            match = re.search(r'has_correct_subject_omission_with_verb_conjugation:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0  # 默认不允许任何错误
            return has_correct_subject_omission_with_verb_conjugation(model_response, max_errors)
        
        elif rule.startswith("has_definite_article_noun_combinations"):
            # 解析参数：[min_count, max_count] 或 [min_count]
            match = re.search(r'has_definite_article_noun_combinations:\[(\d+)(?:,(\d+))?\]', rule)
            if match:
                min_count = int(match.group(1))
                max_count = int(match.group(2)) if match.group(2) else min_count
            else:
                min_count = 1
                max_count = 1
            
            return has_definite_article_noun_combinations(model_response, min_count, max_count)

        elif rule.startswith("has_total_definite_article_noun_combinations"):
            # 解析参数：[min_count,max_count] 或 [count,count]
            match = re.search(r'has_total_definite_article_noun_combinations:\[(\d+),(\d+)\]', rule)
            if match:
                min_count = int(match.group(1))
                max_count = int(match.group(2))
            else:
                # 如果没有匹配到范围格式，尝试单个数字格式
                single_match = re.search(r'has_total_definite_article_noun_combinations:(\d+)', rule)
                if single_match:
                    min_count = max_count = int(single_match.group(1))
                else:
                    min_count = max_count = 0
            
            return has_total_definite_article_noun_combinations(model_response, min_count, max_count)

        
        
        
        elif rule.startswith("has_correct_spanish_article_gender_agreement"):
            # 解析参数：max_errors
            match = re.search(r'has_correct_spanish_article_gender_agreement:(\d+)', rule)
            if match:
                max_errors = int(match.group(1))
            else:
                max_errors = 0
            
            return has_correct_spanish_article_gender_agreement(model_response, max_errors)
        
        elif rule.startswith("has_spanish_keywords_with_articles"):
            # 解析参数：[min_count, max_count] 或 [min_count]
            match = re.search(r'has_spanish_keywords_with_articles:\[(\d+)(?:,(\d+))?\]', rule)
            if match:
                min_count = int(match.group(1))
                max_count = int(match.group(2)) if match.group(2) else min_count
            else:
                min_count = 1
                max_count = 1
            
            return has_spanish_keywords_with_articles(model_response, min_count, max_count)

        elif rule.startswith("rus_stress_homonym_usage"):
            match = re.search(r'rus_stress_homonym_usage:([^:]+):(\d+)', rule)
            if match:
                target_word = match.group(1).strip()
                required_count = int(match.group(2))
                
                if required_count < 1:
                    return 0, "❌ required_count 必须大于0"
                
                if not target_word:
                    return 0, "❌ target_word 不能为空"
                    
            else:
                return 0, "❌ 规则格式错误，应为 'rus_stress_homonym_usage:target_word:required_count'"
            
            return rus_stress_homonym_usage(model_response, target_word, required_count)
        
        elif rule.startswith("detect_russian_evaluative_nouns_contextual"):
            try:
                # 解析参数：required_count:target_suffixes
                match = re.search(r'detect_russian_evaluative_nouns_contextual:(\d+)(?::(.+))?', rule)
                if match:
                    required_count = int(match.group(1))
                    target_suffixes_str = match.group(2)
                    
                    print(f"[DEBUG] 原始后缀字符串: '{target_suffixes_str}'")
                    
                    if target_suffixes_str:
                        # 处理多种格式的后缀参数
                        if target_suffixes_str.startswith('[') and target_suffixes_str.endswith(']'):
                            # 处理列表格式: ["-ик", "-ок", "-ек"]
                            try:
                                import ast
                                target_suffixes = ast.literal_eval(target_suffixes_str)
                                print(f"[DEBUG] AST解析成功: {target_suffixes}")
                            except Exception as e:
                                print(f"[DEBUG] AST解析失败: {e}, 尝试手动解析")
                                # 如果ast解析失败，手动解析
                                target_suffixes_str = target_suffixes_str.strip('[]')
                                target_suffixes = [suffix.strip().strip('"\'') for suffix in target_suffixes_str.split(',')]
                                print(f"[DEBUG] 手动解析结果: {target_suffixes}")
                        else:
                            # 处理逗号分隔格式: -ик,-ок,-ек
                            target_suffixes = [suffix.strip() for suffix in target_suffixes_str.split(',')]
                            print(f"[DEBUG] 逗号分隔解析: {target_suffixes}")
                        
                        # 清理空值和标准化格式
                        target_suffixes = [suffix for suffix in target_suffixes if suffix and suffix.strip()]
                        
                        # 确保后缀以-开头
                        normalized_suffixes = []
                        for suffix in target_suffixes:
                            suffix = suffix.strip()
                            if suffix and not suffix.startswith('-'):
                                suffix = '-' + suffix
                            if suffix:
                                normalized_suffixes.append(suffix)
                        
                        target_suffixes = normalized_suffixes if normalized_suffixes else None
                        print(f"[DEBUG] 标准化后的后缀: {target_suffixes}")
                    else:
                        target_suffixes = None  # 检测所有类型
                        print(f"[DEBUG] 未指定后缀，检测所有类型")
                else:
                    print(f"[DEBUG] 正则匹配失败，使用默认参数")
                    required_count = 1
                    target_suffixes = None
                
                print(f"[DEBUG] 最终解析参数: required_count={required_count}, target_suffixes={target_suffixes}")
                return detect_russian_evaluative_nouns_contextual(model_response, required_count, target_suffixes)
                
            except Exception as e:
                print(f"[ERROR] 解析规则异常: {e}")
                import traceback
                traceback.print_exc()
                return 0, f"❌ 规则解析异常: {str(e)}"


        elif rule.startswith("detect_russian_time_expression_4th_case"):
            match = re.search(r'detect_russian_time_expression_4th_case:(\d+)', rule)
            if match:
                required_count = int(match.group(1))
            else:
                required_count = 1
            return detect_russian_time_expression_4th_case(model_response, required_count)

        elif rule.startswith("detect_russian_time_expression_6th_case"):
            match = re.search(r'detect_russian_time_expression_6th_case:(\d+)', rule)
            if match:
                required_count = int(match.group(1))
            else:
                required_count = 1
            return detect_russian_time_expression_6th_case(model_response, required_count)
        
        
        elif rule.startswith("detect_russian_single_meter"):
            match = re.search(r'detect_russian_single_meter:(.+)', rule)
            if match:
                expected_meter = match.group(1).strip()
                # 验证格律类型是否有效
                valid_meters = ['Хорей', 'Ямб', 'Дактиль', 'Амфибрахий', 'Анапест']
                if expected_meter not in valid_meters:
                    return 0, f"❌ 无效的格律类型: {expected_meter}，必须是 {valid_meters} 之一"
            else:
                expected_meter = 'Ямб'  # 默认值
            return detect_russian_single_meter(model_response, expected_meter)
        
        
        elif rule.startswith("detect_russian_singular_plural_semantic_pairs"):
            match = re.search(r'detect_russian_singular_plural_semantic_pairs:(.+)', rule)
            if match:
                try:
                    required_pairs = int(match.group(1).strip())
                    # 验证要求的对数是否合理
                    if required_pairs < 0:
                        return 0, f"❌ 要求的语义差异对数量不能为负数: {required_pairs}"
                    if required_pairs > 20:
                        return 0, f"❌ 要求的语义差异对数量过大: {required_pairs}，建议不超过20"
                except ValueError:
                    return 0, f"❌ 无效的数量格式: {match.group(1).strip()}，必须是整数"
            else:
                required_pairs = 1  # 默认值
            return detect_russian_singular_plural_semantic_pairs(model_response, required_pairs)
        
        
        elif rule.startswith("detect_russian_multiple_plural_forms_enhanced"):
            # 规则格式应为: detect_russian_multiple_plural_forms_enhanced:2
            # 使用正则表达式从规则字符串中提取所需的“对数”
            match = re.search(r'detect_russian_multiple_plural_forms_enhanced:(\d+)', rule)
            
            if match:
                # 如果正则表达式匹配成功，则从匹配结果中提取数字
                required_pairs = int(match.group(1))
            else:
                # 如果规则中没有指定数量（例如 rule = "detect_russian_multiple_plural_forms_enhanced"），
                # 则使用默认值 1
                required_pairs = 1
                
            # 调用增强版的规则函数，并传入模型回答和要求的数量
            return detect_russian_multiple_plural_forms_enhanced(model_response, required_pairs)



        elif rule.startswith("check_russian_derived_words"):
            # 规则格式: check_russian_derived_words:词汇:数量
            try:
                parts = rule.split(':')
                if len(parts) != 3:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'check_russian_derived_words:词汇:数量'"
                base_word = parts[1]
                required_count = int(parts[2])
                # 调用您刚刚编写并导入的函数
                return check_russian_derived_words(model_response, base_word, required_count)
            except (IndexError, ValueError) as e:
                return 0, f"❌ 规则解析错误: '{rule}', 错误: {e}"


        elif rule.startswith("check_russian_gender_agreement"):
            # 规则格式: check_russian_gender_agreement:关键词[:数量]
            try:
                parts = rule.split(':')
                if len(parts) == 2:
                    keyword = parts[1]
                    required_count = 1
                elif len(parts) == 3:
                    keyword = parts[1]
                    required_count = int(parts[2])
                else:
                    return 0, f"❌ 规则格式错误: '{rule}'"
                
                if not keyword:
                    return 0, f"❌ 规则格式错误: '{rule}', 关键词不能为空。"
                
                return check_russian_gender_agreement(model_response, keyword, required_count)
            except Exception as e:
                return 0, f"❌ 规则解析或执行错误: '{rule}', 错误: {e}"


        elif rule.startswith("check_russian_participle_usage"):
            # 规则格式: check_russian_participle_usage:动词1:动词2
            try:
                parts = rule.split(':')
                if len(parts) != 3:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'check_russian_participle_usage:动词1:动词2'"
                
                base_verb1 = parts[1]
                base_verb2 = parts[2]
                
                if not base_verb1 or not base_verb2:
                    return 0, f"❌ 规则格式错误: '{rule}', 动词关键词不能为空。"

                # 调用新编写的规则函数
                # model_response 应该是一个只包含一个句子的列表
                return check_russian_participle_usage(model_response, base_verb1, base_verb2)
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"
            
           

        elif rule.startswith("check_keyword_inflections_each"):

            try:
                parts = rule.split(':')
                if len(parts) != 2:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'check_keyword_inflections_each:关键词'"
                
                keyword = parts[1]
                
                if not keyword or not keyword.strip():
                    return 0, f"❌ 规则格式错误: '{rule}', 关键词不能为空。"

                # 调用关键词变形检查规则函数
                # model_response 应该是一个包含待检查内容的列表
                return check_keyword_inflections_each(model_response, keyword)
                
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"

        elif rule.startswith("check_hyphenated_words_count"):
            try:
                parts = rule.split(':')
                if len(parts) != 2:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'check_hyphenated_words_count:数量'"
                
                expected_count = parts[1]
                
                if not expected_count or not expected_count.strip():
                    return 0, f"❌ 规则格式错误: '{rule}', 期望数量不能为空。"
                
                # 验证是否为有效的整数
                expected_count = expected_count.strip()
                try:
                    int(expected_count)
                except ValueError:
                    return 0, f"❌ 规则格式错误: '{rule}', 期望数量 '{expected_count}' 不是有效的整数。"
                
                # 调用连字符词汇检查规则函数
                # model_response 应该是一个包含待检查内容的列表
                return check_hyphenated_words_count(model_response, expected_count)
                
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"

        elif rule.startswith("check_russian_verb_temporal_relation"):
            try:
                parts = rule.split(':', 1)
                if len(parts) != 2:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'check_russian_verb_temporal_relation:时间关系'"
                
                expected_relation = parts[1].strip()
                
                if not expected_relation:
                    return 0, f"❌ 规则格式错误: '{rule}', 时间关系不能为空。"
                
                return check_russian_verb_temporal_relation(model_response, expected_relation)
                
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"

        
        elif rule.startswith("russian_adjective_type_count"):
            try:
                parts = rule.split(':', 2)  # 分割成3部分：函数名:类型:数量
                if len(parts) != 3:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'russian_adjective_type_count:short/long:数量'"
                
                adj_type = parts[1].strip()
                expected_count = parts[2].strip()
                
                # 验证形容词类型参数
                valid_types = ['short', 'long', 'краткие', 'полные']
                if adj_type not in valid_types:
                    return 0, f"❌ 规则格式错误: '{rule}', 形容词类型必须是 'short/long' 或 'краткие/полные'，实际为 '{adj_type}'"
                
                # 验证数量参数
                if not expected_count:
                    return 0, f"❌ 规则格式错误: '{rule}', 期望数量不能为空。"
                
                try:
                    int(expected_count)
                except ValueError:
                    return 0, f"❌ 规则格式错误: '{rule}', 期望数量 '{expected_count}' 不是有效整数。"
                
                return russian_adjective_type_count(model_response, adj_type, expected_count)
                
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"
            
        elif rule.startswith("russian_english_ratio"):
            try:
                parts = rule.split(':', 3)
                if len(parts) != 3:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'russian_english_ratio:ratio_a:ratio_b'"
                
                ratio_a = parts[1].strip()
                ratio_b = parts[2].strip()
                
                # 验证ratio_a参数
                if not ratio_a:
                    return 0, f"❌ 规则格式错误: '{rule}', ratio_a不能为空"
                
                try:
                    ratio_a_value = float(ratio_a)
                    if ratio_a_value <= 0:
                        return 0, f"❌ 规则格式错误: '{rule}', ratio_a必须大于0，实际为 '{ratio_a}'"
                except ValueError:
                    return 0, f"❌ 规则格式错误: '{rule}', ratio_a '{ratio_a}' 不是有效数字"
                
                # 验证ratio_b参数
                if not ratio_b:
                    return 0, f"❌ 规则格式错误: '{rule}', ratio_b不能为空"
                
                try:
                    ratio_b_value = float(ratio_b)
                    if ratio_b_value <= 0:
                        return 0, f"❌ 规则格式错误: '{rule}', ratio_b必须大于0，实际为 '{ratio_b}'"
                except ValueError:
                    return 0, f"❌ 规则格式错误: '{rule}', ratio_b '{ratio_b}' 不是有效数字"
                
                # 移除 debug=DEBUG_MODE 参数，或者改为 debug=False
                return russian_english_ratio(model_response, ratio_a, ratio_b, debug=False)
                
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"
        
        elif rule.startswith("check_indonesian_loanwords:"):
            try:
                parts = rule.split(':', 1)
                if len(parts) != 2:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'check_indonesian_loanwords:数量' 或 'check_indonesian_loanwords:数量,字母'"
                
                params_str = parts[1].strip()
                
                if not params_str:
                    return 0, f"❌ 规则格式错误: '{rule}', 参数不能为空。"
                
                
                param_parts = [p.strip() for p in params_str.split(',')]
                
                # 解析借词数量
                try:
                    # 移除可能的模板标记
                    cleaned_count = param_parts[0].replace('###', '')
                    expected_count = int(float(cleaned_count))
                except (ValueError, IndexError):
                    return 0, f"❌ 规则格式错误: '{rule}', 借词数量必须是整数，当前值: '{param_parts[0] if param_parts else params_str}'"
                
                if expected_count < 0:
                    return 0, f"❌ 规则格式错误: '{rule}', 借词数量不能为负数。"
                
                
                start_letter = None
                if len(param_parts) > 1:
                    start_letter = param_parts[1].strip().lower()
                    # 验证首字母格式
                    if len(start_letter) != 1 or not start_letter.isalpha():
                        return 0, f"❌ 规则格式错误: '{rule}', 首字母参数无效: '{param_parts[1]}'"
                
                
                if start_letter:
                    return check_indonesian_loanwords(model_response, expected_count, start_letter, debug=False)
                else:
                    return check_indonesian_loanwords(model_response, expected_count, debug=False)
                
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"


        elif rule.startswith("check_indonesian_plurals:"):
            try:
                parts = rule.split(':', 1)
                if len(parts) != 2:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'check_indonesian_plurals:数量'"
                
                count_str = parts[1].strip()
                
                if not count_str:
                    return 0, f"❌ 规则格式错误: '{rule}', 复数形式数量不能为空。"
                
                try:
                    # 移除可能的模板标记
                    cleaned_count = count_str.replace('###', '')
                    expected_count = int(float(cleaned_count))
                except ValueError:
                    return 0, f"❌ 规则格式错误: '{rule}', 复数形式数量必须是整数，当前值: '{count_str}'"
                
                if expected_count < 0:
                    return 0, f"❌ 规则格式错误: '{rule}', 复数形式数量不能为负数。"
                
                return check_indonesian_plurals(model_response, expected_count)
                
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"



        

        elif rule.startswith("check_indonesian_negation_keyword:"):
            try:
                parts = rule.split(':', 1)
                if len(parts) != 2:
                    return 0, f"❌ 规则格式错误: '{rule}', 应为 'check_indonesian_negation_keyword:否定词'"
                
                keyword = parts[1].strip()
                
                # 移除可能的模板标记
                keyword = keyword.replace('###', '')
                
                if not keyword:
                    return 0, f"❌ 规则格式错误: '{rule}', 否定词不能为空"
                
                # 验证是否为有效的否定词
                if keyword.lower() not in ['tidak', 'bukan', 'jangan']:
                    return 0, f"❌ 规则格式错误: '{keyword}' 不是有效的印尼语否定词（应该是 tidak/bukan/jangan）"
                
                return check_indonesian_negation_keyword(model_response, keyword)

                
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"


        elif rule.startswith("check_indonesian_abbreviations:"):
            try:
                # 提取参数
                params = rule.split(':', 1)[1].strip().replace('###', '')
                
                # 解析数量和模式
                param_parts = params.split(':')
                required_count = int(param_parts[0])
                count_mode = param_parts[1].lower() if len(param_parts) > 1 else 'total'
                
                # 验证
                if required_count < 0:
                    return 0, f"❌ 缩写词数量不能为负数: {required_count}"
                if count_mode not in ['total', 'unique']:
                    return 0, f"❌ 无效的计数模式: {count_mode}"
                
                # 调用
                return check_indonesian_abbreviations(model_response, required_count, count_mode)
                
            except (ValueError, IndexError) as e:
                return 0, f"❌ 规则格式错误: '{rule}', 错误: {e}"
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"

            
        elif rule.startswith("check_se_usage"):
            try:
                # 解析参数（最小出现次数）
                if ':' in rule:
                    min_count_str = rule.split(':', 1)[1].strip()
                    try:
                        min_count = int(min_count_str)
                    except ValueError:
                        return 0, f"❌ 规则参数错误: '{rule}', 参数必须是整数"
                else:
                    # 默认值：至少出现1次
                    min_count = 1
                
                # 调用检测函数
                passed, detail, stats = check_se_usage(model_response, min_count)
                
                # 返回结果
                if passed:
                    return 1, detail
                else:
                    return 0, detail
                    
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"
            
        elif rule.startswith("check_active_voice"):
            try:
                # 解析参数（最小出现次数）
                if ':' in rule:
                    min_count_str = rule.split(':', 1)[1].strip()
                    try:
                        min_count = int(min_count_str)
                    except ValueError:
                        return 0, f"❌ 规则参数错误: '{rule}', 参数必须是整数"
                else:
                    # 默认值：至少5个主动语态动词
                    min_count = 5
                
                # 调用检测函数
                passed, detail, stats = check_active_voice(model_response, min_count)
                
                # 返回结果
                if passed:
                    return 1, detail
                else:
                    return 0, detail
                    
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"
        elif rule.startswith("check_passive_voice"):
            try:
                # 解析参数（最小出现次数）
                if ':' in rule:
                    min_count_str = rule.split(':', 1)[1].strip()
                    try:
                        min_count = int(min_count_str)
                    except ValueError:
                        return 0, f"❌ 规则参数错误: '{rule}', 参数必须是整数"
                else:
                    # 默认值：至少8个被动语态动词
                    min_count = 8
                
                # 调用检测函数
                passed, detail, stats = check_passive_voice(model_response, min_count)
                
                # 返回结果
                if passed:
                    return 1, detail
                else:
                    return 0, detail
                    
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"

        elif rule.startswith("check_exact_colloquial_count"):
            try:
                # 解析参数（精确数量）
                if ':' in rule:
                    exact_count_str = rule.split(':', 1)[1].strip()
                    try:
                        exact_count = int(exact_count_str)
                    except ValueError:
                        return 0, f"❌ 规则参数错误: '{rule}', 参数必须是整数"
                else:
                    # 默认值：正好5个口语化表达
                    exact_count = 5
                
                # 直接使用 model_response
                text_to_check = model_response
                
                if not text_to_check:
                    return 0, f"❌ 错误：model_response 为空"
                
                # 调用检测函数
                passed, detail, stats = check_exact_colloquial_count(text_to_check, exact_count)
                
                # 返回结果
                if passed:
                    return 1, detail
                else:
                    return 0, detail
                    
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"


        elif rule.startswith("check_formal_honorifics"):
            try:
                # 解析参数（最小数量）
                if ':' in rule:
                    min_count_str = rule.split(':', 1)[1].strip()
                    try:
                        min_count = int(min_count_str)
                    except ValueError:
                        return 0, f"❌ 规则参数错误: '{rule}', 参数必须是整数"
                else:
                    # 默认值：至少5个敬语表达
                    min_count = 5
                
                # 直接使用 model_response
                text_to_check = model_response
                
                if not text_to_check:
                    return 0, f"❌ 错误：model_response 为空"
                
                # 调用检测函数
                passed, detail, stats = check_formal_honorifics(text_to_check, min_count)
                
                # 返回结果
                if passed:
                    return 1, detail
                else:
                    return 0, detail
                    
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"


        elif rule.startswith("check_polite_imperatives"):
            try:
                # 解析参数（最小数量）
                if ':' in rule:
                    min_count_str = rule.split(':', 1)[1].strip()
                    try:
                        min_count = int(min_count_str)
                    except ValueError:
                        return 0, f"❌ 规则参数错误: '{rule}', 参数必须是整数"
                else:
                    # 默认值：至少3个礼貌祈使句
                    min_count = 3
                
                # 直接使用 model_response
                text_to_check = model_response
                
                if not text_to_check:
                    return 0, f"❌ 错误：model_response 为空"
                
                # 调用检测函数
                passed, detail, stats = check_polite_imperatives(text_to_check, min_count)
                
                # 返回结果
                if passed:
                    return 1, detail
                else:
                    return 0, detail
                    
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"

        elif rule == "check_si_usage":
            try:
                return check_si_usage(model_response)
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"

        elif rule == "check_sang_usage":
            try:
                return check_sang_usage(model_response)
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"
            
        elif rule.startswith("check_fronted_emphasis:"):
            try:
                exact_count = int(rule.split(":")[1])
                return check_fronted_emphasis(model_response, exact_count)  
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"  

        elif rule.startswith("check_indonesian_loanwords_each:"):
            try:
                # 解析参数：required_count, initial_letter, letter_count
                # 格式：check_indonesian_loanwords_each:1,S,5
                params = rule.split(":")[1]
                param_parts = params.split(",")
                
                if len(param_parts) != 3:
                    return 0, f"❌ 规则参数错误: '{rule}', 需要3个参数（借词数量,首字母,字母数），实际收到 {len(param_parts)} 个参数"
                
                required_count = int(param_parts[0].strip())
                initial_letter = param_parts[1].strip()
                letter_count = int(param_parts[2].strip())
                
                # 参数验证
                if required_count < 0:
                    return 0, f"❌ 参数错误: 借词数量不能为负数 ({required_count})"
                
                if len(initial_letter) != 1 or not initial_letter.isalpha():
                    return 0, f"❌ 参数错误: 首字母必须是单个字母 ('{initial_letter}')"
                
                if letter_count <= 0 or letter_count > 20:
                    return 0, f"❌ 参数错误: 字母数必须在1-20之间 ({letter_count})"
                
                return check_indonesian_loanwords_each(model_response, required_count, initial_letter, letter_count)
                
            except ValueError as e:
                return 0, f"❌ 规则参数解析错误: '{rule}', 错误: {e}"
            except Exception as e:
                import traceback
                return 0, f"❌ 规则执行错误: '{rule}', 错误: {e}\n{traceback.format_exc()}"

    
    # german
        
        elif rule.startswith("german_words_count"):
            # 格式: german_words_count:[5,5]
            # 调用不占位连词检测函数，检查每个句子中的连词数量
            return check_conjunctions_per_sentence(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_conjunctions_per_sentence"):
            return check_conjunctions_per_sentence(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_conjunctions_order"):
            return check_conjunctions_order(model_response)
        elif rule.startswith("order_profession1_check"):
            return order_profession1_check(model_response)
        elif rule.startswith("order_profession2_check"):
            return order_profession2_check(model_response)
        elif rule.startswith("german_numbers_length"):
            return check_number_length(txt_to_json_og(rule), model_response)
        elif rule.startswith("german_numbers_parity"):
            return check_number_parity(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_number_monotonicity"):
            return check_number_monotonicity(model_response)
        elif rule.startswith("check_words_case"):
            return check_words_case(txt_to_json_og(rule), model_response)
        elif rule.startswith("german_text_diminutive_words"):
            return check_text_diminutive_words(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_imperative_sentence"):
            return check_imperative_sentence(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_formal_imperative_sentence"):
            return check_formal_imperative_sentence(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_informal_imperative_sentence"):
            return check_informal_imperative_sentence(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_sentence_length_monotonicity"):
            return check_sentence_length_monotonicity(model_response)
        elif rule.startswith("german_total_sentences"):
            return german_total_sentences(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_declarative_sentence_modal_verbs"):
            return check_declarative_sentence_modal_verbs(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_declarative_sentence_length_monotonicity"):
            return check_declarative_sentence_length_monotonicity(model_response)
        elif rule.startswith("check_three_conjunctions"):
            return check_three_conjunctions(model_response)
        elif rule.startswith("german_clause_conjunction"):
            return german_clause_conjunction(txt_to_json_og(rule), model_response)
        elif rule.startswith("german_clause_verb"):
            return german_clause_verb(model_response)
        elif rule.startswith("german_clause_monotonicity"):
            return german_clause_monotonicity(model_response)
        elif rule.startswith("german_clause_odd_even"):
            return german_clause_odd_even(model_response)
        elif rule.startswith("check_three_articles"):
            return check_three_articles(model_response)
        elif rule.startswith("german_article_count"):
            return german_article_count(txt_to_json_og(rule), model_response)
        elif rule.startswith("german_article_der"):
            return german_article_der(txt_to_json_og(rule), model_response)
        elif rule.startswith("german_article_das"):
            return german_article_das(txt_to_json_og(rule), model_response)
        elif rule.startswith("german_article_die"):
            return german_article_die(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_modal_verbs_count"):
            return check_modal_verbs_count(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_numbers_count"):
            return check_numbers_count(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_numbers_length"):
            return check_numbers_length(txt_to_json_og(rule), model_response)
        elif rule.startswith("check_word_counts_even"):
            return check_word_counts_even(model_response)
        elif rule.startswith("check_word_counts_odd"):
            return check_word_counts_odd(model_response)
        elif rule.startswith("check_even_decrease"):
            return check_even_decrease(model_response)
        elif rule.startswith("check_odd_increase"):
            return check_odd_increase(model_response)
        

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
    