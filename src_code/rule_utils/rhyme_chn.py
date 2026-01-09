import os
import sys
# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import pypinyin
    pypinyin_AVAILABLE = True
except ImportError:
    pypinyin_AVAILABLE = False
    print("pypinyin库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypinyin"])
        print("pypinyin库安装成功，正在导入...")
        import pypinyin
        pypinyin_AVAILABLE = True
        print("✅ pypinyin库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install pypinyin")
        pypinyin_AVAILABLE = False

from pypinyin import pinyin, Style

try:
    import opencc
    opencc_AVAILABLE = True
except ImportError:
    opencc_AVAILABLE = False
    print("opencc库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencc==1.1.6"])
        print("opencc库安装成功，正在导入...")
        import opencc
        opencc_AVAILABLE = True
        print("✅ opencc库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install opencc")
        opencc_AVAILABLE = False

        
import re
from collections import Counter

from ..utils import clean_up_text

try:
    import pypinyin
    pypinyin_AVAILABLE = True
except ImportError:
    pypinyin_AVAILABLE = False
    print("pypinyin库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypinyin"])
        print("pypinyin库安装成功，正在导入...")
        import pypinyin
        pypinyin_AVAILABLE = True
        print("✅ pypinyin库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install pypinyin")
        pypinyin_AVAILABLE = False

from pypinyin import pinyin, Style

try:
    import opencc
    opencc_AVAILABLE = True
except ImportError:
    opencc_AVAILABLE = False
    print("opencc库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencc"])
        print("opencc库安装成功，正在导入...")
        import opencc
        opencc_AVAILABLE = True
        print("✅ opencc库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install opencc")
        opencc_AVAILABLE = False

from pypinyin import pinyin, Style
from collections import Counter

def clean_up_text(text):
    """清理文本，去除标点符号"""
    return re.sub(r'[^\u4e00-\u9fff]', '', text)

def get_rhyme_groups():
    """获取韵部映射表"""
    rhyme_groups = {
        '一麻': ['a', 'ia', 'ua'],
        '二波': ['o', 'uo'],
        '三歌': ['e'],
        '四皆': ['ie', 'üe', 've'],
        '五支': ['-i'],
        '六儿': ['er'],
        '七齐': ['i'],
        '八微': ['ei', 'ui', 'uei'],
        '九开': ['ai', 'uai'],
        '十姑': ['u'],
        '十一鱼': ['ü', 'v'],
        '十二侯': ['ou', 'iu', 'iou'],
        '十三豪': ['ao', 'iao'],
        '十四寒': ['an', 'ian', 'uan', 'üan', 'van'],
        '十五痕': ['en', 'in', 'un', 'uen', 'ün', 'vn'],
        '十六唐': ['ang', 'iang', 'uang'],
        '十七庚': ['eng', 'ing', 'ueng'],
        '十八东': ['ong', 'iong']
    }
    
    # 创建韵母到韵部的反向映射
    vowel_to_group = {}
    for group_name, vowels in rhyme_groups.items():
        for vowel in vowels:
            vowel_to_group[vowel] = group_name
    
    return rhyme_groups, vowel_to_group

def extract_rhyme_vowels_smart(words):
    """智能提取韵母，考虑多音字的最佳选择"""
    rhyme_groups, vowel_to_group = get_rhyme_groups()
    rhyme_vowels = []
    rhyme_chars = []
    
    # 收集所有可能的韵母和对应的韵部
    all_possible_data = []
    for word in words:
        if word:
            last_char = word[-1]
            rhyme_chars.append(last_char)
            possible_vowels = pinyin(last_char, style=Style.FINALS, heteronym=True)[0]
            # 转换为韵部信息
            possible_groups = []
            for vowel in possible_vowels:
                group = vowel_to_group.get(vowel, "未知韵部")
                possible_groups.append((vowel, group))
            all_possible_data.append(possible_groups)
    
    # 尝试所有组合，找到韵部押韵比例最高的组合
    best_combination = []
    best_score = 0
    
    def try_combination(index, current_combination):
        nonlocal best_combination, best_score
        
        if index == len(all_possible_data):
            # 按韵部统计
            groups = [item[1] for item in current_combination]
            group_counter = Counter(groups)
            if group_counter:
                max_count = max(group_counter.values())
                score = max_count / len(current_combination)
                if score > best_score:
                    best_score = score
                    best_combination = current_combination.copy()
            return
        
        # 尝试当前字的每个可能发音
        for vowel_group_pair in all_possible_data[index]:
            current_combination.append(vowel_group_pair)
            try_combination(index + 1, current_combination)
            current_combination.pop()
    
    try_combination(0, [])
    
    # 提取最佳组合的韵母
    rhyme_vowels = [item[0] for item in best_combination]
    
    return rhyme_vowels, rhyme_chars

