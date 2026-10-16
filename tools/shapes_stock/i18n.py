"""Category names of Stock › Formas in the 15 languages of the app, and the singular noun the
other 13 languages use to name each shape («<noun> <n>»; Spanish and English names are written
by hand in shapes.py)."""

OTHER_LANGS = ["ar", "bn", "fr", "it", "ja", "ko", "pl", "pt", "ru", "si", "tl", "vi", "zh"]
LANGS = ["es", "en"] + OTHER_LANGS

_ROWS = {
    #            es, en, ar, bn, fr, it, ja, ko, pl, pt, ru, si, tl, vi, zh
    "hearts": ["Corazones", "Hearts", "قلوب", "হৃদয়", "Cœurs", "Cuori", "ハート", "하트", "Serca", "Corações", "Сердца",
               "හදවත්", "Mga puso", "Trái tim", "爱心"],
    "stars": ["Estrellas", "Stars", "نجوم", "তারা", "Étoiles", "Stelle", "星", "별", "Gwiazdy", "Estrelas", "Звёзды",
              "තරු", "Mga bituin", "Ngôi sao", "星星"],
    "bubbles": ["Bocadillos", "Speech bubbles", "فقاعات الكلام", "কথার বুদবুদ", "Bulles", "Fumetti", "吹き出し", "말풍선",
                "Dymki", "Balões de fala", "Облачка речи", "කතා බුබුළු", "Mga speech bubble", "Bong bóng thoại", "对话气泡"],
    "clouds": ["Nubes", "Clouds", "غيوم", "মেঘ", "Nuages", "Nuvole", "雲", "구름", "Chmury", "Nuvens", "Облака",
               "වලාකුළු", "Mga ulap", "Mây", "云朵"],
    "paper": ["Papel rasgado", "Torn paper", "ورق ممزق", "ছেঁড়া কাগজ", "Papier déchiré", "Carta strappata", "破れた紙",
              "찢어진 종이", "Podarty papier", "Papel rasgado", "Рваная бумага", "ඉරුණු කඩදාසි", "Punit na papel",
              "Giấy xé", "撕纸"],
    "arrows": ["Flechas", "Arrows", "أسهم", "তীর", "Flèches", "Frecce", "矢印", "화살표", "Strzałki", "Setas", "Стрелки",
               "ඊතල", "Mga palaso", "Mũi tên", "箭头"],
    "badges": ["Insignias", "Badges", "شارات", "ব্যাজ", "Badges", "Badge", "バッジ", "배지", "Odznaki", "Emblemas",
               "Значки", "ලාංඡන", "Mga badge", "Huy hiệu", "徽章"],
    "seals": ["Sellos", "Seals and stamps", "أختام", "সিল", "Sceaux et tampons", "Sigilli e timbri", "スタンプ", "도장",
              "Pieczęcie", "Selos", "Печати", "මුද්‍රා", "Mga selyo", "Con dấu", "印章"],
    "frames": ["Marcos", "Frames", "إطارات", "ফ্রেম", "Cadres", "Cornici", "フレーム", "프레임", "Ramki", "Molduras",
               "Рамки", "රාමු", "Mga frame", "Khung", "边框"],
    "nature": ["Naturaleza", "Nature", "طبيعة", "প্রকৃতি", "Nature", "Natura", "自然", "자연", "Natura", "Natureza",
               "Природа", "සොබාදහම", "Kalikasan", "Thiên nhiên", "自然"],
    "waves": ["Ondas", "Waves", "أمواج", "ঢেউ", "Vagues", "Onde", "波", "물결", "Fale", "Ondas", "Волны", "රළ",
              "Mga alon", "Sóng", "波浪"],
    "splash": ["Manchas y salpicaduras", "Splashes and blobs", "بقع ورشّات", "ছিটে ও দাগ", "Taches et éclaboussures",
               "Macchie e schizzi", "しみとしぶき", "얼룩과 물방울", "Plamy i rozbryzgi", "Manchas e respingos",
               "Кляксы и брызги", "පැල්ලම්", "Mga mantsa at tilamsik", "Vệt loang", "斑点与泼溅"],
    "shields": ["Escudos", "Shields", "دروع", "ঢাল", "Boucliers", "Scudi", "盾", "방패", "Tarcze", "Escudos", "Щиты",
                "පලිස", "Mga kalasag", "Khiên", "盾牌"],
    "labels": ["Etiquetas y cintas", "Tags and ribbons", "ملصقات وأشرطة", "ট্যাগ ও ফিতা", "Étiquettes et rubans",
               "Etichette e nastri", "タグとリボン", "태그와 리본", "Etykiety i wstążki", "Etiquetas e fitas", "Ярлыки и ленты",
               "ටැග් සහ රිබන්", "Mga tag at laso", "Nhãn và ruy băng", "标签与丝带"],
    "symbols": ["Símbolos", "Symbols", "رموز", "প্রতীক", "Symboles", "Simboli", "記号", "기호", "Symbole", "Símbolos",
                "Символы", "සංකේත", "Mga simbolo", "Biểu tượng", "符号"],
    "geometric": ["Geométricas", "Geometric", "أشكال هندسية", "জ্যামিতিক", "Géométriques", "Geometriche", "幾何学",
                  "기하학", "Geometryczne", "Geométricas", "Геометрия", "ජ්‍යාමිතික", "Heometriko", "Hình học", "几何"],
}

