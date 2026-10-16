"""Video thumbnails (2026-10-16), 1920x1080, almost still (3 s; the thumbnail moment is the end state, export a frame).
Trends: one clear face with one emotion, three words or fewer, two or three colours with strong contrast, key content
away from the bottom-right corner (the duration badge). No platform logos or platform red. Category thumbnail;
order 5200-5299. Family `thumb` in formats.py.
"""

from __future__ import annotations

from formats import _maker, thumb

O = 5200
C = dict(  # palettes: bg, bg2, accent, accent2
    yel=dict(bg="#FFD23F", bg2="#FF9F1C", accent="#FFFFFF", accent2="#111111"),
    blu=dict(bg="#1E3A8A", bg2="#0EA5E9", accent="#FFE600", accent2="#111111"),
    pur=dict(bg="#3A0CA3", bg2="#F72585", accent="#FFE600", accent2="#111111"),
    grn=dict(bg="#065F46", bg2="#10B981", accent="#FFE600", accent2="#111111"),
    blk=dict(bg="#0B0B0B", bg2="#262626", accent="#FFE600", accent2="#E11D48"),
    org=dict(bg="#EA580C", bg2="#FACC15", accent="#FFFFFF", accent2="#111111"),
    pnk=dict(bg="#DB2777", bg2="#F472B6", accent="#FFFFFF", accent2="#111111"),
    cya=dict(bg="#0891B2", bg2="#22D3EE", accent="#FFE600", accent2="#111111"),
    nvy=dict(bg="#0F172A", bg2="#1E293B", accent="#38BDF8", accent2="#F97316"),
    lim=dict(bg="#65A30D", bg2="#A3E635", accent="#FFFFFF", accent2="#111111"),
)


def T(i, id, es, en, tags, pal, **kw):
    return dict(id=id, es=es, en=en, order=O + i, tags=tags, pal=C[pal], **kw)