def yayun(text):
    rhyme_groups, vowel_to_group = get_rhyme_groups()
    
    # 清理文本
    cleaned_text = [clean_up_text(line) for line in text]
    
    # 智能提取韵母
    rhyme_vowels, rhyme_chars = extract_rhyme_vowels_smart(cleaned_text)
    
    # 按韵部分组统计
    group_data = {}  # {韵部: [(韵母, 字符), ...]}
    
    for i, (vowel, char) in enumerate(zip(rhyme_vowels, rhyme_chars)):
        group = vowel_to_group.get(vowel, "未知韵部")
        if group not in group_data:
            group_data[group] = []
        group_data[group].append((vowel, char))
    
    # 生成结果信息
    result_msg = ""
    total_lines = len(rhyme_vowels)
    max_proportion = 0
    
    for group, items in sorted(group_data.items(), key=lambda x: len(x[1]), reverse=True):
        proportion = len(items) / total_lines
        max_proportion = max(max_proportion, proportion)
        
        # 按韵母细分显示
        vowel_groups = {}
        for vowel, char in items:
            if vowel not in vowel_groups:
                vowel_groups[vowel] = []
            vowel_groups[vowel].append(char)
        
        result_msg += f"【{group}】押韵比例：{proportion*100:.1f}%\n"
        for vowel, chars in vowel_groups.items():
            result_msg += f"  {vowel}：{'，'.join(chars)}\n"
    
    # 判断是否押韵
    if max_proportion >= 0.5:
        return 1, f"✅ 押韵匹配！\n{result_msg}"
    else:
        return 0, f"❌ 押韵不匹配！\n{result_msg}"

def lvshi_yayun(text):
    rhyme_groups, vowel_to_group = get_rhyme_groups()
    
    # 清理文本
    cleaned_text = [clean_up_text(line) for line in text]
    
    # 提取偶数句（索引1,3,5,7...）
    even_lines = []
    even_chars = []
    
    for i in range(1, len(cleaned_text), 2):
        if cleaned_text[i]:  # 确保不是空字符串
            even_lines.append(cleaned_text[i])
            last_char = cleaned_text[i][-1]
            even_chars.append(last_char)
    
    if not even_lines:
        return 0, "❌ 没有偶数句"
    
    # 智能提取偶数句韵母
    rhyme_vowels, _ = extract_rhyme_vowels_smart(even_lines)
    
    # 转换为韵部
    rhyme_groups_list = []
    for vowel in rhyme_vowels:
        group = vowel_to_group.get(vowel, "未知韵部")
        rhyme_groups_list.append(group)
    
    # 按韵部统计
    group_counter = Counter(rhyme_groups_list)
    
    # 生成结果信息
    result_msg = ""
    for group, count in group_counter.most_common():
        proportion = count / len(rhyme_vowels)
        # 找到该韵部对应的字符和韵母
        chars_in_group = []
        vowels_in_group = []
        for i, g in enumerate(rhyme_groups_list):
            if g == group:
                chars_in_group.append(even_chars[i])
                vowels_in_group.append(rhyme_vowels[i])
        
        result_msg += f"【{group}】押韵比例：{proportion*100:.1f}%\n"
        # 按韵母细分
        vowel_char_map = {}
        for vowel, char in zip(vowels_in_group, chars_in_group):
            if vowel not in vowel_char_map:
                vowel_char_map[vowel] = []
            vowel_char_map[vowel].append(char)
        
        for vowel, chars in vowel_char_map.items():
            result_msg += f"  {vowel}：{'，'.join(chars)}\n"
    
    # 判断偶数句是否同韵部
    if len(set(rhyme_groups_list)) == 1:
        return 1, f"✅ 偶数句同韵部！\n{result_msg}"
    else:
        return 0, f"❌ 偶数句不同韵部！\n{result_msg}"

        