_SINGULAR = {
    #             ar, bn, fr, it, ja, ko, pl, pt, ru, si, tl, vi, zh
    "hearts": ["قلب", "হৃদয়", "Cœur", "Cuore", "ハート", "하트", "Serce", "Coração", "Сердце", "හදවත", "Puso", "Trái tim", "爱心"],
    "stars": ["نجمة", "তারা", "Étoile", "Stella", "星", "별", "Gwiazda", "Estrela", "Звезда", "තරුව", "Bituin", "Ngôi sao", "星星"],
    "bubbles": ["فقاعة كلام", "কথার বুদবুদ", "Bulle", "Fumetto", "吹き出し", "말풍선", "Dymek", "Balão", "Облачко", "කතා බුබුළ",
                "Speech bubble", "Bong bóng thoại", "对话气泡"],
    "clouds": ["غيمة", "মেঘ", "Nuage", "Nuvola", "雲", "구름", "Chmura", "Nuvem", "Облако", "වලාකුළ", "Ulap", "Đám mây", "云朵"],
    "paper": ["ورق ممزق", "ছেঁড়া কাগজ", "Papier déchiré", "Carta strappata", "破れた紙", "찢어진 종이", "Podarty papier",
              "Papel rasgado", "Рваная бумага", "ඉරුණු කඩදාසි", "Punit na papel", "Giấy xé", "撕纸"],
    "arrows": ["سهم", "তীর", "Flèche", "Freccia", "矢印", "화살표", "Strzałka", "Seta", "Стрелка", "ඊතලය", "Palaso", "Mũi tên", "箭头"],
    "badges": ["شارة", "ব্যাজ", "Badge", "Badge", "バッジ", "배지", "Odznaka", "Emblema", "Значок", "ලාංඡනය", "Badge", "Huy hiệu", "徽章"],
    "seals": ["ختم", "সিল", "Sceau", "Sigillo", "スタンプ", "도장", "Pieczęć", "Selo", "Печать", "මුද්‍රාව", "Selyo", "Con dấu", "印章"],
    "frames": ["إطار", "ফ্রেম", "Cadre", "Cornice", "フレーム", "프레임", "Ramka", "Moldura", "Рамка", "රාමුව", "Frame", "Khung", "边框"],
    "nature": ["طبيعة", "প্রকৃতি", "Nature", "Natura", "自然", "자연", "Natura", "Natureza", "Природа", "සොබාදහම", "Kalikasan",
               "Thiên nhiên", "自然"],
    "waves": ["موجة", "ঢেউ", "Vague", "Onda", "波", "물결", "Fala", "Onda", "Волна", "රළ", "Alon", "Sóng", "波浪"],
    "splash": ["بقعة", "ছিটে", "Tache", "Macchia", "しみ", "얼룩", "Plama", "Mancha", "Клякса", "පැල්ලම", "Mantsa", "Vệt loang", "斑点"],
    "shields": ["درع", "ঢাল", "Bouclier", "Scudo", "盾", "방패", "Tarcza", "Escudo", "Щит", "පලිහ", "Kalasag", "Khiên", "盾牌"],
    "labels": ["ملصق", "ট্যাগ", "Étiquette", "Etichetta", "タグ", "태그", "Etykieta", "Etiqueta", "Ярлык", "ටැගය", "Tag", "Nhãn", "标签"],
    "symbols": ["رمز", "প্রতীক", "Symbole", "Simbolo", "記号", "기호", "Symbol", "Símbolo", "Символ", "සංකේතය", "Simbolo",
                "Biểu tượng", "符号"],
    "geometric": ["شكل هندسي", "জ্যামিতিক আকার", "Forme", "Forma", "図形", "도형", "Figura", "Forma", "Фигура", "හැඩය", "Hugis",
                  "Hình", "图形"],
}

CATEGORY_NAMES = {cat: dict(zip(LANGS, row)) for cat, row in _ROWS.items()}
CATEGORY_SINGULAR = {cat: dict(zip(OTHER_LANGS, row)) for cat, row in _SINGULAR.items()}
assert all(len(r) == 15 for r in _ROWS.values()) and all(len(r) == 13 for r in _SINGULAR.values())
