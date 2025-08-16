🤖 qBittorrent Tag Manager 🏷️
¡Hola! 👋 Este es un script de Python para automatizar la gestión de tus torrents en qBittorrent. Su principal objetivo es mantener tu cliente ordenado y ayudarte a cumplir las normas de los trackers privados de forma automática.

El script se conecta a la Web UI de tu qBittorrent y realiza las siguientes tareas mágicas:

🧹 Limpia y organiza: Identifica torrents que han sido borrados del tracker.

🏃 Controla el "Hit & Run": Vigila el tiempo que llevas compartiendo en trackers privados.

🎨 Clasifica visualmente: Asigna un emoji único a cada tracker para que sepas de dónde viene cada torrent de un solo vistazo.

✨ Funcionalidades Principales
Este script tiene tres superpoderes para gestionar tus torrents:

1. 🗑️ Etiquetado de Torrents "Borrados"
A veces, los trackers eliminan torrents que ya no están disponibles. Tu cliente sigue intentando conectar, mostrando un error de "Unregistered" o "No registrado".

¿Qué hace el script? Detecta automáticamente estos torrents y les añade la etiqueta "Tracker Borrado".

¿Y si se arregla? Si el torrent vuelve a conectar correctamente, el script le quitará la etiqueta de forma automática. ¡Magia!

2. 🏃‍♂️ Gestión de Hit & Run (H&R)
Muchos trackers privados exigen que compartas un archivo durante un tiempo mínimo. ¡Es de buena educación y necesario para mantener la comunidad!

¿Qué hace el script? Revisa tus torrents de trackers específicos y, si no han cumplido el tiempo de seed obligatorio, les pone la etiqueta "Hit & Run".

Misión cumplida: Una vez que el torrent alcanza el tiempo requerido, el script le quita la etiqueta. ¡Ya eres un buen seeder! ✅

3. 🎨 Clasificación por Tracker con Emojis
¿No sería genial saber de qué tracker es cada torrent con solo un vistazo?

¿Qué hace el script? Asigna una etiqueta con un emoji + nombre del tracker a cada torrent. Por ejemplo, 🌀 dominio.com o 🇪🇸 divxtotal.in.

Totalmente personalizable: Puedes asignar los emojis que más te gusten a tus trackers favoritos.

🛠️ Configuración Inicial
Antes de lanzar el cohete 🚀, necesitas configurar algunas cosas. ¡Es muy fácil! Abre el script y edita las siguientes secciones:

1. Conexión a qBittorrent
Estos son los datos para que el script pueda hablar con tu qBittorrent.

Python

# --- CONFIGURACIÓN GENERAL ---
# Completa aquí los datos de tu qBittorrent Web UI
QBIT_HOST = '192.168.0.160'  # La IP de tu qBittorrent
QBIT_PORT = 6363             # El puerto de la Web UI
QBIT_USER = None             # Tu usuario (si no tienes, déjalo como None)
QBIT_PASS = None             # Tu contraseña (si no tienes, déjala como None)
¡Ojo! 🧐 Asegúrate de que la API Web de qBittorrent está activada. Puedes encontrarla en Opciones -> Web UI.

2. Personaliza las Etiquetas
Puedes cambiar el nombre de las etiquetas de gestión si lo prefieres.

Python

# --- CONFIGURACIÓN DE ETIQUETAS ---
TAG_BORRADO = "Tracker Borrado"
TAG_HR = "Hit & Run"
3. Define tus Reglas de Hit & Run
Aquí es donde le dices al script cuánto tiempo de seed requiere cada tracker.

Python

# --- REGLAS DE HIT & RUN (H&R) ---
# La clave es una parte ÚNICA de la URL del tracker, y el valor es el tiempo en HORAS.
TRACKER_RULES = {
    'trackerprivado.li': 168,   # 168 horas = 7 días
    'otrotracker.org': 72,      # 72 horas = 3 días
}
4. Asigna Emojis a tus Trackers
¡La parte más divertida! Dale a cada tracker su propia identidad visual.

Python

# --- DICCIONARIO DE ETIQUETAS POR TRACKER (EMOJI + NOMBRE) ---
# La clave es una parte ÚNICA de la URL, y el valor es el emoji que quieras usar.
TRACKER_EMOJIS = {
    "midominio.com": "🚀",
    "tracker.ejemplo.org": "🌟",
    "divxtotal.in": "🇪🇸",
}
🚀 Puesta en Marcha
1. Instalación de Dependencias
Este script necesita la librería qbittorrent-api para funcionar. La puedes instalar muy fácilmente con pip:

Bash

pip install qbittorrent-api
2. Ejecución Manual
Para ejecutar el script, simplemente navega hasta el directorio donde lo guardaste y lánzalo con Python:

Bash

python tu_script.py
Verás en la consola un resumen de todo lo que el script ha hecho.

automating with cron to translate to spanish: "Automatización con Cron"
Automatización con Cron
Para que este script sea realmente útil, lo ideal es que se ejecute solo cada cierto tiempo. Aquí es donde entra Cron, el planificador de tareas de los sistemas Linux.

1. Abrir el Editor de Crontab
Abre una terminal y escribe el siguiente comando para editar las tareas programadas de tu usuario:

Bash

crontab -e
2. Añadir la Tarea Programada
Añade la siguiente línea al final del archivo. Este ejemplo ejecuta el script cada 15 minutos:

Fragmento de código

*/15 * * * * /usr/bin/python3 /ruta/completa/a/tu/tu_script.py >> /ruta/completa/a/un/log.txt 2>&1
Desglosemos esa línea:

*/15 * * * *: Esta es la frecuencia. Significa "en el minuto múltipo de 15, de cada hora, de cada día...".

/usr/bin/python3: La ruta al ejecutable de Python. Puedes encontrarla con el comando which python3.

/ruta/completa/a/tu/tu_script.py: La ruta absoluta donde has guardado el script. ¡Muy importante que sea la ruta completa!

>> /ruta/a/un/log.txt 2>&1: Esto es opcional pero muy recomendado. Guarda toda la salida del script (tanto los mensajes normales como los errores) en un archivo de registro (log.txt). Así podrás revisar si todo ha ido bien.

¡Guarda el archivo y listo! Cron se encargará de ejecutar tu script automáticamente para que tu qBittorrent esté siempre impecable. ✨