def get_tone(pinyin_list):
    tones = []
    for py in pinyin_list:
        if py[-1].isdigit():
            tones.append(int(py[-1]))
        else:
            tones.append(0)  # 轻声
    return tones


def get_pingze(sentence):
    pinyin_result = pinyin(sentence, style=Style.TONE3)
    tones = get_tone([py[0] for py in pinyin_result])
    pingze = []
    for tone in tones:
        if tone in [1, 2]:
            pingze.append('平')
        elif tone in [3, 4]:
            pingze.append('仄')
        else:
            pingze.append('轻')
    return ''.join(pingze)


def pingze(poem_list):
    for i in range(len(poem_list)):
        poem_list[i] = clean_up_text(poem_list[i])
    results = []
    pingzeset = set()
    for sentence in poem_list:
        pingze = get_pingze(sentence)
        pingzeset.add(pingze)
        results.append(f"'{str(sentence)}' 的平仄为: {str(pingze)}")
    if len(pingzeset) != 1:
        return 0, f"❌ 平仄不一致，平仄详情：{str(results)}"
    else:
        return 1, f"✅ 平仄一致，平仄详情：{str(results)}"


def fanti(texts):
    converter = opencc.OpenCC('s2t.json')
    
    for idx, text in enumerate(texts):
        # 清理文本
        cleaned_text = clean_up_text(text)
        
        # 转换为繁体
        fanti_text = converter.convert(cleaned_text)
        
        # 检查每个字符是否已经是繁体
        for i in range(len(cleaned_text)):
            if cleaned_text[i] != fanti_text[i]:
                return 0, f"❌ 第{idx+1}个文本中的 '{cleaned_text[i]}' 不是繁体"
    
    return 1, "✅ 所有文本内容全是繁体"


def has_heteronym(texts, num):
    texts = [clean_up_text(text) for text in texts]
    
    for text in texts:
        heteronym_count = 0
        heteronym_words = []
        
        for word in text:
            possible_pronunciations = pinyin(word, style=Style.NORMAL, heteronym=True)[0]
            if len(possible_pronunciations) > 1:
                heteronym_count += 1
                heteronym_words.append((word, possible_pronunciations))
        
        if heteronym_count != num:
            # 限制输出最多50个多音字
            display_words = heteronym_words[:50]
            truncated_msg = f" (showing first 50 of {len(heteronym_words)})" if len(heteronym_words) > 50 else ""
            return 0, f"❌ TEXT: 【{text}】expected {num} heteronym(s), but found {heteronym_count}: {display_words}{truncated_msg}"
    
    return 1, f"✅ All texts have exactly {num} heteronym(s)"

