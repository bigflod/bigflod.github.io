
from pathlib import Path
import os

# ==============================
# CONSTANTES PARA index.html
# ==============================
HEADER_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Sitio en construcción</title>
    <link rel="stylesheet" href="/estilos/main.css">
</head>
<body>
    <!-- ============ NAV SUPERIOR ============ -->
    <nav class="navbar">
        <a href="/es/" class="logo">
            <img src="/assets/logo.webp" alt="Logo" height="40">
        </a>
        <!-- Enlaces dinámicos de primer nivel -->
        {NAV_ENLACES}

        <!-- Icono idiomas -->
        <img src="/assets/language-icon.webp" class="language-menu-icon" onclick="toggleLanguageMenu()">

        <!-- Botón modo noche -->
        <div class="toggle-container" onclick="toggleDarkMode()">
            <div class="toggle-switch"></div>
        </div>

        <!-- Popup idiomas -->
        <div id="languageMenu" class="language-popup-menu">
            <button onclick="changeLanguage('es')">ES</button>
            <button onclick="changeLanguage('en')">EN</button>
            <button onclick="changeLanguage('fr')">FR</button>
            <button onclick="changeLanguage('it')">IT</button>
        </div>
    </nav>

    <!-- ============ CONTENEDOR DE 3 COLUMNAS ============ -->
    <div class="page-layout">
        <!-- SIDEBAR IZQUIERDA -->
        <aside class="sidebar-left">
            <!-- TÍTULO DE CARPETA Y NAVEGACIÓN -->
"""

# Ahora el FOOTER empieza justo después del sidebar UL:
FOOTER = """
        </ul>
        </aside>

        <!-- CONTENIDO PRINCIPAL -->
        <main>
            <img src="/assets/construction-site.webp" width="280">
            <h2>Estamos trabajando en ello</h2>
            <p>Esta sección aún no está lista, pero pronto estará disponible.</p>

            <a href="/es/" class="back-button">Volver atrás</a>
        </main>

        <!-- SIDEBAR DERECHA (vacía por ahora) -->
        <aside class="sidebar-right">
            <!-- Vacío -->
        </aside>
    </div>

    <!-- ============ SCRIPTS ============ -->
    <script>
        function toggleLanguageMenu() {
            const menu = document.getElementById("languageMenu");
            menu.style.display = menu.style.display === "flex" ? "none" : "flex";
        }

        function changeLanguage(lang) {
            const current = window.location.pathname;
            const parts = current.split("/");
            parts[1] = lang;
            window.location.href = parts.join("/");
        }

        function toggleDarkMode() {
            document.body.classList.toggle("dark-mode");
        }
    </script>
