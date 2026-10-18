"""The kits of the Stock home (`colecciones.json`): one shelf per theme with templates, music, sounds, stickers,
overlays, backgrounds and looks that go together.

    py tools/stock_kits/kits.py [--check]

Writes tienda/plantillas/publicar/colecciones.json (the server reads it next to the templates index and shows each
kit as a shelf; a kit with `from`/`to`, MM-DD, only inside those dates, wrapping the new year). Every item must exist
in the published indexes or, for templates not published yet, in tools/scene_templates; `--check` only validates.
Names are in the 15 languages of Stock: the server picks `names[lang]`, then English.

Kits are for the whole world: no national holidays, and no Halloween (Jorge, 2026-10-16).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLICAR = Path(os.environ.get("FLIP_STOCK_PUBLICAR",
                               Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda" / "plantillas" / "publicar"))
DIRS = {"template": "", "animation": "animaciones", "overlay": "superposiciones", "background": "fondos",
        "sound": "sonidos", "music": "musica", "lut": "luts", "look": "looks", "text-style": "estilos-texto",
        "text-animation": "textos-animados", "transition": "transiciones", "shape": "formas"}
LANGS = ["es", "en", "ar", "bn", "fr", "it", "ja", "ko", "pl", "pt", "ru", "si", "tl", "vi", "zh"]


def names(*values: str) -> dict:
    assert len(values) == len(LANGS), values
    return dict(zip(LANGS, values))


def kit(id: str, order: int, name: dict, items: list[str], date: tuple[str, str] | None = None) -> dict:
    out = {"id": id, "names": name, "items": items, "order": order}
    if date:
        out["from"], out["to"] = date
    return out


KITS = [
    # --- By date (shown only around it) -------------------------------------------------------------------------
    kit("kit-anio-nuevo", 5, names(
        "Kit de Año Nuevo", "New Year kit", "عُدّة رأس السنة", "নববর্ষ কিট", "Kit Nouvel An", "Kit di Capodanno",
        "お正月キット", "새해 키트", "Zestaw noworoczny", "Kit de Ano-Novo", "Новогодний набор", "අලුත් අවුරුදු කට්ටලය",
        "Kit sa Bagong Taon", "Bộ Năm Mới", "新年套装"), [
        "template:anio-nuevo-cuenta-regresiva", "template:h-fecha-anio-nuevo", "template:s-anio-nuevo-brindis",
        "template:h-cuenta-anio-nuevo", "template:mi-2026-en-fotos", "template:propositos-2027", "template:st-anio-nuevo",
        "animation:copas-brindis", "animation:fuegos-artificiales", "animation:reloj-medianoche",
        "overlay:cel-fuegos-artificiales", "overlay:cel-confeti-dorado", "background:anio-nuevo",
        "music:fireworks-30s", "music:auld-lang-syne-lo-fi-30s", "sound:cuenta-regresiva", "lut:est-ano-nuevo",
        "text-style:fec-anio-nuevo"], ("12-20", "01-07")),
    kit("kit-navidad", 10, names(
        "Kit de Navidad", "Christmas kit", "عُدّة عيد الميلاد", "বড়দিন কিট", "Kit de Noël", "Kit di Natale",
        "クリスマスキット", "크리스마스 키트", "Zestaw świąteczny", "Kit de Natal", "Рождественский набор",
        "නත්තල් කට්ටලය", "Kit sa Pasko", "Bộ Giáng Sinh", "圣诞套装"), [
        "template:feliz-navidad-luces", "template:navidad-en-familia", "template:navidad-regalo-sorpresa",
        "template:menu-navideno", "template:r-navidad-minimal", "template:h-fecha-navidad",
        "animation:arbol-navidad", "animation:gorro-santa", "animation:esfera-navidad", "animation:campanas-navidad",
        "overlay:luz-luces-navidad", "overlay:part-nieve-brillante", "background:navidad", "background:navidad-2"],
        ("12-01", "12-26")),
    kit("kit-black-friday", 20, names(
        "Kit de Black Friday", "Black Friday kit", "عُدّة الجمعة السوداء", "ব্ল্যাক ফ্রাইডে কিট", "Kit Black Friday",
        "Kit Black Friday", "ブラックフライデーキット", "블랙 프라이데이 키트", "Zestaw Black Friday", "Kit de Black Friday",
        "Набор «Чёрная пятница»", "බ්ලැක් ෆ්‍රයිඩේ කට්ටලය", "Kit sa Black Friday", "Bộ Black Friday", "黑色星期五套装"), [
        "template:black-friday-ofertas", "template:black-friday-ultimas-horas", "template:cyber-monday",
        "template:cupon-de-descuento", "template:oferta-flash", "template:yt-mini-precio-tachado",
        "template:cont-precio-baja", "animation:porcentaje-oferta", "animation:sello-oferta",
        "animation:etiqueta-precio", "sound:caja-registradora", "sound:venta-hecha"], ("11-15", "12-01")),
    kit("kit-amor", 40, names(
        "Kit de San Valentín", "Valentine's kit", "عُدّة عيد الحب", "ভ্যালেন্টাইন কিট", "Kit Saint-Valentin",
        "Kit di San Valentino", "バレンタインキット", "밸런타인 키트", "Zestaw walentynkowy", "Kit de Dia dos Namorados",
        "Набор ко Дню святого Валентина", "වැලන්ටයින් කට්ටලය", "Kit sa Araw ng mga Puso", "Bộ Valentine", "情人节套装"), [
        "template:san-valentin-carta", "template:r-san-valentin-divertido", "template:h-fecha-san-valentin",
        "template:aniversario-pareja", "template:r-primera-cita", "template:cont-dias-juntos",
        "animation:corazones", "animation:corazon-flechado", "animation:carta-amor", "animation:cara-enamorada",
        "overlay:amor-corazones", "overlay:amor-petalos", "background:san-valentin",
        "music:lovely-piano-song-30s", "music:romantic-inspiration-30s"], ("02-01", "02-14")),
    kit("kit-dia-madre", 50, names(
        "Kit del Día de la Madre", "Mother's Day kit", "عُدّة عيد الأم", "মা দিবস কিট", "Kit Fête des mères",
        "Kit Festa della mamma", "母の日キット", "어머니의 날 키트", "Zestaw na Dzień Matki", "Kit de Dia das Mães",
        "Набор ко Дню матери", "මව්වරුන්ගේ දින කට්ටලය", "Kit sa Araw ng mga Ina", "Bộ Ngày của Mẹ", "母亲节套装"), [
        "template:para-mama", "template:r-cumple-mama", "template:h-fecha-dia-madre", "template:r-dia-madre-floral",
        "animation:corazones", "overlay:amor-petalos-rosa", "music:lovely-piano-song-30s"], ("04-25", "05-14")),
    kit("kit-graduacion", 55, names(
        "Kit de graduación", "Graduation kit", "عُدّة التخرّج", "স্নাতক কিট", "Kit remise des diplômes",
        "Kit di laurea", "卒業キット", "졸업 키트", "Zestaw na zakończenie szkoły", "Kit de formatura",
        "Выпускной набор", "උපාධි ප්‍රදාන කට්ටලය", "Kit sa Pagtatapos", "Bộ Tốt nghiệp", "毕业套装"), [
        "template:h-cele-graduacion", "template:r-graduacion-universidad", "template:r-graduacion-kinder",
        "template:s-evento-graduacion", "template:s-graduacion-collage", "animation:birrete",
        "overlay:cel-estrellas-doradas", "overlay:cel-explosion-dorada", "background:graduacion",
        "music:pump-up-your-graduation-30s", "sound:fanfarria-victoria", "text-style:fec-graduacion"],
        ("05-20", "07-10")),
    kit("kit-dia-padre", 57, names(
        "Kit del Día del Padre", "Father's Day kit", "عُدّة عيد الأب", "বাবা দিবস কিট", "Kit Fête des pères",
        "Kit Festa del papà", "父の日キット", "아버지의 날 키트", "Zestaw na Dzień Ojca", "Kit de Dia dos Pais",
        "Набор ко Дню отца", "පියවරුන්ගේ දින කට්ටලය", "Kit sa Araw ng mga Ama", "Bộ Ngày của Cha", "父亲节套装"), [
        "template:dia-del-padre", "template:h-fecha-dia-padre", "template:r-papa-hijo",
        "template:r-dia-padre-deportivo", "template:s-dia-padre", "text-style:fec-dia-padre",
        "overlay:cam-flash", "sound:foto-flash"], ("06-01", "06-21")),
    kit("kit-verano", 58, names(
        "Kit de verano", "Summer kit", "عُدّة الصيف", "গ্রীষ্ম কিট", "Kit d'été", "Kit estate", "夏キット",
        "여름 키트", "Zestaw letni", "Kit de verão", "Летний набор", "ගිම්හාන කට්ටලය", "Kit sa Tag-init",
        "Bộ Mùa hè", "夏日套装"), [
        "template:h-fecha-verano", "template:r-verano", "template:s-verano", "template:r-recuerdo-verano",
        "template:dia-de-playa", "animation:sol", "animation:olas", "animation:cara-lentes",
        "overlay:luz-sol", "overlay:luz-rayos", "background:atardecer-vibrante", "transition:rayos-de-sol",
        "music:summer-break-30s", "music:funshine-30s", "look:verano-tropical", "lut:ver-playa"], ("06-15", "08-31")),
    kit("kit-vuelta-clases", 59, names(
        "Kit de vuelta a clases", "Back to school kit", "عُدّة العودة إلى المدرسة", "স্কুলে ফেরা কিট",
        "Kit rentrée scolaire", "Kit ritorno a scuola", "新学期キット", "개학 키트", "Zestaw na powrót do szkoły",
        "Kit de volta às aulas", "Набор «Снова в школу»", "නැවත පාසලට කට්ටලය", "Kit sa Balik-eskwela",
        "Bộ Tựu trường", "开学套装"), [
        "template:h-fecha-regreso-clases", "template:r-regreso-clases", "template:s-regreso-clases",
        "template:h-presenta-escuela", "template:yt-dia-estudio", "template:yt-expl-pizarra",
        "background:pizarra-frio", "text-style:inf-tiza-colores", "text-style:tit-resaltador",
        "music:from-page-to-practice-30s"], ("08-10", "09-15")),

    # --- For creators --------------------------------------------------------------------------------------------
    kit("kit-youtuber-principiante", 100, names(
        "Kit para empezar en YouTube", "YouTube starter kit", "عُدّة البداية على يوتيوب", "ইউটিউব শুরুর কিট",
        "Kit pour débuter sur YouTube", "Kit per iniziare su YouTube", "YouTube 入門キット", "유튜브 입문 키트",
        "Zestaw na start na YouTube", "Kit para começar no YouTube", "Набор для старта на YouTube",
        "YouTube ආරම්භක කට්ටලය", "Kit pang-umpisa sa YouTube", "Bộ khởi đầu YouTube", "YouTube 入门套装"), [
        "template:yt-intro-minimal", "template:yt-final-columnas", "template:yt-mini-flecha-circulo",
        "template:yt-sub-amarillo", "template:yt-final-short-sigueme", "template:redes-h-todas-fila",
        "overlay:yt-suscribete-clasico-es", "overlay:yt-subscribe-classic-en", "overlay:yt-like-pop", "overlay:yt-campana", "overlay:yt-flecha-roja",
        "sound:suscribir-campana", "sound:barrido-camara", "sound:ding-idea", "transition:latigazo-giro-derecha",
        "text-style:sub-youtuber"]),
    kit("kit-mi-canal", 105, names(
        "Kit de identidad del canal", "Channel branding kit", "عُدّة هوية القناة", "চ্যানেল পরিচিতি কিট",
        "Kit d'identité de chaîne", "Kit identità del canale", "チャンネルブランディングキット", "채널 브랜딩 키트",
        "Zestaw identyfikacji kanału", "Kit de identidade do canal", "Набор оформления канала",
        "නාලිකා අනන්‍යතා කට්ටලය", "Kit pang-branding ng channel", "Bộ nhận diện kênh", "频道品牌套装"), [
        "template:yt-intro-neon", "template:yt-intro-liquido", "template:yt-intro-papel", "template:yt-final-neon",
        "template:yt-final-minimal-uno", "template:yt-final-short-perfil", "template:redes-v-todas-cristal",
        "template:redes-h-instagram-minimal", "template:redes-h-tiktok-neon", "overlay:facecam-circulo-neon",
        "overlay:facecam-placa-nombre", "overlay:yt-notificacion", "sound:intro-golpe", "sound:cierre-video"]),
    kit("kit-reto", 110, names(
        "Kit de retos extremos", "Extreme challenge kit", "عُدّة التحديات القصوى", "চরম চ্যালেঞ্জ কিট",
        "Kit défis extrêmes", "Kit sfide estreme", "過激チャレンジキット", "극한 챌린지 키트", "Zestaw ekstremalnych wyzwań",
        "Kit de desafios extremos", "Набор экстремальных челленджей", "අන්ත අභියෝග කට්ටලය", "Kit ng matinding hamon",
        "Bộ thử thách cực đại", "极限挑战套装"), [
        "template:yt-reto-1-vs-millon", "template:yt-reto-ultimo-en-salir", "template:yt-reto-dia-1-dia-100",
        "template:yt-reto-eliminados", "template:yt-reto-caja-misteriosa", "template:yt-reto-ganador",
        "template:cont-dinero-millon", "animation:trofeo", "animation:lluvia-dinero", "overlay:cel-lluvia-monedas",
        "sound:redoble-largo", "sound:boom-808", "sound:premio-mayor", "music:fanfare-x-15s",
        "music:action-strike-15s", "transition:zoom-saltos", "text-style:d3-dorado"]),
    kit("kit-top-10", 112, names(
        "Kit de rankings y top 10", "Rankings and top 10 kit", "عُدّة التصنيفات وأفضل 10", "র‍্যাংকিং ও টপ ১০ কিট",
        "Kit classements et top 10", "Kit classifiche e top 10", "ランキング・トップ10キット", "랭킹·톱 10 키트",
        "Zestaw rankingów i top 10", "Kit de rankings e top 10", "Набор рейтингов и топ-10", "ශ්‍රේණිගත කිරීම් සහ ටොප් 10 කට්ටලය",
        "Kit ng ranking at top 10", "Bộ xếp hạng và top 10", "排行榜与十大套装"), [
        "template:yt-top-10-rapido", "template:yt-top-3-podio", "template:yt-top-5-tarjetas",
        "template:yt-top-3-revelacion", "template:yt-top-10-intro", "template:yt-top-5-peor-a-mejor",
        "template:yt-mini-tier-list", "animation:podio", "animation:medalla", "sound:redoble-corto",
        "sound:titulo-golpe", "sound:fanfarria-victoria", "music:final-level-30s"]),
    kit("kit-podcast", 115, names(
        "Kit de podcast", "Podcast kit", "عُدّة البودكاست", "পডকাস্ট কিট", "Kit podcast", "Kit podcast",
        "ポッドキャストキット", "팟캐스트 키트", "Zestaw podcastowy", "Kit de podcast", "Набор для подкаста",
        "පොඩ්කාස්ට් කට්ටලය", "Kit sa podcast", "Bộ podcast", "播客套装"), [
        "template:yt-pod-dos-camaras", "template:yt-pod-audiograma", "template:yt-pod-titulo-episodio",
        "template:yt-pod-invitado", "template:yt-pod-cita", "template:yt-pod-clip-subtitulos",
        "template:yt-sub-podcast-h", "overlay:facecam-estudio", "overlay:facecam-placa-nombre",
        "animation:microfono", "background:ecualizador-oscuro", "text-style:sub-podcast",
        "text-style:ter-entrevista", "music:hear-what-they-say-30s", "music:slice-of-life-30s"]),
    kit("kit-reaccion", 117, names(
        "Kit de reacciones y entrevistas", "Reactions and interviews kit", "عُدّة ردود الفعل والمقابلات",
        "রিঅ্যাকশন ও সাক্ষাৎকার কিট", "Kit réactions et interviews", "Kit reaction e interviste",
        "リアクション・インタビューキット", "리액션·인터뷰 키트", "Zestaw reakcji i wywiadów", "Kit de reações e entrevistas",
        "Набор реакций и интервью", "ප්‍රතිචාර සහ සම්මුඛ සාකච්ඡා කට්ටලය", "Kit ng reaksyon at panayam",
        "Bộ reaction và phỏng vấn", "反应与街访套装"), [
        "template:yt-reac-esquina-h", "template:yt-reac-espera", "template:yt-reac-zoom-cara",
        "template:yt-reac-dueto", "template:yt-calle-que-opinas", "template:yt-calle-mic-grande",
        "template:yt-calle-trivia", "template:yt-sub-gancho", "overlay:yt-emoji-risa", "overlay:yt-emoji-sorpresa",
        "overlay:facecam-circulo-blanco", "sound:asombro", "sound:sorpresa", "sound:womp-womp",
        "transition:zoom-saltos-atras", "text-style:sub-emoji-pop"]),
    kit("kit-gaming", 120, names(
        "Kit gamer", "Gaming kit", "عُدّة الألعاب", "গেমিং কিট", "Kit gaming", "Kit gaming", "ゲーム実況キット",
        "게이밍 키트", "Zestaw gamingowy", "Kit gamer", "Игровой набор", "ගේමින් කට්ටලය", "Kit sa gaming",
        "Bộ gaming", "游戏主播套装"), [
        "template:yt-game-overlay-neon", "template:yt-game-alerta-sub", "template:yt-game-empezamos",
        "template:yt-game-vuelvo", "template:yt-game-victoria", "template:yt-game-gg", "template:yt-intro-gaming",
        "template:redes-h-twitch-neon", "overlay:facecam-gamer-neon", "overlay:facecam-gamer-rgb",
        "background:neon-oscuro", "transition:pixelado-rapido", "transition:glitch-neon", "sound:explosion-8bits",
        "sound:subir-nivel-moderno", "music:final-level-30s", "text-style:ret-arcade-neon", "look:vibrante-videojuego"]),
    kit("kit-cocina", 125, names(
        "Kit de cocina", "Cooking kit", "عُدّة الطبخ", "রান্নার কিট", "Kit cuisine", "Kit cucina", "料理キット",
        "요리 키트", "Zestaw kulinarny", "Kit de culinária", "Кулинарный набор", "ආහාර පිසීමේ කට්ටලය",
        "Kit sa pagluluto", "Bộ nấu ăn", "美食烹饪套装"), [
        "template:yt-coc-ingredientes-lista", "template:yt-coc-pasos", "template:yt-coc-temporizador",
        "template:yt-coc-plato-final", "template:yt-coc-receta-card", "template:yt-coc-receta-60s",
        "template:yt-coc-cierre", "animation:cafe-humeante", "animation:pizza", "sound:sarten", "sound:timbre-mostrador",
        "look:comida-apetitosa", "lut:com-cocina-luminosa", "music:morning-coffee-15s", "music:happy-whistling-ukulele-30s"]),
    kit("kit-fitness", 130, names(
        "Kit fitness", "Fitness kit", "عُدّة اللياقة", "ফিটনেস কিট", "Kit fitness", "Kit fitness", "フィットネスキット",
        "피트니스 키트", "Zestaw fitness", "Kit fitness", "Фитнес-набор", "යෝග්‍යතා කට්ටලය", "Kit sa fitness",
        "Bộ thể hình", "健身套装"), [
        "template:yt-fit-contador-reps", "template:yt-fit-tabata", "template:yt-fit-antes-despues-kilos",
        "template:yt-fit-plan-semanal", "template:yt-fit-reto-30-dias", "template:yt-fit-record-personal",
        "template:yt-fit-rutina-en-casa", "template:cont-pasos", "animation:pesas", "animation:silbato",
        "sound:cuenta-regresiva-rapida", "sound:check-tilde", "music:city-run-15s", "music:hit-n-smash-15s",
        "text-style:gam-deportivo"]),
    kit("kit-tecnologia", 135, names(
        "Kit de tecnología", "Tech review kit", "عُدّة مراجعات التقنية", "প্রযুক্তি রিভিউ কিট", "Kit tech",
        "Kit tecnologia", "ガジェットレビューキット", "테크 리뷰 키트", "Zestaw technologiczny", "Kit de tecnologia",
        "Набор техно-обзоров", "තාක්ෂණ සමාලෝචන කට්ටලය", "Kit sa tech review", "Bộ review công nghệ", "科技测评套装"), [
        "template:yt-tec-unboxing", "template:yt-tec-ficha-tecnica", "template:yt-tec-comparacion",
        "template:yt-tec-pros-contras", "template:yt-tec-puntaje", "template:yt-tec-veredicto",
        "template:yt-intro-tech", "background:circuito-oscuro", "overlay:facecam-hexagono-tech", "overlay:luz-escaner",
        "transition:glitch-golpe-rgb", "sound:glitch-digital", "sound:barra-carga", "music:circuit-30s",
        "text-style:tit-rgb"]),
    kit("kit-vlog", 140, names(
        "Kit de vlog", "Vlog kit", "عُدّة الفلوغ", "ভ্লগ কিট", "Kit vlog", "Kit vlog", "Vlog キット", "브이로그 키트",
        "Zestaw vlogowy", "Kit de vlog", "Набор для влога", "ව්ලොග් කට්ටලය", "Kit sa vlog", "Bộ vlog", "Vlog 套装"), [
        "template:yt-vlog-titulo-calle", "template:yt-vlog-ruta-mapa", "template:yt-vlog-dia-1",
        "template:yt-vlog-hora-lugar", "template:yt-dia-0630", "template:yt-dia-checklist", "template:yt-dia-grwm-pasos",
        "template:yt-dia-cozy", "overlay:luz-sol", "sound:titulo-desliza", "sound:barrido-camara-doble",
        "transition:deslizar-historia", "music:city-sunshine-30s", "music:be-chillin-30s", "look:verano-dorado"]),
    kit("kit-viajes", 145, names(
        "Kit de viajes", "Travel kit", "عُدّة السفر", "ভ্রমণ কিট", "Kit voyage", "Kit viaggi", "旅行キット",
        "여행 키트", "Zestaw podróżniczy", "Kit de viagem", "Набор для путешествий", "සංචාරක කට්ටලය",
        "Kit sa paglalakbay", "Bộ du lịch", "旅行套装"), [
        "template:vlog-de-viaje", "template:h-intro-viajes-mapa", "template:h-presenta-viaje",
        "template:r-dump-viaje-mapa", "template:h-final-viajes", "template:r-cuenta-vacaciones",
        "template:yt-vlog-billete", "template:yt-vlog-postal", "template:yt-vlog-stats-viaje",
        "animation:avion-papel", "music:trip-up-north-30s", "music:day-trips-30s"]),
    kit("kit-explicador", 150, names(
        "Kit de videos explicativos", "Explainer kit", "عُدّة الفيديوهات التوضيحية", "ব্যাখ্যামূলক ভিডিও কিট",
        "Kit vidéos explicatives", "Kit video esplicativi", "解説動画キット", "설명 영상 키트", "Zestaw filmów objaśniających",
        "Kit de vídeos explicativos", "Набор для объясняющих видео", "පැහැදිලි කිරීමේ වීඩියෝ කට්ටලය",
        "Kit sa video na nagpapaliwanag", "Bộ video giải thích", "科普讲解套装"), [
        "template:yt-expl-por-que", "template:yt-expl-resaltador", "template:yt-expl-recortes",
        "template:yt-expl-datos", "template:yt-expl-barras", "template:yt-expl-linea-tiempo",
        "template:yt-expl-mito", "template:yt-expl-capitulos", "sound:marcador", "sound:pensando",
        "text-style:tit-resaltador", "music:from-page-to-practice-15s"]),
    kit("kit-misterio", 155, names(
        "Kit de misterio y true crime", "Mystery and true crime kit", "عُدّة الغموض والجرائم الحقيقية",
        "রহস্য ও সত্য অপরাধ কিট", "Kit mystère et true crime", "Kit mistero e true crime", "ミステリー・事件キット",
        "미스터리·실화 범죄 키트", "Zestaw zagadek i true crime", "Kit de mistério e true crime",
        "Набор тайн и тру-крайма", "අභිරහස් සහ සැබෑ අපරාධ කට්ටලය", "Kit ng misteryo at true crime",
        "Bộ bí ẩn và true crime", "悬疑与真实罪案套装"), [
        "template:yt-mist-expediente", "template:yt-mist-tablero", "template:yt-mist-maquina",
        "template:yt-mist-censurado", "template:yt-mist-linea-tiempo", "template:yt-mist-sin-resolver",
        "template:yt-mist-camara", "overlay:clima-niebla", "overlay:cam-vision-nocturna",
        "sound:acento-tension", "sound:dron-oscuro", "music:hidden-truth-15s", "music:cursed-intro-15s",
        "lut:cine-misterio", "text-style:mie-expediente", "text-animation:bor-fantasma"]),

    # --- For business ----------------------------------------------------------------------------------------------
    kit("kit-negocio", 200, names(
        "Kit para tu negocio", "Small business kit", "عُدّة لمشروعك", "আপনার ব্যবসার কিট", "Kit petite entreprise",
        "Kit per la tua attività", "スモールビジネスキット", "소상공인 키트", "Zestaw dla firmy", "Kit para o seu negócio",
        "Набор для бизнеса", "ඔබේ ව්‍යාපාරයට කට්ටලය", "Kit para sa negosyo", "Bộ cho cửa hàng", "小生意套装"), [
        "template:gran-inauguracion", "template:oferta-flash", "template:h-neg-rebajas", "template:r-envio-gratis",
        "template:horario-de-atencion", "template:delivery-pide-por-whatsapp", "template:testimonio-cliente-estrellas",
        "animation:etiqueta-precio", "animation:sello-oferta", "animation:porcentaje-oferta",
        "sound:caja-registradora"]),
    kit("kit-lanzamiento", 205, names(
        "Kit de lanzamiento de producto", "Product launch kit", "عُدّة إطلاق المنتج", "পণ্য লঞ্চ কিট",
        "Kit lancement de produit", "Kit lancio di prodotto", "新商品ローンチキット", "제품 출시 키트",
        "Zestaw premiery produktu", "Kit de lançamento de produto", "Набор для запуска продукта",
        "නිෂ්පාදන දියත් කිරීමේ කට්ටලය", "Kit sa paglulunsad ng produkto", "Bộ ra mắt sản phẩm", "新品发布套装"), [
        "template:h-neg-lanzamiento", "template:lanzamiento-ya-disponible", "template:h-cuenta-lanzamiento",
        "template:r-unboxing", "template:s-split-producto", "template:yt-tec-etiqueta-precio",
        "template:yt-tec-unboxing-vertical", "animation:cohete", "overlay:part-destellos-grandes",
        "sound:subida-corta-golpe", "sound:zoom-dramatico", "transition:alejar-revelar", "music:screen-saver-30s"]),
    kit("kit-inmobiliaria", 210, names(
        "Kit inmobiliario", "Real estate kit", "عُدّة العقارات", "রিয়েল এস্টেট কিট", "Kit immobilier",
        "Kit immobiliare", "不動産キット", "부동산 키트", "Zestaw nieruchomości", "Kit imobiliário",
        "Набор для недвижимости", "දේපළ වෙළඳාම් කට්ටලය", "Kit sa real estate", "Bộ bất động sản", "房产中介套装"), [
        "template:h-neg-inmobiliaria", "template:r-casa-venta", "template:s-carrusel-casa", "template:tour-inmobiliario",
        "template:r-ba-casa", "template:ad-h-inmobiliaria", "template:ad-v-inmobiliaria",
        "music:studio-apartment-30s", "music:laundry-on-the-wire-30s"]),
    kit("kit-cursos", 215, names(
        "Kit de clases y cursos", "Classes and courses kit", "عُدّة الدروس والدورات", "ক্লাস ও কোর্স কিট",
        "Kit cours et formations", "Kit lezioni e corsi", "講座・レッスンキット", "강의·강좌 키트", "Zestaw lekcji i kursów",
        "Kit de aulas e cursos", "Набор для уроков и курсов", "පන්ති සහ පාඨමාලා කට්ටලය", "Kit sa klase at kurso",
        "Bộ bài giảng và khóa học", "课程教学套装"), [
        "template:yt-intro-educacion", "template:h-texto-lecciones", "template:h-final-curso",
        "template:portada-de-tutorial", "template:h-tercio-tutorial-paso", "template:yt-sub-tutorial-h",
        "template:yt-expl-proceso", "overlay:yt-cursor-clic", "overlay:cam-grabando-pantalla",
        "background:pizarra-oscuro", "sound:clic-raton", "music:from-page-to-practice-30s"]),

    # --- Always on ---------------------------------------------------------------------------------------------------
    kit("kit-cumple", 300, names(
        "Kit de cumpleaños", "Birthday kit", "عُدّة عيد الميلاد", "জন্মদিন কিট", "Kit d'anniversaire",
        "Kit di compleanno", "誕生日キット", "생일 키트", "Zestaw urodzinowy", "Kit de aniversário", "Набор ко дню рождения",
        "උපන්දින කට්ටලය", "Kit sa kaarawan", "Bộ sinh nhật", "生日套装"), [
        "template:feliz-cumple", "template:cumple-sorpresa", "template:r-cumple-ritmo", "template:r-pastel-velas",
        "template:h-cele-cumple", "template:cont-edad-cumple", "animation:confeti", "animation:globos",
        "animation:pastel-velas", "animation:gorro-fiesta", "overlay:cel-confeti", "overlay:cel-globos",
        "background:cumpleanos"]),
    kit("kit-boda", 305, names(
        "Kit de boda", "Wedding kit", "عُدّة الزفاف", "বিয়ের কিট", "Kit de mariage", "Kit di nozze", "ウェディングキット",
        "웨딩 키트", "Zestaw ślubny", "Kit de casamento", "Свадебный набор", "විවාහ කට්ටලය", "Kit sa kasal",
        "Bộ đám cưới", "婚礼套装"), [
        "template:boda-save-the-date", "template:resumen-de-boda", "template:r-boda-votos",
        "template:r-boda-primer-baile", "template:h-intro-boda", "template:h-presenta-boda", "template:r-cuenta-boda",
        "animation:anillos-boda", "overlay:amor-petalos-blancos", "sound:campanas-boda",
        "music:a-waltz-for-naseem-30s"]),
]


def known_refs() -> set[str]:
    refs = set()
    for typ, folder in DIRS.items():
        index = PUBLICAR / folder / "index.json"
        if index.exists():
            refs |= {f"{typ}:{t['id']}" for t in json.loads(index.read_text(encoding="utf-8"))["templates"]}
    # Templates written but not published yet.
    sys.path.insert(0, str(HERE.parent / "scene_templates"))
    import templates  # noqa: E402
    refs |= {f"template:{make().id}" for make in templates.TEMPLATES}
    return refs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    refs = known_refs()
    problems = []
    ids = set()
    for k in KITS:
        if k["id"] in ids:
            problems.append(f"{k['id']}: repeated id")
        ids.add(k["id"])
        problems += [f"{k['id']}: {ref} does not exist" for ref in k["items"] if ref not in refs]
        if len(set(k["items"])) != len(k["items"]):
            problems.append(f"{k['id']}: repeated item")
    for p in problems:
        print(p)
    if problems:
        return 1
    print(f"{len(KITS)} kits, {sum(len(k['items']) for k in KITS)} items")
    if not args.check:
        out = PUBLICAR / "colecciones.json"
        out.write_text(json.dumps({"collections": KITS}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
