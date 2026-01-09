# from utils import clean_up_text
import re

# 1.检测出现鼻化元音标记（~）的单词是否在范围里
def has_nasal_vowel(range, corresponding_parts):
    """
    检测葡萄牙语鼻化元音标记的单词数是否在指定范围内
    """
    nasal_marks = ['ã', 'õ', 'ão', 'ões', 'ãe', 'ãs']
    all_issues = []
    all_parts_valid = True
    
    for i, item in enumerate(corresponding_parts):
        if not isinstance(item, str):
            continue
        
        clean_words = []
        for word in item.split():
            clean_word = ''.join(char for char in word if char.isalpha() or char in 'ãõáéíóúâêîôûàèìòùäëïöüç')
            if any(mark in clean_word.lower() for mark in nasal_marks):
                clean_words.append(clean_word)
        
        count = len(clean_words)
        
        if not (range[0] <= count <= range[1]):
            all_parts_valid = False
        
        # 修改输出格式：如果只有一项，不显示"第X项"
        if len(corresponding_parts) == 1:
            if count == 0:
                all_issues.append("0个")
            else:
                all_issues.append(f"发现符合单词{clean_words}{count}个")
        else:
            if count == 0:
                all_issues.append(f"第{i+1}项: 0个")
            else:
                all_issues.append(f"第{i+1}项: {clean_words}{count}个")
    
    if all_parts_valid:
        return 1, f"✅ 所有都符合范围{range}: {'; '.join(all_issues)}"
    else:
        return 0, f"❌ 存在不符合范围{range}: {'; '.join(all_issues)}"



#2.1检测葡萄牙语【开音】重音符号标记的单词数是否在指定范围内（整个corresponding
def has_acute_accent(range, corresponding_parts):
    
    # 合并所有内容
    all_content = ' '.join(corresponding_parts)
    
    # 葡萄牙语开音重音符号标记（acento agudo）
    acute_marks = ['á', 'é', 'í', 'ó', 'ú']
    
    words_with_acute = []
    words = all_content.split()
    
    for word in words:
        clean_word = ''.join(char for char in word if char.isalpha() or char in 'ãõáéíóúâêîôûàèìòùäëïöüç')
        if any(mark in clean_word.lower() for mark in acute_marks):
            words_with_acute.append(clean_word)  # 改为添加 clean_word
    
    acute_word_count = len(words_with_acute)
    
    if not range[0] <= acute_word_count <= range[1]:
        return 0, f"❌ 存在内容开音重音符号单词数量不匹配此range{range}: 满足条件的单词：{words_with_acute}，数量为：{str(acute_word_count)}"

    return 1, f"✅ 全部内容开音重音符号单词数量匹配范围 {range}，共 {acute_word_count} 个满足条件的单词：{words_with_acute}"


#2.2葡萄牙语【开音】重音符号标记的单词数是否在指定范围内（each
def each_has_acute_accent(range, corresponding_parts):
    acute_marks = ['á', 'é', 'í', 'ó', 'ú']
    all_issues = []
    failed_issues = []  # 只记录不满足的项
    satisfied_items = []  # 记录满足的项编号
    failed_items = []     # 记录不满足的项编号
    all_parts_valid = True
    
    for i, text in enumerate(corresponding_parts):
        if not isinstance(text, str):
            continue
        
        clean_words = []
        for word in text.split():
            clean_word = ''.join(char for char in word if char.isalpha() or char in 'ãõáéíóúâêîôûàèìòùäëïöüç')
            if any(mark in clean_word.lower() for mark in acute_marks):
                clean_words.append(clean_word)
        
        count = len(clean_words)
        
        # 判断是否符合范围
        is_valid = range[0] <= count <= range[1]
        if not is_valid:
            all_parts_valid = False
            failed_items.append(f"第{i+1}项")
            # 记录不满足的项详细信息
            if count == 0:
                word_info = f"{count}个开音重音符号单词"
            else:
                word_info = f"{count}个开音重音符号单词{clean_words}"
            failed_issues.append(f"第{i+1}项: {word_info}")
        else:
            satisfied_items.append(f"第{i+1}项")
        
        # 所有项的信息（用于成功时显示）
        if count == 0:
            word_info = f"{count}个开音重音符号单词"
        else:
            word_info = f"{count}个开音重音符号单词{clean_words}"
        all_issues.append(f"第{i+1}部分: {word_info}")
    
    if all_parts_valid:
        return 1, f"✅ 所有都符合范围{range}: {'; '.join(all_issues)}"
    else:
        # 构建新的输出格式
        failed_list = ",".join(failed_items)
        
        if satisfied_items:
            satisfied_list = ",".join(satisfied_items)
            return 0, f"❌ 存在不符合范围{range}: {satisfied_list}满足；{failed_list}不满足：{'; '.join(failed_issues)}"
        else:
            return 0, f"❌ 存在不符合范围{range}: {failed_list}不满足：{'; '.join(failed_issues)}"



#3.1检测葡萄牙语【闭音】重音符号标记的单词数是否在指定范围内（整个corresponding
def has_circumflex_accent(range, corresponding_parts):
    """
    检测葡萄牙语闭音重音符号标记的单词数是否在指定范围内
    """
    # 合并所有内容
    all_content = ' '.join(corresponding_parts)
    
    # 葡萄牙语闭音重音符号标记（acento circunflexo）
    circumflex_marks = ['â', 'ê', 'ô']
    
    words_with_circumflex = []
    words = all_content.split()
    
    for word in words:
        clean_word = ''.join(char for char in word if char.isalpha() or char in 'ãõáéíóúâêîôûàèìòùäëïöüç')
        if any(mark in clean_word.lower() for mark in circumflex_marks):
            words_with_circumflex.append(word)
    
    circumflex_word_count = len(words_with_circumflex)
    
    if not range[0] <= circumflex_word_count <= range[1]:
        return 0, f"❌ 存在内容闭音重音符号单词数量不匹配此range{range}:满足条件的单词：{words_with_circumflex}，数量为：{str(circumflex_word_count)}"

    return 1, f"✅ 全部内容闭音重音符号单词数量匹配范围 {range}，共 {circumflex_word_count} 个满足条件的单词：{words_with_circumflex}"


#3.2 葡萄牙语【闭音】重音符号标记的单词数是否在指定范围内（each 
def each_has_circumflex_accent(range, corresponding_parts):
    """
    检测葡萄牙语闭音重音符号标记的单词数是否在指定范围内
    每个部分都必须符合范围要求
    """
    # 葡萄牙语闭音重音符号标记（acento circunflexo）
    circumflex_marks = ['â', 'ê', 'ô']
    
    all_issues = []
    failed_issues = []  # 只记录不满足的项
    satisfied_items = []  # 记录满足的项编号
    failed_items = []     # 记录不满足的项编号
    all_parts_valid = True
    
    for i, text in enumerate(corresponding_parts):
        if not isinstance(text, str):
            continue
        
        clean_words_with_circumflex = []
        words = text.split()
        
        for word in words:
            clean_word = ''.join(char for char in word if char.isalpha() or char in 'ãõáéíóúâêîôûàèìòùäëïöüç')
            if any(mark in clean_word.lower() for mark in circumflex_marks):
                clean_words_with_circumflex.append(clean_word)
        
        count = len(clean_words_with_circumflex)
        
        # 判断是否符合范围
        is_valid = range[0] <= count <= range[1]
        if not is_valid:
            all_parts_valid = False
            failed_items.append(f"第{i+1}项")
            # 记录不满足的项详细信息
            if count == 0:
                word_info = f"{count}个闭音重音符号单词"
            else:
                word_info = f"{count}个闭音重音符号单词{clean_words_with_circumflex}"
            failed_issues.append(f"第{i+1}项: {word_info}")
        else:
            satisfied_items.append(f"第{i+1}项")
        
        # 所有项的信息（用于成功时显示）
        if count == 0:
            word_info = f"{count}个闭音重音符号单词"
        else:
            word_info = f"{count}个闭音重音符号单词{clean_words_with_circumflex}"
        all_issues.append(f"第{i+1}部分: {word_info}")
    
    if all_parts_valid:
        return 1, f"✅ 所有都符合范围{range}: {'; '.join(all_issues)}"
    else:
        # 构建新的输出格式
        failed_list = "、".join(failed_items)
        
        if satisfied_items:
            satisfied_list = "、".join(satisfied_items)
            return 0, f"❌ 存在不符合范围{range}: {satisfied_list}满足；{failed_list}不满足：{'; '.join(failed_issues)}"
        else:
            return 0, f"❌ 存在不符合范围{range}: {failed_list}不满足：{'; '.join(failed_issues)}"


