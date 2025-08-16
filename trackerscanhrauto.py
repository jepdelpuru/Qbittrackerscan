import qbittorrentapi
import sys
from urllib.parse import urlparse

# --- CONFIGURACIÓN GENERAL ---
# Completa aquí los datos de tu qBittorrent Web UI
QBIT_HOST = '192.168.0.160'
QBIT_PORT = 6363
QBIT_USER = None
QBIT_PASS = None

# --- CONFIGURACIÓN DE ETIQUETAS ---
# Etiqueta para torrents que el tracker ya no reconoce ("unregistered")
TAG_BORRADO = "Tracker Borrado"

# Etiqueta para torrents que aún no cumplen el tiempo de seeding obligatorio
TAG_HR = "Hit & Run"


# --- REGLAS DE HIT & RUN (H&R) ---
# Define el tiempo mínimo de subida en HORAS para cada tracker.
# La clave debe ser una parte ÚNICA de la URL del tracker.
TRACKER_RULES = {
    'xxxxxx.li': 168,
    'xxxxxx.li': 96,
    'xxxxxxx.org': 170,
    'xxxxxxx.xxx': 72,
    'xxxxxxx.com': 48,
    'xxxxxx.eu': 168,
    'xxxxxxx.cx': 72,
    'tracker.xxxxxx.org': 72
}

# --- DICCIONARIO DE ETIQUETAS POR TRACKER (EMOJI + NOMBRE) ---
# Define el emoji para cada tracker. La clave debe ser una parte ÚNICA de la URL.
# El script creará una etiqueta con el formato "EMOJI NombreTracker"
TRACKER_EMOJIS = {
    # --- Trackers Privados y Semi-Privados ---
    "xxxxxxxx.xxx": "🌀",
    "xxxxxxxx.xxx": "🎯",
    "xxxxxxxx.xxx": "🏛️",
    "xxxxx.xxxxx": "🫏",
    "bitporn.eu": "🍆",
    "tracker.happyfappy.org": "😈",
    "ssl.bootytape.com": "🍑",
    "rintor.org": "🪙",
    "xxxxxxxxx.xxx": "⚡️",
    "xxxxxx.xxxx": "🌍",
    "xxxxx.xxx": "🛡️",

    # --- Trackers Públicos en Español ---
    "divxtotal.in": "🇪🇸",
    "elitetorrent.li": "🇪🇸",
    "epublibre.org": "📚",
    "frozen-layer.com": "❄️",
    "gamestorrents.fm": "🎮",
    "moviesdvdr.co": "📀",
    "opensharing.org": "👐",
    "rintor.net": "🌐",
    "wolfmax4k.org": "🐺",

    # --- Trackers Públicos Generales ---
    "1337x.to": "🏴‍☠️",
    "bitru.org": "🇷🇺",
    "bitsearch.to": "🔎",
    "rapidzona.org": "⏩",
    "torrent-pirat.com": "🦜",
    "traht.org": "🇷🇺",

    # --- Trackers Públicos (Contenido Adulto) ---
    "myporn.club": "🔞",
    "onejav.com": "🇯🇵",
    "pornotorrent.eu": "🌶️",
    "pornrips.to": "💦",
    "sexy-pics.org": "📸",
    "sosulki.info": "🍭",
    "sukebei.nyaa.si": "😼",
    "xxxclub.to": "♣️",
    "xxxtor.com": "💋"
}


# --- LÓGICA DEL SCRIPT ---

print("Iniciando script de gestión de etiquetas para qBittorrent...")

# Conectar con el cliente de qBittorrent
try:
    client = qbittorrentapi.Client(
        host=QBIT_HOST, port=QBIT_PORT, username=QBIT_USER, password=QBIT_PASS
    )
    client.auth_log_in()
    print(f"✅ Conexión exitosa a qBittorrent v{client.app.version}")