SPECS = [
    # face + text (15)
    T(0, "mini-cara-probe", "Lo probé", "I tried it", ["probé", "reto", "experimento"], "yel", face="h-portrait-05",
      text="LO PROBÉ", text2="30 DÍAS", size=230, boxed=True),
    T(1, "mini-cara-no-hagas", "No hagas esto", "Don't do this", ["error", "consejo", "advertencia"], "blk",
      face="h-man-03", text="NO HAGAS ESTO", size=200, arrow=(980, 820, 160)),
    T(2, "mini-cara-secreto", "El secreto", "The secret", ["secreto", "truco", "revelado"], "pur", face="h-portrait-02",
      text="EL SECRETO", text2="nadie lo dice", size=220, side="left"),
    T(3, "mini-cara-vale", "¿Vale la pena?", "Is it worth it?", ["reseña", "opinión", "producto"], "nvy",
      face="h-man-05", text="¿VALE LA PENA?", size=190, badge="RESEÑA"),
    T(4, "mini-cara-cambio", "Esto cambió mi vida", "This changed my life", ["hábito", "cambio", "motivación"], "grn",
      face="h-portrait-04", text="CAMBIÓ MI VIDA", size=200, boxed=True, text2="en 1 semana"),
    T(5, "mini-cara-nadie", "Nadie me creyó", "Nobody believed me", ["historia", "storytime", "drama"], "org",
      face="h-portrait-03", text="NADIE ME CREYÓ", size=190, side="left"),
    T(6, "mini-cara-facil", "Así de fácil", "This easy", ["fácil", "tutorial", "aprende"], "cya", face="h-man-01",
      text="ASÍ DE FÁCIL", size=210, arrow=(1000, 300, -150)),
    T(7, "mini-cara-gratis", "Gratis", "Free", ["gratis", "herramientas", "recursos"], "lim", face="h-portrait-01",
      text="GRATIS", text2="y legal", size=300, boxed=True),
    T(8, "mini-cara-primera-vez", "Primera vez", "First time", ["primera vez", "experiencia", "vlog"], "pnk",
      face="h-portrait-06", text="MI PRIMERA VEZ", size=200, side="left", badge="VLOG"),
    T(9, "mini-cara-errores", "Errores de novato", "Rookie mistakes", ["errores", "novato", "consejos"], "blk",
      face="h-man-02", text="ERRORES DE NOVATO", size=180, arrow=(980, 780, 160)),
    T(10, "mini-cara-sin-dinero", "Sin dinero", "No money", ["ahorro", "barato", "viajar"], "grn", face="h-man-04",
      text="VIAJÉ SIN DINERO", size=190, side="left"),
    T(11, "mini-cara-lo-logre", "Lo logré", "I did it", ["logro", "meta", "reto"], "yel", face="h-portrait-05",
      text="¡LO LOGRÉ!", size=240, badge="NUEVO"),
    T(12, "mini-cara-verdad", "La verdad", "The truth", ["verdad", "opinión", "honesto"], "nvy", face="h-portrait-02",
      text="LA VERDAD", text2="sobre esto", size=240, boxed=True, side="left"),
    T(13, "mini-cara-rutina", "Mi rutina", "My routine", ["rutina", "mañana", "productividad"], "cya", face="h-portrait-04",
      text="MI RUTINA 5 AM", size=200),
    T(14, "mini-cara-reaccion", "Reaccionando", "Reacting", ["reacción", "react", "humor"], "pur", face="h-man-03",
      text="NO PUEDE SER", size=210, side="left", arrow=(900, 780, 20)),
    # versus (6)
    T(15, "mini-vs-ciudad-campo", "Ciudad vs campo", "City vs country", ["versus", "comparación", "vida"], "blk",
      kind="vs", photos=["h-city-03", "h-nature-03"], text="¿DÓNDE VIVIR?"),
    T(16, "mini-vs-barato-caro", "Barato vs caro", "Cheap vs expensive", ["versus", "barato", "caro", "prueba"], "org",
      kind="vs", photos=["h-food-04", "h-food-03"], text="$5 VS $50"),
    T(17, "mini-vs-cafe", "Café de casa vs cafetería", "Home vs café coffee", ["versus", "café", "comparación"], "nvy",
      kind="vs", photos=["h-cafe-02", "h-cafe-04"], text="CASA VS CAFETERÍA", size=140),
    T(18, "mini-vs-playa-montana", "Playa vs montaña", "Beach vs mountains", ["versus", "viaje", "vacaciones"], "cya",
      kind="vs", photos=["h-beach-01", "h-nature-05"], text="¿PLAYA O MONTAÑA?", size=150),
    T(19, "mini-vs-gym-casa", "Gym vs casa", "Gym vs home workout", ["versus", "gym", "ejercicio"], "lim", kind="vs",
      photos=["h-fitness-01", "h-interior-05"], text="GYM VS CASA"),
    T(20, "mini-vs-perros-gatos", "¿Perros o gatos?", "Dogs or cats?", ["versus", "mascotas", "debate"], "pnk", kind="vs",
      photos=["h-pet-01", "h-pet-04"], text="¿CUÁL ES MEJOR?"),
    # before / after (6)
    T(21, "mini-ba-cuarto", "Cuarto antes y después", "Room before/after", ["antes y después", "cuarto", "decoración"],
      "yel", kind="beforeafter", photos=["h-interior-02", "h-interior-04"], text="CON $100"),
    T(22, "mini-ba-jardin", "Jardín antes y después", "Garden before/after", ["antes y después", "jardín", "plantas"],
      "grn", kind="beforeafter", photos=["h-autumn-03", "h-spring-01"], text="3 MESES"),
    T(23, "mini-ba-casa", "Casa antes y después", "House before/after", ["antes y después", "casa", "remodelación"],
      "nvy", kind="beforeafter", photos=["h-house-03", "h-house-04"], text="REMODELACIÓN TOTAL"),
    T(24, "mini-ba-cocina", "Cocina antes y después", "Kitchen before/after", ["antes y después", "cocina", "hogar"],
      "org", kind="beforeafter", photos=["h-interior-02", "h-interior-05"], text="¡IRRECONOCIBLE!"),
    T(25, "mini-ba-fitness", "Mi cambio físico", "Fitness transformation", ["antes y después", "fitness", "cambio"],
      "blk", kind="beforeafter", photos=["h-fitness-05", "h-fitness-03"], l1="DÍA 1", l2="DÍA 90", text="MI CAMBIO"),
    T(26, "mini-ba-foto", "Edición antes y después", "Edit before/after", ["antes y después", "edición", "foto"], "pur",
      kind="beforeafter", photos=["h-nature-02", "h-nature-04"], l1="SIN EDITAR", l2="EDITADA", text="1 CLIC"),
    # numbers (8)
    T(27, "mini-num-top5", "Top 5", "Top 5", ["top 5", "ranking", "lista"], "yel", kind="number", face="h-man-05",
      number="TOP 5", nsize=330, text="LUGARES"),
    T(28, "mini-num-dinero", "Gané $1.000", "I made $1,000", ["dinero", "negocio", "reto"], "grn", kind="number",
      face="h-portrait-01", number="$1.000", nsize=330, text="EN 1 SEMANA"),
    T(29, "mini-num-dias", "30 días", "30 days", ["30 días", "reto", "hábito"], "cya", kind="number", face="h-man-01",
      number="30 DÍAS", nsize=300, text="SIN AZÚCAR"),
    T(30, "mini-num-horas", "24 horas", "24 hours", ["24 horas", "reto", "experimento"], "blk", kind="number",
      face="h-portrait-03", number="24 H", nsize=420, text="SIN CELULAR"),
    T(31, "mini-num-kg", "-10 kg", "-10 kg", ["kilos", "fitness", "cambio"], "lim", kind="number", face="h-man-02",
      number="-10 KG", nsize=360, text="ASÍ LO HICE"),
    T(32, "mini-num-trucos", "7 trucos", "7 tricks", ["trucos", "consejos", "hogar"], "org", kind="number",
      face="h-portrait-06", number="7", nsize=620, text="TRUCOS DE COCINA"),
    T(33, "mini-num-precio", "Todo por $10", "Everything for $10", ["barato", "compras", "reto"], "pnk", kind="number",
      face="h-portrait-04", number="$10", nsize=460, text="CENA PARA 4"),
    T(34, "mini-num-anio", "Mi año en números", "My year in numbers", ["resumen", "año", "números"], "nvy",
      kind="number", face="h-man-04", number="2026", nsize=400, text="EN NÚMEROS"),
    # reaction (5)
    T(35, "mini-reaccion-sorpresa", "Reacción sorpresa", "Surprised reaction", ["reacción", "sorpresa", "wow"], "pur",
      kind="reaction", bgphoto="h-concert-02", dim=0.3, face="h-portrait-05", emoji="😱", text="NO ME LO ESPERABA"),
    T(36, "mini-reaccion-comida", "Probando comida", "Food reaction", ["comida", "reacción", "probando"], "org",
      kind="reaction", bgphoto="h-food-01", dim=0.2, face="h-man-03", emoji="🤤", text="LO MEJOR QUE PROBÉ"),
    T(37, "mini-reaccion-viaje", "Reacción de viaje", "Travel reaction", ["viaje", "reacción", "lugar"], "cya",
      kind="reaction", bgphoto="h-nature-01", dim=0.2, face="h-portrait-02", emoji="😍", text="¿ESTO ES REAL?"),
    T(38, "mini-reaccion-gaming", "Reacción gaming", "Gaming reaction", ["gaming", "reacción", "partida"], "blk",
      kind="reaction", bgphoto="h-gaming-01", dim=0.3, face="h-man-05", emoji="🔥", text="PARTIDA ÉPICA",
      circle=(700, 330)),
    T(39, "mini-reaccion-casa", "Reacción a la casa", "House reaction", ["casa", "tour", "reacción"], "grn",
      kind="reaction", bgphoto="h-house-02", dim=0.2, face="h-portrait-06", emoji="🤯", text="MI CASA NUEVA"),
    # lists (5)
    T(40, "mini-lista-ideas", "5 ideas", "5 ideas", ["ideas", "lista", "inspiración"], "yel", kind="list", number="5",
      text="IDEAS DE NEGOCIO", photos=["h-shop-02", "h-cafe-05", "h-desk-02"]),
    T(41, "mini-lista-recetas", "3 recetas", "3 recipes", ["recetas", "cocina", "fácil"], "org", kind="list",
      number="3", text="RECETAS EN 10 MIN", photos=["h-food-02", "h-food-06", "h-cooking-03"]),
    T(42, "mini-lista-lugares", "10 lugares", "10 places", ["viaje", "lugares", "lista"], "cya", kind="list",
      number="10", nsize=400, text="LUGARES PARA IR", photos=["h-travel-06", "h-beach-04", "h-city-06"]),
    T(43, "mini-lista-hacks", "Trucos de casa", "Home hacks", ["trucos", "hogar", "limpieza"], "lim", kind="list",
      number="8", text="TRUCOS DE CASA", photos=["h-interior-01", "h-interior-03", "h-kids-05"]),
    T(44, "mini-lista-apps", "Herramientas", "Tools", ["herramientas", "productividad", "trabajo"], "nvy", kind="list",
      number="6", text="HERRAMIENTAS GRATIS", photos=["h-desk-03", "h-desk-05", "h-office-01"]),
    # question / new (5)
    T(45, "mini-pregunta-por-que", "¿Por qué?", "Why?", ["pregunta", "explicación", "curiosidad"], "pur",
      kind="question", face="h-portrait-03", text="¿POR QUÉ NADIE HABLA DE ESTO?", size=150),
    T(46, "mini-pregunta-como", "¿Cómo lo hizo?", "How?", ["pregunta", "cómo", "tutorial"], "blk", kind="question",
      face="h-man-01", text="¿CÓMO LO HIZO?", size=190),
    T(47, "mini-nuevo-episodio", "Nuevo episodio", "New episode", ["nuevo", "episodio", "podcast"], "nvy",
      bgphoto="h-podcast-03", dim=0.35, face="h-man-04", text="EP. 25", text2="con Ana Ruiz", size=280, badge="NUEVO",
      side="left"),
    T(48, "mini-nuevo-producto", "Producto nuevo", "New product", ["nuevo", "producto", "reseña"], "pnk",
      bgphoto="h-product-01", dim=0.15, face="h-portrait-01", text="¿FUNCIONA?", size=230, badge="NUEVO", side="left"),
    T(49, "mini-directo", "Directo hoy", "Live today", ["directo", "en vivo", "stream"], "blk", bgphoto="h-gaming-05",
      dim=0.4, face="h-man-02", text="EN VIVO", text2="HOY 20:00", size=280, badge="● LIVE", boxed=True),
]

TEMPLATES = [_maker(thumb, s, __name__) for s in SPECS]