#首句是否入韵
def first_line_rhyme(poem_list, requirement="入韵"):
    """
    判断首句和偶数句的韵部是否相同
    
    Args:
        poem_list: 诗句列表
        requirement: "入韵" 或 "不入韵"
        
    Returns:
        tuple: (结果码, 详细信息)
    """
    # 清理文本
    cleaned_poem_list = []
    for i in range(len(poem_list)):
        cleaned_poem_list.append(clean_up_text(poem_list[i]))
    
    if len(cleaned_poem_list) == 0:
        return 0, "❌ 诗句列表为空"
    
    # 获取韵部映射表
    rhyme_groups, vowel_to_group = get_rhyme_groups()
    
    # 获取需要检查的句子：首句(第1句) + 偶数句(第2,4,6,8句等)
    target_lines = [cleaned_poem_list[0]]  # 首句
    target_indices = [0]  # 记录原始索引
    
    for i in range(1, len(cleaned_poem_list), 2):  # 偶数句(索引1,3,5,7...)
        target_lines.append(cleaned_poem_list[i])
        target_indices.append(i)
    
    if len(target_lines) < 2:
        return 0, "❌ 需要检查的句子数量不足"
    
    # 智能提取韵母
    rhyme_vowels, rhyme_chars = extract_rhyme_vowels_smart(target_lines)
    
    # 转换为韵部
    rhyme_groups_list = []
    rhyme_details = []
    
    for i, (vowel, char, line_idx) in enumerate(zip(rhyme_vowels, rhyme_chars, target_indices)):
        group = vowel_to_group.get(vowel, "未知韵部")
        rhyme_groups_list.append(group)
        
        line_type = "首句" if line_idx == 0 else f"第{line_idx+1}句"
        rhyme_details.append(f"{line_type}'{target_lines[i]}'句尾字'{char}'韵母:{vowel} 韵部:{group}")
    
    # 检查所有韵部是否相同
    unique_groups = set(rhyme_groups_list)
    is_same_rhyme = len(unique_groups) == 1
    
    # 根据要求返回结果
    if requirement == "入韵":
        if is_same_rhyme:
            return 1, f"✅ 首句入韵，与偶数句韵部相同，韵部为'{rhyme_groups_list[0]}'。详情：{'; '.join(rhyme_details)}"
        else:
            return 0, f"❌ 首句不入韵，与偶数句韵部不同，发现{len(unique_groups)}种韵部：{unique_groups}。详情：{'; '.join(rhyme_details)}"
    
    elif requirement == "不入韵":
        if is_same_rhyme:
            return 0, f"❌ 首句入韵了，与偶数句韵部相同，但要求首句不入韵。韵部为'{rhyme_groups_list[0]}'。详情：{'; '.join(rhyme_details)}"
        else:
            return 1, f"✅ 首句不入韵，与偶数句韵部不同，符合要求。发现{len(unique_groups)}种韵部：{unique_groups}。详情：{'; '.join(rhyme_details)}"
    
    else:
        return 0, f"❌ 未识别的要求: {requirement}，应为'入韵'或'不入韵'"


#入句不押韵
def chinese_odd_lines_no_rhyme(poem_list):
    """
    检查所有出句（第1、3、5、7句）是否不入韵
    
    Args:
        poem_list: 诗句列表
        
    Returns:
        tuple: (结果码, 详细信息)
               结果码: 1表示出句都不入韵，0表示有出句入韵
    """
    # 清理文本
    cleaned_poem_list = []
    for i in range(len(poem_list)):
        cleaned_poem_list.append(clean_up_text(poem_list[i]))
    
    if len(cleaned_poem_list) == 0:
        return 0, "❌ 诗句列表为空"
    
    # 获取韵部映射表
    rhyme_groups, vowel_to_group = get_rhyme_groups()
    
    # 分别获取出句和对句
    odd_lines = []  # 出句（第1、3、5、7句）
    even_lines = []  # 对句（第2、4、6、8句）
    odd_indices = []
    even_indices = []
    
    for i in range(len(cleaned_poem_list)):
        if i % 2 == 0:  # 奇数句（索引0,2,4,6...对应第1,3,5,7句）
            odd_lines.append(cleaned_poem_list[i])
            odd_indices.append(i)
        else:  # 偶数句（索引1,3,5,7...对应第2,4,6,8句）
            even_lines.append(cleaned_poem_list[i])
            even_indices.append(i)
    
    if len(odd_lines) == 0:
        return 0, "❌ 没有出句"
    
    if len(even_lines) == 0:
        return 0, "❌ 没有对句"
    
    # 获取对句的韵部（作为标准韵部）
    even_rhyme_vowels, even_rhyme_chars = extract_rhyme_vowels_smart(even_lines)
    even_rhyme_groups = []
    for vowel in even_rhyme_vowels:
        group = vowel_to_group.get(vowel, "未知韵部")
        even_rhyme_groups.append(group)
    
    # 检查对句是否同韵部
    unique_even_groups = set(even_rhyme_groups)
    if len(unique_even_groups) != 1:
        return 0, f"❌ 对句韵部不统一，无法判断出句是否入韵。对句韵部：{unique_even_groups}"
    
    standard_rhyme_group = list(unique_even_groups)[0]
    
    # 获取出句的韵部
    odd_rhyme_vowels, odd_rhyme_chars = extract_rhyme_vowels_smart(odd_lines)
    odd_rhyme_groups = []
    for vowel in odd_rhyme_vowels:
        group = vowel_to_group.get(vowel, "未知韵部")
        odd_rhyme_groups.append(group)
    
    # 检查每个出句是否入韵
    rhyme_details = []
    non_rhyming_count = 0
    
    for i, (line, vowel, char, group, line_idx) in enumerate(zip(odd_lines, odd_rhyme_vowels, odd_rhyme_chars, odd_rhyme_groups, odd_indices)):
        line_num = line_idx + 1
        is_rhyming = (group == standard_rhyme_group)
        
        if is_rhyming:
            rhyme_details.append(f"❌ 第{line_num}句'{line}'句尾字'{char}'韵母:{vowel} 韵部:{group} (与标准韵部相同，违反出句不入韵规则)")
        else:
            rhyme_details.append(f"✅ 第{line_num}句'{line}'句尾字'{char}'韵母:{vowel} 韵部:{group} (与标准韵部不同，符合出句不入韵规则)")
            non_rhyming_count += 1
    
    # 添加对句信息作为参考
    even_details = []
    for i, (line, vowel, char, group, line_idx) in enumerate(zip(even_lines, even_rhyme_vowels, even_rhyme_chars, even_rhyme_groups, even_indices)):
        line_num = line_idx + 1
        even_details.append(f"第{line_num}句'{line}'句尾字'{char}'韵母:{vowel} 韵部:{group}")
    
    all_details = f"标准韵部（对句）：{standard_rhyme_group}\n对句详情：{'; '.join(even_details)}\n出句检查：{'; '.join(rhyme_details)}"
    
    if non_rhyming_count == len(odd_lines):
        return 1, f"✅ 所有出句都不入韵！\n{all_details}"
    else:
        rhyming_count = len(odd_lines) - non_rhyming_count
        return 0, f"❌ 有{rhyming_count}个出句入韵，不符合要求！\n{all_details}"