#4.葡萄牙语双重否定 对于每个corresponding_part（以句子为单位计数）
def portuguese_double_negation(num_range, corresponding_parts):
    """
    检测每个部分中双重否定句的数量
    只计算恰好包含两个否定词的句子，排除单个否定词和多个否定词的情况
    排除两个否定词之间出现并列连词Ou、"E"
    排除两个否定词后都跟动词且中间有分句符号的情况
    """
    import re
    
    negation_words = [
        'não', 'nunca', 'jamais', 'nada', 'ninguém', 
        'nenhum', 'nenhuma', 'nenhuns', 'nenhumas', 'nem', 'mal',
        'de jeito nenhum', 'de forma alguma', 'de maneira nenhuma', 
        'de modo algum', 'em hipótese alguma', 'de modo nenhum',
        'jeito nenhum', 'modo algum', 'em tempo algum', 'em parte alguma',
        'nem sequer', 'nem um pouco', 'nem isso', 'de todo', 'nem pensar','sem','falta',
    ]
    
    # 并列连词
    coordinating_conjunctions = ['ou', 'e']
    
    # 分句分隔符
    clause_separators = [',', ';', '.', ':', '—', '–']
    
    def is_mal_as_noun(sentence, mal_match):
        """检查mal是否作为名词使用（前面有阳性冠词o或相关缩合形式）"""
        mal_start = mal_match.start()
        
        # 获取mal之前的文本
        before_mal = sentence[:mal_start].lower()
        
        # 检查阳性冠词和缩合形式：严格匹配，紧挨着mal
        patterns = [
            r'\bo\s+$',      # o + 空格 + mal
            r'\bos\s+$',     # os + 空格 + mal
            r'\bpelo\s+$',   # pelo + 空格 + mal
            r'\bpelos\s+$',  # pelos + 空格 + mal
            r'\bdo\s+$',     # do + 空格 + mal
            r'\bdos\s+$',    # dos + 空格 + mal
            r'\bno\s+$',     # no + 空格 + mal
            r'\bnos\s+$',    # nos + 空格 + mal
            r'\bao\s+$'      # ao + 空格 + mal
        ]
        
        for pattern in patterns:
            if re.search(pattern, before_mal):
                return True
        
        return False
    
    def has_conjunction_between(sentence, pos1, pos2):
        """检查两个位置之间是否有并列连词"""
        start_pos = min(pos1, pos2)
        end_pos = max(pos1, pos2)
        between_text = sentence[start_pos:end_pos].lower()
        
        for conj in coordinating_conjunctions:
            # 使用词边界确保匹配完整单词
            pattern = r'\b' + re.escape(conj) + r'\b'
            if re.search(pattern, between_text):
                return True
        return False
    
    def has_verb_after_negation(sentence, neg_end):
        """检查否定词后是否紧跟动词（考虑宾语前置倒装）"""
        after_neg = sentence[neg_end:].strip()
        
        # 葡萄牙语动词模式（考虑反身代词se）
        verb_patterns = [
            # 规则动词变位模式
            # 现在时 -AR动词
            r'^(se\s+)?\w+o\b',      # eu -o
            r'^(se\s+)?\w+as\b',     # tu -as
            r'^(se\s+)?\w+a\b',      # ele/ela -a  
            r'^(se\s+)?\w+amos\b',   # nós -amos
            r'^(se\s+)?\w+am\b',     # eles/elas -am
            
            # 现在时 -ER动词
            r'^(se\s+)?\w+es\b',     # tu -es
            r'^(se\s+)?\w+e\b',      # ele/ela -e
            r'^(se\s+)?\w+emos\b',   # nós -emos
            r'^(se\s+)?\w+em\b',     # eles/elas -em
            
            # 现在时 -IR动词
            r'^(se\s+)?\w+imos\b',   # nós -imos
            
            # 过去完成时变位模式
            # -AR 动词
            r'^(se\s+)?\w+ei\b',     # eu -ei
            r'^(se\s+)?\w+aste\b',   # tu -aste  
            r'^(se\s+)?\w+ou\b',     # ele/ela -ou
            r'^(se\s+)?\w+ámos\b',   # nós -ámos
            r'^(se\s+)?\w+astes\b',  # vós -astes
            r'^(se\s+)?\w+aram\b',   # eles/elas -aram

            # -ER 动词  
            r'^(se\s+)?\w+i\b',      # eu -i
            r'^(se\s+)?\w+este\b',   # tu -este
            r'^(se\s+)?\w+eu\b',     # ele/ela -eu
            r'^(se\s+)?\w+emos\b',   # nós -emos
            r'^(se\s+)?\w+estes\b',  # vós -estes
            r'^(se\s+)?\w+eram\b',   # eles/elas -eram

            # -IR 动词
            # r'^(se\s+)?\w+i\b',    # eu -i (与-ER重复)
            r'^(se\s+)?\w+iste\b',   # tu -iste
            r'^(se\s+)?\w+iu\b',     # ele/ela -iu
            r'^(se\s+)?\w+imos\b',   # nós -imos
            r'^(se\s+)?\w+istes\b',  # vós -istes  
            r'^(se\s+)?\w+iram\b',   # eles/elas -iram
            
            # 过去未完成时
            r'^(se\s+)?\w+ava\b',    # (se) + 动词-ava
            r'^(se\s+)?\w+esse\b',   # (se) + 动词-esse (虚拟式)
            r'^(se\s+)?\w+asse\b',   # (se) + 动词-asse (虚拟式)
            
            # 不定式动词模式
            r'^(se\s+)?\w+ar\b',     # (se) + 不定式 -ar 动词
            r'^(se\s+)?\w+er\b',     # (se) + 不定式 -er 动词
            r'^(se\s+)?\w+ir\b',     # (se) + 不定式 -ir 动词
            
            # ser 动词的所有变位形式
            # 现在时 (presente)
            r'^sou\b',               # eu sou
            r'^és\b',                # tu és  
            r'^é\b',                 # ele/ela é
            r'^somos\b',             # nós somos
            r'^sois\b',              # vós sois
            r'^são\b',               # eles/elas são
            
            # 过去未完成时 (pretérito imperfeito)
            r'^era\b',               # eu/ele/ela era
            r'^eras\b',              # tu eras
            r'^éramos\b',            # nós éramos
            r'^éreis\b',             # vós éreis
            r'^eram\b',              # eles/elas eram
            
            # 将来时 (futuro)
            r'^serei\b',             # eu serei
            r'^serás\b',             # tu serás
            r'^será\b',              # ele/ela será
            r'^seremos\b',           # nós seremos
            r'^sereis\b',            # vós sereis
            r'^serão\b',             # eles/elas serão
            
            # 常用不规则动词变位
            # dar (给)
            r'^dou\b',               # eu dou
            r'^dás\b',               # tu dás
            r'^dá\b',                # ele/ela dá
            r'^damos\b',             # nós damos
            r'^dais\b',              # vós dais
            r'^dão\b',               # eles/elas dão
            
            # dizer (说)
            r'^digo\b',              # eu digo
            r'^dizes\b',             # tu dizes
            r'^diz\b',               # ele/ela diz
            r'^dizemos\b',           # nós dizemos
            r'^dizeis\b',            # vós dizeis
            r'^dizem\b',             # eles/elas dizem
            
            # fazer (做)
            r'^faço\b',              # eu faço
            r'^fazes\b',             # tu fazes
            r'^faz\b',               # ele/ela faz
            r'^fazemos\b',           # nós fazemos
            r'^fazeis\b',            # vós fazeis
            r'^fazem\b',             # eles/elas fazem
            
            # trazer (带来)
            r'^trago\b',             # eu trago
            r'^trazes\b',            # tu trazes
            r'^traz\b',              # ele/ela traz
            r'^trazemos\b',          # nós trazemos
            r'^trazeis\b',           # vós trazeis
            r'^trazem\b',            # eles/elas trazem
            
            # 不规则动词 ir/ser 过去时
            r'^fui\b', r'^foste\b', r'^foi\b', r'^fomos\b', r'^fostes\b', r'^foram\b',

            # 不规则动词 ver 过去时
            r'^vi\b', r'^viste\b', r'^viu\b', r'^vimos\b', r'^vistes\b', r'^viram\b',
            
            # 其他常见动词
            r'^está\b',              # estar 现在时
            r'^houve\b',             # haver 过去时
        ]
        
        # 直接检查是否有动词（最严格的情况）
        for pattern in verb_patterns:
            if re.match(pattern, after_neg.lower()):
                return True
        
        # 检查宾语前置倒装情况：
        # 严格模式：介词 + 单个名词/形容词 + 动词（中间只允许空格）
        # 更严格的宾语前置模式，只匹配常见的简单结构
        object_fronting_pattern = r'^(à|ao|para|com|de|em|por|sobre|contra|entre|durante|através|na|no|da|do|pela|pelo)\s+(\w+)\s+(' + '|'.join([
            r'(se\s+)?\w+ou\b',
            r'(se\s+)?\w+iu\b', 
            r'(se\s+)?\w+eu\b',
            r'foi\b',
            r'era\b',
            r'está\b',
            r'é\b',
            r'sou\b',
            r'são\b',
            r'sucumbiu\b',
            r'resistiu\b',
            r'cedeu\b'
        ]) + r')(\s|$|[,.;!?])'

        
        # 检查是否匹配且长度合理（避免匹配过长的文本）
        match = re.match(object_fronting_pattern, after_neg.lower())
        if match and len(match.group()) <= 50:  # 限制最大长度
            return True
        
        # 检查更严格的简单宾语前置：否定词 + 代词/特定名词 + 动词
        # 只匹配常见的代词和特定名词
        simple_fronting_pattern = r'^(isso|ele|ela|eles|elas|isto|aquilo|tudo|nada|alguém|algo)\s+(' + '|'.join([
            r'(se\s+)?\w+ou\b',
            r'(se\s+)?\w+iu\b',
            r'(se\s+)?\w+eu\b',
            r'foi\b',
            r'era\b',
            r'está\b',
            r'é\b',
            r'sou\b',
            r'são\b',
            r'(se\s+)?\w+ava\b',
            r'(se\s+)?\w+esse\b',
            r'(se\s+)?\w+asse\b',
            r'houve\b'
        ]) + r')(\s|$|[,.;!?])'
        
        match = re.match(simple_fronting_pattern, after_neg.lower())
        if match:
            return True
            
        return False

    def find_verb_end_after_negation(sentence, neg_end):
        """找到否定词后动词的结束位置（考虑宾语前置倒装）"""
        after_neg = sentence[neg_end:].strip()
        
        # 直接匹配动词（包括反身代词和所有动词变位）
        direct_verb_patterns = [
            r'^(se\s+)?(\w+o|\w+as|\w+a|\w+amos|\w+am|\w+es|\w+e|\w+emos|\w+em|\w+imos|\w+ei|\w+aste|\w+ou|\w+ámos|\w+astes|\w+aram|\w+i|\w+este|\w+eu|\w+estes|\w+eram|\w+iste|\w+iu|\w+istes|\w+iram|\w+ava|\w+esse|\w+asse|\w+ar|\w+er|\w+ir|sou|és|é|somos|sois|são|era|eras|éramos|éreis|eram|serei|serás|será|seremos|sereis|serão|dou|dás|dá|damos|dais|dão|digo|dizes|diz|dizemos|dizeis|dizem|faço|fazes|faz|fazemos|fazeis|fazem|trago|trazes|traz|trazemos|trazeis|trazem|fui|foste|foi|fomos|fostes|foram|vi|viste|viu|vimos|vistes|viram|está|houve)\b'
        ]
        
        for pattern in direct_verb_patterns:
            match = re.match(pattern, after_neg.lower())
            if match:
                return neg_end + len(after_neg) - len(after_neg[match.end():])
        
        # 匹配宾语前置倒装情况（严格模式）
        object_fronting_pattern = r'^(à|ao|para|com|de|em|por|sobre|contra|entre|durante|através|na|no|da|do|pela|pelo|numa|numas|duma|dumas)\s+(o\s+|a\s+|os\s+|as\s+)?([\w]+\s+)?([\w]+)\s+((se\s+)?(\w+ou|\w+iu|\w+eu|foi|era|está|\w+ava|\w+esse|\w+asse|houve|sucumbiu|resistiu|cedeu|entregou|é|sou|são))\b'
        
        match = re.match(object_fronting_pattern, after_neg.lower())
        if match and len(match.group()) <= 50:
            # 找到动词部分的结束位置
            verb_part = match.group(5)  # 动词部分
            verb_start_in_match = match.group().rfind(verb_part.lower())
            return neg_end + verb_start_in_match + len(verb_part)
        
        # 匹配简单宾语前置（严格模式）
        simple_fronting_pattern = r'^(isso|ele|ela|eles|elas|isto|aquilo|tudo|nada|alguém|algo)\s+((se\s+)?(\w+ou|\w+iu|\w+eu|foi|era|está|\w+ava|\w+esse|\w+asse|houve|é|sou|são))\b'
        
        match = re.match(simple_fronting_pattern, after_neg.lower())
        if match:
            # 找到动词部分的结束位置
            verb_part = match.group(2)  # 动词部分
            pronoun_part = match.group(1)  # 代词部分
            return neg_end + len(pronoun_part) + 1 + len(verb_part)  # +1 for space
        
        return neg_end
    
    def has_clause_separator_between(sentence, pos1, pos2):
        """检查两个位置之间是否有分句分隔符"""
        start_pos = min(pos1, pos2)
        end_pos = max(pos1, pos2)
        between_text = sentence[start_pos:end_pos]
        
        return any(sep in between_text for sep in clause_separators)
    
    def is_independent_clauses(sentence, first_neg, second_neg):
        """检查是否为两个独立分句（两个否定词后都跟动词且中间有分句符号）"""
        # 检查两个否定词后是否都有动词（包括宾语前置情况）
        first_has_verb = has_verb_after_negation(sentence, first_neg[2])
        second_has_verb = has_verb_after_negation(sentence, second_neg[2])
        
        if first_has_verb and second_has_verb:
            # 找到第一个动词的结束位置（考虑宾语前置）
            first_verb_end = find_verb_end_after_negation(sentence, first_neg[2])
            
            # 检查第一个动词结束位置到第二个否定词开始位置之间是否有分句符号
            if has_clause_separator_between(sentence, first_verb_end, second_neg[1]):
                return True
        
        return False
    
    def find_double_negation_in_sentence(sentence):
        """在句子中查找双重否定结构，只接受恰好两个否定词的情况"""
        sentence_lower = sentence.lower()
        found_negations = []
        matched_positions = set()
        
        # 按长度降序排列，优先匹配长短语
        sorted_negation_words = sorted(negation_words, key=len, reverse=True)
        
        for neg_word in sorted_negation_words:
            if ' ' in neg_word:
                pattern = re.escape(neg_word)
            else:
                pattern = r'\b' + re.escape(neg_word) + r'\b'
            
            for match in re.finditer(pattern, sentence_lower):
                # 检查是否与已匹配的位置重叠
                match_range = set(range(match.start(), match.end()))
                if not match_range.intersection(matched_positions):
                    # 特殊处理：如果是mal，检查是否为名词用法
                    if neg_word == 'mal' and is_mal_as_noun(sentence, match):
                        continue
                    
                    found_negations.append((neg_word, match.start(), match.end()))
                    matched_positions.update(match_range)
        
        # 只接受恰好两个否定词的情况
        if len(found_negations) == 2:
            # 按位置排序
            found_negations.sort(key=lambda x: x[1])
            first_neg = found_negations[0]
            second_neg = found_negations[1]
            
            # 检查两个否定词之间是否有并列连词
            if has_conjunction_between(sentence_lower, first_neg[2], second_neg[1]):
                return None  # 有并列连词，不算双重否定
            
            # 检查是否为两个独立分句
            if is_independent_clauses(sentence, first_neg, second_neg):
                return None  # 两个独立分句，不算双重否定
            
            return f"{first_neg[0]}...{second_neg[0]}"
        
        return None
    
    all_found_structures = []
    satisfied_items = []
    failed_items = []
    not_found_items = []
    all_items_info = []  # 添加这个来记录所有项的信息
    
    for item_index, item in enumerate(corresponding_parts):
        item_double_negations = 0
        item_structures = []
        
        # 清理文本并分割句子
        cleaned_item = re.sub(r'\n+', ' ', item).strip()
        sentences = re.split(r'[.!?]+', cleaned_item)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            found_structure = find_double_negation_in_sentence(sentence)
            if found_structure:
                item_double_negations += 1
                item_structures.append(found_structure)
                all_found_structures.append(found_structure)
        
        # 判断是否通过
        is_passed = num_range[0] <= item_double_negations <= num_range[1]
        
        # 记录所有项的信息（用于全部不通过的情况）
        if item_double_negations == 0:
            all_items_info.append(f"第{item_index+1}项: 0个")
        else:
            unique_structures = list(set(item_structures))
            all_items_info.append(f"第{item_index+1}项: 数量{item_double_negations}, 结构: {', '.join(unique_structures)}")
        
        # 分类记录项目（简化版）
        if is_passed:
            if item_structures:
                unique_structures = list(set(item_structures))
                satisfied_items.append(f"✅第{item_index+1}项: 数量{item_double_negations}, 结构: {', '.join(unique_structures)}")
            else:
                satisfied_items.append(f"✅第{item_index+1}项: 数量{item_double_negations}")
        else:
            if item_double_negations == 0:
                not_found_items.append(f"第{item_index+1}项")
            else:
                unique_structures = list(set(item_structures))
                failed_items.append(f"第{item_index+1}项: 数量{item_double_negations}, 结构: {', '.join(unique_structures)}")
    
    # 返回结果
    total_count = len(all_found_structures)
    total_parts = len(corresponding_parts)
    
    # 构建输出
    if not failed_items and not not_found_items:
        # 全部通过
        detailed_info = "; ".join(satisfied_items)
        return 1, f"✅ 所有{total_parts}内容都符合要求。{detailed_info}", total_count
    elif not satisfied_items:
        # 全部不通过的情况 - 显示具体信息
        detailed_info = "; ".join(all_items_info)
        return 0, f"❌ 所有内容不符合范围{num_range}。{detailed_info}", total_count
    else:
        # 部分不通过
        output_parts = []
        
        # 添加未发现的项（整合显示）
        if not_found_items:
            not_found_list = "、".join(not_found_items)
            output_parts.append(f"❌{not_found_list}未发现正确的双重否定结构")
        
        # 添加其他失败的项
        if failed_items:
            for item in failed_items:
                output_parts.append(f"❌{item}")
        
        # 添加成功的项
        if satisfied_items:
            output_parts.extend(satisfied_items)
        
        detailed_info = "; ".join(output_parts)
        return 0, f"❌ 部分内容不符合范围{num_range}。{detailed_info}", total_count


