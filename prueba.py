'''
from pathlib import Path
import os

# ==============================
# CONFIG
# ==============================
DOMAIN = "https://bigflod.github.io"  # dominio que me pediste
SITEMAPS_DIRNAME = "sitemaps"

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
        <!-- Botón hamburguesa (abre/cierra sidebars) -->
        <button id="menuToggle" class="menu-toggle" aria-label="Abrir paneles" aria-expanded="false">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- LOGO -->
        <a href="/es/" class="logo">
            <img src="/assets/logo.webp" alt="Logo" height="40">
        </a>

        <!-- Enlaces dinámicos de primer nivel -->
        <div class="nav-links">
            {NAV_ENLACES}
        </div>

        <!-- (Opcional) espacio para iconos a la derecha si los quieres -->
    </nav>

    <!-- Overlay que oscurece ligeramente la página cuando se abren los paneles -->
    <div id="pageOverlay" class="page-overlay" aria-hidden="true"></div>

    <!-- ============ CONTENEDOR DE 3 COLUMNAS ============ -->
    <div class="page-layout">
        <!-- SIDEBAR IZQUIERDA -->
        <aside class="sidebar-left" aria-hidden="true">
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

        <!-- SIDEBAR DERECHA (Ajustes) -->
        <aside class="sidebar-right" aria-hidden="true">
            <h2>Ajustes</h2>

            <div class="setting-block">
                <h3>Idiomas</h3>
                <div class="language-entry">
                    <img src="/assets/language-icon.webp" alt="Idiomas" height="20">
                    <span class="language-label">Idiomas</span>
                    <!-- Si quieres, aquí puedes añadir botones con onclick="changeLanguage('es')" -->
                </div>
            </div>

            <div class="setting-block">
                <h3>Modo</h3>
                <!-- Botón modo oscuro / claro -->
                <button id="darkModeBtn" class="dark-mode-button" title="Usar modo oscuro">
                    <img id="darkModeIcon" src="/assets/moon-icon.webp" alt="Dark mode icon" height="24">
                </button>
            </div>
        </aside>
    </div>

    <!-- ============ SCRIPTS ============ -->
    <script>
        (function(){
            // ---------- Helpers ----------
            function qs(sel){ return document.querySelector(sel); }
            function qsa(sel){ return Array.from(document.querySelectorAll(sel)); }

            // ---------- Toggle Paneles (hamburger) ----------
            const menuToggle = document.getElementById('menuToggle');
            const pageOverlay = document.getElementById('pageOverlay');

            function openPanels() {
                document.body.classList.add('panels-open');
                menuToggle.classList.add('open');
                menuToggle.setAttribute('aria-expanded', 'true');
                pageOverlay.setAttribute('aria-hidden', 'false');
                pageOverlay.style.display = 'block';
            }
            function closePanels() {
                document.body.classList.remove('panels-open');
                menuToggle.classList.remove('open');
                menuToggle.setAttribute('aria-expanded', 'false');
                pageOverlay.setAttribute('aria-hidden', 'true');
                pageOverlay.style.display = 'none';
            }
            function togglePanels(){
                if(document.body.classList.contains('panels-open')) closePanels();
                else openPanels();
            }

            menuToggle.addEventListener('click', togglePanels);
            pageOverlay.addEventListener('click', closePanels);
            document.addEventListener('keydown', function(e){
                if(e.key === 'Escape') closePanels();
            });

            // ---------- Toggle language menu (si sigues usando un popup) ----------
            window.toggleLanguageMenu = function() {
                const menu = document.getElementById("languageMenu");
                if (!menu) return;
                menu.style.display = menu.style.display === "flex" ? "none" : "flex";
            }

            window.changeLanguage = function(lang) {
                const current = window.location.pathname;
                const parts = current.split("/");
                parts[1] = lang;
                window.location.href = parts.join("/");
            }

            // ---------- Dark mode toggle (y cambiar icono) ----------
            function setDarkIcon(isDark){
                const icon = document.getElementById("darkModeIcon");
                const btn = document.getElementById("darkModeBtn");
                if(!icon || !btn) return;
                if(isDark){
                    icon.src = "/assets/sun-icon.svg";
                    icon.alt = "Modo claro";
                    btn.title = "Usar modo claro";
                } else {
                    icon.src = "/assets/moon-icon.svg";
                    icon.alt = "Modo oscuro";
                    btn.title = "Usar modo oscuro";
                }
            }

            window.toggleDarkMode = function(){
                document.body.classList.toggle("dark-mode");
                setDarkIcon(document.body.classList.contains("dark-mode"));
            }

            // inicializar icono según estado
            document.addEventListener('DOMContentLoaded', function(){
                setDarkIcon(document.body.classList.contains('dark-mode'));
            });

        })();
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
        self.ruta_web = ruta_web  # ej "/es/java/"
        self.nombre = nombre
        self.subcarpetas = []
        self.archivos = []

# ==============================
# SITEMAPS (colección)
# ==============================
# mapeo idioma -> set(urls)
sitemaps_por_idioma = {}

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

    if ruta == "":
        return "index.html"

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

def obtener_idioma_de_ruta(ruta_web: str) -> str:
    """Devuelve el primer segmento después de la barra: '/es/java/' -> 'es'"""
    ruta = ruta_web.strip("/")
    if not ruta:
        return ""
    return ruta.split("/")[0]

def registrar_url_en_sitemap(carpeta: CarpetaInfo, url_relativa: str):
    """
    Añade una URL relativa (por ejemplo '/es/java/archivo.html' o '/es/') al sitemap del idioma.
    """
    idioma = obtener_idioma_de_ruta(carpeta.ruta_web)
    if idioma == "":
        return
    if idioma not in sitemaps_por_idioma:
        sitemaps_por_idioma[idioma] = set()
    # Aseguramos que url_relativa empiece y termine correctamente con '/'
    # Si es archivo (contiene '.html') no añadimos '/' al final.
    if url_relativa.startswith("/"):
        url = url_relativa
    else:
        url = "/" + url_relativa
    sitemaps_por_idioma[idioma].add(url)

def crear_archivo_html(carpeta: CarpetaInfo, filename: str):
    """
    Ahora recibe la CarpetaInfo y el nombre de archivo (ej 'mergesort.html').
    Si existe finished_pages/<filename> lo copia y registra la URL en el sitemap del idioma.
    Si no existe, usa unfinished_template.
    """
    ruta_archivo = carpeta.ruta_fisica / filename
    origen = finished_pages / filename
    if origen.exists():
        contenido = origen.read_text(encoding="utf-8")
        ruta_archivo.write_text(contenido, encoding="utf-8")
        # Registrar en sitemap del idioma correspondiente
        url_relativa = carpeta.ruta_web + filename  # '/es/java/' + 'mergesort.html'
        registrar_url_en_sitemap(carpeta, url_relativa)
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
        # Registrar la ruta base del idioma/carpeta en el sitemap (por ejemplo '/es/java/')
        # Para index preferimos registrar la carpeta sin "index.html": '/es/java/'
        url_relativa = carpeta.ruta_web
        registrar_url_en_sitemap(carpeta, url_relativa)
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
        crear_archivo_html(carpeta, archivo)

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
            nueva_info = CarpetaInfo(nueva_ruta, nueva_web, nombre_limpio)
            stack_info[-1].subcarpetas.append(nueva_info)
            stack_rutas.append(nueva_ruta)
            stack_info.append(nueva_info)
        nombre = ""
    elif c == '}':
        nombre_limpio = nombre.strip()
        if nombre_limpio:
            if '.' in nombre_limpio:
                # archivo dentro del nivel
                archivo_path = stack_rutas[-1] / nombre_limpio
                stack_info[-1].archivos.append(nombre_limpio)
                # crear archivo usando la CarpetaInfo actual
                crear_archivo_html(stack_info[-1], nombre_limpio)
            else:
                nueva_ruta = stack_rutas[-1] / nombre_limpio
                nueva_ruta.mkdir(exist_ok=True)
                stack_info[-1].subcarpetas.append(CarpetaInfo(nueva_ruta, stack_info[-1].ruta_web + nombre_limpio + "/", nombre_limpio))
        nombre = ""
        if len(stack_info) > 1:
            # Aquí se cierra un nivel: si era un idioma raíz no hacemos nada especial ahora,
            # los sitemaps se crearán al final para todos los idiomas.
            stack_rutas.pop()
            stack_info.pop()
    elif c == ',':
        nombre_limpio = nombre.strip()
        if nombre_limpio:
            if '.' in nombre_limpio:
                archivo_path = stack_rutas[-1] / nombre_limpio
                stack_info[-1].archivos.append(nombre_limpio)
                crear_archivo_html(stack_info[-1], nombre_limpio)
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

# ==============================
# ESCRIBIR SITEMAPS
# ==============================
def escribir_sitemaps():
    # Crear carpeta sitemaps
    sitemaps_dir = ruta_base / SITEMAPS_DIRNAME
    sitemaps_dir.mkdir(exist_ok=True)

    # Generar sitemap por idioma
    archivos_generados = []
    for idioma, urls in sitemaps_por_idioma.items():
        if not urls:
            continue  # no hay urls para este idioma
        sitemap_fname = f"sitemap-{idioma}.xml"
        sitemap_path = sitemaps_dir / sitemap_fname
        archivos_generados.append(sitemap_fname)

        # ordenar URLs para consistencia
        urls_ordenadas = sorted(urls)

        with sitemap_path.open("w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n')
            for url in urls_ordenadas:
                f.write("  <url>\n")
                f.write(f"    <loc>{DOMAIN}{url}</loc>\n")
                f.write("  </url>\n\n")
            f.write('</urlset>\n')

    # Sitemap index (principal)
    sitemap_index_path = ruta_base / "sitemap.xml"
    with sitemap_index_path.open("w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n')
        for fname in sorted(archivos_generados):
            f.write("  <sitemap>\n")
            f.write(f"    <loc>{DOMAIN}/{SITEMAPS_DIRNAME}/{fname}</loc>\n")
            f.write("  </sitemap>\n\n")
        f.write('</sitemapindex>\n')

# Llamamos a la función que escribe sitemaps
escribir_sitemaps()

print("Carpetas, index.html, archivos y robots.txt creados correctamente.")
input("Press Enter to exit...")
'''