########特殊韵律2：进退韵########
# 提取共用数据和函数
def _get_yun_data():
    """获取韵部数据"""
    yun_order = [
        "一东", "二冬", "三江", "四支", "五微", "六鱼", "七虞", "八齐", "九佳", "十灰",
        "十一真", "十二文", "十三元", "十四寒", "十五删"
    ]
    
    yun_zi_dict = {
        "五微": ["微", "薇", "晖", "辉", "徽", "挥", "韦", "围", "帏", "违", "闱", "霏", "菲", "妃", "飞", "非", "扉", "肥", "威", "祈", "畿", "机", "几", "讥", "玑", "稀", "希", "衣", "依", "归", "饥", "矶", "欷", "诽", "绯", "晞", "葳", "巍", "沂", "圻", "颀"],
        "六鱼": ["鱼", "渔", "初", "书", "舒", "居", "裾", "琚", "车", "渠", "蕖", "余", "予", "誉", "舆", "胥", "狙", "锄", "疏", "蔬", "梳", "虚", "嘘", "墟", "徐", "猪", "闾", "庐", "驴", "诸", "储", "除", "滁", "蜍", "如", "畲", "淤", "妤", "苴", "菹", "沮", "徂", "龉", "茹", "榈", "於", "祛", "蘧", "疽", "蛆", "醵", "纾", "樗", "躇", "欤", "据"],
        "七虞": ["虞", "愚", "娱", "隅", "无", "芜", "巫", "于", "衢", "癯", "瞿", "氍", "儒", "襦", "濡", "须", "需", "朱", "珠", "株", "诛", "铢", "蛛", "殊", "俞", "瑜", "榆", "愉", "逾", "渝", "窬", "谀", "腴", "区", "躯", "驱", "岖", "趋", "扶", "符", "凫", "芙", "雏", "敷", "麸", "夫", "肤", "纡", "输", "枢", "厨", "俱", "驹", "模", "谟", "摹", "蒲", "逋", "胡", "湖", "瑚", "乎", "壶", "狐", "弧", "孤", "辜", "姑", "觚", "菰", "徒", "途", "涂", "荼", "图", "屠", "奴", "吾", "梧", "吴", "租", "卢", "鲈", "炉", "芦", "颅", "垆", "蚨", "孥", "帑", "苏", "酥", "乌", "污", "枯", "粗", "都", "茱", "侏", "姝", "禺", "拘", "嵎", "蹰", "桴", "俘", "臾", "萸", "吁", "滹", "瓠", "糊", "醐", "呼", "沽", "酤", "泸", "舻", "轳", "鸬", "驽", "匍", "葡", "铺", "菟", "诬", "呜", "迂", "盂", "竽", "趺", "毋", "孺", "酴", "鸪", "骷", "刳", "蛄", "晡", "蒱", "葫", "呱", "蝴", "劬", "殂", "猢", "郛", "孚"],
        "八齐": ["齐", "黎", "犁", "梨", "妻", "萋", "凄", "堤", "低", "题", "提", "蹄", "啼", "鸡", "稽", "兮", "倪", "霓", "西", "栖", "犀", "嘶", "撕", "梯", "鼙", "赍", "迷", "泥", "溪", "蹊", "圭", "闺", "携", "畦", "嵇", "跻", "奚", "脐", "醯", "黧", "蠡", "醍", "鹈", "奎", "批", "砒", "睽", "荑", "篦", "齑", "藜", "猊", "蜺", "鲵", "羝"],
        "九佳": ["佳", "街", "鞋", "牌", "柴", "钗", "差", "崖", "涯", "偕", "阶", "皆", "谐", "骸", "排", "乖", "怀", "淮", "豺", "侪", "埋", "霾", "斋", "槐", "睚", "崽", "楷", "秸", "揩", "挨", "俳"]
    }
    
    allowed_yun_names = ["五微", "六鱼", "七虞", "八齐", "九佳"]
    
    # 创建字符到韵部的反向映射
    char_to_yun = {}
    for yun_name, chars in yun_zi_dict.items():
        for char in chars:
            char_to_yun[char] = yun_name
    
    return yun_order, yun_zi_dict, allowed_yun_names, char_to_yun

