"""
印尼语特殊规则检测模块
每个函数包含独立的词库和辅助函数，方便单独修改
"""
try:
    from spellchecker import SpellChecker
    spellchecker_AVAILABLE = True
except ImportError:
    spellchecker_AVAILABLE = False
    print("spellchecker库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyspellchecker", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        print("spellchecker库安装成功，正在导入...")
        from spellchecker import SpellChecker
        spellchecker_AVAILABLE = True
        print("✅ spellchecker库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install pyspellchecker")
        spellchecker_AVAILABLE = False

        
import re


def create_logger(debug):
    """创建日志函数"""
    def log(msg):
        if debug:
            print(msg)
    return log

import re
from spellchecker import SpellChecker

# ==================== 印尼语专项规则集合 ====================
# ==================== 高准确率外来词检测（英语+法语+荷兰语）- 支持首字母筛选 ====================

import re
from typing import Tuple, Dict, List, Set, Optional
from collections import Counter

def check_indonesian_loanwords(content, *args, debug: bool = False, **kwargs) -> Tuple[int, str]:
    """
    高准确率外来词借词检测（仅英语、法语、荷兰语来源）
    
    ⭐ 支持三种调用方式：
    1. check_indonesian_loanwords(content, required_count)
    2. check_indonesian_loanwords(content, required_count, start_letter)
    3. check_indonesian_loanwords(content, "required_count,start_letter")  # 字符串格式
    
    Args:
        content: 文章内容
        *args: 位置参数
            - args[0]: required_count (int) 或 "count,letter" (str)
            - args[1]: start_letter (str, optional) - 当args[0]是整数时使用
        debug: 调试模式
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    
    # ============ 解析参数（兼容字符串格式）============
    if len(args) == 0:
        return 0, "❌ 错误：缺少必需参数 required_count"
    
    first_arg = str(args[0])
    
    # ⭐ 情况1：字符串格式 "3,t"
    if ',' in first_arg:
        parts = [p.strip() for p in first_arg.split(',')]
        try:
            required_count = int(parts[0])
            start_letter = parts[1].lower() if len(parts) > 1 and parts[1] else None
        except (ValueError, IndexError) as e:
            return 0, f"❌ 错误：参数格式错误 '{first_arg}'，应为 '数字,字母' 格式"
    
    # ⭐ 情况2：分离参数 (3, 't')
    else:
        try:
            required_count = int(args[0])
        except (ValueError, TypeError):
            return 0, f"❌ 错误：借词数量必须是整数，当前值: '{args[0]}'"
        
        # 第二个参数：首字母（可选）
        start_letter = None
        if len(args) > 1:
            start_letter = str(args[1]).lower().strip()
    
    # ============ 验证首字母 ============
    if start_letter and (len(start_letter) != 1 or not start_letter.isalpha()):
        return 0, f"❌ 错误：首字母参数无效（'{start_letter}'），应为单个字母"
    
    # ============ 处理输入 ============
    if isinstance(content, list):
        content = ' '.join(str(item) for item in content)
    content = str(content)
    
    if not content.strip():
        return 0, "❌ 错误：输入文本为空"
    
    # ============ 核心借词库（仅英语+法语+荷兰语来源）============
    
    CORE_LOANWORDS = {
        # === 英语来源 ===
        'komputer': 'computer',
        'teknologi': 'technology',
        'aplikasi': 'application',
        'sistem': 'system',
        'elektronik': 'electronic',
        'otomatis': 'automatic',
        'mekanis': 'mechanical',
        
        # 商业/经济
        'bisnis': 'business',
        'strategi': 'strategy',
        'ekonomi': 'economy',
        'investasi': 'investment',
        'diskon': 'discount',
        'promo': 'promotion',
        'desain': 'design',
        'produk': 'product',
        'standar': 'standard',
        'garansi': 'guarantee',
        'servis': 'service',
        'kualitas': 'quality',
        'manajemen': 'management',
        'pemasaran': 'marketing',
        'industri': 'industry',
        'komersial': 'commercial',
        'finansial': 'financial',
        'kredit': 'credit',
        'saldo': 'balance',
        'asuransi': 'insurance',
        'klaim': 'claim',
        'transaksi': 'transaction',
        
        # 餐饮（英语）
        'jus': 'juice',
        'kuliner': 'culinary',
        'resep': 'recipe',
        'ingredien': 'ingredient',
        'krim': 'cream',
        'cokelat': 'chocolate',
        
        # 文化/历史
        'simbol': 'symbol',
        'situs': 'site',
        'monumen': 'monument',  # ✅ 保留
        'artefak': 'artifact',
        'arsitektur': 'architecture',
        'kolonial': 'colonial',
        'galeri': 'gallery',
        'koleksi': 'collection',
        'seremoni': 'ceremony',
        'tradisi': 'tradition',
        
        # 教育
        'universitas': 'university',
        'fakultas': 'faculty',
        'kampus': 'campus',
        'presentasi': 'presentation',
        'diskusi': 'discussion',
        'kelas': 'class',
        'literatur': 'literature',
        'akademis': 'academic',
        'teori': 'theory',
        'praktis': 'practical',
        
        # 交通
        'taksi': 'taxi',
        'tiket': 'ticket',
        'parkir': 'parking',
        'transportasi': 'transportation',
        'bis': 'bus',
        
        # 住宿
        'apartemen': 'apartment',
        'vila': 'villa',
        
        # 医疗
        'klinik': 'clinic',
        'apotik': 'pharmacy',
        'terapi': 'therapy',
        'kalori': 'calorie',
        'konsultasi': 'consultation',
        'diagnosa': 'diagnosis',
        'medis': 'medical',
        
        # 科学
        'spesies': 'species',
        'botani': 'botany',
        'biologi': 'biology',
        'kimia': 'chemistry',
        'fisika': 'physics',
        'geografi': 'geography',
        'astronomi': 'astronomy',
        'geologi': 'geology',
        'ekologi': 'ecology',
        
        # 形容词
        'internasional': 'international',
        'nasional': 'national',
        'lokal': 'local',
        'sentral': 'central',
        'spesial': 'special',
        'aktif': 'active',
        'pasif': 'passive',
        'positif': 'positive',
        'negatif': 'negative',
        'privat': 'private',
        'publik': 'public',
        'profesional': 'professional',
        'efektif': 'effective',
        'efisien': 'efficient',
        'populer': 'popular',
        'favorit': 'favorite',
        'eksklusif': 'exclusive',
        'kompleks': 'complex',
        'fleksibel': 'flexible',
        'stabil': 'stable',
        'dinamis': 'dynamic',
        'unik': 'unique',
        'klasik': 'classic',
        'eksotis': 'exotic',
        'tradisional': 'traditional',
        'spektakuler': 'spectacular',
        'romantis': 'romantic',
        'elegan': 'elegant',
        'kontemporer': 'contemporary',
        'antik': 'antique',
        'historis': 'historic',
        'artifisial': 'artificial',
        'maksimal': 'maximal',
        'minimal': 'minimal',
        'optimal': 'optimal',
        'ilegal': 'illegal',
        
        # 媒体/娱乐
        'foto': 'photo',
        'kamera': 'camera',
        'televisi': 'television',
        'musik': 'music',
        'konser': 'concert',
        'komedi': 'comedy',
        'hobi': 'hobby',
        'joging': 'jogging',
        'fantasi': 'fantasy',
        
        # 政治/政府
        'politik': 'politics',
        'demokrasi': 'democracy',
        'republik': 'republic',
        'parlemen': 'parliament',
        'konstitusi': 'constitution',
        'revolusi': 'revolution',
        'presiden': 'president',  # ⭐ 新增
        
        # 其他高频
        'prioritas': 'priority',
        'metode': 'method',
        'teknik': 'technique',
        'proses': 'process',
        'prosedur': 'procedure',
        'dokumen': 'document',
        'formulir': 'form',
        'informasi': 'information',
        'komunikasi': 'communication',
        'organisasi': 'organization',
        'institusi': 'institution',
        'komunitas': 'community',
        'individu': 'individual',
        'grup': 'group',
        'kolaborasi': 'collaboration',
        'proyek': 'project',
        'kampanye': 'campaign',
        'dekorasi': 'decoration',
        'konsep': 'concept',
        'ide': 'idea',
        'motivasi': 'motivation',
        'emosi': 'emotion',
        'karakter': 'character',
        'personalitas': 'personality',
        'situasi': 'situation',
        'kondisi': 'condition',
        'posisi': 'position',
        'lokasi': 'location',
        'destinasi': 'destination',
        'rute': 'route',
        'akses': 'access',
        'fasilitas': 'facility',
        'utilitas': 'utility',
        'infrastruktur': 'infrastructure',
        'zona': 'zone',
        'sektor': 'sector',
        'kategori': 'category',
        'visi': 'vision',
        'misi': 'mission',
        'sosial': 'social',
        'notifikasi': 'notification',
        'struktur': 'structure',
        'konstruksi': 'construction',
        'renovasi': 'renovation',
        'inovasi': 'innovation',
        'inspirasi': 'inspiration',
        'kreativitas': 'creativity',
        'produktivitas': 'productivity',
        'kompetisi': 'competition',
        'petisi': 'petition',
        'aksesori': 'accessory',
        'dokumentasi': 'documentation',
        'publikasi': 'publication',
        
        # === 法语来源 ===
        'restoran': 'restaurant',
        'kafe': 'café',
        'saus': 'sauce',
        'suvenir': 'souvenir',
        'garasi': 'garage',
        'butik': 'boutique',
        
        # === 荷兰语来源 ===
        'kantor': 'kantoor',
        'kopi': 'koffie',
        'handuk': 'handdoek',
        'koper': 'koffer',
        'kursi': 'stoel',
        'karcis': 'kaartje',
        'kereta': 'karretje',
        'polisi': 'politie',
        'pastor': 'pastoor',
        'tenis': 'tennis',
    }
    
    # ============ 过滤：排除拼写相同的词 ============
    FILTERED_LOANWORDS = {}
    for word, origin in CORE_LOANWORDS.items():
        word_normalized = word.lower().replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        origin_normalized = origin.lower().replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        
        if word_normalized != origin_normalized:
            FILTERED_LOANWORDS[word] = origin
    
    # ⭐ 按首字母筛选借词库
    if start_letter:
        FILTERED_LOANWORDS = {
            word: origin 
            for word, origin in FILTERED_LOANWORDS.items() 
            if word.startswith(start_letter)
        }
        
        if debug:
            print(f"🔤 首字母筛选：仅保留以 '{start_letter}' 开头的借词")
            print(f"   筛选后词库数量：{len(FILTERED_LOANWORDS)} 个")
    
    # ============ ⭐ 扩展的印尼语原生词库 ============
    
    CORE_NATIVE_WORDS = {
        # 语法词
        'yang', 'dengan', 'untuk', 'dari', 'pada', 'di', 'ke', 'oleh', 'karena',
        'ini', 'itu', 'ada', 'tidak', 'bukan', 'akan', 'sudah', 'telah',
        'dan', 'atau', 'tetapi', 'jika', 'kalau', 'bahwa', 'adalah', 'sebagai',
        'tentang', 'kepada', 'bagi', 'antara', 'hingga', 'sampai',
        'melalui', 'menurut', 'selama', 'sejak', 'sebelum', 'sesudah',
        
        # 代词
        'saya', 'anda', 'kamu', 'kami', 'kita', 'mereka', 'dia', 'ia', 'beliau',
        
        # ⭐ 扩展的高频动词词根
        'buat', 'beri', 'terima', 'ambil', 'lihat', 'dengar', 'bicara', 'kata',
        'tanya', 'jawab', 'kerja', 'ajar', 'main', 'tawar', 'saji', 'laku',
        'hadap', 'tunjuk', 'milik', 'guna', 'temu', 'dapat', 'jalan', 'lari',
        'diri', 'duduk', 'tidur', 'bangun', 'makan', 'minum', 'masak', 'datang',
        'pergi', 'pulang', 'kembali', 'tiba', 'kunjung', 'nikmat', 'rasa',
        'suka', 'cinta', 'benci', 'takut', 'harap', 'mimpi', 'usaha', 'latih',
        
        # ⭐ 重点：添加常被误判的词根
        'kenal', 'jual', 'belanja', 'bangga',
        'juang', 'sayang', 'ingat', 'lupa', 'pakai', 'simpan',
        'tulis', 'baca', 'hitung', 'ukur', 'timbang', 'timbul',
        'hidup', 'mati', 'lahir', 'tumbuh', 'kembang', 'ubah',
        
        # 高频名词
        'rumah', 'tempat', 'kota', 'desa', 'kampung', 'orang', 'manusia', 'anak',
        'bapak', 'ibu', 'keluarga', 'teman', 'waktu', 'hari', 'tahun', 'bulan',
        'minggu', 'jam', 'malam', 'pagi', 'siang', 'sore', 'jalan', 'pintu',
        'pasar', 'toko', 'warung', 'air', 'api', 'tanah', 'angin', 'udara',
        'bunga', 'pohon', 'daun', 'gunung', 'laut', 'pantai', 'sungai', 'hutan',
        'batu', 'pulau', 'matahari', 'bulan', 'bintang', 'hewan', 'kucing',
        'anjing', 'ayam', 'burung', 'ikan', 'gedung', 'pusat',
        
        # 高频形容词
        'baik', 'buruk', 'besar', 'kecil', 'tinggi', 'rendah', 'panjang', 'pendek',
        'lebar', 'sempit', 'berat', 'ringan', 'indah', 'cantik', 'bagus', 'jelek',
        'senang', 'sedih', 'marah', 'takut', 'malu', 'bangga', 'mudah', 'sulit',
        'cepat', 'lambat', 'panas', 'dingin', 'hangat', 'sejuk', 'mahal', 'murah',
        'baru', 'lama', 'tua', 'muda', 'ramai', 'sepi', 'tenang', 'lezat', 'enak',
        
        # 其他高频词
        'dapat', 'bisa', 'mampu', 'harus', 'boleh', 'ingin', 'mau', 'sangat',
        'sekali', 'juga', 'lagi', 'hanya', 'cuma', 'semua', 'setiap', 'banyak',
        'sedikit', 'beberapa', 'siapa', 'apa', 'mana', 'kapan', 'mengapa',
        'bagaimana', 'berapa', 'begitu', 'seperti', 'penuh', 'kaya', 'salah', 'satu',
    }
    
    # ⭐ 印尼语常见词根库
    INDONESIAN_ROOTS = {
        'kenal', 'jual', 'belanja', 'bangga', 'terkenal',
        'buat', 'beri', 'ambil', 'lihat', 'dengar', 'kata', 'tanya', 'jawab',
        'kerja', 'ajar', 'main', 'tawar', 'saji', 'laku', 'juang', 'sayang',
        'datang', 'pergi', 'pulang', 'kembali', 'tiba', 'kunjung',
        'suka', 'cinta', 'takut', 'harap', 'mimpi', 'usaha', 'ingat', 'lupa',
    }
    
    # ⭐ 专有名词和地名（修订版 - 移除 monumen）
    PROPER_NOUNS = {
        # 地名
        'jakarta', 'bali', 'yogyakarta', 'surabaya', 'bandung', 'medan',
        'semarang', 'malang', 'solo', 'ubud', 'kuta', 'seminyak',
        'malioboro', 'borobudur', 'prambanan', 'parangtritis', 'tanah', 'lot',
        'nusa', 'dua', 'sanur', 'jimbaran', 'lombok', 'gili', 'trawangan',
        
        # ⚠️ 移除 'monumen'（它是借词，不是专有名词）
        # 保留地理名词
        'candi', 'pantai', 'gunung', 'pulau', 'danau', 'taman',
    }
    
    # ============ ⭐ 词缀检测函数 ============
    
    def is_affixed_native_word(word: str) -> Tuple[bool, str]:
        if word.startswith('per') and word.endswith('an') and len(word) > 7:
            root = word[3:-2]
            if root in INDONESIAN_ROOTS or root in CORE_NATIVE_WORDS:
                return True, f'per-{root}-an (印尼语构词)'
        
        if word.startswith('ke') and word.endswith('an') and len(word) > 6:
            root = word[2:-2]
            if root in INDONESIAN_ROOTS or root in CORE_NATIVE_WORDS:
                return True, f'ke-{root}-an (印尼语构词)'
        
        if word.startswith('ter') and len(word) > 5:
            root = word[3:]
            if root in INDONESIAN_ROOTS or root in CORE_NATIVE_WORDS:
                return True, f'ter-{root} (印尼语被动/状态)'
        
        for prefix in ['meny', 'meng', 'men', 'mem']:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:
                root = word[len(prefix):]
                if root in INDONESIAN_ROOTS or root in CORE_NATIVE_WORDS:
                    return True, f'{prefix}-{root} (印尼语主动语态)'
        
        if word.startswith('ber') and len(word) > 5:
            root = word[3:]
            if root in INDONESIAN_ROOTS or root in CORE_NATIVE_WORDS:
                return True, f'ber-{root} (印尼语动词)'
        
        return False, ''
    
    def is_proper_noun_context(word: str, word_index: int, words_list: List[str]) -> bool:
        if word in PROPER_NOUNS:
            return True
        
        if word_index > 0:
            prev_word = words_list[word_index - 1]
            if prev_word in PROPER_NOUNS:
                return True
        
        if word_index < len(words_list) - 1:
            next_word = words_list[word_index + 1]
            if next_word in PROPER_NOUNS:
                return True
        
        return False
    
    # ============ 主检测流程 ============
    
    text_lower = content.lower()
    text_cleaned = re.sub(r'[^a-zàáâãèéêëìíîïòóôõùúûü\s]', ' ', text_lower)
    words = text_cleaned.split()
    
    unique_words = []
    word_positions = {}
    for i, word in enumerate(words):
        if len(word) >= 3 and word not in word_positions:
            unique_words.append(word)
            word_positions[word] = i
    
    found_loanwords = []
    excluded_words = []
    
    for word in unique_words:
        word_index = word_positions[word]
        
        # ⭐ 首字母筛选
        if start_letter and not word.startswith(start_letter):
            continue
        
        if word in CORE_NATIVE_WORDS:
            if debug:
                excluded_words.append((word, '核心原生词'))
            continue
        
        is_affixed, affix_reason = is_affixed_native_word(word)
        if is_affixed:
            if debug:
                excluded_words.append((word, affix_reason))
            continue
        
        if is_proper_noun_context(word, word_index, words):
            if debug:
                excluded_words.append((word, '专有名词/地名'))
            continue
        
        if word in FILTERED_LOANWORDS:
            found_loanwords.append({
                'word': word,
                'origin': FILTERED_LOANWORDS[word],
                'method': 'core_dict',
                'confidence': 100
            })
            continue
    
    # ============ 统计结果 ============
    
    actual_count = len(found_loanwords)
    
    # ============ 生成输出 ============
    
    letter_info = f" (以字母 '{start_letter}' 开头)" if start_letter else ""
    
    if actual_count == required_count:
        loanword_list = [f"{item['word']} ← {item['origin']}" for item in found_loanwords]
        loanwords_str = ', '.join(loanword_list)
        
        return 1, (
            f"✅ 外来词借词数量符合要求（{actual_count} 个{letter_info}）\n\n"
            f"找到的借词：{loanwords_str}"
        )
    
    elif actual_count < required_count:
        shortage = required_count - actual_count
        loanword_list = [f"{item['word']} ← {item['origin']}" for item in found_loanwords]
        loanwords_str = ', '.join(loanword_list) if loanword_list else '无'
        
        return 0, (
            f"❌ 错误：只找到 {actual_count} 个外来词借词{letter_info}（英语/法语/荷兰语），"
            f"少于要求的 {required_count} 个（还差 {shortage} 个）\n\n"
            f"已找到的借词：{loanwords_str}"
        )
    
    else:
        excess = actual_count - required_count
        loanword_list = [f"{item['word']} ← {item['origin']}" for item in found_loanwords]
        loanwords_str = ', '.join(loanword_list)
        
        return 0, (
            f"❌ 错误：找到 {actual_count} 个外来词借词{letter_info}（英语/法语/荷兰语），"
            f"超过要求的 {required_count} 个（多了 {excess} 个）\n\n"
            f"找到的借词：{loanwords_str}"
        )


def _levenshtein_distance(s1: str, s2: str) -> int:
    """计算编辑距离"""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]



# ==================== 2. 缩写词检测（严格书面缩写版 + 括号注释缩写）====================

def check_indonesian_abbreviations(content, required_count, count_mode='total', debug=False, **kwargs):
    """
    检测印尼语文本中的缩写词数量是否达标
    
    识别两类缩写：
    1. 词库中的标准缩写（KPK, TNI, PR, yg, dgn, sdh等）
    2. 带括号注释的自定义缩写（如：LMS (Learning Management System)）
    
    严格定义：仅识别真正的书面缩写形式
    - ✅ 包括：首字母缩写、书面字母缩写、标准缩写、括号注释缩写
    - ❌ 不包括：口语化表达（udah, nggak, tuh, gitu, aja, sih等）
    - ❌ 不包括：标准完整词汇（yang, dengan, sudah, tapi, di等）
    - ❌ 不包括：带点号的敬语缩写（Yth., Bpk., Ibu.等）
    
    Args:
        content: 文章内容（字符串或列表）
        required_count: 要求的缩写词数量（必须正好等于）
        count_mode: 计数模式 ('total' 或 'unique')
        debug: 是否输出调试信息（默认 False）
        **kwargs: 其他参数（兼容性）
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    import re
    from collections import Counter
    
    # 处理content为列表的情况
    if isinstance(content, list):
        content = ' '.join(str(item) for item in content)
    content = str(content)
    
    # ==================== 仅书面缩写词库 ====================
    
    ABBREVIATIONS = {
        # === 首字母缩写（专有名词/机构）===
        'kpk',          # Komisi Pemberantasan Korupsi
        'tni',          # Tentara Nasional Indonesia
        'polri',        # Kepolisian Republik Indonesia
        'ri',           # Republik Indonesia
        'dpr',          # Dewan Perwakilan Rakyat
        'pbb',          # Perserikatan Bangsa-Bangsa
        'asean',        # Association of Southeast Asian Nations
        'pmk',          # Peraturan Menteri Keuangan
        'uu',           # Undang-Undang
        'sop',          # Standard Operating Procedure
        'npwp',         # Nomor Pokok Wajib Pajak
        'ktp',          # Kartu Tanda Penduduk
        'sim',          # Surat Izin Mengemudi
        'pln',          # Perusahaan Listrik Negara
        'bpjs',         # Badan Penyelenggara Jaminan Sosial
        'pr',           # Pekerjaan Rumah
        'pt',           # Perseroan Terbatas
        'cv',           # Curriculum Vitae / Commanditaire Vennootschap
        'mpr',          # Majelis Permusyawaratan Rakyat
        'bumn',         # Badan Usaha Milik Negara
        'bumd',         # Badan Usaha Milik Daerah
        'pkk',          # Pemberdayaan Kesejahteraan Keluarga
        'apa',          # American Psychological Association
        'lms',          # Learning Management System
        'nim',          # Nomor Induk Mahasiswa
        'wa',           # WhatsApp
        'hrd',          # Human Resources Development
        
        # === 书面字母缩写（连词/介词）===
        'yg',           # yang → yg
        'dgn', 'dg',    # dengan → dgn/dg
        'utk',          # untuk → utk
        'krn',          # karena → krn
        'spy',          # supaya → spy
        'tp',           # tetapi → tp（书面缩写）
        'jd',           # jadi → jd
        'jg',           # juga → jg
        'sm',           # sama → sm
        'pd',           # pada → pd
        'dr',           # dari → dr
        'sbg',          # sebagai → sbg
        'thd',          # terhadap → thd
        'tsb',          # tersebut → tsb
        
        # === 书面音节缩写（动词/形容词）===
        'sdh',          # sudah → sdh（书面）
        'blm',          # belum → blm
        'hrs',          # harus → hrs
        'msh',          # masih → msh
        'bs',           # bisa → bs
        'tdk',          # tidak → tdk（书面）
        'blh',          # boleh → blh
        'prlu',         # perlu → prlu
        'tlh',          # telah → tlh
        'bkn',          # bukan → bkn
        'dpt',          # dapat → dpt
        'akn',          # akan → akn
        
        # === 时间词书面缩写 ===
        'skrg',         # sekarang → skrg
        'kmrn',         # kemarin → kmrn
        'bsk',          # besok → bsk
        'hr',           # hari → hr
        'thn',          # tahun → thn
        'bln',          # bulan → bln
        'mgg',          # minggu → mgg
        'tgl',          # tanggal → tgl
        'td',           # tadi → td
        
        # === 疑问词书面缩写 ===
        'gmn',          # bagaimana → gmn（书面）
        'knp',          # kenapa → knp
        'kpn',          # kapan → kpn
        'dmn',          # dimana → dmn
        'kmn',          # kemana → kmn
        'brp',          # berapa → brp
        'bgmn',         # bagaimana → bgmn
        
        # === 程度副词书面缩写 ===
        'bgt',          # banget → bgt（书面）
        'bnr',          # benar → bnr
        'bnyk',         # banyak → bnyk
        'sgt',          # sangat → sgt
        'trs',          # terus → trs
        
        # === 名词缩写 ===
        'org',          # orang → org
        'tmp',          # tempat → tmp
        'no',           # nomor → no
        'tlp', 'telp',  # telepon → tlp
        'hp',           # handphone → hp
        'info',         # informasi → info
        'foto',         # fotografi → foto
        'dok',          # dokter → dok
        
        # === 介词缩写 ===
        'sblm',         # sebelum → sblm
        'stlh',         # setelah → stlh
        'slm',          # selama → slm
        'krg',          # kurang → krg
        'lbh',          # lebih → lbh
        
        # === 标准缩写 ===
        'dll',          # dan lain-lain
        'dsb',          # dan sebagainya
        'dst',          # dan seterusnya
        'dkk',          # dan kawan-kawan
        'aj',           # saja → aj（书面缩写）
        'etc',          # et cetera
        
        # === 货币和单位 ===
        'rp',           # Rupiah
        'km',           # kilometer
        'kg',           # kilogram
        'gr',           # gram
        'lt',           # liter
        'cm',           # centimeter
        'mm',           # millimeter
        'wib',          # Waktu Indonesia Barat
        'wita',         # Waktu Indonesia Tengah
        'wit',          # Waktu Indonesia Timur
        
        # === 其他专业缩写 ===
        'rt', 'rw',     # Rukun Tetangga/Warga
        'atm',          # ATM
        'nib',          # Nomor Induk Berusaha
        'nik',          # Nomor Induk Kependudukan
        'skck',         # Surat Keterangan Catatan Kepolisian
        'stnk',         # Surat Tanda Nomor Kendaraan
        
        # === 教育相关 ===
        'sd',           # Sekolah Dasar
        'smp',          # Sekolah Menengah Pertama
        'sma',          # Sekolah Menengah Atas
        'smk',          # Sekolah Menengah Kejuruan
        's1', 's2', 's3',  # Strata 1/2/3 (学位)
        
        # === 网络标准缩写 ===
        'btw', 'fyi', 'asap', 'thx', 'pls', 'msg',
        'omg', 'lol', 'brb', 'ttyl', 'imho',
    }
    
    # === 完全排除列表（口语+标准词+敬语缩写）===
    EXCLUDED_WORDS = {
        # === 带点号的敬语缩写（不计入缩写词）===
        'yth',          # Yang Terhormat (Yth.)
        'bpk',          # Bapak (Bpk.)
        'ibu',          # Ibu (Ibu.)
        'sdr',          # Saudara (Sdr.)
        'sdri',         # Saudari (Sdri.)
        'tn',           # Tuan (Tn.)
        'ny',           # Nyonya (Ny.)
        'nn',           # Nona (Nn.)
        
        # === 口语音节简化（不是书面缩写）===
        'udah', 'dah',      # sudah的口语
        'gak', 'ga',        # tidak的口语
        'nggak', 'ngga',    # tidak的口语
        'gpp',              # gak apa-apa
        'tuh', 'nih',       # itu/ini的口语
        'gitu', 'gini',     # begitu/begini的口语
        'ntar', 'nti',      # nanti的口语
        'tau',              # tahu的口语
        'emg',              # emang的缩写（但emang本身是口语）
        
        # === 口语代词 ===
        'gue', 'gua', 'gw', 'ane',
        'lu', 'elu', 'lo', 'loe',
        
        # === 语气词（完整词，不是缩写）===
        'sih', 'aja', 'deh', 'dong', 'kok', 'dunk',
        'ya', 'yah', 'nih', 'lah', 'kah',
        
        # === 口语完整形式 ===
        'banget',           # 完整词
        'emang',            # 完整词
        'kalo', 'kalau',    # 完整词
        'gimana',           # 完整词
        'kenapa',           # 完整词
        'bener', 'benar',   # 完整词
        'banyak',           # 完整词
        'sekarang',         # 完整词
        'tapi', 'tetapi',   # 完整词
        'kayak', 'kaya',    # 完整词
        'buat',             # 完整词
        'pake', 'pakai',    # 完整词
        'bikin',            # 完整词
        'dapet', 'dapat',   # 完整词
        'kasih', 'ngasih',  # 完整词
        'cuma', 'cuman',    # 完整词
        'abis', 'habis',    # 完整词
        'soal', 'soalnya',  # 完整词
        'nyampe', 'sampai', # 完整词
        'mesti',            # 完整词
        'terus',            # 完整词
        'ngerti',           # 完整词（口语 mengerti）
        'ngurangin',        # 完整词（口语 mengurangi）
        
        # === 标准书面语（完整词）===
        'yang', 'dengan', 'untuk', 'karena', 'jadi', 'juga',
        'bisa', 'sudah', 'belum', 'lagi', 'masih', 'harus', 'akan',
        'sama', 'dari', 'pada', 'oleh', 'atau', 'bila', 'jika',
        'maka', 'lalu', 'kemudian', 'seperti', 'tahu', 'orang',
        'sebelum', 'setelah', 'saja', 'ini', 'itu', 'ada', 'tidak',
        'bukan', 'mana', 'siapa', 'kapan', 'dimana', 'bagaimana',
        'apakah', 'bahwa', 'agar', 'supaya', 'tetapi',
        
        # === 完整形容词/副词（不是缩写）===
        'singkat', 'panjang', 'pendek', 'maksimal', 'minimal',
        'cukup', 'kurang', 'lebih',
        
        # === 标准介词/连词（完整词，不是缩写）===
        'di', 'ke', 'dan', 'dalam', 'oleh', 'pada',
        
        # === 其他完整词 ===
        'ya', 'tidak', 'bukan', 'jangan', 'belum', 'sudah',
        'bisa', 'boleh', 'harus', 'perlu', 'mau', 'ingin',
    }
    
    # ==================== 清理文本并提取单词 ====================
    text_lower = content.lower()
    
    # 先移除所有带点号的敬语缩写（如 Yth., Bpk., Ibu.）
    # 这样它们不会被计入缩写词
    text_lower = re.sub(r'\b(yth|bpk|ibu|sdr|sdri|tn|ny|nn)\.', '', text_lower)
    
    # ==================== 1. 改进的括号注释缩写识别 ====================
    # 只匹配真正的缩写形式（2-6个字母）+ 较长的括号注释（20+字符）
    # 避免误匹配如 "singkat (maksimal 1000 kata)"
    bracket_pattern = r'\b([a-z]{2,6})\s*\(([^)]{20,})\)'
    bracket_matches = re.finditer(bracket_pattern, text_lower)
    
    bracket_abbreviations = []
    for match in bracket_matches:
        abbr = match.group(1)
        explanation = match.group(2)
        
        # 额外验证：括号内容应该是完整解释（包含空格和多个单词）
        if ' ' in explanation and len(explanation.split()) >= 2:
            # 排除普通形容词
            if abbr not in EXCLUDED_WORDS:
                bracket_abbreviations.append(abbr)
    
    # ==================== 2. 提取词库中的缩写 ====================
    words = re.findall(r'\b[a-z]+\b', text_lower)
    
    # ==================== 查找缩写词 ====================
    found_abbreviations = []
    found_abbreviations_dict = {}  # 用于记录每个缩写的来源
    
    # 添加括号注释缩写
    for abbr in bracket_abbreviations:
        found_abbreviations.append(abbr)
        if abbr not in found_abbreviations_dict:
            found_abbreviations_dict[abbr] = '括号注释'
    
    # 添加词库中的缩写
    for word in words:
        if len(word) < 2:
            continue
        if word in EXCLUDED_WORDS:
            continue
        if word in ABBREVIATIONS:
            found_abbreviations.append(word)
            if word not in found_abbreviations_dict:
                found_abbreviations_dict[word] = '词库'
    
    # ==================== 统计结果 ====================
    if count_mode == 'unique':
        # 去重：相同的缩写只算一次
        unique_abbrs = list(set(found_abbreviations))
        actual_count = len(unique_abbrs)
        count_description = "不同的缩写词"
        display_list = sorted(unique_abbrs)
    else:
        # 总数：包含重复
        actual_count = len(found_abbreviations)
        count_description = "缩写词（含重复）"
        display_list = sorted(list(set(found_abbreviations)))
    
    # ==================== 判断是否达标（正好等于）====================
    if actual_count == required_count:
        abbreviation_list = ", ".join(display_list[:30])
        if len(display_list) > 30:
            abbreviation_list += f" ... (还有 {len(display_list) - 30} 个)"
        
        msg = f"✅ 正确：文章包含正好 {actual_count} 个{count_description}，符合要求的 {required_count} 个\n\n"
        msg += f"找到的缩写词：{abbreviation_list}"
        
        if count_mode == 'total':
            unique_count = len(set(found_abbreviations))
            if unique_count != actual_count:
                msg += f"\n\n（注：去重后有 {unique_count} 个不同的缩写词）"
        
        if debug:
            word_counts = Counter(found_abbreviations)
            top_words = word_counts.most_common(10)
            msg += f"\n\n【调试信息】使用最多的10个缩写词："
            for word, count in top_words:
                source = found_abbreviations_dict.get(word, '未知')
                msg += f"\n  - {word}: {count}次 (来源: {source})"
        
        return 1, msg
    else:
        if actual_count > required_count:
            difference = actual_count - required_count
            diff_msg = f"多了 {difference} 个"
        else:
            difference = required_count - actual_count
            diff_msg = f"少了 {difference} 个"
        
        msg = f"❌ 错误：文章包含 {actual_count} 个{count_description}，不符合要求的正好 {required_count} 个（{diff_msg}）"
        
        if display_list:
            abbreviation_list = ", ".join(display_list)
            msg += f"\n\n已找到的缩写词：{abbreviation_list}"
            
            if count_mode == 'total' and len(found_abbreviations) > 0:
                word_counts = Counter(found_abbreviations)
                freq_info = [f"{word}({count}次)" for word, count in word_counts.most_common()]
                msg += f"\n详细统计：{', '.join(freq_info)}"
        else:
            msg += "\n\n提示：未找到任何符合要求的缩写词"
        
        return 0, msg

# ==================== 3. 复数形式检测 ====================

def check_indonesian_plurals(content, expected_count, debug=False, **kwargs):
    """
    检测印尼语文章中格式正确的复数形式数量
    
    计数规则：重复出现的复数形式会被多次计数（total模式）
    
    Args:
        content: 印尼语文章内容（字符串或列表）
        expected_count: 期望的复数形式数量
        debug: 是否输出调试信息
        **kwargs: 其他参数（兼容性）
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    import re
    from collections import Counter
    
    # ==================== 本函数专用词库 ====================
    VALID_NOUNS = {
        'anak', 'orang', 'teman', 'keluarga', 'wisatawan', 'turis', 'pengunjung',
        'penduduk', 'warga', 'pemuda', 'kakek', 'nenek', 'pria', 'wanita',
        'guru', 'dokter', 'perawat', 'pelayan', 'sopir', 'pemandu',
        'tempat', 'kota', 'desa', 'negara', 'pulau', 'pantai', 'gunung',
        'sungai', 'danau', 'laut', 'taman', 'kebun', 'hutan', 'jalan',
        'gedung', 'rumah', 'toko', 'pasar', 'restoran', 'hotel', 'penginapan',
        'museum', 'galeri', 'sekolah', 'universitas', 'kantor', 'pabrik',
        'bandara', 'pelabuhan', 'terminal', 'stasiun', 'halte',
        'buku', 'koran', 'majalah', 'surat', 'dokumen', 'foto', 'gambar',
        'barang', 'produk', 'makanan', 'minuman', 'buah', 'sayur',
        'pakaian', 'sepatu', 'tas', 'dompet', 'kunci', 'handphone',
        'mobil', 'motor', 'sepeda', 'bus', 'kereta', 'pesawat', 'kapal',
        'kursi', 'meja', 'lemari', 'ranjang', 'pintu', 'jendela',
        'hari', 'minggu', 'bulan', 'tahun', 'jam', 'menit', 'detik', 'waktu',
        'pagi', 'siang', 'sore', 'malam', 'musim',
        'kegiatan', 'aktivitas', 'acara', 'festival', 'pertunjukan', 'konser',
        'masalah', 'solusi', 'pilihan', 'cara', 'metode', 'sistem',
        'koleksi', 'wahana', 'bangunan', 'objek', 'spot', 'lokasi',
        'pemandangan', 'panorama', 'atraksi', 'wisata',
        'pohon', 'bunga', 'rumput', 'daun', 'batu', 'pasir',
        'hewan', 'burung', 'ikan', 'kucing', 'anjing'
    }

    VALID_ADJECTIVES = {
        'besar', 'kecil', 'tinggi', 'rendah', 'panjang', 'pendek',
        'lebar', 'sempit', 'tebal', 'tipis', 'luas', 'dalam',
        'berat', 'ringan', 'kuat', 'lemah', 'keras', 'lembut',
        'indah', 'cantik', 'bagus', 'jelek', 'menarik', 'membosankan',
        'elok', 'menawan', 'rupawan', 'tampan', 'gagah',
        'bersih', 'kotor', 'rapi', 'berantakan', 'baru', 'lama', 'tua', 'muda',
        'segar', 'layu', 'hidup', 'mati', 'penuh', 'kosong',
        'cepat', 'lambat', 'mudah', 'sulit', 'gampang', 'susah',
        'mahal', 'murah', 'gratis', 'berharga', 'bernilai',
        'panas', 'dingin', 'hangat', 'sejuk', 'lembab', 'kering',
        'ramai', 'sepi', 'tenang', 'bising', 'terang', 'gelap', 'redup',
        'nyaring', 'pelan', 'keras', 'lembut',
        'baik', 'buruk', 'enak', 'lezat', 'pahit', 'manis', 'asin',
        'asam', 'gurih', 'pedas', 'hambar',
        'senang', 'sedih', 'gembira', 'marah', 'takut', 'berani',
        'ramah', 'kasar', 'sopan', 'rajin', 'malas'
    }
    
    # ==================== 本函数专用辅助函数 ====================
    
    def normalize_content(content):
        if isinstance(content, list):
            text = " ".join(str(item) for item in content)
        else:
            text = str(content)
        return text.strip()
    
    def parse_count(value):
        try:
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                cleaned = value.strip().replace('###', '')
                return int(float(cleaned))
            return int(value)
        except:
            return None
    
    def find_reduplications(text):
        """查找所有重叠词，不去重"""
        pattern = r'\b([a-zA-Z]+)-\1\b'
        matches = re.finditer(pattern, text.lower())
        results = []
        for match in matches:
            results.append({
                'full': match.group(0),
                'base': match.group(1),
                'position': match.start()
            })
        return results
    
    def validate_plurals(plural_matches):
        """验证复数形式，保留所有重复"""
        valid = []
        
        for match in plural_matches:
            full_word = match['full']
            base_word = match['base']
            
            # 验证是否为有效的复数形式
            if base_word in VALID_NOUNS:
                valid.append({
                    'word': full_word, 
                    'base': base_word, 
                    'type': '名词',
                    'position': match['position']
                })
            elif base_word in VALID_ADJECTIVES:
                valid.append({
                    'word': full_word, 
                    'base': base_word, 
                    'type': '形容词',
                    'position': match['position']
                })
            elif len(base_word) >= 3:
                # 对于不在词库中的词，如果长度>=3，也认为是有效的
                valid.append({
                    'word': full_word, 
                    'base': base_word, 
                    'type': '名词',
                    'position': match['position']
                })
        
        return valid
    
    # ==================== 主逻辑 ====================
    
    debug = bool(debug) if debug is not None else False
    
    try:
        expected_count = parse_count(expected_count)
        if expected_count is None:
            return 0, "❌ 期望数量格式错误"
        
        text = normalize_content(content)
        if not text:
            return 0, "❌ 文章内容为空"
        
        # 查找所有重叠词
        plural_matches = find_reduplications(text)
        
        # 验证有效性（不去重）
        valid_plurals = validate_plurals(plural_matches)
        
        # 总数计数（包含重复）
        actual_count = len(valid_plurals)
        
        # 统计每个复数形式的出现次数
        plural_counter = Counter([p['word'] for p in valid_plurals])
        unique_count = len(plural_counter)
        
        # ==================== 生成详细说明 ====================
        
        if valid_plurals:
            # 按出现次数排序显示
            plural_items = []
            for word, count in plural_counter.most_common():
                base = next(p['base'] for p in valid_plurals if p['word'] == word)
                word_type = next(p['type'] for p in valid_plurals if p['word'] == word)
                if count > 1:
                    plural_items.append(f"{word}({base}的{word_type}复数，出现{count}次)")
                else:
                    plural_items.append(f"{word}({base}的{word_type}复数)")
            plural_str = "、".join(plural_items)
        else:
            plural_str = "未找到"
        
        # ==================== 判断是否达标 ====================
        
        if actual_count == expected_count:
            msg = f"✅ 正确：文章中包含正好 {actual_count} 个格式正确的复数形式"
            if unique_count != actual_count:
                msg += f"（去重后有 {unique_count} 个不同的复数）"
            msg += f"\n\n找到的复数：{plural_str}"
            return 1, msg
        
        diff = actual_count - expected_count
        if diff > 0:
            msg = f"❌ 错误：文章中包含 {actual_count} 个复数形式，超过期望的 {expected_count} 个（多了 {diff} 个）"
        else:
            msg = f"❌ 错误：文章中包含 {actual_count} 个复数形式，少于期望的 {expected_count} 个（少了 {-diff} 个）"
        
        if unique_count != actual_count:
            msg += f"\n（注：去重后有 {unique_count} 个不同的复数）"
        
        msg += f"\n\n找到的复数：{plural_str}"
        
        if debug:
            msg += f"\n\n【调试信息】"
            msg += f"\n  - 总计数: {actual_count}"
            msg += f"\n  - 不同复数: {unique_count}"
            msg += f"\n  - 详细列表:"
            for p in valid_plurals:
                msg += f"\n    · {p['word']} (位置: {p['position']})"
        
        return 0, msg
        
    except Exception as e:
        import traceback
        return 0, f"❌ 函数执行异常: {str(e)}\n{traceback.format_exc()}"



# ==================== 4. 否定词检测（灵活版 + 语境分析）====================

def check_indonesian_negation_keyword(content, keyword, debug=False, **kwargs):
    """
    检测特定否定词的使用是否正确（灵活版）
    
    核心原则：
    - 如果某个否定结构两种否定词都可以（语义略有不同但都正确），不报错
    - 只检测明确的、无争议的语法错误
    - 考虑语境和完整短语
    
    Args:
        content: 文章内容（字符串或列表）
        keyword: 要检测的否定词 (tidak/bukan/jangan)
        debug: 是否输出调试信息（默认 False）
        **kwargs: 忽略其他参数（兼容性）
    
    Returns:
        tuple: (1/0, 说明信息)
    """
    import re
    
    # ==================== 本函数专用词库 ====================
    
    # 固定搭配（总是正确，不检查）
    FIXED_EXPRESSIONS = {
        'bukan berarti', 'bukan berasal', 'bukan bermaksud', 'bukan berniat',
        'bukan berharap', 'bukan beranggapan', 'bukan berpikir', 'bukan berasumsi',
        'bukan bermain', 'bukan berbicara', 'bukan berlaku', 'bukan bekerja',
        'bukan bertujuan', 'bukan berfungsi', 'bukan main', 'bukan kepalang',
        'tidak lain', 'tidak beda', 'tidak ubahnya',
    }
    
    # 短语模式：如果后面跟这些词，说明是名词性短语，bukan/tidak 都可以
    PHRASE_INDICATORS = {
        'tanpa', 'dengan', 'karena', 'untuk', 'dari', 'tentang', 'seperti',
        'hanya', 'saja', 'pun', 'lagi', 'juga',
    }
    
    # 对比结构标记词（出现这些词说明是对比，bukan/tidak 都可以）
    CONTRAST_MARKERS = {
        'tetapi', 'tapi', 'melainkan', 'namun', 'akan tetapi',
        'sebaliknya', 'justru', 'bahkan',
    }
    
    # 只能用 bukan 的明确情况：纯名词（身份/职业）
    IDENTITY_NOUNS = {
        'guru', 'dokter', 'perawat', 'mahasiswa', 'siswa', 'murid',
        'pilot', 'polisi', 'tentara', 'petani', 'nelayan', 'sopir',
        'pengusaha', 'karyawan', 'pelayan', 'pemandu', 'wartawan',
        'artis', 'penyanyi', 'atlet', 'presiden', 'menteri',
    }
    
    # 只能用 tidak 的明确情况：单个动词词根（无前后缀，无修饰语）
    SIMPLE_VERBS = {
        'pergi', 'datang', 'pulang', 'dateng', 'pergi',
        'makan', 'minum', 'tidur', 'bangun', 'jalan', 'lari',
        'beli', 'jual', 'bayar', 'kirim', 'terima', 'bawa',
        'buka', 'tutup', 'masuk', 'keluar', 'naik', 'turun',
        'suka', 'mau', 'ingin', 'bisa', 'boleh', 'dapat',
        'tahu', 'ingat', 'lupa', 'mengerti', 'paham',
    }
    
    # 只能用 tidak 的明确情况：单个形容词（无修饰语）
    SIMPLE_ADJECTIVES = {
        'besar', 'kecil', 'tinggi', 'rendah', 'panjang', 'pendek',
        'baik', 'buruk', 'bagus', 'jelek', 'cantik', 'indah',
        'bersih', 'kotor', 'baru', 'lama', 'tua', 'muda',
        'panas', 'dingin', 'hangat', 'cepat', 'lambat', 'pelan',
        'mudah', 'sulit', 'gampang', 'susah', 'mahal', 'murah',
        'enak', 'lezat', 'pahit', 'manis', 'asin', 'asam', 'pedas',
        'senang', 'sedih', 'marah', 'takut', 'berani', 'ramah',
        'penting', 'perlu', 'cukup',
    }
    
    # ==================== 辅助函数 ====================
    
    def normalize_content(content):
        if isinstance(content, list):
            text = " ".join(str(item) for item in content)
        else:
            text = str(content)
        return text.strip()
    
    def is_phrase_context(text, match_start, match_end):
        """检查是否在短语语境中（后面有修饰语）"""
        # 获取否定词后的10个词
        after_text = text[match_end:match_end+100].strip()
        
        # 检查是否有短语指示词
        for indicator in PHRASE_INDICATORS:
            if after_text.startswith(indicator) or f' {indicator} ' in after_text[:50]:
                return True
        
        # 检查是否是较长的修饰结构（3个词以上）
        words_after = after_text.split()[:5]
        if len(words_after) >= 3:
            return True
        
        return False
    
    def is_contrast_context(text, match_start):
        """检查是否在对比语境中"""
        # 向前看50个字符
        before_text = text[max(0, match_start-50):match_start]
        # 向后看50个字符
        after_text = text[match_start:match_start+50]
        
        combined = before_text + after_text
        
        # 检查对比标记
        for marker in CONTRAST_MARKERS:
            if marker in combined.lower():
                return True
        
        # 检查是否有逗号分隔的对比结构
        if ',' in before_text or ',' in after_text:
            return True
        
        return False
    
    def check_strict_errors_only(text, keyword_to_check):
        """只检查无争议的明确错误"""
        errors = []
        text_lower = text.lower()
        
        if keyword_to_check == 'tidak':
            # 明确错误：tidak + 身份名词（单个，无修饰）
            for noun in IDENTITY_NOUNS:
                pattern = r'\btidak\s+' + re.escape(noun) + r'(?:\s|[.,;!?]|$)'
                for match in re.finditer(pattern, text_lower):
                    phrase = match.group(0).strip()
                    errors.append({
                        'phrase': phrase,
                        'reason': f'否定身份名词"{noun}"必须使用"bukan"',
                        'suggestion': phrase.replace('tidak', 'bukan'),
                    })
        
        elif keyword_to_check == 'bukan':
            # 明确错误1：bukan + 单个动词（非固定搭配，非对比，非短语）
            for verb in SIMPLE_VERBS:
                pattern = r'\bbukan\s+' + re.escape(verb) + r'(?:\s|[.,;!?]|$)'
                for match in re.finditer(pattern, text_lower):
                    match_start = match.start()
                    match_end = match.end()
                    phrase = match.group(0).strip()
                    
                    # 检查例外情况
                    if phrase.lower() in FIXED_EXPRESSIONS:
                        continue
                    if is_phrase_context(text_lower, match_start, match_end):
                        continue  # 短语语境，两者都可以
                    if is_contrast_context(text_lower, match_start):
                        continue  # 对比语境，两者都可以
                    
                    errors.append({
                        'phrase': phrase,
                        'reason': f'否定单个动词"{verb}"（无修饰语）必须使用"tidak"',
                        'suggestion': phrase.replace('bukan', 'tidak'),
                    })
            
            # 明确错误2：bukan + 单个形容词（无修饰语）
            for adj in SIMPLE_ADJECTIVES:
                pattern = r'\bbukan\s+' + re.escape(adj) + r'(?:\s|[.,;!?]|$)'
                for match in re.finditer(pattern, text_lower):
                    match_start = match.start()
                    match_end = match.end()
                    phrase = match.group(0).strip()
                    
                    # 检查例外情况
                    if is_phrase_context(text_lower, match_start, match_end):
                        continue  # 短语语境，两者都可以
                    if is_contrast_context(text_lower, match_start):
                        continue  # 对比语境，两者都可以
                    
                    errors.append({
                        'phrase': phrase,
                        'reason': f'否定单个形容词"{adj}"（无修饰语）必须使用"tidak"',
                        'suggestion': phrase.replace('bukan', 'tidak'),
                    })
            
            # 明确错误3：bukan + me-/ber- 动词（非固定搭配，非对比）
            active_verb_pattern = r'\bbukan\s+(me\w+|ber\w+)(?:\s|[.,;!?]|$)'
            for match in re.finditer(active_verb_pattern, text_lower):
                match_start = match.start()
                match_end = match.end()
                phrase = match.group(0).strip()
                phrase_clean = phrase.lower().strip('.,;!? ')
                
                # 检查例外
                if phrase_clean in FIXED_EXPRESSIONS:
                    continue
                if is_contrast_context(text_lower, match_start):
                    continue  # 对比语境，允许
                
                errors.append({
                    'phrase': phrase,
                    'reason': f'否定主动动词（非对比语境）应使用"tidak"',
                    'suggestion': phrase.replace('bukan', 'tidak'),
                })
        
        elif keyword_to_check == 'jangan':
            # 明确错误：jangan + 主语代词
            pronouns = ['saya', 'aku', 'kamu', 'dia', 'kami', 'kita', 'mereka']
            for pronoun in pronouns:
                pattern = r'\bjangan\s+' + re.escape(pronoun) + r'\s+\w+'
                for match in re.finditer(pattern, text_lower):
                    phrase = match.group(0).strip()
                    errors.append({
                        'phrase': phrase,
                        'reason': f'"jangan"是命令式，不能有主语"{pronoun}"',
                        'suggestion': phrase.replace('jangan', 'tidak'),
                    })
        
        return errors
    
    def create_logger(debug):
        def log(msg):
            if debug:
                print(f"[DEBUG] {msg}")
        return log
    
    # ==================== 主逻辑 ====================
    
    debug = bool(debug) if debug is not None else False
    log = create_logger(debug)
    
    try:
        keyword = str(keyword).strip().lower()
        
        # 支持口语变体
        keyword_variants = {
            'tidak': ['tidak', 'gak', 'ga', 'nggak', 'ngga', 'tak'],
            'bukan': ['bukan', 'bkn'],
            'jangan': ['jangan', 'jgn']
        }
        
        if keyword not in ['tidak', 'bukan', 'jangan']:
            return 0, f"❌ 错误：'{keyword}' 不是有效的印尼语否定词（应该是 tidak/bukan/jangan）"
        
        text = normalize_content(content)
        if not text:
            return 0, "❌ 文章内容为空"
        
        text_lower = text.lower()
        
        # 检查是否使用了要求的否定词
        variants = keyword_variants.get(keyword, [keyword])
        found_variant = None
        total_count = 0
        
        for variant in variants:
            count = len(re.findall(r'\b' + variant + r'\b', text_lower))
            if count > 0:
                found_variant = variant
                total_count += count
                log(f"找到 '{variant}': {count} 次")
        
        if not found_variant:
            return 0, f"❌ 错误：文章中未找到否定词 '{keyword}' 或其变体 {variants}"
        
        # 只检查明确的、无争议的错误
        strict_errors = check_strict_errors_only(text, keyword)
        
        if not strict_errors:
            return 1, f"✅ 正确：'{found_variant}' 使用正确（共出现 {total_count} 次，无明确语法错误）"
        else:
            # 只报告高置信度的错误
            error_details = []
            for i, err in enumerate(strict_errors[:3], 1):  # 最多显示3个
                detail = f"  {i}. 错误短语：「{err['phrase']}」\n"
                detail += f"     原因：{err['reason']}\n"
                detail += f"     建议：{err['suggestion']}"
                error_details.append(detail)
            
            error_summary = "\n".join(error_details)
            
            if len(strict_errors) > 3:
                error_summary += f"\n  ... 还有 {len(strict_errors) - 3} 个类似错误"
            
            return 0, f"❌ 错误：'{found_variant}' 存在 {len(strict_errors)} 处明确的语法错误\n\n{error_summary}"
        
    except Exception as e:
        import traceback
        return 0, f"❌ 函数执行异常: {str(e)}\n{traceback.format_exc()}"


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        # 应该通过的情况
        {
            'content': 'Aku bukan marah tanpa alasan.',
            'keyword': 'bukan',
            'expected': 1,
            'reason': '短语语境，bukan 正确'
        },
        {
            'content': 'Aku hanya membantu, bukan mengganggu.',
            'keyword': 'bukan',
            'expected': 1,
            'reason': '对比语境，bukan 正确'
        },
        {
            'content': 'Aku tidak marah tanpa alasan.',
            'keyword': 'tidak',
            'expected': 1,
            'reason': 'tidak 也正确'
        },
        
        # 应该报错的情况
        {
            'content': 'Saya tidak guru.',
            'keyword': 'tidak',
            'expected': 0,
            'reason': '身份名词必须用 bukan'
        },
        {
            'content': 'Dia bukan pergi.',
            'keyword': 'bukan',
            'expected': 0,
            'reason': '单个动词必须用 tidak'
        },
        {
            'content': 'Ini bukan besar.',
            'keyword': 'bukan',
            'expected': 0,
            'reason': '单个形容词必须用 tidak'
        },
    ]
    
    print("=" * 60)
    print("否定词检测规则测试")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        result, msg = check_indonesian_negation_keyword(
            test['content'], 
            test['keyword'], 
            debug=False
        )
        
        status = "✅ 通过" if result == test['expected'] else "❌ 失败"
        print(f"\n测试 {i}: {status}")
        print(f"内容: {test['content']}")
        print(f"关键词: {test['keyword']}")
        print(f"期望: {test['expected']}, 实际: {result}")
        print(f"原因: {test['reason']}")
        print(f"结果: {msg}")


# ==================== 5. satu 使用规范检测（完整版 - 修复 paket 缺失）====================

import re
from typing import Tuple, Optional, Dict
from collections import Counter

def check_se_usage(content, min_count: Optional[int] = None, debug: bool = False, **kwargs) -> Tuple[int, str, Dict]:
    """
    检测印尼语中 se + kata pengukur + kata benda 形式的 satu（一）的使用
    
    两种模式：
    1. 如果指定 min_count：要求至少出现指定数量
    2. 如果不指定 min_count：只要有使用且无错误即可
    
    核心规则：
    satu（一）在除了数数等单独使用以外的情景中必须缩写为 se-
    如：seorang（一个人），sebuah（一个物品），seminggu（一周）
    
    错误用法：
    - ❌ satu orang（应该是 seorang）
    - ❌ satu buah rumah（应该是 sebuah rumah）
    - ❌ satu minggu（应该是 seminggu）
    - ❌ satu paket（应该是 sepaket）
    
    Args:
        content: 要检测的文本（可以是字符串或列表）
        min_count: 最少需要出现的次数（None=只要有且无错误即可）
        debug: 是否输出调试信息
        **kwargs: 其他参数（兼容性）
    
    Returns:
        (1/0, 详细说明, 统计数据字典)
    """
    
    # 默认统计数据
    default_stats = {
        'total_se_words': 0,
        'correct_count': 0,
        'wrong_satu_usage_count': 0,
        'wrong_format_count': 0,
        'required_count': min_count,
        'passed': False,
        'correct_words': [],
        'wrong_satu_usages': [],
        'wrong_format_words': [],
        'all_se_words': [],
        'check_mode': 'flexible' if min_count is None else 'strict'
    }
    
    # ============ 本地类型检查和转换 ============
    if content is None:
        return 0, "❌ 错误：输入文本为空（None）", default_stats
    
    # 处理列表类型
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                for key in ['text', 'content', 'message', 'response']:
                    if key in item and isinstance(item[key], str):
                        text_parts.append(item[key])
                        break
            else:
                text_parts.append(str(item))
        text = ' '.join(text_parts)
    else:
        try:
            text = str(content)
        except Exception:
            return 0, f"❌ 错误：无法转换为字符串，类型: {type(content)}", default_stats
    
    if not text or not text.strip():
        return 0, "❌ 错误：输入文本为空", default_stats
    
    # ============ 1. 量词模式（kata pengukur）============
    CLASSIFIER_PATTERNS = [
        # 人的量词
        r'\bseorang\b',
        
        # 物品量词
        r'\bsebuah\b', r'\bsebiji\b', r'\bsebutir\b',
        
        # 形状量词
        r'\bsebatang\b', r'\bselembar\b', r'\bsehelai\b', 
        r'\bsepotong\b', r'\bsekeping\b',
        
        # 动物量词
        r'\bseekor\b',
        
        # 容器量词
        r'\bsepiring\b', r'\bsegelas\b', r'\bsekotak\b', 
        r'\bsekantong\b', r'\bsekarung\b', r'\bsebungkus\b', r'\bsebotol\b',
        
        # 集合量词
        r'\bsepasang\b', r'\bsekelompok\b', r'\bserombongan\b', r'\bsekumpulan\b',
        
        # 单位量词
        r'\bseunit\b', r'\bsepaket\b', r'\bserangkaian\b',
        
        # 时间量词
        r'\bsehari\b', r'\bseminggu\b', r'\bsebulan\b', r'\bsetahun\b',
        r'\bsejam\b', r'\bsemenit\b', r'\bsedetik\b',
        r'\bsesaat\b', r'\bsekejap\b',
    ]
    
    # ============ 2. 错误模式（satu + 量词）- 必须与上面完全对应 ============
    WRONG_SATU_PATTERNS = [
        # 物品和人
        ('orang', 'seorang'),
        ('buah', 'sebuah'),
        ('biji', 'sebiji'),
        ('butir', 'sebutir'),
        
        # 形状
        ('batang', 'sebatang'),
        ('lembar', 'selembar'),
        ('helai', 'sehelai'),
        ('potong', 'sepotong'),
        ('keping', 'sekeping'),
        
        # 动物
        ('ekor', 'seekor'),
        
        # 容器
        ('piring', 'sepiring'),
        ('gelas', 'segelas'),
        ('kotak', 'sekotak'),
        ('kantong', 'sekantong'),
        ('karung', 'sekarung'),
        ('bungkus', 'sebungkus'),
        ('botol', 'sebotol'),
        
        # 集合
        ('pasang', 'sepasang'),
        ('kelompok', 'sekelompok'),
        ('rombongan', 'serombongan'),
        ('kumpulan', 'sekumpulan'),
        
        # ⭐ 单位量词（修复：添加 paket）
        ('unit', 'seunit'),
        ('paket', 'sepaket'),          # ✅ 添加这个！
        ('rangkaian', 'serangkaian'),
        
        # 时间量词
        ('hari', 'sehari'),
        ('minggu', 'seminggu'),
        ('bulan', 'sebulan'),
        ('tahun', 'setahun'),
        ('jam', 'sejam'),
        ('menit', 'semenit'),
        ('detik', 'sedetik'),
        ('saat', 'sesaat'),
        ('kejap', 'sekejap'),
    ]
    
    # ============ 3. 格式错误模式 ============
    WRONG_FORMAT_PATTERNS = [
        (r'\bse\s+\w+', 'se 和后面的词之间不应有空格（应连写）'),
        (r'\bse-\w+', 'se 和后面的词之间不应有连字符'),
    ]
    
    # ============ 4. 查找所有用法 ============
    found_correct = []
    found_wrong_satu = []
    found_wrong_format = []
    
    text_lower = text.lower()
    
    # 4.1 检查错误的 satu + 量词
    for classifier, correct_form in WRONG_SATU_PATTERNS:
        pattern = r'\bsatu\s+' + re.escape(classifier) + r'\b'
        for match in re.finditer(pattern, text_lower):
            found_wrong_satu.append({
                'text': match.group(),
                'wrong_form': f'satu {classifier}',
                'correct_form': correct_form,
                'position': match.start(),
                'context': text[max(0, match.start()-25):min(len(text), match.end()+25)]
            })
    
    # 4.2 检查格式错误
    for pattern, error_msg in WRONG_FORMAT_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            # 排除已经在 wrong_satu 中检测到的
            if not any(ws['position'] == match.start() for ws in found_wrong_satu):
                found_wrong_format.append({
                    'text': match.group(),
                    'position': match.start(),
                    'context': text[max(0, match.start()-25):min(len(text), match.end()+25)],
                    'error': error_msg
                })
    
    # 4.3 查找正确的 se- 量词形式
    for pattern in CLASSIFIER_PATTERNS:
        for match in re.finditer(pattern, text_lower):
            start_pos = match.start()
            end_pos = match.end()
            found_correct.append({
                'word': text[start_pos:end_pos],  # 保留原始大小写
                'word_lower': match.group(),
                'position': start_pos,
                'context': text[max(0, start_pos-20):min(len(text), end_pos+20)]
            })
    
    # ============ 5. 判断结果 ============
    has_no_errors = (len(found_wrong_satu) == 0 and len(found_wrong_format) == 0)
    
    if min_count is None:
        # 灵活模式：只要有使用且无错误即可
        passed = (len(found_correct) > 0 and has_no_errors)
        check_mode = 'flexible'
    else:
        # 严格模式：必须达到指定数量且无错误
        passed = (len(found_correct) >= min_count and has_no_errors)
        check_mode = 'strict'
    
    # ============ 6. 生成详细说明 ============
    detail_parts = []
    
    if passed:
        # ========== 成功情况 ==========
        if check_mode == 'flexible':
            detail_parts.append(f"✅ 正确：找到 {len(found_correct)} 个正确的 se- 量词形式，且无错误用法")
        else:
            detail_parts.append(f"✅ 正确：找到 {len(found_correct)} 个正确的 se- 量词形式（要求至少 {min_count} 个），且无错误用法")
        
        if found_correct:
            detail_parts.append("\n正确使用的 se- 量词形式：")
            word_counter = Counter([item['word_lower'] for item in found_correct])
            
            for i, (word, count) in enumerate(word_counter.most_common(), 1):
                detail_parts.append(f"  {i}. {word} （出现 {count} 次）")
            
            if debug:
                detail_parts.append("\n详细位置：")
                for item in found_correct:
                    detail_parts.append(f"  - {item['word']} (位置 {item['position']})")
    
    else:
        # ========== 失败情况 ==========
        
        # 统计问题数量
        total_issues = len(found_wrong_satu) + len(found_wrong_format)
        if check_mode == 'strict' and min_count is not None and len(found_correct) < min_count:
            total_issues += 1
        elif check_mode == 'flexible' and len(found_correct) == 0:
            total_issues += 1
        
        detail_parts.append(f"❌ 未达到要求，发现 {total_issues} 个问题：")
        
        problem_num = 1
        
        # 问题1：错误使用 satu + 量词
        if found_wrong_satu:
            detail_parts.append(f"\n【问题{problem_num}】错误用法：发现 {len(found_wrong_satu)} 处错误地使用了 'satu + 量词'")
            detail_parts.append("核心规则：satu（一）在与量词搭配时必须缩写为 se-")
            for i, item in enumerate(found_wrong_satu, 1):
                detail_parts.append(f"\n  错误 {i}:")
                detail_parts.append(f"    ❌ 错误写法: '{item['text']}'")
                detail_parts.append(f"    ✅ 正确写法: '{item['correct_form']}'")
                detail_parts.append(f"    📍 位置: 字符 {item['position']}")
                if debug:
                    detail_parts.append(f"    📝 上下文: ...{item['context']}...")
            problem_num += 1
        
        # 问题2：格式错误
        if found_wrong_format:
            detail_parts.append(f"\n【问题{problem_num}】格式错误：发现 {len(found_wrong_format)} 个错误的 se 格式")
            for i, item in enumerate(found_wrong_format, 1):
                detail_parts.append(f"\n  错误 {i}:")
                detail_parts.append(f"    ❌ 错误: '{item['text']}'")
                detail_parts.append(f"    📋 问题: {item['error']}")
                detail_parts.append(f"    📍 位置: 字符 {item['position']}")
                if debug:
                    detail_parts.append(f"    📝 上下文: ...{item['context']}...")
            problem_num += 1
        
        # 问题3：数量不足
        if check_mode == 'strict' and min_count is not None and len(found_correct) < min_count:
            shortage = min_count - len(found_correct)
            detail_parts.append(f"\n【问题{problem_num}】数量不足")
            detail_parts.append(f"  要求: 至少 {min_count} 个 se- 量词形式")
            detail_parts.append(f"  实际: 只找到 {len(found_correct)} 个")
            detail_parts.append(f"  差距: 还差 {shortage} 个")
        elif check_mode == 'flexible' and len(found_correct) == 0:
            detail_parts.append(f"\n【问题{problem_num}】未使用")
            detail_parts.append(f"  文中没有使用任何 se- 量词形式")
        
        # 显示已有的正确用法
        if found_correct:
            detail_parts.append("\n" + "=" * 50)
            detail_parts.append("\n✅ 已正确使用的 se- 量词形式：")
            word_counter = Counter([item['word_lower'] for item in found_correct])
            
            for i, (word, count) in enumerate(word_counter.most_common(), 1):
                detail_parts.append(f"  {i}. {word} （出现 {count} 次）")
            
            if debug:
                detail_parts.append("\n详细位置：")
                for item in found_correct:
                    detail_parts.append(f"  - {item['word']} (位置 {item['position']})")
    
    detail = '\n'.join(detail_parts)
    
    # ============ 7. 构建统计数据 ============
    stats = {
        'total_se_words': len(found_correct),
        'correct_count': len(found_correct),
        'wrong_satu_usage_count': len(found_wrong_satu),
        'wrong_format_count': len(found_wrong_format),
        'required_count': min_count,
        'passed': passed,
        'correct_words': [item['word'] for item in found_correct],
        'wrong_satu_usages': [item['text'] for item in found_wrong_satu],
        'wrong_format_words': [item['text'] for item in found_wrong_format],
        'all_se_words': [item['word'] for item in found_correct],
        'check_mode': check_mode
    }
    
    return (1 if passed else 0), detail, stats



# ==================== 6. 印尼语主动语态检测（仅 me- 前缀版 - 已修正）====================

import re
from typing import Tuple, Dict, List

def check_active_voice(text: str, exact_count: int = 5, debug: bool = False) -> Tuple[bool, str, Dict]:
    """
    检测印尼语主动语态动词（仅 me- 前缀及其变体）
    
    ⭐ 核心规则（2024版 - 已修正）：
    1. 只计算 me-/mem-/men-/meng-/meny-/menge-/memper- 开头的词
    2. 排除明确的非动词（名词、介词、副词等）
    3. ⭐ 包括系动词（merupakan, menjadi）- 它们也是主动形式
    4. ⭐ ber- 前缀的词完全不计入（根据题目要求）
    
    Args:
        text: 要检测的文本
        exact_count: 要求的精确主动语态动词数量
        debug: 是否输出调试信息
    
    Returns:
        (是否通过, 详细说明, 统计数据)
    """
    
    # ============ 类型检查和转换 ============
    if text is None:
        return False, "❌ 错误：输入文本为空（None）", {
            'total_active': 0,
            'all_verbs': [],
            'required_count': exact_count,
            'passed': False
        }
    
    # 处理列表类型
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                for key in ['text', 'content', 'message', 'response']:
                    if key in item and isinstance(item[key], str):
                        text_parts.append(item[key])
                        break
            else:
                text_parts.append(str(item))
        text = ' '.join(text_parts)
    
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception as e:
            return False, f"❌ 错误：无法转换为字符串，类型: {type(text)}", {
                'total_active': 0,
                'all_verbs': [],
                'required_count': exact_count,
                'passed': False
            }
    
    if not text.strip():
        return False, "❌ 错误：输入文本为空", {
            'total_active': 0,
            'all_verbs': [],
            'required_count': exact_count,
            'passed': False
        }
    
    text_lower = text.lower()
    
    # ============ ⭐ me- 开头但不是动词的排除词汇 ============
    me_non_verbs = {
        # 代词
        'mereka',
        
        # 名词
        'media', 'meja', 'merah', 'metal', 'meter',
        'memori', 'menu', 'menteri', 'mesin', 'merek',
        'metode', 'medan',
        
        # 副词/连词
        'memang', 'melainkan',
        
        # 介词
        'melalui', 'menuju', 'menurut', 'mengenai', 'menjelang',
        'melampaui',
        
        # 形容词
        'medis', 'mekanik',
        
        # ⚠️ 注意：不包括系动词！
        # 'menjadi' 和 'merupakan' 虽然是系动词，
        # 但它们仍然是主动语态形式，所以不排除
    }
    
    # ============ 查找所有 me- 主动动词 ============
    all_active_verbs = []
    found_positions = set()
    excluded_verbs = []
    ber_verbs_found = []  # 用于调试：记录被排除的 ber- 词
    
    # 1. memper- 前缀（优先级最高）
    memper_pattern = r'\bmemper[a-z]{2,}\b'
    for match in re.finditer(memper_pattern, text_lower):
        verb_lower = match.group()
        start_pos = match.start()
        end_pos = match.end()
        
        if start_pos not in found_positions:
            all_active_verbs.append({
                'verb': text[start_pos:end_pos],
                'verb_lower': verb_lower,
                'position': start_pos,
                'context': text[max(0, start_pos-30):min(len(text), end_pos+30)],
                'type': 'memper-',
                'reason': '使役动词前缀'
            })
            found_positions.add(start_pos)
    
    # 2. me- 系列前缀
    me_pattern = r'\bme(?:m|n|ng|ny|nge)?[a-z]{2,}\b'
    for match in re.finditer(me_pattern, text_lower):
        verb_lower = match.group()
        start_pos = match.start()
        end_pos = match.end()
        
        if start_pos in found_positions:
            continue
            
        # 排除明确的非动词
        if verb_lower in me_non_verbs:
            if debug:
                excluded_verbs.append({
                    'verb': text[start_pos:end_pos],
                    'reason': f'非动词 - {get_word_type_me(verb_lower)}',
                    'position': start_pos
                })
            continue
            
        # 排除重复的 memper-
        if verb_lower.startswith('memper'):
            if debug:
                excluded_verbs.append({
                    'verb': text[start_pos:end_pos],
                    'reason': 'memper- 已在前面匹配',
                    'position': start_pos
                })
            continue
        
        # ⭐ 保留所有其他 me- 词（包括系动词）
        verb_type = 'me-'
        reason = '主动态前缀 (me-)'
        
        # 特殊标注系动词
        if verb_lower in {'menjadi', 'merupakan'}:
            reason = '主动态前缀 (me-) - 系动词'
        
        all_active_verbs.append({
            'verb': text[start_pos:end_pos],
            'verb_lower': verb_lower,
            'position': start_pos,
            'context': text[max(0, start_pos-30):min(len(text), end_pos+30)],
            'type': verb_type,
            'reason': reason
        })
        found_positions.add(start_pos)
    
    # ⭐ 3. 检测 ber- 词汇（仅用于调试，不计入结果）
    if debug:
        ber_pattern = r'\b(ber|bel|be)[a-z]{2,}\b'
        for match in re.finditer(ber_pattern, text_lower):
            verb_lower = match.group()
            start_pos = match.start()
            end_pos = match.end()
            
            # 排除明显的非动词
            ber_non_verbs = {
                'beras', 'berita', 'belakang', 'besok', 'berat', 'besar',
                'berani', 'benar', 'begitu', 'belum', 'berdasarkan'
            }
            
            if verb_lower not in ber_non_verbs:
                ber_verbs_found.append({
                    'verb': text[start_pos:end_pos],
                    'position': start_pos,
                    'reason': '根据题目要求不计入（仅计算 me- 前缀）'
                })
    
    all_active_verbs.sort(key=lambda x: x['position'])
    
    # ============ 判断结果 ============
    total_count = len(all_active_verbs)
    passed = (total_count == exact_count)
    
    # ============ 生成详细说明 ============
    detail_parts = []
    
    detail_parts.append("⭐ 检测范围：仅计算 me- 前缀及其变体（me-/mem-/men-/meng-/meny-/menge-/memper-）")
    detail_parts.append("⭐ 包括：系动词（merupakan, menjadi）也算作主动形式")
    detail_parts.append("⭐ 不包括：ber- 前缀的词（根据题目要求）\n")
    
    if passed:
        detail_parts.append(f"✅ 正确：找到正好 {total_count} 个主动语态动词（要求正好 {exact_count} 个）\n")
    else:
        if total_count < exact_count:
            shortage = exact_count - total_count
            detail_parts.append(f"❌ 错误：只找到 {total_count} 个主动语态动词，少于要求的 {exact_count} 个（还差 {shortage} 个）\n")
        else:
            excess = total_count - exact_count
            detail_parts.append(f"❌ 错误：找到 {total_count} 个主动语态动词，超过要求的 {exact_count} 个（多了 {excess} 个）\n")
    
    detail_parts.append(f"📊 检测到的主动语态动词（共 {total_count} 个）：")
    for i, item in enumerate(all_active_verbs, 1):
        # 标注系动词
        marker = " 🔹系动词" if item['verb_lower'] in {'menjadi', 'merupakan'} else ""
        detail_parts.append(f"  {i:2d}. {item['verb']:20s} [{item['type']:8s}] (位置 {item['position']:4d}){marker}")
        if debug:
            detail_parts.append(f"      上下文: ...{item['context']}...")
    
    if debug and excluded_verbs:
        detail_parts.append(f"\n🔍 调试信息 - 被排除的 me- 词（共 {len(excluded_verbs)} 个）：")
        for i, item in enumerate(excluded_verbs, 1):
            detail_parts.append(f"  {i:2d}. {item['verb']:20s} (位置 {item['position']:4d})")
            detail_parts.append(f"      原因: {item['reason']}")
    
    if debug and ber_verbs_found:
        detail_parts.append(f"\n🔍 调试信息 - 检测到但未计入的 ber- 词（共 {len(ber_verbs_found)} 个）：")
        for i, item in enumerate(ber_verbs_found, 1):
            detail_parts.append(f"  {i:2d}. {item['verb']:20s} (位置 {item['position']:4d})")
            detail_parts.append(f"      原因: {item['reason']}")
    
    detail = '\n'.join(detail_parts)
    
    # ============ 统计数据 ============
    stats = {
        'total_active': total_count,
        'all_verbs': [v['verb'] for v in all_active_verbs],
        'all_verbs_with_type': [(v['verb'], v['type']) for v in all_active_verbs],
        'all_verbs_detailed': [
            {
                'verb': v['verb'],
                'type': v['type'],
                'position': v['position'],
                'reason': v['reason']
            } for v in all_active_verbs
        ],
        'required_count': exact_count,
        'difference': total_count - exact_count,
        'passed': passed,
        'excluded_count': len(excluded_verbs),
        'excluded_verbs': [v['verb'] for v in excluded_verbs] if debug else [],
        'ber_verbs_found': len(ber_verbs_found),
        'ber_verbs_list': [v['verb'] for v in ber_verbs_found] if debug else [],
        'check_mode': 'me_prefix_only_include_copula',
        'copula_verbs': [v['verb'] for v in all_active_verbs if v['verb_lower'] in {'menjadi', 'merupakan'}]
    }
    
    return passed, detail, stats


def get_word_type_me(word: str) -> str:
    """
    辅助函数：返回 me- 开头词的类型
    
    Args:
        word: 要检查的词
    
    Returns:
        词的类型（中文说明）
    """
    if word in {'menjadi', 'merupakan'}:
        return '系动词（但仍算主动形式）'
    elif word in {'mereka'}:
        return '代词'
    elif word in {'media', 'meja', 'metal', 'meter', 'memori', 'menu', 'menteri', 'mesin', 'merek', 'metode', 'medan'}:
        return '名词'
    elif word in {'memang', 'melainkan'}:
        return '副词/连词'
    elif word in {'melalui', 'menuju', 'menurut', 'mengenai', 'menjelang', 'melampaui'}:
        return '介词'
    elif word in {'medis', 'mekanik'}:
        return '形容词'
    else:
        return '非动词'


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试文本（包含 menjadi）
    test_text = [
        "Nusantara Tech menggelar acara peluncuran ponsel lipat Garuda X di Jakarta Convention Center pada 15 Januari 2024. Acara ini menarik perhatian banyak penggemar teknologi dan media lokal. Garuda X merupakan ponsel lipat 5G pertama buatan Indonesia, hasil kerja sama teknologi dengan Samsung Korea. Ponsel ini menawarkan desain inovatif dan fitur canggih yang diharapkan dapat bersaing di pasar global. Nusantara Tech berkomitmen untuk mengembangkan produk berkualitas tinggi yang memenuhi kebutuhan konsumen modern. Peluncuran ini menandai langkah besar bagi industri teknologi Indonesia, yang semakin berani bersaing di kancah internasional.",
        "Pada acara tersebut, CEO Nusantara Tech, Budi Santoso, menyampaikan rasa bangganya atas pencapaian ini. \"Kami berusaha keras untuk menghadirkan produk yang dapat dibanggakan oleh masyarakat Indonesia,\" ujar Budi. Garuda X dilengkapi dengan layar AMOLED fleksibel yang dapat dilipat, prosesor terbaru, dan kamera berkualitas tinggi. Fitur-fitur ini dirancang untuk memberikan pengalaman pengguna yang optimal. Selain itu, ponsel ini mendukung jaringan 5G, memungkinkan pengguna menikmati kecepatan internet yang lebih tinggi. Nusantara Tech juga berencana untuk memperluas pasar ke negara-negara Asia Tenggara lainnya, dengan harapan dapat meningkatkan ekspor produk teknologi Indonesia.",
        "Para pengunjung acara peluncuran berkesempatan mencoba langsung Garuda X dan memberikan tanggapan positif. Banyak yang terkesan dengan desain elegan dan performa ponsel ini. Nusantara Tech berharap dapat meningkatkan penjualan melalui strategi pemasaran yang efektif. Produk ini akan tersedia di toko-toko resmi dan platform e-commerce mulai bulan depan. Dengan peluncuran Garuda X, Nusantara Tech menunjukkan bahwa Indonesia mampu berinovasi dan bersaing di industri teknologi global. Dukungan dari Samsung Korea juga memperkuat posisi Nusantara Tech sebagai pemain utama dalam pengembangan teknologi di Indonesia. Para analis memprediksi produk ini akan menjadi salah satu unggulan."
    ]
    
    print("=" * 100)
    print("印尼语主动语态检测 - 仅 me- 前缀版测试（已修正 - 包含系动词）")
    print("=" * 100)
    
    # 测试：统计文本中的 me- 主动动词
    print("\n【测试：统计文本中的 me- 主动语态动词数量】")
    passed, detail, stats = check_active_voice(test_text, exact_count=999, debug=True)
    print(detail)
    print(f"\n💡 结果：文本中实际包含 {stats['total_active']} 个 me- 主动语态动词")
    
    if stats.get('copula_verbs'):
        print(f"💡 其中包含系动词：{', '.join(stats['copula_verbs'])}")
    
    if stats['ber_verbs_found'] > 0:
        print(f"💡 补充：检测到 {stats['ber_verbs_found']} 个 ber- 词汇（未计入结果）")
    
    print("\n" + "=" * 100)
    print("📌 结论：")
    print(f"   - 仅计算 me- 前缀（包括系动词），文本包含 {stats['total_active']} 个主动语态动词")
    print(f"   - rule 名称保持为: check_active_voice:###数量1###")
    print("=" * 100)


# ==================== 7. 印尼语被动语态检测（精确数量版 - 仅识别 di- 词头 - 已修正）====================

import re
from typing import Tuple, Dict, List

def check_passive_voice(text: str, exact_count: int = 8, debug: bool = False) -> Tuple[bool, str, Dict]:
    """
    检测印尼语被动语态动词（仅 di- 前缀连写词）
    
    ⭐ 核心规则（2024版 - 已修正）：
    1. 只计算 di- 开头的连写词（如 dikembangkan, dilakukan）
    2. 排除明确的非动词（名词、形容词、外来词）
    3. ⭐ 不计算 "di + 空格 + 词" 的介词结构（如 "di Jakarta"）
    4. ⭐ 排除 distribusi 等外来名词
    
    Args:
        text: 要检测的文本
        exact_count: 要求的精确被动语态动词数量
        debug: 是否输出调试信息
    
    Returns:
        (是否通过, 详细说明, 统计数据)
    """
    
    # ============ 类型检查和转换 ============
    if text is None:
        return False, "❌ 错误：输入文本为空（None）", {
            'total_passive': 0,
            'passive_verbs': [],
            'required_count': exact_count,
            'passed': False
        }
    
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                for key in ['text', 'content', 'message', 'response']:
                    if key in item and isinstance(item[key], str):
                        text_parts.append(item[key])
                        break
            else:
                text_parts.append(str(item))
        text = ' '.join(text_parts)
    
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception as e:
            return False, f"❌ 错误：无法转换为字符串，类型: {type(text)}", {
                'total_passive': 0,
                'passive_verbs': [],
                'required_count': exact_count,
                'passed': False
            }
    
    if not text.strip():
        return False, "❌ 错误：输入文本为空", {
            'total_passive': 0,
            'passive_verbs': [],
            'required_count': exact_count,
            'passed': False
        }
    
    text_lower = text.lower()
    
    # ============ ⭐ 排除词汇（仅明确的非动词）============
    
    non_passive_di_words = {
        # ========== 外来词（A-D）==========
        'dialog', 'diameter', 'diagnosa', 'diploma', 'dinosaurus',
        'direksi', 'direktur', 'dinas', 'dinasti', 'diskon',
        'diskusi', 'divisi', 'diet', 'diesel', 'dinamis',
        'digital', 'dinamika', 'diagram', 'diare',
        
        # ⭐ 新增：distribution 相关（常见错误）
        'distribusi',      # 分配/分发（名词）
        'distributor',     # 分销商（名词）
        'distrik',         # 区域（名词）
        
        # ========== 其他外来词 ==========
        'dimensi',         # dimension
        'diplomasi',       # diplomacy
        'direktif',        # directive
        'disiplin',        # discipline
        'diversitas',      # diversity
        'dilemma',         # dilemma
        'dikotomi',        # dichotomy
        'divestasi',       # divestment
        'diskriminasi',    # discrimination
        'dispensasi',      # dispensation
        
        # ========== 印尼语原生词（名词、形容词）==========
        'diri',            # 自己
        'dinding',         # 墙
        'dingin',          # 冷
        'diam',            # 安静
    }
    
    # ============ 查找被动动词（仅连写词）============
    
    passive_verbs_list = []
    excluded_words = []
    di_space_phrases = []  # 用于调试：记录 "di + 空格" 的介词短语
    found_positions = set()
    
    # ⭐ 只匹配 di- 连写词（不包括 "di + 空格"）
    di_connected_pattern = r'\bdi([a-z]{2,})\b'
    
    for match in re.finditer(di_connected_pattern, text_lower):
        full_word_lower = match.group(0)  # 完整的词（如 dikembangkan）
        root = match.group(1)              # 词根（如 kembangkan）
        start_pos = match.start()
        end_pos = match.end()
        original_word = text[start_pos:end_pos]  # 保留原始大小写
        
        if start_pos in found_positions:
            continue
        
        # 排除明确的非动词
        if full_word_lower in non_passive_di_words:
            if debug:
                excluded_words.append({
                    'word': original_word,
                    'type': get_word_type_di(full_word_lower),
                    'position': start_pos
                })
            found_positions.add(start_pos)
            continue
        
        # ⭐ 保留为被动语态动词
        passive_verbs_list.append({
            'verb': original_word,
            'verb_lower': full_word_lower,
            'root': root,
            'position': start_pos,
            'context': text[max(0, start_pos-30):min(len(text), end_pos+30)]
        })
        found_positions.add(start_pos)
    
    # ⭐ 检测 "di + 空格 + 词" 的介词短语（仅用于调试，不计入结果）
    if debug:
        di_separated_pattern = r'\bdi\s+([a-z]+)\b'
        for match in re.finditer(di_separated_pattern, text_lower):
            location = match.group(1)
            start_pos = match.start()
            end_pos = match.end()
            original_phrase = text[start_pos:end_pos]
            
            di_space_phrases.append({
                'phrase': original_phrase,
                'word_after_di': location,
                'position': start_pos,
                'reason': '介词短语（不计入被动语态）'
            })
    
    passive_verbs_list.sort(key=lambda x: x['position'])
    
    # ============ 判断结果 ============
    total_count = len(passive_verbs_list)
    passed = (total_count == exact_count)
    
    # ============ 生成详细说明 ============
    detail_parts = []
    
    detail_parts.append("⭐ 检测范围：仅计算 di- 前缀的连写词（如 dikembangkan, dilakukan）")
    detail_parts.append("⭐ 不包括：'di + 空格 + 词' 的介词短语（如 'di Jakarta'）")
    detail_parts.append("⭐ 不包括：外来名词（如 distribusi, dialog）\n")
    
    if passed:
        detail_parts.append(f"✅ 正确：找到正好 {total_count} 个被动语态动词（要求正好 {exact_count} 个）\n")
    else:
        if total_count < exact_count:
            shortage = exact_count - total_count
            detail_parts.append(f"❌ 错误：只找到 {total_count} 个被动语态动词，少于要求的 {exact_count} 个（还差 {shortage} 个）\n")
        else:
            excess = total_count - exact_count
            detail_parts.append(f"❌ 错误：找到 {total_count} 个被动语态动词，超过要求的 {exact_count} 个（多了 {excess} 个）\n")
    
    detail_parts.append(f"📊 检测到的被动语态动词（共 {total_count} 个）：")
    for i, item in enumerate(passive_verbs_list, 1):
        detail_parts.append(f"  {i:2d}. {item['verb']:20s} (词根: {item['root']:15s}, 位置 {item['position']:4d})")
        if debug:
            detail_parts.append(f"      上下文: ...{item['context']}...")
    
    if debug and excluded_words:
        detail_parts.append(f"\n🔍 调试信息 - 被排除的 di- 词（共 {len(excluded_words)} 个）：")
        for i, item in enumerate(excluded_words, 1):
            detail_parts.append(f"  {i:2d}. {item['word']:20s} (位置 {item['position']:4d})")
            detail_parts.append(f"      原因: {item['type']}")
    
    if debug and di_space_phrases:
        detail_parts.append(f"\n🔍 调试信息 - 检测到但未计入的 'di + 空格' 短语（共 {len(di_space_phrases)} 个）：")
        for i, item in enumerate(di_space_phrases[:10], 1):  # 最多显示10个
            detail_parts.append(f"  {i:2d}. '{item['phrase']:20s}' (位置 {item['position']:4d})")
            detail_parts.append(f"      原因: {item['reason']}")
    
    detail = '\n'.join(detail_parts)
    
    # ============ 统计数据 ============
    stats = {
        'total_passive': total_count,
        'passive_verbs': [v['verb'] for v in passive_verbs_list],
        'passive_verbs_detailed': [
            {
                'verb': v['verb'],
                'root': v['root'],
                'position': v['position']
            } for v in passive_verbs_list
        ],
        'passive_roots': [v['root'] for v in passive_verbs_list],
        'excluded_count': len(excluded_words),
        'excluded_words': [e['word'] for e in excluded_words] if debug else [],
        'di_space_phrases_count': len(di_space_phrases),
        'di_space_phrases': [p['phrase'] for p in di_space_phrases] if debug else [],
        'required_count': exact_count,
        'difference': total_count - exact_count,
        'passed': passed,
        'check_mode': 'di_prefix_connected_only_fixed'
    }
    
    return passed, detail, stats


def get_word_type_di(word: str) -> str:
    """
    辅助函数：返回 di- 开头词的类型
    
    Args:
        word: 要检查的词
    
    Returns:
        词的类型（中文说明）
    """
    # 外来名词
    foreign_nouns = {
        'distribusi', 'distributor', 'distrik', 'dialog', 'diameter',
        'diagnosa', 'diploma', 'dinosaurus', 'direksi', 'direktur',
        'dinas', 'dinasti', 'diskon', 'diskusi', 'divisi',
        'diet', 'diesel', 'diagram', 'diare', 'dimensi',
        'diplomasi', 'direktif', 'disiplin', 'diversitas', 'dilemma',
        'dikotomi', 'divestasi', 'diskriminasi', 'dispensasi'
    }
    
    # 印尼语原生名词/形容词
    native_words = {
        'diri': '名词（自己）',
        'dinding': '名词（墙）',
        'dingin': '形容词（冷）',
        'diam': '形容词（安静）'
    }
    
    if word in foreign_nouns:
        return f'外来名词（{word}）'
    elif word in native_words:
        return native_words[word]
    else:
        return '非被动动词'


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试文本
    test_text = [
        "Nusantara Tech menggelar acara peluncuran ponsel lipat Garuda X di Jakarta Convention Center pada 15 Januari 2024. Acara ini menarik perhatian banyak penggemar teknologi dan media lokal. Garuda X merupakan ponsel lipat 5G pertama buatan Indonesia, hasil kerja sama teknologi dengan Samsung Korea. Ponsel ini menawarkan desain inovatif dan fitur canggih yang diharapkan dapat bersaing di pasar global. Para pengunjung acara berkesempatan mencoba langsung ponsel tersebut dan mengagumi kualitas layar serta kecepatan koneksi internetnya.",
        "Dalam sambutannya, CEO Nusantara Tech, Budi Santoso, menyampaikan rasa bangga atas pencapaian ini. \"Kami berkomitmen mengembangkan teknologi yang dapat bersaing secara internasional,\" ujar Budi. Kerja sama dengan Samsung memungkinkan Nusantara Tech mengakses teknologi terkini dan meningkatkan kapabilitas produksi. Garuda X dilengkapi dengan prosesor terbaru dan kamera berkualitas tinggi, yang diharapkan dapat memenuhi kebutuhan pengguna yang semakin kompleks. Selain itu, ponsel ini dirancang dengan mempertimbangkan aspek keberlanjutan, menggunakan bahan ramah lingkungan.",
        "Peluncuran Garuda X menandai langkah besar bagi industri teknologi Indonesia. Produk ini diharapkan dapat meningkatkan daya saing Indonesia di pasar teknologi global. Nusantara Tech berencana memperluas distribusi ponsel ini ke berbagai negara, termasuk Asia Tenggara dan Eropa. Dengan harga yang kompetitif, Garuda X diharapkan menarik minat konsumen yang mencari ponsel berkualitas dengan fitur inovatif. Para analis industri memprediksi bahwa ponsel ini akan menjadi salah satu produk unggulan Nusantara Tech dan memperkuat posisi Indonesia sebagai pemain penting dalam industri teknologi dunia."
    ]
    
    print("=" * 100)
    print("印尼语被动语态检测 - 仅 di- 词头连写词版测试（已修正）")
    print("=" * 100)
    
    # 测试：统计文本中的被动动词
    print("\n【测试：统计文本中的 di- 被动语态动词数量】")
    passed, detail, stats = check_passive_voice(test_text, exact_count=999, debug=True)
    print(detail)
    print(f"\n💡 结果：文本中实际包含 {stats['total_passive']} 个 di- 被动语态动词")
    
    if stats['excluded_count'] > 0:
        print(f"💡 补充：排除了 {stats['excluded_count']} 个非动词（外来词等）")
    
    if stats['di_space_phrases_count'] > 0:
        print(f"💡 补充：检测到 {stats['di_space_phrases_count']} 个 'di + 空格' 介词短语（未计入结果）")
    
    print("\n" + "=" * 100)
    print("📌 结论：")
    print(f"   - 仅计算 di- 连写词，文本包含 {stats['total_passive']} 个被动语态动词")
    print(f"   - 'distribusi' 等外来名词已被正确排除")
    print(f"   - rule 名称保持为: check_passive_voice:###数量2###")
    print("=" * 100)



# ==================== 印尼语口语化表达检测（精确数量版 - 完全增强版 v4） ====================

import re
from typing import Tuple, Dict
from collections import Counter

def check_exact_colloquial_count(text: str, exact_count: int, debug: bool = False) -> Tuple[bool, str, Dict]:
    """
    检测印尼语口语化表达数量（完全增强版 v4）
    
    严格模式：必须正好等于 exact_count，不能多也不能少
    
    Args:
        text: 要检测的文本
        exact_count: 要求的精确口语化表达数量
        debug: 是否输出调试信息
    
    Returns:
        (是否通过, 详细说明, 统计数据)
    """
    
    # ============ 类型检查和转换 ============
    if text is None:
        return False, "❌ 错误：输入文本为空（None）", {
            'total_count': 0,
            'required_count': exact_count,
            'passed': False,
            'colloquial_words': [],
            'word_counts': {}
        }
    
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                for key in ['text', 'content', 'message', 'response']:
                    if key in item and isinstance(item[key], str):
                        text_parts.append(item[key])
                        break
            else:
                text_parts.append(str(item))
        text = ' '.join(text_parts)
    
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return False, f"❌ 错误：无法转换为字符串", {
                'total_count': 0,
                'required_count': exact_count,
                'passed': False,
                'colloquial_words': [],
                'word_counts': {}
            }
    
    if not text.strip():
        return False, "❌ 错误：输入文本为空", {
            'total_count': 0,
            'required_count': exact_count,
            'passed': False,
            'colloquial_words': [],
            'word_counts': {}
        }
    
    # ============ 口语化表达词库 ============
    
    COLLOQUIAL_EXPRESSIONS = {
        # 口语人称代词
        'gue': '我（口语，标准语: saya）',
        'gua': '我（口语，标准语: saya）',
        'gw': '我（口语，标准语: saya）',
        'ane': '我（口语，标准语: saya）',
        'lo': '你（口语，标准语: kamu/Anda）',
        'lu': '你（口语，标准语: kamu/Anda）',
        'loe': '你（口语，标准语: kamu/Anda）',
        'elu': '你（口语，标准语: kamu/Anda）',
        
        # 口语否定词
        'nggak': '不（口语，标准语: tidak）',
        'gak': '不（口语，标准语: tidak）',
        'engga': '不（口语，标准语: tidak）',
        'ngga': '不（口语，标准语: tidak）',
        'ga': '不（口语，标准语: tidak）',
        'enggak': '不（口语，标准语: tidak）',
        
        # 口语时间/状态副词
        'udah': '已经（口语，标准语: sudah）',
        'dah': '已经（口语，标准语: sudah）',
        'udh': '已经（口语，标准语: sudah）',
        'abis': '之后（口语，标准语: setelah/habis）',
        'ntar': '等会（口语，标准语: nanti）',
        'nti': '等会（口语，标准语: nanti）',
        'bakal': '将要（口语，标准语: akan）',
        
        # 口语动词（省略前缀）
        'tau': '知道（口语，标准语: tahu）',
        'ketemu': '遇见（口语，标准语: bertemu）',
        'kenal': '认识（口语，标准语: mengenal）',
        'kasih': '给（口语，标准语: beri/berikan）',
        'buat': '为了/做（口语，标准语: untuk/membuat）',
        'nyesel': '后悔（口语，标准语: menyesal）',
        'pengen': '想要（口语，标准语: ingin）',
        
        # 口语化动词（ng- 前缀）
        'ngomong': '说话（口语，标准语: berbicara/mengatakan）',
        'ngomongin': '谈论（口语，标准语: membicarakan）',
        'ngasih': '给（口语，标准语: memberi）',
        'ngasihin': '给予（口语，标准语: memberikan）',
        'ngeliat': '看（口语，标准语: melihat）',
        'ngelakuin': '做（口语，标准语: melakukan）',
        'ngelupain': '忘记（口语，标准语: melupakan）',
        'ngerasa': '感觉（口语，标准语: merasa）',
        'ngerti': '懂（口语，标准语: mengerti）',
        'ngulangin': '重复（口语，标准语: mengulangi）',
        'ngobrol': '聊天（口语，标准语: berbicara/mengobrol）',
        'ngobrolin': '聊关于（口语，标准语: membicarakan）',
        
        # 口语化动词后缀 -in
        'bikin': '做/使（口语，标准语: membuat）',
        'bikinin': '做给（口语，标准语: membuatkan）',
        'maafin': '原谅（口语，标准语: memaafkan）',
        'benerin': '修复（口语，标准语: membetulkan/memperbaiki）',
        'tungguin': '等待（口语，标准语: menunggu）',
        'dengerin': '听（口语，标准语: mendengarkan）',
        'bantuin': '帮助（口语，标准语: membantu）',
        'ikutin': '跟随（口语，标准语: mengikuti）',
        'ajakin': '邀请（口语，标准语: mengajak）',
        'tanyain': '询问（口语，标准语: menanyakan）',
        
        # 口语程度副词
        'banget': '非常（口语，标准语: sangat/sekali）',
        'bgt': '非常（口语缩写，标准语: sangat）',
        'bngt': '非常（口语缩写，标准语: sangat）',
        'bener': '真的（口语，标准语: benar）',
        'bnr': '真的（口语缩写，标准语: benar）',
        
        # 口语连词/助词
        'emang': '确实（口语，标准语: memang）',
        'emg': '确实（口语缩写，标准语: memang）',
        'sih': '呢/啊（口语语气助词）',
        'deh': '吧（口语语气助词）',
        'dong': '嘛（口语语气助词）',
        'kok': '怎么（口语疑问词）',
        'dunk': '嘛（口语，标准语: dong）',
        'ya': '好吗/吧（口语语气助词）',
        'yah': '啊（口语叹词）',
        'kan': '不是吗（口语助词，标准语: bukan）',
        'sumpah': '发誓（口语强调词）',
        
        # 口语疑问词
        'gimana': '怎么样（口语，标准语: bagaimana）',
        'gmn': '怎么样（口语缩写，标准语: bagaimana）',
        'kenapa': '为什么（口语，标准语: mengapa）',
        'knp': '为什么（口语缩写）',
        'kayak': '像（口语，标准语: seperti）',
        'kaya': '像（口语，标准语: seperti）',
        
        # 其他常见口语词
        'aja': '就/只（口语，标准语: saja）',
        'aj': '就/只（口语缩写，标准语: saja）',
        'nih': '这（口语，标准语: ini）',
        'tuh': '那（口语，标准语: itu）',
        'gitu': '那样（口语，标准语: begitu）',
        'gini': '这样（口语，标准语: begini）',
        'cuma': '只（口语，标准语: hanya）',
        'doang': '只（口语）',
        'ama': '和（口语，标准语: dengan）',
        'ma': '和（口语缩写）',
        'sama': '和（口语，标准语: dengan）',
        
        # 俚语和感叹词
        'bete': '烦躁（口语/俚语）',
        'kesel': '烦恼/生气（俚语）',
        'dodol': '笨蛋（口语/俚语）',
        'beres': '搞定（口语，标准语: selesai）',
        'kacau': '糟糕（口语）',
        'gara-gara': '因为（口语，标准语: karena）',
        'soalnya': '因为（口语，标准语: karena）',
        'makanya': '所以（口语，标准语: oleh karena itu）',
        'kelewat': '过分/错过（口语，标准语: terlalu/melewatkan）',
        
        # 口语邀请/呼唤词
        'yuk': '来吧（口语邀请词）',
        'yo': '嘿（英语外来口语打招呼）',
        'ayo': '来吧（口语邀请词）',
        'hei': '嘿（口语打招呼）',
        'hai': '嗨（口语打招呼）',
        
        # 口语缩写
        'gt': '那样（口语缩写，标准语: begitu）',
        'bc': '因为（口语缩写，标准语: karena）',
        'yg': '的（书面缩写，但常用于口语，标准语: yang）',
        'dgn': '和（书面缩写，但常用于口语，标准语: dengan）',
        
        # 网络/年轻人口语
        'asik': '好玩（口语，标准语: asyik）',
        'mantap': '很棒（口语）',
        'mantep': '很棒（口语）',
        'keren': '酷（口语）',
        'oke': '好（口语，标准语: baik）',
        'ok': '好（口语缩写）',
        
        # 英语外来口语
        'please': '拜托（英语外来口语）',
        'happy': '开心（英语外来口语）',
        'love': '爱（英语外来口语）',
        'sorry': '抱歉（英语外来口语）',
        'thanks': '谢谢（英语外来口语）',
        'cool': '酷（英语外来口语）',
        'wow': '哇（英语外来口语）',
        'yeah': '耶（英语外来口语）',
        'yup': '是的（英语外来口语）',
        'bye': '再见（英语外来口语）',
        
        # 其他常用口语
        'traktir': '请客（口语）',
        'siapin': '准备（口语，标准语: menyiapkan）',
        'jadian': '成为情侣（口语）',
        'galau': '迷茫/纠结（口语）',
        'lebay': '夸张（口语）',
    }
    
    # ============ 固定礼貌用语/正式短语（需要排除的） ============
    
    FORMAL_PHRASES = {
        ('terima', 'kasih'): ['kasih'],
        ('sama', 'sama'): ['sama'],
        ('selamat', 'pagi'): [],
        ('selamat', 'siang'): [],
        ('selamat', 'malam'): [],
        ('mohon', 'maaf'): [],
        ('dengan', 'hormat'): [],
    }
    
    # ============ 查找口语化表达 ============
    
    text_lower = text.lower()
    found_colloquial = []
    found_positions = set()
    excluded_positions = set()
    
    # 第一步：标记所有固定礼貌用语中需要排除的词
    for (word1, word2), exclude_words in FORMAL_PHRASES.items():
        phrase_pattern = r'\b' + re.escape(word1) + r'[\s\-]*' + re.escape(word2) + r'\b'
        phrase_matches = re.finditer(phrase_pattern, text_lower, re.IGNORECASE)
        
        for phrase_match in phrase_matches:
            phrase_start = phrase_match.start()
            phrase_end = phrase_match.end()
            
            for exclude_word in exclude_words:
                word_pattern = r'\b' + re.escape(exclude_word) + r'\b'
                word_matches = re.finditer(word_pattern, text_lower[phrase_start:phrase_end])
                
                for word_match in word_matches:
                    actual_pos = phrase_start + word_match.start()
                    excluded_positions.add(actual_pos)
    
    # 第二步：查找所有口语化表达
    for colloquial_word, description in COLLOQUIAL_EXPRESSIONS.items():
        pattern = r'\b' + re.escape(colloquial_word) + r'\b'
        matches = re.finditer(pattern, text_lower)
        
        for match in matches:
            start_pos = match.start()
            end_pos = match.end()
            
            if start_pos in excluded_positions:
                continue
            
            if start_pos in found_positions:
                continue
            
            # 特殊上下文检查：kasih
            if colloquial_word == 'kasih':
                context_before = text_lower[max(0, start_pos-10):start_pos].strip()
                if context_before.endswith('terima'):
                    continue
            
            # 特殊上下文检查：sama
            if colloquial_word == 'sama':
                context_before = text_lower[max(0, start_pos-7):start_pos].strip()
                context_after = text_lower[end_pos:end_pos+7].strip()
                
                if context_before.endswith('sama') or context_after.startswith('sama'):
                    broader_context = text_lower[max(0, start_pos-50):min(len(text), end_pos+50)]
                    if any(formal_word in broader_context for formal_word in ['hormat', 'yth', 'dengan segala']):
                        continue
            
            original_word = text[start_pos:end_pos]
            
            found_colloquial.append({
                'word': original_word,
                'word_lower': colloquial_word,
                'description': description,
                'position': start_pos,
                'context': text[max(0, start_pos-30):min(len(text), end_pos+30)],
                'category': _categorize_colloquial(colloquial_word, description)
            })
            
            found_positions.add(start_pos)
    
    found_colloquial.sort(key=lambda x: x['position'])
    
    # ============ 统计 ============
    
    total_count = len(found_colloquial)
    word_counter = Counter([item['word_lower'] for item in found_colloquial])
    category_counter = Counter([item['category'] for item in found_colloquial])
    
    # ============ 判断是否通过 ============
    
    passed = (total_count == exact_count)
    
    # ============ 生成详细说明 ============
    
    detail_parts = []
    
    if passed:
        detail_parts.append(f"✅ 正确：找到正好 {total_count} 个口语化表达（要求正好 {exact_count} 个）\n")
        
        detail_parts.append("找到的口语化表达：")
        for i, item in enumerate(found_colloquial, 1):
            detail_parts.append(f"  {i}. {item['word']} - {item['description']} (位置 {item['position']})")
        
        if len(word_counter) < total_count:
            detail_parts.append(f"\n词频统计：")
            for word, count in word_counter.most_common(10):
                if count > 1:
                    detail_parts.append(f"  - {word}: {count}次")
    
    else:
        if total_count < exact_count:
            shortage = exact_count - total_count
            detail_parts.append(f"❌ 错误：只找到 {total_count} 个口语化表达，少于要求的 {exact_count} 个（还差 {shortage} 个）\n")
        else:
            excess = total_count - exact_count
            detail_parts.append(f"❌ 错误：找到 {total_count} 个口语化表达，超过要求的 {exact_count} 个（多了 {excess} 个）\n")
        
        if found_colloquial:
            detail_parts.append("已找到的口语化表达：")
            for i, item in enumerate(found_colloquial, 1):
                detail_parts.append(f"  {i}. {item['word']} - {item['description']} (位置 {item['position']})")
            
            if len(word_counter) < total_count:
                detail_parts.append(f"\n词频统计：")
                for word, count in word_counter.most_common(10):
                    if count > 1:
                        detail_parts.append(f"  - {word}: {count}次")
    
    detail = '\n'.join(detail_parts)
    
    # ============ 统计数据 ============
    
    stats = {
        'total_count': total_count,
        'required_count': exact_count,
        'difference': total_count - exact_count,
        'passed': passed,
        'colloquial_words': [item['word'] for item in found_colloquial],
        'word_counts': dict(word_counter),
        'category_counts': dict(category_counter),
        'unique_count': len(word_counter),
        'all_found': found_colloquial,
        'excluded_count': len(excluded_positions),
        'check_mode': 'exact_match_enhanced_v4'
    }
    
    return passed, detail, stats


def _categorize_colloquial(word: str, description: str) -> str:
    """将口语化表达分类"""
    if '人称' in description or word in ['gue', 'gua', 'gw', 'lo', 'lu', 'loe']:
        return '口语人称'
    elif '否定' in description or word in ['gak', 'nggak', 'ga', 'ngga']:
        return '口语否定'
    elif '动词' in description or word.startswith('ng') or word.endswith('in') or word in ['bikin', 'kasih', 'buat', 'nyesel', 'pengen']:
        return '口语动词'
    elif '程度' in description or word in ['banget', 'bener']:
        return '程度副词'
    elif '助词' in description or word in ['sih', 'deh', 'dong', 'kok', 'ya', 'yah']:
        return '语气助词'
    elif '时间' in description or word in ['udah', 'ntar', 'bakal']:
        return '时间副词'
    elif '俚语' in description or word in ['bete', 'dodol', 'kacau', 'kesel']:
        return '俚语'
    elif '英语' in description:
        return '英语外来口语'
    elif '邀请' in description or word in ['yuk', 'ayo']:
        return '邀请词'
    else:
        return '其他口语'


# ==================== 印尼语敬语表达检测（精确数量版 - 修订版 v3） ====================
def check_formal_honorifics(text: str, exact_count: int = 5) -> Tuple[bool, str, Dict]:
    """
    检测印尼语敬语表达（bahasa hormat）- 修订版 v3
    严格模式：必须正好等于 exact_count，不能多也不能少
    Args:
        text: 要检测的文本
        exact_count: 要求的精确敬语表达数量
    Returns:
        (是否通过, 详细说明, 统计数据)
    """
    # ============ 类型检查和转换 ============
    if text is None:
        return False, "❌ 错误：输入文本为空（None）", {
            'total_count': 0,
            'required_count': exact_count,
            'passed': False,
            'honorific_words': [],
            'word_counts': {},
            'by_category': {}
        }
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                for key in ['text', 'content', 'message', 'response']:
                    if key in item and isinstance(item[key], str):
                        text_parts.append(item[key])
                        break
            else:
                text_parts.append(str(item))
        text = ' '.join(text_parts)
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return False, f"❌ 错误：无法转换为字符串", {
                'total_count': 0,
                'required_count': exact_count,
                'passed': False,
                'honorific_words': [],
                'word_counts': {},
                'by_category': {}
            }
    if not text.strip():
        return False, "❌ 错误：输入文本为空", {
            'total_count': 0,
            'required_count': exact_count,
            'passed': False,
            'honorific_words': [],
            'word_counts': {},
            'by_category': {}
        }
    # ============ 敬语词库 ============
    # 优先级1：敬语短语（必须整体匹配）
    HONORIFIC_PHRASES = {
        'minta maaf': {'category': '礼貌短语', 'meaning': '道歉'},
        'terima kasih': {'category': '礼貌短语', 'meaning': '感谢'},
        'permohonan maaf': {'category': '礼貌短语', 'meaning': '请求原谅'},
        'permintaan maaf': {'category': '礼貌短语', 'meaning': '请求原谅'},
        'yang terhormat': {'category': '敬称短语', 'meaning': '尊敬的'},
        'yang tercinta': {'category': '敬称短语', 'meaning': '挚爱的'},
        'hormat saya': {'category': '礼貌短语', 'meaning': '我的敬意'},
        'dengan hormat': {'category': '礼貌短语', 'meaning': '敬上'},
        'mohon memaafkan': {'category': '礼貌短语', 'meaning': '请原谅'},
        'memaafkan kesalahan': {'category': '礼貌短语', 'meaning': '原谅错误'},
        'sang penyanyi': {'category': '敬称短语', 'meaning': '敬语标记词（尊敬的歌手）'},
    }
    # 优先级2：敬语单词
    HONORIFIC_WORDS = {
        # 敬称人称代词
        'anda': {'category': '敬称人称代词', 'meaning': '您'},
        'saudara': {'category': '敬称人称代词', 'meaning': '您（同辈）'},
        'beliau': {'category': '敬称人称代词', 'meaning': '他/她（尊称）'},
        # 敬称呼词和缩写
        'bapak': {'category': '敬称呼词', 'meaning': '先生'},
        'ibu': {'category': '敬称呼词', 'meaning': '女士/太太'},
        'sang': {'category': '敬称呼词', 'meaning': '敬语标记词（用于尊敬地指代某人）'},
        'yth': {'category': '敬称呼词', 'meaning': '尊敬的（缩写）'},
        # 礼貌助词
        'silakan': {'category': '礼貌助词', 'meaning': '请'},
        'mohon': {'category': '礼貌助词', 'meaning': '恳请'},
        'tolong': {'category': '通用礼貌词', 'meaning': '请（帮忙）'},
        'sudilah': {'category': '礼貌助词', 'meaning': '请（文雅）'},
        'kiranya': {'category': '礼貌助词', 'meaning': '希望（正式）'},
        # 正式敬语词汇
        'hormat': {'category': '正式敬语', 'meaning': '敬意'},
        'terhormat': {'category': '正式敬语', 'meaning': '尊敬的'},
        'berkenan': {'category': '正式敬语', 'meaning': '愿意（敬语）'},
        'salam': {'category': '正式敬语', 'meaning': '敬礼/问候'},
    }
    # ============ 查找敬语表达 ============
    text_lower = text.lower()
    found_honorifics = []
    category_counts = {}
    phrase_positions = []
    # 第一步：先匹配短语（使用灵活的空白符匹配）
    for phrase, info in HONORIFIC_PHRASES.items():
        # 对于多词短语，允许词之间有多个空格或换行符
        if ' ' in phrase:
            # 将短语中的空格替换为灵活的空白符匹配
            flexible_phrase = re.escape(phrase)
            flexible_phrase = flexible_phrase.replace(r'\ ', r'\s+')
            pattern = r'\b' + flexible_phrase + r'\b'
        else:
            pattern = r'\b' + re.escape(phrase) + r'\b'
        
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            start_pos = match.start()
            end_pos = match.end()
            original_phrase = text[start_pos:end_pos]
            found_honorifics.append({
                'word': original_phrase,
                'word_lower': phrase,
                'category': info['category'],
                'meaning': info['meaning'],
                'position': start_pos,
                'is_phrase': True
            })
            category = info['category']
            category_counts[category] = category_counts.get(category, 0) + 1
            phrase_positions.append((start_pos, end_pos))
    # 第二步：再匹配单词（排除已匹配短语的位置）
    for word, info in HONORIFIC_WORDS.items():
        pattern = r'\b' + re.escape(word) + r'\b'
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            start_pos = match.start()
            end_pos = match.end()
            # 检查是否在短语内
            in_phrase = any(p_start <= start_pos < p_end 
                          for p_start, p_end in phrase_positions)
            if not in_phrase:
                original_word = text[start_pos:end_pos]
                found_honorifics.append({
                    'word': original_word,
                    'word_lower': word,
                    'category': info['category'],
                    'meaning': info['meaning'],
                    'position': start_pos,
                    'is_phrase': False
                })
                category = info['category']
                category_counts[category] = category_counts.get(category, 0) + 1
    # 按位置排序
    found_honorifics.sort(key=lambda x: x['position'])
    # ============ 统计 ============
    total_count = len(found_honorifics)
    word_counter = Counter([item['word_lower'] for item in found_honorifics])
    # ============ 判断是否通过 ============
    passed = (total_count == exact_count)
    # ============ 生成详细说明 ============
    detail_parts = []
    if passed:
        detail_parts.append(f"✅ 正确：找到正好 {total_count} 个敬语表达（要求正好 {exact_count} 个）\n")
        detail_parts.append("找到的敬语表达：")
        for i, item in enumerate(found_honorifics, 1):
            detail_parts.append(f"  {i}. {item['word']} - 【{item['category']}】{item['meaning']} (位置 {item['position']})")
        if category_counts:
            detail_parts.append(f"\n按类别统计：")
            for category, count in category_counts.items():
                detail_parts.append(f"  - {category}: {count} 个")
    else:
        if total_count < exact_count:
            shortage = exact_count - total_count
            detail_parts.append(f"❌ 错误：只找到 {total_count} 个敬语表达，少于要求的 {exact_count} 个（还差 {shortage} 个）\n")
        else:
            excess = total_count - exact_count
            detail_parts.append(f"❌ 错误：找到 {total_count} 个敬语表达，超过要求的 {exact_count} 个（多了 {excess} 个）\n")
        if found_honorifics:
            detail_parts.append("已找到的敬语表达：")
            for i, item in enumerate(found_honorifics, 1):
                detail_parts.append(f"  {i}. {item['word']} - 【{item['category']}】{item['meaning']} (位置 {item['position']})")
            if category_counts:
                detail_parts.append(f"\n按类别统计：")
                for category, count in category_counts.items():
                    detail_parts.append(f"  - {category}: {count} 个")
        detail_parts.append("\n\n⚠️ 注意：")
        detail_parts.append("  - memaafkan 单独出现不算敬语，需在短语中（如：mohon memaafkan）")
        detail_parts.append("  - hormat 单独出现算敬语，常见短语：hormat saya, dengan hormat")
        detail_parts.append("  - sang 是敬语标记词，用于尊敬地指代某人（如：sang penyanyi）")
    detail = '\n'.join(detail_parts)
    # ============ 统计数据 ============
    stats = {
        'total_count': total_count,
        'required_count': exact_count,
        'difference': total_count - exact_count,
        'passed': passed,
        'honorific_words': [item['word'] for item in found_honorifics],
        'word_counts': dict(word_counter),
        'by_category': category_counts,
        'unique_count': len(word_counter),
        'all_found': found_honorifics,
        'check_mode': 'exact_match_v3_flexible'
    }
    return passed, detail, stats
# ==================== 测试示例 ====================
if __name__ == "__main__":
    # 测试文本
    test_text = """
    Selamat malam, hadirin yang terhormat. Dengan penuh rasa syukur dan kebahagiaan,
    saya menyambut Anda semua di acara tahunan perusahaan kita yang ke-10. Malam ini
    adalah malam yang istimewa, di mana kita berkumpul untuk merayakan pencapaian dan
    kebersamaan kita selama setahun terakhir.
    Pertama-tama, izinkan saya mengucapkan terima kasih yang sebesar-besarnya kepada
    seluruh tamu undangan yang telah meluangkan waktu untuk hadir di sini. Kehadiran
    Anda semua adalah kehormatan besar bagi kami. Terlebih lagi, kami merasa sangat
    beruntung karena malam ini kita akan ditemani oleh beberapa bintang penyanyi
    terkenal yang akan menghibur kita dengan suara merdu mereka.
    Si acara tahunan ini adalah momen yang kita nantikan setiap tahun, di mana kita
    dapat berkumpul, berbagi cerita, dan mempererat hubungan. Sang penyanyi yang akan
    tampil malam ini adalah sosok yang telah menginspirasi banyak orang dengan
    karya-karya mereka. Kami berharap penampilan mereka akan memberikan kenangan
    indah bagi kita semua.
    Sebelum kita memulai rangkaian acara, saya ingin mengajak Anda semua untuk
    menikmati malam ini dengan penuh sukacita. Mohon untuk menjaga ketertiban dan
    kenyamanan selama acara berlangsung. Kami juga memohon kesediaan Anda untuk
    memberikan apresiasi yang hangat kepada para penampil kita malam ini.
    Sekali lagi, terima kasih atas kehadiran Anda. Semoga malam ini menjadi malam
    yang penuh kebahagiaan dan kenangan indah bagi kita semua. Selamat menikmati acara!
    """

# ==================== 印尼语口语化表达检测（精确数量版 - 完全增强版 v4） ====================

import re
from typing import Tuple, Dict
from collections import Counter

def check_exact_colloquial_count(text: str, exact_count: int, debug: bool = False) -> Tuple[bool, str, Dict]:
    """
    检测印尼语口语化表达数量（完全增强版 v4）
    
    严格模式：必须正好等于 exact_count，不能多也不能少
    
    Args:
        text: 要检测的文本
        exact_count: 要求的精确口语化表达数量
        debug: 是否输出调试信息
    
    Returns:
        (是否通过, 详细说明, 统计数据)
    """
    
    # ============ 类型检查和转换 ============
    if text is None:
        return False, "❌ 错误：输入文本为空（None）", {
            'total_count': 0,
            'required_count': exact_count,
            'passed': False,
            'colloquial_words': [],
            'word_counts': {}
        }
    
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                for key in ['text', 'content', 'message', 'response']:
                    if key in item and isinstance(item[key], str):
                        text_parts.append(item[key])
                        break
            else:
                text_parts.append(str(item))
        text = ' '.join(text_parts)
    
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return False, f"❌ 错误：无法转换为字符串", {
                'total_count': 0,
                'required_count': exact_count,
                'passed': False,
                'colloquial_words': [],
                'word_counts': {}
            }
    
    if not text.strip():
        return False, "❌ 错误：输入文本为空", {
            'total_count': 0,
            'required_count': exact_count,
            'passed': False,
            'colloquial_words': [],
            'word_counts': {}
        }
    
    # ============ 口语化表达词库 ============
    
    COLLOQUIAL_EXPRESSIONS = {
        # 口语人称代词
        'gue': '我（口语，标准语: saya）',
        'gua': '我（口语，标准语: saya）',
        'gw': '我（口语，标准语: saya）',
        'ane': '我（口语，标准语: saya）',
        'lo': '你（口语，标准语: kamu/Anda）',
        'lu': '你（口语，标准语: kamu/Anda）',
        'loe': '你（口语，标准语: kamu/Anda）',
        'elu': '你（口语，标准语: kamu/Anda）',
        
        # 口语否定词
        'nggak': '不（口语，标准语: tidak）',
        'gak': '不（口语，标准语: tidak）',
        'engga': '不（口语，标准语: tidak）',
        'ngga': '不（口语，标准语: tidak）',
        'ga': '不（口语，标准语: tidak）',
        'enggak': '不（口语，标准语: tidak）',
        
        # 口语时间/状态副词
        'udah': '已经（口语，标准语: sudah）',
        'dah': '已经（口语，标准语: sudah）',
        'udh': '已经（口语，标准语: sudah）',
        'abis': '之后（口语，标准语: setelah/habis）',
        'ntar': '等会（口语，标准语: nanti）',
        'nti': '等会（口语，标准语: nanti）',
        'bakal': '将要（口语，标准语: akan）',
        
        # 口语动词（省略前缀）
        'tau': '知道（口语，标准语: tahu）',
        'ketemu': '遇见（口语，标准语: bertemu）',
        'kenal': '认识（口语，标准语: mengenal）',
        'kasih': '给（口语，标准语: beri/berikan）',
        'buat': '为了/做（口语，标准语: untuk/membuat）',
        'nyesel': '后悔（口语，标准语: menyesal）',
        'pengen': '想要（口语，标准语: ingin）',
        
        # 口语化动词（ng- 前缀）
        'ngomong': '说话（口语，标准语: berbicara/mengatakan）',
        'ngomongin': '谈论（口语，标准语: membicarakan）',
        'ngasih': '给（口语，标准语: memberi）',
        'ngasihin': '给予（口语，标准语: memberikan）',
        'ngeliat': '看（口语，标准语: melihat）',
        'ngelakuin': '做（口语，标准语: melakukan）',
        'ngelupain': '忘记（口语，标准语: melupakan）',
        'ngerasa': '感觉（口语，标准语: merasa）',
        'ngerti': '懂（口语，标准语: mengerti）',
        'ngulangin': '重复（口语，标准语: mengulangi）',
        'ngobrol': '聊天（口语，标准语: berbicara/mengobrol）',
        'ngobrolin': '聊关于（口语，标准语: membicarakan）',
        
        # 口语化动词后缀 -in
        'bikin': '做/使（口语，标准语: membuat）',
        'bikinin': '做给（口语，标准语: membuatkan）',
        'maafin': '原谅（口语，标准语: memaafkan）',
        'benerin': '修复（口语，标准语: membetulkan/memperbaiki）',
        'tungguin': '等待（口语，标准语: menunggu）',
        'dengerin': '听（口语，标准语: mendengarkan）',
        'bantuin': '帮助（口语，标准语: membantu）',
        'ikutin': '跟随（口语，标准语: mengikuti）',
        'ajakin': '邀请（口语，标准语: mengajak）',
        'tanyain': '询问（口语，标准语: menanyakan）',
        
        # 口语程度副词
        'banget': '非常（口语，标准语: sangat/sekali）',
        'bgt': '非常（口语缩写，标准语: sangat）',
        'bngt': '非常（口语缩写，标准语: sangat）',
        'bener': '真的（口语，标准语: benar）',
        'bnr': '真的（口语缩写，标准语: benar）',
        
        # 口语连词/助词
        'emang': '确实（口语，标准语: memang）',
        'emg': '确实（口语缩写，标准语: memang）',
        'sih': '呢/啊（口语语气助词）',
        'deh': '吧（口语语气助词）',
        'dong': '嘛（口语语气助词）',
        'kok': '怎么（口语疑问词）',
        'dunk': '嘛（口语，标准语: dong）',
        'ya': '好吗/吧（口语语气助词）',
        'yah': '啊（口语叹词）',
        'kan': '不是吗（口语助词，标准语: bukan）',
        'sumpah': '发誓（口语强调词）',
        
        # 口语疑问词
        'gimana': '怎么样（口语，标准语: bagaimana）',
        'gmn': '怎么样（口语缩写，标准语: bagaimana）',
        'kenapa': '为什么（口语，标准语: mengapa）',
        'knp': '为什么（口语缩写）',
        'kayak': '像（口语，标准语: seperti）',
        'kaya': '像（口语，标准语: seperti）',
        
        # 其他常见口语词
        'aja': '就/只（口语，标准语: saja）',
        'aj': '就/只（口语缩写，标准语: saja）',
        'nih': '这（口语，标准语: ini）',
        'tuh': '那（口语，标准语: itu）',
        'gitu': '那样（口语，标准语: begitu）',
        'gini': '这样（口语，标准语: begini）',
        'cuma': '只（口语，标准语: hanya）',
        'doang': '只（口语）',
        'ama': '和（口语，标准语: dengan）',
        'ma': '和（口语缩写）',
        'sama': '和（口语，标准语: dengan）',
        
        # 俚语和感叹词
        'bete': '烦躁（口语/俚语）',
        'kesel': '烦恼/生气（俚语）',
        'dodol': '笨蛋（口语/俚语）',
        'beres': '搞定（口语，标准语: selesai）',
        'kacau': '糟糕（口语）',
        'gara-gara': '因为（口语，标准语: karena）',
        'soalnya': '因为（口语，标准语: karena）',
        'makanya': '所以（口语，标准语: oleh karena itu）',
        'kelewat': '过分/错过（口语，标准语: terlalu/melewatkan）',
        
        # 口语邀请/呼唤词
        'yuk': '来吧（口语邀请词）',
        'yo': '嘿（英语外来口语打招呼）',
        'ayo': '来吧（口语邀请词）',
        'hei': '嘿（口语打招呼）',
        'hai': '嗨（口语打招呼）',
        
        # 口语缩写
        'gt': '那样（口语缩写，标准语: begitu）',
        'bc': '因为（口语缩写，标准语: karena）',
        'yg': '的（书面缩写，但常用于口语，标准语: yang）',
        'dgn': '和（书面缩写，但常用于口语，标准语: dengan）',
        
        # 网络/年轻人口语
        'asik': '好玩（口语，标准语: asyik）',
        'mantap': '很棒（口语）',
        'mantep': '很棒（口语）',
        'keren': '酷（口语）',
        'oke': '好（口语，标准语: baik）',
        'ok': '好（口语缩写）',
        
        # 英语外来口语
        'please': '拜托（英语外来口语）',
        'happy': '开心（英语外来口语）',
        'love': '爱（英语外来口语）',
        'sorry': '抱歉（英语外来口语）',
        'thanks': '谢谢（英语外来口语）',
        'cool': '酷（英语外来口语）',
        'wow': '哇（英语外来口语）',
        'yeah': '耶（英语外来口语）',
        'yup': '是的（英语外来口语）',
        'bye': '再见（英语外来口语）',
        
        # 其他常用口语
        'traktir': '请客（口语）',
        'siapin': '准备（口语，标准语: menyiapkan）',
        'jadian': '成为情侣（口语）',
        'galau': '迷茫/纠结（口语）',
        'lebay': '夸张（口语）',
    }
    
    # ============ 固定礼貌用语/正式短语（需要排除的） ============
    
    FORMAL_PHRASES = {
        ('terima', 'kasih'): ['kasih'],
        ('sama', 'sama'): ['sama'],
        ('selamat', 'pagi'): [],
        ('selamat', 'siang'): [],
        ('selamat', 'malam'): [],
        ('mohon', 'maaf'): [],
        ('dengan', 'hormat'): [],
        ('dengan', 'segala', 'kerendahan', 'hati'): [],
        ('atas', 'perhatian', 'dan', 'pengertian', 'anda'): [],  # ⭐ 新增
    }
    
    # ============ 查找口语化表达 ============
    
    text_lower = text.lower()
    found_colloquial = []
    found_positions = set()
    excluded_positions = set()
    
    # 第一步：标记所有固定礼貌用语中需要排除的词
    for phrase_tuple, exclude_words in FORMAL_PHRASES.items():
        # 构建正则表达式：处理多词短语
        if len(phrase_tuple) == 2:
            word1, word2 = phrase_tuple
            phrase_pattern = r'\b' + re.escape(word1) + r'[\s\-]*' + re.escape(word2) + r'\b'
        elif len(phrase_tuple) == 3:
            word1, word2, word3 = phrase_tuple
            phrase_pattern = r'\b' + re.escape(word1) + r'[\s\-]*' + re.escape(word2) + r'[\s\-]*' + re.escape(word3) + r'\b'
        elif len(phrase_tuple) == 4:
            word1, word2, word3, word4 = phrase_tuple
            phrase_pattern = r'\b' + re.escape(word1) + r'[\s\-]*' + re.escape(word2) + r'[\s\-]*' + re.escape(word3) + r'[\s\-]*' + re.escape(word4) + r'\b'
        elif len(phrase_tuple) == 5:
            word1, word2, word3, word4, word5 = phrase_tuple
            phrase_pattern = r'\b' + re.escape(word1) + r'[\s\-]*' + re.escape(word2) + r'[\s\-]*' + re.escape(word3) + r'[\s\-]*' + re.escape(word4) + r'[\s\-]*' + re.escape(word5) + r'\b'
        else:
            continue
        
        phrase_matches = re.finditer(phrase_pattern, text_lower, re.IGNORECASE)
        
        for phrase_match in phrase_matches:
            phrase_start = phrase_match.start()
            phrase_end = phrase_match.end()
            
            for exclude_word in exclude_words:
                word_pattern = r'\b' + re.escape(exclude_word) + r'\b'
                word_matches = re.finditer(word_pattern, text_lower[phrase_start:phrase_end])
                
                for word_match in word_matches:
                    actual_pos = phrase_start + word_match.start()
                    excluded_positions.add(actual_pos)
    
    # 第二步：查找所有口语化表达
    for colloquial_word, description in COLLOQUIAL_EXPRESSIONS.items():
        pattern = r'\b' + re.escape(colloquial_word) + r'\b'
        matches = re.finditer(pattern, text_lower)
        
        for match in matches:
            start_pos = match.start()
            end_pos = match.end()
            
            if start_pos in excluded_positions:
                continue
            
            if start_pos in found_positions:
                continue
            
            # 特殊上下文检查：kasih
            if colloquial_word == 'kasih':
                context_before = text_lower[max(0, start_pos-10):start_pos].strip()
                if context_before.endswith('terima'):
                    continue
            
            # 特殊上下文检查：sama
            if colloquial_word == 'sama':
                context_before = text_lower[max(0, start_pos-7):start_pos].strip()
                context_after = text_lower[end_pos:end_pos+7].strip()
                
                if context_before.endswith('sama') or context_after.startswith('sama'):
                    broader_context = text_lower[max(0, start_pos-50):min(len(text), end_pos+50)]
                    if any(formal_word in broader_context for formal_word in ['hormat', 'yth', 'dengan segala']):
                        continue
            
            original_word = text[start_pos:end_pos]
            
            found_colloquial.append({
                'word': original_word,
                'word_lower': colloquial_word,
                'description': description,
                'position': start_pos,
                'context': text[max(0, start_pos-30):min(len(text), end_pos+30)],
                'category': _categorize_colloquial(colloquial_word, description)
            })
            
            found_positions.add(start_pos)
    
    found_colloquial.sort(key=lambda x: x['position'])
    
    # ============ 统计 ============
    
    total_count = len(found_colloquial)
    word_counter = Counter([item['word_lower'] for item in found_colloquial])
    category_counter = Counter([item['category'] for item in found_colloquial])
    
    # ============ 判断是否通过 ============
    
    passed = (total_count == exact_count)
    
    # ============ 生成详细说明 ============
    
    detail_parts = []
    
    if passed:
        detail_parts.append(f"✅ 正确：找到正好 {total_count} 个口语化表达（要求正好 {exact_count} 个）\n")
        
        detail_parts.append("找到的口语化表达：")
        for i, item in enumerate(found_colloquial, 1):
            detail_parts.append(f"  {i}. {item['word']} - {item['description']} (位置 {item['position']})")
        
        if len(word_counter) < total_count:
            detail_parts.append(f"\n词频统计：")
            for word, count in word_counter.most_common(10):
                if count > 1:
                    detail_parts.append(f"  - {word}: {count}次")
    
    else:
        if total_count < exact_count:
            shortage = exact_count - total_count
            detail_parts.append(f"❌ 错误：只找到 {total_count} 个口语化表达，少于要求的 {exact_count} 个（还差 {shortage} 个）\n")
        else:
            excess = total_count - exact_count
            detail_parts.append(f"❌ 错误：找到 {total_count} 个口语化表达，超过要求的 {exact_count} 个（多了 {excess} 个）\n")
        
        if found_colloquial:
            detail_parts.append("已找到的口语化表达：")
            for i, item in enumerate(found_colloquial, 1):
                detail_parts.append(f"  {i}. {item['word']} - {item['description']} (位置 {item['position']})")
            
            if len(word_counter) < total_count:
                detail_parts.append(f"\n词频统计：")
                for word, count in word_counter.most_common(10):
                    if count > 1:
                        detail_parts.append(f"  - {word}: {count}次")
    
    detail = '\n'.join(detail_parts)
    
    # ============ 统计数据 ============
    
    stats = {
        'total_count': total_count,
        'required_count': exact_count,
        'difference': total_count - exact_count,
        'passed': passed,
        'colloquial_words': [item['word'] for item in found_colloquial],
        'word_counts': dict(word_counter),
        'category_counts': dict(category_counter),
        'unique_count': len(word_counter),
        'all_found': found_colloquial,
        'excluded_count': len(excluded_positions),
        'check_mode': 'exact_match_enhanced_v4'
    }
    
    return passed, detail, stats


def _categorize_colloquial(word: str, description: str) -> str:
    """将口语化表达分类"""
    if '人称' in description or word in ['gue', 'gua', 'gw', 'lo', 'lu', 'loe']:
        return '口语人称'
    elif '否定' in description or word in ['gak', 'nggak', 'ga', 'ngga']:
        return '口语否定'
    elif '动词' in description or word.startswith('ng') or word.endswith('in') or word in ['bikin', 'kasih', 'buat', 'nyesel', 'pengen']:
        return '口语动词'
    elif '程度' in description or word in ['banget', 'bener']:
        return '程度副词'
    elif '助词' in description or word in ['sih', 'deh', 'dong', 'kok', 'ya', 'yah']:
        return '语气助词'
    elif '时间' in description or word in ['udah', 'ntar', 'bakal']:
        return '时间副词'
    elif '俚语' in description or word in ['bete', 'dodol', 'kacau', 'kesel']:
        return '俚语'
    elif '英语' in description:
        return '英语外来口语'
    elif '邀请' in description or word in ['yuk', 'ayo']:
        return '邀请词'
    else:
        return '其他口语'


# ==================== 印尼语包含礼貌词的礼貌祈使句检测（精确数量版 - 修复版）====================

import re
from typing import Tuple, Dict, List
from collections import Counter

def check_polite_imperatives(text: str, exact_count: int = 3) -> Tuple[bool, str, Dict]:
    """
    检测印尼语包含礼貌词的礼貌祈使句
    
    严格定义：必须包含礼貌词（tolong, mohon, silakan等）的祈使句
    严格模式：必须正好等于 exact_count，不能多也不能少
    
    改进：识别用 dan 连接的多个礼貌祈使句（如 "silakan duduk dan mari kita rayakan"）
    
    包含礼貌词的祈使句结构：
    - 礼貌词 + 动词：silakan maafkan (请原谅)
    - 礼貌词 + 动词 + 宾语：mohon beri kesempatan (恳请给机会)
    - 礼貌词 + 动词短语：tolong dengarkan penjelasan ini (请听这个解释)
    
    礼貌词包括：tolong, mohon, silakan, harap, mari, sudilah, semoga, kiranya
    
    Args:
        text: 要检测的文本
        exact_count: 要求的精确数量
    
    Returns:
        (是否通过, 详细说明, 统计数据)
    """
    
    # ============ 类型检查和转换 ============
    if text is None:
        return False, "❌ 错误：输入文本为空（None）", {
            'total_count': 0,
            'required_count': exact_count,
            'passed': False,
            'imperatives': [],
            'by_marker': {}
        }
    
    # 处理列表类型
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                for key in ['text', 'content', 'message', 'response']:
                    if key in item and isinstance(item[key], str):
                        text_parts.append(item[key])
                        break
            else:
                text_parts.append(str(item))
        text = ' '.join(text_parts)
    
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return False, f"❌ 错误：无法转换为字符串", {
                'total_count': 0,
                'required_count': exact_count,
                'passed': False,
                'imperatives': [],
                'by_marker': {}
            }
    
    if not text.strip():
        return False, "❌ 错误：输入文本为空", {
            'total_count': 0,
            'required_count': exact_count,
            'passed': False,
            'imperatives': [],
            'by_marker': {}
        }
    
    # ============ 礼貌词定义 ============
    
    POLITE_WORDS = {
        'tolong': '请（帮忙）',
        'mohon': '恳请',
        'silakan': '请',
        'harap': '希望/请',
        'mari': '让我们',
        'sudilah': '请（正式）',
        'semoga': '希望',
        'kiranya': '希望（正式）',
    }
    
    # ============ 排除模式：不算祈使句的固定短语 ============
    
    EXCLUDED_PHRASES = [
        r'\bsaya\s+mohon\s+maaf\b',      # "saya mohon maaf" = 我道歉（陈述句）
        r'\bkami\s+mohon\s+maaf\b',      # "kami mohon maaf" = 我们道歉
        r'\bkita\s+mohon\s+maaf\b',      # "kita mohon maaf" = 我们道歉
        r'\bdia\s+mohon\s+maaf\b',       # "dia mohon maaf" = 他/她道歉
        r'\bmereka\s+mohon\s+maaf\b',    # "mereka mohon maaf" = 他们道歉
    ]
    
    # ============ 查找包含礼貌词的祈使句 ============
    
    text_lower = text.lower()
    found_imperatives = []
    marker_counts = {word: 0 for word in POLITE_WORDS.keys()}
    
    # 查找所有可能的匹配
    all_matches = []
    
    for polite_word, meaning in POLITE_WORDS.items():
        # 模式：礼貌词 + 后续动词短语（到 dan, 句号, 逗号等为止）
        # 改进：匹配到 dan 之前就停止，避免跨越多个祈使句
        pattern = r'\b' + re.escape(polite_word) + r'\s+([^.!,\n]+?)(?=\s+dan\s+|\.|!|,|\n|$)'
        
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        
        for match in matches:
            start_pos = match.start()
            end_pos = match.end()
            
            full_phrase = text[start_pos:end_pos].strip()
            verb_part = match.group(1).strip()
            
            # 检查是否是排除的固定短语（陈述句）
            is_excluded = False
            for excluded_pattern in EXCLUDED_PHRASES:
                context_start = max(0, start_pos - 20)
                context = text_lower[context_start:end_pos + 20]
                if re.search(excluded_pattern, context):
                    is_excluded = True
                    break
            
            if is_excluded:
                continue
            
            # 检查是否包含有效动词（至少2个字母）
            if len(verb_part) < 2:
                continue
            
            all_matches.append({
                'phrase': full_phrase,
                'full_sentence': full_phrase,  # 这里记录实际的祈使句部分
                'polite_word': polite_word,
                'word_meaning': meaning,
                'verb': verb_part,
                'position': start_pos,
                'end_position': end_pos,
            })
    
    # ============ 去重处理（避免重叠匹配）============
    
    all_matches.sort(key=lambda x: x['position'])
    
    filtered_matches = []
    used_positions = set()
    
    for match in all_matches:
        start = match['position']
        end = match['end_position']
        
        # 检查是否与已有匹配重叠
        is_overlapping = False
        for prev_match in filtered_matches:
            prev_start = prev_match['position']
            prev_end = prev_match['end_position']
            
            # 如果起始位置在之前匹配的范围内，认为是重叠
            if prev_start <= start < prev_end:
                is_overlapping = True
                break
            
            # 如果有任何位置重叠，也认为是重叠
            if start < prev_end and end > prev_start:
                is_overlapping = True
                break
        
        if not is_overlapping:
            filtered_matches.append(match)
            # 标记使用的位置范围
            for pos in range(start, end):
                used_positions.add(pos)
    
    found_imperatives = filtered_matches
    found_imperatives.sort(key=lambda x: x['position'])
    
    # 统计各礼貌词的使用次数
    for item in found_imperatives:
        marker_counts[item['polite_word']] += 1
    
    # ============ 统计 ============
    
    total_count = len(found_imperatives)
    passed = (total_count == exact_count)
    
    # ============ 生成详细说明 ============
    
    detail_parts = []
    
    if passed:
        detail_parts.append(f"✅ 正确：找到正好 {total_count} 个包含礼貌词的祈使句（要求正好 {exact_count} 个）\n")
        
        detail_parts.append("找到的包含礼貌词的祈使句：")
        for i, item in enumerate(found_imperatives, 1):
            detail_parts.append(f"\n  {i}. 礼貌词：【{item['polite_word']}】（{item['word_meaning']}）")
            detail_parts.append(f"     完整句子: {item['full_sentence']}")
        
        # 按礼貌词分类统计
        active_markers = {k: v for k, v in marker_counts.items() if v > 0}
        if active_markers:
            detail_parts.append(f"\n使用的礼貌词统计：")
            for word, count in active_markers.items():
                detail_parts.append(f"  - {word}: {count} 次")
    
    else:
        if total_count < exact_count:
            shortage = exact_count - total_count
            detail_parts.append(f"❌ 错误：只找到 {total_count} 个包含礼貌词的祈使句，少于要求的 {exact_count} 个（还差 {shortage} 个）\n")
        else:
            excess = total_count - exact_count
            detail_parts.append(f"❌ 错误：找到 {total_count} 个包含礼貌词的祈使句，超过要求的 {exact_count} 个（多了 {excess} 个）\n")
        
        if found_imperatives:
            detail_parts.append("已找到的包含礼貌词的祈使句：")
            for i, item in enumerate(found_imperatives, 1):
                detail_parts.append(f"\n  {i}. 礼貌词：【{item['polite_word']}】（{item['word_meaning']}）")
                detail_parts.append(f"     完整句子: {item['full_sentence']}")
        else:
            detail_parts.append("未找到任何包含礼貌词的祈使句")
    
    detail = '\n'.join(detail_parts)
    
    # ============ 统计数据 ============
    
    stats = {
        'total_count': total_count,
        'required_count': exact_count,
        'difference': total_count - exact_count,
        'passed': passed,
        'imperatives': [item['full_sentence'] for item in found_imperatives],
        'by_marker': marker_counts,
        'unique_markers': len([v for v in marker_counts.values() if v > 0]),
        'all_found': found_imperatives,
        'check_mode': 'exact_match'
    }
    
    return passed, detail, stats


# ============ 测试代码 ============
if __name__ == "__main__":
    # 测试包含 dan 连接的多个礼貌祈使句
    test_text = """
    Selamat siang semuanya, terima kasih telah hadir di hari istimewa ini.
    Tolong luangkan waktu untuk saling berkenalan dan menikmati acara ini bersama.
    Mohon jangan ragu untuk berbagi cerita dan kebahagiaan hari ini.
    Silakan menikmati hidangan yang telah disiapkan dan mari kita rayakan hari yang penuh cinta ini.
    Terima kasih!
    """
    
    passed, detail, stats = check_polite_imperatives(test_text, exact_count=4)
    print("=" * 70)
    print("测试结果：")
    print(detail)
    print("=" * 70)
    print(f"\n统计数据:")
    print(f"  - 总数: {stats['total_count']}")
    print(f"  - 要求: {stats['required_count']}")
    print(f"  - 通过: {stats['passed']}")
    print(f"\n找到的祈使句:")
    for i, imp in enumerate(stats['imperatives'], 1):
        print(f"  {i}. {imp}")


    
def check_si_usage(text):
    """
    检查印尼语冠词 'si' 的使用是否正确
    返回: (score, message)
    """
    import re
    
    # 处理输入类型
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    elif not isinstance(text, str):
        text = str(text)
    
    # 查找所有 'si' + 名词的模式
    si_pattern = r'\b[Ss]i\s+([a-zA-Z]+)'
    matches = re.findall(si_pattern, text)
    
    if not matches:
        return 1, "✓ 未使用 'si' 冠词"
    
    # 不应该与 'si' 搭配的词（表示尊贵、神圣的词）
    forbidden_with_si = [
        'raja', 'ratu', 'pangeran', 'putri', 'sultan',  # 王室
        'kaisar', 'maharaja', 'permaisuri',
        'dewa', 'dewi', 'allah', 'tuhan',  # 神灵
        'hakim', 'menteri', 'presiden', 'gubernur',  # 高官
        'wali', 'bupati', 'walikota',
        'profesor', 'doktor', 'guru',  # 学术尊称
    ]
    
    errors = []
    
    # 检查每个匹配
    for match in matches:
        word_after_si = match.lower().strip()
        
        # 检查是否使用了不当的词
        is_forbidden = False
        for forbidden in forbidden_with_si:
            if word_after_si == forbidden or word_after_si.startswith(forbidden + ' '):
                errors.append(f"'si {match}'")
                is_forbidden = True
                break
        
        if is_forbidden:
            continue
    
    if errors:
        error_list = ", ".join(errors)
        return 0, f"❌ 'si' 使用不当，不应用于尊贵或神圣的称呼: {error_list}。'si' 应该用于昵称、小动物或带有亲昵/略带贬义的称呼。"
    
    return 1, f"✓ 'si' 冠词使用正确（共 {len(matches)} 处）"


def check_sang_usage(text):
    """
    检查印尼语冠词 'sang' 的使用是否正确
    返回: (score, message)
    """
    import re
    
    # 处理输入类型
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    elif not isinstance(text, str):
        text = str(text)
    
    # 查找所有 'sang' + 名词的模式
    sang_pattern = r'\b[Ss]ang\s+([a-zA-Z\s]+?)(?=\.|,|!|\?|\s+[a-z]{2,}\s|$|\n)'
    matches = re.findall(sang_pattern, text)
    
    if not matches:
        return 1, "✓ 未使用 'sang' 冠词"
    
    # 不应该与 'sang' 搭配的词（表示卑微、渺小的词）
    inappropriate_with_sang = [
        'tikus', 'kecoa', 'lalat', 'nyamuk', 'kutu',  # 害虫小动物
        'cacing', 'ulat',  # 小虫子
        'sampah', 'kotoran',  # 污秽之物
        'semut kecil', 'kutu busuk', 'tikus got',  # 组合贬义词
    ]
    
    # 适合与 'sang' 搭配的词（表示尊贵、重要的词）
    appropriate_with_sang = [
        'raja', 'ratu', 'pangeran', 'putri', 'sultan', 'kaisar',  # 王室
        'harimau', 'singa', 'elang', 'naga', 'gajah', 'ular', 'buaya',  # 威严的动物
        'pemimpin', 'komandan', 'ketua', 'kepala', 'jenderal',  # 领导者
        'matahari', 'bulan', 'bintang', 'langit', 'laut', 'angin',  # 拟人化自然
        'dewi', 'dewa', 'bidadari',  # 神灵
        'pahlawan', 'pejuang', 'juara', 'pemenang',  # 英雄
        'guru', 'bijak', 'arif', 'penyair', 'seniman',  # 智者/艺术家
        'kancil', 'kelinci', 'burung', 'beruang', 'serigala',  # 童话中常见的主角动物
        'rubah', 'kerbau', 'kuda', 'monyet', 'rusa',
        'kura', 'penyu', 'lumba',
    ]
    
    errors = []
    warnings = []
    
    # 检查每个匹配
    for match in matches:
        words_after_sang = match.lower().strip()
        
        # 检查是否使用了明确不当的词
        found_inappropriate = False
        for inappropriate in inappropriate_with_sang:
            if inappropriate in words_after_sang:
                errors.append(f"'sang {match.strip()}'")
                found_inappropriate = True
                break
        
        if found_inappropriate:
            continue
        
        # 检查是否使用了合适的词
        is_appropriate = False
        for appropriate in appropriate_with_sang:
            if appropriate in words_after_sang:
                is_appropriate = True
                break
        
        # 如果没有匹配到合适的词，但也不是明确错误的，给出警告
        if not is_appropriate:
            first_word = words_after_sang.split()[0] if words_after_sang else ""
            # 只在特定情况下给出警告，避免过于严格
            if len(first_word) > 0 and first_word not in ['yang', 'ini', 'itu']:
                warnings.append(f"'sang {match.strip()}'")
    
    if errors:
        error_list = ", ".join(errors)
        return 0, f"❌ 'sang' 使用不当，不应用于卑微或不受尊敬的事物: {error_list}。'sang' 应该用于尊贵的人物、威严的动物或拟人化的自然现象。"
    
    if warnings:
        # 警告不影响得分，只是提示
        warning_list = ", ".join(warnings)
        return 1, f"✓ 'sang' 冠词使用基本正确（共 {len(matches)} 处），但请注意: {warning_list} 可能不是最典型的用法"
    
    return 1, f"✓ 'sang' 冠词使用正确（共 {len(matches)} 处）"

# ==================== 印尼语宾语前置强调句检测（修正版）====================

import re
from typing import Tuple, Dict, List

def check_fronted_emphasis(text: str, exact_count: int = 1) -> Tuple[bool, str]:
    """
    检测印尼语中的宾语前置强调句（只检测主句）
    
    核心定义：
    将正常语序中的宾语提前到句首，用逗号分隔，以强调该宾语。
    
    结构：[宾语名词短语], [主语] + [及物动词] + ...
    
    排除：
    1. 称呼语
    2. 状语
    3. 主系表结构
    4. 固定表达
    5. "主语, 关系从句, 谓语" 结构（这不是宾语前置）
    
    示例：
    ✅ Adik, aku ajak ke mal
       正常：Aku ajak adik ke mal
       前置：主句宾语(adik)被提前
    
    ✅ Hubungan kita, aku sangat menghargainya
       正常：Aku menghargai hubungan kita
       前置：主句宾语(hubungan kita)被提前
    
    ✅ Adik yang dekat denganku, aku ajak
       "yang dekat denganku" 是定语从句，修饰 adik
       简化后：Adik, aku ajak（是宾语前置）
    
    ❌ Kesalahpahaman ini, yang mungkin membuatmu tidak nyaman, sangat aku sesali
       这是 "主语, 关系从句插入语, 谓语" 结构
       不是宾语前置
    
    ❌ Terima kasih, aku senang
       固定表达，不是宾语前置
    
    Args:
        text: 要检测的文本
        exact_count: 要求的精确数量
    
    Returns:
        (是否通过, 详细说明)
    """
    
    # ============ 类型检查和转换 ============
    if text is None:
        return False, "❌ 错误：输入文本为空（None）"
    
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                for key in ['text', 'content', 'message', 'response']:
                    if key in item and isinstance(item[key], str):
                        text_parts.append(item[key])
                        break
            else:
                text_parts.append(str(item))
        text = ' '.join(text_parts)
    
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return False, f"❌ 错误：无法转换为字符串"
    
    if not text.strip():
        return False, "❌ 错误：输入文本为空"
    
    # ============ 称呼语列表（需要排除）============
    vocatives = {
        'sayang', 'kamu', 'sobat', 'teman', 'bapak', 'ibu', 'mas', 'mbak',
        'pak', 'bu', 'bang', 'kak', 'dik', 'nak', 'ananda', 'ayah', 'bunda',
        'saudara', 'saudari', 'tuan', 'nyonya', 'nona', 'adik', 'kakak',
        'yang terhormat', 'yth', 'kepada', 'dear'
    }
    
    # ============ 固定表达/感叹语（需要排除）============
    fixed_expressions = [
        'terima kasih', 'selamat pagi', 'selamat siang', 'selamat sore', 
        'selamat malam', 'selamat datang', 'selamat tinggal', 'selamat jalan',
        'maaf', 'mohon maaf', 'permisi', 'assalamualaikum', 'waalaikumsalam',
        'salam sejahtera', 'halo', 'hai', 'sampai jumpa', 'salam', 'hormat saya'
    ]
    
    # ============ 系动词列表（需要排除主系表结构）============
    copula_verbs = {'adalah', 'ialah', 'yaitu', 'merupakan'}
    
    # ============ 代词后缀 ============
    pronoun_suffixes = {'ku', 'mu', 'nya', 'kah', 'lah'}
    
    # ============ 及物动词列表 ============
    transitive_verbs = {
        # 基本形式
        'ajak', 'pilih', 'beli', 'lihat', 'hargai', 'percaya', 'jelaskan', 'harap',
        'lupakan', 'buat', 'cari', 'kirim', 'terima', 'berikan', 'kasih',
        'cinta', 'sayang', 'tunggu', 'kenal', 'ingat', 'lupa', 'mengerti', 'pahami',
        'ketahui', 'tahu', 'minta', 'ambil', 'bawa', 'ucapkan', 'sampaikan',
        'sesali', 'rayakan', 'nikmati', 'jaga', 'upayakan', 'pergi',
        
        # me- 前缀
        'mengajak', 'memilih', 'membeli', 'melihat', 'menghargai', 'mempercayai',
        'menjelaskan', 'mengharapkan', 'melupakan', 'menginginkan', 'membuat',
        'mencari', 'mengirim', 'menerima', 'memberikan', 'mencintai', 'menyayangi',
        'menunggu', 'mengenal', 'mengingat', 'memahami', 'mengetahui', 'meminta',
        'mengambil', 'membawa', 'mengucapkan', 'menyampaikan',
        'menyesali', 'merayakan', 'menikmati', 'menjaga', 'mengupayakan',
        
        # 口语形式
        'kuajak', 'kupilih', 'kubeli', 'kulihat', 'kuhargai', 'kupercaya',
        'kujelaskan', 'kuharap', 'kulupakan', 'kucari', 'kubuat', 'kusesali',
        'kujaga',
        'kauajak', 'kaupilih', 'kaubeli',
    }
    
    # 助动词（需要跳过）
    auxiliary_verbs = {
        'ingin', 'mau', 'akan', 'harus', 'bisa', 'dapat', 'boleh',
        'perlu', 'hendak', 'mesti', 'sudah', 'telah', 'sedang', 'masih',
        'pernah', 'sempat', 'bakal'
    }
    
    # 程度副词（需要跳过）
    adverbs = {
        'sangat', 'sekali', 'amat', 'benar', 'paling', 'lebih', 'kurang',
        'cukup', 'terlalu', 'agak', 'sedikit', 'banyak', 'selalu', 'sering',
        'jarang', 'kadang', 'pernah', 'benar-benar', 'sebenarnya', 'memang',
        'tidak', 'belum', 'jangan'
    }
    
    # 主语代词
    subject_pronouns = {
        'aku', 'ku', 'saya', 'kamu', 'kau', 'mu', 'dia', 'ia',
        'kami', 'kita', 'kalian', 'mereka', 'beliau', 'anda'
    }
    
    # 排除的起始词（这些是状语，不是宾语）
    adverbial_starters = {
        'di', 'ke', 'dari', 'pada', 'untuk', 'dengan', 'tanpa',
        'ketika', 'saat', 'setelah', 'sebelum', 'kemarin', 'besok',
        'selama', 'sejak', 'sampai', 'hingga', 'tadi', 'nanti',
        'karena', 'sebab', 'meskipun', 'walaupun', 'jika', 'kalau'
    }
    
    found_patterns = []
    
    # ============ 核心改进：检测并排除"主语 + 关系从句 + 谓语"结构 ============
    def is_subject_with_relative_clause(sentence):
        """
        检测是否是 "主语, 关系从句, 谓语" 结构
        例如：Kesalahpahaman ini, yang mungkin membuatmu tidak nyaman, sangat aku sesali
        
        特征：
        1. 第一个逗号后紧跟 yang
        2. 第二个逗号后是谓语（没有主语+动词结构）
        
        返回：True 表示是这种结构（需要排除）
        """
        # 匹配模式：名词, yang ..., 动词/副词
        pattern = r'^[^,]+,\s*yang\s+[^,]+,\s*(.+)$'
        match = re.match(pattern, sentence.strip(), re.IGNORECASE)
        
        if not match:
            return False
        
        # 检查第二个逗号后的部分
        after_second_comma = match.group(1).strip().lower()
        words = after_second_comma.split()
        
        if not words:
            return False
        
        # 如果第一个词是副词或否定词，很可能是 "主语, 关系从句, 谓语" 结构
        # 例如：sangat aku sesali, tidak aku lupa
        first_word = words[0]
        if first_word in adverbs or first_word in {'tidak', 'belum', 'jangan'}:
            return True
        
        # 如果直接是动词（没有主语），也可能是这种结构
        # 但这种情况较少见，暂不处理
        
        return False
    
    # ============ 改进：处理定语从句 ============
    def extract_main_clause_only(sentence):
        """
        提取主句，移除定语从句
        
        处理两种情况：
        1. "名词 yang ..., 主语 动词" -> "名词, 主语 动词" （宾语前置）
        2. "名词, yang ..., 谓语" -> 返回 None（不是宾语前置，是主语+关系从句）
        """
        
        # 先检查是否是 "主语 + 关系从句 + 谓语" 结构
        if is_subject_with_relative_clause(sentence):
            return None  # 返回 None 表示需要排除
        
        # 移除 "yang ... " 格式的定语从句（在逗号前）
        # 例如："Adik yang dekat denganku, aku ajak" -> "Adik, aku ajak"
        cleaned = re.sub(r'\s+yang\s+[^,]+(?=,)', '', sentence)
        
        # 移除 bahwa 引导的宾语从句
        cleaned = re.sub(r'\s+bahwa\s+[^.!?]+', '', cleaned)
        
        return cleaned
    
    # ============ 按句子分割 ============
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # ============ 关键改进：提取主句并排除特殊结构 ============
        sentence_main_only = extract_main_clause_only(sentence)
        
        # 如果返回 None，说明是 "主语 + 关系从句 + 谓语" 结构，跳过
        if sentence_main_only is None:
            continue
        
        # ============ 查找逗号分隔的结构 ============
        comma_parts = sentence_main_only.split(',', 1)
        if len(comma_parts) != 2:
            continue
        
        potential_object = comma_parts[0].strip()
        main_clause = comma_parts[1].strip()
        
        # ============ 验证前置部分 ============
        
        # 1. 前置部分不能为空或太短
        if len(potential_object) < 2:
            continue
        
        # 2. 排除称呼语
        potential_lower = potential_object.lower()
        if potential_lower in vocatives:
            continue
        
        potential_words = potential_lower.split()
        if len(potential_words) == 1 and potential_words[0] in vocatives:
            continue
        
        # 3. 排除固定表达
        is_fixed_expr = False
        for expr in fixed_expressions:
            if potential_lower.startswith(expr):
                is_fixed_expr = True
                break
        
        if is_fixed_expr:
            continue
        
        # 4. 排除状语（地点、时间等）
        first_word = potential_words[0]
        if first_word in adverbial_starters:
            continue
        
        # 5. 排除完整句子（包含主句动词）
        has_main_verb = False
        for verb in copula_verbs:
            if verb in potential_lower:
                has_main_verb = True
                break
        
        if has_main_verb:
            continue
        
        # ============ 验证主句部分 ============
        
        main_words = main_clause.lower().split()
        if len(main_words) < 2:
            continue
        
        # ============ 检查是否以 dan/atau 开头（并列句）============
        if main_words[0] in {'dan', 'atau', 'tetapi', 'namun', 'tapi'}:
            continue
        
        # ============ 检查是否是主系表结构 ============
        has_copula = False
        for copula in copula_verbs:
            if copula in main_words:
                has_copula = True
                break
        
        if has_copula:
            continue
        
        # ============ 查找主语和及物动词 ============
        
        found_subject = None
        found_verb = None
        
        # 遍历主句，寻找动词和主语
        for i, word in enumerate(main_words):
            # 跳过副词和助动词
            if word in adverbs or word in auxiliary_verbs:
                continue
            
            # ============ 处理代词后缀 ============
            clean_word = word
            for suffix in pronoun_suffixes:
                if word.endswith(suffix) and len(word) > len(suffix) + 2:
                    clean_word = word[:-len(suffix)]
                    break
            
            # 去掉前缀检查
            verb_root = clean_word
            for prefix in ['me', 'mem', 'men', 'meng', 'meny', 'ku', 'kau', 'di']:
                if clean_word.startswith(prefix) and len(clean_word) > len(prefix) + 2:
                    verb_root = clean_word[len(prefix):]
                    break
            
            # 检查是否是及物动词
            is_transitive = (word in transitive_verbs or 
                           clean_word in transitive_verbs or 
                           verb_root in transitive_verbs)
            
            if is_transitive:
                found_verb = word
                
                # ============ 向前和向后查找主语 ============
                # 先向前查找（标准语序：主语在动词前）
                for j in range(max(0, i-4), i):
                    if main_words[j] in subject_pronouns:
                        found_subject = main_words[j]
                        break
                
                # 如果没找到，向后查找（倒装：主语在动词后）
                if not found_subject:
                    for j in range(i+1, min(len(main_words), i+4)):
                        if main_words[j] in subject_pronouns:
                            found_subject = main_words[j]
                            break
                
                # 找到就退出
                if found_subject:
                    break
        
        # ============ 确认是宾语前置 ============
        
        if found_subject and found_verb:
            # 还原正常语序
            restored = f"{found_subject} {found_verb} {potential_object}"
            
            found_patterns.append({
                'original_sentence': sentence,  # 原始句子（包含从句）
                'main_clause_only': sentence_main_only,  # 只有主句的简化版
                'fronted_object': potential_object,
                'subject': found_subject,
                'verb': found_verb,
                'main_clause': main_clause,
                'restored_order': restored,
            })
    
    # ============ 去重 ============
    unique_patterns = []
    seen = set()
    
    for item in found_patterns:
        # 基于主句结构去重
        key = (item['fronted_object'].lower(), item['subject'], item['verb'])
        if key not in seen:
            unique_patterns.append(item)
            seen.add(key)
    
    # ============ 统计和判断 ============
    
    total_count = len(unique_patterns)
    passed = (total_count == exact_count)
    
    # ============ 生成说明 ============
    
    detail_parts = []
    
    if passed:
        detail_parts.append(f"✅ 正确：找到正好 {total_count} 个主句宾语前置强调句（要求正好 {exact_count} 个）\n")
    else:
        if total_count < exact_count:
            shortage = exact_count - total_count
            detail_parts.append(f"❌ 错误：只找到 {total_count} 个主句宾语前置强调句，少于要求的 {exact_count} 个（还差 {shortage} 个）\n")
        else:
            excess = total_count - exact_count
            detail_parts.append(f"❌ 错误：找到 {total_count} 个主句宾语前置强调句，超过要求的 {exact_count} 个（多了 {excess} 个）\n")
    
    if unique_patterns:
        detail_parts.append("找到的主句宾语前置强调句详情：")
        for i, item in enumerate(unique_patterns, 1):
            detail_parts.append(f"\n  [{i}] 主句宾语前置强调句")
            detail_parts.append(f"      原始句子: {item['original_sentence']}")
            detail_parts.append(f"      主句简化: {item['main_clause_only']}")
            detail_parts.append(f"      前置宾语: {item['fronted_object']}")
            detail_parts.append(f"      主语: {item['subject']}")
            detail_parts.append(f"      动词: {item['verb']}")
            detail_parts.append(f"      还原语序: {item['restored_order']}")
    else:
        detail_parts.append("❌ 未找到任何主句宾语前置强调句")
    
    detail = '\n'.join(detail_parts)
    
    return passed, detail


# ============ 测试代码 ============
if __name__ == "__main__":
    # 测试案例1：标准宾语前置
    test_text1 = """
    Adik yang sangat dekat denganku, aku ajak untuk membantu.
    Hubungan kita, aku sangat menghargainya.
    Hadiah yang spesial adalah tujuan utamaku.
    """
    
    print("=" * 70)
    print("测试案例1：应该找到2个主句宾语前置强调句")
    print("=" * 70)
    passed, detail = check_fronted_emphasis(test_text1, exact_count=2)
    print(detail)
    print()
    
    # 测试案例2：需要排除的结构
    test_text2 = """
    Kesalahpahaman ini, yang mungkin membuatmu merasa tidak nyaman, sangat aku sesali.
    Sayang, kemarin aku pergi ke mal.
    Terima kasih atas pengertianmu, dan aku sangat senang.
    Di mal, kita bertemu secara kebetulan.
    """
    
    print("=" * 70)
    print("测试案例2：应该找到0个（都需要排除）")
    print("=" * 70)
    passed, detail = check_fronted_emphasis(test_text2, exact_count=0)
    print(detail)
    print()
    
    # 测试案例3：混合案例
    test_text3 = """
    Hadiah ulang tahun untukmu, aku pergi ke mal kemarin untuk membelinya. 
    Adik yang sangat dekat denganku, aku ajak untuk membantu memberikan pendapat tentang hadiah yang tepat. 
    Kesalahpahaman yang terjadi, aku ingin menjelaskan bahwa orang yang bersamaku adalah adikku. 
    Hubungan kita, aku sangat menghargainya dan tidak ingin ada kesalahpahaman yang mengganggu.
    Kesalahpahaman ini, yang mungkin membuatmu tidak nyaman, sangat aku sesali.
    """
    
    print("=" * 70)
    print("测试案例3：混合测试")
    print("=" * 70)
    passed, detail = check_fronted_emphasis(test_text3, exact_count=4)
    print(detail)
    print()


# ==================== 印尼语借词检测（每个店名必须包含指定数量）====================

import re
from typing import Tuple, List, Dict
from collections import Counter

def check_indonesian_loanwords_each(text: str, required_count: int, initial_letter: str, letter_count: int) -> Tuple[bool, str]:
    """
    检测每个店名是否都包含指定数量的、以指定字母开头且由指定字母数组成的英语/法语/荷兰语借词
    
    Args:
        text: 要检测的文本（包含多个店名）
        required_count: 每个店名要求的借词数量
        initial_letter: 要求的首字母（如 'S', 'M', 'F' 等）
        letter_count: 要求的字母数（如 5, 6, 7 等）
    
    Returns:
        (是否通过, 详细说明)
    """
    
    # ============ 类型检查和转换 ============
    if text is None:
        return False, "❌ 错误：输入文本为空（None）"
    
    # 处理列表类型
    if isinstance(text, list):
        store_names = []
        for item in text:
            if isinstance(item, str):
                store_names.append(item.strip())
            elif isinstance(item, dict):
                for key in ['name', 'text', 'content', 'title']:
                    if key in item and isinstance(item[key], str):
                        store_names.append(item[key].strip())
                        break
        text = store_names
    
    # 处理字符串类型
    if isinstance(text, str):
        lines = text.strip().split('\n')
        store_names = []
        for line in lines:
            line = line.strip()
            # 移除编号、符号等
            line = re.sub(r'^[\d\-\*\•]+[\.\)]\s*', '', line)
            line = re.sub(r'^[\-\*\•]+\s*', '', line)
            # 提取冒号或破折号前的部分作为店名
            if ':' in line or '：' in line:
                line = re.split(r'[:：]', line)[0].strip()
            if '—' in line or '–' in line:
                parts = re.split(r'[—–]', line)
                if len(parts) > 0:
                    line = parts[0].strip()
            if line and len(line) > 0:
                store_names.append(line)
        text = store_names
    
    if not text or (isinstance(text, list) and len(text) == 0):
        return False, "❌ 错误：未找到任何店名"
    
    # ============ 印尼语借词词库（按首字母和字母数分类）============
    
    INDONESIAN_LOANWORDS = {
        'S': {    
            5: ['serba'],
            6: ['sistem',  'sukses', 'sentra', 'simpel', 'sentral'],
            7: ['spesial'],        
        },
        'M': {
            4: ['moda'],
        },
        'F': {
            5: ['fokus'],            
            7: ['favorit',  'fantasi'],            
        },
        'K': {    
            6: ['komplit', 'komplet'],
            7: ['kreatif'],
            8: ['kualitas'],            
        },
        'P': {
            7: [ 'populer',  'praktis'],            
        },
        'T': {
            7: [ 'tradisi'],
        },
        'E': { 
            6: ['ekspres',  'elegan'],
            7: ['ekonomis', 'efisien'],
            8: [ 'ekonomi']
        }
    }
    
    # ============ 辅助函数：检查是否为借词 ============
    
    def is_valid_loanword(word: str, letter: str, length: int) -> bool:
        """检查词是否是有效的借词"""
        word_lower = word.lower().strip('.,;:!?()[]{}"""\'\'—–-')
        letter_lower = letter.lower()
        
        # 检查首字母
        if not word_lower.startswith(letter_lower):
            return False
        
        # 检查字母数
        if len(word_lower) != length:
            return False
        
        # 检查是否在借词词库中
        if letter.upper() in INDONESIAN_LOANWORDS:
            if length in INDONESIAN_LOANWORDS[letter.upper()]:
                if word_lower in INDONESIAN_LOANWORDS[letter.upper()][length]:
                    return True
        
        # 宽松模式：如果不在词库但符合借词特征
        # 借词特征：包含特定字母组合
        loanword_patterns = [
            r'ph', r'th', r'ch', r'tion', r'sion', 
            r'sch', r'ck', r'ff', r'ss', r'tial', r'cial'
        ]
        
        for pattern in loanword_patterns:
            if re.search(pattern, word_lower):
                return True
        
        return False
    
    # ============ 检测每个店名中的借词 ============
    
    initial_upper = initial_letter.upper()
    initial_lower = initial_letter.lower()
    
    store_details = []
    failed_stores = []
    all_passed = True
    
    for store_idx, store_name in enumerate(text, 1):
        if not isinstance(store_name, str):
            store_name = str(store_name)
        
        store_name_clean = store_name.strip()
        words = store_name_clean.split()
        
        store_loanwords = []
        
        for word in words:
            word_clean = word.strip('.,;:!?()[]{}"""\'\'—–-')
            
            # 检查是否是有效借词
            if is_valid_loanword(word_clean, initial_letter, letter_count):
                store_loanwords.append(word_clean)
        
        loanword_count = len(store_loanwords)
        is_passed = (loanword_count == required_count)
        
        store_details.append({
            'index': store_idx,
            'store_name': store_name_clean,
            'loanwords': store_loanwords,
            'count': loanword_count,
            'required': required_count,
            'passed': is_passed
        })
        
        if not is_passed:
            all_passed = False
            failed_stores.append({
                'index': store_idx,
                'store_name': store_name_clean,
                'count': loanword_count,
                'required': required_count,
                'difference': loanword_count - required_count
            })
    
    # ============ 判断是否通过 ============
    
    passed = all_passed
    
    # ============ 生成详细说明 ============
    
    detail_parts = []
    
    # 构建条件描述
    condition_desc = f"以字母 '{initial_letter}' 开头且由 {letter_count} 个字母组成的借词"
    
    if passed:
        detail_parts.append(f"✅ 正确：所有 {len(store_details)} 个店名都包含正好 {required_count} 个{condition_desc}\n")
        
        detail_parts.append("各店名检测结果：")
        for detail in store_details:
            detail_parts.append(f"  {detail['index']}. {detail['store_name']}")
            if detail['loanwords']:
                detail_parts.append(f"     ✓ 包含借词: {', '.join(detail['loanwords'])} ({detail['count']}个)")
            else:
                detail_parts.append(f"     ✓ （恰好0个借词）")
    
    else:
        failed_count = len(failed_stores)
        passed_count = len(store_details) - failed_count
        
        detail_parts.append(f"❌ 错误：有 {failed_count} 个店名不符合要求（共 {len(store_details)} 个店名，{passed_count} 个通过）\n")
        
        detail_parts.append("✅ 通过的店名：")
        passed_stores = [d for d in store_details if d['passed']]
        if passed_stores:
            for detail in passed_stores:
                detail_parts.append(f"  {detail['index']}. {detail['store_name']}")
                if detail['loanwords']:
                    detail_parts.append(f"     ✓ 包含借词: {', '.join(detail['loanwords'])} ({detail['count']}个)")
        else:
            detail_parts.append("  （无）")
        
        detail_parts.append("\n❌ 未通过的店名：")
        for fail in failed_stores:
            detail_parts.append(f"  {fail['index']}. {fail['store_name']}")
            if fail['difference'] > 0:
                detail_parts.append(f"     ✗ 找到 {fail['count']} 个借词，超过要求的 {fail['required']} 个（多 {fail['difference']} 个）")
            else:
                shortage = abs(fail['difference'])
                detail_parts.append(f"     ✗ 找到 {fail['count']} 个借词，少于要求的 {fail['required']} 个（少 {shortage} 个）")
            
            # 显示该店名找到的借词
            failed_detail = next(d for d in store_details if d['index'] == fail['index'])
            if failed_detail['loanwords']:
                detail_parts.append(f"     找到的借词: {', '.join(failed_detail['loanwords'])}")
        
        # 提供参考建议
        detail_parts.append(f"\n💡 符合条件的 '{initial_letter}' 开头、{letter_count} 字母的借词参考：")
        if initial_upper in INDONESIAN_LOANWORDS:
            if letter_count in INDONESIAN_LOANWORDS[initial_upper]:
                examples = INDONESIAN_LOANWORDS[initial_upper][letter_count]
                detail_parts.append(f"  {', '.join(examples[:15])}")
            else:
                detail_parts.append(f"  （词库中暂无 {letter_count} 字母的 {initial_letter} 开头借词）")
                # 显示相近字母数的借词
                nearby_lengths = sorted([l for l in INDONESIAN_LOANWORDS[initial_upper].keys() 
                                        if abs(l - letter_count) <= 2])
                if nearby_lengths:
                    detail_parts.append(f"\n  相近字母数的借词：")
                    for length in nearby_lengths:
                        examples = INDONESIAN_LOANWORDS[initial_upper][length]
                        detail_parts.append(f"    {length}字母: {', '.join(examples[:5])}")
        else:
            detail_parts.append(f"  （词库中暂无 {initial_letter} 开头的借词）")
    
    detail = '\n'.join(detail_parts)
    
    return passed, detail


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 测试案例1：要求每个店名包含1个5字母的S开头借词
    test_case_1 = [
        "Super Makmur Jaya",
        "Toko Smart Indonesia",
        "Pasar Sport Sejahtera"
    ]
    
    print("=" * 80)
    print("测试案例1：要求每个店名包含1个5字母的S开头借词")
    print("店名：")
    for name in test_case_1:
        print(f"  - {name}")
    
    result, detail = check_indonesian_loanwords_each(test_case_1, 1, 'S', 5)
    print(f"\n结果：{'✅ 通过' if result else '❌ 失败'}")
    print(f"\n{detail}")
    
    # 测试案例2：失败案例（第3个店名没有符合条件的借词）
    test_case_2 = [
        "Super Makmur Jaya",
        "Toko Smart Indonesia",
        "Pasar Sejahtera Sentosa"  # Sentosa不是借词
    ]
    
    print("\n" + "=" * 80)
    print("测试案例2：要求每个店名包含1个5字母的S开头借词（第3个不符合）")
    print("店名：")
    for name in test_case_2:
        print(f"  - {name}")
    
    result, detail = check_indonesian_loanwords_each(test_case_2, 1, 'S', 5)
    print(f"\n结果：{'✅ 通过' if result else '❌ 失败'}")
    print(f"\n{detail}")
    
    # 测试案例3：失败案例（第1个店名有2个符合条件的借词）
    test_case_3 = [
        "Super Smart Mart",  # 有2个5字母S开头借词
        "Toko Sport Indonesia",
        "Pasar Salon Makmur"
    ]
    
    print("\n" + "=" * 80)
    print("测试案例3：要求每个店名包含1个5字母的S开头借词（第1个有2个）")
    print("店名：")
    for name in test_case_3:
        print(f"  - {name}")
    
    result, detail = check_indonesian_loanwords_each(test_case_3, 1, 'S', 5)
    print(f"\n结果：{'✅ 通过' if result else '❌ 失败'}")
    print(f"\n{detail}")
    
    # 测试案例4：要求每个店名包含2个6字母的M开头借词
    test_case_4 = [
        "Modern Mandiri Mart",  # Modern(6), Mandiri(7), Mart(4)
        "Toko Makmur Indonesia"  # Makmur(6)
    ]
    
    print("\n" + "=" * 80)
    print("测试案例4：要求每个店名包含2个6字母的M开头借词")
    print("店名：")
    for name in test_case_4:
        print(f"  - {name}")
    
    result, detail = check_indonesian_loanwords_each(test_case_4, 2, 'M', 6)
    print(f"\n结果：{'✅ 通过' if result else '❌ 失败'}")
    print(f"\n{detail}")
    
    # 测试案例5：要求0个（允许没有借词）
    test_case_5 = [
        "Toko Makmur Jaya",
        "Pasar Sejahtera"
    ]
    
    print("\n" + "=" * 80)
    print("测试案例5：要求每个店名包含0个5字母的S开头借词")
    print("店名：")
    for name in test_case_5:
        print(f"  - {name}")
    
    result, detail = check_indonesian_loanwords_each(test_case_5, 0, 'S', 5)
    print(f"\n结果：{'✅ 通过' if result else '❌ 失败'}")
    print(f"\n{detail}")
