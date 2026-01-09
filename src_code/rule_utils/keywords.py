# 1. 每个corresponding part都需要出现所有keywords
def model_keywords(keywords, corresponding_parts):
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    keywords = [keyword.lower() for keyword in keywords]
    for corresponding_part in corresponding_parts:
        for keyword in keywords:
            if keyword not in corresponding_part:
                return 0, f"❌ {str(corresponding_part)} 内缺少关键词: {str(keyword)}"
    return 1, f"✅ 关键词匹配，所有内容中均出现了关键词：{str(keywords)}"

# 2. 每个corresponding part都不能出现任何keywords
def model_non_keywords(keywords, corresponding_parts):
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    keywords = [keyword.lower() for keyword in keywords]
    for corresponding_part in corresponding_parts:
        for keyword in keywords:
            if str(keyword) in str(corresponding_part):
                return 0, f"❌ {str(corresponding_part)} 内包含关键词: {str(keyword)}"
    return 1, f"✅ 无关键词，所有内容中均未出现关键词：{str(keywords)}"

# 3. keywords any  找到其中任意n个字，是至少的关系，不是精确
def model_keywords_any(num_need, keywords, corresponding_parts):
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    keywords = [keyword.lower() for keyword in keywords]
    og_num_need = num_need
    keywords_matched = []
    for keyword in keywords:
        if str(keyword) in str(corresponding_parts):
            keywords_matched.append(keyword)
            num_need -= 1
            if num_need == 0:
                return 1, f"✅ 包含{og_num_need}个关键词：{', '.join(keywords_matched)}"
    
    if keywords_matched:
        return 0, f"❌ 不包含/不够 {og_num_need} 关键词，还差{num_need}个关键词。已包含：{', '.join(keywords_matched)}"
    else:
        return 0, f"❌ 不包含/不够 {og_num_need} 关键词，还差{num_need}个关键词"


# 4. word frequency
def model_word_freq(num_need, keywords, corresponding_parts):
    # 统计每个keyword在每个corresponding_part中出现的次数是否是num_need
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    
    all_correct = True
    error_details = []
    
    for i, corresponding_part in enumerate(corresponding_parts):
        part_errors = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            word_freq = corresponding_part.count(keyword_lower)
            if word_freq != num_need:
                all_correct = False
                part_errors.append(f"'{keyword}': {word_freq}次")
        
        if part_errors:
            error_details.append(f"第{i+1}部分: {', '.join(part_errors)}")
    
    if all_correct:
        return 1, f"✅ 每个部分中每个关键词都出现刚好 {num_need} 次"
    else:
        return 0, f"❌ 词频不符合要求: {' | '.join(error_details)}，题目要求每个关键词在每个部分中出现 {num_need} 次"

# 5. non word frequency
def model_non_word_freq(num_need, keywords, corresponding_parts):
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    # 统计每个keyword在corresponding_parts中出现的次数是否不超过num_need
    corresponding_part = corresponding_parts[0]
    
    all_correct = True
    results = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        word_freq = corresponding_part.count(keyword_lower)
        results.append((keyword, word_freq))
        if word_freq > num_need:
            all_correct = False
    
    if all_correct:
        return 1, f"✅ 每个关键词都不超过 {num_need} 次"
    else:
        details = [f"{keyword}: {freq}次" for keyword, freq in results]
        return 0, f"❌ 实际出现次数: {', '.join(details)}，题目要求每个关键词最多出现 {num_need} 次"
    

# 4. word frequency (any version)
def model_word_freq_any(num_need, keywords, corresponding_parts):
    # 统计任意keyword在corresponding_parts中出现的总次数是否是num_need
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    
    # 检查每个corresponding_part
    for part_idx, corresponding_part in enumerate(corresponding_parts):
        total_freq = 0
        all_keyword_details = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            word_freq = corresponding_part.count(keyword_lower)
            total_freq += word_freq
            all_keyword_details.append(f"'{keyword}': {word_freq}次")
        
        if total_freq != num_need:
            details_str = ' | '.join(all_keyword_details)
            return 0, f"❌ 第{part_idx+1}个部分检查失败\n   各关键词出现次数: [{details_str}]\n   总计: {total_freq}次，要求: {num_need}次"
    
    # 所有部分都满足条件
    return 1, f"✅ 所有部分中关键词总共都出现刚好 {num_need} 次"

# 5. non word frequency (any version)
def model_non_word_freq_any(num_need, keywords, corresponding_parts):
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    # 统计任意keyword在corresponding_parts中出现的总次数是否不超过num_need
    
    # 检查每个corresponding_part
    for part_idx, corresponding_part in enumerate(corresponding_parts):
        total_freq = 0
        all_keyword_details = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            word_freq = corresponding_part.count(keyword_lower)
            total_freq += word_freq
            all_keyword_details.append(f"'{keyword}': {word_freq}次")
        
        if total_freq > num_need:
            details_str = ' | '.join(all_keyword_details)
            return 0, f"❌ 第{part_idx+1}个部分检查失败\n   各关键词出现次数: [{details_str}]\n   总计: {total_freq}次，要求: 最多{num_need}次"
    
    # 所有部分都满足条件
    return 1, f"✅ 所有部分中关键词总共都不超过 {num_need} 次"

# 6.startword 接龙的第一个词是否满足某个关键词
def model_startword(startwords, corresponding_parts):
    if not corresponding_parts:
        return 0, "❌ corresponding_parts 为空"
    
    first_part = corresponding_parts[0].lower()
    startwords = [startword.lower() for startword in startwords]
    
    for startword in startwords:
        if startword in first_part:
            return 1, f"✅ 在第一个部分中找到起始词: {startword}"
    
    return 0, f"❌ 第一个部分 '{corresponding_parts[0]}' 中未找到任何起始词: {startwords}"