def _check_yun_pattern(poem_list, pattern_name, jia_positions, yi_positions):
    """
    通用韵律格式检查函数
    
    Args:
        poem_list: 诗句列表
        pattern_name: 格式名称（如"进退韵"、"辘轳格"）
        jia_positions: 甲韵句子位置列表（如[0,2]表示第2、6句）
        yi_positions: 乙韵句子位置列表（如[1,3]表示第4、8句）
    """
    yun_order, yun_zi_dict, allowed_yun_names, char_to_yun = _get_yun_data()
    
    # 清理文本
    cleaned_poem_list = [clean_up_text(line) for line in poem_list]
    
    if len(cleaned_poem_list) < 8:
        return 0, f"❌ {pattern_name}需要至少8句诗，当前只有{len(cleaned_poem_list)}句"
    
    # 获取目标句子：第2、4、6、8句
    target_indices = [1, 3, 5, 7]
    target_positions = ["第2句", "第4句", "第6句", "第8句"]
    
    line_details = []
    for i, idx in enumerate(target_indices):
        if idx < len(cleaned_poem_list):
            line = cleaned_poem_list[idx]
            char = line[-1] if line else ""
            yun = char_to_yun.get(char, "未知韵部")
            line_details.append({
                'position': target_positions[i],
                'line': line,
                'char': char,
                'yun': yun
            })
        else:
            return 0, f"❌ 缺少第{idx+1}句"
    
    # 第一层检查：韵脚范围检查
    range_errors = [f"❌ {detail['position']}句尾字'{detail['char']}'不在要求韵部中" 
                   for detail in line_details if detail['yun'] == "未知韵部"]
    
    if range_errors:
        allowed_yun_str = "、".join(allowed_yun_names)
        return 0, f"❌ 【韵脚范围检查失败】你的韵脚只能在平水韵的{allowed_yun_str}中选择。\n检测详情：{'; '.join(range_errors)}"
    
    # 第二层检查：格式检查
    jia_yun_names = [line_details[pos]['yun'] for pos in jia_positions]
    yi_yun_names = [line_details[pos]['yun'] for pos in yi_positions]
    
    jia_yun_same = len(set(jia_yun_names)) == 1
    yi_yun_same = len(set(yi_yun_names)) == 1
    jia_yi_different = jia_yun_same and yi_yun_same and jia_yun_names[0] != yi_yun_names[0]
    
    # 检查相邻
    adjacent = False
    if jia_yi_different:
        try:
            jia_index = yun_order.index(jia_yun_names[0])
            yi_index = yun_order.index(yi_yun_names[0])
            adjacent = abs(jia_index - yi_index) == 1
        except ValueError:
            adjacent = False
    
    # 生成详细信息
    format_details = [f"{detail['position']}句尾字'{detail['char']}'韵部:{detail['yun']}" for detail in line_details]
    
    # 生成位置描述
    jia_pos_desc = "、".join([target_positions[pos] for pos in jia_positions])
    yi_pos_desc = "、".join([target_positions[pos] for pos in yi_positions])
    
    # 检查结果
    if not jia_yun_same:
        return 0, f"❌ 【{pattern_name}格式检查失败】{jia_pos_desc}韵部不同！\n{pattern_name}要求：{jia_pos_desc}用甲韵，{yi_pos_desc}用乙韵，且甲乙韵相邻。\n检测详情：{'; '.join(format_details)}"
    
    if not yi_yun_same:
        return 0, f"❌ 【{pattern_name}格式检查失败】{yi_pos_desc}韵部不同！\n{pattern_name}要求：{jia_pos_desc}用甲韵，{yi_pos_desc}用乙韵，且甲乙韵相邻。\n检测详情：{'; '.join(format_details)}"
    
    if not jia_yi_different:
        return 0, f"❌ 【{pattern_name}格式检查失败】甲韵和乙韵相同！都是:{jia_yun_names[0]}\n{pattern_name}要求：{jia_pos_desc}用甲韵，{yi_pos_desc}用乙韵，且甲乙韵相邻。\n检测详情：{'; '.join(format_details)}"
    
    if not adjacent:
        return 0, f"❌ 【{pattern_name}格式检查失败】甲韵'{jia_yun_names[0]}'和乙韵'{yi_yun_names[0]}'不是相邻韵部！\n{pattern_name}要求：{jia_pos_desc}用甲韵，{yi_pos_desc}用乙韵，且甲乙韵相邻。\n检测详情：{'; '.join(format_details)}"
    
    # 全部通过
    allowed_yun_str = "、".join(allowed_yun_names)
    return 1, f"✅ 【检查通过】\n✅ 韵脚范围：符合平水韵{allowed_yun_str}要求\n✅ {pattern_name}格式：甲韵({jia_yun_names[0]})和乙韵({yi_yun_names[0]})为相邻韵部\n检测详情：{'; '.join(format_details)}"