#5.葡语日期格式验证
def portuguese_date_format(corresponding_parts):
    """
    检测葡萄牙语日期格式是否正确：日-月-年顺序
    支持格式：
    1. 数字格式：15 de julho de 2023 (日 de 月 de 年)
    2. 文字格式：primeiro de junho de dois mil e vinte (日 de 月 de 年)
    重点检查顺序：日在前，月在中，年在后
    """
    # 葡萄牙语月份（小写）
    portuguese_months = [
        'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
        'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
    ]
    
    # 葡萄牙语日期数字拼写（1-31）
    portuguese_day_numbers = [
        'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto', 'sexto', 
        'sétimo', 'oitavo', 'nono', 'décimo', 'um', 'dois', 'três', 
        'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove', 'dez',
        'onze', 'doze', 'treze', 'catorze', 'quinze', 'dezesseis',
        'dezessete', 'dezoito', 'dezenove', 'vinte', 'vinte e um',
        'vinte e dois', 'vinte e três', 'vinte e quatro', 'vinte e cinco',
        'vinte e seis', 'vinte e sete', 'vinte e oito', 'vinte e nove',
        'trinta', 'trinta e um'
    ]
    
    total_correct_dates = 0
    total_found_dates = 0
    correct_dates = []
    incorrect_dates = []
    failed_parts = []
    
    for item_index, item in enumerate(corresponding_parts):
        item_correct_count = 0
        item_total_count = 0
        item_correct_dates = []
        item_incorrect_dates = []
        
        # 清理文本
        cleaned_item = re.sub(r'\n+', ' ', item).strip()
        
        # 1. 检查正确的日-月-年格式（数字）
        # 日(1-31) de 月份 de 年份(4位数字)
        correct_numeric_pattern = r'\b([1-9]|[12][0-9]|3[01])\s+de\s+(' + '|'.join(portuguese_months) + r')\s+de\s+(\d{4})\b'
        
        correct_matches = re.findall(correct_numeric_pattern, cleaned_item.lower())
        for match in correct_matches:
            day, month, year = match
            date_str = f"{day} de {month} de {year}"
            item_correct_count += 1
            item_correct_dates.append(date_str)
            correct_dates.append(date_str)
            total_correct_dates += 1
            item_total_count += 1
            total_found_dates += 1
        
        # 2. 检查正确的日-月-年格式（文字）
        # 日期词 de 月份 de 年份表达
        day_pattern = '|'.join(portuguese_day_numbers)
        month_pattern = '|'.join(portuguese_months)
        year_text_pattern = r'(?:dois\s+mil(?:\s+e\s+(?:vinte|trinta|quarenta|cinquenta)(?:\s+e\s+(?:um|dois|três|quatro|cinco|seis|sete|oito|nove))?)?|mil\s+novecentos\s+e\s+(?:oitenta|noventa)(?:\s+e\s+(?:um|dois|três|quatro|cinco|seis|sete|oito|nove))?)'
        
        correct_text_pattern = rf'\b({day_pattern})\s+de\s+({month_pattern})\s+de\s+({year_text_pattern})\b'
        
        text_matches = re.findall(correct_text_pattern, cleaned_item.lower())
        for match in text_matches:
            day_word, month, year_phrase = match
            date_str = f"{day_word} de {month} de {year_phrase}"
            item_correct_count += 1
            item_correct_dates.append(date_str)
            correct_dates.append(date_str)
            total_correct_dates += 1
            item_total_count += 1
            total_found_dates += 1
        
        # 3. 检查错误的顺序格式
        # 错误格式1: 月-日-年 (如：julho de 15 de 2023)
        wrong_month_day_pattern = rf'\b({month_pattern})\s+de\s+([1-9]|[12][0-9]|3[01])\s+de\s+(\d{{4}})\b'
        wrong_matches1 = re.findall(wrong_month_day_pattern, cleaned_item.lower())
        
        for match in wrong_matches1:
            month, day, year = match
            wrong_date = f"{month} de {day} de {year}"
            correct_date = f"{day} de {month} de {year}"
            item_incorrect_dates.append(f"{wrong_date} (应为: {correct_date})")
            incorrect_dates.append(wrong_date)
            item_total_count += 1
            total_found_dates += 1
        
        # 错误格式2: 年-月-日 (如：2023 de julho de 15)
        wrong_year_month_pattern = rf'\b(\d{{4}})\s+de\s+({month_pattern})\s+de\s+([1-9]|[12][0-9]|3[01])\b'
        wrong_matches2 = re.findall(wrong_year_month_pattern, cleaned_item.lower())
        
        for match in wrong_matches2:
            year, month, day = match
            wrong_date = f"{year} de {month} de {day}"
            correct_date = f"{day} de {month} de {year}"
            item_incorrect_dates.append(f"{wrong_date} (应为: {correct_date})")
            incorrect_dates.append(wrong_date)
            item_total_count += 1
            total_found_dates += 1
        
        # 错误格式3: 年-日-月 (如：2023 de 15 de julho)
        wrong_year_day_pattern = rf'\b(\d{{4}})\s+de\s+([1-9]|[12][0-9]|3[01])\s+de\s+({month_pattern})\b'
        wrong_matches3 = re.findall(wrong_year_day_pattern, cleaned_item.lower())
        
        for match in wrong_matches3:
            year, day, month = match
            wrong_date = f"{year} de {day} de {month}"
            correct_date = f"{day} de {month} de {year}"
            item_incorrect_dates.append(f"{wrong_date} (应为: {correct_date})")
            incorrect_dates.append(wrong_date)
            item_total_count += 1
            total_found_dates += 1
        
        # 如果找到了日期但顺序不正确，记录失败
        if item_total_count > 0 and item_correct_count < item_total_count:
            error_info = []
            if item_correct_dates:
                error_info.append(f"正确顺序: {', '.join(item_correct_dates[:2])}")
            if item_incorrect_dates:
                error_info.append(f"错误顺序: {', '.join(item_incorrect_dates[:2])}")
            
            failed_parts.append(f"第{item_index+1}个部分: {'; '.join(error_info)}")
    
    total_parts = len(corresponding_parts)
    
    # 如果没有找到任何日期，返回成功
    if total_found_dates == 0:
        return 1, f"✅ 未发现日期表达，无需检查顺序", 0
    
    # 检查是否所有找到的日期顺序都正确
    if failed_parts:
        failed_info = "; ".join(failed_parts)
        return 0, f"❌ {len(failed_parts)}/{total_parts}部分存在日期顺序错误: {failed_info}", total_correct_dates
    else:
        # 所有日期顺序都正确
        if correct_dates:
            unique_dates = list(set(correct_dates))[:3]
            dates_examples = ", ".join(unique_dates)
            success_text = f"发现正确日期顺序: {dates_examples}"
            if len(correct_dates) > 3:
                success_text += f" 等{total_correct_dates}个"
        else:
            success_text = "未发现日期"
        
        return 1, f"✅ 所有日期顺序正确：共{total_correct_dates}个日期。{success_text}", total_correct_dates