except qbittorrentapi.LoginFailed as e:
    print(f"❌ Error de conexión: {e}. Revisa tus datos en la sección de CONFIGURACIÓN.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"❌ Ha ocurrido un error inesperado al conectar: {e}", file=sys.stderr)
    sys.exit(1)

# Crear las etiquetas de gestión si no existen
tags_gestion_a_crear = [tag for tag in [TAG_BORRADO, TAG_HR] if tag not in client.torrents_tags()]
if tags_gestion_a_crear:
    client.torrents_create_tags(tags=tags_gestion_a_crear)
    print(f"🏷️  Etiquetas de gestión creadas: {', '.join(tags_gestion_a_crear)}")

print("🔎 Escaneando todos los torrents para aplicar reglas...")

# Listas para agrupar las acciones
torrents_a_etiquetar_borrado = []
torrents_a_etiquetar_hr = []
torrents_a_desetiquetar_hr = []
torrents_a_desetiquetar_borrado = []
# NUEVO: Diccionario para agrupar torrents por su nueva etiqueta de tracker
torrents_a_etiquetar_por_tracker = {}

# Obtener todos los torrents
all_torrents = client.torrents_info()

# Analizar cada torrent
for torrent in all_torrents:
    existing_tags = [tag.strip() for tag in torrent.tags.split(',')] if torrent.tags else []

    # --- LÓGICA 1: GESTIÓN DE TORRENTS NO REGISTRADOS ("BORRADOS") ---
    is_currently_unregistered = False
    for tracker_info in torrent.trackers:
        msg = tracker_info['msg'].lower()
        status = tracker_info['status']
        
        # Comprueba si algún tracker da el error específico
        if status == 4 and ("not registered" in msg or "unregistered" in msg or "no registrado" in msg or "expected digit in bencoded string" in msg):
            is_currently_unregistered = True
            break # Si uno falla, marcamos el torrent como fallido y salimos del bucle

    has_borrado_tag = TAG_BORRADO in existing_tags

    # Decidir si añadir o quitar la etiqueta
    if is_currently_unregistered and not has_borrado_tag:
        # El torrent está fallando ahora y no tiene la etiqueta -> Añadirla
        torrents_a_etiquetar_borrado.append(torrent)
    elif not is_currently_unregistered and has_borrado_tag:
        # El torrent funciona bien ahora, pero tenía la etiqueta -> Quitarla
        torrents_a_desetiquetar_borrado.append(torrent)

    # --- LÓGICA 2: GESTIÓN DE HIT & RUN (H&R) ---
    for tracker_key, required_hours in TRACKER_RULES.items():
        if tracker_key in torrent.tracker:
            seeding_time_hours = torrent.seeding_time / 3600
            is_hr_completed = seeding_time_hours >= required_hours
            has_hr_tag = TAG_HR in existing_tags

            if not is_hr_completed and not has_hr_tag:
                torrents_a_etiquetar_hr.append(torrent)

            elif is_hr_completed and has_hr_tag:
                torrents_a_desetiquetar_hr.append(torrent)
            
            break
            
    # --- LÓGICA 3: ETIQUETADO AUTOMÁTICO POR TRACKER ---
    for domain, emoji in TRACKER_EMOJIS.items():
        if domain in torrent.tracker:
            tag_name = f"{emoji} {domain}"
            if tag_name not in existing_tags:
                if tag_name not in torrents_a_etiquetar_por_tracker:
                    torrents_a_etiquetar_por_tracker[tag_name] = []
                torrents_a_etiquetar_por_tracker[tag_name].append(torrent)
            # Una vez encontrado el tracker, pasamos al siguiente torrent
            break

print("⚙️  Escaneo finalizado. Aplicando cambios...")

# --- APLICAR CAMBIOS Y GENERAR REPORTE ---
acciones_realizadas = False

# 1. Aplicar etiqueta de "Tracker Borrado"
if torrents_a_etiquetar_borrado:
    hashes = [t.hash for t in torrents_a_etiquetar_borrado]
    client.torrents_add_tags(tags=TAG_BORRADO, torrent_hashes=hashes)
    print(f"\n🆕 Se aplicó la etiqueta '{TAG_BORRADO}' a {len(hashes)} torrent(s):")
    for torrent in torrents_a_etiquetar_borrado:
        print(f"  - {torrent.name[:80]}")
    acciones_realizadas = True

# 2. Quitar etiqueta de "Tracker Borrado" por estar solucionado
if torrents_a_desetiquetar_borrado:
    hashes = [t.hash for t in torrents_a_desetiquetar_borrado]
    client.torrents_remove_tags(tags=TAG_BORRADO, torrent_hashes=hashes)
    print(f"\n🔄 Se quitó la etiqueta '{TAG_BORRADO}' a {len(hashes)} torrent(s) que volvieron a comunicar:")
    for torrent in torrents_a_desetiquetar_borrado:
        print(f"  - {torrent.name[:80]}")
    acciones_realizadas = True

# 2. Aplicar etiqueta de "Hit & Run"
if torrents_a_etiquetar_hr:
    hashes = [t.hash for t in torrents_a_etiquetar_hr]
    client.torrents_add_tags(tags=TAG_HR, torrent_hashes=hashes)
    print(f"\n🏃 Se marcó como '{TAG_HR}' a {len(hashes)} torrent(s) por no cumplir el tiempo de seed:")
    for torrent in torrents_a_etiquetar_hr:
        print(f"  - {torrent.name[:80]}")
    acciones_realizadas = True

# 3. Quitar etiqueta de "Hit & Run"
if torrents_a_desetiquetar_hr:
    hashes = [t.hash for t in torrents_a_desetiquetar_hr]
    client.torrents_remove_tags(tags=TAG_HR, torrent_hashes=hashes)
    print(f"\n✅ Se quitó la etiqueta '{TAG_HR}' a {len(hashes)} torrent(s) que ya cumplieron su tiempo:")
    for torrent in torrents_a_desetiquetar_hr:
        print(f"  - {torrent.name[:80]}")
    acciones_realizadas = True

# 4. NUEVO: Crear y aplicar etiquetas por tracker
if torrents_a_etiquetar_por_tracker:
    print(f"\n🎨 Se van a aplicar {len(torrents_a_etiquetar_por_tracker)} tipo(s) de etiquetas de tracker:")
    # Obtener todas las etiquetas que qBittorrent conoce actualmente
    all_current_tags = [t.strip() for t in client.torrents_tags()]
    # Filtrar para encontrar solo las que necesitamos crear
    all_current_tags_set = {t.strip() for t in client.torrents_tags()}
    new_tags_to_create = [tag for tag in torrents_a_etiquetar_por_tracker.keys() if tag.strip() not in all_current_tags_set]

    
    if new_tags_to_create:
        client.torrents_create_tags(tags=new_tags_to_create)
        print(f"  - Se han creado {len(new_tags_to_create)} nuevas etiquetas de tracker en qBittorrent.")

    # Aplicar las etiquetas a los torrents correspondientes
    for tag_name, torrents_list in torrents_a_etiquetar_por_tracker.items():
        if torrents_list:
            hashes = [t.hash for t in torrents_list]
            client.torrents_add_tags(tags=tag_name, torrent_hashes=hashes)
            print(f"  - Etiqueta '{tag_name}' aplicada a {len(hashes)} torrent(s).")
    acciones_realizadas = True


# --- REPORTE FINAL ---
print("\n" + "─" * 70)
if not acciones_realizadas:
    print("👍 ¡Todo en orden! No se realizaron nuevas acciones en esta ejecución.")
else:
    print("📄 Resumen de acciones completado.")
    
print("─" * 70)
print("\n🎉 Script finalizado.")