def jin_tui_yun(poem_list):
    """进退韵：第2、6句用甲韵，第4、8句用乙韵"""
    return _check_yun_pattern(poem_list, "进退韵", [0, 2], [1, 3])

def lu_lu_yun(poem_list):
    """辘轳韵：第2、4句用甲韵，第6、8句用乙韵"""
    return _check_yun_pattern(poem_list, "辘轳格", [0, 1], [2, 3])


if __name__ == "__main__":
    # 测试用例1：包含多音字的诗句
    test_poems1 = [
        "春眠不觉晓，",
        "处处闻啼鸟。",
        "夜来风雨声，",
        "花落知多少。"
    ]
    
    print("=== 测试用例1：春晓 ===")
    result, msg = yayun(test_poems1)
    print(f"结果：{result}")
    print(msg)
    
    # 测试用例2：包含"藉"字的多音字测试
    test_poems2 = [
        "借问酒家何处有",
        "牧童遥指杏花村",
        "清明时节雨纷纷",
        "路上行人欲断魂"
    ]
    
    print("\n=== 测试用例2：清明 ===")
    result, msg = yayun(test_poems2)
    print(f"结果：{result}")
    print(msg)
    
    # 测试用例3：律诗偶数句押韵
    test_lvshi = [
        "白日依山尽",
        "黄河入海流",
        "欲穷千里目",
        "更上一层楼"
    ]
    
    print("\n=== 测试用例3：登鹳雀楼（律诗） ===")
    result, msg = lvshi_yayun(test_lvshi)
    print(f"结果：{result}")
    print(msg)
    
    # 测试用例4：包含多音字"藉"的测试
    test_poems3 = [
        "藉此机会表心意",
        "真情实意诉衷肠",
        "借问何时能相见",
        "思君不见下渝州"
    ]
    
    print("\n=== 测试用例4：多音字测试 ===")
    result, msg = yayun(test_poems3)
    print(f"结果：{result}")