#6.检查葡语正式数字表达
def portuguese_number_spelling(num_range, corresponding_parts):
    """
    检查葡萄牙语规范拼写数字数量是否在指定范围内
    包含整数、小数拼写、阴阳性变化和缩合形式，阿拉伯数字视为错误
    """
    import re
    
    # 基础数字词汇（不包括有阴阳性变化的）
    basic_numbers = ['zero', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove', 'dez',
                    'onze', 'doze', 'treze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 
                    'dezenove', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 
                    'oitenta', 'noventa', 'cem', 'mil', 'milhão', 'bilhão']
    
    # "um"的阴阳性和单复数变化
    um_variations = ['um', 'uma', 'uns', 'umas']
    
    # "dois"的阴阳性变化
    dois_variations = ['dois', 'duas']
    
    # "十四"的两种拼写
    fourteen_variations = ['quatorze', 'catorze']
    
    # 缩合形式
    contractions = ['dum', 'duma', 'duns', 'dumas',  # de + um/uma/uns/umas
                   'num', 'numa', 'nuns', 'numas']   # em + um/uma/uns/umas
    
    # 合并所有数字词汇
    all_number_words = basic_numbers + um_variations + dois_variations + fourteen_variations + contractions
    
    all_issues = []
    failed_items = []
    satisfied_items = []
    all_parts_valid = True
    
    for i, text in enumerate(corresponding_parts):
        if not isinstance(text, str):
            continue
        
        text_lower = text.lower()
        correct_spellings = []
        matched_positions = set()
        
        # 1. 查找复合数字（包含"um"和"dois"的变化形式）
        compound_pattern = r'\b(vinte|trinta|quarenta|cinquenta|sessenta|setenta|oitenta|noventa)\s+e\s+(um|uma|dois|duas|três|quatro|cinco|seis|sete|oito|nove)\b'
        for match in re.finditer(compound_pattern, text_lower):
            correct_spellings.append(f"{match.group(1)} e {match.group(2)}")
            matched_positions.update(range(match.start(), match.end()))
        
        # 2. 查找缩合形式
        for contraction in contractions:
            for match in re.finditer(r'\b' + re.escape(contraction) + r'\b', text_lower):
                if not any(pos in matched_positions for pos in range(match.start(), match.end())):
                    correct_spellings.append(match.group())
                    matched_positions.update(range(match.start(), match.end()))
        
        # 3. 查找单个数字词（包括所有变化形式）
        for word in all_number_words:
            for match in re.finditer(r'\b' + re.escape(word) + r'\b', text_lower):
                if not any(pos in matched_positions for pos in range(match.start(), match.end())):
                    correct_spellings.append(match.group())
                    matched_positions.update(range(match.start(), match.end()))
        
        # 4. 查找小数拼写（vírgula形式）
        decimal_pattern = r'\b([a-záàâãéêíóôõúç\s]+)\s+vírgula\s+([a-záàâãéêíóôõúç\s]+)\b'
        for match in re.finditer(decimal_pattern, text_lower):
            if not any(pos in matched_positions for pos in range(match.start(), match.end())):
                integer_part, decimal_part = match.groups()
                integer_words = integer_part.strip().split()
                decimal_words = decimal_part.strip().split()
                
                # 检查整数部分和小数部分是否包含数字词汇
                integer_valid = any(word in all_number_words for word in integer_words)
                decimal_valid = any(word in all_number_words for word in decimal_words)
                
                if integer_valid and decimal_valid:
                    correct_spellings.append(f"{integer_part.strip()} vírgula {decimal_part.strip()}")
                    matched_positions.update(range(match.start(), match.end()))
        
        # 5. 检测阿拉伯数字
        arabic_numbers = re.findall(r'\b\d+(?:[.,]\d+)?\b', text)
        
        count = len(correct_spellings)
        arabic_count = len(arabic_numbers)
        is_valid = (num_range[0] <= count <= num_range[1]) and (arabic_count == 0)
        
        if is_valid:
            satisfied_items.append(f"第{i+1}项")
        else:
            failed_items.append(f"第{i+1}项")
            all_parts_valid = False
        
        # 构建输出信息
        info_parts = []
        if count > 0:
            info_parts.append(f"拼写数字{correct_spellings}{count}个")
        else:
            info_parts.append("拼写数字0个")
            
        if arabic_count > 0:
            info_parts.append(f"阿拉伯数字{arabic_numbers}{arabic_count}个")
        
        all_issues.append(f"第{i+1}项: {'; '.join(info_parts)}")
    
    # 统一输出格式
    if all_parts_valid:
        return 1, f"✅ 所有都符合范围{num_range}: {'; '.join(all_issues)}"
    else:
        failed_list = "、".join(failed_items)
        if satisfied_items:
            satisfied_list = "、".join(satisfied_items)
            return 0, f"❌ {satisfied_list}满足；{failed_list}不满足范围{num_range}: {'; '.join([issue for j, issue in enumerate(all_issues) if f'第{j+1}项' in failed_items])}"
        else:
            return 0, f"❌ {failed_list}不满足范围{num_range}: {'; '.join([issue for j, issue in enumerate(all_issues) if f'第{j+1}项' in failed_items])}"