</body>
</html>
"""


# ==============================
# RUTAS BASE
# ==============================
ruta_base = Path(os.getcwd())
finished_pages = ruta_base / "finishedPages"
unfinished_template = ruta_base / "unfinishedPage.html"
texto = (ruta_base / "datos.txt").read_text()

# ==============================
# ESTRUCTURA DE CARPETAS
# ==============================
class CarpetaInfo:
    def __init__(self, ruta_fisica: Path, ruta_web: str, nombre: str):
        self.ruta_fisica = ruta_fisica
        self.ruta_web = ruta_web
        self.nombre = nombre
        self.subcarpetas = []
        self.archivos = []

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def convertir_ruta_a_nombre_archivo(ruta_web: str) -> str:
    """
    Convierte /es/java/bucles/ → es-java-bucles.html
    Convierte /en/algorithms/sorting/mergesort.html → en-algorithms-sorting-mergesort.html
    """
    ruta = ruta_web.strip("/")

    if ruta.endswith(".html"):
        ruta = ruta[:-5]

    partes = ruta.split("/")
    nombre = "-".join(partes) + ".html"
    return nombre

def formatear_nombre_archivo(nombre_archivo: str) -> str:
    base = nombre_archivo.rsplit(".", 1)[0]
    partes = base.split("-")
    partes = [p.capitalize() for p in partes]
    return " ".join(partes)

def formatear_nombre_carpeta(nombre: str) -> str:
    partes = nombre.split("-")
    partes = [p.capitalize() for p in partes]
    return " ".join(partes)

def crear_archivo_html(ruta_archivo: Path):
    filename = ruta_archivo.name
    origen = finished_pages / filename
    if origen.exists():
        contenido = origen.read_text(encoding="utf-8")
    else:
        contenido = unfinished_template.read_text(encoding="utf-8")
    ruta_archivo.write_text(contenido, encoding="utf-8")

def generar_nav_superior(primer_nivel: list) -> str:
    html = ""
    for carpeta in primer_nivel:
        html += f'<a href="{carpeta.ruta_web}">{carpeta.nombre.capitalize()}</a>\n'
    return html

def generar_sidebar(carpeta: CarpetaInfo) -> str:
    html = ""
    # Subcarpetas
    for sub in carpeta.subcarpetas:
        if sub.nombre == carpeta.nombre:
            html += f'    <li>{sub.nombre.capitalize()}</li>\n'
        else:
            html += f'    <li><a href="{sub.ruta_web}">{formatear_nombre_carpeta(sub.nombre)}</a></li>\n'
    # Archivos
    for archivo in carpeta.archivos:
        html += f'    <li><a href="{carpeta.ruta_web}{archivo}">{formatear_nombre_archivo(archivo)}</a></li>\n'
    return html

def crear_index(carpeta: CarpetaInfo, nav_html: str):
    index_path = carpeta.ruta_fisica / "index.html"

    # ============================
    # 1) Intentar usar versión personalizada desde finishedPages
    # ============================
    nombre_convertido = convertir_ruta_a_nombre_archivo(carpeta.ruta_web)
    ruta_personalizada = finished_pages / nombre_convertido

    if ruta_personalizada.exists():
        contenido = ruta_personalizada.read_text(encoding="utf-8")
        index_path.write_text(contenido, encoding="utf-8")
        return  # ← Usamos versión personalizada. NO generamos nada más.

    # ============================
    # 2) Si no existe, usamos plantilla generada por el script
    # ============================
    sidebar_html = generar_sidebar(carpeta)

    nombre_formateado = formatear_nombre_carpeta(carpeta.nombre)

    titulo_html = (
        f'<h2>{nombre_formateado}</h2>\n'
        f'<h2 class="titulo-carpeta">Navegación</h2>\n'
        f'<ul>\n'
    )

    contenido = (
        HEADER_TEMPLATE.replace("{NAV_ENLACES}", nav_html)
        + titulo_html
        + sidebar_html
        + FOOTER
    )

    index_path.write_text(contenido, encoding="utf-8")


def procesar_arbol(carpeta: CarpetaInfo, nav_html: str):
    # Crear HTML de archivos
    for archivo in carpeta.archivos:
        ruta_archivo = carpeta.ruta_fisica / archivo
        crear_archivo_html(ruta_archivo)

    # Crear index.html
    crear_index(carpeta, nav_html)

    # Recursión en subcarpetas
    for sub in carpeta.subcarpetas:
        procesar_arbol(sub, nav_html)

# ==============================
# CREAR ÁRBOL DESDE datos.txt
# ==============================
stack_rutas = [ruta_base]
stack_info = [CarpetaInfo(ruta_base, "/", "")]
nombre = ""

for c in texto:
    if c == '{':
        nombre_limpio = nombre.strip()
        if nombre_limpio:
            nueva_ruta = stack_rutas[-1] / nombre_limpio
            nueva_ruta.mkdir(exist_ok=True)
            if stack_info[-1].ruta_web == "/":
                nueva_web = "/" + nombre_limpio + "/"
            else:
                nueva_web = stack_info[-1].ruta_web + nombre_limpio + "/"
            stack_info[-1].subcarpetas.append(CarpetaInfo(nueva_ruta, nueva_web, nombre_limpio))
            stack_rutas.append(nueva_ruta)
            stack_info.append(stack_info[-1].subcarpetas[-1])
        nombre = ""
    elif c == '}':
        nombre_limpio = nombre.strip()
        if nombre_limpio:
            if '.' in nombre_limpio:
                archivo_path = stack_rutas[-1] / nombre_limpio
                stack_info[-1].archivos.append(nombre_limpio)
                crear_archivo_html(archivo_path)
            else:
                nueva_ruta = stack_rutas[-1] / nombre_limpio
                nueva_ruta.mkdir(exist_ok=True)
                stack_info[-1].subcarpetas.append(CarpetaInfo(nueva_ruta, stack_info[-1].ruta_web + nombre_limpio + "/", nombre_limpio))
        nombre = ""
        if len(stack_info) > 1:
            stack_rutas.pop()
            stack_info.pop()
    elif c == ',':
        nombre_limpio = nombre.strip()
        if nombre_limpio:
            if '.' in nombre_limpio:
                archivo_path = stack_rutas[-1] / nombre_limpio
                stack_info[-1].archivos.append(nombre_limpio)
                crear_archivo_html(archivo_path)
            else:
                nueva_ruta = stack_rutas[-1] / nombre_limpio
                nueva_ruta.mkdir(exist_ok=True)
                stack_info[-1].subcarpetas.append(CarpetaInfo(nueva_ruta, stack_info[-1].ruta_web + nombre_limpio + "/", nombre_limpio))
        nombre = ""
    else:
        nombre += c

# ==============================
# GENERAR index.html PARA TODOS LOS IDIOMAS
# ==============================
for idioma in stack_info[0].subcarpetas:
    nav_superior_html = generar_nav_superior(idioma.subcarpetas)
    procesar_arbol(idioma, nav_superior_html)

# ==============================
# CREAR robots.txt
# ==============================
rutas_disallow = []

def registrar_rutas(carpeta: CarpetaInfo):
    for archivo in carpeta.archivos:
        ruta = carpeta.ruta_web + archivo
        rutas_disallow.append(ruta)
    for sub in carpeta.subcarpetas:
        rutas_disallow.append(sub.ruta_web)
        registrar_rutas(sub)

# Registrar TODAS las rutas de TODOS los idiomas
for idioma in stack_info[0].subcarpetas:
    registrar_rutas(idioma)

robots_path = ruta_base / "robots.txt"
with robots_path.open("w", encoding="utf-8") as robots:
    robots.write("User-agent: *\n")
    for ruta in rutas_disallow:
        robots.write(f"Disallow: {ruta}\n")
    robots.write("Allow: /\n")
    robots.write("Sitemap: https://bigflod.github.io/sitemap.xml\n")

print("Carpetas, index.html, archivos y robots.txt creados correctamente.")
input("Press Enter to exit...")


