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
    'meloinvento.li': 168,
    'meloinvento.li': 96,
    'meloinvento.org': 170,
    'meloinvento.club': 72,
    'meloinvento.com': 48,
    'meloinvento.eu': 168,
    'meloinvento.cx': 72,
    'tracker.meloinvento.org': 72
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

# Crear las etiquetas si no existen
tags_a_crear = [tag for tag in [TAG_BORRADO, TAG_HR] if tag not in client.torrents_tags()]
if tags_a_crear:
    client.torrents_create_tags(tags=tags_a_crear)
    print(f"🏷️  Etiquetas creadas: {', '.join(tags_a_crear)}")

print("🔎 Escaneando todos los torrents para aplicar reglas...")

# Listas para agrupar las acciones
torrents_a_etiquetar_borrado = []
torrents_a_etiquetar_hr = []
torrents_a_desetiquetar_hr = []

# Obtener todos los torrents
all_torrents = client.torrents_info()

# Analizar cada torrent
for torrent in all_torrents:
    existing_tags = torrent.tags.split(',') if torrent.tags else []

    # --- LÓGICA 1: TORRENTS NO REGISTRADOS ("BORRADOS") ---
    if TAG_BORRADO not in existing_tags:
        for tracker_info in torrent.trackers:
            msg = tracker_info['msg'].lower()
            status = tracker_info['status']
            
            is_unregistered = status == 4 and ("not registered" in msg or "unregistered" in msg or "no registrado" in msg)

            if is_unregistered:
                torrents_a_etiquetar_borrado.append(torrent)
                # Una vez detectado, no hace falta seguir mirando más trackers para este torrent
                break 

    # --- LÓGICA 2: GESTIÓN DE HIT & RUN (H&R) ---
    for tracker_key, required_hours in TRACKER_RULES.items():
        if tracker_key in torrent.tracker:
            seeding_time_hours = torrent.seeding_time / 3600
            is_hr_completed = seeding_time_hours >= required_hours
            has_hr_tag = TAG_HR in existing_tags

            # AÑADIR etiqueta H&R: No ha cumplido el tiempo Y no tiene la etiqueta.
            if not is_hr_completed and not has_hr_tag:
                torrents_a_etiquetar_hr.append(torrent)

            # QUITAR etiqueta H&R: Ya ha cumplido el tiempo Y todavía tiene la etiqueta.
            elif is_hr_completed and has_hr_tag:
                torrents_a_desetiquetar_hr.append(torrent)
            
            # La regla de H&R ya ha aplicado, pasamos al siguiente torrent
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

# --- REPORTE FINAL ---
print("\n" + "─" * 70)
if not acciones_realizadas:
    print("👍 ¡Todo en orden! No se realizaron nuevas acciones en esta ejecución.")
else:
    print("📄 Resumen de acciones completado.")
    
print("─" * 70)
print("\n🎉 Script finalizado.")