#7."Não"单独成句的情况
def portuguese_starts_with_nao(corresponding_parts):
    """
    判断葡萄牙语否定回答是否以"Não"开头，且用句号或逗号分隔
    """
    
    if not isinstance(corresponding_parts, list) or len(corresponding_parts) == 0:
        return False, "❌ 输入格式错误或为空"
    
    violation_items = []  # 记录不满足条件的项目编号
    
    for i, answer in enumerate(corresponding_parts):
        if not isinstance(answer, str) or not answer.strip():
            violation_items.append(f"第{i+1}项")
            continue
        
        answer = answer.strip()
        
        # 检查是否以"Não"开头且后跟句号或逗号
        if not (answer.startswith("Não") and len(answer) > 3 and answer[3] in ['.', ',']):
            violation_items.append(f"第{i+1}项")
    
    if violation_items:
        # 检查是否所有项都不满足
        if len(violation_items) == len(corresponding_parts):
            return False, f"❌ 所有{len(corresponding_parts)}个格式错误"
        else:
            # 部分不满足，列出具体项目
            items_list = "、".join(violation_items)
            return False, f"❌ {items_list}不满足Não独立成句"
    else:
        return True, f"✅ 所有{len(corresponding_parts)}个否定回答格式正确"


#8.葡语序数词缩写
def portuguese_ordinal_abbreviation(range_param, corresponding_parts):
    """
    检查每个corresponding是否包含序数词缩写格式
    支持前置名词/缩写的情况，如 Art. 4.º
    采用两步处理：先定位上标，再分析上下文
    """
    import re
    
    if not corresponding_parts:
        return 1, "✅ 输入为空，无需检查", 0
    
    # 只排除系动词
    invalid_following_words = {
        'é', 'são'
    }
    
    def get_noun_gender(word):
        """根据词尾规律判断名词性别"""
        word_lower = word.lower().strip()
        
        # 如果是多个词，取第一个实词进行判断
        words = word_lower.split()
        if len(words) > 1:
            # 跳过冠词和介词，找到实词
            skip_words = {'a', 'o', 'as', 'os', 'da', 'do', 'das', 'dos', 'na', 'no', 'nas', 'nos', 'de', 'em', 'para', 'com'}
            for w in words:
                if w not in skip_words:
                    return get_noun_gender(w)
            # 如果都是虚词，用第一个词判断
            word_lower = words[0]
        
        # 处理复数形式
        if word_lower.endswith('s'):
            if word_lower.endswith('ões'):  # comunicações, nações
                return 'ª', "阴性复数"
            elif word_lower.endswith('ãos'):  # corações, feijões  
                return 'º', "阳性复数"
            elif word_lower.endswith('es'):
                singular = word_lower[:-2]
                if singular.endswith('or'):  # professores
                    return 'º', "阳性复数"
                elif singular == 'flor':  # flores
                    return 'ª', "阴性复数"
                else:
                    # 其他-es复数，根据单数形式判断
                    return get_noun_gender(singular)
            elif word_lower.endswith('as'):  # bananas, medidas
                return 'ª', "阴性复数"
            elif word_lower.endswith('os'):  # livros, problemas
                return 'º', "阳性复数"
        
        # 特殊例外词汇
        feminine_exceptions = ['lei', 'tribo', 'vez', 'parte', 'fase', 'etapa', 'mão', 'flor', 'plataforma']
        if word_lower in feminine_exceptions:
            return 'ª', "阴性"
        
        masculine_exceptions = ['dia', 'mapa', 'planeta', 'artigo', 'poema', 'problema', 'tema', 'idioma', 'sistema']
        if word_lower in masculine_exceptions:
            return 'º', "阳性"
        
        # 以-ão结尾的规则
        if word_lower.endswith('ão'):
            # 抽象名词和动词派生名词（阴性）
            if word_lower.endswith(('ção', 'são', 'ação', 'ição', 'ução')):
                return 'ª', "阴性"
            # 具体名词（阳性）
            else:
                return 'º', "阳性"
        
        # 指示代词缩合的特殊处理
        if word_lower in ['desta', 'destas', 'nesta', 'nestas', 'dessa', 'dessas', 'nessa', 'nessas']:
            return 'ª', "阴性指示代词缩合"
        elif word_lower in ['deste', 'destes', 'neste', 'nestes', 'desse', 'desses', 'nesse', 'nesses']:
            return 'º', "阳性指示代词缩合"
        
        # 缩合冠词的特殊处理
        if word_lower in ['da', 'das']:  # de + a/as
            return 'ª', "阴性缩合冠词"
        elif word_lower in ['do', 'dos']:  # de + o/os
            return 'º', "阳性缩合冠词"
        elif word_lower in ['na', 'nas']:  # em + a/as
            return 'ª', "阴性缩合冠词"
        elif word_lower in ['no', 'nos']:  # em + o/os
            return 'º', "阳性缩合冠词"
        elif word_lower in ['pela', 'pelas']:  # por + a/as
            return 'ª', "阴性缩合冠词"
        elif word_lower in ['pelo', 'pelos']:  # por + o/os
            return 'º', "阳性缩合冠词"
        
        # 单独冠词
        if word_lower in ['a', 'as']:
            return 'ª', "阴性冠词"
        elif word_lower in ['o', 'os']:
            return 'º', "阳性冠词"
        
        # 一般规律
        if word_lower.endswith(('ade', 'ice')):
            return 'ª', "阴性"
        elif word_lower.endswith('a') and not word_lower.endswith('ma'):
            return 'ª', "阴性"
        elif word_lower.endswith(('ma', 'o')):
            return 'º', "阳性"
        elif word_lower.endswith(('l', 'r', 'n', 't', 'z')):  # 辅音结尾
            return 'º', "阳性"
        
        return None, "未知性别"
    
    # 处理每一项
    item_results = []
    total_valid_ordinals = 0
    
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        cleaned_item = re.sub(r'\n+', ' ', item).strip()
        
        # 第一步：找到所有上标位置
        ordinal_positions = list(re.finditer(r'(\d+)\.([ºª])', cleaned_item, re.IGNORECASE))
        
        item_valid_ordinals = []
        
        # 第二步：对每个位置单独分析前后文
        for ordinal_match in ordinal_positions:
            number = ordinal_match.group(1)
            symbol = ordinal_match.group(2)
            ordinal_start = ordinal_match.start()
            ordinal_end = ordinal_match.end()
            
            # 分析前置词（向前看15个字符）
            prefix_start = max(0, ordinal_start - 15)
            prefix_text = cleaned_item[prefix_start:ordinal_start]
            
            # 匹配前置词：至少2个字母的缩写词
            prefix_match = re.search(r'(\w{2,}\.?\s+)$', prefix_text)
            prefix = prefix_match.group(1).strip() if prefix_match else ""
            
            # 分析后置词（向后看20个字符）
            suffix_end = min(len(cleaned_item), ordinal_end + 20)
            suffix_text = cleaned_item[ordinal_end:suffix_end]
            
            # 只匹配紧跟在序数词后的内容
            suffix_pattern = r'^\s*(?:((?:da|do|das|dos|na|no|nas|nos|pela|pelo|pelas|pelos|deste|desta|destes|destas|neste|nesta|nestes|nestas|desse|dessa|desses|dessas|nesse|nessa|nesses|nessas)\s+))?(\w+)'
            suffix_match = re.search(suffix_pattern, suffix_text, re.IGNORECASE)
            
            article = ""
            noun = ""
            if suffix_match:
                article = suffix_match.group(1).strip() if suffix_match.group(1) else ""
                noun = suffix_match.group(2) if suffix_match.group(2) else ""
            
            # 如果没有后置内容，跳过（除非有前置词）
            if not noun and not prefix:
                continue
            
            # 如果有后置内容，检查是否是系动词
            if noun and noun.lower() in invalid_following_words:
                continue
            
            # 判断输出格式
            if prefix and noun and noun[0].isupper():
                # 有前置词且后置第一个词首字母大写 → 只输出前置部分
                complete_ordinal = f"{prefix} {number}.{symbol}"
            elif prefix and not noun:
                # 只有前置词，没有后置词
                complete_ordinal = f"{prefix} {number}.{symbol}"
            elif noun:
                # 有后置词的情况
                # 判断性别（基于实际名词或缩合冠词）
                gender_word = article if article else noun
                expected_symbol, noun_gender = get_noun_gender(gender_word)
                
                # 检查阴阳性配合
                if expected_symbol and symbol != expected_symbol:
                    continue
                
                # 输出格式：只包含序数词和紧跟的内容
                if article:
                    complete_ordinal = f"{number}.{symbol} {article} {noun}"
                else:
                    complete_ordinal = f"{number}.{symbol} {noun}"
            else:
                # 其他情况跳过
                continue
            
            item_valid_ordinals.append(complete_ordinal)
        
        item_results.append({
            'index': i,
            'ordinals': item_valid_ordinals,
            'count': len(item_valid_ordinals),
            'in_range': range_param[0] <= len(item_valid_ordinals) <= range_param[1]
        })
        total_valid_ordinals += len(item_valid_ordinals)
    
    # 判断是否只有一项
    is_single_item = len(corresponding_parts) == 1
    
    # 检查所有项是否都在范围内
    all_in_range = all(item['in_range'] for item in item_results)
    
    # 返回结果
    if is_single_item:
        # 单项特殊处理
        item = item_results[0]
        ordinals_str = "、".join(item['ordinals']) if item['ordinals'] else ""
        
        if item['in_range']:
            if item['count'] == 0:
                return 1, f"✅ 符合范围{range_param}，未发现序数词缩写", total_valid_ordinals
            else:
                return 1, f"✅ 符合范围{range_param}，数量{item['count']}，{ordinals_str}", total_valid_ordinals
        else:
            if item['count'] == 0:
                return 0, f"❌ 不符合范围{range_param}，未发现标准序数词缩写", total_valid_ordinals
            else:
                return 0, f"❌ 不符合范围{range_param}，数量{item['count']}，{ordinals_str}", total_valid_ordinals
    else:
        # 多项处理
        item_details = []
        for item in item_results:
            ordinals_str = "、".join(item['ordinals']) if item['ordinals'] else ""
            
            if item['in_range']:
                item_details.append(f"✅第{item['index']+1}项，数量{item['count']}，{ordinals_str}")
            else:
                item_details.append(f"❌第{item['index']+1}项，数量{item['count']}，{ordinals_str}")
        
        if all_in_range:
            return 1, f"✅ 符合范围{range_param}，{' '.join(item_details)}", total_valid_ordinals
        else:
            return 0, f"❌ 有内容不符合范围{range_param}，{' '.join(item_details)}", total_valid_ordinals

