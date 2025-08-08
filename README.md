# Gestor Automatizado para qBittorrent

Un script en Python diseñado para conectarse a la WebUI de qBittorrent y automatizar tareas de mantenimiento y organización. Ideal para ejecutarse de forma periódica a través de un `cron job` en un servidor o Raspberry Pi.

El propósito principal de este script es mantener una lista de torrents limpia y organizada, asegurando el cumplimiento de las normas de trackers privados y liberando al usuario de tareas manuales repetitivas.

## Características Principales ✨

* **Gestión de Hit & Run (H&R):**
    * Aplica automáticamente una etiqueta (ej. `Hit & Run`) a los torrents que aún no han cumplido el tiempo mínimo de seedeo requerido por tracker.
    * Elimina la etiqueta una vez que el tiempo de seedeo se ha completado.
* **Etiquetado de Torrents Borrados:**
    * Detecta torrents que han sido eliminados del tracker (error "Unregistered torrent").
    * Les aplica una etiqueta (ej. `Tracker Borrado`) para facilitar su posterior revisión o eliminación.
* **Configuración Sencilla:** Todas las reglas y datos de conexión se configuran fácilmente en la parte superior del script.
* **Registro de Actividad:** Genera un archivo de log para poder revisar las acciones realizadas en cada ejecución.
* **Ligero y Eficiente:** Diseñado para consumir mínimos recursos, perfecto para dispositivos de baja potencia.

## Requisitos 📋

* Python 3.7+
* Un cliente qBittorrent en funcionamiento con la **WebUI activada**.
* Acceso a la red entre el dispositivo que ejecuta el script y el servidor de qBittorrent.

## Instalación 🚀

1.  **Clona este repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
    cd tu-repositorio
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Crea un archivo `requirements.txt`** con el siguiente contenido:
    ```txt
    qbittorrent-api
    ```

4.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuración ⚙️

Antes de ejecutar el script, debes editar el archivo `.py` para ajustarlo a tu configuración. Abre el archivo y modifica las siguientes secciones:

```python
# --- CONFIGURACIÓN GENERAL ---
# Completa aquí los datos de tu qBittorrent Web UI
QBIT_HOST = '192.168.0.160' # IP de tu qBittorrent
QBIT_PORT = 6363            # Puerto de la WebUI
QBIT_USER = None            # Tu usuario (si no tienes, déjalo en None)
QBIT_PASS = None            # Tu contraseña (si no tienes, déjala en None)

# --- CONFIGURACIÓN DE ETIQUETAS ---
TAG_BORRADO = "Tracker Borrado"
TAG_HR = "Hit & Run"

# --- REGLAS DE HIT & RUN (H&R) ---
# Define el tiempo mínimo de subida en HORAS para cada tracker.
# La clave debe ser una parte ÚNICA de la URL del tracker.
TRACKER_RULES = {
    'meloinvento.li': 168,
    'meloinvento2.li': 96,
    'meloinvento3.org': 170,
    # Añade aquí tus propias reglas
}
```

## Uso ▶️

Puedes ejecutar el script de dos maneras:

#### 1. Ejecución Manual
Para probar el script o ejecutarlo una sola vez, simplemente corre el siguiente comando desde la terminal (asegúrate de tener el entorno virtual activado):
```bash
python tu_script.py
```

#### 2. Ejecución Automática con `cron`
El método ideal es programar su ejecución periódica. Para ejecutarlo cada hora, edita tu `crontab`:
```bash
crontab -e
```
Y añade la siguiente línea (ajustando las rutas a tu configuración):
```crontab
0 * * * * /ruta/a/tu/venv/bin/python /ruta/a/tu/script.py >> /ruta/a/tu/log.log 2>&1
```

## Posibles Mejoras Futuras 💡

Este proyecto tiene potencial para crecer. Algunas ideas incluyen:
* Gestión de espacio en disco (borrado automático por antigüedad o ratio).
* Pausado automático de torrents que alcanzan un ratio objetivo.
* Notificaciones a Telegram, Pushover o Discord.
* Organización automática de torrents por categorías.

## Licencia 📄

Este proyecto se distribuye bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
