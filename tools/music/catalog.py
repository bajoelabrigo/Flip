"""The catalogue of Stock › Música: which song, which mood, which lengths.

Each line of SONGS is `source key | category | lengths | tags`, where the lengths are 15/30/60 (the first one is
the main cut; the others are extra cuts of the same song) and the tags are extra search words (genre,
instruments, uses), "es/en" pairs separated by commas. Optional fields after the tags: `meter=3`, `start=42.0`
(do not start before that second), `intro=1.0` (bonus for starting at the very beginning), `name=...`.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

# Order of the categories in the app's filter.
CATEGORIES = {
    "alegre": {"es": "Alegre", "en": "Happy"},
    "energetico": {"es": "Energética y deportes", "en": "Energetic and sports"},
    "epico": {"es": "Épica y cine", "en": "Epic and cinematic"},
    "tranquilo": {"es": "Tranquila, lofi y estudio", "en": "Chill, lofi and study"},
    "romantico": {"es": "Romántica", "en": "Romantic"},
    "triste": {"es": "Triste y emotiva", "en": "Sad and emotional"},
    "suspenso": {"es": "Misterio y suspenso", "en": "Mystery and suspense"},
    "divertido": {"es": "Divertida y comedia", "en": "Funny and comedy"},
    "corporativo": {"es": "Corporativa y negocios", "en": "Corporate and business"},
    "infantil": {"es": "Infantil", "en": "Kids"},
    "fiesta": {"es": "Fiesta y baile", "en": "Party and dance"},
    "fechas": {"es": "Navidad y fechas", "en": "Christmas and holidays"},
    "mundo": {"es": "Del mundo", "en": "World"},
}

COLORS = {
    "alegre": ("#ffb000", "#ff5e3a"),
    "energetico": ("#ff2d55", "#7a00ff"),
    "epico": ("#2b1d0e", "#b8860b"),
    "tranquilo": ("#6a8caf", "#3d4f7a"),
    "romantico": ("#ff6f91", "#c9184a"),
    "triste": ("#3a4a63", "#1b2233"),
    "suspenso": ("#121826", "#4b1d5e"),
    "divertido": ("#ffd23f", "#ff8c42"),
    "corporativo": ("#0ea5e9", "#1e3a8a"),
    "infantil": ("#7bdff2", "#b388eb"),
    "fiesta": ("#f72585", "#3a0ca3"),
    "fechas": ("#c1121f", "#1b7a3a"),
    "mundo": ("#2a9d8f", "#e9c46a"),
}

# Search words every song of a category gets (es + en).
CATEGORY_TAGS = {
    "alegre": "alegre, feliz, positiva, optimista, buen rollo, vlog, dia a dia, happy, upbeat, positive, cheerful, sunny",
    "energetico": "energetica, deporte, gimnasio, entrenamiento, accion, motivacion, energetic, sports, workout, gym, "
                  "action, hype",
    "epico": "epica, cine, cinematografica, trailer, heroica, orquesta, epic, cinematic, trailer, heroic, orchestral, "
             "film",
    "tranquilo": "tranquila, relajante, calma, estudio, concentracion, fondo, chill, relaxing, calm, study, focus, "
                 "background",
    "romantico": "romantica, amor, pareja, boda, san valentin, romantic, love, couple, wedding, valentine",
    "triste": "triste, emotiva, nostalgia, melancolia, recuerdos, sad, emotional, nostalgic, melancholic, memories",
    "suspenso": "misterio, suspenso, tension, terror, oscuro, intriga, mystery, suspense, tension, horror, dark, "
                "thriller",
    "divertido": "divertida, comedia, humor, gracioso, meme, chistosa, funny, comedy, humor, quirky, silly",
    "corporativo": "corporativa, negocios, empresa, presentacion, publicidad, anuncio, corporate, business, "
                   "presentation, advertising, commercial",
    "infantil": "infantil, ninos, juego, dibujos, escuela, kids, children, playful, cartoon, school",
    "fiesta": "fiesta, baile, bailar, celebracion, discoteca, party, dance, celebration, club",
    "fechas": "fechas especiales, festividad, celebracion, holiday, seasonal, celebration",
    "mundo": "del mundo, cultura, viaje, tradicional, world, culture, travel, traditional",
}

LENGTH_TAGS = {
    15: "15 s, 15 segundos, corta, reel, historia, story, short",
    30: "30 s, 30 segundos, reel, tiktok, short",
    60: "60 s, 1 minuto, minuto, larga, video, one minute, long",
}


@dataclass
class Item:
    id: str
    key: str
    length: int
    category: str
    names: dict
    tags: list
    meter: int = 4
    start: float | None = None
    prefer_intro: float | None = None
    avoid: list = field(default_factory=list)


def plain(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(ch for ch in s if not unicodedata.combining(ch)).strip()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", plain(s)).strip("-")


def tempo_tags(bpm: float) -> list[str]:
    b = int(round(bpm / 5) * 5)
    out = [f"{b} bpm"]
    if bpm < 85:
        out += ["lenta", "slow"]
    elif bpm > 125:
        out += ["rapida", "fast"]
    return out


# ------------------------------------------------------------------ the songs
# key | category | lengths | tags [| options]
# key: "<folder>/<title>" for FreePD (freepd/<folder>__<title>.mp3), "fma:<album>/<title>" for the Free Music
# Archive (the first track of that album whose title starts like that).
SONGS = """
# ---------------- Alegre
upbeat/Advertime | alegre | 30,15 | pop, ukelele, ukulele, anuncio, commercial
upbeat/And Just Like That | alegre | 30,15 | pop, vlog, guitarra, guitar
upbeat/City Sunshine | alegre | 30,60,15 | pop, ciudad, city, verano, summer
upbeat/Funshine | alegre | 30,15 | pop, sol, sunshine, verano, summer
upbeat/Happy Whistling Ukulele | alegre | 30,15 | ukelele, ukulele, silbido, whistle, acustica, acoustic
upbeat/Ukulele Song | alegre | 30 | ukelele, ukulele, acustica, acoustic
upbeat/Pickled Pink | alegre | 30 | pop, divertida, fun
upbeat/Natural Vibes | alegre | 30 | acustica, acoustic, naturaleza, nature
upbeat/Inventing Flight | alegre | 30 | inspiradora, inspiring, descubrimiento
comedy/Hopeful | alegre | 30 | esperanza, hopeful, inspiradora, inspiring
unsorted/Hippety Hop | alegre | 30 | saltarina, bouncy, pop
unsorted/Favorite | alegre | 30 | pop, vlog
romantic/Lucky Break | alegre | 60 | acustica, acoustic, folk
country/Trip Up North | alegre | 30 | country, viaje, road trip, guitarra
fantasy/One Step Closer | alegre | 30 | inspiradora, inspiring, motivacion
fma:public-domain-lofi/Doodles | alegre | 30 | lofi, lo-fi, beat, hip hop
fma:public-domain-lofi/Projector Screen | alegre | 30 | lofi, lo-fi, beat, hip hop
fma:public-domain-lofi/Summer Break | alegre | 30 | lofi, lo-fi, verano, summer, vacaciones
# ---------------- Energética y deportes
epic/Hit n Smash | energetico | 30,15 | rock, accion, trailer, golpes
scoring/Action Strike | energetico | 30,15 | accion, action, persecucion, chase
scoring/City Run | energetico | 15 | correr, running, ciudad, city
unsorted/Uberpunch | energetico | 30,15 | rock, golpe, punch, pelea, fight
misc/Gotta Keep On Movin | energetico | 30,15 | rock, movimiento, viaje
comedy/Rush | energetico | 30,15 | rapida, prisa, rush, carrera, race
scoring/Funky Energy Loop | energetico | 30 | funk, groove, loop
epic/Battle Ready | energetico | 30 | batalla, battle, tambores, drums
unsorted/Beat Thee | energetico | 30 | electronica, electronic, beat
unsorted/Apex | energetico | 60 | electronica, electronic, cumbre, apex
unsorted/Horizon Flare | energetico | 30 | electronica, electronic, synth
misc/Drop Point | energetico | 30 | electronica, accion, espias
misc/Burning Trapezoid of Fire | energetico | 30 | rock, guitarra electrica, electric guitar
misc/Spec Ops | energetico | 30 | accion, militar, operaciones, ops
epic/Release the Hybrids | energetico | 30 | electronica, industrial, accion
fma:phonk-aura-farming/Phonk ish | energetico | 30,15 | phonk, drift, gimnasio, gym, trap
fma:phonk-aura-farming/Phonk Remix | energetico | 30 | phonk, drift, gimnasio, gym, trap
fma:phonk-aura-farming/Pantheon | energetico | 30 | phonk, drift, trap, aura
fma:rock-montage/Punk | energetico | 30 | punk, rock, guitarra electrica, skate
fma:rock-montage/Grunge | energetico | 30 | grunge, rock, guitarra electrica
fma:rock-montage/Jams | energetico | 30 | rock, jam, guitarra electrica
fma:gamer-beats/Hard Mode | energetico | 30 | gamer, videojuego, video game, beat
fma:gamer-beats/Final Level | energetico | 30 | gamer, videojuego, video game, beat
# ---------------- Épica y cine
epic/Adventure | epico | 60,15 | aventura, adventure, orquesta
epic/Heroic Adventure | epico | 30,60,15 | heroe, hero, aventura, adventure
epic/Epic Blockbuster 2 | epico | 30,60,15 | taquillera, blockbuster, trailer
epic/Emotional Blockbuster 2 | epico | 60 | emotiva, emotional, trailer
epic/Honor Bound | epico | 30 | honor, batalla, battle
epic/New Hero in Town | epico | 30 | heroe, hero, superheroe
epic/Strength of the Titans | epico | 30 | titanes, titans, fuerza, power
epic/Kings Trailer | epico | 30,15 | trailer, reyes, kings, cine
epic/Rulers of Our Lands | epico | 60 | reino, kingdom, fantasia
epic/Video Game Blockbuster | epico | 30 | videojuego, video game, trailer
epic/Epic Boss Battle | epico | 30 | jefe final, boss, batalla, videojuego
epic/Black Knight | epico | 30 | caballero, knight, medieval
unsorted/Behind the Sword | epico | 60 | espada, sword, medieval
unsorted/Brothers Unite | epico | 30 | hermanos, union, batalla
unsorted/The Crown | epico | 60 | corona, crown, reino, realeza
unsorted/Novus Initium | epico | 30 | nuevo comienzo, new beginning, inspiradora
unsorted/Fanfare X | epico | 15 | fanfarria, fanfare, intro, logo, premios
unsorted/Overture | epico | 30 | obertura, overture, orquesta
epic/Lonely Mountain | epico | 60 | montana, mountain, aventura, viaje
unsorted/Journey of Hope | epico | 60 | esperanza, hope, viaje, journey
# ---------------- Tranquila, lofi y estudio
chill/Adding the Sun | tranquilo | 60,15 | chill, sol, manana, morning
chill/I Guess What I'm Trying to Say | tranquilo | 30,15 | chill, beat, hip hop
chill/Downtown Boogie | tranquilo | 30,15 | groove, funk, ciudad
chill/Study and Relax | tranquilo | 60 | estudio, study, lofi
chill/Kalimba Relaxation Music | tranquilo | 60 | kalimba, meditacion, meditation, spa, yoga
chill/Wisdom in the Sun | tranquilo | 60 | ambiental, ambient, meditacion, yoga
unsorted/Be Chillin | tranquilo | 30 | chill, beat, hip hop
unsorted/Take the Sting Out - Jazz Fi | tranquilo | 30,60 | jazz, lofi, jazz hop, cafe | name=Take the Sting Out
electronic/Meditating Beat | tranquilo | 60 | meditacion, meditation, beat, downtempo
misc/Sunday Dub | tranquilo | 30 | dub, reggae, domingo, sunday
misc/River Meditation | tranquilo | 60 | rio, river, meditacion, naturaleza, yoga
chill/Neptunian Princess | tranquilo | 30 | chill, espacio, space, ensueno, dreamy
jazz/Martini Sunset | tranquilo | 30 | jazz, atardecer, sunset, lounge, bar
fma:public-domain-lofi/Tokyo Sunset | tranquilo | 30,60 | lofi, lo-fi, atardecer, sunset, hip hop
fma:public-domain-lofi/Bubbles | tranquilo | 30 | lofi, lo-fi, burbujas, hip hop
fma:public-domain-lofi/Tranquil Mindscape | tranquilo | 60 | lofi, lo-fi, estudio, study, beat
fma:public-domain-lofi/Calm Currents | tranquilo | 30 | lofi, lo-fi, estudio, study
fma:public-domain-lofi/Walking Away | tranquilo | 30 | lofi, lo-fi, paseo, walk
fma:public-domain-lofi/Ocean Breeze | tranquilo | 30 | lofi, ukelele, ukulele, playa, beach
fma:public-domain-lofi/Birds | tranquilo | 30 | lofi, lo-fi, pajaros, birds, naturaleza
fma:public-domain-lofi/Down Time | tranquilo | 30 | lofi, lo-fi, descanso
fma:public-domain-lofi/The Best Of Times | tranquilo | 60 | lofi, lo-fi, estudio, study
fma:public-domain-lofi/Shimmer | tranquilo | 30 | lofi, lo-fi, chill
fma:lo-fi-and-chill/Morning Coffee | tranquilo | 30,15 | lofi, cafe, coffee, manana, morning
fma:city-slacker/Busking In the SunLight | tranquilo | 30 | lofi, hip hop, ciudad, city
fma:city-slacker/Studio Apartment | tranquilo | 30 | lofi, hip hop, casa, home
fma:city-slacker/Day Trips | tranquilo | 30 | lofi, hip hop, viaje, trip
fma:summer-air-lo-fi/Roof Tops | tranquilo | 30 | lofi, verano, summer, azotea
fma:lazy-summer-lofi-1/Laundry On The Wire | tranquilo | 30 | lofi, verano, summer, casa
fma:lazy-summer-lofi-1/Windows Down | tranquilo | 30 | lofi, verano, auto, car, road trip
fma:kick-it-laid-back-hiphop/Unwind | tranquilo | 30 | hip hop, relax, beat
fma:spring-at-last-lofi-tape/Spring At Last | tranquilo | 30 | lofi, primavera, spring
fma:busted-guitar-lofi-edit/Keeping Cool | tranquilo | 30 | lofi, guitarra, guitar
fma:ocean-memory-lo-fi-chill/Ocean Memory | tranquilo | 60 | lofi, mar, ocean, playa
# ---------------- Romántica
romantic/Lovely Piano Song | romantico | 60,30,15 | piano, boda, wedding
romantic/Romantic Inspiration | romantico | 30,15 | piano, inspiradora
romantic/Night in Venice | romantico | 60,15 | venecia, venice, italia, noche, cena
romantic/Shining Stars | romantico | 30 | estrellas, stars, noche
romantic/Nostalgic Piano | romantico | 60 | piano, nostalgia, recuerdos
romantic/Champ de tournesol | romantico | 30 | francesa, french, girasoles, campo
romantic/La Citadelle | romantico | 60 | orquesta, boda, wedding
romantic/Landra's Dream | romantico | 30 | sueno, dream, piano
romantic/Piano Magic Motive | romantico | 15 | piano, magia, intro
romantic/Pond | romantico | 30 | piano, calma, lago
unsorted/Hold Me, Love Me | romantico | 30 | amor, abrazo, love
misc/A Waltz For Naseem | romantico | 30 | vals, waltz, piano | meter=3
fma:lo-fi-and-chill/Puppy Love | romantico | 30 | lofi, amor, love, pareja
fma:we-drove-all-night/Stealing Glimpses Of Your Face | romantico | 30 | synthwave, retro, amor, noche
# ---------------- Triste y emotiva
epic/Go On Without Me | triste | 60,15 | despedida, goodbye, orquesta, cine
scoring/After the End | triste | 60,15 | final, perdida, loss, cine
scoring/Dreams of Vain | triste | 30,15 | suenos, piano, reflexion
scoring/Final Step | triste | 30 | final, despedida, reflexion
romantic/Isolation Waltz | triste | 30 | vals, waltz, soledad, loneliness | meter=3
unsorted/Burt's Requiem | triste | 60 | requiem, homenaje, tribute, memorial
unsorted/Cold Journey | triste | 60 | frio, viaje, soledad
unsorted/Winter | triste | 60 | invierno, winter, piano
classical/Icicles Melting | triste | 60 | piano, invierno, deshielo, delicada
unsorted/The Story | triste | 30 | historia, story, reflexion
unsorted/Consecrated Ground | triste | 30 | homenaje, memorial, solemne
fma:public-domain-lofi/Canon Event | triste | 30 | lofi, reflexion, nostalgia
fma:public-domain-lofi/Forgotten Keep Sakes | triste | 30 | lofi, recuerdos, memories
fma:lo-fi-and-chill/All The Way Sad | triste | 30 | lofi, triste, sad
fma:winter-lofi/Winter Blues | triste | 30 | lofi, invierno, winter
fma:sad-beats/Chills | triste | 30 | lofi, beat, sad beats
fma:public-domain-lofi/Never Sleeping | triste | 30 | lofi, noche, insomnio, dark
# ---------------- Misterio y suspenso
horror/Horror Suspense | suspenso | 30,15 | terror, horror, tension
horror/Mysterious Lights | suspenso | 60,15 | luces, ovni, ufo, ambiental
horror/Hidden Truth | suspenso | 30,15 | verdad oculta, investigacion, documental
horror/Asking Questions | suspenso | 30 | preguntas, investigacion, crimen, true crime
horror/Cursed Intro | suspenso | 15 | maldicion, intro, terror
horror/Footsteps in the Attic | suspenso | 30 | pasos, atico, terror
horror/Mind Chaos | suspenso | 30 | caos, psicologico, thriller
misc/Abstract Anxiety | suspenso | 30 | ansiedad, anxiety, tension
scoring/Driving Concern | suspenso | 30 | tension, persecucion, thriller
scoring/Patron Saint of Heists | suspenso | 30 | robo, heist, espias, spy
scoring/Desert Fox Underscore | suspenso | 60 | fondo, underscore, documental
scoring/Guerilla Tactics | suspenso | 30 | tactica, militar, sigilo, stealth
unsorted/Lurking Sloth | suspenso | 30 | acecho, sigilo, misterio
unsorted/The Abyss | suspenso | 60 | abismo, abyss, oscuro, ambiental
unsorted/Find Them | suspenso | 30 | busqueda, investigacion, thriller
epic/Evil Incoming | suspenso | 30 | villano, villain, oscuro, trailer
epic/Night Attack | suspenso | 30 | noche, ataque, accion
epic/Assassin | suspenso | 30 | asesino, assassin, sigilo
fma:beats-from-the-crypt/Tension In The Air | suspenso | 30 | tension, beat, oscuro
fma:stranger-than-fiction-halloween-sci-fi/Somethings Out There | suspenso | 30 | ciencia ficcion, sci-fi, alien, espacio
# ---------------- Divertida y comedia
comedy/Silly Boy | divertido | 30,15 | tonta, silly, caricatura
comedy/Going Bananas | divertido | 30,15 | locura, bananas, caricatura
comedy/Wakka Wakka | divertido | 30,15 | caricatura, cartoon, travesura
comedy/Fancy Family | divertido | 30,15 | elegante, familia, ironica
comedy/Busybody | divertido | 15 | chismoso, travesura, pizzicato
comedy/Managing Mischief | divertido | 30 | travesura, mischief, pizzicato
comedy/Comic Game Loop - Mischief | divertido | 30 | travesura, videojuego, loop | name=Comic Mischief
comedy/Baltic Levity | divertido | 30 | ligera, humor, acordeon
comedy/Barroom Ballet | divertido | 30 | piano de bar, saloon, western
comedy/Dance of the Tuba Plum Fairy | divertido | 15 | tuba, torpe, clumsy
comedy/Monsters in Hotel | divertido | 30 | monstruos, monsters, caricatura
unsorted/Silly Intro | divertido | 15 | intro, tonta, silly
unsorted/Le Baguette | divertido | 30 | francesa, french, paris, acordeon
unsorted/Foam Rubber | divertido | 30 | goma, rebote, bouncy
unsorted/Pantscrapper | divertido | 30 | funk, tonta, groove
upbeat/Stereotype News | divertido | 30 | noticias, news, parodia
comedy/Maple Leaf Rag | divertido | 60 | ragtime, piano, joplin, cine mudo, silent film
comedy/The Entertainer | divertido | 60,30 | ragtime, piano, joplin, cine mudo, silent film
comedy/Frogs Legs Rag | divertido | 30 | ragtime, piano, cine mudo
comedy/Hello! Ma Baby | divertido | 30 | vintage, cancion antigua, cine mudo
country/Lukewarm Banjo | divertido | 15 | banjo, country
country/Jethro on the Run | divertido | 30 | banjo, country, persecucion
comedy/Creepy Comedy | divertido | 30 | terror gracioso, spooky, caricatura
comedy/Barnville | divertido | 30 | granja, farm, country
# ---------------- Corporativa y negocios
upbeat/Inspiration | corporativo | 30,60,15 | inspiradora, inspiring, motivacion, presentacion
upbeat/Fresh Focus | corporativo | 30,15 | tecnologia, tech, startup, enfoque
upbeat/From Page to Practice | corporativo | 30,15 | educacion, tutorial, curso
upbeat/Motions | corporativo | 30 | tecnologia, tech, movimiento
upbeat/Screen Saver | corporativo | 30 | tecnologia, tech, app, producto
upbeat/Limit 70 | corporativo | 60 | carretera, viaje, publicidad, auto
misc/Sciencenet Theme | corporativo | 30 | ciencia, science, tecnologia, noticias
unsorted/Circuit | corporativo | 30 | tecnologia, tech, electronica, circuitos
unsorted/Construction | corporativo | 30 | construccion, obra, industria, ferreteria
electronic/Arpent | corporativo | 30 | electronica, tecnologia, minimal
electronic/Hear What They Say | corporativo | 30 | electronica, testimonios, entrevistas
scoring/Slice of Life | corporativo | 30 | vida diaria, documental, tutorial
scoring/Travelers Notebook | corporativo | 30 | viaje, cuaderno, documental, inmobiliaria
misc/Bleu | corporativo | 30 | elegante, minimal, moda, fashion
upbeat/Still Pickin | corporativo | 60 | guitarra, acustica, campo, agro
unsorted/Rural Industry | corporativo | 30 | industria, campo, produccion
# ---------------- Infantil
comedy/Llama in Pajama | infantil | 30,15 | llama, pijama, caricatura, cuento
comedy/My Giant Bunny Friend | infantil | 30,15 | conejo, bunny, amigo, cuento
misc/Improved Ice Cream Truck | infantil | 15 | heladero, helado, ice cream
fantasy/Magical Transition | infantil | 15 | magia, magic, transicion, hada
fantasy/Painting Room | infantil | 30,15 | pintar, painting, arte, manualidades
fantasy/Brewing Potions | infantil | 30 | pociones, magia, brujo, wizard
scoring/Magic in the Garden | infantil | 30 | jardin, garden, magia, hadas
world/Forest Frolic Loop | infantil | 15 | bosque, forest, juego
comedy/Spring Chicken | infantil | 30 | pollito, granja, farm
unsorted/A Surprising Encounter | infantil | 30 | sorpresa, cuento, aventura
unsorted/Adventures of Flying Jack | infantil | 30 | aventura, volar, cuento
scoring/Stunted Adventure | infantil | 15 | aventura, juego
fma:background-music/OST Music Box 1 | infantil | 30 | caja musical, music box, cuna, dormir, bebe
fma:background-music/OST Music Box 3 | infantil | 30 | caja musical, music box, cuna, bebe
fma:chiptunes/Sunny Afternoon | infantil | 30 | chiptune, 8 bits, videojuego, retro
fma:chiptunes/Adventure Begins Loop | infantil | 30 | chiptune, 8 bits, videojuego, aventura
fma:retro-gamer-soundtrack/Jump! | infantil | 30 | chiptune, 8 bits, videojuego, saltar
fma:retro-gamer-soundtrack/Comfort Game 1 | infantil | 30 | videojuego, retro, tranquilo | name=Comfort Game
fma:tiny-plastic-video-games-for-long-anxious-space-travel/Pixel Party | infantil | 30 | chiptune, 8 bits, pixel, fiesta
fma:gamer-beats/Coins | infantil | 15 | monedas, coins, videojuego, gamer
# ---------------- Fiesta y baile
chill/Blippy Trance | fiesta | 15,30 | electronica, trance, edm
electronic/Beat One | fiesta | 30,15 | electronica, beat, hip hop
electronic/Backbeat | fiesta | 30,15 | electronica, beat, breakbeat
jazz/Funkeriffic | fiesta | 30,15 | funk, groove, disco
world/Shenzhen Nightlife | fiesta | 30 | noche, club, electronica, asia
electronic/Goodnightmare | fiesta | 30 | electronica, techno, club
electronic/Bit Bit Loop | fiesta | 15 | electronica, 8 bits, loop
jazz/Swing Maching | fiesta | 30 | swing, electro swing, jazz | name=Swing Machine
jazz/Stompin at Midnight | fiesta | 30 | swing, jazz, charleston, anos 20
comedy/Vintage Party | fiesta | 30 | vintage, anos 20, charleston
world/Modern Island Jam | fiesta | 30 | tropical, isla, island, verano
unsorted/Pina Colada | fiesta | 30 | tropical, playa, beach, verano
chill/Planeteer Reaction | fiesta | 30 | groove, funk, beat
comedy/Take the Ride | fiesta | 30 | rock, viaje, ride
fma:waves-of-nostalgia-2/Night Life | fiesta | 30 | synthwave, retro, anos 80, noche
fma:waves-of-nostalgia-2/We used To Dance | fiesta | 30 | synthwave, retro, anos 80, baile
fma:power-pop/Back In The 80s | fiesta | 30 | synth pop, anos 80, retro
fma:power-pop/Retro Synths | fiesta | 30 | synth pop, retro, anos 80
fma:power-pop/Funky Pop | fiesta | 30 | funk, pop, groove
# ---------------- Navidad y fechas
unsorted/Deck the Halls | fechas | 30,60,15 | navidad, christmas, villancico, carol | name=Deck the Halls
unsorted/We Wish You a Merry Christmas | fechas | 30,15 | navidad, christmas, villancico, carol
comedy/Krampus's Workshop | fechas | 30,15 | navidad, christmas, taller, juguetes
comedy/Holiday Weasel | fechas | 30,15 | navidad, christmas, fiestas, holidays
fma:a-lo-fi-christmas-special/Silent Night | fechas | 30,60 | navidad, christmas, noche de paz, villancico, lofi | name=Silent Night (Lo-Fi)
fma:a-lo-fi-christmas-special/Oh Holy Night | fechas | 60 | navidad, christmas, villancico, lofi | name=O Holy Night (Lo-Fi)
fma:a-lo-fi-christmas-special/Angels We Have Heard On High | fechas | 30 | navidad, christmas, angeles, villancico, lofi | name=Angels We Have Heard on High (Lo-Fi)
fma:a-lo-fi-christmas-special/Auld Lang Syne | fechas | 30 | ano nuevo, new year, fin de ano, lofi | name=Auld Lang Syne (Lo-Fi)
fma:a-synth-wave-christmas-special/Joy To The World | fechas | 30 | navidad, christmas, villancico, synthwave | name=Joy to the World (Synthwave)
fma:a-synth-wave-christmas-special/God Rest Ye Merry Gentlemen | fechas | 30 | navidad, christmas, villancico, synthwave | name=God Rest Ye Merry Gentlemen (Synthwave)
fma:a-synth-wave-christmas-special/We Three Kings | fechas | 30 | reyes magos, epifania, navidad, synthwave | name=We Three Kings (Synthwave)
fma:a-synth-wave-christmas-special/The First Noel | fechas | 30 | navidad, christmas, villancico, synthwave | name=The First Noel (Synthwave)
fma:winter-lofi/First Snow | fechas | 30 | invierno, winter, nieve, snow, lofi
fma:winter-lofi/Fire Place | fechas | 30 | invierno, chimenea, fireplace, navidad, lofi | name=Fireplace
unsorted/Pump up your Graduation | fechas | 30,60 | graduacion, graduation, ceremonia, pompa
unsorted/Fireworks | fechas | 30 | fuegos artificiales, fireworks, ano nuevo, new year
unsorted/Celebration | fechas | 30 | cumpleanos, birthday, celebracion, aniversario
comedy/Ghost Town | fechas | 30 | halloween, fantasmas, ghosts, spooky
comedy/Night in the Castle | fechas | 30 | halloween, castillo, vampiro, spooky
comedy/Fright Night Twist | fechas | 30 | halloween, twist, spooky, fiesta
fantasy/Witch Waltz | fechas | 30 | halloween, bruja, witch, vals | meter=3
comedy/Wizard Circus | fechas | 30 | halloween, circo, magia, spooky
fma:horseless-headman-halloween-beats/Haunted Houses | fechas | 30 | halloween, casa embrujada, beat
fma:beats-from-the-crypt/Dance Of The Dead | fechas | 30 | halloween, muertos, baile, beat
# ---------------- Del mundo
world/Bollywood Groove | mundo | 30,15 | india, bollywood, sitar, tabla
world/Breaking Bollywood | mundo | 30,15 | india, bollywood, tabla
world/Bavarian Seascape | mundo | 30,15 | europa, alemania, bavaria, acordeon
world/Coy Koi | mundo | 30,15 | japon, japan, asia, koto
world/Cumbish | mundo | 30 | cumbia, latina, tropical
world/Del Rio Bravo | mundo | 30 | mexico, western, guitarra, desierto
world/Desert Conflict | mundo | 30 | medio oriente, middle east, desierto, arabe
world/Eye of Forgiveness | mundo | 30 | medio oriente, oriental, meditacion
world/Hillbilly Swing | mundo | 30 | estados unidos, country, bluegrass, banjo
world/Midnight in the Green House | mundo | 30 | asia, oriental, noche
world/Palm and Soul | mundo | 30 | tropical, caribe, palmeras, soul
world/Village Tarantella | mundo | 15 | italia, italy, tarantela, tarantella, mandolina
world/Windy Old Weather | mundo | 30 | marinera, sea shanty, irlanda, celta
world/Aquatic City Vanished | mundo | 30 | asia, oriental, agua
world/Connecting Rainbows | mundo | 30 | multicultural, arcoiris, alegre
unsorted/Ambient Bongos | mundo | 30 | bongos, percusion, africa, tribal
unsorted/Sunny Rasta | mundo | 30 | reggae, jamaica, caribe
unsorted/Nomadic Sunset | mundo | 30 | desierto, nomada, oriental
unsorted/The Desert | mundo | 30 | desierto, desert, medio oriente
unsorted/Bouchedag | mundo | 30 | europa, folk, acordeon
fantasy/Dancing at the Inn | mundo | 30 | celta, celtic, irlanda, taberna, medieval
fantasy/The Britons | mundo | 60 | celta, britanica, britons, gaita
unsorted/The Vikings | mundo | 30 | vikingos, vikings, nordica, norse
fantasy/Nordic Wist | mundo | 30 | nordica, escandinavia, norse
misc/Ambush in Rattlesnake Gulch | mundo | 30 | western, vaqueros, cowboys, lejano oeste
fma:nature-spirit/Kitsune | mundo | 30 | japon, japan, zorro, espiritu
fma:nature-spirit/Kodama | mundo | 30 | japon, japan, bosque, espiritu
"""


def resolve(ref: str, src: dict) -> str | None:
    if ref.startswith("fma:"):
        album, title = ref[4:].split("/", 1)
        want = plain(title)
        for k, s in sorted(src.items()):
            if k.startswith("fma/") and s.get("albumSlug") == album and plain(s["title"]).startswith(want):
                return k
        return None
    if "/" in ref and not ref.endswith(".mp3"):
        folder, title = ref.split("/", 1)
        ref = f"freepd/{folder}__{title}.mp3"
    return ref if ref in src else None


def clean_title(t: str) -> str:
    t = re.sub(r"\.mp3$", "", t.strip(), flags=re.I)
    t = re.sub(r"\s*\([^)]*\)\s*", " ", t)   # "( Lofi , Chill )" descriptors
    t = re.sub(r"\s+", " ", t).strip(" .")
    if t.isupper() and len(t) > 3:
        t = t.title()
    return t


def _parse() -> list[Item]:
    from fetch import load_sources  # titles come from the downloaded sources
    src = load_sources()
    items, seen = [], set()
    for line in SONGS.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        key, cat, lengths, tags = parts[:4]
        opts = dict(p.split("=", 1) for p in parts[4:] if "=" in p)
        assert cat in CATEGORIES, line
        key = resolve(key, src)
        if key is None:
            print("catalog: not found:", line)
            continue
        s = src[key]
        title = opts.get("name") or clean_title(s["title"])
        if title.isupper() and len(title) > 3:
            title = title.title()
        base = slug(title)
        for n in (int(v) for v in lengths.split(",")):
            iid = f"{base}-{n}s"
            assert iid not in seen, iid
            seen.add(iid)
            words = [title, s["artist"], *CATEGORY_TAGS[cat].split(","), *LENGTH_TAGS[n].split(","),
                     *tags.split(",")]
            out = []
            for w in words:
                w = plain(w)
                if w and w not in out:
                    out.append(w)
            items.append(Item(id=iid, key=key, length=n, category=cat,
                              names={"es": f"{title} · {n} s", "en": f"{title} · {n} s"}, tags=out,
                              meter=int(opts.get("meter", 4)),
                              start=float(opts["start"]) if "start" in opts else None,
                              prefer_intro=float(opts["intro"]) if "intro" in opts else None))
    return items


ITEMS = _parse()