#9.检测同时有鼻化元音标记和软音ç的单词
def has_nasal_and_cedilla_words(range, corresponding_parts):
    """
    检测同时包含葡萄牙语鼻化元音标记（ã, õ）和软音ç的单词数是否在指定范围内
    """
    # 鼻化元音标记
    nasal_marks = ['ã', 'õ']
    # 软音符号
    cedilla_mark = 'ç'
    
    item_results = []
    all_in_range = True
    
    for i, item in enumerate(corresponding_parts):
        words_with_both = []
        words = item.split()
        
        for word in words:
            clean_word = ''.join(char for char in word if char.isalpha() or char in 'ãõáéíóúâêîôûàèìòùäëïöüç')
            clean_word_lower = clean_word.lower()
            
            # 检查是否同时包含鼻化元音和软音ç
            has_nasal = any(mark in clean_word_lower for mark in nasal_marks)
            has_cedilla = cedilla_mark in clean_word_lower
            
            if has_nasal and has_cedilla:
                words_with_both.append(word)
        
        both_marks_count = len(words_with_both)
        is_in_range = range[0] <= both_marks_count <= range[1]
        
        if not is_in_range:
            all_in_range = False
        
        item_results.append({
            'index': i,
            'words': words_with_both,
            'count': both_marks_count,
            'in_range': is_in_range
        })
    
    # 判断是否只有一项
    is_single_item = len(corresponding_parts) == 1
    
    # 返回结果
    if is_single_item:
        # 单项特殊处理
        item = item_results[0]
        words_str = "、".join(item['words']) if item['words'] else ""
        
        if item['in_range']:
            if item['count'] == 0:
                return 1, f"✅ 符合范围{range}，未发现同时含鼻化元音和软音ç的单词"
            else:
                return 1, f"✅ 符合范围{range}，数量{item['count']}，{words_str}"
        else:
            if item['count'] == 0:
                return 0, f"❌ 不符合范围{range}，未发现同时含鼻化元音和软音ç的单词"
            else:
                return 0, f"❌ 不符合范围{range}，数量{item['count']}，{words_str}"
    else:
        # 多项处理
        item_details = []
        for item in item_results:
            words_str = "、".join(item['words']) if item['words'] else ""
            
            if item['in_range']:
                item_details.append(f"✅第{item['index']+1}项，数量{item['count']}，{words_str}")
            else:
                item_details.append(f"❌第{item['index']+1}项，数量{item['count']}，{words_str}")
        
        if all_in_range:
            return 1, f"✅ 符合范围{range}，{' '.join(item_details)}"
        else:
            return 0, f"❌ 有内容不符合范围{range}，{' '.join(item_details)}"


