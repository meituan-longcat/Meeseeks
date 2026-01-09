"""
special_ru.py - 俄语语言规则检测模块
版本: 3.0.0 (优化版)
作者: AI Assistant
日期: 2024

优化要点:
1. 统一的库加载和缓存机制
2. 减少重复代码
3. 每个规则独立完整（方便单独修改）
4. 统一的错误处理和日志
5. 性能优化（缓存、正则预编译）
"""




import re
import json
import os
import inspect
from collections import defaultdict
from functools import lru_cache
try:
    import pymorphy2
    pymorphy2_AVAILABLE = True
except ImportError:
    pymorphy2_AVAILABLE = False
    print("pymorphy2库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymorphy2", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("pymorphy2库安装成功，正在导入...")
        import pymorphy2
        pymorphy2_AVAILABLE = True
        print("✅ pymorphy2库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install pymorphy2")
        pymorphy2_AVAILABLE = False

try:
    import russtress
    russtress_AVAILABLE = True
    print("✅ russtress库已存在")
except ImportError:
    russtress_AVAILABLE = False
    print("russtress库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        
        # 同时安装 russtress 和精确版本的 NumPy
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "russtress",
            "numpy==1.25.0",  # 精确锁定为 1.25.0
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        
        print("russtress库安装成功，正在导入...")
        import russtress
        import numpy as np
        russtress_AVAILABLE = True
        print(f"✅ russtress库已成功导入")
        print(f"✅ NumPy 版本: {np.__version__}")
        
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install russtress numpy==1.25.0")
        russtress_AVAILABLE = False



try:
    import tensorflow
    tensorflow_AVAILABLE = True
except ImportError:
    tensorflow_AVAILABLE = False
    print("tensorflow库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("tensorflow库安装成功，正在导入...")
        import tensorflow
        tensorflow_AVAILABLE = True
        print("✅ tensorflow库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install tensorflow")
        tensorflow_AVAILABLE = False
# ==================== 版本标记 ====================
__VERSION__ = "3.0.0"

# ==================== 兼容性修复 ====================
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec


# ==================== 全局库管理器（统一管理外部依赖） ====================
class LibraryManager:
    """统一管理 Pymorphy2 和 Russtress 的加载和缓存"""
    
    _morph = None
    _morph_available = None
    _stresser = None
    _stresser_available = None
    
    @classmethod
    def get_morph(cls):
        """获取 Pymorphy2 分析器（延迟加载+缓存）"""
        if cls._morph_available is None:
            try:
                import pymorphy2
                cls._morph = pymorphy2.MorphAnalyzer()
                cls._morph_available = True
            except ImportError:
                cls._morph = None
                cls._morph_available = False
            except Exception as e:
                print(f"[ERROR] Pymorphy2 加载失败: {e}")
                cls._morph = None
                cls._morph_available = False
        
        return cls._morph, cls._morph_available
    
    @classmethod
    def get_stresser(cls):
        """获取 Russtress 重音标注器（延迟加载+缓存）"""
        if cls._stresser_available is None:
            try:
                os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
                os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
                
                import tensorflow as tf
                if hasattr(tf, 'compat') and hasattr(tf.compat, 'v1'):
                    tf.compat.v1.disable_eager_execution()
                
                import russtress
                accent_marker = russtress.Accent()
                
                class StresserWrapper:
                    def __init__(self, marker):
                        self.marker = marker
                    def stress(self, text):
                        result = self.marker.put_stress(text)
                        return result[0] if isinstance(result, list) and result else text
                
                cls._stresser = StresserWrapper(accent_marker)
                cls._stresser_available = True
            except Exception:
                cls._stresser = None
                cls._stresser_available = False
        
        return cls._stresser, cls._stresser_available


# ==================== 通用工具函数（所有规则共用） ====================
def create_logger(debug=False):
    """创建统一的日志函数"""
    def log(message):
        if debug:
            print(message)
    return log


def extract_russian_words(text):
    """提取俄语单词"""
    return re.findall(r'\b[а-яёА-ЯЁ]+\b', text)


def parse_keywords(keywords):
    """解析关键词参数（支持多种格式）"""
    if not keywords:
        return []
    
    if isinstance(keywords, list):
        return keywords
    
    if isinstance(keywords, str):
        keywords = keywords.strip()
        
        if keywords.startswith('[') and keywords.endswith(']'):
            try:
                parsed = json.loads(keywords)
                if isinstance(parsed, list):
                    return [str(k).strip() for k in parsed]
            except json.JSONDecodeError:
                try:
                    inner = keywords[1:-1]
                    return [item.strip().strip('"\'') for item in inner.split(',') if item.strip()]
                except:
                    pass
        
        if ',' in keywords:
            return [k.strip() for k in keywords.split(',') if k.strip()]
        
        return [keywords]
    
    return [str(keywords)]


# ==================== 规则 1: 俄语重音变义词检测 ====================
def rus_stress_homonym_usage(content_list, target_word, required_count):
    """
    俄语重音变义词检测规则（基于语义判断）
    
    检测文本中是否正确使用了重音变义词的不同语义形式。
    由于俄语文本通常不标注重音，本规则主要通过语义上下文判断。
    
    Args:
        content_list: 文本内容列表
        target_word: 目标重音变义词（无重音版本）
        required_count: 要求的不同语义类型数量
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    # 输入验证
    if not isinstance(content_list, list):
        return 0, "❌ content is not a list format"
    
    if not content_list:
        return 0, "❌ content list is empty"
    
    # ✅ 清理 target_word 中可能存在的重音符号
    target_word = target_word.replace('́', '')
    
    combined_text = ' '.join(content_list)
    
    # 步骤1: 检测关键词是否存在
    word_result = _stress_detect_target_word(combined_text, target_word)
    if word_result[0] == 0:
        return word_result
    
    # 步骤2: 提取所有关键词出现位置（包括带重音和不带重音的）
    all_matches = _stress_find_all_occurrences(combined_text, target_word)
    
    if not all_matches:
        return 0, f"❌ 未找到关键词'{target_word}'的任何出现"
    
    # 步骤3: 分析每个出现位置的语义
    semantic_result = _stress_analyze_all_semantics(
        combined_text, target_word, required_count, all_matches
    )
    
    return semantic_result


def _stress_detect_target_word(text, target_word):
    """步骤1: 检测关键词是否存在"""
    # 清理重音符号
    clean_target = target_word.replace('́', '')
    
    # 匹配不带重音的基础形式
    basic_pattern = re.compile(r'\b' + re.escape(clean_target) + r'\b', re.IGNORECASE)
    basic_matches = basic_pattern.findall(text.lower())
    
    # 匹配带重音的变体
    stress_variants = _stress_get_variants(clean_target)
    stress_matches = []
    
    for variant in stress_variants:
        variant_pattern = re.compile(r'\b' + re.escape(variant) + r'\b', re.IGNORECASE)
        stress_matches.extend(variant_pattern.findall(text))
    
    total = len(basic_matches) + len(stress_matches)
    
    if total == 0:
        return 0, f"❌ 未找到关键词'{target_word}'"
    
    return 1, f"✅ 找到关键词'{target_word}' {total}次"


def _stress_find_all_occurrences(text, target_word):
    """步骤2: 查找所有出现位置（不带重音和带重音的都找）"""
    clean_target = target_word.replace('́', '')
    all_matches = []
    
    # 查找不带重音的基础形式
    basic_pattern = re.compile(r'\b' + re.escape(clean_target) + r'\b', re.IGNORECASE)
    for match in basic_pattern.finditer(text):
        all_matches.append({
            'word': match.group(),
            'start': match.start(),
            'end': match.end(),
            'has_stress_mark': False
        })
    
    # 查找带重音的变体
    stress_variants = _stress_get_variants(clean_target)
    for variant in stress_variants:
        variant_pattern = re.compile(r'\b' + re.escape(variant) + r'\b')
        for match in variant_pattern.finditer(text):
            all_matches.append({
                'word': match.group(),
                'start': match.start(),
                'end': match.end(),
                'has_stress_mark': True,
                'variant': variant
            })
    
    # 按位置排序并去重
    all_matches.sort(key=lambda x: x['start'])
    
    # 去除重复位置（如果同一位置既有带重音又有不带重音的匹配）
    unique_matches = []
    seen_positions = set()
    for match in all_matches:
        if match['start'] not in seen_positions:
            unique_matches.append(match)
            seen_positions.add(match['start'])
    
    return unique_matches


def _stress_find_sentence(text, start_pos, end_pos):
    """提取包含关键词的完整句子"""
    # 定义句子结束标记
    sentence_endings = '.!?。！？\n'
    
    # 向前查找句子开始
    sentence_start = start_pos
    for i in range(start_pos - 1, -1, -1):
        if text[i] in sentence_endings:
            sentence_start = i + 1
            break
        if i == 0:
            sentence_start = 0
    
    # 向后查找句子结束
    sentence_end = end_pos
    for i in range(end_pos, len(text)):
        if text[i] in sentence_endings:
            sentence_end = i + 1
            break
        if i == len(text) - 1:
            sentence_end = len(text)
    
    # 提取并清理句子
    sentence = text[sentence_start:sentence_end].strip()
    return sentence


def _stress_analyze_all_semantics(text, target_word, required_count, all_matches):
    """步骤3: 分析所有出现位置的语义"""
    clean_target = target_word.replace('́', '')
    
    # 检查是否是已知的重音变义词
    semantic_categories = _stress_get_semantic_categories(clean_target)
    if not semantic_categories:
        return 0, f"❌ '{target_word}'不是已知的重音变义词"
    
    semantic_results = []
    
    for match_info in all_matches:
        start = match_info['start']
        end = match_info['end']
        word = match_info['word']
        
        # 提取包含关键词的完整句子
        sentence = _stress_find_sentence(text, start, end)
        
        # 提取上下文用于语义分析
        context = text[max(0, start-150):min(len(text), end+150)].lower()
        
        # 分析语义
        semantic_type = _stress_analyze_context(context, word, clean_target, semantic_categories)
        
        semantic_results.append({
            'word': word,
            'sentence': sentence,
            'semantic': semantic_type
        })
    
    # 统计不同的语义类型（排除 unknown）
    unique_semantics = set(result['semantic'] for result in semantic_results if result['semantic'] != 'unknown')
    
    # 生成输出信息
    output_lines = []
    output_lines.append(f"关键词'{target_word}'共出现 {len(all_matches)} 次：")
    
    for i, result in enumerate(semantic_results, 1):
        output_lines.append(f"\n【第{i}次】{result['word']}")
        output_lines.append(f"句子：{result['sentence']}")
    
    # 判断结果
    output_lines.append("")
    if len(unique_semantics) >= required_count:
        output_lines.append(f"✅ 符合题目要求")
        return 1, "\n".join(output_lines)
    else:
        output_lines.append(f"❌ 不符合题目要求")
        return 0, "\n".join(output_lines)


def _stress_get_variants(target_word):
    """获取重音变义词变体"""
    # ✅ 清理重音符号
    clean_word = target_word.replace('́', '')
    
    db = {
        # 单数形式
        "атлас": ["а́тлас", "атла́с"],
        "мука": ["му́ка", "мука́"],
        "замок": ["за́мок", "замо́к"],
        "орган": ["о́рган", "орга́н"],
        "хлопок": ["хло́пок", "хлопо́к"],
        "стрелка": ["стре́лка", "стрелка́"],
        "полка": ["по́лка", "полка́"],
        "пили": ["пи́ли", "пили́"],
        "парить": ["па́рить", "пари́ть"],
        "пропасть": ["про́пасть", "пропа́сть"],
        
        # 复数/变格形式
        "часы": ["часы́", "ча́сы"],
        "кружки": ["кру́жки", "кружки́"],
        "стрелки": ["стре́лки", "стрелки́"],
        "полки": ["по́лки", "полки́"],
        
        # 变格形式补充
        "атласа": ["а́тласа", "атла́са"],
        "муки": ["му́ки", "муки́"],
        "замка": ["за́мка", "замка́"],
        "органа": ["о́ргана", "орга́на"],
        "хлопка": ["хло́пка", "хлопка́"],
        "стрелку": ["стре́лку", "стрелку́"],
        "стрелкой": ["стре́лкой", "стрелко́й"],
    }
    
    return db.get(clean_word, [])


def _stress_get_semantic_categories(target_word):
    """获取特定词的语义类别"""
    clean_word = target_word.replace('́', '')
    
    semantic_map = {
        "атлас": ['geography', 'fabric'],
        "мука": ['flour', 'suffering'],
        "замок": ['castle', 'lock'],
        "орган": ['anatomy', 'instrument'],
        "хлопок": ['cotton', 'clap'],
        "стрелка": ['pointer', 'shooter'],
        "полка": ['shelf', 'regiment'],
        "пили": ['drink_past', 'saw_past'],
        "парить": ['soar', 'steam'],
        "пропасть": ['abyss', 'disappear'],
        "часы": ['device', 'duration'],
        "кружки": ['cup', 'circle'],
        "стрелки": ['pointer', 'shooter'],
        "полки": ['shelf', 'regiment'],
    }
    
    return semantic_map.get(clean_word, [])


def _stress_analyze_context(context, variant, base_word, valid_categories):
    """分析语义语境（只返回该词的有效语义类型）"""
    indicators = {
        # атлас
        'geography': ['карта', 'география', 'страна', 'город', 'путешествие', 'мир', 'континент', 'глобус'],
        'fabric': ['ткань', 'материал', 'одежда', 'платье', 'шелк', 'блестящий', 'гладкий'],
        
        # мука
        'flour': ['хлеб', 'тесто', 'выпечка', 'готовить', 'ингредиент', 'мешок', 'пшеничн', 'печь'],
        'suffering': ['боль', 'страдание', 'мучение', 'трудно', 'тяжело', 'терпеть', 'испытание', 'проблема'],
        
        # замок
        'castle': ['дворец', 'крепость', 'средневековый', 'история', 'музей', 'башня', 'стена', 'символ', 'единство', 'построить', 'укрепить', 'крепкий', 'старинный', 'исторические места'],
        'lock': ['ключ', 'дверь', 'сейф', 'безопасность', 'закрыть', 'открыть', 'запер', 'замкнут', 'замок на'],
        
        # орган
        'anatomy': ['тело', 'здоровье', 'врач', 'медицина', 'операция', 'внутренний', 'организм', 'функция'],
        'instrument': ['музыка', 'церковь', 'концерт', 'играть', 'звук', 'клавиши', 'исполн', 'мелодия'],
        
        # хлопок
        'cotton': ['ткань', 'растение', 'поле', 'одежда', 'текстиль', 'волокно', 'урожай', 'выращива'],
        'clap': ['звук', 'хлопать', 'удар', 'ладони', 'аплодисменты', 'хлопну', 'громко'],
        
        # стрелка
        'pointer': ['указывать', 'направление', 'часы', 'циферблат', 'компас', 'показывать', 'стрелки', 'время', 'путь'],
        'shooter': ['стрелять', 'охотник', 'лучник', 'меткий', 'цель', 'оружие', 'выстрел', 'попадание'],
        
        # полка/полки
        'shelf': ['книги', 'мебель', 'хранить', 'стена', 'шкаф', 'вещи', 'стоят', 'лежат'],
        'regiment': ['армия', 'войско', 'военный', 'солдат', 'командир', 'строй', 'батальон', 'рота'],
        
        # часы
        'device': ['циферблат', 'стрелки', 'время', 'механизм', 'наручные', 'настенные', 'тикают', 'показывают', 'часы'],
        'duration': ['час', 'минут', 'долго', 'продолжительность', 'период', 'длительность', 'несколько часов'],
        
        # пили
        'drink_past': ['пить', 'чай', 'кофе', 'вода', 'напиток', 'вчера', 'выпи', 'пьян'],
        'saw_past': ['пилить', 'дрова', 'дерево', 'инструмент', 'распилить', 'бревно', 'доски'],
        
        # парить
        'soar': ['летать', 'небо', 'высоко', 'птица', 'воздух', 'парение', 'взлет', 'облака'],
        'steam': ['готовить', 'пар', 'кастрюля', 'овощи', 'варить', 'паровой', 'кипят'],
        
        # пропасть
        'abyss': ['глубокий', 'бездна', 'пропасть', 'обрыв', 'край', 'упасть', 'глубина'],
        'disappear': ['исчезнуть', 'потеряться', 'пропасть', 'исчез', 'не найти', 'куда-то'],
        
        # кружки
        'cup': ['чай', 'кофе', 'пить', 'посуда', 'керамическ', 'фарфор', 'напиток'],
        'circle': ['клуб', 'группа', 'занятия', 'интерес', 'секция', 'кружок', 'студия']
    }
    
    # ✅ 只计算该词有效的语义类型
    scores = {}
    for category in valid_categories:
        if category in indicators:
            keywords = indicators[category]
            score = sum(1 for kw in keywords if kw in context)
            if score > 0:
                scores[category] = score
    
    # 如果没有匹配，返回 unknown
    if not scores:
        return 'unknown'
    
    # 返回得分最高的语义类型
    return max(scores, key=scores.get)



# ==================== 规则 2: 评价性后缀名词检测 ====================
def detect_russian_evaluative_nouns_contextual(content_list, required_count, target_suffixes=None):
    """
    基于语境的俄语评价性后缀名词检测
    
    特点:
    1. 排除生造词和拟词
    2. 根据语境判断词汇的实际意义
    3. 只识别真实存在且有实际评价意义的词汇
    4. 精确匹配指定后缀
    
    Args:
        content_list: 待检测的文本内容
        required_count: 要求的最小数量  
        target_suffixes: 目标后缀列表
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    # 输入验证
    if content_list == "INVALID" or content_list is None:
        return 0, "❌ 输入文本无效"
    
    try:
        required_count = int(required_count)
    except (ValueError, TypeError):
        return 0, f"❌ required_count 必须是整数: '{required_count}'"

    # 文本预处理
    if isinstance(content_list, list):
        text = ' '.join(str(item) for item in content_list if item and str(item) != "INVALID")
    else:
        text = str(content_list)
    
    if not text.strip():
        return 1 if required_count <= 0 else 0, "✅ 内容为空" if required_count <= 0 else "❌ 内容为空"
    
    # 处理目标后缀
    target_suffixes = _eval_normalize_suffixes(target_suffixes)

    try:
        # 真实词汇库
        AUTHENTIC_WORDS = _eval_get_word_database()
        
        # 排除词
        EXCLUDED = _eval_get_excluded_words()
        
        # 根据后缀筛选
        if target_suffixes == "all":
            target_words = AUTHENTIC_WORDS
        else:
            target_words = {w: info for w, info in AUTHENTIC_WORDS.items() 
                          if info['suffix'] in target_suffixes}
        
        # 提取词汇
        found = []
        text_words = re.findall(r'[а-яёА-ЯЁ]+', text.lower())
        
        for word in text_words:
            if word in EXCLUDED:
                continue
            
            if word in target_words:
                info = target_words[word]
                if _eval_validate_context(word, info, text):
                    display = f"{word}{info['suffix']}"
                    found.append({'display': display, 'word': word, 'info': info})
        
        # 去重
        unique = []
        seen = set()
        for item in found:
            if item['display'] not in seen:
                unique.append(item['display'])
                seen.add(item['display'])
        
        total = len(unique)
        
        # 结果
        suffix_desc = "评价性后缀" if target_suffixes == "all" else "、".join(target_suffixes) + "后缀"
        
        if total >= required_count:
            return 1, f"✅ 找到 {total} 个带{suffix_desc}的真实评价性名词 (要求≥{required_count}个): {unique}"
        else:
            return 0, f"❌ 只找到 {total} 个带{suffix_desc}的真实评价性名词 (要求≥{required_count}个): {unique}"
    
    except Exception as e:
        return 0, f"❌ 函数执行异常: {e}"


def _eval_normalize_suffixes(suffixes):
    """标准化后缀"""
    if suffixes is None:
        return "all"
    
    if isinstance(suffixes, str):
        if suffixes.startswith('[') and suffixes.endswith(']'):
            try:
                import ast
                suffixes = ast.literal_eval(suffixes)
            except:
                suffixes = [suffixes.strip('[]"\'')]
        else:
            suffixes = [suffixes]
    
    if suffixes != "all":
        return [f"-{s}" if not s.startswith('-') else s for s in suffixes]
    
    return suffixes


def _eval_get_word_database():
    """评价性词汇数据库"""
    return {
        # -ик 后缀（指小爱称）
        'домик': {'suffix': '-ик', 'base': 'дом', 'meaning': '小房子', 'evaluation': 'diminutive_affectionate'},
        'котик': {'suffix': '-ик', 'base': 'кот', 'meaning': '小猫咪', 'evaluation': 'diminutive_affectionate'},
        'песик': {'suffix': '-ик', 'base': 'пёс', 'meaning': '小狗狗', 'evaluation': 'diminutive_affectionate'},
        'дворик': {'suffix': '-ик', 'base': 'двор', 'meaning': '小院子', 'evaluation': 'diminutive_affectionate'},
        'садик': {'suffix': '-ик', 'base': 'сад', 'meaning': '小花园', 'evaluation': 'diminutive_affectionate'},
        'столик': {'suffix': '-ик', 'base': 'стол', 'meaning': '小桌子', 'evaluation': 'diminutive_affectionate'},
        'носик': {'suffix': '-ик', 'base': 'нос', 'meaning': '小鼻子', 'evaluation': 'diminutive_affectionate'},
        'ротик': {'suffix': '-ик', 'base': 'рот', 'meaning': '小嘴巴', 'evaluation': 'diminutive_affectionate'},
        'лучик': {'suffix': '-ик', 'base': 'луч', 'meaning': '小光束', 'evaluation': 'diminutive_affectionate'},
        'цветик': {'suffix': '-ик', 'base': 'цвет', 'meaning': '小花朵', 'evaluation': 'diminutive_affectionate'},
        'листик': {'suffix': '-ик', 'base': 'лист', 'meaning': '小叶子', 'evaluation': 'diminutive_affectionate'},
        'дождик': {'suffix': '-ик', 'base': 'дождь', 'meaning': '小雨', 'evaluation': 'diminutive_affectionate'},
        'ветерик': {'suffix': '-ик', 'base': 'ветер', 'meaning': '微风', 'evaluation': 'diminutive_affectionate'},
        'мостик': {'suffix': '-ик', 'base': 'мост', 'meaning': '小桥', 'evaluation': 'diminutive_affectionate'},
        'холмик': {'suffix': '-ик', 'base': 'холм', 'meaning': '小山丘', 'evaluation': 'diminutive_affectionate'},
        'шарик': {'suffix': '-ик', 'base': 'шар', 'meaning': '小球', 'evaluation': 'diminutive_affectionate'},
        'кубик': {'suffix': '-ик', 'base': 'куб', 'meaning': '小方块', 'evaluation': 'diminutive_affectionate'},
        'ключик': {'suffix': '-ик', 'base': 'ключ', 'meaning': '小钥匙', 'evaluation': 'diminutive_affectionate'},
        'братик': {'suffix': '-ик', 'base': 'брат', 'meaning': '小弟弟', 'evaluation': 'diminutive_affectionate'},
        'хвостик': {'suffix': '-ик', 'base': 'хвост', 'meaning': '小尾巴', 'evaluation': 'diminutive_affectionate'},
        'зайчик': {'suffix': '-ик', 'base': 'заяц', 'meaning': '小兔子', 'evaluation': 'diminutive_affectionate'},
        'пальчик': {'suffix': '-ик', 'base': 'палец', 'meaning': '小手指', 'evaluation': 'diminutive_affectionate'},
        'глазик': {'suffix': '-ик', 'base': 'глаз', 'meaning': '小眼睛', 'evaluation': 'diminutive_affectionate'},
        'ушик': {'suffix': '-ик', 'base': 'ухо', 'meaning': '小耳朵', 'evaluation': 'diminutive_affectionate'},
        
        # -ок 后缀（指小）
        'лесок': {'suffix': '-ок', 'base': 'лес', 'meaning': '小树林', 'evaluation': 'diminutive_affectionate'},
        'городок': {'suffix': '-ок', 'base': 'город', 'meaning': '小城镇', 'evaluation': 'diminutive_affectionate'},
        'уголок': {'suffix': '-ок', 'base': 'угол', 'meaning': '小角落', 'evaluation': 'diminutive_affectionate'},
        'голосок': {'suffix': '-ок', 'base': 'голос', 'meaning': '小嗓音', 'evaluation': 'diminutive_affectionate'},
        'сынок': {'suffix': '-ок', 'base': 'сын', 'meaning': '儿子（爱称）', 'evaluation': 'diminutive_affectionate'},
        'дружок': {'suffix': '-ок', 'base': 'друг', 'meaning': '小朋友', 'evaluation': 'diminutive_affectionate'},
        'ветерок': {'suffix': '-ок', 'base': 'ветер', 'meaning': '微风', 'evaluation': 'diminutive_affectionate'},
        'лужок': {'suffix': '-ок', 'base': 'луг', 'meaning': '小草地', 'evaluation': 'diminutive_affectionate'},
        'снежок': {'suffix': '-ок', 'base': 'снег', 'meaning': '小雪花', 'evaluation': 'diminutive_affectionate'},
        'стишок': {'suffix': '-ок', 'base': 'стих', 'meaning': '小诗', 'evaluation': 'diminutive_affectionate'},
        'листок': {'suffix': '-ок', 'base': 'лист', 'meaning': '叶子', 'evaluation': 'diminutive_neutral'},
        'цветок': {'suffix': '-ок', 'base': 'цвет', 'meaning': '花朵', 'evaluation': 'diminutive_neutral'},
        'платок': {'suffix': '-ок', 'base': 'плат', 'meaning': '手帕', 'evaluation': 'diminutive_neutral'},
        'клубок': {'suffix': '-ок', 'base': 'клуб', 'meaning': '线团', 'evaluation': 'diminutive_neutral'},
        'мешок': {'suffix': '-ок', 'base': 'мех', 'meaning': '袋子', 'evaluation': 'diminutive_neutral'},
        'пирожок': {'suffix': '-ок', 'base': 'пирог', 'meaning': '小馅饼', 'evaluation': 'diminutive_affectionate'},
        'творожок': {'suffix': '-ок', 'base': 'творог', 'meaning': '小奶渣', 'evaluation': 'diminutive_affectionate'},
        'медок': {'suffix': '-ок', 'base': 'мёд', 'meaning': '小蜜糖', 'evaluation': 'diminutive_affectionate'},
        'теремок': {'suffix': '-ок', 'base': 'терем', 'meaning': '小木屋', 'evaluation': 'diminutive_affectionate'},
        
        # -ёк 后缀
        'огонёк': {'suffix': '-ёк', 'base': 'огонь', 'meaning': '小火光', 'evaluation': 'diminutive_affectionate'},
        'денёк': {'suffix': '-ёк', 'base': 'день', 'meaning': '小日子', 'evaluation': 'diminutive_affectionate'},
        'ручеёк': {'suffix': '-ёк', 'base': 'ручей', 'meaning': '小溪', 'evaluation': 'diminutive_affectionate'},
        'мотылёк': {'suffix': '-ёк', 'base': 'мотыль', 'meaning': '小蛾子', 'evaluation': 'diminutive_affectionate'},
        'пузырёк': {'suffix': '-ёк', 'base': 'пузырь', 'meaning': '小泡泡', 'evaluation': 'diminutive_affectionate'},
        'уголёк': {'suffix': '-ёк', 'base': 'уголь', 'meaning': '小煤炭', 'evaluation': 'diminutive_affectionate'},
        'паренёк': {'suffix': '-ёк', 'base': 'парень', 'meaning': '小伙子', 'evaluation': 'diminutive_affectionate'},
        
        # -ек 后缀
        'камешек': {'suffix': '-ек', 'base': 'камень', 'meaning': '小石头', 'evaluation': 'diminutive_affectionate'},
        'цветочек': {'suffix': '-ек', 'base': 'цветок', 'meaning': '小花朵', 'evaluation': 'diminutive_affectionate'},
        'кусочек': {'suffix': '-ек', 'base': 'кусок', 'meaning': '小块', 'evaluation': 'diminutive_affectionate'},
        'листочек': {'suffix': '-ек', 'base': 'листок', 'meaning': '小叶子', 'evaluation': 'diminutive_affectionate'},
        'мешочек': {'suffix': '-ек', 'base': 'мешок', 'meaning': '小袋子', 'evaluation': 'diminutive_affectionate'},
        'платочек': {'suffix': '-ек', 'base': 'платок', 'meaning': '小手帕', 'evaluation': 'diminutive_affectionate'},
        'комочек': {'suffix': '-ек', 'base': 'комок', 'meaning': '小团', 'evaluation': 'diminutive_affectionate'},
        'орешек': {'suffix': '-ек', 'base': 'орех', 'meaning': '小坚果', 'evaluation': 'diminutive_affectionate'},
        'горошек': {'suffix': '-ек', 'base': 'горох', 'meaning': '豌豆', 'evaluation': 'diminutive_neutral'},
        'человечек': {'suffix': '-ек', 'base': 'человек', 'meaning': '小人', 'evaluation': 'diminutive_affectionate'},
        'воробышек': {'suffix': '-ек', 'base': 'воробей', 'meaning': '小麻雀', 'evaluation': 'diminutive_affectionate'},
        
        # -ишк 后缀
        'братишка': {'suffix': '-ишк', 'base': 'брат', 'meaning': '小兄弟', 'evaluation': 'diminutive_familiar'},
        'парнишка': {'suffix': '-ишк', 'base': 'парень', 'meaning': '小伙子', 'evaluation': 'diminutive_familiar'},
        'домишко': {'suffix': '-ишк', 'base': 'дом', 'meaning': '破房子', 'evaluation': 'diminutive_pejorative'},
        'городишко': {'suffix': '-ишк', 'base': 'город', 'meaning': '小破城', 'evaluation': 'diminutive_pejorative'},
        'мальчишка': {'suffix': '-ишк', 'base': 'мальчик', 'meaning': '小男孩', 'evaluation': 'diminutive_familiar'},
        'девчишка': {'suffix': '-ишк', 'base': 'девочка', 'meaning': '小女孩', 'evaluation': 'diminutive_familiar'},
        
        # -очка/-ечка/-ичка 后缀
        'мамочка': {'suffix': '-очка', 'base': 'мама', 'meaning': '妈妈（爱称）', 'evaluation': 'diminutive_affectionate'},
        'папочка': {'suffix': '-очка', 'base': 'папа', 'meaning': '爸爸（爱称）', 'evaluation': 'diminutive_affectionate'},
        'звёздочка': {'suffix': '-очка', 'base': 'звезда', 'meaning': '小星星', 'evaluation': 'diminutive_affectionate'},
        'лампочка': {'suffix': '-очка', 'base': 'лампа', 'meaning': '小灯泡', 'evaluation': 'diminutive_neutral'},
        'веточка': {'suffix': '-очка', 'base': 'ветка', 'meaning': '小树枝', 'evaluation': 'diminutive_affectionate'},
        'ленточка': {'suffix': '-очка', 'base': 'лента', 'meaning': '小丝带', 'evaluation': 'diminutive_affectionate'},
        'кошечка': {'suffix': '-ечка', 'base': 'кошка', 'meaning': '小猫咪', 'evaluation': 'diminutive_affectionate'},
        'семечка': {'suffix': '-ечка', 'base': 'семя', 'meaning': '小种子', 'evaluation': 'diminutive_neutral'},
        'овечка': {'suffix': '-ечка', 'base': 'овца', 'meaning': '小绵羊', 'evaluation': 'diminutive_affectionate'},
        'птичка': {'suffix': '-ичка', 'base': 'птица', 'meaning': '小鸟', 'evaluation': 'diminutive_affectionate'},
        'водичка': {'suffix': '-ичка', 'base': 'вода', 'meaning': '小水', 'evaluation': 'diminutive_affectionate'},
        'косичка': {'suffix': '-ичка', 'base': 'коса', 'meaning': '小辫子', 'evaluation': 'diminutive_affectionate'},
        
        # -ушка/-юшка 后缀
        'старушка': {'suffix': '-ушка', 'base': 'старуха', 'meaning': '老奶奶', 'evaluation': 'diminutive_affectionate'},
        'бабушка': {'suffix': '-ушка', 'base': 'баба', 'meaning': '奶奶', 'evaluation': 'diminutive_affectionate'},
        'дедушка': {'suffix': '-ушка', 'base': 'дед', 'meaning': '爷爷', 'evaluation': 'diminutive_affectionate'},
        'избушка': {'suffix': '-ушка', 'base': 'изба', 'meaning': '小木屋', 'evaluation': 'diminutive_affectionate'},
        'подружка': {'suffix': '-ушка', 'base': 'подруга', 'meaning': '小女友', 'evaluation': 'diminutive_affectionate'},
        'горушка': {'suffix': '-ушка', 'base': 'гора', 'meaning': '小山', 'evaluation': 'diminutive_affectionate'},
        'волюшка': {'suffix': '-юшка', 'base': 'воля', 'meaning': '自由（爱称）', 'evaluation': 'diminutive_affectionate'},
        'долюшка': {'suffix': '-юшка', 'base': 'доля', 'meaning': '命运（爱称）', 'evaluation': 'diminutive_affectionate'},
        'батюшка': {'suffix': '-юшка', 'base': 'батя', 'meaning': '父亲（爱称）', 'evaluation': 'diminutive_affectionate'},
        'матушка': {'suffix': '-ушка', 'base': 'мать', 'meaning': '母亲（爱称）', 'evaluation': 'diminutive_affectionate'},
        
        # -ка 后缀
        'дочка': {'suffix': '-ка', 'base': 'дочь', 'meaning': '女儿（爱称）', 'evaluation': 'diminutive_affectionate'},
        'собачка': {'suffix': '-ка', 'base': 'собака', 'meaning': '小狗狗', 'evaluation': 'diminutive_affectionate'},
        'рыбка': {'suffix': '-ка', 'base': 'рыба', 'meaning': '小鱼', 'evaluation': 'diminutive_affectionate'},
        'ручка': {'suffix': '-ка', 'base': 'рука', 'meaning': '小手', 'evaluation': 'diminutive_affectionate'},
        'ножка': {'suffix': '-ка', 'base': 'нога', 'meaning': '小脚', 'evaluation': 'diminutive_affectionate'},
        'дорожка': {'suffix': '-ка', 'base': 'дорога', 'meaning': '小路', 'evaluation': 'diminutive_affectionate'},
        'тропинка': {'suffix': '-ка', 'base': 'тропа', 'meaning': '小径', 'evaluation': 'diminutive_affectionate'},
        'головка': {'suffix': '-ка', 'base': 'голова', 'meaning': '小头', 'evaluation': 'diminutive_affectionate'},
        'морковка': {'suffix': '-ка', 'base': 'морковь', 'meaning': '胡萝卜', 'evaluation': 'diminutive_neutral'},
        'речка': {'suffix': '-ка', 'base': 'река', 'meaning': '小河', 'evaluation': 'diminutive_affectionate'},
        
        # 增大后缀 -ин
        'исполин': {'suffix': '-ин', 'base': 'исполнить', 'meaning': '巨人', 'evaluation': 'augmentative_awe'},
        'господин': {'suffix': '-ин', 'base': 'господь', 'meaning': '先生、主人', 'evaluation': 'augmentative_respect'},
        'болярин': {'suffix': '-ин', 'base': 'боляр', 'meaning': '贵族', 'evaluation': 'augmentative_respect'},
        
        # -ан 后缀
        'великан': {'suffix': '-ан', 'base': 'великий', 'meaning': '巨人', 'evaluation': 'augmentative_awe'},
        'атаман': {'suffix': '-ан', 'base': 'ата', 'meaning': '首领', 'evaluation': 'augmentative_respect'},
        'капитан': {'suffix': '-ан', 'base': 'капит', 'meaning': '船长', 'evaluation': 'augmentative_respect'},
        
        # -ище 后缀
        'домище': {'suffix': '-ище', 'base': 'дом', 'meaning': '大房子', 'evaluation': 'augmentative_impressive'},
        'ручища': {'suffix': '-ища', 'base': 'рука', 'meaning': '大手', 'evaluation': 'augmentative_impressive'},
        'носище': {'suffix': '-ище', 'base': 'нос', 'meaning': '大鼻子', 'evaluation': 'augmentative_impressive'},
        'голосище': {'suffix': '-ище', 'base': 'голос', 'meaning': '大嗓门', 'evaluation': 'augmentative_impressive'},
        'котище': {'suffix': '-ище', 'base': 'кот', 'meaning': '大猫', 'evaluation': 'augmentative_impressive'},
        'собачище': {'suffix': '-ище', 'base': 'собака', 'meaning': '大狗', 'evaluation': 'augmentative_impressive'},
        
        # -як 后缀
        'толстяк': {'suffix': '-як', 'base': 'толстый', 'meaning': '胖子', 'evaluation': 'augmentative_characteristic'},
        'здоровяк': {'suffix': '-як', 'base': 'здоровый', 'meaning': '壮汉', 'evaluation': 'augmentative_positive'},
        'добряк': {'suffix': '-як', 'base': 'добрый', 'meaning': '好人', 'evaluation': 'augmentative_positive'},
        'бедняк': {'suffix': '-як', 'base': 'бедный', 'meaning': '穷人', 'evaluation': 'augmentative_sympathetic'},
        'простяк': {'suffix': '-як', 'base': 'простой', 'meaning': '老实人', 'evaluation': 'augmentative_neutral'},
        
        # -ыш 后缀
        'крепыш': {'suffix': '-ыш', 'base': 'крепкий', 'meaning': '结实的人', 'evaluation': 'augmentative_positive'},
        'малыш': {'suffix': '-ыш', 'base': 'малый', 'meaning': '小家伙', 'evaluation': 'diminutive_affectionate'},
        'голыш': {'suffix': '-ыш', 'base': 'голый', 'meaning': '光身子', 'evaluation': 'augmentative_neutral'},
        
        # -ач 后缀
        'силач': {'suffix': '-ач', 'base': 'сильный', 'meaning': '大力士', 'evaluation': 'augmentative_admiration'},
        'богач': {'suffix': '-ач', 'base': 'богатый', 'meaning': '富翁', 'evaluation': 'augmentative_neutral'},
        'ловкач': {'suffix': '-ач', 'base': 'ловкий', 'meaning': '灵巧的人', 'evaluation': 'augmentative_positive'},
        'усач': {'suffix': '-ач', 'base': 'ус', 'meaning': '大胡子', 'evaluation': 'augmentative_characteristic'},
        
        # -ырь 后缀
        'богатырь': {'suffix': '-ырь', 'base': 'богатый', 'meaning': '勇士', 'evaluation': 'augmentative_heroic'},
        'пустырь': {'suffix': '-ырь', 'base': 'пустой', 'meaning': '荒地', 'evaluation': 'augmentative_neutral'},
        
        # 复数形式
        'домики': {'suffix': '-ик', 'base': 'дом', 'meaning': '小房子们', 'evaluation': 'diminutive_affectionate'},
        'котики': {'suffix': '-ик', 'base': 'кот', 'meaning': '小猫咪们', 'evaluation': 'diminutive_affectionate'},
        'цветики': {'suffix': '-ик', 'base': 'цвет', 'meaning': '小花朵们', 'evaluation': 'diminutive_affectionate'},
        'огоньки': {'suffix': '-ки', 'base': 'огонь', 'meaning': '小火光们', 'evaluation': 'diminutive_affectionate'},
        'цветочки': {'suffix': '-ки', 'base': 'цветок', 'meaning': '小花朵们', 'evaluation': 'diminutive_affectionate'},
        'дорожки': {'suffix': '-ки', 'base': 'дорога', 'meaning': '小路们', 'evaluation': 'diminutive_affectionate'},
        'ручки': {'suffix': '-ки', 'base': 'рука', 'meaning': '小手们', 'evaluation': 'diminutive_affectionate'},
        'звёздочки': {'suffix': '-ки', 'base': 'звезда', 'meaning': '小星星们', 'evaluation': 'diminutive_affectionate'},
        'веточки': {'suffix': '-ки', 'base': 'ветка', 'meaning': '小树枝们', 'evaluation': 'diminutive_affectionate'},
    }


def _eval_get_excluded_words():
    """排除词列表"""
    return {
        # 生造词
        'великанок', 'мудрецок', 'высотища', 'горища', 'тайнища', 'мечтища',
        'звездище', 'легендище', 'зеленище', 'мудрище', 'гигантище',
        'горун', 'величавица', 'мечтательница', 'сказочники', 'каменистик',
        
        # 普通名词
        'урок', 'уроки', 'звук', 'звуки', 'язык', 'языки', 'ученик', 'ученики',
        'источник', 'источники', 'человек', 'люди', 'маяк', 'маяки',
        'рубин', 'рубины', 'старик', 'старики', 'поток', 'потоки',
        'исток', 'истоки', 'чертог', 'чертоги',
        
        # 工具
        'светильник', 'будильник', 'холодильник', 'паяльник', 'рубильник',
        'выключатель', 'указатель', 'показатель', 'измеритель', 'очиститель',
        
        # 抽象概念
        'красота', 'доброта', 'мудрость', 'величие', 'богатство', 'бедность',
        'старина', 'старины',
        
        # 地理和空间
        'вершина', 'вершины', 'глубина', 'высота', 'ширина', 'длина',
        
        # 时间
        'время', 'место', 'дело', 'слово', 'число', 'суть',
    }


def _eval_validate_context(word, info, text):
    """语境验证"""
    evaluation = info.get('evaluation', '')
    context = text.lower()
    
    # 指小爱称
    if 'diminutive_affectionate' in evaluation:
        positive_keywords = [
            'красив', 'мил', 'добр', 'нежн', 'ласков', 'уют', 'тепл', 'свет',
            'любов', 'дорог', 'прекрасн', 'чудесн', 'волшебн', 'сказочн',
            'зелён', 'светл', 'путеводн', 'надёжн'
        ]
        
        pos = context.find(word)
        if pos != -1:
            window = context[max(0, pos-100):pos+len(word)+100]
            if any(kw in window for kw in positive_keywords):
                return True
    
    # 增大后缀
    elif 'augmentative' in evaluation:
        impressive_keywords = [
            'велич', 'мощ', 'сил', 'огромн', 'гигант', 'колосс', 'грозн',
            'могуч', 'внушительн', 'впечатляющ', 'поразительн', 'гордост',
            'красот', 'небесн', 'вечн'
        ]
        
        pos = context.find(word)
        if pos != -1:
            window = context[max(0, pos-100):pos+len(word)+100]
            if any(kw in window for kw in impressive_keywords):
                return True
    
    # 高置信度词
    high_confidence = {
        'исполин', 'великан', 'камешек', 'лесок', 'домик', 'котик', 'песик',
        'дворик', 'садик', 'цветочек', 'листочек', 'ручеёк', 'огонёк', 'уголок',
        'денёк', 'голосок', 'сынок', 'дружок', 'ветерок', 'снежок', 'стишок'
    }
    
    if word in high_confidence:
        return True
    
    return True

# ==================== 规则 3: 第四格时间表达检测 ====================
def detect_russian_time_expression_4th_case(content_list, required_count):
    """
    检测俄语第四格时间表达格式
    
    Args:
        content_list: 文本内容列表
        required_count: 要求的时间表达数量
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    if content_list == "INVALID" or content_list is None:
        return 0, "❌ 输入文本无效"
    
    try:
        required_count = int(required_count)
    except (ValueError, TypeError):
        return 0, f"❌ required_count 必须是整数: '{required_count}'"

    try:
        if isinstance(content_list, list):
            text = ' '.join(str(item) for item in content_list if item and str(item) != "INVALID")
        else:
            text = str(content_list)
        
        if not text.strip():
            if required_count == 0:
                return 1, "✅ 内容为空，符合要求 0 个时间表达"
            else:
                return 0, "❌ 内容为空，无法检测"
        
        patterns_4th = [
            # 基础时间点表达
            (r'[Вв]\s+(?:[а-яё]+|\d+)\s+час(?:а|ов)?\b(?:\s+(?:утра|дня|вечера|ночи))?', False),
            (r'[Вв]\s+\d+[:.]\d+(?:\s+(?:утра|дня|вечера|ночи))?', False),
            
            # 星期表达
            (r'[Вв]\s+(?:(?:следующ(?:ий|ую)|прошл(?:ый|ую)|эт(?:от|у))\s+)?(?:понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье)\b', False),
            
            # 🔥 新增：в то (же) время 固定短语
            (r'[Вв]\s+то\s+(?:же\s+)?врем[яю]', False),
            
            # в + 形容词 + время 结构
            (r'[Вв]\s+[а-яёА-ЯЁ]+(?:ое|ее)\s+врем[яю](?:\s+года)?', True),
            (r'[Вв]\s+(?:это|всё|какое|любое|каждое|следующее|прошлое|будущее|холодное|теплое|жаркое|зимнее|летнее|весеннее|осеннее|трудное|тяжелое|свободное|рабочее|такое|другое)\s+врем[яю](?:\s+года)?', False),
            
            # 形容词 + 时间名词（单数）
            # 修复：增加了 (?:этот|тот|весь|наш|ваш|свой) 来匹配代词
            (r'[Вв]\s+(?:[а-яёА-ЯЁ]+(?:ый|ий|ой)|этот|тот|весь|наш|ваш|свой)\s+(?:день|момент|час|период|раз)\b', True),
            (r'[Вв]\s+[а-яёА-ЯЁ]+ую\s+(?:ночь|неделю|минуту|секунду|погоду|пору|зиму|весну|осень)\b', True),
            
            # 🔥 修复：形容词 + 时间名词（复数） - 支持多个形容词
            (r'[Вв]\s+(?:[а-яёА-ЯЁ]+(?:ые|ие)\s+){1,3}(?:дни|ночи|часы|минуты|секунды|моменты|недели|месяцы|времена)\b', True),
            (r'[Вв]\s+(?:[а-яёА-ЯЁ]+(?:ые|ие)\s+)+(?:и|или)\s+[а-яёА-ЯЁ]+(?:ые|ие)\s+(?:дни|ночи|часы|минуты|секунды|моменты|недели|месяцы|времена)\b', True),
            
            # 其他时间表达
            (r'[Вв]\s+(?:день|вечер|ночь|утро)\s+[а-яёА-ЯЁ]+', False),
            
            # на + 时间段
            (r'[Нн]а\s+(?:неделю|день|месяц|год|час|минуту|секунду|мгновение)\b', False),
            (r'[Нн]а\s+(?:[а-яё]+|\d+)\s+(?:недел[июь]|дн[яей]|месяц[ае]?|год[а]?|лет|час[аов]?|минут[уы]?)\b', False),
            (r'[Нн]а\s+(?:перв(?:ый|ую)|втор(?:ой|ую)|трет(?:ий|ью)|четв[ёе]рт(?:ый|ую)|пят(?:ый|ую)|шест(?:ой|ую)|седьм(?:ой|ую)|восьм(?:ой|ую)|девят(?:ый|ую)|десят(?:ый|ую))\s+(?:день|неделю|месяц|год)\b', False),
            
            # по + 时间（🔥 添加年份支持）
            (r'[Пп]о\s+(?:январь|февраль|март|апрель|май|июнь|июль|август|сентябрь|октябрь|ноябрь|декабрь)(?:\s+\d+)?(?:\s+года)?\b', False),
            (r'[Пп]о\s+(?:понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье)\b', False),
            (r'[Пп]о\s+(?:утро|день|вечер|ночь)\b', False),
            
            # через + 时间段
            (r'[Чч]ерез\s+(?:неделю|день|месяц|год|час|минуту|секунду|мгновение)\b', False),
            (r'[Чч]ерез\s+(?:(?:несколько|пару)\s+)?(?:[а-яё]+|\d+)\s+(?:недел[июь]|дн[яей]|месяц[ае]?|год[а]?|лет|час[аов]?|минут[уы]?)\b', False),
            
            # за + 时间段
            (r'[Зз]а\s+(?:неделю|день|месяц|год|час|минуту|секунду)\b', False),
            (r'[Зз]а\s+(?:(?:несколько|пару)\s+)?(?:[а-яё]+|\d+)\s+(?:недел[июь]|дн[яей]|месяц[ае]?|год[а]?|лет|час[аов]?|минут[уы]?)\b', False),
        ]
        
        found_expressions = []
        
        for pattern, needs_adj_validation in patterns_4th:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                full_match = match.group(0).strip()
                
                if _time4_is_valid(full_match, needs_adj_validation):
                    found_expressions.append({
                        'text': full_match,
                        'position': match.start()
                    })
        
        unique = _time4_remove_overlapping(found_expressions)
        
        total_found = len(unique)
        found_display = [expr['text'] for expr in unique]
        
        if total_found == required_count:
            if required_count == 0:
                return 1, f"✅ 正确：未找到第四格时间表达 (要求=0个)"
            else:
                return 1, f"✅ 找到 {total_found} 个第四格时间表达 (要求={required_count}个): {found_display}"
        else:
            if required_count == 0:
                return 0, f"❌ 找到 {total_found} 个第四格时间表达，但要求 0 个: {found_display}"
            else:
                return 0, f"❌ 找到 {total_found} 个第四格时间表达 (要求={required_count}个): {found_display}"

    except Exception as e:
        import traceback
        return 0, f"❌ 函数执行异常: {str(e)}\n{traceback.format_exc()}"


def _time4_is_valid(expression, needs_adj_validation):
    """验证第四格表达式（修复版 - 支持 в + 形容词 + время）"""
    expr_lower = expression.lower()
    
    # ========== 排除规则 ==========
    
    # 排除第六格（年份）
    if 'году' in expr_lower or 'годах' in expr_lower:
        return False
    if re.search(r'в\s+\d+\s+год[ауе]', expr_lower):
        return False
    if re.search(r'в\s+\d+-?(?:ом|м)\s+век[еу]', expr_lower):
        return False
    
    # 排除月份第六格
    sixth_months = ['январе', 'феврале', 'марте', 'апреле', 'мае', 'июне', 
                    'июле', 'августе', 'сентябре', 'октябре', 'ноябре', 'декабре']
    if any(m in expr_lower for m in sixth_months):
        return False
    
    # 排除固定短语（但不排除 "в то время"）
    invalid = ['в том числе', 'в связи', 'в случае', 'в целом', 'в итоге',
               'в результате', 'в отличие', 'в зависимости', 'в соответствии',
               'на самом деле', 'на всякий случай', 'на первый взгляд',
               'по крайней мере', 'по сути', 'по мнению', 'по причине']
    if any(phrase in expr_lower for phrase in invalid):
        return False
    
    # 排除非时间名词
    non_time = ['вопрос', 'тему', 'проблему', 'задачу', 'работу', 'человека', 'состав', 'процесс', 'часть', 'части']
    if any(re.search(r'\b' + noun + r'\b', expr_lower) for noun in non_time):
        return False
    
    # ========== 验证规则 ==========
    
    # 🔥 专门处理 "в то (же) время" 固定短语
    if re.search(r'[вВ]\s+то\s+(?:же\s+)?врем[яю]', expr_lower):
        return True
    
    # 处理 "в + 形容词 + время" 结构
    if re.search(r'[вВ]\s+[а-яёА-ЯЁ]+(?:ое|ее)\s+врем[яю]', expr_lower):
        time_related_adjs = [
            'холодн', 'тепл', 'жарк', 'морозн', 'солнечн', 'дождлив', 'снежн',
            'летн', 'зимн', 'весенн', 'осенн', 'ранн', 'поздн', 'долг', 'коротк',
            'прошл', 'будущ', 'настоящ', 'минувш', 'последн', 'давн', 'недавн', 'ближайш',
            'трудн', 'сложн', 'тяжел', 'легк', 'прият', 'счастлив', 'особ', 'обычн',
            'хорош', 'плох', 'светл', 'темн', 'тих', 'шумн', 'следующ', 'другой', 'иной', 'нов', 'стар',
            'свободн', 'рабочее', 'военн', 'мирн', 'такое', 'сам'
        ]
        
        time_pronouns = ['это', 'всё', 'какое', 'любое', 'каждое', 'другое']
        
        if any(adj in expr_lower for adj in time_related_adjs) or any(pron in expr_lower for pron in time_pronouns):
            return True
    
    # 原有验证逻辑（形容词 + 其他时间名词）
    if needs_adj_validation:
        explicit_time_nouns = [
            'день', 'ночь', 'неделю', 'минуту', 'секунду', 'момент', 'час', 'период', 'раз',
            'погоду', 'пору', 'зиму', 'весну', 'осень', 'лето', 'врем[яю]',
            'дни', 'ночи', 'часы', 'минуты', 'секунды', 'моменты', 'недели', 'месяцы', 'времена'
        ]
        
        has_time_noun = any(re.search(r'\b' + noun + r'\b', expr_lower) for noun in explicit_time_nouns)
        
        if has_time_noun:
            # 检查是否有形容词词尾（阳性/中性/阴性/复数第四格）
            if re.search(r'\b[а-яё]+(?:ый|ий|ой|ое|ее|ую|ые|ие)\b', expr_lower):
                return True
        
        # 兜底：检查是否有时间相关形容词
        time_adjs = [
            'холодн', 'тепл', 'жарк', 'морозн', 'солнечн', 'дождлив', 'снежн', 'ясн', 'пасмурн',
            'летн', 'зимн', 'весенн', 'осенн', 'ранн', 'поздн', 'долг', 'коротк',
            'прошл', 'будущ', 'настоящ', 'минувш', 'последн', 'давн', 'недавн', 'ближайш',
            'трудн', 'сложн', 'тяжел', 'легк', 'прият', 'счастлив', 'особ', 'обычн',
            'хорош', 'плох', 'светл', 'темн', 'тих', 'шумн', 'следующ', 'другой', 'иной', 'нов', 'стар',
            'эт', 'тот', 'кажд', 'люб', 'вс', 'как', 'так', 'сам'
        ]
        if any(adj in expr_lower for adj in time_adjs):
            return True
        
        return False
    
    return True


def _time4_remove_overlapping(expressions):
    """移除重叠的表达式"""
    if not expressions:
        return []
    
    sorted_expr = sorted(expressions, key=lambda x: x['position'])
    unique = []
    
    for expr in sorted_expr:
        is_overlap = False
        for existing in unique:
            existing_start = existing['position']
            existing_end = existing_start + len(existing['text'])
            expr_start = expr['position']
            expr_end = expr_start + len(expr['text'])
            
            if not (expr_end <= existing_start or expr_start >= existing_end):
                is_overlap = True
                if len(expr['text']) > len(existing['text']):
                    unique.remove(existing)
                    unique.append(expr)
                break
        
        if not is_overlap:
            unique.append(expr)
    
    return unique




# ==================== 规则 4: 第六格时间表达检测 ====================
def detect_russian_time_expression_6th_case(content_list, required_count):
    """
    检测俄语第六格时间表达格式
    
    Args:
        content_list: 文本内容列表
        required_count: 要求的时间表达数量
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    if content_list == "INVALID" or content_list is None:
        return 0, "❌ 输入文本无效"
    
    try:
        required_count = int(required_count)
    except (ValueError, TypeError):
        return 0, f"❌ required_count 必须是整数: '{required_count}'"

    try:
        if isinstance(content_list, list):
            text = ' '.join(str(item) for item in content_list if item and str(item) != "INVALID")
        else:
            text = str(content_list)
        
        if not text.strip():
            if required_count == 0:
                return 1, "✅ 内容为空，符合要求 0 个时间表达"
            else:
                return 0, "❌ 内容为空，无法检测"
        
        patterns_6th = [
            r'в\s+(этом|прошлом|следующем|будущем)\s+году',
            r'в\s+(\d{4})\s+году',
            r'в\s+(две\s+тысячи\s+)?(\d+)-?ом\s+году',
            r'в\s+(\d{4})-(\d{4})\s+годах',
            r'в\s+(\d\d)-х\s+годах',
            r'в\s+(январе|феврале|марте|апреле|мае|июне|июле|августе|сентябре|октябре|ноябре|декабре)',
            r'в\s+(этом|прошлом|следующем)\s+месяце',
            r'в(?:о)?\s+(первом|втором|третьем|четвёртом|четвертом|пятом|шестом|седьмом|восьмом|девятом|десятом|одиннадцатом|двенадцатом)\s+час[уе](?:\s+(ночи|утра|дня|вечера))?',
            r'в\s+(прошлом|этом|следующем)\s+веке',
            r'в\s+(\d+)-?ом\s+веке',
            r'в\s+(\d+)-?ых\s+годах',
            r'в\s+(X{0,3}(?:IX|IV|V?I{0,3}))[-ом]?\s+веке',
            r'в\s+(прошлом|настоящем|будущем)(?!\s+году)',
            r'в\s+(начале|конце|середине)\s+([а-яёА-ЯЁ]+(?:\s+[а-яёА-ЯЁ]+)*)',
            r'в\s+(зиму|весну|лето|осень)',
            r'в\s+(утро|вечер|ночь|полдень|полночь)',
            r'в\s+(последнее|ближайшем|скором)\s+(время|будущем)',
            r'в\s+(период|эпоху|рамках|процессе|ходе)\s+([а-яёА-ЯЁ]+(?:\s+[а-яёА-ЯЁ]+)*)',
            r'в\s+(дни|годы|сутки)(?:\s+([а-яёА-ЯЁ]+(?:\s+[а-яёА-ЯЁ]+)*))?',
            r'на\s+(этой|прошлой|следующей|будущей)\s+неделе',
            r'на\s+протяжении\s+([а-яёА-ЯЁ]+(?:\s+[а-яёА-ЯЁ]+)*)',
            r'в\s+условиях\s+([а-яёА-ЯЁ]+(?:\s+[а-яёА-ЯЁ]+)*)',
        ]
        
        found = []
        
        for i, pattern in enumerate(patterns_6th):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                full_match = match.group(0).strip()
                
                if _time6_is_valid(full_match):
                    found.append({
                        'text': full_match,
                        'position': match.start(),
                        'pattern_type': i
                    })
        
        unique = _time6_remove_overlapping(found)
        
        total = len(unique)
        display = [expr['text'] for expr in unique]
        
        if total == required_count:
            if required_count == 0:
                return 1, f"✅ 正确：未找到第六格时间表达 (要求=0个)"
            else:
                return 1, f"✅ 找到 {total} 个第六格时间表达 (要求={required_count}个): {display}"
        else:
            if required_count == 0:
                return 0, f"❌ 找到 {total} 个第六格时间表达，但要求 0 个: {display}"
            else:
                return 0, f"❌ 找到 {total} 个第六格时间表达 (要求={required_count}个): {display}"

    except Exception as e:
        return 0, f"❌ 函数执行异常: {e}"


def _time6_is_valid(full_text):
    """验证第六格时间表达"""
    if len(full_text) < 2:
        return False
    
    excluded = [
        r'в\s+том\s+числе', r'в\s+частности', r'в\s+результате', r'в\s+случае',
        r'в\s+связи', r'в\s+соответствии', r'в\s+зависимости', r'в\s+течение',
        r'на\s+стол', r'на\s+улиц', r'в\s+комнат', r'в\s+здани',
    ]
    
    for pattern in excluded:
        if re.search(pattern, full_text, re.IGNORECASE):
            return False
    
    return True


def _time6_remove_overlapping(expressions):
    """去除重叠的第六格表达式"""
    if not expressions:
        return []
    
    expressions.sort(key=lambda x: x['position'])
    
    unique = []
    for expr in expressions:
        overlaps = False
        for existing in unique:
            if abs(expr['position'] - existing['position']) < 15:
                overlaps = True
                if len(expr['text']) > len(existing['text']):
                    unique.remove(existing)
                    unique.append(expr)
                break
        
        if not overlaps:
            unique.append(expr)
    
    return unique





try:
    import pyphen
    RUSSIAN_SYLLABIFIER = pyphen.Pyphen(lang='ru_RU')
    PYPHEN_AVAILABLE = True
except ImportError:
    RUSSIAN_SYLLABIFIER = None
    PYPHEN_AVAILABLE = False
    print("⚠️  警告: pyphen 库未安装，将使用备用音节划分方法。建议运行: pip install pyphen")


# ==================== LibraryManager 类 ====================
class LibraryManager:
    """管理外部库的加载"""
    _stresser = None
    _stresser_available = None
    
    @classmethod
    def get_stresser(cls):
        """返回 (stresser对象, 是否可用)"""
        if cls._stresser_available is not None:
            return cls._stresser, cls._stresser_available
        
        try:
            import russtress
            cls._stresser = russtress.Accent()
            cls._stresser_available = True
        except ImportError:
            cls._stresser = None
            cls._stresser_available = False
        
        return cls._stresser, cls._stresser_available


def create_logger(debug):
    """创建日志函数"""
    def log(msg):
        if debug:
            print(msg)
    return log


# ==================== 规则 5: 俄语格律检测 ====================
def detect_russian_single_meter(content_list, expected_meter, debug=False):
    """
    检测俄语诗歌是否符合指定的格律类型（简化输出版）
    
    Args:
        content_list: 诗歌内容列表
        expected_meter: 期望的格律类型（Хорей/Ямб/Дактиль/Амфибрахий/Анапест）
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    if not isinstance(content_list, list) or not content_list:
        return 0, "❌ 输入诗歌无效"
    
    poem = str(content_list[0]).strip()
    if not poem:
        return 0, "❌ 没有找到诗歌内容"
    
    log(f"[DEBUG] 期望格律: {expected_meter}")

    try:
        detected_meter, analysis = _meter_analyze_poem(poem, log)
        
        meter_names = {
            'Хорей': '扬抑格(Хорей)', 
            'Ямб': '抑扬格(Ямб)', 
            'Дактиль': '扬抑抑格(Дактиль)', 
            'Амфибрахий': '抑扬抑格(Амфибрахий)', 
            'Анапест': '抑抑扬格(Анапест)', 
            'Unknown': '未知或混合格律'
        }
        
        detected_name = meter_names.get(detected_meter, '未知格律')
        expected_name = meter_names.get(expected_meter, expected_meter)
        
        # ✅ 添加覆盖率检查
        matched_lines = analysis.get('matched_lines', 0)
        total_lines = analysis.get('total_lines', 0)
        coverage_rate = matched_lines / total_lines if total_lines > 0 else 0
        
        if detected_meter == expected_meter:
            # ✅ 即使格律匹配，也要检查覆盖率
            if coverage_rate < 0.75:
                return 0, f"❌ 格律一致性不足: 虽然检测到{detected_name}，但符合度不够（需≥75%）"
            return 1, f"✅ 诗歌格律符合要求: 检测到{detected_name}，符合期望的{expected_name}"
        else:
            return 0, f"❌ 诗歌格律不符合要求: 检测到{detected_name}，期望{expected_name}"
    
    except Exception as e:
        log(f"[ERROR] 异常: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 0, f"❌ 函数执行异常: {e}"


def _meter_analyze_poem(poem, log):
    """分析诗歌格律"""
    lines = [line.strip() for line in poem.split('\n') if line.strip()]
    if not lines:
        return 'Unknown', {'method': 'error', 'details': '无有效诗行', 'matched_lines': 0, 'total_lines': 0}
    
    log(f"[DEBUG] 诗歌共 {len(lines)} 行")
    line_analyses = [_meter_analyze_line(line, i + 1, log) for i, line in enumerate(lines)]
    return _meter_determine(line_analyses, log)


def _meter_analyze_line(line, line_num, log):
    """分析单行诗歌的格律"""
    clean_line = re.sub(r'[—,.:;!?»«""\(\)]+', ' ', line)
    words = re.findall(r'[а-яёА-ЯЁ]+', clean_line)
    
    log(f"[DEBUG] 第{line_num}行单词: {words}")
    
    all_patterns = []
    
    for word in words:
        stressed_word = _meter_get_stress(word, log)
        word_info = _meter_word_stress(word, stressed_word, log)
        
        # 直接添加每个词的重音模式
        stress_pattern = word_info.get('stress_pattern', [])
        all_patterns.extend(stress_pattern)
        
        log(f"[DEBUG]   单词: {word} -> 音节: {word_info.get('syllables', [])} -> 模式: {stress_pattern}")
    
    log(f"[DEBUG] 第{line_num}行完整模式: {all_patterns}")
    
    matches = _meter_match_pattern(all_patterns, log)
    
    return {
        'line_num': line_num,
        'line_text': line,
        'stress_pattern': all_patterns,
        'meter_matches': matches
    }


def _meter_split_syllables(word):
    """使用 pyphen 进行准确的音节划分"""
    if PYPHEN_AVAILABLE and RUSSIAN_SYLLABIFIER:
        try:
            syllables_str = RUSSIAN_SYLLABIFIER.inserted(word.lower(), hyphen='|')
            syllables = syllables_str.split('|')
            if syllables and all(syllables):
                return syllables
        except:
            pass
    
    # 备用方案：基于元音的简单划分
    vowels = "аеёиоуыэюя"
    word_lower = word.lower()
    syllables = []
    temp = ""
    
    for char in word_lower:
        temp += char
        if char in vowels:
            syllables.append(temp)
            temp = ""
    
    if temp and syllables:
        syllables[-1] += temp
    elif temp:
        syllables.append(temp)
    
    return syllables if syllables else [word]


def _meter_word_stress(original, stressed, log):
    """获取单词的重音分析"""
    vowels_lower = "аеёиоуыэюя"
    word_lower = original.lower()
    has_vowels = any(c in vowels_lower for c in word_lower)
    
    # 功能词列表
    function_words = {
        'в', 'к', 'с', 'на', 'за', 'под', 'над', 'от', 'до', 'по', 'при', 'про',
        'без', 'для', 'через', 'между', 'у', 'о', 'об', 'из', 'со', 'ко', 'во',
        'и', 'а', 'но', 'или', 'да', 'ни',
        'не', 'же', 'ли', 'бы',
        'что', 'как', 'где', 'куда', 'когда', 'кто', 'чей', 'чем', 'кем'
    }
    
    if word_lower in function_words:
        if has_vowels:
            return {
                'word': original,
                'syllables': [original],
                'stress_pattern': ['轻'],
                'is_syllabic': True,
                'is_function_word': True
            }
        else:
            return {
                'word': original,
                'syllables': [],
                'stress_pattern': [],
                'is_syllabic': False,
                'is_function_word': True
            }

    if not has_vowels:
        return {
            'word': original,
            'syllables': [],
            'stress_pattern': [],
            'is_syllabic': False
        }

    syllables = _meter_split_syllables(original)
    syllable_count = len(syllables)
    
    log(f"[DEBUG]     {original} 的音节划分: {syllables} (共{syllable_count}个)")
    
    stress_pattern = ['轻'] * syllable_count
    stressed_syllable_index = -1
    
    if '́' in stressed:
        vowel_count = 0
        for i, char in enumerate(stressed):
            if char.lower() in vowels_lower:
                vowel_count += 1
            if char == '́':
                stressed_syllable_index = vowel_count - 1
                log(f"[DEBUG]     找到重音符号，位置在第 {stressed_syllable_index + 1} 个音节")
                break
    
    if stressed_syllable_index == -1 and 'ё' in word_lower:
        vowel_count = 0
        for char in word_lower:
            if char in vowels_lower:
                vowel_count += 1
                if char == 'ё':
                    stressed_syllable_index = vowel_count - 1
                    log(f"[DEBUG]     找到 ё，位置在第 {stressed_syllable_index + 1} 个音节")
                    break
    
    if stressed_syllable_index != -1 and 0 <= stressed_syllable_index < syllable_count:
        stress_pattern[stressed_syllable_index] = '重'
        log(f"[DEBUG]     标记第 {stressed_syllable_index + 1} 个音节为重音")
    elif syllable_count > 0:
        default_stress = -2 if syllable_count >= 2 else 0
        stress_pattern[default_stress] = '重'
        log(f"[DEBUG]     使用默认重音位置: 第 {syllable_count + default_stress + 1} 个音节")

    return {
        'word': original,
        'syllables': syllables,
        'stress_pattern': stress_pattern,
        'is_syllabic': True,
        'syllable_count': syllable_count
    }


@lru_cache(maxsize=2000)
def _meter_get_stress(word, log):
    """获取单词重音"""
    stresser, available = LibraryManager.get_stresser()
    
    word_lower = word.lower().strip('.,!?;:—»«""')
    if not word_lower:
        return ""
    
    stress_dict = {
        'прогресс': 'прогре́сс', 'технология': 'техноло́гия', 'технологий': 'техноло́гий',
        'инновация': 'иннова́ция', 'инновацию': 'иннова́цию', 'развитие': 'разви́тие',
        'развитии': 'разви́тии', 'будущее': 'бу́дущее', 'модернизация': 'модерниза́ция',
        'модернизации': 'модерниза́ции', 'строительство': 'строи́тельство',
        'достижение': 'достиже́ние', 'преобразование': 'преобразова́ние',
        'индустрия': 'инду́стрия', 'экономика': 'эконо́мика', 'цифры': 'ци́фры',
        'процесс': 'проце́сс', 'движет': 'дви́жет', 'движемся': 'дви́жемся',
        'потоке': 'пото́ке', 'правит': 'пра́вит', 'светом': 'све́том',
        'прогресса': 'прогре́сса', 'ввысь': 'ввысь', 'оставит': 'оста́вит',
        'шанса': 'ша́нса', 'сомненьям': 'сомне́ньям', 'вперед': 'вперёд',
        'стремись': 'стреми́сь', 'творчество': 'тво́рчество', 'надежды': 'наде́жды',
        'сияет': 'сия́ет', 'облаках': 'облака́х', 'шагаем': 'шага́ем',
        'боясь': 'боя́сь', 'славит': 'сла́вит', 'замок': 'за́мок',
        'мука': 'му́ка', 'орган': 'о́рган', 'атлас': 'а́тлас',
        'хлопок': 'хло́пок', 'пили': 'пи́ли', 'парить': 'па́рить',
        'ветер': 'ве́тер', 'свежий': 'све́жий', 'светит': 'све́тит',
        'светлый': 'све́тлый', 'солнце': 'со́лнце', 'мир': 'мир',
        'мире': 'ми́ре', 'идей': 'иде́й', 'меняется': 'меня́ется',
        'танце': 'та́нце', 'новый': 'но́вый', 'день': 'день',
        'счастье': 'сча́стье', 'несёт': 'несёт', 'идём': 'идём',
        'найдём': 'найдём', 'растёт': 'растёт', 'оживёт': 'оживёт',
        'полёт': 'полёт', 'идёт': 'идёт', 'море': 'мо́ре',
        'свет': 'свет', 'путь': 'путь', 'земля': 'земля́',
        'вода': 'вода́', 'огонь': 'ого́нь', 'небо': 'не́бо',
        'река': 'река́', 'гора': 'гора́', 'смело': 'сме́ло',
        'вместе': 'вме́сте', 'время': 'вре́мя', 'сердце': 'се́рдце',
        'мечты': 'мечты́', 'наша': 'на́ша', 'весна': 'весна́', 'она': 'она́',
        'ясно': 'я́сно', 'глядь': 'глядь', 'развиваемся': 'развива́емся',
        'прекрасно': 'прекра́сно'
    }
    
    if word_lower in stress_dict:
        return stress_dict[word_lower]
    
    if available and stresser:
        try:
            stressed = stresser.put_stress(word_lower, stress_symbol='́')
            if stressed and ('́' in stressed or 'ё' in stressed):
                return stressed
        except:
            pass
    
    if 'ё' in word_lower:
        return word_lower
    
    vowels_lower = "аеиоуыэюя"
    vowel_count = sum(1 for c in word_lower if c in vowels_lower)
    
    if vowel_count == 1:
        for i, c in enumerate(word_lower):
            if c in vowels_lower:
                return word_lower[:i+1] + '́' + word_lower[i+1:]
        return word_lower
    
    if word_lower.endswith(('ой', 'ая', 'ое', 'ые', 'ий', 'яя', 'ее', 'ие')):
        vowel_positions = [i for i, c in enumerate(word_lower) if c in vowels_lower]
        if vowel_positions:
            pos = vowel_positions[-1]
            return word_lower[:pos+1] + '́' + word_lower[pos+1:]
    
    if word_lower.endswith(('ение', 'ание', 'ство', 'ация', 'яция')):
        vowel_positions = [i for i, c in enumerate(word_lower) if c in vowels_lower]
        if len(vowel_positions) >= 3:
            pos = vowel_positions[-3]
            return word_lower[:pos+1] + '́' + word_lower[pos+1:]
    
    vowel_positions = [i for i, c in enumerate(word_lower) if c in vowels_lower]
    if vowel_positions:
        pos = vowel_positions[-2] if len(vowel_positions) >= 2 else vowel_positions[0]
        return word_lower[:pos+1] + '́' + word_lower[pos+1:]
    
    return word_lower


def _meter_has_pattern_violations(stress_pattern):
    """检测是否有格律违规"""
    pattern_str = ''.join(stress_pattern)
    
    if '重重' in pattern_str:
        return True
    
    if '轻轻轻轻' in pattern_str:
        return True
    
    total = len(stress_pattern)
    heavy_count = stress_pattern.count('重')
    
    if total > 0:
        heavy_ratio = heavy_count / total
        if heavy_ratio < 0.25 or heavy_ratio > 0.60:
            return True
    
    return False


def _meter_match_pattern(stress_pattern, log):
    """匹配格律模式"""
    if len(stress_pattern) < 2:
        return []
    
    if _meter_has_pattern_violations(stress_pattern):
        log(f"[DEBUG] 检测到格律违规: {stress_pattern}")
        return []
    
    meter_patterns = {
        'Хорей': ['重', '轻'],
        'Ямб': ['轻', '重'],
        'Дактиль': ['重', '轻', '轻'],
        'Амфибрахий': ['轻', '重', '轻'],
        'Анапест': ['轻', '轻', '重']
    }
    
    matches = []
    for name, pattern in meter_patterns.items():
        score = _meter_calc_score(stress_pattern, pattern)
        if score >= 0.80:
            matches.append({'meter': name, 'confidence': score})
            log(f"[DEBUG] 格律 {name} 匹配分数: {score:.1%}")
    
    return sorted(matches, key=lambda x: x['confidence'], reverse=True)


def _meter_calc_score(stress_pattern, meter_pattern):
    """计算格律匹配分数"""
    total = len(stress_pattern)
    if total == 0:
        return 0.0
    
    match = 0
    p_len = len(meter_pattern)
    penalty = 0
    
    for i, actual in enumerate(stress_pattern):
        expected = meter_pattern[i % p_len]
        
        if actual == expected:
            match += 1.0
        else:
            if i == 0:
                match += 0.5
            elif i == total - 1:
                match += 0.4
            else:
                match += 0.2
                penalty += 0.3
    
    base_score = match / total
    final_score = base_score - (penalty / total)
    
    return max(0.0, final_score)


def _meter_determine(line_analyses, log):
    """判断诗歌的主导格律"""
    if not line_analyses:
        return 'Unknown', {'matched_lines': 0, 'total_lines': 0}
    
    meter_votes = defaultdict(list)
    total_lines = len(line_analyses)
    
    for analysis in line_analyses:
        matches = analysis.get('meter_matches', [])
        if matches:
            best = matches[0]
            if best['confidence'] >= 0.80:
                meter_votes[best['meter']].append(best['confidence'])
    
    if not meter_votes:
        return 'Unknown', {
            'method': 'no_matches',
            'matched_lines': 0,
            'total_lines': total_lines
        }
    
    best_meter = None
    best_score = 0
    
    for meter, confidences in meter_votes.items():
        line_count = len(confidences)
        avg_conf = sum(confidences) / line_count
        coverage = line_count / total_lines
        score = coverage * avg_conf
        
        if coverage >= 0.80 and avg_conf >= 0.80 and score > best_score:
            best_score = score
            best_meter = meter
    
    if not best_meter:
        for meter, confidences in meter_votes.items():
            line_count = len(confidences)
            avg_conf = sum(confidences) / line_count
            coverage = line_count / total_lines
            
            if coverage >= 0.75 and avg_conf >= 0.75:
                return meter, {
                    'method': 'partial_match',
                    'matched_lines': line_count,
                    'total_lines': total_lines
                }
        
        return 'Unknown', {
            'method': 'insufficient_match',
            'matched_lines': 0,
            'total_lines': total_lines
        }
    
    confidences = meter_votes[best_meter]
    return best_meter, {
        'method': 'strict_analysis',
        'matched_lines': len(confidences),
        'total_lines': total_lines
    }





# ==================== 规则 6: 单复数语义差异对检测 ====================
def detect_russian_singular_plural_semantic_pairs(content_list, required_pairs, debug=False):
    """
    动态检测俄语文本中单复数语义差异名词对
    
    改进版本：更严格地区分真正的语义差异和普通语法变化
    
    Args:
        content_list: 文本内容列表
        required_pairs: 要求的单复数语义差异对数量
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    log(f"[DEBUG] 开始动态检测单复数语义差异对, required_pairs={required_pairs}")
    
    # 输入验证
    if content_list == "INVALID" or content_list is None:
        return 0, "❌ 输入文本无效"
    
    try:
        required_pairs = int(required_pairs)
    except (ValueError, TypeError):
        return 0, f"❌ required_pairs 必须是整数: '{required_pairs}'"

    try:
        # 文本预处理
        if isinstance(content_list, list):
            text = ' '.join(str(item) for item in content_list if item and str(item) != "INVALID")
        else:
            text = str(content_list)
        
        if not text.strip():
            return 1 if required_pairs == 0 else 0, "✅ 内容为空" if required_pairs == 0 else "❌ 内容为空"
        
        log(f"[DEBUG] 处理文本长度: {len(text)}")
        
        # 步骤1: 检查已知的语义差异对
        known_pairs = _sp_check_known_pairs(text, log)
        log(f"[DEBUG] 发现 {len(known_pairs)} 个已知语义差异对")
        
        # 步骤2: 提取潜在名词
        potential_nouns = _sp_extract_nouns(text, log)
        log(f"[DEBUG] 提取到 {len(potential_nouns)} 个潜在名词")
        
        # 步骤3: 识别单复数关系
        sg_pl_pairs = _sp_identify_relationships(potential_nouns, text, log)
        log(f"[DEBUG] 识别到 {len(sg_pl_pairs)} 个单复数关系")
        
        # 步骤4: 严格分析语义差异
        dynamic_pairs = _sp_analyze_semantics(sg_pl_pairs, text, log)
        log(f"[DEBUG] 动态发现 {len(dynamic_pairs)} 个语义差异对")
        
        # 步骤5: 合并结果
        all_pairs = _sp_merge_deduplicate(known_pairs, dynamic_pairs, log)
        total_found = len(all_pairs)
        
        # 构建结果说明
        if all_pairs:
            descriptions = []
            for pair in all_pairs:
                sg_info = f"{pair['singular']}({pair['singular_context']})"
                pl_info = f"{pair['plural']}({pair['plural_context']})"
                conf = f"置信度:{pair['confidence']:.2f}"
                descriptions.append(f"{sg_info} vs {pl_info} [{conf}]")
            
            pairs_text = "; ".join(descriptions[:3])
            if len(descriptions) > 3:
                pairs_text += f" 等{total_found}组"
        else:
            pairs_text = "无"
        
        # 判断结果
        if total_found == required_pairs:
            return 1, f"✅ 找到恰好 {total_found} 组单复数语义差异对 (要求={required_pairs}组): {pairs_text}"
        else:
            return 0, f"❌ 找到 {total_found} 组单复数语义差异对 (要求={required_pairs}组): {pairs_text}"

    except Exception as e:
        log(f"[DEBUG] 异常: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 0, f"❌ 函数执行异常: {e}"


def _sp_check_known_pairs(text, log):
    """检查已知的语义差异对"""
    known = {
        ('способность', 'способности'): {
            'singular_meaning': '抽象能力',
            'plural_meaning': '具体才能',
            'confidence': 0.95
        },
        ('власть', 'власти'): {
            'singular_meaning': '权力概念',
            'plural_meaning': '当局机构',
            'confidence': 0.95
        },
        ('бумага', 'бумаги'): {
            'singular_meaning': '纸张材料',
            'plural_meaning': '文件资料',
            'confidence': 0.90
        },
        ('время', 'времена'): {
            'singular_meaning': '时间概念',
            'plural_meaning': '时代时期',
            'confidence': 0.90
        },
        ('дело', 'дела'): {
            'singular_meaning': '事情概念',
            'plural_meaning': '具体事务',
            'confidence': 0.85
        },
    }
    
    found = []
    text_lower = text.lower()
    
    for (singular, plural), info in known.items():
        if re.search(r'\b' + re.escape(singular) + r'\b', text_lower) and \
           re.search(r'\b' + re.escape(plural) + r'\b', text_lower):
            
            sg_contexts = _sp_get_contexts(text_lower, singular)
            pl_contexts = _sp_get_contexts(text_lower, plural)
            
            if _sp_validate_difference(sg_contexts, pl_contexts, singular, plural, log):
                if (singular, plural) == ('власть', 'власти'):
                    if _sp_check_contextual_diff(text_lower, singular, plural, 
                                                  ['политика', 'управление', 'государство']):
                        found.append({
                            'singular': singular,
                            'plural': plural,
                            'singular_context': info['singular_meaning'],
                            'plural_context': info['plural_meaning'],
                            'confidence': info['confidence'],
                            'evidence': '已知语义差异对'
                        })
                        log(f"[DEBUG] 发现已知语义差异对: {singular} vs {plural}")
                else:
                    found.append({
                        'singular': singular,
                        'plural': plural,
                        'singular_context': info['singular_meaning'],
                        'plural_context': info['plural_meaning'],
                        'confidence': info['confidence'],
                        'evidence': '已知语义差异对'
                    })
                    log(f"[DEBUG] 发现已知语义差异对: {singular} vs {plural}")
    
    return found


def _sp_extract_nouns(text, log):
    """提取潜在名词"""
    patterns = [
        r'\b[а-яёА-ЯЁ]+(?:ость|ние|ция|сия|тие|ство|ение|ание)\b',
        r'\b[а-яёА-ЯЁ]+(?:тель|ник|щик|чик|арь|ырь)\b',
        r'\b[а-яёА-ЯЁ]+(?:ка|га|ба|па|та|да|за|са|ра|ла|на|ма)\b',
        r'\b[а-яёА-ЯЁ]+[а-яё]{3,}\b'
    ]
    
    nouns = set()
    text_lower = text.lower()
    
    for pattern in patterns:
        nouns.update(re.findall(pattern, text_lower))
    
    # 排除词
    excluded = {
        'это', 'что', 'как', 'где', 'когда', 'почему', 'зачем', 'откуда', 'куда',
        'который', 'которая', 'которое', 'которые', 'такой', 'такая', 'такое', 'такие',
        'этот', 'эта', 'это', 'эти', 'тот', 'та', 'то', 'те', 'место', 'места',
        'мой', 'моя', 'моё', 'мои', 'твой', 'твоя', 'твоё', 'твои',
        'его', 'её', 'их', 'наш', 'наша', 'наше', 'наши', 'ваш', 'ваша', 'ваше', 'ваши',
        'жизнь', 'жизни', 'жизнью', 'жизням'
    }
    
    function_words = {
        'в', 'к', 'с', 'на', 'за', 'под', 'над', 'от', 'до', 'по', 'при', 'про',
        'без', 'для', 'через', 'между', 'и', 'а', 'но', 'или', 'не', 'же', 'ли', 'бы'
    }
    
    filtered = [n for n in nouns if n not in excluded and len(n) > 3 and n not in function_words]
    
    return filtered


def _sp_identify_relationships(nouns, text, log):
    """识别单复数关系"""
    pairs = []
    text_lower = text.lower()
    
    # 复数规则
    plural_rules = [
        (r'([а-яё]+)ость$', r'\1ости'),
        (r'([а-яё]+)ние$', r'\1ния'),
        (r'([а-яё]*[бвгджзклмнпрстфхцчшщ])$', r'\1ы'),
        (r'([а-яё]*[жчшщ])$', r'\1и'),
        (r'([а-яё]+)ь$', r'\1и'),
        (r'([а-яё]+)о$', r'\1а'),
        (r'([а-яё]+)е$', r'\1я'),
        (r'([а-яё]+)а$', r'\1ы'),
        (r'([а-яё]+)я$', r'\1и'),
    ]
    
    noun_set = set(re.findall(r'\b[а-яё]+\b', text_lower))
    
    for noun in nouns:
        for sg_pattern, pl_replacement in plural_rules:
            if re.match(sg_pattern, noun):
                potential_plural = re.sub(sg_pattern, pl_replacement, noun)
                if potential_plural in noun_set and potential_plural != noun:
                    if _sp_check_contextual_difference(text_lower, noun, potential_plural):
                        pairs.append({
                            'singular': noun,
                            'plural': potential_plural,
                            'confidence': 0.75
                        })
                        log(f"[DEBUG] 识别到单复数关系: {noun} -> {potential_plural}")
                    break
    
    return pairs


def _sp_analyze_semantics(pairs, text, log):
    """严格分析语义差异"""
    semantic_pairs = []
    text_lower = text.lower()
    
    for pair in pairs:
        singular = pair['singular']
        plural = pair['plural']
        
        log(f"[DEBUG] 严格分析语义差异: {singular} vs {plural}")
        
        sg_contexts = _sp_get_contexts(text_lower, singular)
        pl_contexts = _sp_get_contexts(text_lower, plural)
        
        if not sg_contexts or not pl_contexts:
            continue
        
        analysis = _sp_compare_contexts(sg_contexts, pl_contexts, singular, plural)
        
        if analysis['has_semantic_difference']:
            semantic_pairs.append({
                'singular': singular,
                'plural': plural,
                'singular_context': analysis['singular_meaning'],
                'plural_context': analysis['plural_meaning'],
                'confidence': analysis['confidence'],
                'evidence': analysis['evidence']
            })
            
            log(f"[DEBUG] 发现语义差异: {singular}({analysis['singular_meaning']}) vs {plural}({analysis['plural_meaning']})")
    
    return semantic_pairs


def _sp_get_contexts(text, word, window=5):
    """获取词汇上下文"""
    contexts = []
    words = re.split(r'\s+', text)
    
    for i, w in enumerate(words):
        if w == word:
            start = max(0, i - window)
            end = min(len(words), i + window + 1)
            context = ' '.join(words[start:end])
            contexts.append(context.strip())
    
    return contexts


def _sp_validate_difference(sg_contexts, pl_contexts, sg_word, pl_word, log):
    """验证上下文差异"""
    # 特别处理"место/места"
    if sg_word == 'место' and pl_word == 'места':
        if _sp_check_same_context(sg_contexts, pl_contexts):
            log(f"[DEBUG] 排除误判: {sg_word} vs {pl_word} 出现在相同上下文中")
            return False
    
    # 检查所有格结构
    if _sp_check_possessives(sg_contexts, pl_contexts):
        log(f"[DEBUG] 排除误判: {sg_word} vs {pl_word} 出现在所有格结构中")
        return False
    
    return True


def _sp_check_same_context(sg_contexts, pl_contexts):
    """检查是否在相同上下文"""
    for sg_ctx in sg_contexts:
        for pl_ctx in pl_contexts:
            if _sp_context_similarity(sg_ctx, pl_ctx) > 0.8:
                return True
    return False


def _sp_context_similarity(ctx1, ctx2):
    """计算上下文相似度"""
    words1 = set(re.findall(r'\w+', ctx1))
    words2 = set(re.findall(r'\w+', ctx2))
    
    if not words1 or not words2:
        return 0.0
    
    common = words1.intersection(words2)
    total = words1.union(words2)
    
    return len(common) / len(total) if total else 0.0


def _sp_check_possessives(sg_contexts, pl_contexts):
    """检查所有格结构"""
    possessive_patterns = [
        r'\b(?:мой|моя|моё|мои|твой|твоя|твоё|твои|его|её|их|наш|наша|наше|наши|ваш|ваша|ваше|ваши)\b',
        r'\b(?:этот|эта|это|эти|тот|та|то|те)\b'
    ]
    
    pattern = '|'.join(possessive_patterns)
    sg_has = any(re.search(pattern, ctx) for ctx in sg_contexts)
    pl_has = any(re.search(pattern, ctx) for ctx in pl_contexts)
    
    return sg_has and pl_has


def _sp_check_contextual_difference(text, singular, plural):
    """检查单复数是否出现在不同语义上下文"""
    sg_contexts = _sp_get_contexts(text, singular)
    pl_contexts = _sp_get_contexts(text, plural)
    
    for sg_ctx in sg_contexts:
        for pl_ctx in pl_contexts:
            if _sp_context_similarity(sg_ctx, pl_ctx) < 0.4:
                return True
    
    return False


def _sp_check_contextual_diff(text, singular, plural, context_keywords):
    """检查是否出现在不同语义上下文中"""
    pattern = '|'.join(re.escape(k) for k in context_keywords)
    sg_proximity = bool(re.search(rf'\b{re.escape(singular)}\b.{{0,50}}(?:{pattern})', text))
    pl_proximity = bool(re.search(rf'\b{re.escape(plural)}\b.{{0,50}}(?:{pattern})', text))
    
    return sg_proximity and pl_proximity


def _sp_compare_contexts(sg_contexts, pl_contexts, sg_word, pl_word):
    """比较语义上下文"""
    indicators = {
        'abstract_concepts': ['понятие', 'идея', 'концепция', 'принцип', 'теория', 'философия', 'мысль'],
        'concrete_objects': ['предмет', 'вещь', 'объект', 'материал', 'изделие', 'товар', 'продукт'],
        'actions': ['действие', 'процесс', 'деятельность', 'работа', 'операция', 'функция'],
        'qualities': ['качество', 'свойство', 'характеристика', 'особенность', 'черта'],
        'institutions': ['организация', 'учреждение', 'институт', 'орган', 'структура', 'система'],
        'collections': ['множество', 'совокупность', 'группа', 'набор', 'комплекс', 'ряд'],
        'skills': ['умение', 'навык', 'мастерство', 'искусство', 'талант', 'дар'],
        'documents': ['документ', 'справка', 'бумага', 'заявление', 'отчет', 'акт'],
        'temporal': ['время', 'период', 'эпоха', 'момент', 'час', 'день'],
        'spatial': ['место', 'пространство', 'территория', 'область', 'зона']
    }
    
    sg_scores = defaultdict(float)
    pl_scores = defaultdict(float)
    
    for ctx in sg_contexts:
        for category, keywords in indicators.items():
            for kw in keywords:
                if kw in ctx:
                    sg_scores[category] += 1
    
    for ctx in pl_contexts:
        for category, keywords in indicators.items():
            for kw in keywords:
                if kw in ctx:
                    pl_scores[category] += 1
    
    semantic_diff = _sp_calc_semantic_diff(sg_scores, pl_scores)
    has_diff = semantic_diff > 0.7
    confidence = min(semantic_diff * 1.2, 0.95)
    
    # 特别处理
    if (sg_word, pl_word) in [('власть', 'власти'), ('бумага', 'бумаги'), ('время', 'времена')]:
        if _sp_check_same_context(sg_contexts, pl_contexts):
            has_diff = False
            confidence = 0.0
    
    sg_meaning = _sp_infer_meaning(sg_contexts, sg_word, sg_scores)
    pl_meaning = _sp_infer_meaning(pl_contexts, pl_word, pl_scores)
    
    if has_diff:
        if sg_meaning == pl_meaning or '含义不明' in [sg_meaning, pl_meaning]:
            has_diff = False
            confidence = 0.0
    
    return {
        'has_semantic_difference': has_diff,
        'confidence': confidence,
        'singular_meaning': sg_meaning,
        'plural_meaning': pl_meaning,
        'evidence': f'语义差异度: {semantic_diff:.2f}'
    }


def _sp_calc_semantic_diff(scores1, scores2):
    """计算语义差异度"""
    all_categories = set(scores1.keys()) | set(scores2.keys())
    
    if not all_categories:
        return 0.0
    
    diffs = []
    for category in all_categories:
        s1 = scores1.get(category, 0)
        s2 = scores2.get(category, 0)
        total = s1 + s2
        
        if total > 0:
            diff = abs(s1 - s2) / total
            diffs.append(diff)
    
    return sum(diffs) / len(diffs) if diffs else 0.0


def _sp_infer_meaning(contexts, word, scores):
    """推断含义"""
    if not scores:
        return "含义不明"
    
    top_category = max(scores.items(), key=lambda x: x[1])
    if top_category[1] == 0:
        return "含义不明"
    
    meaning_map = {
        'abstract_concepts': '抽象概念',
        'concrete_objects': '具体物品',
        'actions': '行为动作',
        'qualities': '品质特征',
        'institutions': '机构组织',
        'collections': '集合概念',
        'skills': '技能才能',
        'documents': '文件资料',
        'temporal': '时间概念',
        'spatial': '空间概念'
    }
    
    return meaning_map.get(top_category[0], '一般概念')


def _sp_merge_deduplicate(known, dynamic, log):
    """合并并去重"""
    all_pairs = []
    seen = set()
    
    for pair in known:
        key = (pair['singular'], pair['plural'])
        if key not in seen:
            seen.add(key)
            all_pairs.append(pair)
    
    for pair in dynamic:
        key = (pair['singular'], pair['plural'])
        if key not in seen:
            if key == ('место', 'места'):
                log("[DEBUG] 排除误判: место/места")
                continue
            seen.add(key)
            all_pairs.append(pair)
    
    return all_pairs


# ==================== 规则 7: 多种复数形式检测 ====================
def detect_russian_multiple_plural_forms_enhanced(content_list, required_pairs, debug=False):
    """
    检测一个名词的两种不同含义的复数形式
    结合"已知知识库"和"动态发现"两种策略
    
    Args:
        content_list: 文本内容列表
        required_pairs: 要求的复数形式对数量
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    log(f"[DEBUG] 开始检测, required_pairs={required_pairs}")

    # 输入验证
    if not content_list or content_list == "INVALID":
        return 0, "❌ 输入文本无效"
    
    try:
        required_pairs = int(required_pairs)
    except (ValueError, TypeError):
        return 0, "❌ required_pairs 必须是整数"

    text = ' '.join(str(item) for item in content_list if item).lower()
    if not text.strip():
        return 1 if required_pairs == 0 else 0, "✅ 内容为空"

    # 策略1: 检查已知知识库
    known_pairs = _mpl_check_known(text, log)
    log(f"[DEBUG] 策略1(知识库)发现 {len(known_pairs)} 对")

    # 策略2: 动态发现
    dynamic_pairs = []
    morph, available = LibraryManager.get_morph()
    
    if available:
        log("[INFO] Pymorphy2 库加载成功，将用于动态分析")
        dynamic_pairs = _mpl_discover_dynamic(text, morph, log)
        log(f"[DEBUG] 策略2(动态发现)发现 {len(dynamic_pairs)} 对")
    else:
        if debug:
            log("[WARNING] Pymorphy2 库未安装，动态发现功能将受限")

    # 合并去重
    all_found = known_pairs
    seen_bases = {p['base_noun'] for p in known_pairs}
    for d_pair in dynamic_pairs:
        if d_pair['base_noun'] not in seen_bases:
            all_found.append(d_pair)
            seen_bases.add(d_pair['base_noun'])
    
    # 生成结果
    total = len(all_found)
    if all_found:
        descriptions = [f"'{p['form1']}'({p['meaning1']}) vs '{p['form2']}'({p['meaning2']}) [来源: {p['source']}]" 
                       for p in all_found]
        pairs_text = "; ".join(descriptions)
    else:
        pairs_text = "无"

    if total == required_pairs:
        return 1, f"✅ 找到恰好 {total} 组多种复数形式对 (要求={required_pairs}): {pairs_text}"
    else:
        return 0, f"❌ 找到 {total} 组多种复数形式对 (要求={required_pairs}): {pairs_text}"


def _mpl_check_known(text, log):
    """策略1：检查知识库"""
    knowledge_base = {
        'зуб': {
            'plural1': {'form': 'зубы', 'meaning': '牙齿(生物)', 'context': ['стоматолог', 'врач', 'чистить', 'болит', 'человек', 'челюсть']},
            'plural2': {'form': 'зубья', 'meaning': '锯齿(工具)', 'context': ['пилы', 'шестерни', 'механизм', 'инструмент', 'гребня']}
        },
        'лист': {
            'plural1': {'form': 'листы', 'meaning': '纸张/板材', 'context': ['бумаги', 'металла', 'книги', 'документ', 'стали']},
            'plural2': {'form': 'листья', 'meaning': '树叶', 'context': ['дерева', 'осень', 'зелёные', 'жёлтые', 'растение']}
        },
    }
    
    found = []
    for base_noun, info in knowledge_base.items():
        p1 = info['plural1']
        p2 = info['plural2']
        if re.search(r'\b' + p1['form'] + r'\b', text) and re.search(r'\b' + p2['form'] + r'\b', text):
            contexts1 = _mpl_get_contexts(text, p1['form'])
            contexts2 = _mpl_get_contexts(text, p2['form'])
            if any(c in ctx for ctx in contexts1 for c in p1['context']) and \
               any(c in ctx for ctx in contexts2 for c in p2['context']):
                found.append({
                    'base_noun': base_noun,
                    'form1': p1['form'],
                    'form2': p2['form'],
                    'meaning1': p1['meaning'],
                    'meaning2': p2['meaning'],
                    'source': '知识库'
                })
                log(f"[DEBUG] 知识库发现: {base_noun} -> {p1['form']} vs {p2['form']}")
    return found


def _mpl_discover_dynamic(text, morph, log):
    """策略2：动态发现"""
    words = set(re.findall(r'\b[а-яё-]{3,}\b', text))
    lemmas = defaultdict(list)

    # 词形还原
    for word in words:
        parses = morph.parse(word)
        if parses:
            p = parses[0]
            if 'NOUN' in p.tag:
                lemmas[p.normal_form].append(word)

    found = []
    # 查找多个复数形式
    for base_noun, forms in lemmas.items():
        if len(forms) > 1:
            plurals = [f for f in forms if 'plur' in morph.parse(f)[0].tag]
            if len(plurals) > 1:
                form1, form2 = plurals[0], plurals[1]
                
                # 使用 russtress 获取重音
                stresser, available = LibraryManager.get_stresser()
                if available and stresser:
                    try:
                        stressed1 = stresser.stress(form1)
                        stressed2 = stresser.stress(form2)
                        
                        if stressed1 != stressed2 and '́' in stressed1 and '́' in stressed2:
                            log(f"[DEBUG] 动态发现: {base_noun} -> {form1}({stressed1}) vs {form2}({stressed2})")
                            found.append({
                                'base_noun': base_noun,
                                'form1': form1,
                                'form2': form2,
                                'meaning1': f"复数形式1({stressed1})",
                                'meaning2': f"复数形式2({stressed2})",
                                'source': '动态分析'
                            })
                    except:
                        pass
    return found


def _mpl_get_contexts(text, word, window=5):
    """获取上下文"""
    contexts = []
    for match in re.finditer(r'\b' + re.escape(word) + r'\b', text):
        pre = text[:match.start()].split()
        post = text[match.end():].split()
        start_words = pre[-window:]
        end_words = post[:window]
        contexts.append(' '.join(start_words + [word] + end_words))
    return contexts


# ==================== 规则 8: 派生词检测 ====================
def check_russian_derived_words(content_list, base_verb, required_count, debug=False):
    """
    检测由基础动词派生出的、具有不同前缀的新动词
    
    Args:
        content_list: 文本内容列表
        base_verb: 基础动词（不定式）
        required_count: 要求的派生词数量
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    # 前置检查
    morph, available = LibraryManager.get_morph()
    
    if not available:
        if debug:
            log("[WARNING] Pymorphy2 库未安装，此规则不可用")
        return 0, "❌ 规则评估失败: Pymorphy2 库未安装，无法执行动词派生分析"
    else:
        log("[INFO] Pymorphy2 库加载成功")
    
    if not content_list or content_list == "INVALID":
        return 0, "❌ 输入文本无效"
    
    try:
        required_count = int(required_count)
    except (ValueError, TypeError):
        return 0, f"❌ 'required_count' 必须是有效的整数，但收到了 '{required_count}'"

    text = ' '.join(str(item) for item in content_list if item).lower()
    if not text.strip():
        return 1 if required_count == 0 else 0, f"❌ 内容为空 (要求找到 {required_count} 个派生词)"

    # 准备基础动词的词根
    base_verb_lower = base_verb.lower()
    
    # 词根映射表
    verb_root_map = {
        "идти": ["ход", "йд", "шед"],
        "ехать": ["езж", "ех"],
        "брать": ["бер", "бир"],
        "слать": ["сыл", "сл"],
    }
    
    if base_verb_lower in verb_root_map:
        possible_roots = verb_root_map[base_verb_lower]
        log(f"[DEBUG] 从词根映射表找到基础动词 '{base_verb}' 的词根: {possible_roots}")
    else:
        root = _deriv_get_root(base_verb_lower, morph)
        if not root:
            return 0, f"❌ 无法从基础动词 '{base_verb}' 中提取有效的词根"
        possible_roots = [root]
        log(f"[DEBUG] 提取基础动词 '{base_verb}' 的词根: {possible_roots}")

    # 提取单词
    words = set(re.findall(r'\b[а-яё-]{3,}\b', text))
    log(f"[DEBUG] 从文本中提取到 {len(words)} 个单词")
    
    found = set()

    # 动词前缀
    prefixes = {
        'в', 'во', 'вз', 'взо', 'воз', 'возо', 'вы', 'до', 'за', 'из', 'изо',
        'на', 'над', 'надо', 'не', 'низ', 'низо', 'о', 'об', 'обо', 'от', 'ото',
        'пере', 'по', 'под', 'подо', 'пра', 'пред', 'пре', 'про', 'раз', 'разо',
        'с', 'со', 'су', 'у'
    }

    # 遍历分析
    for word in words:
        parses = morph.parse(word)
        if not parses:
            continue

        lemma = parses[0].normal_form
        
        if 'VERB' not in parses[0].tag and 'INFN' not in parses[0].tag:
            continue

        # 判断是否为派生词
        is_base = (lemma == base_verb_lower) or \
                  (base_verb_lower == "идти" and lemma == "ходить") or \
                  (base_verb_lower == "ехать" and lemma == "ездить")
        
        if not is_base:
            for root in possible_roots:
                if root in lemma:
                    is_derived = False
                    for prefix in prefixes:
                        if lemma.startswith(prefix) and root in lemma.replace(prefix, '', 1):
                            is_derived = True
                            log(f"[DEBUG] 找到派生词: {word} -> {lemma} (前缀: {prefix}, 词根: {root})")
                            break
                    
                    if is_derived:
                        found.add(lemma)
                        break

    # 结果判断
    found_count = len(found)
    found_str = ", ".join(sorted(list(found))) if found else "无"

    log(f"[DEBUG] 总共找到 {found_count} 个派生词")

    if found_count >= required_count:
        return 1, f"✅ 成功找到 {found_count} 个派生词 (要求≥{required_count}): {found_str}"
    else:
        return 0, f"❌ 找到 {found_count} 个派生词 (要求≥{required_count}): {found_str}"


def _deriv_get_root(verb_str, morph):
    """提取动词词根"""
    if morph is None:
        endings = ['ать', 'еть', 'ить', 'ти', 'чь']
        for end in endings:
            if verb_str.endswith(end):
                return verb_str[:-len(end)]
        return verb_str
    
    p = morph.parse(verb_str)
    if not p:
        return verb_str

    infinitive = p[0].normal_form
    if infinitive.endswith(('ать', 'ять')):
        return infinitive[:-3]
    if infinitive.endswith(('ить', 'еть')):
        return infinitive[:-3]
    if infinitive.endswith('ти'):
        return infinitive[:-2]
    if infinitive.endswith('чь'):
        return infinitive[:-2]
    return infinitive


# ==================== 规则 9: 副动词使用检测 ====================
def check_russian_participle_usage(content_list, *args, debug=False):
    """
    检查句子中的副动词使用是否正确
    
    Args:
        content_list: 文本内容列表
        *args: 关键词列表
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    morph, available = LibraryManager.get_morph()
    
    if not available:
        if debug:
            log("[WARNING] Pymorphy2 库未安装")
        return 0, "❌ 规则评估失败: Pymorphy2 库未安装"
    else:
        log("[INFO] Pymorphy2 库加载成功")
    
    if not content_list or len(content_list) == 0 or not content_list[0]:
        return 0, "❌ 输入内容为空"
    if not args or len(args) < 2:
        return 0, "❌ 至少需要两个关键词"
    
    sentence = content_list[0]
    keywords = list(args)
    
    log(f"\n[DEBUG] 检查句子: {sentence}")
    log(f"[DEBUG] 关键词: {keywords}")
    
    try:
        # 获取关键词的体对
        all_target_lemmas = {}
        for keyword in keywords:
            aspect_variants = _part_get_aspect_pair(keyword)
            target_lemmas = set()
            for variant in aspect_variants:
                keyword_parse = morph.parse(variant)
                if keyword_parse:
                    target_lemmas.update(p.normal_form for p in keyword_parse)
            all_target_lemmas[keyword] = target_lemmas
            log(f"[DEBUG] 关键词 '{keyword}' 的体对标准形式: {target_lemmas}")
        
        words = re.findall(r'\b[а-яёА-ЯЁ-]+\b', sentence)
        parses = [morph.parse(w)[0] for w in words]
        
        # 查找所有副动词
        all_gerunds = []
        for word, parse in zip(words, parses):
            if parse.tag.POS == 'GRND':
                word_lemma = parse.normal_form
                aspect = 'perf' if 'perf' in parse.tag else ('impf' if 'impf' in parse.tag else None)
                all_gerunds.append({
                    'word': word,
                    'lemma': word_lemma,
                    'aspect': aspect
                })
                log(f"[DEBUG] 发现副动词: {word} (原形: {word_lemma}, 体: {aspect})")
        
        if not all_gerunds:
            log(f"[DEBUG] 句子中没有找到任何副动词")
        else:
            log(f"[DEBUG] 句子中共找到 {len(all_gerunds)} 个副动词")
        
        # 查找关键词的各种形式
        found_forms = {keyword: {
            'finite_verbs': [],
            'gerunds': [],
            'infinitives': [],
            'other_forms': []
        } for keyword in keywords}
        
        for word, parse in zip(words, parses):
            word_lemma = parse.normal_form
            pos = parse.tag.POS
            aspect = 'perf' if 'perf' in parse.tag else ('impf' if 'impf' in parse.tag else None)
            
            for keyword in keywords:
                if word_lemma in all_target_lemmas[keyword]:
                    if pos == 'GRND':
                        found_forms[keyword]['gerunds'].append({
                            'word': word, 'lemma': word_lemma, 'aspect': aspect
                        })
                        log(f"[DEBUG] ✓ 找到副动词(GRND): {word}")
                    elif pos == 'INFN':
                        found_forms[keyword]['infinitives'].append({
                            'word': word, 'lemma': word_lemma, 'aspect': aspect
                        })
                        log(f"[DEBUG] ⚠ 找到不定式(INFN): {word}")
                    elif pos == 'VERB':
                        found_forms[keyword]['finite_verbs'].append({
                            'word': word, 'lemma': word_lemma, 'aspect': aspect
                        })
                        log(f"[DEBUG] ✓ 找到限定动词(VERB): {word}")
                    else:
                        found_forms[keyword]['other_forms'].append({
                            'word': word, 'lemma': word_lemma, 'aspect': aspect, 'pos': pos
                        })
        
        # 检查缺失的关键词
        missing = []
        for keyword in keywords:
            forms = found_forms[keyword]
            total_found = sum(len(forms[k]) for k in forms.keys())
            if total_found == 0:
                missing.append(keyword)
        
        if missing:
            if all_gerunds:
                gerund_info = ', '.join([f"{g['word']}({g['lemma']})" for g in all_gerunds])
                return 0, f"❌ 关键词 {missing} 未在句中找到。\n\n   句中副动词：{gerund_info}（不来自要求的关键词）"
            return 0, f"❌ 关键词 {missing} 未在句中找到"
        
        # 构建报告
        forms_report = []
        for keyword, forms in found_forms.items():
            parts = []
            if forms['finite_verbs']:
                parts.append(f"限定动词: {', '.join([f['word'] for f in forms['finite_verbs']])}")
            if forms['gerunds']:
                parts.append(f"副动词: {', '.join([f['word'] for f in forms['gerunds']])}")
            if forms['infinitives']:
                parts.append(f"不定式: {', '.join([f['word'] for f in forms['infinitives']])}")
            if forms['other_forms']:
                # ✅ 修复：拆分表达式
                other_forms_str = ', '.join([f"{f['word']}({f['pos']})" for f in forms['other_forms']])
                parts.append(f"其他: {other_forms_str}")
            
            if parts:
                forms_report.append(f"'{keyword}': {', '.join(parts)}")

        
        forms_report_str = '\n   '.join(forms_report) if forms_report else "未找到任何形式"
        
        # 检查是否有副动词
        if len(all_gerunds) == 0:
            return 0, f"❌ 句子中未找到副动词。\n\n   关键词使用情况：\n   {forms_report_str}"
        
        # 检查关键词是否以独立形式使用
        keywords_without_main = []
        keywords_only_inf = []
        
        for keyword, forms in found_forms.items():
            has_finite = len(forms['finite_verbs']) > 0
            has_gerund = len(forms['gerunds']) > 0
            has_infinitive = len(forms['infinitives']) > 0
            
            if not has_finite and not has_gerund:
                keywords_without_main.append(keyword)
                if has_infinitive:
                    keywords_only_inf.append({
                        'keyword': keyword,
                        'infinitive_word': forms['infinitives'][0]['word']
                    })
        
        if keywords_without_main:
            error_msg = f"❌ 关键词 {keywords_without_main} 未以独立形式使用。\n\n"
            
            if keywords_only_inf:
                inf_examples = ', '.join([f"'{item['infinitive_word']}'" for item in keywords_only_inf])
                error_msg += f"   不定式 {inf_examples} 依附于其他动词，不是独立动作。\n\n"
            
            error_msg += f"   关键词使用情况：\n"
            for keyword, forms in found_forms.items():
                if forms['finite_verbs']:
                    error_msg += f"   ✓ '{keyword}': 限定动词 {', '.join([f['word'] for f in forms['finite_verbs']])}\n"
                elif forms['gerunds']:
                    error_msg += f"   ✓ '{keyword}': 副动词 {', '.join([f['word'] for f in forms['gerunds']])}\n"
                elif forms['infinitives']:
                    error_msg += f"   ✗ '{keyword}': 不定式 {forms['infinitives'][0]['word']}\n"
            
            if all_gerunds:
                gerund_info = ', '.join([f"{g['word']}({g['lemma']})" for g in all_gerunds])
                error_msg += f"\n   句中副动词：{gerund_info}（不来自关键词）"
            
            return 0, error_msg
        
        # 成功
        gerund_info = ', '.join([f"{g['word']}({g['lemma']}, {g['aspect']})" for g in all_gerunds])
        
        keyword_main_forms = []
        for keyword, forms in found_forms.items():
            for fv in forms['finite_verbs']:
                keyword_main_forms.append(f"{fv['word']}(限定-{keyword})")
            for gv in forms['gerunds']:
                keyword_main_forms.append(f"{gv['word']}(副动-{keyword})")
        
        keyword_forms_info = ', '.join(keyword_main_forms)
        
        return 1, f"✅ 副动词使用正确。\n\n   关键词：{keyword_forms_info}\n   句中副动词：{gerund_info}"
    
    except Exception as e:
        log(f"[ERROR] 异常: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 0, f"❌ 函数执行异常: {e}"


def _part_get_aspect_pair(verb):
    """获取动词体对"""
    pairs = {
        'пить': {'пить', 'выпить', 'выпивать', 'попить'},
        'выпить': {'пить', 'выпить', 'выпивать'},
        'выпивать': {'пить', 'выпить', 'выпивать'},
        'попить': {'пить', 'попить'},
        'читать': {'читать', 'прочитать', 'почитать'},
        'прочитать': {'читать', 'прочитать'},
        'почитать': {'читать', 'почитать'},
        'делать': {'делать', 'сделать'},
        'сделать': {'делать', 'сделать'},
        'отдыхать': {'отдыхать', 'отдохнуть'},
        'отдохнуть': {'отдыхать', 'отдохнуть'},
        'слушать': {'слушать', 'послушать'},
        'послушать': {'слушать', 'послушать'},
        'говорить': {'говорить', 'сказать', 'поговорить'},
        'сказать': {'говорить', 'сказать'},
        'поговорить': {'говорить', 'поговорить'},
        'гулять': {'гулять', 'погулять'},
        'погулять': {'гулять', 'погулять'},
        'смотреть': {'смотреть', 'посмотреть'},
        'посмотреть': {'смотреть', 'посмотреть'},
        'ужинать': {'ужинать', 'поужинать'},
        'поужинать': {'ужинать', 'поужинать'},
        'возвращаться': {'возвращаться', 'вернуться'},
        'вернуться': {'возвращаться', 'вернуться'},
        'начинать': {'начинать', 'начать'},
        'начать': {'начинать', 'начать'},
        'ложиться': {'ложиться', 'лечь'},
        'лечь': {'ложиться', 'лечь'},
        'решать': {'решать', 'решить'},
        'решить': {'решать', 'решить'},
        'садиться': {'садиться', 'сесть'},
        'сесть': {'садиться', 'сесть'},
        'включать': {'включать', 'включить'},
        'включить': {'включать', 'включить'},
        'заканчивать': {'заканчивать', 'закончить'},
        'закончить': {'заканчивать', 'закончить'},
        'писать': {'писать', 'написать'},
        'написать': {'писать', 'написать'},
        'работать': {'работать', 'поработать'},
        'поработать': {'работать', 'поработать'},
        'учить': {'учить', 'выучить', 'изучать', 'изучить'},
        'выучить': {'учить', 'выучить'},
        'изучать': {'изучать', 'изучить'},
        'изучить': {'изучать', 'изучить'},
        'думать': {'думать', 'подумать'},
        'подумать': {'думать', 'подумать'},
        'сидеть': {'сидеть', 'посидеть'},
        'посидеть': {'сидеть', 'посидеть'},
        'есть': {'есть', 'съесть', 'поесть'},
        'съесть': {'есть', 'съесть'},
        'поесть': {'есть', 'поесть'},
        'жить': {'жить', 'прожить', 'пожить'},
        'прожить': {'жить', 'прожить'},
        'пожить': {'жить', 'пожить'},
        'спать': {'спать', 'поспать'},
        'поспать': {'спать', 'поспать'},
        'вставать': {'вставать', 'встать'},
        'встать': {'вставать', 'встать'},
        'идти': {'идти', 'пойти'},
        'пойти': {'идти', 'пойти'},
        'ходить': {'ходить', 'сходить', 'походить'},
        'сходить': {'ходить', 'сходить'},
        'походить': {'ходить', 'походить'},
        'ехать': {'ехать', 'поехать'},
        'поехать': {'ехать', 'поехать'},
        'бежать': {'бежать', 'побежать'},
        'побежать': {'бежать', 'побежать'},
        'брать': {'брать', 'взять'},
        'взять': {'брать', 'взять'},
        'давать': {'давать', 'дать'},
        'дать': {'давать', 'дать'},
        'покупать': {'покупать', 'купить'},
        'купить': {'покупать', 'купить'},
        'продавать': {'продавать', 'продать'},
        'продать': {'продавать', 'продать'},
    }
    verb_lower = verb.lower().strip()
    return pairs.get(verb_lower, {verb_lower})


# ==================== 规则 10: 关键词变形检测（每条内容） ====================
def check_keyword_inflections_each(content_list, keywords, debug=False):
    """
    检查每一条内容是否都包含指定关键词的任何变形
    
    Args:
        content_list: 文本内容列表
        keywords: 关键词列表
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    morph, available = LibraryManager.get_morph()
    
    if not available:
        if debug:
            log("[WARNING] Pymorphy2 库未安装")
        return 0, "❌ pymorphy2 库未安装，无法执行此规则"
    else:
        log("[INFO] Pymorphy2 库加载成功")
    
    if not content_list or content_list == "INVALID":
        return 0, "❌ 输入文本无效"
    if not keywords:
        return 0, "❌ 关键词不能为空"
        
    if not isinstance(content_list, list):
        content_list = [str(content_list)]
    
    keywords = parse_keywords(keywords)
    if not keywords:
        return 0, "❌ 关键词解析失败或为空"
    
    log(f"[DEBUG] 解析后的关键词列表: {keywords}")
    
    try:
        all_target_lemmas = {}
        
        for keyword in keywords:
            aspect_variants = _part_get_aspect_pair(keyword)
            target_lemmas = set()
            for variant in aspect_variants:
                keyword_parse = morph.parse(variant)
                if keyword_parse:
                    target_lemmas.update(p.normal_form for p in keyword_parse)
            all_target_lemmas[keyword] = target_lemmas
            log(f"[DEBUG] 关键词 '{keyword}' 及其体对的标准形式: {target_lemmas}")

        failing_items = []

        for i, item_text in enumerate(content_list):
            if not item_text or not str(item_text).strip():
                failing_items.append(f"第 {i+1} 条内容为空")
                continue

            item_text_str = str(item_text).lower()
            words_in_item = set(re.findall(r'\b[а-яё-]+\b', item_text_str))
            
            missing_keywords = []
            
            for keyword in keywords:
                found_keyword = False
                target_lemmas = all_target_lemmas[keyword]
                
                for word in words_in_item:
                    parses = morph.parse(word)
                    if parses:
                        word_lemma = parses[0].normal_form
                        if word_lemma in target_lemmas:
                            found_keyword = True
                            log(f"[DEBUG] 第 {i+1} 条找到 '{keyword}': {word} → {word_lemma}")
                            break
                
                if not found_keyword:
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                failing_items.append(f"第 {i+1} 条内容未找到关键词 {missing_keywords}")

        if not failing_items:
            keywords_str = "', '".join(keywords)
            return 1, f"✅ 所有 {len(content_list)} 条内容都包含了关键词 '{keywords_str}'"
        else:
            return 0, f"❌ 有 {len(failing_items)}/{len(content_list)} 条内容不满足要求: {'; '.join(failing_items)}"

    except Exception as e:
        log(f"[ERROR] 异常: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 0, f"❌ 函数执行异常: {e}"


# ==================== 规则 11: 连字符单词检测 ====================
def check_hyphenated_words_count(content_list, min_count=1, debug=False):
    """
    检查文本中带连字符的俄语单词数量
    
    Args:
        content_list: 文本内容列表
        min_count: 最小数量（可以是字符串或整数）
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    
    try:
        min_count = int(min_count)
    except (ValueError, TypeError):
        return 0, f"❌ 期望数量必须是整数，实际为 '{min_count}'"
    
    if min_count < 0:
        return 0, f"❌ 期望数量不能为负数，实际为 {min_count}"
    
    if not content_list or not content_list[0]:
        return 0, "❌ 输入内容为空"
    
    text = content_list[0] if isinstance(content_list, list) else str(content_list)
    
    pattern = r'\b[а-яёА-ЯЁ]+-[а-яёА-ЯЁ]+(?:-[а-яёА-ЯЁ]+)*\b'
    matches = re.findall(pattern, text)
    
    count = len(matches)
    
    log(f"[DEBUG] 找到 {count} 个带连字符的单词: {matches}")
    
    if count >= min_count:
        return 1, f"✅ 找到 {count} 个带连字符的单词（≥{min_count}个）: {', '.join(matches)}"
    else:
        return 0, f"❌ 只找到 {count} 个带连字符的单词，要求至少 {min_count} 个。找到的: {', '.join(matches) if matches else '无'}"


# ==================== 规则 12: 性别一致性检测 ====================
def check_russian_gender_agreement(content_list, keyword, required_count, debug=False):
    """
    检查与关键词搭配的动词、形容词等的"性"是否一致
    
    Args:
        content_list: 文本内容列表
        keyword: 关键词（名词）
        required_count: 每条评论要求的最小搭配数量
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    morph, available = LibraryManager.get_morph()
    
    if not available:
        if debug:
            log("[WARNING] Pymorphy2 库未安装")
        return 0, "❌ 规则评估失败: Pymorphy2 库未安装"
    else:
        log("[INFO] Pymorphy2 库加载成功")
    
    if not content_list or content_list == "INVALID":
        return 0, "❌ 输入文本无效"
    
    if not isinstance(content_list, list):
        content_list = [str(content_list)]
        
    try:
        min_agreements = int(required_count)
        if min_agreements <= 0:
            return 1, "✅ 要求找到0个或更少搭配，自动通过"
    except (ValueError, TypeError):
        return 0, f"❌ 'required_count' 必须是有效的整数，但收到了 '{required_count}'"

    keyword_lower = keyword.lower()
    try:
        keyword_parses = morph.parse(keyword_lower)
        if not keyword_parses:
            return 0, f"❌ 词性搭配不符合要求"
        
        noun_parse = None
        for parse in keyword_parses:
            if 'NOUN' in parse.tag:
                noun_parse = parse
                break
        
        if not noun_parse:
            return 0, f"❌ 词性搭配不符合要求"
        
        expected_gender = noun_parse.tag.gender
        if not expected_gender:
            return 0, f"❌ 词性搭配不符合要求"
        
        gender_map = {"masc": "阳性", "femn": "阴性", "neut": "中性"}
        expected_gender_text = gender_map.get(expected_gender, "未知")
        log(f"[DEBUG] 关键词 '{keyword}' 性别: {expected_gender_text}")
        
    except Exception as e:
        return 0, f"❌ 词性搭配不符合要求"

    failing_count = 0
    total_items = len(content_list)

    for i, item_text in enumerate(content_list):
        item_text_str = str(item_text).strip()
        
        # 🔥 修改：不检查是否包含关键词，只检查搭配
        agreement_details = set()
        text_lower = item_text_str.lower()
        
        try:
            words = re.findall(r'\b[а-яё]+\b', text_lower)
            if not words:
                failing_count += 1
                continue
            
            log(f"[DEBUG] 第 {i+1} 条评论找到的词汇: {words}")
            
            word_analyses = {}
            for word in words:
                try:
                    parses = morph.parse(word)
                    if parses:
                        word_analyses[word] = parses[0]
                except:
                    continue
            
            keyword_found = False
            keyword_positions = []
            
            # 查找关键词位置
            for idx, word in enumerate(words):
                if word == keyword_lower:
                    keyword_found = True
                    keyword_positions.append(idx)
                elif word in word_analyses:
                    parse = word_analyses[word]
                    if parse.normal_form == keyword_lower:
                        keyword_found = True
                        keyword_positions.append(idx)
            
            # 🔥 修改：如果没有关键词，当前评论不合格，但不说明是因为缺少关键词
            if not keyword_found:
                failing_count += 1
                log(f"[DEBUG] 第 {i+1} 条评论未找到关键词")
                continue
            
            log(f"[DEBUG] 关键词位置: {keyword_positions}")
            
            # 搜索与关键词搭配的词
            for kw_pos in keyword_positions:
                search_start = max(0, kw_pos - 5)
                search_end = min(len(words), kw_pos + 8)
                
                for word_idx in range(search_start, search_end):
                    if word_idx == kw_pos:
                        continue
                    
                    word = words[word_idx]
                    if word not in word_analyses:
                        continue
                    
                    parse = word_analyses[word]
                    
                    try:
                        # 检查动词
                        if 'VERB' in parse.tag:
                            if 'past' in parse.tag and 'sing' in parse.tag:
                                if hasattr(parse.tag, 'gender') and parse.tag.gender == expected_gender:
                                    agreement_details.add(f"动词'{word}'")
                                    log(f"[DEBUG] 找到匹配: 动词'{word}'")
                                    continue
                            
                            if hasattr(parse.tag, 'gender') and parse.tag.gender == expected_gender:
                                if 'past' in parse.tag or 'pres' in parse.tag:
                                    agreement_details.add(f"动词'{word}'")
                                    log(f"[DEBUG] 找到匹配: 动词'{word}'")
                        
                        # 检查形容词
                        if 'ADJF' in parse.tag or 'ADJS' in parse.tag:
                            if 'nomn' in parse.tag and hasattr(parse.tag, 'gender'):
                                if parse.tag.gender == expected_gender:
                                    agreement_details.add(f"形容词'{word}'")
                                    log(f"[DEBUG] 找到匹配: 形容词'{word}'")
                        
                        # 检查系动词
                        if parse.normal_form == 'быть':
                            if 'past' in parse.tag and hasattr(parse.tag, 'gender'):
                                if parse.tag.gender == expected_gender:
                                    agreement_details.add(f"系动词'{word}'")
                                    log(f"[DEBUG] 找到匹配: 系动词'{word}'")
                        
                        # 检查分词
                        if 'PRTF' in parse.tag or 'PRTS' in parse.tag:
                            if hasattr(parse.tag, 'gender') and parse.tag.gender == expected_gender:
                                agreement_details.add(f"分词'{word}'")
                                log(f"[DEBUG] 找到匹配: 分词'{word}'")
                                
                    except Exception as e:
                        log(f"[DEBUG] 解析词 '{word}' 时出错: {e}")
                        continue
            
            # 特殊处理已知动词
            special_verbs = ['впечатлило', 'вдохновило', 'понравилось', 'получилось', 'оказалось']
            for verb in special_verbs:
                if verb in text_lower:
                    try:
                        verb_parse = morph.parse(verb)[0]
                        if ('VERB' in verb_parse.tag and 
                            'past' in verb_parse.tag and 
                            'sing' in verb_parse.tag and 
                            hasattr(verb_parse.tag, 'gender') and
                            verb_parse.tag.gender == expected_gender):
                            agreement_details.add(f"动词'{verb}'")
                            log(f"[DEBUG] 特殊处理找到匹配: 动词'{verb}'")
                    except:
                        pass
                        
        except Exception as e:
            log(f"[DEBUG] 文本解析出错: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            failing_count += 1
            continue
        
        found_count = len(agreement_details)
        log(f"[DEBUG] 第 {i+1} 条评论找到 {found_count} 个搭配")
        
        # 🔥 修改：如果搭配数量不足，算作不合格
        if found_count < min_agreements:
            failing_count += 1

    # 🔥 修改：简化输出信息
    if failing_count == 0:
        return 1, f"✅ 词性搭配符合要求\n   所有 {total_items} 条文案的动词都与关键词 '{keyword}' 性别一致"
    else:
        return 0, f"❌ 词性搭配不符合要求\n   有 {failing_count}/{total_items} 条文案的动词与关键词 '{keyword}' 性别不一致或搭配不足"



# ==================== 规则 13: 动词时间关系检测 ====================
def check_russian_verb_temporal_relation(content_list, expected_relation, debug=False):
    """
    检查俄语句子中副动词和谓语动词的时间关系
    
    Args:
        content_list: 文本内容列表
        expected_relation: 期望的时间关系
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    morph, available = LibraryManager.get_morph()
    
    if not available:
        if debug:
            log("[WARNING] Pymorphy2 库未安装")
        return 0, "❌ 规则评估失败: Pymorphy2 库未安装"
    else:
        log("[INFO] Pymorphy2 库加载成功")
    
    if not content_list or len(content_list) == 0 or not content_list[0]:
        return 0, "❌ 输入内容为空"
    if not expected_relation:
        return 0, "❌ 期望的时间关系参数为空"
    
    sentence = content_list[0]
    expected_relation = expected_relation.strip()
    
    log(f"\n[DEBUG] 检查句子: {sentence}")
    log(f"[DEBUG] 期望的时间关系: {expected_relation}")

    try:
        # 时间顺序标志词
        temporal_markers = [
            'после того как', 'после', 'потом', 'затем', 'сначала', 
            'сперва', 'прежде чем', 'перед тем как'
        ]
        
        # 同时关系标志词
        simultaneous_markers = [
            'одновременно', 'в то же время', 'в это время', 'тем временем'
        ]
        
        sentence_lower = sentence.lower()
        has_temporal = any(m in sentence_lower for m in temporal_markers)
        has_simultaneous = any(m in sentence_lower for m in simultaneous_markers)
        
        log(f"[DEBUG] 时间顺序标志词: {has_temporal}")
        log(f"[DEBUG] 同时关系标志词: {has_simultaneous}")
        
        words = re.findall(r'\b[а-яёА-ЯЁ-]+\b', sentence)
        parses = [morph.parse(w)[0] for w in words]
        
        main_verbs = []
        subordinate_verbs = []
        participles = []
        all_verbs = []
        
        subordinate_markers = ['после того как', 'когда', 'если', 'который', 'которая', 'которое', 'которые']
        
        for word_index, (word, parse) in enumerate(zip(words, parses)):
            pos = parse.tag.POS
            aspect = 'perf' if 'perf' in parse.tag else ('impf' if 'impf' in parse.tag else None)
            
            word_position = sentence.find(word)
            in_subordinate = False
            
            for marker in subordinate_markers:
                if marker in sentence_lower:
                    marker_pos = sentence_lower.find(marker)
                    comma_after = sentence.find(',', marker_pos)
                    if comma_after > 0:
                        if marker_pos < word_position < comma_after:
                            in_subordinate = True
                            break
            
            if pos == 'GRND':
                participles.append({
                    'word': word,
                    'lemma': parse.normal_form,
                    'aspect': aspect,
                    'parse': parse,
                    'position': word_index
                })
                log(f"[DEBUG] 找到副动词: {word} (lemma: {parse.normal_form}, aspect: {aspect})")
            
            elif pos == 'VERB':
                verb_info = {
                    'word': word,
                    'lemma': parse.normal_form,
                    'aspect': aspect,
                    'parse': parse,
                    'position': word_index,
                    'in_subordinate': in_subordinate
                }
                all_verbs.append(verb_info)
                
                if in_subordinate:
                    subordinate_verbs.append(verb_info)
                    log(f"[DEBUG] 找到从句动词: {word}")
                else:
                    main_verbs.append(verb_info)
                    log(f"[DEBUG] 找到主句动词: {word}")
        
        if not all_verbs:
            return 0, "❌ 句子中未找到任何动词，无法判断时间关系"
        
        actual_relation = None
        explanation = []
        
        # 判断时间关系
        if has_simultaneous:
            actual_relation = "Одновременные отношения"
            explanation.append(f"句子使用了同时关系标志词")
        
        if not actual_relation and has_temporal:
            perf_verbs = [v for v in all_verbs if v['aspect'] == 'perf']
            if len(perf_verbs) >= 2:
                actual_relation = "Хронологическая последовательность"
                explanation.append(f"句子使用了时间顺序标志词，并且有多个完成体动词")
            elif perf_verbs:
                actual_relation = "Хронологическая последовательность"
                explanation.append(f"句子使用了时间顺序标志词")
        
        if not actual_relation and participles:
            target_main = main_verbs if main_verbs else all_verbs[:1]
            
            if target_main:
                participle = participles[0]
                main_verb = target_main[0]
                
                main_aspect = main_verb['aspect']
                part_aspect = participle['aspect']
                
                log(f"[DEBUG] 副动词体: {part_aspect}, 主句动词体: {main_aspect}")
                
                if main_aspect == 'impf' and part_aspect == 'impf':
                    actual_relation = "Одновременные отношения"
                    explanation.append(f"副动词和谓语动词都是未完成体")
                elif part_aspect == 'perf':
                    actual_relation = "Хронологическая последовательность"
                    explanation.append(f"副动词是完成体")
                elif part_aspect == 'impf' and main_aspect == 'perf':
                    actual_relation = "Одновременные отношения"
                    explanation.append(f"背景-事件关系")
                elif part_aspect == 'perf' and main_aspect == 'impf':
                    actual_relation = "Хронологическая последовательность"
                    explanation.append(f"副动词完成体 + 谓语未完成体")
        
        if not actual_relation and not participles:
            perf_verbs = [v for v in all_verbs if v['aspect'] == 'perf']
            if len(perf_verbs) >= 2 and has_temporal:
                actual_relation = "Хронологическая последовательность"
                explanation.append(f"连续完成体动词 + 时间顺序标志词")
        
        if not actual_relation:
            return 0, "❌ 无法明确判断时间关系"
        
        explanation_text = ' '.join(explanation)
        log(f"[DEBUG] 实际时间关系: {actual_relation}")
        
        if actual_relation == expected_relation:
            return 1, f"✅ 时间关系正确: {actual_relation}。{explanation_text}"
        else:
            return 0, f"❌ 时间关系不符: 期望 '{expected_relation}'，实际为 '{actual_relation}'。{explanation_text}"
    
    except Exception as e:
        log(f"[ERROR] 异常: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 0, f"❌ 函数执行异常: {e}"


# ==================== 规则 14: 俄语形容词类型检测 ====================
def russian_adjective_type_count(content_list, adj_type_str, expected_count_str, debug=False):
    """
    检查俄语文本中指定类型形容词的数量（严格区分副词和短尾形容词）
    
    Args:
        content_list: 文本内容列表
        adj_type_str: 形容词类型（short/long/краткие прилагательные/полные прилагательные）
        expected_count_str: 期望数量
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    morph, available = LibraryManager.get_morph()
    
    if not available:
        log("[ERROR] Pymorphy2 库未能正确加载")
        return 0, "❌ Pymorphy2 库未能正确加载，请检查安装"
    else:
        log("[INFO] Pymorphy2 库加载成功")
    
    if not content_list or content_list == "INVALID":
        return 0, "❌ 输入内容为空"

    adj_type_mapping = {
        'short': {'tag': 'ADJS', 'name': '短尾形容词'},
        'long': {'tag': 'ADJF', 'name': '完全形容词'},
        'краткие прилагательные': {'tag': 'ADJS', 'name': '短尾形容词'},
        'полные прилагательные': {'tag': 'ADJF', 'name': '完全形容词'}
    }
    
    target_info = adj_type_mapping.get(str(adj_type_str).strip().lower())
    if not target_info:
        return 0, f"❌ 类型参数无效: '{adj_type_str}'"
    
    try:
        expected_count = int(expected_count_str)
    except (ValueError, TypeError):
        return 0, f"❌ 数量参数无效: '{expected_count_str}'"

    found_adjectives = []
    filtered_words = []
    
    if not isinstance(content_list, list):
        content_list = [str(content_list)]

    # 扩充代词黑名单
    PRONOUN_BLACKLIST = {
        'все', 'всё', 'весь', 'вся', 'всего', 'всех', 'всем', 'всеми', 'всему', 'всей', 'всею',
        'этот', 'эта', 'это', 'эти', 'этого', 'этой', 'этих', 'этому', 'этим', 'этими', 'этою',
        'тот', 'та', 'то', 'те', 'того', 'той', 'тех', 'тому', 'тем', 'теми', 'тою',
        'такой', 'такая', 'такое', 'такие', 'такого', 'таких', 'такому', 'таким', 'такими', 'такою',
        'который', 'которая', 'которое', 'которые', 'которого', 'которой', 'которых',
        'которому', 'которым', 'которыми', 'которою',
        'каждый', 'каждая', 'каждое', 'каждые', 'каждого', 'каждой', 'каждых',
        'каждому', 'каждым', 'каждыми', 'каждою',
        'любой', 'любая', 'любое', 'любые', 'любого', 'любых', 'любой',
        'любому', 'любым', 'любыми', 'любою',
        'другой', 'другая', 'другое', 'другие', 'другого', 'других', 'другой',
        'другому', 'другим', 'другими', 'другою',
        'сам', 'сама', 'само', 'сами', 'самого', 'самой', 'самих',
        'самому', 'самим', 'самими', 'самою',
        'мой', 'моя', 'моё', 'мои', 'моего', 'моей', 'моих', 'моему', 'моим', 'моими', 'моею',
        'твой', 'твоя', 'твоё', 'твои', 'твоего', 'твоей', 'твоих', 'твоему', 'твоим', 'твоими', 'твоею',
        'его', 'её', 'их',
        'наш', 'наша', 'наше', 'наши', 'нашего', 'нашей', 'наших', 'нашему', 'нашим', 'нашими', 'нашею',
        'ваш', 'ваша', 'ваше', 'ваши', 'вашего', 'вашей', 'ваших', 'вашему', 'вашим', 'вашими', 'вашею',
        'свой', 'своя', 'своё', 'свои', 'своего', 'своей', 'своих', 'своему', 'своим', 'своими', 'своею',
        'какой', 'какая', 'какое', 'какие', 'какого', 'каких', 'какому', 'каким', 'какими', 'какою',
        'чей', 'чья', 'чьё', 'чьи', 'чьего', 'чьей', 'чьих', 'чьему', 'чьим', 'чьими', 'чьею',
        'некоторый', 'некоторая', 'некоторое', 'некоторые',
        'некоторого', 'некоторых', 'некоторому', 'некоторым', 'некоторыми',
        'никакой', 'никакая', 'никакое', 'никакие',
        'никакого', 'никаких', 'никакому', 'никаким', 'никакими',
    }
    
    PURE_ADVERB_BLACKLIST = {
        'просто', 'часто', 'редко', 'долго', 'скоро', 'недавно', 'давно', 
        'медленно', 'много', 'мало', 'немного',
        'очень', 'слишком', 'довольно', 'совсем', 'вполне', 'почти',
        'только', 'лишь', 'даже', 'уже', 'ещё', 'всегда', 'никогда',
        'иногда', 'обычно', 'обязательно', 'специально', 'случайно',
        'вместе', 'отдельно', 'вдруг', 'сразу', 'потом', 'сейчас',
        'снова', 'опять', 'везде', 'всюду', 'нигде', 'никуда',
        'особенно', 'действительно', 'конечно', 'безусловно',
    }
    
    PURE_PREDICATIVE_BLACKLIST = {
        'жаль', 'жалко', 'пора', 'лень', 'недосуг', 'охота', 'неохота',
        'грех', 'стыдно', 'совестно', 'невмоготу', 'невтерпёж', 'невтерпеж',
        'видно', 'слышно',
    }
    
    MODAL_WORDS_BLACKLIST = {
        'можно', 'нельзя', 'надо', 'нужно', 'необходимо', 'должно', 'следует',
    }
    
    CONTEXT_DEPENDENT_WORDS = {
        'хорошо', 'плохо', 'трудно', 'легко', 'интересно', 'скучно',
        'приятно', 'неприятно', 'удобно', 'неудобно', 'важно',
        'возможно', 'невозможно', 'понятно', 'непонятно', 'ясно', 'темно', 'светло',
        'холодно', 'жарко', 'тепло', 'прохладно', 'душно', 'свежо',
        'тихо', 'громко', 'шумно', 'спокойно', 'весело', 'грустно',
        'страшно', 'опасно', 'безопасно', 'полезно', 'вредно',
        'замечательно', 'прекрасно', 'чудесно', 'ужасно', 'странно',
        'ярко', 'тускло', 'быстро', 'живописно', 'красиво',
        'невероятно', 'удивительно', 'поразительно',
    }
    
    NOUN_LEMMA_BLACKLIST = {
        'всё', 'прошлое', 'будущее', 'настоящее', 'главное', 'важное',
        'новое', 'старое', 'хорошее', 'плохое', 'лучшее', 'худшее',
        'вещь', 'дело', 'место', 'время', 'слово', 'лицо'
    }
    
    NOUN_FORM_BLACKLIST = {
        'вещи', 'дела', 'места', 'времена', 'слова', 'лица',
        'глаза', 'руки', 'ноги', 'головы', 'сердца', 'души'
    }
    
    processed_positions = set()

    for seg_idx, text_segment in enumerate(content_list):
        text = str(text_segment)
        if not text.strip():
            continue
        
        log(f"[DEBUG] 处理段落 {seg_idx + 1}")
        
        for match in re.finditer(r'\b[а-яёА-ЯЁ]+\b', text):
            word = match.group(0)
            start_pos = match.start()
            word_lower = word.lower()
            
            # 🔥 特别标记新的
            is_novye = (word_lower == 'новые')
            if is_novye:
                log(f"[DEBUG] ⚠️⚠️⚠️ 开始处理'новые' at pos {start_pos}")
            
            position_key = (seg_idx, start_pos, word_lower)
            if position_key in processed_positions:
                if is_novye:
                    log(f"[DEBUG] ❌ 'новые'因重复被跳过")
                continue
            processed_positions.add(position_key)
            
            if word_lower in PRONOUN_BLACKLIST:
                if is_novye:
                    log(f"[DEBUG] ❌ 'новые'在代词黑名单中")
                filtered_words.append(f"{word}(代词黑名单)")
                continue
            
            if target_info['tag'] == 'ADJS' and word_lower in PURE_PREDICATIVE_BLACKLIST:
                if is_novye:
                    log(f"[DEBUG] ❌ 'новые'在状态词黑名单中")
                filtered_words.append(f"{word}(纯状态词)")
                continue
            
            if target_info['tag'] == 'ADJS' and word_lower in MODAL_WORDS_BLACKLIST:
                if is_novye:
                    log(f"[DEBUG] ❌ 'новые'在情态词黑名单中")
                filtered_words.append(f"{word}(情态词)")
                continue
            
            if word_lower in NOUN_FORM_BLACKLIST:
                if is_novye:
                    log(f"[DEBUG] ❌ 'новые'在名词词形黑名单中")
                filtered_words.append(f"{word}(纯名词词形)")
                continue
            
            if target_info['tag'] == 'ADJS' and word_lower in PURE_ADVERB_BLACKLIST:
                if is_novye:
                    log(f"[DEBUG] ❌ 'новые'在纯副词黑名单中")
                filtered_words.append(f"{word}(纯副词)")
                continue
            
            try:
                parses = morph.parse(word)
                if not parses:
                    if is_novye:
                        log(f"[DEBUG] ❌ 'новые'无法解析")
                    continue
                
                if is_novye:
                    log(f"[DEBUG] 'новые'的解析结果:")
                    for p in parses:
                        log(f"[DEBUG]   POS={p.tag.POS}, lemma={p.normal_form}")
                
                best_parse = None
                has_noun = False
                noun_parse = None
                has_adj = False
                adj_parse = None
                has_adverb = False
                has_adjs = False
                adjs_parse = None
                has_pred = False
                has_pronoun = False
                
                all_noun = all(p.tag.POS == 'NOUN' for p in parses)
                
                if all_noun:
                    if is_novye:
                        log(f"[DEBUG] ❌ 'новые'所有解析都是名词")
                    filtered_words.append(f"{word}(纯名词)")
                    continue
                
                for parse in parses:
                    pos = parse.tag.POS
                    lemma = parse.normal_form
                    
                    log(f"[DEBUG] 词 '{word}' 的解析: POS={pos}, lemma={lemma}")
                    
                    if pos == 'NPRO':
                        has_pronoun = True
                    if pos == 'PRED':
                        has_pred = True
                    if pos == 'ADVB':
                        has_adverb = True
                    if pos == 'ADJS':
                        has_adjs = True
                        adjs_parse = parse
                    if pos == 'NOUN':
                        has_noun = True
                        noun_parse = parse
                    
                    if lemma in PRONOUN_BLACKLIST:
                        has_pronoun = True
                    
                    if target_info['tag'] == 'ADJF':
                        if pos in ['ADJF', 'PRTF']:
                            has_adj = True
                            adj_parse = parse
                            if not best_parse:
                                best_parse = parse
                    elif target_info['tag'] == 'ADJS':
                        if pos == 'ADJS':
                            has_adj = True
                            adj_parse = parse
                            if not best_parse:
                                best_parse = parse
                
                if is_novye:
                    log(f"[DEBUG] 'новые'的标记: has_adj={has_adj}, has_noun={has_noun}, has_pronoun={has_pronoun}")
                
                if has_pronoun:
                    if is_novye:
                        log(f"[DEBUG] ❌ 'новые'被判定为代词")
                    filtered_words.append(f"{word}(代词-词性分析)")
                    continue
                
                # 🔥 修复：只有在没有形容词解析时才排除名词黑名单
                if has_noun and noun_parse and noun_parse.normal_form in NOUN_LEMMA_BLACKLIST:
                    if not has_adj:  # 🔥 关键修复
                        if is_novye:
                            log(f"[DEBUG] ❌ 'новые'在名词黑名单且无形容词解析")
                        filtered_words.append(f"{word}(名词黑名单-{noun_parse.normal_form})")
                        continue
                    else:
                        if is_novye:
                            log(f"[DEBUG] ✓ 'новые'虽在名词黑名单但有形容词解析，保留")
                
                if has_noun and not has_adj and not has_adjs:
                    if is_novye:
                        log(f"[DEBUG] ❌ 'новые'只有名词解析")
                    filtered_words.append(f"{word}(只有名词解析)")
                    continue
                
                if has_noun and noun_parse and noun_parse.normal_form in ['прошлое', 'будущее', 'настоящее']:
                    words_before = re.findall(r'\b[а-яё]+\b', text[:start_pos].lower())
                    prepositions = ['из', 'в', 'к', 'от', 'для', 'про', 'о', 'об', 'на', 'при', 'по']
                    if words_before and words_before[-1] in prepositions:
                        filtered_words.append(f"{word}(介词+名词)")
                        continue
                    if has_adj:
                        best_parse = adj_parse
                
                if best_parse is None:
                    best_parse = parses[0]
                
                main_pos = best_parse.tag.POS
                main_lemma = best_parse.normal_form
                
                if is_novye:
                    log(f"[DEBUG] 'новые' best_parse: POS={main_pos}, lemma={main_lemma}")
                
                if main_pos == 'NPRO':
                    if is_novye:
                        log(f"[DEBUG] ❌ 'новые'的main_pos是NPRO")
                    filtered_words.append(f"{word}(代词-{main_lemma})")
                    continue
                
                # 🔥 完全形容词检测
                if target_info['tag'] == 'ADJF':
                    if main_pos == 'PRTF':
                        if is_novye:
                            log(f"[DEBUG] ✓ 'новые'是形动词")
                        found_adjectives.append(word)
                        continue
                    
                    # 🔥 关键修复：直接接受ADJF
                    if main_pos == 'ADJF':
                        if is_novye:
                            log(f"[DEBUG] ✓✓✓ 'новые'被接受为完全形容词")
                        found_adjectives.append(word)
                        continue
                    
                    # 如果不是ADJF或PRTF
                    if is_novye:
                        log(f"[DEBUG] ❌ 'новые'词性不匹配: {main_pos}")
                    continue
                
                # 短尾形容词检测逻辑
                if target_info['tag'] == 'ADJS':
                    log(f"[DEBUG] 检测短尾形容词: {word}, ADJS={has_adjs}, ADVB={has_adverb}, PRED={has_pred}")
                    
                    if has_pred and not has_adjs:
                        filtered_words.append(f"{word}(PRED-状态词)")
                        continue
                    
                    if has_noun and not has_adjs and not has_adverb:
                        filtered_words.append(f"{word}(名词-无ADJS)")
                        continue
                    
                    if has_adjs and has_adverb:
                        if _adj_is_modifying_adjective(text, start_pos, morph, debug):
                            filtered_words.append(f"{word}(副词-修饰形容词)")
                            continue
                        
                        if _adj_check_action_verb_before(text[:start_pos], morph, debug):
                            filtered_words.append(f"{word}(副词-修饰动作动词)")
                            continue
                        
                        if _adj_check_descriptive_verb_before(text[:start_pos], morph, debug):
                            found_adjectives.append(word)
                            continue
                        
                        if _adj_check_copula_verb_before(text[:start_pos], debug):
                            found_adjectives.append(word)
                            continue
                        
                        found_adjectives.append(word)
                        continue
                    
                    elif has_adverb and not has_adjs and word_lower in CONTEXT_DEPENDENT_WORDS:
                        if _adj_is_modifying_adjective(text, start_pos, morph, debug):
                            filtered_words.append(f"{word}(副词-修饰形容词)")
                            continue
                        
                        if _adj_check_copula_verb_before(text[:start_pos], debug):
                            found_adjectives.append(word)
                            continue
                        
                        if _adj_check_action_verb_before(text[:start_pos], morph, debug):
                            filtered_words.append(f"{word}(副词-修饰动作动词)")
                            continue
                        
                        found_adjectives.append(word)
                        continue
                    
                    elif has_adverb and not has_adjs:
                        filtered_words.append(f"{word}(纯副词)")
                        continue
                    
                    elif has_adjs:
                        found_adjectives.append(word)
                        continue
                    
                    continue

            except Exception as e:
                log(f"[DEBUG] 解析错误 '{word}': {e}")
                if debug:
                    import traceback
                    traceback.print_exc()
                continue

    actual_count = len(found_adjectives)
    adj_name = target_info['name']
    
    if found_adjectives:
        found_lines = []
        for i in range(0, len(found_adjectives), 10):
            found_lines.append(", ".join(found_adjectives[i:i+10]))
        found_str = "\n       ".join(found_lines)
    else:
        found_str = "无"
    
    if actual_count == expected_count:
        status = "✅"
        message = f"{adj_name}数量正确"
    else:
        status = "❌"
        message = f"{adj_name}数量不符"

    explanation = (
        f"{status} {message}\n"
        f"   期望: {expected_count}个\n"
        f"   实际: {actual_count}个\n"
        f"   找到: {found_str}"
    )
    
    if debug and filtered_words:
        log(f"\n[DEBUG] 被过滤的词（前30个）:")
        for i, word in enumerate(filtered_words[:30], 1):
            log(f"  {i}. {word}")
        if len(filtered_words) > 30:
            log(f"[DEBUG] ... 共过滤 {len(filtered_words)} 个词")
    
    return 1 if actual_count == expected_count else 0, explanation


def _adj_is_modifying_adjective(text, word_start_pos, morph, debug=False):
    """检查词后是否紧跟形容词（副词修饰形容词的结构）"""
    log = create_logger(debug)
    
    text_after = text[word_start_pos:]
    current_match = re.match(r'\b[а-яёА-ЯЁ]+\b', text_after)
    if not current_match:
        return False
    
    current_word = current_match.group(0).lower()
    text_after_current = text_after[current_match.end():]
    next_match = re.search(r'\b([а-яёА-ЯЁ]+)\b', text_after_current)
    
    if not next_match:
        return False
    
    next_word = next_match.group(1).lower()
    
    try:
        current_parses = morph.parse(current_word)
        current_has_adjf = any(p.tag.POS == 'ADJF' for p in current_parses)
        current_has_advb = any(p.tag.POS == 'ADVB' for p in current_parses)
        
        next_parses = morph.parse(next_word)
        next_has_adjf = any(p.tag.POS == 'ADJF' for p in next_parses)
        
        log(f"[DEBUG] 检查结构: {current_word}(ADJF={current_has_adjf},ADVB={current_has_advb}) -> {next_word}(ADJF={next_has_adjf})")
        
        if current_has_adjf and next_has_adjf:
            text_after_next = text_after_current[next_match.end():]
            third_match = re.search(r'\b([а-яёА-ЯЁ]+)\b', text_after_next)
            
            if third_match:
                third_word = third_match.group(1).lower()
                third_parses = morph.parse(third_word)
                third_has_noun = any(p.tag.POS == 'NOUN' for p in third_parses)
                
                if third_has_noun:
                    log(f"[DEBUG] ✓ 并列形容词: {current_word} {next_word} {third_word}")
                    return False
            
            if current_has_advb:
                log(f"[DEBUG] 当前词有ADVB，判定为副词")
                return True
            else:
                log(f"[DEBUG] 当前词无ADVB，判定为并列形容词")
                return False
        
        elif current_has_advb and not current_has_adjf and next_has_adjf:
            log(f"[DEBUG] 副词修饰形容词")
            return True
        
        return False
        
    except Exception as e:
        log(f"[DEBUG] 检查修饰关系出错: {e}")
        return False


def _adj_check_descriptive_verb_before(text_before, morph, debug=False):
    """检查词前是否有描述性动词"""
    log = create_logger(debug)
    words_before = re.findall(r'\b[а-яё]+\b', text_before.lower())
    if not words_before:
        return False
    
    descriptive_verbs = {
        'выглядеть', 'выглядит', 'выглядел', 'выглядела', 'выглядело', 'выглядели',
        'казаться', 'кажется', 'казался', 'казалась', 'казалось', 'казались',
        'показаться', 'показался', 'показалась', 'показалось', 'показались',
        'оказаться', 'оказался', 'оказалась', 'оказалось', 'оказались',
        'становиться', 'становится', 'становился', 'становилась', 'становилось',
        'считаться', 'считается', 'считался', 'считалась', 'считалось',
    }
    
    for i in range(min(3, len(words_before))):
        word = words_before[-(i+1)]
        if word in descriptive_verbs:
            return True
        
        try:
            parses = morph.parse(word)
            for parse in parses:
                if parse.normal_form in ['выглядеть', 'казаться', 'показаться', 'оказаться']:
                    return True
        except:
            pass
    return False


def _adj_check_copula_verb_before(text_before, debug=False):
    """检查词前是否有系动词"""
    log = create_logger(debug)
    words_before = re.findall(r'\b[а-яё]+\b', text_before.lower())
    if not words_before:
        return False
    
    copula_verbs = {
        'был', 'была', 'было', 'были', 'есть', 'суть',
        'будет', 'будут', 'будем', 'будешь', 'будете',
        'быть', 'стал', 'стала', 'стало', 'стали',
        'становиться', 'казаться', 'оказаться'
    }
    
    for i in range(min(5, len(words_before))):
        if words_before[-(i+1)] in copula_verbs:
            return True
    return False


def _adj_check_action_verb_before(text_before, morph, debug=False):
    """检查词前是否有动作动词"""
    log = create_logger(debug)
    words_before = re.findall(r'\b[а-яё]+\b', text_before.lower())
    if not words_before:
        return False
    
    copula_verbs = {'был', 'была', 'было', 'были', 'есть', 'суть',
                    'будет', 'будут', 'будем', 'будешь', 'будете',
                    'быть', 'стал', 'стала', 'стало', 'стали'}
    
    descriptive_verbs = {'выглядеть', 'казаться', 'показаться', 'оказаться', 'становиться', 'считаться'}
    
    for i in range(min(3, len(words_before))):
        word = words_before[-(i+1)]
        if word in copula_verbs:
            continue
        
        try:
            parses = morph.parse(word)
            for parse in parses:
                if parse.tag.POS == 'VERB' and parse.normal_form not in descriptive_verbs:
                    return True
        except:
            pass
    return False




# ==================== 规则 15: 段落数量检测 ====================
def check_paragraph_count(content_list, expected_count, debug=False):
    """
    检查段落数量
    
    Args:
        content_list: 文本内容列表
        expected_count: 期望的段落数量
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    if not content_list or content_list == "INVALID":
        return 0, "❌ 输入内容为空"
    
    try:
        expected_count = int(expected_count)
    except (ValueError, TypeError):
        return 0, f"❌ 期望数量 '{expected_count}' 不是有效的整数"
    
    try:
        if isinstance(content_list, list):
            actual_count = len([item for item in content_list if item and str(item).strip()])
        else:
            text = str(content_list)
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            if len(paragraphs) <= 1:
                paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
            actual_count = len(paragraphs)
        
        log(f"[DEBUG] 段落数量: {actual_count}")
        
        if actual_count == expected_count:
            return 1, f"✅ 段落数量正确：{actual_count}个"
        else:
            return 0, f"❌ 段落数量不符：期望{expected_count}个，实际{actual_count}个"
    
    except Exception as e:
        log(f"[ERROR] 异常: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 0, f"❌ 函数执行异常: {e}"


# ==================== 规则 16: 文本总长度检测 ====================
def russian_total_length(content_list, min_length, max_length, debug=False):
    """
    检查俄语文本总词数
    
    Args:
        content_list: 文本内容列表
        min_length: 最小词数
        max_length: 最大词数
        debug: 是否输出调试信息
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    log = create_logger(debug)
    
    if not content_list or content_list == "INVALID":
        return 0, "❌ 输入内容为空"
    
    try:
        min_length = int(min_length)
        max_length = int(max_length)
    except (ValueError, TypeError):
        return 0, f"❌ 长度参数必须是整数"
    
    try:
        if isinstance(content_list, list):
            text = ' '.join(map(str, content_list))
        else:
            text = str(content_list)
        
        words = re.findall(r'\b[а-яёА-ЯЁ]+\b', text)
        actual_count = len(words)
        
        log(f"[DEBUG] 词数: {actual_count}")
        
        if min_length <= actual_count <= max_length:
            if max_length >= 9999:
                return 1, f"✅ 词数符合要求：{actual_count}词（≥{min_length}词）"
            else:
                return 1, f"✅ 词数符合要求：{actual_count}词"
        else:
            if max_length >= 9999:
                return 0, f"❌ 词数不符：{actual_count}词，要求≥{min_length}词"
            else:
                return 0, f"❌ 词数不符：{actual_count}词，要求{min_length}-{max_length}词"
    
    except Exception as e:
        log(f"[ERROR] 异常: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 0, f"❌ 函数执行异常: {e}"
# ==================== 规则 17:俄英单词比例  ====================
def russian_english_ratio(content_list, ratio_a, ratio_b, debug=False):
    """检查俄英比例"""
    log = create_logger(debug)
    
    if not content_list or content_list == "INVALID":
        return 0, "❌ 输入内容为空"
    
    try:
        ratio_a = float(ratio_a)
        ratio_b = float(ratio_b)
    except (ValueError, TypeError):
        return 0, f"❌ 比例参数必须是数字"
    
    if ratio_a <= 0 or ratio_b <= 0:
        return 0, f"❌ 比例参数必须大于0"
    
    try:
        if isinstance(content_list, list):
            text = ' '.join(map(str, content_list))
        else:
            text = str(content_list)
        
        # 清理文本：移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 改进：使用更精确的分词方式
        # 1. 先将标点符号替换为空格（保留连字符）
        text_cleaned = re.sub(r'[^\w\s-]', ' ', text)
        # 2. 分词
        words = text_cleaned.split()
        
        # 过滤出俄语词（纯俄语字符，可含连字符）
        russian_words = []
        for w in words:
            w = w.strip('-')  # 去除首尾连字符
            if w and re.fullmatch(r'[а-яёА-ЯЁ]+(?:-[а-яёА-ЯЁ]+)*', w):
                russian_words.append(w)
        russian_count = len(russian_words)
        
        # 改进：过滤出英语词（纯英语字符，更严格）
        english_words = []
        for w in words:
            w = w.strip('-')  # 去除首尾连字符
            # 只接受纯英语字母，且长度>=2（避免单字母干扰）
            if w and len(w) >= 2 and re.fullmatch(r'[a-zA-Z]+', w):
                english_words.append(w)
            # 特殊处理：单字母但是常见词（I, a）
            elif w and len(w) == 1 and w.lower() in ['i', 'a']:
                english_words.append(w)
        english_count = len(english_words)
        
        log(f"[DEBUG] 俄语词数: {russian_count}")
        log(f"[DEBUG] 英语词数: {english_count}")
        log(f"[DEBUG] 俄语词示例: {russian_words[:10]}")
        log(f"[DEBUG] 英语词示例: {english_words[:10]}")
        log(f"[DEBUG] 要求比例: {ratio_a}:{ratio_b}")
        
        if russian_count == 0 and english_count == 0:
            return 0, f"❌ 未检测到俄语和英语单词"
        
        if english_count == 0 and ratio_b > 0:
            return 0, f"❌ 未检测到英语单词，无法满足 {ratio_a}:{ratio_b} 比例"
        
        if russian_count == 0 and ratio_a > 0:
            return 0, f"❌ 未检测到俄语单词，无法满足 {ratio_a}:{ratio_b} 比例"
        
        expected_ratio = ratio_a / ratio_b
        actual_ratio = russian_count / english_count if english_count > 0 else float('inf')
        
        log(f"[DEBUG] 期望比例值: {expected_ratio:.2f}")
        log(f"[DEBUG] 实际比例值: {actual_ratio:.2f}")
        
        # 增大容差到 ±40%，适应混合语言的不确定性
        tolerance = 0.4
        lower_bound = expected_ratio * (1 - tolerance)
        upper_bound = expected_ratio * (1 + tolerance)
        
        log(f"[DEBUG] 允许范围: {lower_bound:.2f} - {upper_bound:.2f}")
        
        # 格式化比例显示（保留1位小数）
        actual_ratio_str = f"{actual_ratio:.1f}:1"
        expected_ratio_str = f"{expected_ratio:.1f}:1"
        
        if lower_bound <= actual_ratio <= upper_bound:
            return 1, f"✅ 俄英比例符合要求：当前比例 {actual_ratio_str}，期望比例 {expected_ratio_str}"
        else:
            return 0, f"❌ 俄英比例不符：当前比例 {actual_ratio_str}，期望比例 {expected_ratio_str}"
    
    except Exception as e:
        log(f"[ERROR] 异常: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 0, f"❌ 函数执行异常: {e}"


if __name__ == "__main__":
    word = "орган"
    content_list = [
        "12 июня\n\nСегодня я решил записать свои впечатления от отпуска, который оказался удивительно насыщенным. В этом году я отправился в путешествие по Европе, и каждый день приносил что-то новое. Особенно запомнилась экскурсия в Вену, где я посетил знаменитую филармонию. Орган, установленный в главном зале, поразил меня своим величием и чистотой звучания. Я даже задумался, как много труда вложено в создание такого музыкального инструмента, ведь орган — это не просто часть оркестра, а его душа.\n\nПосле Вены я поехал в Прагу, где познакомился с местной кухней и архитектурой. В одном из музеев мне рассказали о важности охраны культурного наследия, и я задумался о том, как каждый орган власти в этих странах заботится о сохранении истории. Это слово здесь приобрело совсем другое значение: орган как учреждение, отвечающее за порядок и развитие общества. Путешествие подарило мне не только яркие эмоции, но и новые знания о мире, его устройстве и многогранности значений привычных слов."
    ]
    rus_stress_homonym_usage(content_list, word, 2)