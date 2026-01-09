import re,ast
import unicodedata
from math import gcd
from collections import Counter,defaultdict

import sys

import subprocess
import os
# ===== 第一部分：先安装 transformers 4.51.3（最高优先级） =====
try:
    import transformers
    required_version = "4.51.3"
    current_version = transformers.__version__
    
    if current_version == required_version:
        transformers_AVAILABLE = True
        print(f"✅ transformers库已安装，版本: {current_version}")
    else:
        print(f"⚠️ transformers版本不匹配，当前: {current_version}，需要: {required_version}")
        raise ImportError("版本不匹配")
        
except ImportError:
    transformers_AVAILABLE = False
    print("transformers库未安装或版本不匹配，正在自动安装...")
    try:
        # 卸载旧版本
        print("正在卸载旧版本...")
        subprocess.run([
            sys.executable, "-m", "pip", "uninstall", 
            "transformers", "tokenizers", "-y"
        ], check=False, capture_output=True)
        
        # 安装新版本
        print("正在安装transformers==4.51.3...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "transformers==4.51.3",
            "tokenizers==0.19.1",
            "--no-cache-dir",
            "--force-reinstall",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        
        # 清除模块缓存
        print("正在清除模块缓存...")
        modules_to_remove = [key for key in sys.modules.keys() if 'transformers' in key or 'tokenizers' in key]
        for module in modules_to_remove:
            del sys.modules[module]
        
        # 重新导入
        print("正在重新导入transformers...")
        import transformers
        import importlib
        importlib.reload(transformers)
        
        new_version = transformers.__version__
        if new_version == "4.51.3":
            transformers_AVAILABLE = True
            print(f"✅ transformers库已成功更新，版本: {new_version}")
        else:
            print(f"⚠️ 版本仍然不匹配: {new_version}")
            print("请重启Python运行时后再次运行此代码")
            transformers_AVAILABLE = False
            
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install transformers==4.51.3 tokenizers==0.19.1")
        print("然后重启Python运行时")
        transformers_AVAILABLE = False


# ===== 第二部分：安装 camel_tools（使用 --no-dependencies） =====
try:
    import camel_tools
    camel_tools_AVAILABLE = True
    print(f"✅ camel_tools已安装，版本: {camel_tools.__version__}")
except ImportError:
    camel_tools_AVAILABLE = False
    print("camel_tools库未安装，正在自动安装...")
    try:
        # 关键：使用 --no-dependencies 避免降级 transformers
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "camel-tools", 
            "--no-dependencies",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        print("camel_tools库安装成功")
        import camel_tools
        camel_tools_AVAILABLE = True
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        camel_tools_AVAILABLE = False

try:
    import tqdm
    tqdm_AVAILABLE = True
    print(f"✅ tqdm已安装，当前版本: {tqdm.__version__}")
    
    # 如果需要强制安装特定版本
    required_version = "4.64.0"
    if tqdm.__version__ != required_version:
        print(f"⚠️ 版本不匹配，正在安装 {required_version}...")
        raise ImportError("需要重新安装")
        
except ImportError:
    tqdm_AVAILABLE = False
    print("正在安装 tqdm==4.64.0...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "tqdm==4.64.0",
            "--no-dependencies",
            "--force-reinstall",  # 强制重装
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        print("✅ tqdm==4.64.0 安装成功")
        import tqdm
        tqdm_AVAILABLE = True
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        tqdm_AVAILABLE = False


# ===== 第三部分：手动安装 camel_tools 的所有依赖（除了 transformers） =====
if camel_tools_AVAILABLE:
    print("\n检查并安装 camel_tools 依赖...")
    
    # camel_tools 的完整依赖列表（从你的 pip install 输出中提取）
    camel_deps = {
        'future': 'future',
        'six': 'six',
        'docopt': 'docopt',
        'cachetools': 'cachetools<=6.0.0',
        'numpy': 'numpy<2',
        'scipy': 'scipy',
        'pandas': 'pandas',
        'sklearn': 'scikit-learn',
        'dill': 'dill',
        'torch': 'torch>=2.0',
        'editdistance': 'editdistance',
        'requests': 'requests',
        'emoji': 'emoji',
        'pyrsistent': 'pyrsistent',
        'tabulate': 'tabulate',
        'tqdm': 'tqdm',
        'muddler': 'muddler',
        'camel_kenlm': 'camel-kenlm<=2025.09.16',
    }
    
    missing_deps = []
    for module_name, package_spec in camel_deps.items():
        try:
            if module_name == 'sklearn':
                __import__('sklearn')
            elif module_name == 'camel_kenlm':
                __import__('camel_kenlm')
            else:
                __import__(module_name)
        except ImportError:
            missing_deps.append(package_spec)
    
    if missing_deps:
        print(f"发现缺失的依赖: {', '.join(missing_deps)}")
        print("正在安装...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                *missing_deps,
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
            ])
            print("✅ 依赖安装完成")
        except Exception as e:
            print(f"⚠️ 部分依赖安装失败: {e}")
            print("请手动安装: pip install " + " ".join(missing_deps))
    else:
        print("✅ 所有依赖已满足")


# ===== 第四部分：验证 transformers 版本未被降级 =====
print("\n验证 transformers 版本...")
try:
    import transformers
    current_version = transformers.__version__
    if current_version == "4.51.3":
        print(f"✅ transformers 版本正确: {current_version}")
    else:
        print(f"⚠️ transformers 版本被降级为: {current_version}")
        print("需要重新安装 transformers 4.51.3")
        
        # 重新安装
        subprocess.run([
            sys.executable, "-m", "pip", "uninstall", 
            "transformers", "tokenizers", "-y"
        ], check=False, capture_output=True)
        
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "transformers==4.51.3",
            "tokenizers==0.19.1",
            "--force-reinstall",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        print("✅ transformers 已重新安装为 4.51.3")
        print("⚠️ 请重启 Python 运行时")
except Exception as e:
    print(f"❌ 验证失败: {e}")


# ===== 第五部分：安装 naftawayh =====
try:
    import naftawayh
    naftawayh_AVAILABLE = True
    print("✅ naftawayh库已安装")
except ImportError:
    naftawayh_AVAILABLE = False
    print("naftawayh库未安装，正在自动安装...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "naftawayh", 
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        print("naftawayh库安装成功，正在导入...")
        import naftawayh
        naftawayh_AVAILABLE = True
        print("✅ naftawayh库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install naftawayh")
        naftawayh_AVAILABLE = False


# ===== 第六部分：配置 Camel 数据库路径 =====
# 自动检测多个可能的路径，兼容不同用户环境
def get_camel_data_base():
    """自动检测 Camel Tools 数据库路径"""
    # 可能的路径列表（按优先级排序）
    possible_paths = [
        # 环境变量指定的路径（最高优先级）
        os.getenv('CAMEL_DATA_BASE'),
        # 用户主目录下的标准位置
        os.path.expanduser('~/.camel_tools'),
        # 常见的拼写变体
        os.path.expanduser('~/.camel_tools/camel_toools'),
        os.path.expanduser('~/.camel_tools/camel_tools'),
    ]
    
    # 检查每个路径是否存在
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    # 如果都不存在，返回标准默认路径（让 camel_tools 使用内置数据库）
    return os.path.expanduser('~/.camel_tools')

CAMEL_DATA_BASE = get_camel_data_base()

# 数据库文件路径
MORPHOLOGY_DB_FILE = os.path.join(CAMEL_DATA_BASE, "data/morphology_db/calima-msa-r13/morphology.db")
DISAMBIG_MODEL_FILE = os.path.join(CAMEL_DATA_BASE, "data/disambig_mle/calima-msa-r13/model.json")

print(f"\n配置的数据库基础路径: {CAMEL_DATA_BASE}")


def verify_camel_data():
    """验证 Camel 数据库文件是否存在"""
    print("\n" + "="*60)
    print("验证 Camel 数据库文件")
    print("="*60)
    
    if not os.path.exists(CAMEL_DATA_BASE):
        print(f"❌ 基础目录不存在: {CAMEL_DATA_BASE}")
        return False
    else:
        print(f"✅ 基础目录存在: {CAMEL_DATA_BASE}")
    
    files_to_check = {
        '形态学数据库': MORPHOLOGY_DB_FILE,
        '消歧器模型': DISAMBIG_MODEL_FILE
    }
    
    all_exist = True
    for name, path in files_to_check.items():
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"✅ {name}: {size_mb:.1f} MB")
            print(f"   路径: {path}")
        else:
            print(f"❌ {name} 不存在")
            print(f"   期望路径: {path}")
            all_exist = False
    
    return all_exist


def load_camel_components():
    """加载 Camel Tools 组件"""
    if not camel_tools_AVAILABLE:
        print("❌ camel_tools 库未成功导入，无法加载组件")
        return None, None, None
    
    try:
        from camel_tools.morphology.database import MorphologyDB
        from camel_tools.morphology.analyzer import Analyzer
        from camel_tools.disambig.mle import MLEDisambiguator
        
        print("\n" + "="*60)
        print("加载 Camel Tools 组件")
        print("="*60)
        
        print("[1/3] 加载形态学数据库...")
        print(f"      从: {MORPHOLOGY_DB_FILE}")
        morphology_db = MorphologyDB(MORPHOLOGY_DB_FILE, 'a')
        print("      ✅ 成功")
        
        print("[2/3] 初始化分析器...")
        analyzer = Analyzer(morphology_db)
        print("      ✅ 成功")
        
        print("[3/3] 加载消歧器...")
        print(f"      从: {DISAMBIG_MODEL_FILE}")
        disambiguator = MLEDisambiguator(analyzer, DISAMBIG_MODEL_FILE)
        print("      ✅ 成功")
        
        print("\n✅ 所有 Camel Tools 组件加载完成")
        
        return morphology_db, analyzer, disambiguator
        
    except Exception as e:
        print(f"\n❌ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def test_camel_tools(analyzer, disambiguator):
    """测试 Camel Tools 功能"""
    if not analyzer or not disambiguator:
        print("❌ 组件未正确加载，跳过测试")
        return False
    
    print("\n" + "="*60)
    print("功能测试")
    print("="*60)
    
    try:
        # 测试1: 单词分析
        print("\n【测试1: 单词分析】")
        test_word = "كتب"
        analyses = analyzer.analyze(test_word)
        print(f"词: {test_word}")
        print(f"  分析数: {len(analyses)}")
        if analyses:
            first = analyses[0]
            print(f"  词根: {first.get('root', 'N/A')}")
            print(f"  词性: {first.get('pos', 'N/A')}")
            print(f"  带音标: {first.get('diac', 'N/A')}")
        
        # 测试2: 句子消歧
        print("\n【测试2: 句子消歧】")
        test_sentence = "كتب الطالب الدرس"
        words = test_sentence.split()
        result = disambiguator.disambiguate(words)
        print(f"句子: {test_sentence}")
        print(f"消歧结果: {len(result)} 个词")
        
        for i, (word, analysis) in enumerate(zip(words, result), 1):
            print(f"  {i}. {word} -> {analysis.get('diac', 'N/A')} [{analysis.get('pos', 'N/A')}]")
        
        print("\n✅ 测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ===== 主执行流程 =====
print("\n" + "="*60)
print("初始化流程")
print("="*60)

morphology_db = None
analyzer = None
disambiguator = None

data_files_exist = verify_camel_data()

if data_files_exist:
    morphology_db, analyzer, disambiguator = load_camel_components()
    
    if analyzer and disambiguator:
        print("\n✅ 初始化完成")
        print("\n可用组件:")
        print("  - morphology_db: 形态学数据库")
        print("  - analyzer: 词形分析器")
        print("  - disambiguator: 句子消歧器")
    else:
        print("\n❌ 组件加载失败")
else:
    print("\n❌ 数据库文件验证失败")

__all__ = [
    'camel_tools_AVAILABLE',
    'transformers_AVAILABLE', 
    'naftawayh_AVAILABLE',
    'morphology_db',
    'analyzer',
    'disambiguator'
]

from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.disambig.mle import MLEDisambiguator


print("\n" + "="*60)
print("初始化脚本执行完毕")
print("="*60)


# ===== 全局数据库实例管理 =====
def get_morphology_db():
    """
    获取形态学数据库实例（单例模式）
    优先使用自定义路径，失败则回退到内置数据库
    """
    if not hasattr(get_morphology_db, '_db_instance'):
        try:
            # 尝试使用自定义路径
            if morphology_db is not None:
                print(f"✅ 使用自定义数据库: {MORPHOLOGY_DB_FILE}")
                get_morphology_db._db_instance = morphology_db
            else:
                # 回退到内置数据库
                print("⚠️  自定义数据库不可用，使用内置数据库")
                get_morphology_db._db_instance = MorphologyDB.builtin_db('calima-msa-r13')
        except Exception as e:
            print(f"❌ 数据库加载失败: {e}")
            # 最后的回退
            try:
                get_morphology_db._db_instance = MorphologyDB.builtin_db('calima-msa-r13')
            except:
                get_morphology_db._db_instance = MorphologyDB.builtin_db()

    return get_morphology_db._db_instance


def get_analyzer():
    """
    获取分析器实例（单例模式）
    """
    if not hasattr(get_analyzer, '_analyzer_instance'):
        try:
            # 优先使用全局analyzer
            if analyzer is not None:
                print("✅ 使用全局分析器")
                get_analyzer._analyzer_instance = analyzer
            else:
                # 创建新的分析器
                db = get_morphology_db()
                get_analyzer._analyzer_instance = Analyzer(db)
        except Exception as e:
            print(f"❌ 分析器初始化失败: {e}")
            # 回退方案
            db = get_morphology_db()
            get_analyzer._analyzer_instance = Analyzer(db)

    return get_analyzer._analyzer_instance


def get_disambiguator():
    """
    获取消歧器实例（单例模式）
    """
    if not hasattr(get_disambiguator, '_disambiguator_instance'):
        try:
            # 优先使用全局disambiguator
            if disambiguator is not None:
                print("✅ 使用全局消歧器")
                get_disambiguator._disambiguator_instance = disambiguator
            else:
                # 创建新的消歧器
                print("⚠️  创建新的消歧器实例")
                get_disambiguator._disambiguator_instance = MLEDisambiguator.pretrained()
        except Exception as e:
            print(f"❌ 消歧器初始化失败: {e}")
            # 回退方案
            get_disambiguator._disambiguator_instance = MLEDisambiguator.pretrained()

    return get_disambiguator._disambiguator_instance


### 1.检测阿语双数形式(仅指两个)
def check_ar_dual_noun_three_stage_lib_based_v18(corresponding_parts, rule_params, mode="total"):
    """三阶段过滤库依赖版v18：添加真正双数词尾检测"""
    
    NON_DUAL_NOUNS = {
        'لبنان', 'عمان', 'السودان', 'أفغانستان', 'باكستان', 'إيران', 'اليابان', 'الأردن', 'فلسطين', 'البحرين', 'عجمان', 'الشارقة', 'أبو', 'دبي',
        'عثمان', 'سليمان', 'لقمان', 'عدنان', 'مروان', 'حسان', 'غسان', 'عفان', 'سفيان', 'حمدان', 'شعبان', 'رمضان', 'شوال', 'رجب', 'صفر', 'جمادى', 'محرم', 'ربيع',
        'عمران', 'غفران', 'إحسان', 'إيمان', 'رضوان', 'عرفان', 'شكران', 'امتنان', 'حنان', 'جنان', 'حسنان', 'منان', 'حليمان', 'نعمان', 'سرحان', 'ريحان', 'بدران', 'زيدان', 'حيدران', 'طارقان', 'ريمان', 'جيهان', 'وجدان', 'أمان',
        'المسيح', 'الرحمن', 'الرحيم', 'الغفار', 'الغفور', 'الصبور', 'الشكور', 'الحليم', 'العليم', 'الحكيم', 'الكريم',
        'الدين', 'الإسلام', 'الملك', 'الأمير', 'الشيخ', 'الإمام', 'الخليفة', 'السلطان',
        'إنسان', 'شيطان', 'سلطان', 'حيوان', 'طوفان', 'بركان', 'ميدان', 'دكان', 'خزان', 'ديوان', 'أذان', 'لسان', 'بستان', 'قرآن', 'فرقان', 'تبيان', 'برهان', 'سرطان', 'طيران', 'فقدان', 'كتمان', 'اطمئنان', 'خسران', 'حرمان', 'نسيان', 'عصيان', 'طغيان', 'كفران', 'عنوان', 'بيان', 'امتحان', 'زمان', 'مكان', 'ضمان',
        'قحطان', 'هاشم', 'أمية', 'تميم', 'طيء', 'كندة', 'لخم', 'جذام',
        'تفسير', 'تاريخ', 'سيرة', 'مقامات', 'رسائل', 'مناقب', 'طبقات',
        'إجازة', 'شهادة', 'رسالة', 'دراسة', 'مقالة', 'محاضرة', 'ندوة', 'مؤتمر', 'معرض', 'مسابقة', 'جائزة', 'منحة', 'بعثة', 'زمالة', 'عضوية'
    }
    
    def preprocess_with_naftawayh(text):
        """使用 Naftawayh 进行文本预处理"""
        try:
            from naftawayh import stopwords
            from camel_tools.tokenizers.word import simple_word_tokenize
            
            if isinstance(stopwords.STOPWORDS, dict):
                arabic_stopwords = set(stopwords.STOPWORDS.keys())
            else:
                arabic_stopwords = set(stopwords.STOPWORDS)
            
            tokens = simple_word_tokenize(text)
            
            filtered_tokens = []
            for token in tokens:
                if re.match(r'[\u0600-\u06FF]+', token):
                    if token not in arabic_stopwords:
                        filtered_tokens.append(token)
            
            return filtered_tokens
            
        except ImportError:
            from camel_tools.tokenizers.word import simple_word_tokenize
            tokens = simple_word_tokenize(text)
            return [token for token in tokens if re.match(r'[\u0600-\u06FF]+', token)]
        except Exception:
            from camel_tools.tokenizers.word import simple_word_tokenize
            tokens = simple_word_tokenize(text)
            return [token for token in tokens if re.match(r'[\u0600-\u06FF]+', token)]
    
    def clean_token_prefixes(token):
        """清理词汇前缀"""
        clean_token = token
        removed_prefix = ""
        prefixes = ['و', 'ف', 'ب', 'ل', 'ك']
        for prefix in prefixes:
            if clean_token.startswith(prefix) and len(clean_token) > len(prefix):
                removed_prefix = prefix
                clean_token = clean_token[len(prefix):]
                break
        return clean_token, removed_prefix
    
    def is_non_dual_noun(token):
        """检查是否在非双数名词黑名单中"""
        clean_token, _ = clean_token_prefixes(token)
        return clean_token in NON_DUAL_NOUNS
    
    def is_real_dual_ending(token, analysis):
        """判断是否是真正的双数词尾"""
        if not token.endswith(('ان', 'ين')):
            return False
        
        if not analysis:
            return True  # 没有分析信息，保守处理
        
        # 简单方法：检查数量标记
        num = analysis.get('num', '')
        if num == 'd':  # dual - 明确的双数标记
            return True
        elif num == 's':  # singular - 单数但以 ان/ين 结尾，是词根的一部分
            return False
        
        # 其他情况认为是真正的双数
        return True
    
    def is_likely_adjective_by_english_suffix_final(stemgloss):
        """最终版：精确判断是否是形容词概念"""
        if not stemgloss:
            return False
        
        stemgloss = stemgloss.lower().strip()
        
        # 明确的形容词后缀（排除容易混淆的 ed, ly, ing, like, ward, wise）
        clear_adjective_suffixes = [
            'ful',      # successful, helpful
            'al',       # professional, national  
            'ical',     # logical, practical
            'able',     # capable, reliable
            'ible',     # possible, flexible
            'ous',      # famous, serious
            'ious',     # curious, obvious
            'ive',      # active, creative
            'ic',       # academic, economic
            'ant',      # important, elegant
            'ent',      # different, excellent
            'ary',      # necessary, temporary
            'ory',      # satisfactory, advisory
            'less',     # helpless, careless
        ]
        
        # 处理分号分割的情况
        if ';' in stemgloss:
            parts = stemgloss.split(';')
            for part in parts:
                part = part.strip()
                if part:
                    for suffix in clear_adjective_suffixes:
                        if part.endswith(suffix):
                            return True
        else:
            # 单个词的情况
            for suffix in clear_adjective_suffixes:
                if stemgloss.endswith(suffix):
                    return True
        
        return False
    
    def is_likely_adverb_by_position_using_lib_flexible(token, position, tokens, disambiguated, analyzer):
        """灵活版：基于阿拉伯语副词位置的灵活性，只有存在副词分析时才检查"""
        
        # 1. 首先检查是否有副词分析（关键前提）
        try:
            all_analyses = analyzer.analyze(token)
            adv_analyses = [a for a in all_analyses if a.get('pos') == 'adv']
            if not adv_analyses:
                return False  # 没有副词分析，直接返回False
            
            # 检查副词分析的语义是否合理
            has_valid_adv_meaning = False
            for adv_analysis in adv_analyses:
                adv_stemgloss = adv_analysis.get('stemgloss', '').lower()
                adverb_concepts = ['also', 'too', 'even', 'still', 'just', 'only', 'again', 'already', 'always', 'never', 'sometimes', 'often']
                if any(concept in adv_stemgloss for concept in adverb_concepts):
                    has_valid_adv_meaning = True
                    break
            
            if not has_valid_adv_meaning:
                return False  # 没有合理的副词语义，返回False
            
        except:
            return False
        
        # 2. 只有通过上面检查，才进入位置模式检查
        try:
            # 模式1: 动词 + 副词 (副词修饰动词，跟在动词后) ✅
            if position > 0:
                prev_disambiguated = disambiguated[position-1]
                if prev_disambiguated and hasattr(prev_disambiguated, 'analyses') and prev_disambiguated.analyses:
                    prev_analysis = prev_disambiguated.analyses[0].analysis
                    prev_pos = prev_analysis.get('pos', '')
                    
                    if prev_pos == 'verb':
                        return True
            
            # 模式2: 副词 + 介词短语 (副词在介词短语前) ✅
            if position < len(disambiguated) - 1:
                next_disambiguated = disambiguated[position+1]
                if next_disambiguated and hasattr(next_disambiguated, 'analyses') and next_disambiguated.analyses:
                    next_analysis = next_disambiguated.analyses[0].analysis
                    next_pos = next_analysis.get('pos', '')
                    
                    # 检查下一个词是否是介词
                    if next_pos == 'prep':
                        return True
                    
                    # 或者检查是否是介词短语的开始（通过stemgloss）
                    next_stemgloss = next_analysis.get('stemgloss', '').lower()
                    prep_concepts = ['in', 'on', 'at', 'to', 'from', 'with', 'by', 'for']
                    if any(concept in next_stemgloss for concept in prep_concepts):
                        return True
            
            # 模式3: 句首副词 (修饰整个句子，位置灵活) ✅
            if position == 0:
                return True
            
            # 模式4: 其他灵活位置 - 由于副词位置很灵活，采用排除法
            if position > 0 and position < len(disambiguated) - 1:
                prev_disambiguated = disambiguated[position-1]
                next_disambiguated = disambiguated[position+1]
                
                if (prev_disambiguated and hasattr(prev_disambiguated, 'analyses') and prev_disambiguated.analyses and
                    next_disambiguated and hasattr(next_disambiguated, 'analyses') and next_disambiguated.analyses):
                    
                    prev_analysis = prev_disambiguated.analyses[0].analysis
                    next_analysis = next_disambiguated.analyses[0].analysis
                    
                    prev_pos = prev_analysis.get('pos', '')
                    next_pos = next_analysis.get('pos', '')
                    
                    # 如果前后都是名词且都是双数词尾，可能是错误位置
                    prev_token = tokens[position-1]
                    next_token = tokens[position+1]
                    
                    if (prev_pos in ['noun', 'noun_prop'] and next_pos in ['noun', 'noun_prop'] and
                        prev_token.endswith(('ان', 'ين')) and next_token.endswith(('ان', 'ين'))):
                        return False  # 明显错误的位置
            
            # 其他情况，由于副词位置灵活，倾向于认为是副词
            return True
            
        except:
            pass
        
        return False
    
    def is_verbal_noun_masdar(analysis):
        """判断是否是动词性名词"""
        if not analysis:
            return False
        
        stemcat = analysis.get('stemcat', '')
        if 'N0_Nh' in stemcat:
            return True
        
        root = analysis.get('root', '')
        if root and '#' in root:
            return True
        
        stemgloss = analysis.get('stemgloss', '').lower()
        if stemgloss:
            verbal_concepts = [
                'purchase', 'purchasing', 'buying', 'going', 'departure', 'arrival',
                'reading', 'writing', 'studying', 'eating', 'drinking', 'sleeping',
                'working', 'playing', 'running', 'start', 'begin', 'end', 'finish'
            ]
            if any(concept in stemgloss for concept in verbal_concepts):
                return True
        
        return False
    
    def get_best_analysis_for_token(token, position, tokens, disambiguated_word, analyzer):
        """获取token的最佳分析"""
        
        if not disambiguated_word or not hasattr(disambiguated_word, 'analyses') or not disambiguated_word.analyses:
            return None
        
        return disambiguated_word.analyses[0].analysis
    
    def is_likely_modification_relationship_lib_based_v2(position, tokens, disambiguated, analyzer):
        """基于库的修饰关系判断v2：使用灵活的副词检测"""
        
        if position <= 0:
            return False
        
        try:
            prev_token = tokens[position-1]
            current_token = tokens[position]
            
            # 检查前词是否可能是副词（基于位置和库分析）
            if is_likely_adverb_by_position_using_lib_flexible(prev_token, position-1, tokens, disambiguated, analyzer):
                return False  # 前词是副词，不是修饰关系
            
            # 获取前词和当前词的分析
            if position-1 < len(disambiguated) and position < len(disambiguated):
                prev_disambiguated = disambiguated[position-1]
                current_disambiguated = disambiguated[position]
                
                prev_analysis = get_best_analysis_for_token(prev_token, position-1, tokens, prev_disambiguated, analyzer)
                current_analysis = get_best_analysis_for_token(current_token, position, tokens, current_disambiguated, analyzer)
                
                if not prev_analysis or not current_analysis:
                    return False
                
                prev_pos = prev_analysis.get('pos', '')
                current_pos = current_analysis.get('pos', '')
                
                # 如果前一个词是动词性名词，当前词不是修饰关系
                if is_verbal_noun_masdar(prev_analysis):
                    return False
                
                # 双数词尾的修饰关系（最可靠）
                if (prev_token.endswith(('ان', 'ين')) and 
                    current_token.endswith(('ان', 'ين')) and 
                    prev_pos in ['noun', 'noun_prop']):
                    return True
                
                # 明确的形容词修饰名词
                if prev_pos == 'noun' and current_pos == 'adj':
                    return True
                
                # 其他情况暂时不认为是修饰关系
                return False
            
            return False
            
        except Exception:
            return False
    
    def is_likely_noun_not_adjective_by_grammar_lib_based_v2(position, tokens, disambiguated, analyzer, current_token):
        """基于库的语法验证v2：使用灵活的副词检测"""
        
        # 获取当前词的分析
        if position >= len(disambiguated):
            return True
        
        current_disambiguated = disambiguated[position]
        best_analysis = get_best_analysis_for_token(current_token, position, tokens, current_disambiguated, analyzer)
        
        if not best_analysis:
            return True
        
        # 更精确的修饰关系检查
        if position > 0:
            prev_token = tokens[position-1]
            
            # 获取前词分析
            if position-1 < len(disambiguated):
                prev_disambiguated = disambiguated[position-1]
                if prev_disambiguated and hasattr(prev_disambiguated, 'analyses') and prev_disambiguated.analyses:
                    prev_analysis = prev_disambiguated.analyses[0].analysis
                    prev_pos = prev_analysis.get('pos', '')
                    prev_num = prev_analysis.get('num', '')
                    
                    # 模式1：双数+双数的明确修饰关系（原有逻辑，保持不变）
                    if (prev_token.endswith(('ان', 'ين')) and 
                        current_token.endswith(('ان', 'ين')) and 
                        prev_pos in ['noun', 'noun_prop', 'adj']):
                        return False
                    
                    # 模式2：复数名词+双数形容词（新增，但更严格）
                    # 只有当前词明显是形容词概念时才应用前词备选分析
                    current_stemgloss = best_analysis.get('stemgloss', '')
                    
                    is_likely_adjective_concept = is_likely_adjective_by_english_suffix_final(current_stemgloss)
                    
                    if is_likely_adjective_concept:
                        # 只有当前词明显是形容词概念时，才检查前词的备选分析
                        if prev_pos not in ['noun', 'noun_prop']:
                            try:
                                all_prev_analyses = analyzer.analyze(prev_token)
                                
                                # 寻找前词的名词分析
                                prev_noun_analyses = [
                                    a for a in all_prev_analyses 
                                    if (a.get('pos') in ['noun', 'noun_prop'] and 
                                        a.get('stemgloss') and
                                        a.get('lex_logprob', -999) > -99.5)
                                ]
                                
                                if prev_noun_analyses:
                                    # 使用前词的最佳名词分析
                                    prev_noun_analyses.sort(key=lambda x: x.get('pos_logprob', -999), reverse=True)
                                    best_prev_analysis = prev_noun_analyses[0]
                                    prev_pos = best_prev_analysis.get('pos', '')
                                    prev_num = best_prev_analysis.get('num', '')
                                    
                            except:
                                pass  # 分析失败，继续使用原分析
                        
                        # 检查修饰关系
                        if (prev_pos in ['noun', 'noun_prop'] and  
                            current_token.endswith(('ان', 'ين')) and
                            prev_num in ['s', 'd', 'p']):
                            return False  # 很可能是修饰关系
        
        # 介词前缀检查
        prc1 = best_analysis.get('prc1', '0')
        if prc1 and prc1 != '0' and 'prep' in prc1:
            if prc1 == 'ka_prep':
                pass  # ka_prep 可以继续检查
            else:
                return False  # 其他介词前缀，不是独立名词
        
        # UD标签检查
        ud = best_analysis.get('ud', '')
        if ud and 'ADP+' in ud:
            bw = best_analysis.get('bw', '')
            
            if 'كَ/PREP' in bw or 'كَ/PART' in bw:
                pass  # ka介词/助词，继续检查
            elif any(prep in bw for prep in ['بِ/PREP', 'لِ/PREP', 'فِي/PREP']):
                return False  # 其他介词标记，不是独立名词
            else:
                if prc1 != 'ka_prep':
                    return False
        
        # 复杂修饰关系检查（使用基于库的v2版本）
        try:
            is_modification = is_likely_modification_relationship_lib_based_v2(position, tokens, disambiguated, analyzer)
            if is_modification:
                current_prc1 = best_analysis.get('prc1', '0')
                if current_prc1 == 'ka_prep':
                    pass  # ka_prep在修饰关系中，继续
                else:
                    return False  # 修饰关系中非ka_prep，不是独立名词
        except:
            pass  # 复杂检查失败，继续简单检查
        
        return True  # 其他情况认为是独立名词
    
    def detect_dual_nouns_three_stage_lib_based_v3(text):
        """三阶段过滤库依赖版v3：添加真正双数词尾检测"""
        try:
            from camel_tools.disambig.mle import MLEDisambiguator
            if not hasattr(detect_dual_nouns_three_stage_lib_based_v3, 'initialized'):
                detect_dual_nouns_three_stage_lib_based_v3.disambiguator = get_disambiguator()
                detect_dual_nouns_three_stage_lib_based_v3.analyzer = get_analyzer()
                detect_dual_nouns_three_stage_lib_based_v3.initialized = True
            
            disambiguator = detect_dual_nouns_three_stage_lib_based_v3.disambiguator
            analyzer = detect_dual_nouns_three_stage_lib_based_v3.analyzer
            
            # 步骤1: 使用 Naftawayh 预处理
            filtered_tokens = preprocess_with_naftawayh(text)
            
            # 步骤2: 消歧
            disambiguated = disambiguator.disambiguate(filtered_tokens)
            
            # 步骤3: 收集候选双数名词
            candidates = []
            
            for i, (token, disambiguated_word) in enumerate(zip(filtered_tokens, disambiguated)):
                
                # 条件1: 必须有双数词尾
                if not token.endswith(('ان', 'ين')):
                    continue
                
                # 条件2: 不在黑名单中
                if is_non_dual_noun(token):
                    continue
                
                # 条件3: 有有效的消歧分析
                if not disambiguated_word or not hasattr(disambiguated_word, 'analyses') or not disambiguated_word.analyses:
                    continue
                
                best_analysis = disambiguated_word.analyses[0].analysis
                
                # 新增条件：检查是否是真正的双数词尾
                if not is_real_dual_ending(token, best_analysis):
                    continue  # 不是真正的双数词尾，跳过
                
                pos = best_analysis.get('pos', '')
                num = best_analysis.get('num', '')
                stemgloss = best_analysis.get('stemgloss', '')
                
                # 阶段1过滤：检查形容词是否有名词备选
                if pos == 'adj':
                    # 对于被识别为形容词的词，检查是否有名词备选分析
                    try:
                        all_analyses = analyzer.analyze(token)
                        
                        # 寻找名词分析
                        noun_analyses = [
                            a for a in all_analyses 
                            if (a.get('pos') in ['noun', 'noun_prop'] and 
                                a.get('stemgloss') and
                                a.get('lex_logprob', -999) > -99.5)
                        ]
                        
                        if noun_analyses:
                            # 使用最佳的名词分析替代消歧器结果
                            noun_analyses.sort(key=lambda x: x.get('pos_logprob', -999), reverse=True)
                            best_analysis = noun_analyses[0]
                            pos = best_analysis.get('pos', '')
                            num = best_analysis.get('num', '')
                            stemgloss = best_analysis.get('stemgloss', '')
                        else:
                            continue  # 没有名词备选，确实是形容词，跳过
                            
                    except:
                        continue  # 分析失败，跳过
                
                # 阶段2筛选：放宽条件 - noun或noun_prop + 双数词尾 → 候选
                if pos in ['noun', 'noun_prop'] and token.endswith(('ان', 'ين')):
                    # noun_prop 总是接受，noun 需要有 stemgloss
                    if pos == 'noun_prop' or stemgloss:
                        clean_token, removed_prefix = clean_token_prefixes(token)
                        
                        candidate = {
                            'token': token,
                            'clean_token': clean_token,
                            'position': i,
                            'analysis': best_analysis,
                            'prefix_removed': removed_prefix
                        }
                        candidates.append(candidate)
            
            # 步骤4: 语法验证 - 使用基于库的v2版本
            final_duals = []
            
            for candidate in candidates:
                token = candidate['token']
                position = candidate['position']
                analysis = candidate['analysis']
                
                # 使用基于库的v2语法关系判断是否为独立名词
                if is_likely_noun_not_adjective_by_grammar_lib_based_v2(position, filtered_tokens, disambiguated, analyzer, token):
                    
                    dual_info = {
                        'word': candidate['clean_token'],
                        'original_token': token,
                        'root': analysis.get('root', ''),
                        'stemgloss': analysis.get('stemgloss', ''),
                        'gender': analysis.get('gen', ''),
                        'prefix_removed': candidate['prefix_removed'],
                        'source': 'three_stage_lib_based_v18'
                    }
                    final_duals.append(dual_info)
            
            return final_duals
            
        except Exception as e:
            raise Exception(f"双数名词检测异常: {str(e)}")
    
    def get_display(dual_info):
        """显示信息"""
        word = dual_info['word']
        gender = dual_info.get('gender', '')
        prefix_removed = dual_info.get('prefix_removed', '')
        
        gender_display = {'m': '阳性', 'f': '阴性'}.get(gender, gender or '通用')
        prefix_mark = f"(-{prefix_removed})" if prefix_removed else ""
        
        return f"{word}(双数){prefix_mark}"
    
    # 主逻辑
    try:
        params_str = str(rule_params).strip()
        if params_str.startswith('[') and params_str.endswith(']'):
            params_str = '(' + params_str[1:-1] + ')'
        min_count, max_count = ast.literal_eval(params_str)
        min_count = int(min_count)
        max_count = int(max_count)
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}\n期望格式: [min,max]，例如 [2,5]"
    
    results = []
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        try:
            duals = detect_dual_nouns_three_stage_lib_based_v3(text)
        except Exception as e:
            return 0, f"❌ {str(e)}"
        
        unique_duals = []
        seen_words = set()
        for dual in duals:
            word = dual['word']
            if word not in seen_words:
                unique_duals.append(dual)
                seen_words.add(word)
        
        dual_displays = [get_display(dual) for dual in unique_duals]
        
        results.append({
            'index': i,
            'duals': unique_duals,
            'dual_displays': dual_displays,
            'count': len(unique_duals)
        })
    
    if mode == "total":
        all_duals = {}
        for r in results:
            for dual in r['duals']:
                word = dual['word']
                if word not in all_duals:
                    all_duals[word] = dual
        
        total = len(all_duals)
        passed = min_count <= total <= max_count
        
        if len(results) == 1:
            r = results[0]
            dual_text = f" : {'、'.join(r['dual_displays'])}" if r['dual_displays'] else ""
            status = "✅" if passed else "❌"
            text = f"{status} 阿拉伯语双数名词数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {r['count']}个{dual_text}"
        else:
            status = "✅" if passed else "❌"
            details = []
            for r in results:
                dual_list = f" ({'、'.join(r['dual_displays'])})" if r['dual_displays'] else ""
                details.append(f"第{r['index']+1}项: {r['count']}个{dual_list}")
            
            text = f"{status} 阿拉伯语双数名词总数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {total}个\n" + "\n".join(details)
        
        return (1 if passed else 0), text
    else:
        failed = [r for r in results if not (min_count <= r['count'] <= max_count)]
        passed = len(failed) == 0
        
        status = "✅ 所有项双数名词数量都正确" if passed else f"❌ 双数名词数量不符合范围[{min_count},{max_count}]"
        details = []
        for r in results:
            dual_list = f" ({'、'.join(r['dual_displays'])})" if r['dual_displays'] else ""
            details.append(f"第{r['index']+1}项: {r['count']}个{dual_list}")
        
        return (1 if passed else 0), status + ("\n" + "\n".join(details) if details else "")

# 测试函数
def arabic_dual_noun_total(corresponding_parts, rule_params):
    return check_ar_dual_noun_three_stage_lib_based_v18(corresponding_parts, rule_params, mode="total")

def arabic_dual_noun_each(corresponding_parts, rule_params):
    return check_ar_dual_noun_three_stage_lib_based_v18(corresponding_parts, rule_params, mode="each")


###2.阿拉伯语阳性复数
def check_arabic_sound_masculine_plural_core(corresponding_parts, rule_params, mode="total", debug=False):
    """检查阿拉伯语阳性规则复数（以ون/ين结尾）的使用 - 严格模式：只检测名词/形容词的主格形式"""
    
    if not hasattr(check_arabic_sound_masculine_plural_core, 'analyzer'):
        check_arabic_sound_masculine_plural_core.analyzer = get_analyzer()
    
    analyzer = check_arabic_sound_masculine_plural_core.analyzer
    
    EXCLUSION_LIST = {
        'قانون', 'القانون', 'فنون', 'الفنون', 'عيون', 'العيون',
        'شؤون', 'الشؤون', 'مجنون', 'المجنون', 'يقين', 'اليقين',
        'زيتون', 'الزيتون', 'ليمون', 'الليمون', 'جنون', 'الجنون',
        'حنون', 'الحنون', 'عون', 'العون', 'هارون', 'فرعون',
        'وحيد', 'الوحيد', 'ورد', 'الورد', 'وجه', 'الوجه',
    }
    
    WHITELIST = {
        'مستمتعون', 'المستمتعون', 'ومستمتعون', 'والمستمتعون',
        'ودودون', 'الودودون', 'وودودون', 'والودودون',
        'منبهرون', 'المنبهرون', 'ومنبهرون', 'والمنبهرون',
        'متفاجئون', 'المتفاجئون', 'ومتفاجئون', 'والمتفاجئون',
        'متحمسون', 'المتحمسون', 'ومتحمسون', 'والمتحمسون',
        'منتظرون', 'المنتظرون', 'ومنتظرون', 'والمنتظرون',
        'متعاونون', 'المتعاونون', 'ومتعاونون', 'والمتعاونون',
        'مندهشون', 'المندهشون', 'ومندهشون', 'والمندهشون',
        'متأثرون', 'المتأثرون', 'ومتأثرون', 'والمتأثرون',
    }
    
    def extract_arabic_words(text):
        if not text:
            return []
        
        try:
            from camel_tools.tokenizers.word import simple_word_tokenize
            tokens = simple_word_tokenize(text)
            arabic_words = [token for token in tokens if re.match(r'[\u0600-\u06FF]+', token)]
        except Exception:
            arabic_words = re.findall(r'[\u0600-\u06FF]+', text)
        
        return arabic_words
    
    def normalize_word(word):
        return re.sub(r'[\u064B-\u0652]', '', word)
    
    def remove_conjunction_waw(word):
        cleaned = normalize_word(word)
        
        if not cleaned.startswith('و'):
            return word
        
        without_waw = cleaned[1:]
        
        if len(without_waw) < 2:
            if debug:
                print(f"  [保留و] {word} - 去掉后太短")
            return word
        
        try:
            original_analyses = analyzer.analyze(cleaned)
            
            if original_analyses:
                for analysis in original_analyses:
                    diac = analysis.get('diac', '')
                    stem = analysis.get('stem', '')
                    lex = analysis.get('lex', '')
                    
                    stem_clean = normalize_word(stem) if stem else ''
                    lex_clean = normalize_word(lex) if lex else ''
                    
                    if debug:
                        print(f"  [原词分析] {word}:")
                        print(f"    - diac: {diac}")
                        print(f"    - stem: {stem_clean}")
                        print(f"    - lex: {lex_clean}")
                    
                    if stem_clean and stem_clean.startswith('و'):
                        if debug:
                            print(f"  [保留و] {word} - و在词干中")
                        return word
                    
                    if lex_clean and lex_clean.startswith('و'):
                        if debug:
                            print(f"  [保留و] {word} - و在词元中")
                        return word
            
        except Exception as e:
            if debug:
                print(f"  [分析异常] {word}: {e}")
        
        if without_waw in EXCLUSION_LIST or ('ال' + without_waw) in EXCLUSION_LIST:
            if debug:
                print(f"  [保留و] {word} - 在排除列表中")
            return word
        
        if without_waw in WHITELIST or ('ال' + without_waw) in WHITELIST:
            if debug:
                print(f"  [去除و] {word} → {without_waw} (白名单)")
            return word[1:] if word.startswith('و') else word
        
        try:
            analyses = analyzer.analyze(without_waw)
            
            if analyses:
                if debug:
                    print(f"  [去除و] {word} → {without_waw} (去掉后可识别)")
                return word[1:] if word.startswith('و') else word
            else:
                if debug:
                    print(f"  [保留و] {word} - 去掉后无法识别")
                return word
        except Exception:
            return word
    
    def is_sound_masculine_plural(word):
        cleaned = normalize_word(word)
        
        if cleaned in WHITELIST:
            if debug:
                print(f"  [✓ 白名单接受] {word} - 已知规则复数")
            return True
        
        if not (cleaned.endswith('ون') or cleaned.endswith('ين')):
            return False
        
        if len(cleaned) < 3:
            return False
        
        if cleaned in EXCLUSION_LIST:
            if debug:
                print(f"  [排除] {word} - 在排除列表中")
            return False
        
        try:
            analyses = analyzer.analyze(cleaned)
            
            if not analyses and cleaned.startswith('ال') and len(cleaned) > 4:
                without_al = cleaned[2:]
                analyses = analyzer.analyze(without_al)
            
            if not analyses:
                if debug:
                    print(f"  [无法直接分析] {word} - 尝试词干验证")
                
                if cleaned.endswith('ون'):
                    stem = cleaned[:-2]
                elif cleaned.endswith('ين'):
                    stem = cleaned[:-2]
                else:
                    return False
                
                if debug:
                    print(f"  [提取词干] {stem}")
                
                stem_analyses = analyzer.analyze(stem)
                
                if stem_analyses:
                    if debug:
                        seen_analyses = set()
                        for stem_analysis in stem_analyses:
                            stem_pos = stem_analysis.get('pos', '')
                            stem_num = stem_analysis.get('num', '')
                            stem_gen = stem_analysis.get('gen', '')
                            key = (stem_pos, stem_num, stem_gen)
                            if key not in seen_analyses:
                                seen_analyses.add(key)
                                print(f"  [词干分析] {stem}: pos={stem_pos}, num={stem_num}, gen={stem_gen}")
                    
                    for stem_analysis in stem_analyses:
                        stem_pos = stem_analysis.get('pos', '')
                        stem_num = stem_analysis.get('num', '')
                        stem_gen = stem_analysis.get('gen', '')
                        
                        if (stem_pos in ['noun', 'adj'] and 
                            stem_num in ['s', 'na', ''] and 
                            stem_gen in ['m', '']):
                            
                            if cleaned.endswith('ين'):
                                if debug:
                                    print(f"  [拒绝] {word} - 以ين结尾（宾格/属格形式）")
                                return False
                            
                            if debug:
                                print(f"  [✓ 接受] {word} - 通过词干验证（{stem}）")
                            return True
                
                if debug:
                    print(f"  [拒绝] {word} - 词干验证失败")
                return False
            
            for analysis in analyses:
                num = analysis.get('num', '')
                gen = analysis.get('gen', '')
                pos = analysis.get('pos', '')
                cas = analysis.get('cas', '')
                
                if debug:
                    print(f"  [分析] {word}: num={num}, gen={gen}, pos={pos}, cas={cas}")
                
                if num == 'p' and gen == 'm':
                    if pos == 'verb':
                        if debug:
                            print(f"  [拒绝] {word} - 动词不属于主格规则复数")
                        continue
                    
                    if pos not in ['noun', 'adj']:
                        if debug:
                            print(f"  [拒绝] {word} - 词性不符 (pos={pos})")
                        continue
                    
                    if cas and cas != 'n':
                        if debug:
                            print(f"  [拒绝] {word} - 非主格形式 (cas={cas})")
                        continue
                    
                    if cleaned.endswith('ين'):
                        if debug:
                            print(f"  [拒绝] {word} - 以ين结尾（宾格/属格形式）")
                        continue
                    
                    stem_from_analysis = analysis.get('stem', None)
                    lex_from_analysis = analysis.get('lex', None)
                    
                    validated = False
                    
                    if stem_from_analysis:
                        stem_clean = re.sub(r'[\u064B-\u0652]', '', stem_from_analysis)
                        
                        if debug:
                            print(f"  [词干来自分析器] {stem_clean}")
                        
                        stem_analyses = analyzer.analyze(stem_clean)
                        
                        if stem_analyses:
                            if debug:
                                seen_stems = set()
                                for sa in stem_analyses:
                                    key = (sa.get('pos', ''), sa.get('num', ''))
                                    if key not in seen_stems:
                                        seen_stems.add(key)
                                        print(f"  [词干分析] {stem_clean}: num={sa.get('num', '')}, pos={sa.get('pos', '')}")
                            
                            for stem_analysis in stem_analyses:
                                stem_num = stem_analysis.get('num', '')
                                stem_pos = stem_analysis.get('pos', '')
                                
                                if stem_num in ['s', 'na', ''] and stem_pos == pos:
                                    if debug:
                                        print(f"  [✓ 接受] {word} - 主格规则复数（词干验证通过）")
                                    validated = True
                                    break
                            
                            if validated:
                                return True
                            
                            if debug:
                                print(f"  [词干验证失败] 尝试使用词元")
                        else:
                            if debug:
                                print(f"  [词干无法分析] 尝试使用词元")
                    
                    if not validated and lex_from_analysis:
                        lex_clean = re.sub(r'[\u064B-\u0652]', '', lex_from_analysis)
                        
                        if debug:
                            print(f"  [词元] {lex_clean}")
                        
                        lex_analyses = analyzer.analyze(lex_clean)
                        
                        if lex_analyses:
                            if debug:
                                seen_lex = set()
                                for la in lex_analyses:
                                    key = (la.get('pos', ''), la.get('num', ''))
                                    if key not in seen_lex:
                                        seen_lex.add(key)
                                        print(f"  [词元分析] {lex_clean}: num={la.get('num', '')}, pos={la.get('pos', '')}")
                            
                            for lex_analysis in lex_analyses:
                                lex_num = lex_analysis.get('num', '')
                                lex_pos = lex_analysis.get('pos', '')
                                
                                if lex_num in ['s', 'na', ''] and lex_pos == pos:
                                    if debug:
                                        print(f"  [✓ 接受] {word} - 主格规则复数（通过词元验证）")
                                    return True
                            
                            if debug:
                                print(f"  [拒绝] {word} - 词元不是有效单数")
                        else:
                            if debug:
                                print(f"  [拒绝] {word} - 词元无法分析")
                    
                    if not validated:
                        if debug:
                            print(f"  [拒绝] {word} - 无法找到有效词干或词元")
                        return False
            
            if debug:
                print(f"  [拒绝] {word} - 不是符合条件的阳性复数")
            return False
            
        except Exception as e:
            if debug:
                print(f"  [异常] {word}: {e}")
            return False
    
    def extract_sound_masculine_plurals(text):
        words = extract_arabic_words(text)
        plurals = []
        
        for word in words:
            if debug:
                print(f"\n检查词汇: {word}")
            if is_sound_masculine_plural(word):
                clean_word = remove_conjunction_waw(word)
                plurals.append(clean_word)
        
        return plurals
    
    def format_word_list(words):
        if not words:
            return ""
        
        normalized = [unicodedata.normalize('NFC', w) for w in words]
        word_counts = Counter(normalized)
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        lines = []
        for word, count in sorted_words:
            if count > 1:
                lines.append(f"  {word} ({count}次)")
            else:
                lines.append(f"  {word}")
        
        return "\n" + "\n".join(lines)
    
    try:
        min_count, max_count = ast.literal_eval(rule_params)
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    results = []
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        if debug:
            print(f"\n{'='*60}")
            print(f"分析第 {i+1} 项: {text}")
            print(f"{'='*60}")
        
        plural_words = extract_sound_masculine_plurals(text)
        
        results.append({
            'index': i,
            'plural_words': plural_words,
            'count': len(plural_words)
        })
    
    if mode == "total":
        total = sum(r['count'] for r in results)
        passed = min_count <= total <= max_count
        
        if len(results) == 1:
            r = results[0]
            word_text = format_word_list(r['plural_words']) if r['plural_words'] else ""
            
            status = "✅" if passed else "❌"
            text = f"{status} 阿拉伯语阳性主格规则复数数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {r['count']}个{word_text}"
        else:
            all_words = []
            for r in results:
                all_words.extend(r['plural_words'])
            
            word_text = format_word_list(all_words) if all_words else ""
            
            status = "✅" if passed else "❌"
            details = [f"第{r['index']+1}项: {r['count']}个" for r in results]
            
            text = f"{status} 阿拉伯语阳性主格规则复数总数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {total}个\n" + "\n".join(details) + word_text
        
        return (1 if passed else 0), text
    
    else:
        failed = [r for r in results if not (min_count <= r['count'] <= max_count)]
        passed = len(failed) == 0
        
        status = "✅ 所有项阿拉伯语阳性主格规则复数数量都正确" if passed else f"❌ 阿拉伯语阳性主格规则复数数量不符合范围[{min_count},{max_count}]"
        
        details = []
        for r in results:
            word_text = format_word_list(r['plural_words']) if r['plural_words'] else ""
            detail = f"第{r['index']+1}项: {r['count']}个{word_text}"
            details.append(detail)
        
        return (1 if passed else 0), status + "\n" + "\n".join(details)


def athlete_masc_plural_total(corresponding_parts, rule_params):
    """检查阿拉伯语阳性主格规则复数总数"""
    return check_arabic_sound_masculine_plural_core(corresponding_parts, rule_params, mode="total")

def athlete_masc_plural_each(corresponding_parts, rule_params):
    """检查每项阿拉伯语阳性主格规则复数数量"""
    return check_arabic_sound_masculine_plural_core(corresponding_parts, rule_params, mode="each")



###3.定冠词
def check_arabic_definite_article_core(corresponding_parts, rule_params, mode="total", debug=False):
    """检查阿拉伯语定冠词"ال"的使用"""
    
    # 初始化camel工具
    db = get_morphology_db()
    analyzer = Analyzer(db)
    
    # ✅ 固定短语列表（只包含完整短语）
    FIXED_PHRASES_WITH_AL = {
        'بالنسبة',
        'بالإضافة',
        'بالرغم',
        'بالفعل',
        'بالطبع',
        'بالتأكيد',
        'بالضبط',
        'بالكاد',
        'بالتالي',
        'بالمناسبة',
        'بالأمس',
        'بالأحرى',
        'بالذات',
        'بالنظر',
        'بالمقارنة',
        'بالمقابل',
        'بالكامل',
        'على الرغم',
        'على الأقل',
        'على العموم',
        'على الفور',
        'على الإطلاق',
        'على الأغلب',
        'على الأرجح',
        'على العكس',
        'على الدوام',
        'في الواقع',
        'في الحقيقة',
        'في النهاية',
        'في البداية',
        'في الوقت',
        'في الماضي',
        'في المستقبل',
        'في الغالب',
        'في الآونة',
        'في الحال',
        'في الحين',
        'في البدء',
        'من الممكن',
        'من المحتمل',
        'من الضروري',
        'من المهم',
        'من الواضح',
        'من المؤكد',
        'من الأفضل',
        'من الصعب',
        'من السهل',
        'من الطبيعي',
        'إلى الآن',
        'إلى الأبد',
        'حتى الآن',
        'للآن',
        'طوال الوقت',
        'طوال اليوم',
        'طوال الليل',
        'منذ الآن',
        'في الوقت نفسه',
        'في الوقت الحاضر',
        'في الأحيان',
        'في الآونة الأخيرة',
        'في الحالة',
        'على الرغم من',
        'بالرغم من',
        'على المثال',
        'على الخصوص',
        'على العلم',
        'إلى الحد',
        'بالشكل',
        'بالصورة',
        'بالصفة',
        'بالوجه',
        'من الوجهة',
        'بالعبارة',
        'بالمعنى',
        'للغاية',#副词
        'بالنكهة'
    }
    
    def extract_words_from_fixed_phrases(text):
        """从文本中提取所有出现的固定短语中的词"""
        words_in_phrases = set()
        for phrase in FIXED_PHRASES_WITH_AL:
            if phrase in text:
                # 固定短语出现在文本中，提取其中的所有词
                words = phrase.split()
                for word in words:
                    cleaned = re.sub(r'[^\u0621-\u063A\u0641-\u064A]', '', word)
                    if cleaned and 'ال' in cleaned:
                        words_in_phrases.add(cleaned)
                if debug:
                    print(f"  发现固定短语: {phrase}, 排除词: {[w for w in words if 'ال' in w]}")
        return words_in_phrases
    
    def extract_definite_article_nouns(text):
        """提取带定冠词的阿拉伯语名词"""
        if not text:
            return []
        
        # ✅ 首先提取文本中出现的固定短语的词
        words_in_fixed_phrases = extract_words_from_fixed_phrases(text)
        
        if debug and words_in_fixed_phrases:
            print(f"固定短语中需要排除的词: {sorted(words_in_fixed_phrases)}")
        
        punctuation_pattern = r'[、，。！？；：""''（）《》【】\.,;:!?\[\]\(\){}]+'
        text_normalized = re.sub(punctuation_pattern, ' ', text)
        words = text_normalized.split()
        arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
        arabic_words = [word for word in words if word and re.search(arabic_pattern, word)]
        
        if debug:
            print(f"\n原始文本: {text}")
            print(f"分割后的阿拉伯语单词数量: {len(arabic_words)}")
        
        definite_nouns = []
        
        # ✅ 所有可能的介词+定冠词缩写形式
        AL_CONTRACTIONS = {
            'ولل': 'ال',    # و + ل + ال (最长的先匹配)
            'وبال': 'ال',   # و + ب + ال
            'وكال': 'ال',   # و + ك + ال
            'فلل': 'ال',    # ف + ل + ال
            'فبال': 'ال',   # ف + ب + ال
            'فكال': 'ال',   # ف + ك + ال
            'لل': 'ال',     # ل + ال
            'بال': 'ال',    # ب + ال
            'كال': 'ال',    # ك + ال
            'وال': 'ال',    # و + ال
            'فال': 'ال',    # ف + ال
        }
        
        # 所有常见的单字符连接词/介词前缀（用于单独的ال检测）
        single_prefixes = ['و', 'ف', 'ب', 'ل', 'ك']
        
        for word in arabic_words:
            # 移除剩余标点和音标，只保留基本阿拉伯语字母
            cleaned = re.sub(r'[^\u0621-\u063A\u0641-\u064A]', '', word)
            
            if debug:
                print(f"\n原始单词: {word} -> 清理后: {cleaned}")
            
            # ✅ 预先检查：是否是完整的单词固定短语
            if cleaned in FIXED_PHRASES_WITH_AL:
                if debug:
                    print(f"  × 跳过：整个词是固定短语: {cleaned}")
                continue
            
            original_cleaned = cleaned
            converted_to_al = False
            al_word = None  # 转换后的ال形式
            
            # ✅ 检查所有可能的介词+定冠词缩写形式
            for contraction, replacement in AL_CONTRACTIONS.items():
                if cleaned.startswith(contraction) and len(cleaned) > len(contraction):
                    # 将缩写形式转换为 ال 形式
                    al_word = replacement + cleaned[len(contraction):]
                    converted_to_al = True
                    if debug:
                        print(f"  ✓ 检测到缩写形式 '{contraction}'，转换为: {original_cleaned} -> {al_word}")
                    
                    # ✅ 检查转换后的词是否在固定短语中
                    if al_word in words_in_fixed_phrases:
                        if debug:
                            print(f"  × 跳过：转换后的 '{al_word}' 在固定短语中")
                        converted_to_al = False
                    break
            
            # 如果已经通过缩写转换处理了，使用al_word
            if converted_to_al:
                cleaned = al_word
            # 原有的 ال 检测逻辑（处理单前缀+ال的情况）
            elif 'ال' in cleaned:
                al_pos = cleaned.find('ال')
                
                if al_pos > 0:
                    # 'ال' 前面有字符，检查是否为单字符前缀
                    potential_prefix = cleaned[:al_pos]
                    
                    if len(potential_prefix) == 1 and potential_prefix in single_prefixes:
                        al_word = cleaned[al_pos:]
                        if debug:
                            print(f"  ✓ 检测到 '{potential_prefix}ال' 组合，去除前缀: {original_cleaned} -> {al_word}")
                        
                        # ✅ 检查去除前缀后的词是否在固定短语中
                        if al_word in words_in_fixed_phrases:
                            if debug:
                                print(f"  × 跳过：去除前缀后的 '{al_word}' 在固定短语中")
                            continue
                        
                        cleaned = al_word
                        converted_to_al = True
                elif al_pos == 0:
                    # ال 在开头
                    if cleaned in words_in_fixed_phrases:
                        if debug:
                            print(f"  × 跳过：'{cleaned}' 在固定短语中")
                        continue
                    converted_to_al = True
            
            # 预检查：必须以"ال"开头且长度足够
            if not (cleaned.startswith('ال') and len(cleaned) > 2):
                continue
            
            # 使用camel库分析词汇
            if converted_to_al and has_true_definite_article(cleaned, analyzer, debug):
                # ✅ 返回原始形式
                definite_nouns.append(original_cleaned)
        
        if debug:
            print(f"\n找到的特指名词: {definite_nouns}")
        
        return definite_nouns
    
    def has_true_definite_article(word, analyzer, debug=False):
        """使用camel库判断词汇是否有真正的定冠词"""
        
        RELATION_PRONOUNS = {
            'التي', 'الذي', 'اللذان', 'اللتان', 'اللذين', 'اللتين',
            'الذين', 'اللواتي', 'اللاتي', 'الذى'
        }
        
        if word in RELATION_PRONOUNS:
            if debug:
                print(f"  × 硬编码排除关系代词: {word}")
            return False
        
        WORDS_WITH_AL_IN_ROOT = {
            'الألف', 'الآن', 'الأن', 'الليل', 'الآخر', 
            'الألم', 'الآمال', 'الآباء', 'الأولى',
        }
        
        if word in WORDS_WITH_AL_IN_ROOT:
            if debug:
                print(f"  × 硬编码排除：ال是词根一部分: {word}")
            return False
        
        try:
            base_word = word[2:]
            analyses = analyzer.analyze(word)
            
            if not analyses:
                if debug:
                    print(f"  ⚠️ CamelTools 无法分析词汇: {word}")
                
                if 2 <= len(base_word) <= 10:
                    if debug:
                        print(f"    → 回退判定：可能是外来词/专有名词/新词，判定为有定冠词 ✅")
                    return True
                else:
                    if debug:
                        print(f"    → 回退判定：长度异常({len(base_word)}个字符)，判定为无定冠词 ❌")
                    return False
            
            for analysis in analyses:
                if 'prc0' in analysis and analysis['prc0'] == 'Al_det':
                    if debug:
                        print(f"  ✓ 找到明确定冠词标记 prc0=Al_det: {word}")
                    return True
                
                analysis_str = analysis.get('analysis', '')
                if 'Al+' in analysis_str:
                    if debug:
                        print(f"  ✓ 找到明确定冠词标记 Al+ in analysis: {analysis_str}")
                    return True
            
            has_valid_definite_article = False
            
            for analysis in analyses:
                if 'enc0' in analysis and analysis['enc0'] != '0':
                    enc0 = analysis['enc0']
                    if 'poss' in str(enc0).lower() or 'pron' in str(enc0).lower():
                        if debug:
                            print(f"  × 发现属格代词后缀，跳过此分析: {word}, enc0: {enc0}")
                        continue
                
                if 'root' in analysis:
                    root = analysis['root']
                    root_clean = root.replace('.', '').replace('_', '').replace('-', '')
                    
                    if debug:
                        print(f"  检查词根: {root} -> 清理后: {root_clean}")
                    
                    if 'ال' in root_clean:
                        if debug:
                            print(f"  × 词根包含ال，判断为词根一部分: {word}, 词根: {root_clean}")
                        return False
                    
                    pos = analysis.get('pos', '')
                    if pos in ['noun', 'noun_prop', 'adj']:
                        if debug:
                            print(f"  ✓ 找到名词/形容词候选，词性: {pos}, 词根: {root_clean}")
                        has_valid_definite_article = True
            
            if debug:
                print(f"  最终判断: {word} 是否有定冠词: {has_valid_definite_article}")
            
            return has_valid_definite_article
            
        except Exception as e:
            if debug:
                print(f"  ❌ 分析词汇 {word} 时出错: {e}")
            return False
    
    # ✅ 统一的格式化函数
    def format_noun_list(definite_nouns):
        """格式化名词列表"""
        if not definite_nouns:
            return ""
        
        normalized_nouns = [unicodedata.normalize('NFC', noun) for noun in definite_nouns]
        noun_counts = Counter(normalized_nouns)
        sorted_nouns = sorted(noun_counts.items(), key=lambda x: x[1], reverse=True)
        
        # ✅ 只有一个单词时，不换行
        if len(sorted_nouns) == 1:
            noun, count = sorted_nouns[0]
            if count > 1:
                return f" ({noun}, {count}次)"
            else:
                return f" ({noun})"
        
        # ✅ 多个单词时，换行显示
        noun_lines = []
        for noun, count in sorted_nouns:
            if count > 1:
                noun_lines.append(f"  {noun} ({count}次)")
            else:
                noun_lines.append(f"  {noun}")
        
        return " :\n" + "\n".join(noun_lines)

    # 主逻辑
    try:
        min_count, max_count = ast.literal_eval(rule_params)
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"

    results = []
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        definite_nouns = extract_definite_article_nouns(text)
        
        result = {
            'index': i, 
            'definite_nouns': definite_nouns, 
            'count': len(definite_nouns)
        }
        results.append(result)

    if mode == "total":
        total = sum(r['count'] for r in results)
        passed = min_count <= total <= max_count
        
        if len(results) == 1:
            r = results[0]
            noun_text = format_noun_list(r['definite_nouns'])
            
            status = "✅" if passed else "❌"
            text = f"{status} 阿拉伯语特指词汇数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {r['count']}个{noun_text}"
        else:
            status = "✅" if passed else "❌"
            details = []
            for r in results:
                noun_text = format_noun_list(r['definite_nouns'])
                details.append(f"第{r['index']+1}项: {r['count']}个{noun_text}")
            
            text = f"{status} 阿拉伯语特指词汇总数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {total}个\n" + "\n".join(details)
        
        return (1 if passed else 0), text
        
    else:
        failed = [r for r in results if not (min_count <= r['count'] <= max_count)]
        passed = len(failed) == 0
        
        status = "✅ 所有项阿拉伯语特指词汇数量都正确" if passed else f"❌ 阿拉伯语特指词汇数量不符合范围[{min_count},{max_count}]"
        details = []
        for r in results:
            noun_text = format_noun_list(r['definite_nouns'])
            details.append(f"第{r['index']+1}项: {r['count']}个{noun_text}")
        
        return (1 if passed else 0), status + ("\n" + "\n".join(details) if details else "")


def arabic_definite_article_total(corresponding_parts, rule_params):
    """检查阿拉伯语特指词总数"""
    return check_arabic_definite_article_core(corresponding_parts, rule_params, mode="total")

def arabic_definite_article_each(corresponding_parts, rule_params):
    """检查每项阿拉伯语特指词数量"""
    return check_arabic_definite_article_core(corresponding_parts, rule_params, mode="each")



###4.独立人称代词
def check_ar_independent_pronouns_safe(corresponding_parts, rule_params, mode="total"):

    def extract_arabic_words(text):
        """提取阿拉伯语词汇"""
        try:
            from camel_tools.tokenizers.word import simple_word_tokenize
            tokens = simple_word_tokenize(text)
            return [token for token in tokens if re.match(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', token)]
        except Exception:
            return re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)

    def detect_independent_pronouns_with_disambiguator(words):
        """使用消歧器检测独立人称代词"""
        found_pronouns = []
        
        try:
            from camel_tools.disambig.mle import MLEDisambiguator
            
            if not hasattr(detect_independent_pronouns_with_disambiguator, 'disambiguator'):
                # ✅ 修改：使用全局的消歧器
                detect_independent_pronouns_with_disambiguator.disambiguator = get_disambiguator()
            
            disambiguator = detect_independent_pronouns_with_disambiguator.disambiguator
            disambiguated = disambiguator.disambiguate(words)
            
            for word, disambiguated_word in zip(words, disambiguated):
                # 特殊处理：أنتن 和带前缀的أنتن
                if word == 'أنتن' or (word.startswith(('و', 'ف')) and word[1:] == 'أنتن'):
                    base_form = 'أنتن' if word == 'أنتن' else word[1:]
                    pronoun_info = {
                        'word': word,
                        'base_form': base_form,
                        'type': '第二人称阴性复数',
                        'stemgloss': 'you_[fem.pl.]',
                        'source': 'special_correction'
                    }
                    found_pronouns.append(pronoun_info)
                    continue
                
                # 检查消歧器的最佳分析结果
                if (disambiguated_word and disambiguated_word.analyses):
                    best_analysis = disambiguated_word.analyses[0].analysis
                    pos = best_analysis.get('pos', '')
                    stemgloss = best_analysis.get('stemgloss', '')
                    
                    # 只处理词性为代词的情况
                    if pos == 'pron':
                        chinese_type = get_chinese_type_from_stemgloss(stemgloss, word)  # 传入word参数
                        base_form = get_base_form_from_stemgloss(stemgloss, word)
                        
                        if chinese_type and base_form:
                            pronoun_info = {
                                'word': word,
                                'base_form': base_form,
                                'type': chinese_type,
                                'stemgloss': stemgloss,
                                'source': 'disambiguator_best'
                            }
                            found_pronouns.append(pronoun_info)
                    
        except Exception:
            # 如果CamelTools完全失败，处理特殊情况
            for word in words:
                if word == 'أنتن' or (word.startswith(('و', 'ف')) and word[1:] == 'أنتن'):
                    base_form = 'أنتن' if word == 'أنتن' else word[1:]
                    found_pronouns.append({
                        'word': word,
                        'base_form': base_form,
                        'type': '第二人称阴性复数',
                        'stemgloss': 'you_[fem.pl.]',
                        'source': 'fallback_special'
                    })
        
        return found_pronouns

    def get_chinese_type_from_stemgloss(stemgloss, original_word):
        """从stemgloss获取中文人称类型（修正版）"""
        # 特殊处理：根据原词判断أنتِ的性别
        if stemgloss == 'you_[masc.sg.]':
            if original_word in ['أنتِ', 'وأنتِ', 'فأنتِ']:
                return '第二人称阴性单数'
            else:
                return '第二人称阳性单数'
        
        # 基于测试结果的映射
        stemgloss_mapping = {
            'I': '第一人称单数',
            'we': '第一人称复数',
            'you_[fem.sg.]': '第二人称阴性单数',
            'you_both': '第二人称双数',
            'you_[masc.pl.]': '第二人称阳性复数',
            'you_[fem.pl.]': '第二人称阴性复数',
            'it;he': '第三人称阳性单数',
            'he': '第三人称阳性单数',
            'it;they;she': '第三人称阴性单数',
            'she': '第三人称阴性单数',
            'they_(both)': '第三人称双数',
            'they_[masc.pl]': '第三人称阳性复数',
            'they_[masc.pl.]': '第三人称阳性复数',
            'they_[fem.pl.]': '第三人称阴性复数'
        }
        return stemgloss_mapping.get(stemgloss)

    def get_base_form_from_stemgloss(stemgloss, original_word):
        """从stemgloss获取基本形式（修正版）"""
        # 特殊处理：根据原词判断أنتِ
        if stemgloss == 'you_[masc.sg.]':
            if original_word in ['أنتِ', 'وأنتِ', 'فأنتِ']:
                return 'أنتِ'
            else:
                return 'أنت'
        
        # 基于测试结果的基本形式映射
        base_form_mapping = {
            'I': 'أنا',
            'we': 'نحن', 
            'you_[fem.sg.]': 'أنتِ',
            'you_both': 'أنتما',
            'you_[masc.pl.]': 'أنتم',
            'you_[fem.pl.]': 'أنتن',
            'it;he': 'هو',
            'he': 'هو',
            'it;they;she': 'هي', 
            'she': 'هي',
            'they_(both)': 'هما',
            'they_[masc.pl]': 'هم',
            'they_[masc.pl.]': 'هم',
            'they_[fem.pl.]': 'هن'
        }
        
        base_form = base_form_mapping.get(stemgloss)
        if base_form:
            return base_form
        
        # 如果没有找到映射，返回原词（可能是带前缀的形式）
        return original_word

    def get_pronoun_display_info(pronoun_info):
        """获取代词显示信息"""
        word = pronoun_info['word']
        base_form = pronoun_info['base_form']
        pronoun_type = pronoun_info['type']
        
        if word == base_form:
            return f"{word}({pronoun_type})"
        else:
            return f"{word}→{base_form}({pronoun_type})"

    # 主逻辑
    try:
        min_count, max_count = ast.literal_eval(rule_params)
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    results = []
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        words = extract_arabic_words(text)
        pronouns = detect_independent_pronouns_with_disambiguator(words)
        
        # 去重：基于base_form
        unique_pronouns = []
        seen_base_forms = set()
        for pronoun in pronouns:
            base_form = pronoun['base_form']
            if base_form not in seen_base_forms:
                unique_pronouns.append(pronoun)
                seen_base_forms.add(base_form)
        
        results.append({
            'index': i,
            'pronouns': unique_pronouns,
            'pronoun_displays': [get_pronoun_display_info(p) for p in unique_pronouns],
            'count': len(unique_pronouns)
        })
    
    # 处理结果
    if mode == "total":
        all_pronouns = {}
        for r in results:
            for pronoun in r['pronouns']:
                base_form = pronoun['base_form']
                if base_form not in all_pronouns:
                    all_pronouns[base_form] = pronoun
        
        total = len(all_pronouns)
        passed = min_count <= total <= max_count
        status = "✅" if passed else "❌"
        
        unique_displays = [get_pronoun_display_info(pronoun) for pronoun in all_pronouns.values()]
        pronoun_text = f" : {'、'.join(unique_displays)}" if unique_displays else ""
        
        text = f"{status} 独立人称代词数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {total}个{pronoun_text}"
        
        return (1 if passed else 0), text
    
    else:  # mode == "each"
        failed = [r for r in results if not (min_count <= r['count'] <= max_count)]
        passed = len(failed) == 0
        status = "✅ 所有项独立人称代词数量都正确" if passed else f"❌ 独立人称代词数量不符合范围[{min_count},{max_count}]"
        
        details = [f"第{r['index']+1}项: {r['count']}个 ({'、'.join(r['pronoun_displays'])})" 
                  if r['pronoun_displays'] else f"第{r['index']+1}项: {r['count']}个" for r in results]
        
        return (1 if passed else 0), status + ("\n" + "\n".join(details) if details else "")

# 导出函数
def ar_independent_pronoun_total(corresponding_parts, rule_params):
    return check_ar_independent_pronouns_safe(corresponding_parts, rule_params, mode="total")

def ar_independent_pronoun_each(corresponding_parts, rule_params):
    return check_ar_independent_pronouns_safe(corresponding_parts, rule_params, mode="each")


###5.现在时的第三人称 阳性、单数 动词
def check_ar_present_third_masculine_singular_verb_fixed(corresponding_parts, rule_params, mode="total"):
    """修正版：基于词尾规则优先的现在时第三人称阳性单数动词检测"""
    
    def extract_arabic_words(text):
        """提取阿拉伯语词汇"""
        try:
            from camel_tools.tokenizers.word import simple_word_tokenize
            tokens = simple_word_tokenize(text)
            return [token for token in tokens if re.match(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', token)]
        except Exception:
            return re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
    
    def has_present_third_masculine_ending(word):
        """检查是否符合现在时第三人称阳性单数词尾规则：以ُ结尾"""
        return word.endswith('ُ')
    
    def detect_present_verbs_fixed(words):
        """修正版检测：词尾规则优先 + 忽略mood字段"""
        
        try:
            if not hasattr(detect_present_verbs_fixed, 'analyzer'):
                db = get_morphology_db()
                detect_present_verbs_fixed.analyzer = Analyzer(db)
            
            analyzer = detect_present_verbs_fixed.analyzer
            found_verbs = []
            
            for word in words:
                # 🎯 步骤1: 词尾规则检查（最高优先级）
                has_correct_ending = has_present_third_masculine_ending(word)
                
                if not has_correct_ending:
                    continue  # 不符合词尾规则直接跳过
                
                try:
                    analyses = analyzer.analyze(word)
                    
                    if not analyses:
                        # 无分析结果但词尾符合，基于规则接受
                        if len(word) >= 3:
                            verb_info = {
                                'word': word,
                                'root': 'unknown',
                                'source': 'ending_rule_only',
                                'confidence': 'medium'
                            }
                            found_verbs.append(verb_info)
                        continue
                    
                    # 🎯 修正的检测逻辑：忽略mood字段
                    matching_analyses = []
                    verb_analyses = []
                    
                    for analysis in analyses:
                        pos = analysis.get('pos')
                        per = analysis.get('per')
                        num = analysis.get('num')
                        gen = analysis.get('gen')
                        asp = analysis.get('asp')
                        
                        if pos == 'verb':
                            verb_analyses.append(analysis)
                            
                            # 🔧 修正的条件：不要求mood='i'
                            is_present_third_masc_sing = (
                                per == '3' and      # 第三人称
                                num == 's' and     # 单数
                                gen == 'm' and     # 阳性
                                asp == 'i'         # 未完成时（现在时）
                            )
                            
                            if is_present_third_masc_sing:
                                matching_analyses.append(analysis)
                    
                    # 🎯 决策逻辑
                    if matching_analyses:
                        # 完美匹配：词尾符合 + 分析器确认
                        best_analysis = matching_analyses[0]
                        verb_info = {
                            'word': word,
                            'root': best_analysis.get('root', 'unknown'),
                            'source': 'analyzer_confirmed',
                            'confidence': 'high',
                            'analysis': best_analysis
                        }
                        found_verbs.append(verb_info)
                        
                    elif verb_analyses:
                        # 有动词分析但不完全匹配 + 词尾符合 → 仍接受
                        verb_info = {
                            'word': word,
                            'root': verb_analyses[0].get('root', 'unknown'),
                            'source': 'ending_rule_priority',
                            'confidence': 'medium'
                        }
                        found_verbs.append(verb_info)
                        
                    else:
                        # 无动词分析但词尾符合 → 基于规则接受
                        if len(word) >= 3:
                            verb_info = {
                                'word': word,
                                'root': 'unknown',
                                'source': 'ending_rule_only',
                                'confidence': 'medium'
                            }
                            found_verbs.append(verb_info)
                
                except Exception:
                    # 分析异常但词尾符合 → 兜底接受
                    if has_correct_ending and len(word) >= 3:
                        verb_info = {
                            'word': word,
                            'root': 'unknown',
                            'source': 'ending_rule_fallback',
                            'confidence': 'low'
                        }
                        found_verbs.append(verb_info)
            
            return found_verbs
            
        except Exception:
            # 系统异常 → 完全基于词尾规则
            return [
                {
                    'word': word,
                    'root': 'unknown',
                    'source': 'ending_rule_only',
                    'confidence': 'low'
                }
                for word in words 
                if has_present_third_masculine_ending(word) and len(word) >= 3
            ]
    
    def get_verb_display_info(verb_info):
        """获取动词显示信息"""
        word = verb_info['word']
        root = verb_info['root']
        source = verb_info['source']
        confidence = verb_info['confidence']
        
        # 来源和置信度标记
        source_marks = {
            'analyzer_confirmed': '🎯',     # 分析器完全确认
            'ending_rule_priority': '📏',  # 词尾规则优先
            'ending_rule_only': '🔄',      # 仅基于词尾规则
            'ending_rule_fallback': '⚠️'   # 异常兜底
        }
        
        confidence_marks = {
            'high': '✅',
            'medium': '🟡', 
            'low': '🔴'
        }
        
        source_mark = source_marks.get(source, '❓')
        confidence_mark = confidence_marks.get(confidence, '❓')
        
        return f"{word}({root}-现在时-阳性){source_mark}{confidence_mark}"
    
    # 主逻辑
    try:
        min_count, max_count = ast.literal_eval(rule_params)
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    results = []
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        words = extract_arabic_words(text)
        verbs = detect_present_verbs_fixed(words)
        
        # 去重：基于词汇本身
        unique_verbs = []
        seen_words = set()
        
        for verb in verbs:
            word = verb['word']
            if word not in seen_words:
                unique_verbs.append(verb)
                seen_words.add(word)
        
        verb_displays = [get_verb_display_info(verb) for verb in unique_verbs]
        
        result = {
            'index': i, 
            'verbs': unique_verbs,
            'verb_displays': verb_displays,
            'count': len(unique_verbs)
        }
        results.append(result)
    
    # 返回结果
    if mode == "total":
        all_verbs = {}
        for r in results:
            for verb in r['verbs']:
                word = verb['word']
                if word not in all_verbs:
                    all_verbs[word] = verb
        
        total = len(all_verbs)
        passed = min_count <= total <= max_count
        
        if len(results) == 1:
            r = results[0]
            verb_text = f" : {'、'.join(r['verb_displays'])}" if r['verb_displays'] else ""
            status = "✅" if passed else "❌"
            text = f"{status} 现在时第三人称阳性单数动词数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {r['count']}个{verb_text}"
        else:
            status = "✅" if passed else "❌"
            details = []
            for r in results:
                verb_list = f" ({'、'.join(r['verb_displays'])})" if r['verb_displays'] else ""
                details.append(f"第{r['index']+1}项: {r['count']}个{verb_list}")
            
            text = f"{status} 现在时第三人称阳性单数动词总数量{'正确' if passed else f'不符合范围[{min_count},{max_count}]'}: {total}个\n" + "\n".join(details)
        
        return (1 if passed else 0), text
        
    else:
        failed = [r for r in results if not (min_count <= r['count'] <= max_count)]
        passed = len(failed) == 0
        
        status = "✅ 所有项动词数量都正确" if passed else f"❌ 动词数量不符合范围[{min_count},{max_count}]"
        details = []
        for r in results:
            verb_list = f" ({'、'.join(r['verb_displays'])})" if r['verb_displays'] else ""
            details.append(f"第{r['index']+1}项: {r['count']}个{verb_list}")
        
        return (1 if passed else 0), status + ("\n" + "\n".join(details) if details else "")


# 导出函数
def arabic_present_third_masc_verb_total(corresponding_parts, rule_params):
    """检查现在时第三人称阳性单数动词总数"""
    return check_ar_present_third_masculine_singular_verb_fixed(corresponding_parts, rule_params, mode="total")

def arabic_present_third_masc_verb_each(corresponding_parts, rule_params):
    """检查每项现在时第三人称阳性单数动词数量"""
    return check_ar_present_third_masculine_singular_verb_fixed(corresponding_parts, rule_params, mode="each")


#6.破碎复数
def check_ar_broken_plurals_simple(corresponding_parts, rule_params, mode="total", debug=False):
    """破碎复数检查函数"""
    
    PREFIXES = ['و', 'ف', 'ب', 'ل', 'ك']
    
    TEMPORAL_CONNECTORS = {
        'أثناء', 'أثناءَ', 'أثناءً', 'أثناءِ', 'خلال', 'خلالَ', 'خلالً', 'خلالِ',
        'عند', 'عندَ', 'عندً', 'عندِ','حين', 'حينَ', 'حينً', 'حينِ',
        'وقت', 'وقتَ', 'وقتً', 'وقتِ','بينما','لما','كلما'
    }
    
    SINGULAR_NOUNS_ENDING_S = {
        'news', 'mathematics', 'physics', 'economics', 'politics',
        'athletics', 'gymnastics', 'statistics', 'linguistics',
        'glass', 'grass', 'class', 'mass', 'bass',
        'business', 'process', 'address', 'stress', 'success',
        'bus', 'tennis', 'chess', 'focus', 'basis', 'beauty'
    }
    
    IRREGULAR_PLURALS = {
        'children', 'men', 'women', 'people', 'feet', 'teeth', 
        'mice', 'geese', 'sheep', 'deer', 'fish', 'species', 'series',
        'data', 'criteria', 'phenomena', 'alumni', 'cacti', 'fungi',
        'nuclei', 'radii', 'stimuli', 'syllabi', 'wadis', 'valleys'
    }
    
    COLLECTIVE_NOUN_ROOTS = {'س.ح.ب', 'ش.ج.ر', 'و.ر.ق', 'ط.ي.ر', 'ن.ج.م'}
    
    COLLECTIVE_NOUNS = {
        'بيض', 'تمر', 'حب', 'نخل', 'شجر', 'ورق', 'طير', 'سمك', 
        'حيوان', 'نبات', 'لبن', 'عنب', 'زرع', 'حطب', 'نور',
        'ماء', 'هوا', 'تراب', 'رمل', 'حجر', 'ذهب', 'فضة', 
        'نحاس', 'حديد', 'خشب', 'قطن', 'صوف', 'حرير'
    }
    
    BROKEN_PLURAL_PATTERNS = [
        (r'^أ[\u064B-\u0652]*[ا-ي][\u064B-\u0652]*[ا-ي][\u064B-\u0652]*[ا-ي][\u064B-\u0652]*[ا-ي]?[\u064B-\u0652]*ل?[\u064B-\u0652]*$', 'أفعال'),
        (r'^أ[\u064B-\u0652]*[ا-ي][\u064B-\u0652]*[ا-ي][\u064B-\u0652]*ا[\u064B-\u0652]*ء[\u064B-\u0652]*$', 'أفعلاء'),
        (r'^أ[\u064B-\u0652]*[ا-ي][\u064B-\u0652]*ا[\u064B-\u0652]*[ا-ي][\u064B-\u0652]*ي[\u064B-\u0652]*[سل][\u064B-\u0652]*$', 'أفاعيل'),
        (r'^أ[\u064B-\u0652]*[ا-ي][\u064B-\u0652]*[ا-ي][\u064B-\u0652]*ة[\u064B-\u0652]*$', 'أفعلة'),
        (r'^[ا-ي][\u064B-\u0652]*[ا-ي][\u064B-\u0652]*ا[\u064B-\u0652]*[ا-ي][\u064B-\u0652]*$', 'فعال'),
        (r'^[ا-ي][\u064B-\u0652]*[ا-ي][\u064B-\u0652]*و[\u064B-\u0652]*[ا-ي][\u064B-\u0652]*$', 'فعول'),
    ]

    def has_diacritics(text):
        return bool(re.search(r'[\u064B-\u0652]', text))
    
    def remove_diacritics(text):
        return re.sub(r'[\u064B-\u0652]', '', text)
    
    def normalize_for_matching(word):
        word = re.sub(r'[ًٌٍ]$', '', word)
        word = re.sub(r'[َُِ]$', '', word)
        return word
    
    def normalize_for_comparison(text):
        text = unicodedata.normalize('NFC', text)
        text = text.replace('إ', 'ا')
        text = text.replace('أ', 'ا')
        text = text.replace('آ', 'ا')
        text = text.replace('ٱ', 'ا')
        text = text.replace('ْ', '')
        text = text.replace('\u0652', '')
        text = re.sub(r'َا', 'ا', text)
        text = re.sub(r'ُو', 'و', text)
        text = re.sub(r'ِي', 'ي', text)
        return text
    
    def diac_matches_input(input_word, analysis_diac, exact=False):
        if not analysis_diac:
            return True
        
        input_normalized = normalize_for_comparison(input_word)
        diac_normalized = normalize_for_comparison(analysis_diac)
        
        if exact:
            return input_normalized == diac_normalized
        else:
            input_stripped = normalize_for_matching(input_normalized)
            diac_stripped = normalize_for_matching(diac_normalized)
            return input_stripped == diac_stripped
    
    def matches_broken_plural_pattern(word):
        for pattern, _ in BROKEN_PLURAL_PATTERNS:
            if re.match(pattern, word):
                return True
        return False
    
    def is_english_plural_in_stemgloss(stemgloss):
        if not stemgloss:
            return False
        
        words = stemgloss.lower().replace(';', ' ').replace(',', ' ').split()
        
        for word in words:
            word = word.strip()
            if not word or word in SINGULAR_NOUNS_ENDING_S:
                continue
            
            if word in IRREGULAR_PLURALS:
                return True
            
            if (word.endswith('ies') and len(word) > 3) or \
               (word.endswith('ves') and len(word) > 3) or \
               (word.endswith('es') and len(word) > 2 and not word.endswith(('ss', 'us'))) or \
               (word.endswith('s') and len(word) > 3 and not word.endswith(('ss', 'us'))):
                return True
        
        return False
    
    def is_broken_plural_analysis(analysis):
        stemcat = analysis.get('stemcat', '')
        num = analysis.get('num', '')
        pattern = analysis.get('pattern', '')
        pos = analysis.get('pos', '')
        stemgloss = analysis.get('stemgloss', '')
        lex = analysis.get('lex', '')
        
        if pos not in ['noun', 'adj']:
            return False
        
        if lex:
            lex_stripped = remove_diacritics(lex)
            if lex_stripped in COLLECTIVE_NOUNS:
                return True
        
        if num == 's' and stemcat == 'N':
            if is_english_plural_in_stemgloss(stemgloss):
                return True
        
        if num != 'p':
            return False
        
        BROKEN_STEMCATS = {'N', 'Ndip', 'N0_Nh'}
        if stemcat in BROKEN_STEMCATS:
            return True
        
        SOUND_STEMCATS = {'Nall', 'NAt', 'NapAt', 'NapAt_L'}
        if stemcat in SOUND_STEMCATS:
            return False
        
        SPECIAL_STEMCATS = {'NAn_Nayn', 'Nel'}
        if stemcat in SPECIAL_STEMCATS:
            return False
        
        if stemcat == 'Nap':
            if pattern:
                sound_markers = ['ُون', 'ِين', 'َات', 'ون', 'ين', 'ات']
                if any(marker in pattern for marker in sound_markers):
                    return False
            
            if pattern and 'فَاعِل' in pattern:
                return False
            
            if is_english_plural_in_stemgloss(stemgloss):
                return True
            
            if pattern:
                if re.search(r'أَ.{0,3}َا.{0,3}', pattern):
                    return True
                if 'أَ' in pattern and 'ِ' in pattern and 'َة' in pattern:
                    return True
                if 'أَ' in pattern and 'اعِي' in pattern:
                    return True
            
            return True
        
        if stemcat in ['N/ap', 'N/At']:
            if pattern:
                sound_markers = ['ُون', 'ِين', 'َات', 'ون', 'ين', 'ات']
                if any(marker in pattern for marker in sound_markers):
                    return False
            
            if is_english_plural_in_stemgloss(stemgloss):
                return True
            
            if pattern:
                broken_pattern_markers = ['أَفْعَال', 'أَفْعِلَة', 'فِعَال', 'فُعُول', 'أَفَاعِيل', 'فُعَلَاء']
                if any(marker in pattern for marker in broken_pattern_markers):
                    return True
            
            return True
        
        if pattern:
            broken_pattern_markers = ['أَفْعَال', 'أَفْعِلَة', 'فِعَال', 'فُعُول', 'أَفَاعِيل']
            if any(marker in pattern for marker in broken_pattern_markers):
                return True
        
        return False

    def extract_arabic_words(text):
        try:
            from camel_tools.tokenizers.word import simple_word_tokenize
            tokens = simple_word_tokenize(text)
            return [token for token in tokens if re.match(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', token)]
        except Exception:
            return re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
    
    def is_prefix_part_of_root(prefix, root):
        if not root or not prefix:
            return False
        root_clean = root.replace('.', '').replace('_', '').replace('-', '')
        return root_clean.startswith(prefix)
    
    def get_stemgloss_root(stemgloss):
        if not stemgloss:
            return ''
        clean = stemgloss.lower().split(';')[0].split(',')[0].strip()
        clean = re.sub(r'\([^)]*\)', '', clean).strip()
        return clean

    def ultra_smart_remove_stopwords_and_prefixes(words, analyzer=None):
        try:
            from naftawayh.stopwords import STOPWORDS
        except:
            STOPWORDS = set()
        
        filtered_words = []
        
        for word in words:
            if word in TEMPORAL_CONNECTORS or word in STOPWORDS:
                continue
            
            word_added = False
            
            for prefix in PREFIXES:
                if word.startswith(prefix) and len(word) > len(prefix) and prefix in STOPWORDS:
                    remaining_word = word[len(prefix):]
                    should_split = False
                    
                    if analyzer:
                        try:
                            original_analyses = analyzer.analyze(word)
                            if original_analyses:
                                original_roots = {a.get('root', '') for a in original_analyses if a.get('root')}
                                if not any(is_prefix_part_of_root(prefix, root) for root in original_roots):
                                    if analyzer.analyze(remaining_word):
                                        should_split = True
                            else:
                                if analyzer.analyze(remaining_word) and len(remaining_word) >= 3:
                                    should_split = True
                        except:
                            pass
                    
                    if should_split and remaining_word not in STOPWORDS:
                        filtered_words.append(remaining_word)
                        word_added = True
                        break
            
            if not word_added:
                filtered_words.append(word)
        
        return filtered_words
    
    def is_broken_plural_wordtagger(word):
        try:
            from naftawayh.wordtag import WordTagger
            
            if not hasattr(is_broken_plural_wordtagger, 'tagger'):
                is_broken_plural_wordtagger.tagger = WordTagger()
            
            tagger = is_broken_plural_wordtagger.tagger
            return (tagger.is_noun(word) and 
                    tagger.one_word_tagging(word) == 'n' and
                    tagger.is_possible_verb(word) < 0)
        except:
            return False
    
    def analyze_broken_plurals(words):
        try:
            if not hasattr(analyze_broken_plurals, 'analyzer'):
                db = get_morphology_db()
                analyze_broken_plurals.analyzer = Analyzer(db)
            
            analyzer = analyze_broken_plurals.analyzer
        except:
            analyzer = None
        
        filtered_words = ultra_smart_remove_stopwords_and_prefixes(words, analyzer)
        
        word_analysis_mapping = [(w, remove_diacritics(w), has_diacritics(w), i) 
                                for i, w in enumerate(filtered_words)]
        
        broken_plurals = []
        
        for original_word, clean_word, has_diac, position in word_analysis_mapping:
            try:
                analyses = analyzer.analyze(clean_word) if analyzer else []
                
                if not analyses:
                    if matches_broken_plural_pattern(original_word):
                        broken_plurals.append({
                            'word': original_word,
                            'root': 'pattern_detected',
                            'stemgloss': 'broken_plural_by_pattern',
                            'pos': 'noun',
                            'analysis': {'pos': 'noun', 'num': 'p', 'source': 'pattern'},
                            'detection_method': 'pattern_matching'
                        })
                        continue
                    
                    if is_broken_plural_wordtagger(clean_word):
                        broken_plurals.append({
                            'word': original_word,
                            'root': 'wordtagger_detected',
                            'stemgloss': 'broken_plural_by_wordtagger',
                            'pos': 'noun',
                            'analysis': {'pos': 'noun', 'num': 'p', 'source': 'wordtagger'},
                            'detection_method': 'wordtagger'
                        })
                    
                    continue
                
                main = None
                
                if has_diac:
                    for analysis in analyses:
                        pos = analysis.get('pos', '')
                        num = analysis.get('num', '')
                        stemcat = analysis.get('stemcat', '')
                        diac = analysis.get('diac', '')
                        
                        if pos == 'noun_prop' or stemcat in ['NAn_Nayn', 'Nel']:
                            continue
                        
                        if pos in ['noun', 'adj'] and num == 'p':
                            if diac_matches_input(original_word, diac, exact=True):
                                main = analysis
                                break
                    
                    if not main:
                        for analysis in analyses:
                            pos = analysis.get('pos', '')
                            num = analysis.get('num', '')
                            stemcat = analysis.get('stemcat', '')
                            diac = analysis.get('diac', '')
                            
                            if pos == 'noun_prop' or stemcat in ['NAn_Nayn', 'Nel']:
                                continue
                            
                            if pos in ['noun', 'adj'] and num == 'p':
                                if diac_matches_input(original_word, diac, exact=False):
                                    main = analysis
                                    break
                    
                    if not main:
                        for analysis in analyses:
                            pos = analysis.get('pos', '')
                            stemcat = analysis.get('stemcat', '')
                            diac = analysis.get('diac', '')
                            
                            if pos == 'noun_prop' or stemcat in ['NAn_Nayn', 'Nel']:
                                continue
                            
                            if pos in ['noun', 'adj']:
                                if diac_matches_input(original_word, diac, exact=True):
                                    main = analysis
                                    break
                    
                    if not main:
                        for analysis in analyses:
                            pos = analysis.get('pos', '')
                            stemcat = analysis.get('stemcat', '')
                            diac = analysis.get('diac', '')
                            
                            if pos == 'noun_prop' or stemcat in ['NAn_Nayn', 'Nel']:
                                continue
                            
                            if pos in ['noun', 'adj']:
                                if diac_matches_input(original_word, diac, exact=False):
                                    main = analysis
                                    break
                    
                    if not main:
                        for analysis in analyses:
                            pos = analysis.get('pos', '')
                            stemcat = analysis.get('stemcat', '')
                            
                            if pos == 'noun_prop' or stemcat in ['NAn_Nayn', 'Nel']:
                                continue
                            
                            if pos in ['noun', 'adj']:
                                main = analysis
                                break
                else:
                    for analysis in analyses:
                        pos = analysis.get('pos', '')
                        num = analysis.get('num', '')
                        stemcat = analysis.get('stemcat', '')
                        
                        if pos == 'noun_prop' or stemcat in ['NAn_Nayn', 'Nel']:
                            continue
                        
                        if pos in ['noun', 'adj'] and num == 'p':
                            main = analysis
                            break
                    
                    if not main:
                        for analysis in analyses:
                            pos = analysis.get('pos', '')
                            stemcat = analysis.get('stemcat', '')
                            
                            if pos == 'noun_prop' or stemcat in ['NAn_Nayn', 'Nel']:
                                continue
                            
                            if pos in ['noun', 'adj']:
                                main = analysis
                                break
                
                if not main:
                    continue
                
                main_num = main.get('num', '')
                main_stemcat = main.get('stemcat', '')
                main_root = main.get('root', '')
                main_stemgloss = main.get('stemgloss', '')
                
                if main_num == 'p':
                    if is_broken_plural_analysis(main):
                        broken_plurals.append({
                            'word': original_word,
                            'root': main_root,
                            'stemgloss': main_stemgloss,
                            'pos': main.get('pos', ''),
                            'analysis': main,
                            'detection_method': 'main_analysis_broken'
                        })
                    continue
                
                elif main_num in ['s', 'd']:
                    if is_broken_plural_analysis(main):
                        broken_plurals.append({
                            'word': original_word,
                            'root': main_root,
                            'stemgloss': main_stemgloss,
                            'pos': main.get('pos', ''),
                            'analysis': main,
                            'detection_method': 'collective_noun'
                        })
                        continue
                    
                    main_gloss_root = get_stemgloss_root(main_stemgloss)
                    
                    plural_analyses = [a for a in analyses
                                      if a.get('num', '') == 'p'
                                      and a.get('pos', '') in ['noun', 'adj']
                                      and a.get('stemcat', '') not in ['NAn_Nayn', 'Nel']]
                    
                    same_meaning_broken = []
                    for a in plural_analyses:
                        a_gloss_root = get_stemgloss_root(a.get('stemgloss', ''))
                        if a_gloss_root == main_gloss_root and is_broken_plural_analysis(a):
                            same_meaning_broken.append(a)
                    
                    if same_meaning_broken:
                        best = same_meaning_broken[0]
                        broken_plurals.append({
                            'word': original_word,
                            'root': best.get('root', ''),
                            'stemgloss': best.get('stemgloss', ''),
                            'pos': best.get('pos', ''),
                            'analysis': best,
                            'detection_method': 'same_meaning_broken'
                        })
                        continue
                    
                    if main_num == 's' and is_english_plural_in_stemgloss(main_stemgloss):
                        if main_root in COLLECTIVE_NOUN_ROOTS:
                            broken_plurals.append({
                                'word': original_word,
                                'root': main_root,
                                'stemgloss': main_stemgloss,
                                'pos': main.get('pos', ''),
                                'analysis': main,
                                'detection_method': 'collective_noun_by_root'
                            })
                            continue
                        elif main_stemcat == 'N':
                            broken_plurals.append({
                                'word': original_word,
                                'root': main_root,
                                'stemgloss': main_stemgloss,
                                'pos': main.get('pos', ''),
                                'analysis': main,
                                'detection_method': 'collective_noun_by_stemcat'
                            })
                            continue
            
            except Exception:
                continue
        
        return broken_plurals
    
    try:
        min_count, max_count = ast.literal_eval(rule_params)
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    results = []
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        words = extract_arabic_words(text)
        broken_plurals = analyze_broken_plurals(words)
        
        results.append({
            'index': i,
            'broken_plurals': broken_plurals,
            'broken_displays': [p['word'] for p in broken_plurals],
            'broken_count': len(broken_plurals)
        })
    
    if mode == "total":
        broken_total = sum(r['broken_count'] for r in results)
        broken_passed = min_count <= broken_total <= max_count
        
        status = "✅" if broken_passed else "❌"
        broken_status = "✅" if broken_passed else f"❌不符合范围[{min_count},{max_count}]"
        
        if len(results) == 1:
            r = results[0]
            
            if r['broken_displays']:
                normalized_words = [unicodedata.normalize('NFC', w) for w in r['broken_displays']]
                word_counts = Counter(normalized_words)
                sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                
                word_lines = []
                for word, count in sorted_words:
                    if count > 1:
                        word_lines.append(f"  {word} ({count}次)")
                    else:
                        word_lines.append(f"  {word}")
                
                broken_text = f"破碎复数: {r['broken_count']}个 :\n" + "\n".join(word_lines)
            else:
                broken_text = "破碎复数: 0个"
            
            return (1 if broken_passed else 0), f"{status} 破碎复数检查结果:\n{broken_text} {broken_status}"
        
        else:
            details = []
            for r in results:
                if r['broken_displays']:
                    normalized_words = [unicodedata.normalize('NFC', w) for w in r['broken_displays']]
                    word_counts = Counter(normalized_words)
                    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                    
                    display_parts = []
                    for word, count in sorted_words:
                        if count > 1:
                            display_parts.append(f"{word} ({count}次)")
                        else:
                            display_parts.append(word)
                    
                    broken_items = "\n  ".join(display_parts)
                    details.append(f"第{r['index']+1}项: 破碎复数{r['broken_count']}个:\n  {broken_items}")
                else:
                    details.append(f"第{r['index']+1}项: 破碎复数0个")
            
            detail_text = "\n".join(details) if details else ""
            return (1 if broken_passed else 0), \
                   f"{status} 破碎复数总计: {broken_total}个{broken_status}\n{detail_text}"
    
    else:
        failed = [r for r in results if not (min_count <= r['broken_count'] <= max_count)]
        passed = not failed
        
        status = "✅ 所有项破碎复数数量都正确" if passed else f"❌ 破碎复数数量不符合范围[{min_count},{max_count}]"
        details = []
        
        for r in results:
            if r['broken_displays']:
                normalized_words = [unicodedata.normalize('NFC', w) for w in r['broken_displays']]
                word_counts = Counter(normalized_words)
                sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                
                display_parts = []
                for word, count in sorted_words:
                    if count > 1:
                        display_parts.append(f"{word} ({count}次)")
                    else:
                        display_parts.append(word)
                
                broken_items = "\n  ".join(display_parts)
                details.append(f"第{r['index']+1}项: 破碎复数{r['broken_count']}个:\n  {broken_items}")
            else:
                details.append(f"第{r['index']+1}项: 破碎复数0个")
        
        if details:
            return (1 if passed else 0), f"{status}\n" + "\n".join(details)
        else:
            return (1 if passed else 0), status


def arabic_broken_plurals_total(corresponding_parts, rule_params, debug=False):
    """检查破碎复数总数"""
    return check_ar_broken_plurals_simple(corresponding_parts, rule_params, mode="total", debug=debug)


def arabic_broken_plurals_each(corresponding_parts, rule_params, debug=False):
    """检查每项破碎复数数量"""
    return check_ar_broken_plurals_simple(corresponding_parts, rule_params, mode="each", debug=debug)


####7.阿语重复
def ar_repeat_each(model_response):

    def is_arabic_text(text):
        """检查文本是否包含阿拉伯语字符"""
        if not text:
            return False
        return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', str(text)))
    
    def clean_arabic_text(text):
        if not text:
            return ""
        
        text = str(text)
        
        # 只保留阿拉伯语字符和空格
        cleaned = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s]', '', text)
        
        # 清理标点残留的多余空格
        cleaned = re.sub(r'\s*،\s*', ' ', cleaned)  # 处理阿拉伯语逗号
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    # 输入验证
    if not model_response:
        return 1, "✅ 输入为空，无重复"
    
    if not isinstance(model_response, (list, tuple)):
        return 0, "❌ 输入必须是列表或元组"
    
    # 处理每个响应
    processed_responses = []
    
    for response in model_response:
        if response is None:
            processed_responses.append("")
            continue
        
        # 检查是否包含阿拉伯语
        if not is_arabic_text(response):
            processed_responses.append("")
            continue
        
        # 清理阿拉伯语文本
        cleaned = clean_arabic_text(response)
        processed_responses.append(cleaned)
    
    # 过滤空值
    valid_responses = [resp for resp in processed_responses if resp and resp.strip()]
    
    if not valid_responses:
        return 1, f"✅ 无有效阿拉伯语数据进行重复检测 (总计{len(model_response)}项)"
    
    # 统计重复
    item_count = {}
    for item in valid_responses:
        if item in item_count:
            item_count[item] += 1
        else:
            item_count[item] = 1
    
    # 找出重复项
    duplicates = []
    for item, count in item_count.items():
        if count > 1:
            duplicates.append((item, count))
    
    # 按重复次数排序
    duplicates.sort(key=lambda x: x[1], reverse=True)
    
    if duplicates:
        # 构建重复信息 - 显示项目索引
        duplicate_parts = []
        
        for item, count in duplicates:
            # 找出重复项的索引位置
            indices = []
            for i, resp in enumerate(processed_responses):
                if resp == item:
                    indices.append(i + 1)  # 转为1基索引
            
            if len(indices) > 1:
                indices_str = "、".join([f"第{idx}项" for idx in indices])
                duplicate_parts.append(f"{indices_str}重复")
    
        duplicate_info = "；".join(duplicate_parts)
        return 0, f"❌ 发现阿拉伯语重复：{duplicate_info}"
    return 1, f"✅ 阿拉伯语无重复 (检查了{len(valid_responses)}个有效项)"

####7.1 阿语单词重复检测
def ar_no_word_repeat(model_response):
    """检查阿拉伯语文本中是否有单词重复"""
    
    def is_arabic_text(text):
        """检查文本是否包含阿拉伯语字符"""
        if not text:
            return False
        return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', str(text)))
    
    def clean_arabic_text(text):
        """清理阿拉伯语文本"""
        if not text:
            return ""
        
        text = str(text)
        
        # 只保留阿拉伯语字符和空格
        cleaned = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s]', '', text)
        
        # 清理标点残留的多余空格
        cleaned = re.sub(r'\s*،\s*', ' ', cleaned)  # 处理阿拉伯语逗号
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    # 输入验证
    if not model_response:
        return 1, "✅ 输入为空，无单词重复"
    
    if not isinstance(model_response, (list, tuple)):
        return 0, "❌ 输入必须是列表或元组"
    
    # 处理每个响应
    processed_responses = []
    
    for response in model_response:
        if response is None:
            processed_responses.append("")
            continue
        
        # 检查是否包含阿拉伯语
        if not is_arabic_text(response):
            processed_responses.append("")
            continue
        
        # 清理阿拉伯语文本
        cleaned = clean_arabic_text(response)
        processed_responses.append(cleaned)
    
    # 检查每个文本中的单词重复
    for i, text in enumerate(processed_responses):
        if not text or not text.strip():
            continue
        
        # 分割成单词
        words = text.split()
        
        # 检测重复单词
        seen_words = set()
        duplicates = []
        
        for word in words:
            if word in seen_words:
                if word not in duplicates:
                    duplicates.append(word)
            else:
                seen_words.add(word)
        
        if duplicates:
            duplicate_words = "、".join(duplicates)
            duplicate_info = f"'{duplicate_words}'" if len(duplicate_words) <= 50 else f"'{duplicate_words[:50]}...'({len(duplicates)} 个词)"
            text_preview = text[:100] + "..." if len(text) > 100 else text
            return 0, f"❌ 第{i+1}项文本 '{text_preview}' 包含重复单词：【{duplicate_info}】"
    
    return 1, f"✅ 阿拉伯语无单词重复 (检查了{len([r for r in processed_responses if r.strip()])}个有效项)"


#######偏正结构
def arabic_idafa_structure_v4(corresponding_parts, rule_params, mode="total"):
    def find_best_analysis(token, analyzer, position, total_tokens):
        """找到最佳分析"""
        try:
            all_analyses = analyzer.analyze(token)
            
            # 接受的词性：名词、专有名词、形容词
            acceptable_pos = ['noun', 'noun_prop', 'adj']
            
            # 过滤可接受的词性
            valid_analyses = [a for a in all_analyses if a.get('pos') in acceptable_pos]
            
            if position == 0:
                # 第一个词：不能带定冠词ال
                no_det_analyses = []
                for analysis in valid_analyses:
                    bw = analysis.get('bw', '')
                    if not bw.startswith('ال/DET+'):  # 不带定冠词
                        no_det_analyses.append(analysis)
                
                if no_det_analyses:
                    return max(no_det_analyses, key=lambda x: x.get('pos_logprob', -999))
            
            elif position == total_tokens - 1:
                # 最后一个词：必须带定冠词ال（确指的正偏结构）
                definite_analyses = []
                for analysis in valid_analyses:
                    bw = analysis.get('bw', '')
                    if bw.startswith('ال/DET+'):  # 必须带定冠词
                        definite_analyses.append(analysis)
                
                if definite_analyses:
                    return max(definite_analyses, key=lambda x: x.get('pos_logprob', -999))
            
            else:
                # 中间的词：不能带定冠词
                no_det_analyses = []
                for analysis in valid_analyses:
                    bw = analysis.get('bw', '')
                    if not bw.startswith('ال/DET+'):  # 不带定冠词
                        no_det_analyses.append(analysis)
                
                if no_det_analyses:
                    return max(no_det_analyses, key=lambda x: x.get('pos_logprob', -999))
            
            return None
            
        except:
            return None
    
    def analyze_definite_structure(text):
        """分析确指结构"""
        from camel_tools.tokenizers.word import simple_word_tokenize
        
        # 初始化
        if not hasattr(analyze_definite_structure, 'analyzer'):
            db = get_morphology_db()
            analyze_definite_structure.analyzer = Analyzer(db)
        
        analyzer = analyze_definite_structure.analyzer
        
        # 分词
        tokens = simple_word_tokenize(text)
        tokens = [t for t in tokens if re.match(r'[\u0600-\u06FF]+', t)]
        
        if len(tokens) < 2:
            return {
                'is_valid': False,
                'errors': ['确指结构必须包含至少两个阿拉伯语词汇'],
                'analysis': [],
                'detailed_errors': []
            }
        
        errors = []
        detailed_errors = []
        word_analyses = []
        total_tokens = len(tokens)
        
        for i, token in enumerate(tokens):
            # 获取所有分析结果用于错误诊断
            try:
                all_analyses = analyzer.analyze(token)
            except:
                all_analyses = []
            
            analysis = find_best_analysis(token, analyzer, i, total_tokens)
            
            # 详细错误分析
            if not analysis:
                # 分析失败的具体原因
                acceptable_pos = ['noun', 'noun_prop', 'adj']
                valid_pos_analyses = [a for a in all_analyses if a.get('pos') in acceptable_pos]
                
                if not all_analyses:
                    detailed_errors.append(f"词汇'{token}'无法识别或分析")
                elif not valid_pos_analyses:
                    # 找出实际的词性
                    actual_pos = list(set([a.get('pos', 'unknown') for a in all_analyses]))
                    pos_map = {
                        'prep': '介词',
                        'verb': '动词',
                        'part': '小品词',
                        'conj': '连词',
                        'pron': '代词',
                        'adv': '副词',
                        'noun': '名词',
                        'noun_prop': '专有名词',
                        'adj': '形容词'
                    }
                    actual_pos_cn = [pos_map.get(pos, pos) for pos in actual_pos]
                    detailed_errors.append(f"词汇'{token}'词性为{'/'.join(actual_pos_cn)}，不符合正偏结构要求（需要名词/专有名词/形容词）")
                else:
                    # 词性正确但定冠词规则不符合
                    if i == 0:
                        detailed_errors.append(f"正次部分'{token}'不能带定冠词")
                    elif i == total_tokens - 1:
                        detailed_errors.append(f"偏次最后一个词'{token}'必须带定冠词")
                    else:
                        detailed_errors.append(f"确指的连环正偏组合中，中间词'{token}'不带定冠词")
                
                # 即使分析失败，也要添加到word_analyses中，用于显示
                word_info = {
                    'token': token,
                    'position': i,
                    'analysis': None,
                    'pos': '',
                    'cas': '',
                    'bw': '',
                    'stemgloss': '',
                    'has_definite': False,
                    'diac': token,  # 使用原始token
                    'display_word': token  # 添加显示用的词
                }
                word_analyses.append(word_info)
                continue
            
            # 即使找到了分析，也要检查是否完全符合规则
            bw = analysis.get('bw', '')
            
            if i == 0:
                # 第一个词不能带定冠词
                if bw.startswith('ال/DET+'):
                    detailed_errors.append(f"正次部分'{token}'不能带定冠词")
            elif i == total_tokens - 1:
                # 最后一个词必须带定冠词
                if not bw.startswith('ال/DET+'):
                    detailed_errors.append(f"偏次最后一个词'{token}'必须带定冠词")
            else:
                # 中间的词不能带定冠词
                if bw.startswith('ال/DET+'):
                    detailed_errors.append(f"确指的连环正偏组合中，中间词'{token}'不带定冠词")
            
            word_info = {
                'token': token,
                'position': i,
                'analysis': analysis,
                'pos': analysis.get('pos', ''),
                'cas': analysis.get('cas', ''),
                'bw': bw,
                'stemgloss': analysis.get('stemgloss', ''),
                'has_definite': bw.startswith('ال/DET+'),
                'diac': analysis.get('diac', token),
                'display_word': token  # 直接使用原始输入的token作为显示
            }
            
            word_analyses.append(word_info)
        
        is_valid = len(detailed_errors) == 0 and len(word_analyses) >= 2
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'detailed_errors': detailed_errors,
            'analysis': word_analyses
        }
    
    def get_display_info(word_info):
        """获取显示信息 - 返回完整的词形"""
        # 直接使用原始输入的token，这样能保证显示完整的词
        return word_info.get('display_word', word_info.get('token', ''))
    
    # 主逻辑
    try:
        if rule_params.startswith('[') and rule_params.endswith(']'):
            min_count, max_count = ast.literal_eval(rule_params)
        else:
            expected_count = int(rule_params)
            min_count = max_count = expected_count
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    results = []
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        
        try:
            result = analyze_definite_structure(text)
        except Exception as e:
            return 0, f"❌ 确指结构检测异常: {str(e)}"
        
        result_info = {
            'index': i,
            'text': text,
            'is_valid': result['is_valid'],
            'errors': result['errors'],
            'detailed_errors': result['detailed_errors'],
            'analysis': result['analysis']
        }
        
        results.append(result_info)
    
    # 返回结果
    if mode == "total":
        valid_count = sum(1 for r in results if r['is_valid'])
        passed = min_count <= valid_count <= max_count
        
        if len(results) == 1:
            r = results[0]
            status = "✅" if r['is_valid'] else "❌"
            
            if r['is_valid']:
                words = [get_display_info(w) for w in r['analysis']]
                words_text = ' '.join(words)
                text = f"{status} 确指正偏结构正确：{words_text}"
            else:
                words = [get_display_info(w) for w in r['analysis']]
                words_text = ' '.join(words) if words else r['text']
                error_details = '；'.join(r['detailed_errors']) if r['detailed_errors'] else '结构不符合要求'
                text = f"{status} 确指正偏结构不正确：{words_text}（{error_details}）"
        else:
            status = "✅" if passed else "❌"
            range_text = f"[{min_count},{max_count}]" if min_count != max_count else str(min_count)
            details = []
            for r in results:
                if r['is_valid']:
                    words = [get_display_info(w) for w in r['analysis']]
                    words_text = ' '.join(words)
                    details.append(f"第{r['index']+1}项: ✅ 确指正偏结构正确：{words_text}")
                else:
                    words = [get_display_info(w) for w in r['analysis']]
                    words_text = ' '.join(words) if words else r['text']
                    error_details = '；'.join(r['detailed_errors']) if r['detailed_errors'] else '结构不符合要求'
                    details.append(f"第{r['index']+1}项: ❌ 确指正偏结构不正确：{words_text}（{error_details}）")
            
            text = f"{status} 确指结构检测{'通过' if passed else f'未通过，期望{range_text}个有效结构，实际{valid_count}个'}\n" + "\n".join(details)
        
        return (1 if passed else 0), text

    else:  # mode == "each"
        failed_items = [r for r in results if not r['is_valid']]
        all_passed = len(failed_items) == 0
        
        status = "✅ 所有项确指正偏结构都正确" if all_passed else "❌ 部分项确指正偏结构不正确"
        details = []
        
        for r in results:
            if r['is_valid']:
                words = [get_display_info(w) for w in r['analysis']]
                words_text = ' '.join(words)
                details.append(f"第{r['index']+1}项: ✅ 确指正偏结构正确：{words_text}")
            else:
                words = [get_display_info(w) for w in r['analysis']]
                words_text = ' '.join(words) if words else r['text']
                error_details = '；'.join(r['detailed_errors']) if r['detailed_errors'] else '结构不符合要求'
                details.append(f"第{r['index']+1}项: ❌ 确指正偏结构不正确：{words_text}（{error_details}）")
        
        return (1 if all_passed else 0), status + ("\n" + "\n".join(details) if details else "")

# 便捷函数
def arabic_idafa_structure_total(corresponding_parts, rule_params):
    """检查确指结构 - 总数模式"""
    return arabic_idafa_structure_v4(corresponding_parts, rule_params, mode="total")

def arabic_idafa_structure_each(corresponding_parts, rule_params):
    """检查确指结构 - 逐项模式"""
    return arabic_idafa_structure_v4(corresponding_parts, rule_params, mode="each")



######圆形标志阴性特指&泛指函数
def check_ar_feminine_noun_forms(corresponding_parts, rule_params, mode="total"):
    """检查阿拉伯语，圆形标志阴性名词的特指和泛指形式"""

    def extract_arabic_words(text):
        """提取阿拉伯语词汇"""
        try:
            from camel_tools.tokenizers.word import simple_word_tokenize
            tokens = simple_word_tokenize(text)
            return [token for token in tokens if re.match(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', token)]
        except Exception:
            return re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
    
    def is_feminine_definite_form(word):
        """检查是否为阴性名词特指形式（带ال的ة结尾）"""
        if word.startswith('ال') and word.endswith('ة'):
            if len(word) >= 4:  # ال + 至少1个字符 + ة
                return True
        return False
    
    def is_feminine_indefinite_form(word):
        """检查是否为阴性名词泛指形式"""
        if len(word) >= 3:
            # 检测带 fatḥa 的完整形式
            if word.endswith('َةٌ') or word.endswith('َةً') or word.endswith('َةٍ'):
                return True
            # 检测省略 fatḥa 的形式
            elif word.endswith('ةٌ') or word.endswith('ةً') or word.endswith('ةٍ'):
                return True
        return False
    
    def analyze_feminine_nouns(words, target_form):
        """分析阴性名词形式"""
        found_nouns = []
        
        for word in words:
            if target_form == "definite":
                if is_feminine_definite_form(word):
                    noun_info = {
                        'word': word,
                        'form': 'definite',
                        'root': word[2:-1],
                        'pattern': 'ال...ة'
                    }
                    found_nouns.append(noun_info)
            
            elif target_form == "indefinite":
                if is_feminine_indefinite_form(word):
                    # 判断是否有 fatḥa 来确定词根长度
                    if word.endswith('َةٌ') or word.endswith('َةً') or word.endswith('َةٍ'):
                        root = word[:-3]  # 去掉َةX
                    else:
                        root = word[:-2]  # 去掉ةX
                    
                    noun_info = {
                        'word': word,
                        'form': 'indefinite',
                        'root': root,
                        'pattern': '...ة'
                    }
                    found_nouns.append(noun_info)
            
            elif target_form == "both":
                if is_feminine_definite_form(word):
                    noun_info = {
                        'word': word,
                        'form': 'definite',
                        'root': word[2:-1],
                        'pattern': 'ال...ة'
                    }
                    found_nouns.append(noun_info)
                elif is_feminine_indefinite_form(word):
                    # 判断是否有 fatḥa 来确定词根长度
                    if word.endswith('َةٌ') or word.endswith('َةً') or word.endswith('َةٍ'):
                        root = word[:-3]  # 去掉َةX
                    else:
                        root = word[:-2]  # 去掉ةX
                    
                    noun_info = {
                        'word': word,
                        'form': 'indefinite',
                        'root': root,
                        'pattern': '...ة'
                    }
                    found_nouns.append(noun_info)
        
        return found_nouns
    
    try:
        params = ast.literal_eval(rule_params)
        if isinstance(params, list) and len(params) >= 3:
            min_count, max_count, target_form = params[0], params[1], params[2]
        else:
            return 0, f"❌ 参数格式错误: 需要 [min_count, max_count, 'form_type']"
        
        if target_form not in ["definite", "indefinite"]:
            return 0, f"❌ form_type参数错误: 必须是 'definite', 'indefinite'"
            
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    # 分析文本
    results = []
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        words = extract_arabic_words(text)
        feminine_nouns = analyze_feminine_nouns(words, target_form)
        
        # 去重
        unique_nouns = []
        seen_nouns = set()
        
        for noun in feminine_nouns:
            word = noun['word']
            if word not in seen_nouns:
                unique_nouns.append(noun)
                seen_nouns.add(word)
        
        noun_displays = []
        for n in unique_nouns:
            noun_displays.append(f"{n['word']}({n['form']})")
        
        result = {
            'index': i,
            'feminine_nouns': unique_nouns,
            'noun_displays': noun_displays,
            'noun_count': len(unique_nouns)
        }
        results.append(result)
    
    # 返回结果
    all_nouns = {}
    for r in results:
        for noun in r['feminine_nouns']:
            word = noun['word']
            if word not in all_nouns:
                all_nouns[word] = noun
    
    noun_total = len(all_nouns)
    noun_passed = min_count <= noun_total <= max_count
    
    form_desc = {
        "definite": "特指形式(ال...ة)",
        "indefinite": "泛指形式(...ةٌ/ةً/ةٍ)"
    }
    
    if len(results) == 1:
        r = results[0]
        noun_text = f"圆形标志阴性名词{form_desc[target_form]}: {r['noun_count']}个 ({'、'.join(r['noun_displays'])})" if r['noun_displays'] else f"圆形标志阴性名词{form_desc[target_form]}: 0个"
        
        status = "✅" if noun_passed else "❌"
        noun_status = "✅" if noun_passed else f"❌不符合范围[{min_count},{max_count}]"
        
        text = f"{status} 圆形标志阴性名词检查结果:\n{noun_text} {noun_status}"
    else:
        status = "✅" if noun_passed else "❌"
        details = []
        
        for r in results:
            noun_list = f"({'、'.join(r['noun_displays'])})" if r['noun_displays'] else ""
            details.append(f"第{r['index']+1}项: {r['noun_count']}个{noun_list}")
        
        noun_status = "✅" if noun_passed else f"❌不符合范围[{min_count},{max_count}]"
        
        text = f"{status} 圆形标志阴性名词{form_desc[target_form]}总计: {noun_total}个{noun_status}\n" + "\n".join(details)
    
    return (1 if noun_passed else 0), text


####阴阳性比例
import re
import ast
from math import gcd
from collections import Counter, defaultdict

def remove_diacritics(text):
    return re.sub(r'[\u064B-\u0657\u0670]', '', text)

def check_ar_gender_ratio(corresponding_parts, rule_params, mode="total"):
    
    def extract_arabic_words(text):
        try:
            from camel_tools.tokenizers.word import simple_word_tokenize
            tokens = simple_word_tokenize(text)
            return [token for token in tokens 
                    if re.match(r'[\u0610-\u06FF\u0750-\u077F\u08A0-\u08FF]+', token)]
        except Exception:
            return re.findall(r'[\u0610-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
    
    def get_syntactic_gender(analysis):
        lexical_gender = analysis.get('gen', '')
        num = analysis.get('num', '')
        rat = analysis.get('rat', '')
        
        if num == 'p' and rat == 'i':
            return 'f'
        
        return lexical_gender
    
    def is_feminine_by_pattern(word, camel_analysis=None):
        """只用于形态规则判断，不包含预定义词表"""
        cleaned = remove_diacritics(word)
        
        if camel_analysis:
            pos = camel_analysis.get('pos', '')
            gen = camel_analysis.get('gen', '')
            num = camel_analysis.get('num', '')
            rat = camel_analysis.get('rat', '')
            
            if pos in ['verb', 'verb_imperfect', 'verb_perfect', 'verb_imperative']:
                return None
            
            if pos in ['noun', 'noun_prop']:
                if num == 'p' and rat == 'i':
                    return True
                return gen == 'f'
            
            if pos == 'adj':
                return gen == 'f'
            
            if pos in ['pron_dem', 'dem_pron', 'pron_rel', 'rel_pron']:
                return gen == 'f'
        
        feminine_endings = ['ة', 'اء', 'ى', 'ات']
        for ending in feminine_endings:
            if cleaned.endswith(ending):
                return True
        
        if cleaned.endswith('ت'):
            word_core = cleaned
            
            for prefix in ['وال', 'فال', 'بال', 'كال', 'لال', 'ال', 'و', 'ف', 'ب', 'ك', 'ل']:
                if word_core.startswith(prefix):
                    word_core = word_core[len(prefix):]
                    break
            
            masculine_t_words = {
                'وقت', 'بيت', 'صوت', 'موت', 'زيت', 'ميت', 'نفت', 'توت', 
                'كبريت', 'نبت', 'قوت', 'فوت', 'سبت', 'حوت', 'قت',
            }
            
            if word_core in masculine_t_words or cleaned in masculine_t_words:
                return False
        
        if camel_analysis:
            root = camel_analysis.get('root', '').replace(' ', '').replace('.', '')
            
            if re.search(r'ت(نا|ي|ك|كم|كن|ه|ها|هم|هن)$', cleaned):
                if 'ت' in root:
                    return False
                else:
                    return True
        
        word_without_suffix = re.sub(r'(نا|ي|ك|كم|كن|ه|ها|هم|هن)$', '', cleaned)
        if len(word_without_suffix) <= 3 and word_without_suffix.endswith('ت'):
            return False
        
        if re.search(r'[اويى]ت(نا|ي|ك|كم|كن|ه|ها|هم|هن)$', cleaned):
            return True
        
        if re.search(r'.{3,}ت(نا|ي|ك|كم|كن|ه|ها|هم|هن)$', cleaned):
            stem_match = re.search(r'(.+)ت(نا|ي|ك|كم|كن|ه|ها|هم|هن)$', cleaned)
            if stem_match:
                stem = stem_match.group(1)
                stem_clean = re.sub(r'^[والبفكل]', '', stem)
                if len(stem_clean) >= 3:
                    return True
        
        if re.search(r'ات(نا|ي|ك|كم|كن|ه|ها|هم|هن)$', cleaned):
            return True
        
        return False
    
    def has_future_prefix(word):
        cleaned = remove_diacritics(word)
        return cleaned.startswith('س') or cleaned.startswith('سوف')
    
    def is_in_fixed_phrase(words, index):
        if index >= len(words):
            return False
            
        word = words[index]
        
        fixed_phrases = {
            'مرة': ['آخر', 'أول', 'كل', 'هذه', 'تلك'],
            'مرات': ['عدة', 'بضع', 'كثير'],
        }
        
        if word not in fixed_phrases:
            return False
        
        if index > 0:
            prev_word = words[index - 1]
            if prev_word in fixed_phrases[word]:
                return True
        
        if index < len(words) - 1:
            next_word = words[index + 1]
            if word == 'مرة' and next_word in ['واحدة', 'أخرى']:
                return True
        
        return False
    
    def remove_stopwords_with_phrase_check(words):
        try:
            from naftawayh.stopwords import STOPWORDS
            
            gender_function_words = {
                'التي', 'الذي', 'اللتان', 'اللذان', 'اللتين', 'اللذين',
                'اللاتي', 'اللواتي', 'الذين',
                'هذه', 'هذا', 'تلك', 'ذلك', 'هاتان', 'هذان',
                'وهذه', 'فهذه', 'بهذه', 'كهذه', 'لهذه',
                'وتلك', 'فتلك', 'بتلك', 'كتلك', 'لتلك',
                'وهاتان', 'فهاتان', 'بهاتان', 'كهاتان', 'لهاتان',
                'وهذا', 'فهذا', 'بهذا', 'كهذا', 'لهذا',
                'وذلك', 'فذلك', 'بذلك', 'كذلك', 'لذلك',
                'وهذان', 'فهذان', 'بهذان', 'كهذان', 'لهذان',
            }
            
            filtered = []
            for i, word in enumerate(words):
                if word in STOPWORDS:
                    if is_in_fixed_phrase(words, i) or word in gender_function_words:
                        filtered.append(word)
                else:
                    filtered.append(word)
            
            return filtered
        except Exception:
            return words
    
    def analyze_gender_with_camel(words):
        try:
            from camel_tools.morphology.analyzer import Analyzer
            from camel_tools.morphology.database import MorphologyDB
            
            if not hasattr(analyze_gender_with_camel, 'analyzer'):
                db = get_morphology_db()
                analyze_gender_with_camel.analyzer = Analyzer(db)
            
            analyzer = analyze_gender_with_camel.analyzer
            feminine_words = []
            masculine_words = []
            skipped_words = []
            
            FORCED_FEMININE_WORDS = {
                'مرة', 'مرات',
                'فاطمة', 'عائشة', 'خديجة', 'مريم', 'زينب', 'ياسمين',
                'التي', 'اللتي', 'اللتان', 'اللتين', 'اللاتي', 'اللواتي',
                'هذه', 'تلك', 'هاتان', 'تانك', 'تيك',
                'وهذه', 'فهذه', 'بهذه', 'كهذه', 'لهذه',
                'وتلك', 'فتلك', 'بتلك', 'كتلك', 'لتلك',
                'وهاتان', 'فهاتان', 'بهاتان', 'كهاتان', 'لهاتان',
                'أيام', 'الأيام', 'ليال', 'الليالي', 'ليلة',
            }
            
            def extract_core_words_from_analyses(analyses):
                core_words = set()
                for analysis in analyses:
                    lex = analysis.get('lex', '')
                    if lex:
                        lex_cleaned = remove_diacritics(lex)
                        core_words.add(lex_cleaned)
                return core_words
            
            def classify_core_words_by_pos(core_words, all_analyses):
                verb_cores = set()
                noun_cores = set()
                
                for analysis in all_analyses:
                    lex = remove_diacritics(analysis.get('lex', ''))
                    pos = analysis.get('pos', '')
                    
                    if lex in core_words:
                        if pos in ['verb', 'verb_imperfect', 'verb_perfect', 'verb_imperative']:
                            verb_cores.add(lex)
                        elif pos in ['noun', 'adj', 'noun_prop', 'noun_num']:
                            noun_cores.add(lex)
                
                return verb_cores, noun_cores
            
            for word_index, word in enumerate(words):
                try:
                    word_cleaned = remove_diacritics(word)
                    
                    # 检查强制阴性词表
                    if word_cleaned in FORCED_FEMININE_WORDS:
                        feminine_words.append({
                            'word': word,
                            'gender': 'feminine',
                            'confidence': 1.0
                        })
                        continue
                    
                    # CAMeL 分析
                    analyses = analyzer.analyze(word)
                    
                    if not analyses:
                        pattern_result = is_feminine_by_pattern(word)
                        if pattern_result is True:
                            feminine_words.append({
                                'word': word,
                                'gender': 'feminine',
                                'confidence': 0.8
                            })
                        elif pattern_result is False:
                            masculine_words.append({
                                'word': word,
                                'gender': 'masculine',
                                'confidence': 0.8
                            })
                        continue
                    
                    # 匹配分析
                    word_undiac = remove_diacritics(word)
                    matched_analyses = []
                    
                    for analysis in analyses:
                        diac = analysis.get('diac', '')
                        diac_undiac = remove_diacritics(diac)
                        
                        if diac_undiac == word_undiac:
                            matched_analyses.append(analysis)
                        elif has_future_prefix(word_undiac):
                            if word_undiac in diac_undiac or diac_undiac in word_undiac:
                                matched_analyses.append(analysis)
                    
                    if not matched_analyses:
                        pattern_result = is_feminine_by_pattern(word)
                        if pattern_result is True:
                            feminine_words.append({
                                'word': word,
                                'gender': 'feminine',
                                'confidence': 0.8
                            })
                        elif pattern_result is False:
                            masculine_words.append({
                                'word': word,
                                'gender': 'masculine',
                                'confidence': 0.8
                            })
                        continue
                    
                    # 检查标点符号和数字
                    has_only_punc_or_digit = all(
                        a.get('pos', '') in ['punc', 'digit'] 
                        for a in matched_analyses
                    )
                    
                    if has_only_punc_or_digit:
                        skipped_words.append(word)
                        continue
                    
                    # ⭐⭐⭐ 改进的副词检查
                    adv_analyses = [a for a in matched_analyses if a.get('pos', '') == 'adv']
                    non_adv_analyses = [a for a in matched_analyses if a.get('pos', '') != 'adv']
                    
                    if adv_analyses:
                        if non_adv_analyses:
                            best_adv_prob = max(a.get('lex_logprob', -999) for a in adv_analyses)
                            best_non_adv_prob = max(a.get('lex_logprob', -999) for a in non_adv_analyses)
                            prob_diff = best_adv_prob - best_non_adv_prob
                            
                            # 1. 如果副词概率显著更高（差异 > 5.0）→ 跳过
                            if best_adv_prob > best_non_adv_prob + 5.0:
                                skipped_words.append(word)
                                continue
                            # ⭐ 2. 如果概率相近（差异 ≤ 1.0）且有副词形态特征（ا结尾）→ 跳过
                            elif abs(prob_diff) <= 1.0 and word_cleaned.endswith('ا'):
                                skipped_words.append(word)
                                continue
                            # 3. 否则使用非副词分析
                            else:
                                matched_analyses = non_adv_analyses
                        else:
                            # 只有副词分析，没有其他分析 → 跳过
                            skipped_words.append(word)
                            continue
                    
                    # 提取核心词
                    core_words = extract_core_words_from_analyses(matched_analyses)
                    
                    # 判断核心词词性
                    verb_cores, noun_cores = classify_core_words_by_pos(core_words, matched_analyses)
                    
                    # 情况1：只有动词核心词 → 排除
                    if verb_cores and not noun_cores:
                        skipped_words.append(word)
                        continue
                    
                    # 情况2：只有名词核心词 → 使用名词分析
                    if noun_cores and not verb_cores:
                        noun_analyses = [a for a in matched_analyses 
                                       if a.get('pos', '') in ['noun', 'adj', 'noun_prop', 'noun_num']]
                        final_analyses = noun_analyses
                    
                    # 情况3：既有动词核心词，也有名词核心词 → 需要进一步判断
                    elif verb_cores and noun_cores:
                        has_feminine_marker = any(core.endswith('ة') for core in noun_cores)
                        
                        if has_feminine_marker:
                            noun_analyses = [a for a in matched_analyses 
                                           if a.get('pos', '') in ['noun', 'adj', 'noun_prop', 'noun_num']]
                            final_analyses = noun_analyses
                        else:
                            verb_analyses = [a for a in matched_analyses 
                                           if a.get('pos', '') in ['verb', 'verb_imperfect', 'verb_perfect', 'verb_imperative']]
                            noun_analyses_list = [a for a in matched_analyses 
                                                if a.get('pos', '') in ['noun', 'adj', 'noun_prop', 'noun_num']]
                            
                            if verb_analyses and noun_analyses_list:
                                best_verb_prob = max(a.get('lex_logprob', -999) for a in verb_analyses)
                                best_noun_prob = max(a.get('lex_logprob', -999) for a in noun_analyses_list)
                                prob_diff = best_verb_prob - best_noun_prob
                                
                                if prob_diff > 1.0:
                                    skipped_words.append(word)
                                    continue
                                else:
                                    final_analyses = noun_analyses_list
                            else:
                                final_analyses = noun_analyses_list if noun_analyses_list else verb_analyses
                    
                    else:
                        non_verb_analyses = [a for a in matched_analyses 
                                           if a.get('pos', '') not in ['verb', 'verb_imperfect', 'verb_perfect', 'verb_imperative']]
                        
                        if not non_verb_analyses:
                            skipped_words.append(word)
                            continue
                        
                        final_analyses = non_verb_analyses
                    
                    # 再次过滤掉标点和数字
                    final_analyses = [a for a in final_analyses 
                                     if a.get('pos', '') not in ['punc', 'digit']]
                    
                    if not final_analyses:
                        skipped_words.append(word)
                        continue
                    
                    # 性别判断逻辑
                    lex_groups = defaultdict(list)
                    
                    for analysis in final_analyses:
                        lex = analysis.get('lex', '')
                        lex_groups[lex].append(analysis)
                    
                    if not lex_groups:
                        continue
                    
                    best_lex = max(lex_groups.items(), 
                                  key=lambda x: x[1][0].get('lex_logprob', -999))[0]
                    
                    best_analyses = lex_groups[best_lex]
                    
                    gender_counts = {'f': 0, 'm': 0}
                    found_valid_analysis = False
                    
                    for analysis in best_analyses:
                        pos = analysis.get('pos', '')
                        gender = get_syntactic_gender(analysis)
                        
                        valid_pos = pos in [
                            'noun', 'adj', 'noun_prop', 'noun_num', 'pron',
                            'rel_pron', 'pron_rel',
                            'rel_adj', 
                            'dem_pron', 'pron_dem'
                        ]
                        
                        if valid_pos and gender in ['f', 'm']:
                            gender_counts[gender] += 1
                            found_valid_analysis = True
                    
                    if not found_valid_analysis:
                        best_analysis = best_analyses[0] if best_analyses else None
                        pattern_result = is_feminine_by_pattern(word, best_analysis)
                        
                        if pattern_result is True:
                            feminine_words.append({
                                'word': word,
                                'gender': 'feminine',
                                'confidence': 0.7
                            })
                        elif pattern_result is False:
                            masculine_words.append({
                                'word': word,
                                'gender': 'masculine',
                                'confidence': 0.7
                            })
                        continue
                    
                    total = gender_counts['f'] + gender_counts['m']
                    
                    if total == 0:
                        continue
                    
                    if gender_counts['f'] > 0 and gender_counts['m'] == 0:
                        feminine_words.append({
                            'word': word,
                            'gender': 'feminine',
                            'confidence': 1.0
                        })
                    elif gender_counts['m'] > 0 and gender_counts['f'] == 0:
                        masculine_words.append({
                            'word': word,
                            'gender': 'masculine',
                            'confidence': 1.0
                        })
                    elif gender_counts['f'] > gender_counts['m']:
                        feminine_words.append({
                            'word': word,
                            'gender': 'feminine',
                            'confidence': gender_counts['f'] / total
                        })
                    elif gender_counts['m'] > gender_counts['f']:
                        masculine_words.append({
                            'word': word,
                            'gender': 'masculine',
                            'confidence': gender_counts['m'] / total
                        })
                    else:
                        best_analysis = best_analyses[0] if best_analyses else None
                        pattern_result = is_feminine_by_pattern(word, best_analysis)
                        
                        if pattern_result is True:
                            feminine_words.append({
                                'word': word,
                                'gender': 'feminine',
                                'confidence': 0.5
                            })
                        elif pattern_result is False:
                            masculine_words.append({
                                'word': word,
                                'gender': 'masculine',
                                'confidence': 0.5
                            })
                    
                except Exception:
                    continue
            
            return feminine_words, masculine_words, skipped_words
            
        except Exception as e:
            return [], [], []
    
    def analyze_gender_with_wordtagger(words):
        try:
            from naftawayh.wordtag import WordTagger
            
            if not hasattr(analyze_gender_with_wordtagger, 'tagger'):
                analyze_gender_with_wordtagger.tagger = WordTagger()
            
            tagger = analyze_gender_with_wordtagger.tagger
            feminine_words = []
            masculine_words = []
            
            for word in words:
                try:
                    pattern_result = is_feminine_by_pattern(word)
                    
                    if pattern_result is True:
                        feminine_words.append({
                            'word': word,
                            'gender': 'feminine',
                            'confidence': 0.7
                        })
                    elif pattern_result is False and tagger.is_noun(word):
                        masculine_words.append({
                            'word': word,
                            'gender': 'masculine',
                            'confidence': 0.6
                        })
                except Exception:
                    continue
            
            return feminine_words, masculine_words
            
        except Exception:
            return [], []
    
    def format_word_list(words):
        word_list = [w['word'] for w in words]
        word_counts = Counter(word_list)
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        formatted_lines = []
        for word, count in sorted_words:
            if count > 1:
                formatted_lines.append(f"  {word} ({count}次)")
            else:
                formatted_lines.append(f"  {word}")
        
        return "\n".join(formatted_lines) if formatted_lines else "  (无)"
    
    try:
        params = ast.literal_eval(rule_params)
        if isinstance(params, list) and len(params) >= 2:
            feminine_ratio = params[0]
            masculine_ratio = params[1]
        else:
            return 0, f"❌ 参数格式错误: 需要 [feminine_ratio, masculine_ratio]"
    except Exception as e:
        return 0, f"❌ 参数格式错误: {e}"
    
    results = []
    
    for i, item in enumerate(corresponding_parts):
        text = str(item or "")
        words = extract_arabic_words(text)
        filtered_words = remove_stopwords_with_phrase_check(words)
        
        feminine_words, masculine_words, skipped_words = analyze_gender_with_camel(filtered_words)
        
        processable_words = len(filtered_words) - len(skipped_words)
        
        if processable_words > 0 and len(feminine_words) + len(masculine_words) < processable_words * 0.3:
            fem_backup, masc_backup = analyze_gender_with_wordtagger(filtered_words)
            existing_words = {w['word'] for w in feminine_words + masculine_words}
            
            skipped_word_set = set(skipped_words)
            feminine_words.extend([w for w in fem_backup 
                                  if w['word'] not in existing_words 
                                  and w['word'] not in skipped_word_set])
            masculine_words.extend([w for w in masc_backup 
                                   if w['word'] not in existing_words 
                                   and w['word'] not in skipped_word_set])
        
        result = {
            'index': i,
            'feminine_words': feminine_words,
            'masculine_words': masculine_words,
            'feminine_count': len(feminine_words),
            'masculine_count': len(masculine_words)
        }
        results.append(result)
    
    if mode == "total":
        total_feminine = 0
        total_masculine = 0
        all_feminine_words = []
        all_masculine_words = []
        
        for r in results:
            all_feminine_words.extend(r['feminine_words'])
            all_masculine_words.extend(r['masculine_words'])
            total_feminine += len(r['feminine_words'])
            total_masculine += len(r['masculine_words'])
        
        if total_feminine == 0 and total_masculine == 0:
            return 0, "❌ 未找到有效的阴性词或阳性词"
        
        if total_feminine > 0 and total_masculine > 0:
            common_divisor = gcd(total_feminine, total_masculine)
            actual_fem_ratio = total_feminine // common_divisor
            actual_masc_ratio = total_masculine // common_divisor
        else:
            actual_fem_ratio = total_feminine
            actual_masc_ratio = total_masculine
        
        ratio_match = (actual_fem_ratio == feminine_ratio and actual_masc_ratio == masculine_ratio)
        
        fem_words_formatted = format_word_list(all_feminine_words)
        masc_words_formatted = format_word_list(all_masculine_words)
        
        word_type_note = ""
        
        fem_text = f"阴性词: {total_feminine}个{word_type_note}\n{fem_words_formatted}"
        masc_text = f"阳性词: {total_masculine}个{word_type_note}\n{masc_words_formatted}"
        
        status = "✅" if ratio_match else "❌"
        ratio_status = f"实际比例 {actual_fem_ratio}:{actual_masc_ratio}" + ("✅" if ratio_match else f" ❌ 不符合要求比例 {feminine_ratio}:{masculine_ratio}")
        
        text = f"{status} 性别词汇比例检查结果:\n{fem_text}\n\n{masc_text}\n\n{ratio_status}"
        
        return (1 if ratio_match else 0), text
    
    else:
        failed = []
        details = []
        
        word_type_note = ""
        
        for r in results:
            fem_count = r['feminine_count']
            masc_count = r['masculine_count']
            
            if fem_count == 0 and masc_count == 0:
                failed.append(r)
                details.append(f"第{r['index']+1}项: 未找到有效词汇")
                continue
            
            if fem_count > 0 and masc_count > 0:
                common_divisor = gcd(fem_count, masc_count)
                actual_fem_ratio = fem_count // common_divisor
                actual_masc_ratio = masc_count // common_divisor
            else:
                actual_fem_ratio = fem_count
                actual_masc_ratio = masc_count
            
            ratio_match = (actual_fem_ratio == feminine_ratio and actual_masc_ratio == masculine_ratio)
            if not ratio_match:
                failed.append(r)
            
            fem_words_formatted = format_word_list(r['feminine_words'])
            masc_words_formatted = format_word_list(r['masculine_words'])
            
            item_detail = f"第{r['index']+1}项: 实际比例 {actual_fem_ratio}:{actual_masc_ratio} {'✅' if ratio_match else f'❌ 不符合 {feminine_ratio}:{masculine_ratio}'}\n"
            item_detail += f"阴性词({fem_count}个):\n{fem_words_formatted}\n"
            item_detail += f"阳性词({masc_count}个):\n{masc_words_formatted}"
            
            details.append(item_detail)
        
        passed = len(failed) == 0
        
        status = "✅ 所有项性别词汇比例都正确" if passed else f"❌ 有{len(failed)}项性别词汇比例不符合要求 {feminine_ratio}:{masculine_ratio}"
        
        return (1 if passed else 0), status + word_type_note + "\n\n" + "\n\n".join(details)


def arabic_gender_ratio_total(corresponding_parts, rule_params):
    return check_ar_gender_ratio(corresponding_parts, rule_params, mode="total")


def arabic_gender_ratio_each(corresponding_parts, rule_params):
    return check_ar_gender_ratio(corresponding_parts, rule_params, mode="each")



################阿拉伯语和英文 混杂比例#####################################################################################
def calculate_arabic_english_word_ratio(text):
    # 统计阿拉伯语词数
    words = re.split(r'[ \n]+', text)
    arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
    arabic_words = [word for word in words if word and re.search(arabic_pattern, word)]
    arabic_count = len(arabic_words)
    
    # 统计英文单词数
    english_words = re.findall(r'[a-zA-Z]+', text)
    english_word_count = len(english_words)
    
    return arabic_count, english_word_count

def arabic_english_ratio(ratio, model_responses):
    for model_response in model_responses:
        arabic_count, english_word_count = calculate_arabic_english_word_ratio(model_response)
        real_ratio = 1 if english_word_count == 0 else arabic_count / english_word_count
        if real_ratio != ratio[0] / ratio[1]:
            return 0, f"❌ 不匹配: 阿拉伯语单词数：{str(arabic_count)}，英文单词数：{str(english_word_count)}，比例：{real_ratio}, 期望比例为：{str(ratio[0])} / {str(ratio[1])} = {str(ratio[0] / ratio[1])}"
    return 1, "✅ 匹配"


if __name__ == "__main__":
    response = [
                "أود أن أرحب بك في مكتبنا، حيث نحن جميعًا هنا لدعمك ومساعدتك في كل ما تحتاجه، وأنا وزملائي سنكون سعداء بالتعاون معك لتحقيق النجاح المشترك.",
                "نحن في هذا المكتب نعمل كفريق واحد، وأنت الآن جزء من هذا الفريق، لذا لا تتردد في التواصل معنا، سواء كنت بحاجة إلى مساعدة أو لديك أي استفسار، فنحن هنا لخدمتك.",
                "أود أن أقدم لك أعضاء فريقنا، حيث كل واحد منا لديه دور مهم في تحقيق أهداف الشركة، ونحن جميعًا ملتزمون بتقديم أفضل ما لدينا لضمان نجاحك ونجاحنا.",
                "نحن سعداء بانضمامك إلينا، وأود أن أؤكد لك أنني وزملائي هنا لدعمك في كل خطوة، فلا تتردد في التواصل معنا إذا كان لديك أي سؤال أو تحتاج إلى أي مساعدة."
            ]
    para = "[5,5]"
    print(ar_independent_pronoun_each(response,para))