#10.地址缩写格式
def portuguese_address_abbreviation(corresponding_parts):
    """
    检查葡萄牙语地址缩写格式：必须同时包含街道缩写和n.º
    """
    if not corresponding_parts:
        return 1, "✅ 输入为空，无需检查"
    
    all_details = []
    all_errors = []
    
    for i, item in enumerate(corresponding_parts):
        if item is None:
            item = ""
        elif not isinstance(item, str):
            item = str(item)
        
        cleaned_item = re.sub(r'\n+', ' ', item).strip()
        
        # 检查是否有街道缩写
        street_abbrs = ['Av.', 'R.', 'Pç.', 'Lg.', 'Trav.', 'Est.', 'Rod.', 'Al.']
        found_streets = [abbr for abbr in street_abbrs if abbr in cleaned_item]
        has_street = len(found_streets) > 0
        
        # 检查是否有正确的号码缩写
        has_number = 'n.º' in cleaned_item
        
        # 检查错误格式
        street_errors = ['Av ', 'R ', 'Pç ', 'Lg ', 'Trav ', 'Est ', 'Rod ', 'Al ']
        number_errors = ['nº', 'n°', 'no.', 'num.', 'nr.']
        
        found_street_errors = [err.strip() for err in street_errors if err in cleaned_item]
        found_number_errors = [err for err in number_errors if err in cleaned_item]
        
        # 生成详情信息
        item_detail = f"第{i+1}项"
        
        if found_street_errors:
            all_errors.append(f"{item_detail}街道缩写缺少句点: {found_street_errors}")
            continue
        
        if found_number_errors:
            all_errors.append(f"{item_detail}号码格式错误: {found_number_errors}（应使用n.º）")
            continue
        
        if not has_street:
            all_errors.append(f"{item_detail}缺少街道缩写")
            continue
        
        if not has_number:
            all_errors.append(f"{item_detail}缺少号码缩写n.º")
            continue
        
        # 如果都正确，记录详情
        street_info = f"街道: {found_streets}"
        number_info = "号码: n.º"
        all_details.append(f"{item_detail}✅ {street_info}, {number_info}")
    
    # 返回结果
    if all_errors:
        return 0, f"❌ 地址格式错误。{'; '.join(all_errors)}"
    else:
        return 1, f"✅ 所有地址格式正确。{'; '.join(all_details)}"
    

