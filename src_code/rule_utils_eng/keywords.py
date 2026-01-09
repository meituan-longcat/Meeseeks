
# coding=utf-8
import os
import sys
import re

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._detect_primary_language import detect_primary_language
from src_code.utils_eng import to_lowercase_list

try:
    import simplemma
    simplemma_AVAILABLE = True
except ImportError:
    simplemma_AVAILABLE = False
    print("simplemma库未安装,正在自动安装...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "simplemma"])
        import simplemma 
        simplemma_AVAILABLE = True
        print("✅ simplemma库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install simplemma")


def tokenize_texts_with_normalization(texts, language=None, return_mapping=False):
    """
    对文本进行分词和标准化处理
    
    参数:
        texts: 文本列表或单个文本
        language: 语言代码,如果为None则自动检测
        return_mapping: 是否返回原始token到标准化token的映射
    
    返回:
        如果return_mapping=False: 返回标准化后的tokens列表
        如果return_mapping=True: 返回 (tokens列表, 映射列表)
    """
    if isinstance(texts, str):
        texts = [texts]
    
    # 自动检测语言
    if language is None:
        combined_text = ' '.join(texts)
        language = detect_primary_language(combined_text)
    
    tokens_list = []
    mappings_list = []
    
    for text in texts:
        # 简单的分词：按空格和标点符号分割
        # 保留原始的分词结果用于映射
        raw_tokens = re.findall(r'\b\w+\b', text.lower())
        
        # 标准化tokens
        normalized_tokens = []
        mapping = {}
        
        for token in raw_tokens:
            # 使用simplemma进行词形还原作为标准化
            normalized = simplemma.lemmatize(token, lang=language)
            normalized_tokens.append(normalized)
            mapping[token] = normalized
        
        tokens_list.append(normalized_tokens)
        mappings_list.append(mapping)
    
    if return_mapping:
        return tokens_list, mappings_list
    return tokens_list


def is_chinese_or_japanese(text):
    """判断文本是否包含中文或日文字符"""
    return bool(re.search(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", text))
 

def is_raw_keyword(keyword):
    """判断关键词是否需要原文本直接匹配（中文 ,日文或包含空白字符）"""
    return is_chinese_or_japanese(keyword) or bool(re.search(r"\s", keyword))


def match_keyword_in_text(keyword, tokens, original_text, language=None):
    """
    检查关键词是否在文本中
    返回: (是否匹配, 匹配类型)
    """
    # 对于中日文或包含空格的关键词,直接在原文中查找（这些语言没有明确的单词边界）
    if is_cjk_language(keyword):
        if keyword.lower() in original_text.lower():
            return True, "直接匹配"
        return False, None
    
    # 对于英文等其他语言，使用单词边界匹配避免匹配子串
    # 先尝试使用正则表达式的单词边界匹配
    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
    if re.search(pattern, original_text.lower()):
        return True, "直接匹配"
    
    # 标准化关键词
    if language is None:
        language = detect_primary_language(original_text)
    
    normalized_keyword = simplemma.lemmatize(keyword.lower(), lang=language) 
    
    # 检查是否在tokens中
    if normalized_keyword in tokens:
        return True, "标准化匹配"
    
    # 检查词形还原匹配
    for token in set(tokens):  # 使用set避免重复检查
        if not token or not token.strip():
            continue
        lemmatized_token = simplemma.lemmatize(token.lower(), lang=language) 
        if lemmatized_token == normalized_keyword:
            return True, "词形还原匹配"
    
    return False, None


def count_keyword_occurrences(keyword, tokens, original_text, language=None):
    """计算关键词在文本中出现的次数"""
    
    # 如果是中文日语或者韩语
    if is_cjk_language(keyword):
        return original_text.count(keyword)
    else:
        # 对于英文关键词，先尝试在原始文本中直接计数（处理混合中英文的情况）
        # 这样可以避免分词问题
        
        # 删除原文中的中文日语韩语字符
        cleaned_text = remove_cjk_characters(original_text)
        
        if language is None:
            language = detect_primary_language(cleaned_text)
        
        # 标准化关键词
        normalized_keyword = simplemma.lemmatize(keyword.lower(), lang=language)
        
        # 方法1: 先尝试在tokens中计数
        count = 0
        for token in tokens:
            # 跳过空token
            if not token or not token.strip():
                continue
            
            # 标准化token
            normalized_token = simplemma.lemmatize(token.lower(), lang=language)
            
            # 比较标准化后的token和关键词
            if normalized_token == normalized_keyword:
                count += 1
        
        # 方法2: 如果tokens中没有找到，尝试在原始文本中直接查找
        # 这处理了分词可能遗漏的情况（特别是混合中英文）
        if count == 0:
            # 在原始文本中查找关键词（不区分大小写）
            import re
            # 对于混合中英文的情况，使用更灵活的匹配
            # 先尝试单词边界匹配
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = re.findall(pattern, original_text.lower())
            
            # 如果单词边界匹配失败（可能是中文环境），尝试直接匹配
            if not matches:
                # 直接查找关键词（不区分大小写）
                count = original_text.lower().count(keyword.lower())
            else:
                count = len(matches)
        
        return count

def is_cjk_language(text):
    """判断文本是否包含中文、日语或韩语字符"""
    for char in text:
        # 中文字符范围
        if '\u4e00' <= char <= '\u9fff':
            return True
        # 日语平假名
        if '\u3040' <= char <= '\u309f':
            return True
        # 日语片假名
        if '\u30a0' <= char <= '\u30ff':
            return True
        # 韩语字符范围
        if '\uac00' <= char <= '\ud7af':
            return True
    return False

def remove_cjk_characters(text):
    """删除文本中的中文、日语、韩语字符"""
    result = []
    for char in text:
        # 跳过中文字符
        if '\u4e00' <= char <= '\u9fff':
            continue
        # 跳过日语平假名
        if '\u3040' <= char <= '\u309f':
            continue
        # 跳过日语片假名
        if '\u30a0' <= char <= '\u30ff':
            continue
        # 跳过韩语字符
        if '\uac00' <= char <= '\ud7af':
            continue
        result.append(char)
    return ''.join(result)




def format_keyword_display(keyword, language):
    """格式化关键词显示,包括标准化形式"""
    normalized = simplemma.lemmatize(keyword.lower(), lang=language)
    if normalized != keyword.lower():
        return f"'{keyword}'(标准化: '{normalized}')"
    return f"'{keyword}'"


# ===== 主要的模型函数 =====

def model_non_keywords(keywords, corresponding_parts, question):
    """每个 part 都不应出现任何关键词"""
    kws = to_lowercase_list(keywords)
    language = detect_primary_language(question)
    
    for part in corresponding_parts:
        tokens = tokenize_texts_with_normalization(part, language)[0]
        part_lower = part.lower()
        
        for kw in kws:
            is_match, match_type = match_keyword_in_text(kw, tokens, part_lower, language)
            if is_match:
                kw_display = format_keyword_display(kw, language)
                return 0, f"❌ '{part}' 内包含关键词: {kw_display}({match_type})"
    
    return 1, f"✅ 所有内容均未出现关键词: {kws} (包括词形变体)"


def model_keywords(keywords, corresponding_parts, question):
    """每个 part 都需出现所有关键词"""
    kws = to_lowercase_list(keywords)
    language = detect_primary_language(question)
    
    for part in corresponding_parts:
        tokens = tokenize_texts_with_normalization(part, language)[0]
        
        part_lower = part.lower()
        
        for kw in kws:
            is_match, match_type = match_keyword_in_text(kw, tokens, part_lower, language)
            if not is_match:
                kw_display = format_keyword_display(kw, language)
                return 0, f"❌ '{part}' 内缺少关键词: {kw_display}"
    
    return 1, f"✅ 所有内容均出现关键词: {kws} (包括词形变体)"


def model_keywords_any(num_need, keywords, corresponding_parts, question):
    """检查至少出现 num_need 个关键词"""
    kws = to_lowercase_list(keywords)
    language = detect_primary_language(question)
    
    # 合并所有内容
    all_text = ' '.join(corresponding_parts).lower()
    all_tokens = []
    for part in corresponding_parts:
        all_tokens.extend(tokenize_texts_with_normalization(part, language)[0])
    
    matched = []
    for kw in kws:
        is_match, match_type = match_keyword_in_text(kw, all_tokens, all_text, language)
        if is_match:
            kw_display = format_keyword_display(kw, language)
            matched.append(f"{kw_display}({match_type})")
            
            if len(matched) >= num_need:
                return 1, f"✅ 包含至少 {num_need} 个关键词: {matched[:num_need]}"
    
    return 0, f"❌ 未包含足够关键词,还需 {num_need - len(matched)} 个,已匹配: {matched}"


def model_word_freq(num_need, keywords, corresponding_parts, question):
    """检查第一个关键词出现次数恰好为 num_need"""
    kw = to_lowercase_list(keywords)[0]
    language = detect_primary_language(question)
    
    total_count = 0
    details = []
    
    for part in corresponding_parts:
        tokens = tokenize_texts_with_normalization(part, language=language)[0]
        print(tokens)
        count = count_keyword_occurrences(kw, tokens, part.lower(), language)
        if count > 0:
            details.append(f"'{part}' 中出现 {count} 次")
        total_count += count
    
    kw_display = format_keyword_display(kw, language)
    
    if total_count == num_need:
        detail_str = f"({'; '.join(details)})" if details else ""
        return 1, f"✅ {kw_display} 共出现 {total_count} 次,符合要求 {detail_str}"
    
    detail_str = f"({'; '.join(details) if details else '未找到'})"
    return 0, f"❌ {kw_display} 共出现 {total_count} 次,要求 {num_need} 次 {detail_str}"


def model_non_word_freq(num_need, keywords, corresponding_parts, question):
    """检查第一个关键词出现次数不超过 num_need"""
    kw = to_lowercase_list(keywords)[0]
    language = detect_primary_language(question)
    
    total_count = 0
    details = []
    
    for part in corresponding_parts:
        tokens = tokenize_texts_with_normalization(part, language)[0]
        count = count_keyword_occurrences(kw, tokens, part.lower(), language)
        if count > 0:
            details.append(f"'{part}' 中出现 {count} 次")
        total_count += count
    
    kw_display = format_keyword_display(kw, language)
    
    if total_count <= num_need:
        detail_str = f"({'; '.join(details) if details else '未找到'})"
        return 1, f"✅ {kw_display} 共出现 {total_count} 次,不超过 {num_need} 次 {detail_str}"
    
    return 0, f"❌ {kw_display} 共出现 {total_count} 次,超过 {num_need} 次 ({'; '.join(details)})"


def model_non_very_similar(sentences_list, question):
    """如果有两个句子的词集合复合率超过75%,则认为不匹配"""
    language = detect_primary_language(question)
    tokens_list = tokenize_texts_with_normalization(sentences_list)
    
    def calculate_similarity(tokens1, tokens2):
        set1, set2 = set(tokens1), set(tokens2)
        total = len(set1) + len(set2)
        if total == 0:
            return 0
        return (2 * len(set1 & set2)) / total
    
    for i in range(len(sentences_list)):
        for j in range(i + 1, len(sentences_list)):
            sim = calculate_similarity(tokens_list[i], tokens_list[j])
            
            if sim > 0.75:
                common_words = set(tokens_list[i]) & set(tokens_list[j])
                return 0, (f"❌ 句子对相似度过高:\n"
                          f"1: '{sentences_list[i]}'\n"
                          f"2: '{sentences_list[j]}'\n"
                          f"相似度: {sim:.3f}\n"
                          f"共同词汇: {list(common_words)}")
    
    max_sim = max([calculate_similarity(tokens_list[i], tokens_list[j]) 
                   for i in range(len(tokens_list)) 
                   for j in range(i + 1, len(tokens_list))], default=0)
    
    return 1, f"✅ 无特别相似句子 (最高相似度: {max_sim:.3f})"

#针对each的词频
def each_word_freq(num_need, keywords, corresponding_parts, question):
    """检查每一条中所有关键词出现次数恰好为 num_need"""
    kw_list = to_lowercase_list(keywords)
    language = detect_primary_language(question)
    
    details = []
    failed_items = []
    satisfied_items = []
    all_parts_valid = True
    
    for i, part in enumerate(corresponding_parts):
        tokens = tokenize_texts_with_normalization(part, language=language)[0]
        print(f"第{i+1}项 tokens: {tokens}")
        
        part_details = []
        part_valid = True
        
        # 检查每个关键词
        for kw in kw_list:
            kw_display = format_keyword_display(kw, language)
            count = count_keyword_occurrences(kw, tokens, part.lower(), language)
            
            # 判断当前关键词是否符合要求
            is_kw_valid = count == num_need
            part_details.append(f"{kw_display}{count}次")
            
            if not is_kw_valid:
                part_valid = False
        
        # 判断当前部分是否符合要求（所有关键词都要满足）
        if not part_valid:
            all_parts_valid = False
            failed_items.append(f"第{i+1}项")
            details.append(f"第{i+1}项({'; '.join(part_details)})")
        else:
            satisfied_items.append(f"第{i+1}项")
            details.append(f"第{i+1}项({'; '.join(part_details)})")
    
    if all_parts_valid:
        detail_str = f": {'; '.join(details)}" if details else ""
        return 1, f"✅ 所有项中所有关键词都出现 {num_need} 次{detail_str}"
    else:
        # 构建失败时的输出格式
        failed_list = "、".join(failed_items)
        failed_details = [d for d in details if any(item in d for item in failed_items)]
        
        if satisfied_items:
            satisfied_list = "、".join(satisfied_items)
            return 0, f"❌ {satisfied_list}满足；{failed_list}不满足要求：{'; '.join(failed_details)}"
        else:
            return 0, f"❌ 均不满足要求 {num_need} 次：{'; '.join(failed_details)}"


if __name__ == '__main__':
    # 测试代码
    # print(tokenize_texts_with_normalization("travaux", language="fr"))
    # print(tokenize_texts_with_normalization("trabajo", language="es"))
    # print(tokenize_texts_with_normalization("s’il", language="fr"))
    # print(tokenize_texts_with_normalization("qu’il", language="fr"))
    # print(tokenize_texts_with_normalization("jusqu’il", language="fr"))
    # print(tokenize_texts_with_normalization("lorsqu’il", language="fr"))
    # осведомленность осведомлённость
    # keywords = ["therme"]
    # model_response = ["Die Thermen in Japan sind wunderschön.", "Ich besuche gerne eine Therme."]

    # model_response = "大家好,我是一个来自遥远地方的有趣灵魂,来到上海这座充满活力的城市,感受着这里的繁华与多元。小时候我喜欢在院子里追逐蝴蝶,也爱在雨天听老奶奶讲故事。我的家乡有很多美食,但来到上海后,我发现这里的生煎和小笼包更让我流口水。我喜欢在黄浦江边散步,欣赏上海夜景,偶尔会和朋友一起去外滩拍照。我的性格开朗,喜欢结交新朋友,尤其是在上海这样的大都市,认识了很多来自世界各地的人。平时我喜欢看书,尤其是科幻小说,也爱听音乐,偶尔会弹吉他。我觉得生活就像一场冒险,每天都充满新鲜事物。来到上海后,我学会了用上海话点菜,虽然发音还不标准,但老板娘总是很热情地纠正我。我的梦想是能在上海实现自己的价值,成为一个有趣又有用的人。说到工作,我在APP开发领域有丰富经验。曾经参与过多个APP项目,从需求分析到上线运营,每个环节都亲力亲为。比如我在一个电商APP项目中,负责前端界面设计和后端数据交互,采用了最新的Flutter技术,让用户体验更加流畅。还记得有一次,客户突然要求增加一个社交功能,我和团队连夜加班,最终在上海的办公室里完成了任务,客户非常满意。在另一个健康管理APP项目中,我负责数据采集和分析模块,利用AI算法提升了用户健康建议的准确性。我的代码风格简洁,注重可维护性,团队成员都说和我合作很愉快。曾经在上海举办的APP开发大赛中获得过二等奖,那次经历让我认识到创新的重要性。除了开发,我还参与过APP的测试和优化工作,发现并修复了多个关键bug,保障了产品稳定运行。我的APP开发经验不仅限于技术层面,还包括与产品经理、设计师的沟通协作,确保每个APP都能满足用户需求。每次看到自己的APP在上海的地铁里被用户使用,我都感到非常自豪。说到数据挖掘,我在这个领域也有不少心得。曾经在上海一家互联网公司担任数据分析师,负责用户行为数据挖掘。通过构建用户画像,帮助公司精准营销,提升了APP用户活跃度。还参与过金融APP的数据风控项目,利用机器学习模型识别高风险用户,有效降低了坏账率。我的数据挖掘方法包括数据清洗、特征工程、模型训练和结果可视化,能够独立完成从数据到决策的全过程。曾经在上海的一个医疗APP项目中,分析用户健康数据,发现了影响用户睡眠质量的关键因素,为产品优化提供了科学依据。我的数据挖掘工具包括Python、R、SQL等,熟练使用pandas、scikit-learn等库。团队成员都说我思路清晰,善于发现问题并提出解决方案。还记得有一次在上海的咖啡馆里,和同事讨论APP用户增长策略,灵感迸发,最终制定了有效的数据驱动方案。我的数据挖掘经验不仅限于技术,还包括与业务部门的沟通,确保数据分析结果能够落地应用。每次看到自己的分析成果在上海的APP产品中发挥作用,我都感到非常有成就感。工作之余,我喜欢参加上海的技术沙龙,结识志同道合的朋友,一起交流APP开发和数据挖掘的最新趋势。我的工作态度积极,喜欢挑战新技术,乐于分享经验。每当遇到难题,我总是能用幽默化解压力,团队气氛也因此更加轻松。我相信,只有不断学习和创新,才能在上海这样竞争激烈的环境中脱颖而出。我的目标是成为上海最有趣、最专业的APP开发和数据挖掘专家。希望能在上海的工作中继续成长,和大家一起创造更美好的未来。工作对我来说不仅是谋生,更是实现自我价值的舞台。每次完成一个APP项目,或是挖掘出有价值的数据洞见,我都感到无比满足。上海给了我很多机会,也让我结识了很多优秀的人。未来我希望能在上海继续深耕APP开发和数据挖掘领域,用自己的专业和热情为公司创造更多价值。感谢您阅读我的简历,期待在上海与您共事,一起用APP和数据改变世界!"




    # question = "请根据以下要求生成一片啊啊啊啊啊啊啊啊啊啊"
    # result, message = model_word_freq(
    #     num_need=3,
    #     keywords=["APP"],
    #     corresponding_parts=[model_response],
    #     question=question
    # )
    # print(result,message)

    keyword = ["discovery"]
    cor = ["Last week, while swimming in a suburban lake, I stumbled upon a cave entrance hidden beneath mud. Diving in, I found myself surrounded by mysterious murals—vivid, intricate, and unlike anything in known archaeology. This discovery has sparked debate, disbelief, and wonder. Now, I prepare to return, seeking evidence that will silence skeptics and inspire believers."]    
    question = "heelllllo"
    print(model_non_keywords(keyword,cor,question))