#11.金额格式
def portuguese_euro_format(range, corresponding_parts):
    """
    验证葡萄牙语金额表达格式规则
    格式：数字+1个空格+€
    """
    all_errors = []
    all_success_info = []
    total_correct = 0
    total_incorrect = 0
    
    expected_min, expected_max = range[0], range[1]
    
    for i, text in enumerate(corresponding_parts):
        if not isinstance(text, str):
            continue
        
        # 严格的正确格式：数字 + 1个空格 + €（支持逗号小数）
        correct_pattern = r'\b\d+(?:,\d{1,2})? €\b'
        correct_matches = re.findall(correct_pattern, text)
        
        # 查找所有错误的欧元格式
        incorrect_matches = []
        
        # 1. €符号在前面的格式（€1.200, €750等）
        euro_before_pattern = r'€\d+(?:[.,]\d+)?'
        euro_before_matches = re.findall(euro_before_pattern, text)
        incorrect_matches.extend(euro_before_matches)
        
        # 2. 数字紧接€符号（无空格）
        no_space_pattern = r'\b\d+(?:[.,]\d+)?€\b'
        no_space_matches = re.findall(no_space_pattern, text)
        incorrect_matches.extend(no_space_matches)
        
        # 3. 多个空格的格式
        multi_space_pattern = r'\b\d+(?:[.,]\d+)?\s{2,}€\b'
        multi_space_matches = re.findall(multi_space_pattern, text)
        incorrect_matches.extend(multi_space_matches)
        
        part_correct = len(correct_matches)
        part_incorrect = len(incorrect_matches)
        
        total_correct += part_correct
        total_incorrect += part_incorrect
        
        if part_incorrect > 0:
            error_examples = ', '.join(incorrect_matches)
            all_errors.append(f"第{i+1}部分: {part_incorrect}个错误格式({error_examples})")
        
        if part_correct > 0:
            correct_examples = ', '.join(correct_matches)
            all_success_info.append(f"第{i+1}部分: {part_correct}个标准格式({correct_examples})")
    
    # 检查标准格式数量是否在期望范围内
    if expected_min <= total_correct <= expected_max and total_incorrect == 0:
        return 1, f"✅ 标准格式符合要求({total_correct}个，范围{range}): {'; '.join(all_success_info)}"
    else:
        # 直接输出详情，不要前面的汇总信息
        all_issues = []
        if all_errors:
            all_issues.extend(all_errors)
        if all_success_info:
            all_issues.extend(all_success_info)
            
        return 0, f"❌ 不符合要求的格式范围{range}: {'; '.join(all_issues)}"
    
#12.检查软音ç的单词
def has_cedilla_words(range, corresponding_parts):
    """
    检测包含葡萄牙语软音ç的单词数是否在指定范围内
    """
    import re
    
    item_results = []
    all_in_range = True
    
    for i, item in enumerate(corresponding_parts):
        # 软音符号
        cedilla_mark = 'ç'
        
        words_with_cedilla = []
        # 使用正则表达式提取单词，排除标点符号
        words = re.findall(r'\b[a-zA-ZáàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]+\b', item)
        
        for word in words:
            # 检查是否包含软音ç
            if cedilla_mark in word.lower():
                words_with_cedilla.append(word)
        
        cedilla_count = len(words_with_cedilla)
        is_in_range = range[0] <= cedilla_count <= range[1]
        
        if not is_in_range:
            all_in_range = False
        
        item_results.append({
            'index': i,
            'words': words_with_cedilla,
            'count': cedilla_count,
            'in_range': is_in_range
        })
    
    # 判断是否只有一项
    is_single_item = len(corresponding_parts) == 1
    
    # 返回结果
    if is_single_item:
        # 单项特殊处理
        item = item_results[0]
        words_str = "、".join(item['words']) if item['words'] else ""
        
        if item['in_range']:
            if item['count'] == 0:
                return 1, f"✅ 符合范围{range}，未发现含软音ç的单词"
            else:
                return 1, f"✅ 符合范围{range}，数量{item['count']}，{words_str}"
        else:
            if item['count'] == 0:
                return 0, f"❌ 不符合范围{range}，未发现含软音ç的单词"
            else:
                return 0, f"❌ 不符合范围{range}，数量{item['count']}，{words_str}"
    else:
        # 多项处理
        item_details = []
        for item in item_results:
            words_str = "、".join(item['words']) if item['words'] else ""
            
            if item['in_range']:
                item_details.append(f"✅第{item['index']+1}项，数量{item['count']}，{words_str}")
            else:
                item_details.append(f"❌第{item['index']+1}项，数量{item['count']}，{words_str}")
        
        if all_in_range:
            return 1, f"✅ 符合范围{range}，{' '.join(item_details)}"
        else:
            return 0, f"❌ 有内容不符合范围{range}，{' '.join(item_details)}"

if __name__ == "__main__":
    cor = [
 "O 1.º usuário, o 2.º desenvolvedor, o 3.º operador e o 4.º fiscalizador devem garantir transparência, precisão, segurança e proteção jurídica.",
 "O 1.º sistema, o 2.º algoritmo, o 3.º modelo e o 4.º resultado exigem avaliação, supervisão, atualização, fiscalização e conformidade regulatória contínua e eficaz.",
 "O 1.º titular, o 2.º controlador, o 3.º responsável e o 4.º auditor devem assegurar integridade, confidencialidade, rastreabilidade, acessibilidade e responsabilidade legal permanente.",
 "O 1.º fornecedor, o 2.º programador, o 3.º gestor e o 4.º analista devem promover equidade, imparcialidade, eficiência, inovação e respeito à legislação vigente.",
 "O 1.º órgão, o 2.º comitê, o 3.º conselho e o 4.º representante devem fiscalizar, regulamentar, deliberar, monitorar e garantir conformidade ética e legal absoluta."
]
    print(portuguese_ordinal_abbreviation([4,4],cor))