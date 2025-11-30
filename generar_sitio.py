#!/usr/bin/env python3
# generar_sitio.py
# Genera estructura del sitio desde datos.txt, copia páginas desde finishedPages,
# inyecta referencias a /estilos/main.css y /scripts/main.js si faltan,
# escribe robots.txt y sitemaps por idioma + sitemap index.

from pathlib import Path
import re
import os
import sys

# ============== CONFIG ==============
DOMAIN = "https://bigflod.github.io"
SITEMAPS_DIRNAME = "sitemaps"

ruta_base = Path.cwd()
finished_pages = ruta_base / "finishedPages"
unfinished_template = ruta_base / "unfinishedPage.html"
datos_path = ruta_base / "datos.txt"

if not datos_path.exists():
    print("Error: no se encontró 'datos.txt' en la carpeta actual.")
    sys.exit(1)

texto = datos_path.read_text(encoding="utf-8")

# ============== UTILIDADES ==============
def convertir_ruta_a_nombre_archivo(ruta_web: str) -> str:
    """
    /es/java/ -> es-java.html? (index -> es-index.html is not wanted)
    Spec: /es/ -> index.html when writing file names in finishedPages the earlier convention
    used was: /es/ -> es-index.html? But earlier you required es-index.html only when checking finishedPages.
    To keep compatibility with your previous behavior we map:
      - '/es/' -> es-index.html  (so finishedPages/es-index.html)
      - '/es/alg/' -> es-alg.html? Earlier you used full segments and appended .html:
        Example desired: /en/algorithms/sorting/mergesort.html -> en-algorithms-sorting-mergesort.html
    We'll convert like this:
    - Strip leading slash
    - If ruta ends with '.html' strip '.html'
    - For directory path (ending with '/'), we join segments and append '-index' ? Earlier you used 'es-index.html' for /es/index.html?
      To avoid ambiguity we will:
        - If ruta points to a directory (no '.html' present): join parts and append '.html' (so /es/ -> 'es.html')
          BUT you previously wanted 'es-index.html'. To be safe choose the exact rule you specified earlier:
          **You specified earlier:** "/es/index.html -> es-index.html; /es/ -> es-index.html" in examples.
    So implement: if ruta == "" then return "index.html" (for generic) but for finishedPages lookup we create mapping:
    Build name: join(parts) ; if last segment is empty or ruta endswith '/', append 'index' to parts before join.
    Then return joined + '.html'
    """
    r = ruta_web.strip("/")
    # if r empty, represent root dir -> "index.html"
    if r == "":
        return "index.html"
    # if ends with .html, strip extension
    if r.endswith(".html"):
        r = r[:-5]
    parts = [p for p in r.split("/") if p != ""]
    # If the original ruta_web ended with '/' (a directory), make sure to represent index:
    if ruta_web.endswith("/"):
        parts.append("index")
    # join with hyphen
    nombre = "-".join(parts) + ".html"
    return nombre

def ensure_resource_in_html(html: str) -> str:
    """
    Si falta <link rel="stylesheet" href="/estilos/main.css"> lo inserta antes de </head>.
    Si falta <script src="/scripts/main.js"></script> lo inserta antes de </body>.
    Hacemos búsquedas case-insensitive.
    """
    modified = html
    has_css = re.search(r'/estilos/main\.css', modified, flags=re.IGNORECASE) is not None
    has_js = re.search(r'/scripts/main\.js', modified, flags=re.IGNORECASE) is not None

    css_tag = '<link rel="stylesheet" href="/estilos/main.css">'
    js_tag = '<script src="/scripts/main.js"></script>'

    # insert CSS if missing
    if not has_css:
        # try to insert before closing head
        m = re.search(r'</head\s*>', modified, flags=re.IGNORECASE)
        if m:
            i = m.start()
            modified = modified[:i] + css_tag + "\n" + modified[i:]
        else:
            # prepend to document
            modified = css_tag + "\n" + modified

    # insert JS if missing
    if not has_js:
        m = re.search(r'</body\s*>', modified, flags=re.IGNORECASE)
        if m:
            i = m.start()
            modified = modified[:i] + js_tag + "\n" + modified[i:]
        else:
            modified = modified + "\n" + js_tag

    return modified

# Helper: format names for display
def formatear_nombre_carpeta(nombre: str) -> str:
    partes = nombre.split("-")
    return " ".join(p.capitalize() for p in partes)

def formatear_nombre_archivo(nombre_archivo: str) -> str:
    base = nombre_archivo.rsplit(".", 1)[0]
    partes = base.split("-")
    return " ".join(p.capitalize() for p in partes)

def obtener_idioma_de_ruta(ruta_web: str) -> str:
    ruta = ruta_web.strip("/")
    if not ruta:
        return ""
    return ruta.split("/")[0]

# sitemaps por idioma
sitemaps_por_idioma = {}

def registrar_url_en_sitemap(carpeta_ruta_web: str, url_relativa: str):
    idioma = obtener_idioma_de_ruta(carpeta_ruta_web)
    if idioma == "":
        return
    if idioma not in sitemaps_por_idioma:
        sitemaps_por_idioma[idioma] = set()
    url = url_relativa if url_relativa.startswith("/") else "/" + url_relativa
    sitemaps_por_idioma[idioma].add(url)

# ============== ESTRUCTURAS ==============
class CarpetaInfo:
    def __init__(self, ruta_fisica: Path, ruta_web: str, nombre: str):
        self.ruta_fisica = ruta_fisica
        self.ruta_web = ruta_web  # ej "/es/java/"
        self.nombre = nombre
        self.subcarpetas = []
        self.archivos = []

# ============== CREACION / COPIA DE ARCHIVOS ==============
def crear_archivo_html(carpeta: CarpetaInfo, filename: str):
    destino = carpeta.ruta_fisica / filename
    origen = finished_pages / filename
    if origen.exists():
        contenido = origen.read_text(encoding="utf-8")
        contenido = ensure_resource_in_html(contenido)
        destino.write_text(contenido, encoding="utf-8")
        # registrar ruta en sitemap (archivo)
        registrar_url_en_sitemap(carpeta.ruta_web, carpeta.ruta_web + filename)
    else:
        # si no existe, crear usando unfinished_template si está presente
        if unfinished_template.exists():
            contenido = unfinished_template.read_text(encoding="utf-8")
            contenido = ensure_resource_in_html(contenido)
            destino.write_text(contenido, encoding="utf-8")
        else:
            # fallback mínimo
            minimal = ("<!doctype html><html><head>"
                       '<meta charset="utf-8">'
                       '<link rel="stylesheet" href="/estilos/main.css">'
                       "</head><body>"
                       "<main><h2>En construcción</h2></main>"
                       '<script src="/scripts/main.js"></script>'
                       "</body></html>")
            destino.write_text(minimal, encoding="utf-8")

def generar_nav_superior(primer_nivel: list) -> str:
    html = ""
    for carpeta in primer_nivel:
        html += f'            <a href="{carpeta.ruta_web}">{formatear_nombre_carpeta(carpeta.nombre)}</a>\n'
    return html

def generar_sidebar(carpeta: CarpetaInfo) -> str:
    html = ""
    for sub in carpeta.subcarpetas:
        if sub.nombre == carpeta.nombre:
            html += f'      <li>{formatear_nombre_carpeta(sub.nombre)}</li>\n'
        else:
            html += f'      <li><a href="{sub.ruta_web}">{formatear_nombre_carpeta(sub.nombre)}</a></li>\n'
    for archivo in carpeta.archivos:
        html += f'      <li><a href="{carpeta.ruta_web}{archivo}">{formatear_nombre_archivo(archivo)}</a></li>\n'
    return html

# Template HTML generado cuando no hay versión personalizada
HTML_TEMPLATE_SIMPLE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{TITLE}</title>
  <link rel="stylesheet" href="/estilos/main.css">
</head>
<body>

<nav class="navbar">
  <a class="logo" href="{LOGO_HREF}"><img src="/assets/logo.webp" alt="Logo" height="40"></a>
  <div class="nav-links">
{NAV_ENLACES}
  </div>
  <button id="menuToggle" class="menu-toggle" aria-label="Abrir paneles"><span class="bar1"></span><span class="bar2"></span><span class="bar3"></span></button>
</nav>

<div id="pageOverlay" class="page-overlay" style="display:none"></div>

<aside id="sidebar-left" class="sidebar">
  <h2 class="titulo-carpeta">{CARPETA_TITULO}</h2>
  <h2>Navegación</h2>
  <ul>
{SIDEBAR_HTML}
  </ul>
</aside>

<main>
{PAGE_CONTENT}
</main>

<aside id="sidebar-right" class="sidebar">
  <h2>Ajustes</h2>
  <div class="setting-block">
    <h3>Idiomas</h3>
    <div id="languageMenu" class="language-popup-menu" style="display:none">
      <button onclick="changeLanguage('es')">ES</button>
      <button onclick="changeLanguage('en')">EN</button>
      <button onclick="changeLanguage('fr')">FR</button>
      <button onclick="changeLanguage('it')">IT</button>
    </div>
  </div>
  <div class="setting-block">
    <h3>Modo</h3>
    <button id="darkModeBtn" class="dark-mode-button" title="Use Dark Mode">
      <img id="darkModeIcon" src="/assets/moon-icon.webp" alt="Dark mode icon" height="24">
    </button>
  </div>
</aside>

<div id="contentOverlay"></div>

<script src="/scripts/main.js"></script>
</body>
</html>
"""

def crear_index(carpeta: CarpetaInfo, nav_html: str):
    index_path = carpeta.ruta_fisica / "index.html"
    # comprobar si existe versión personalizada en finished_pages
    nombre_convertido = convertir_ruta_a_nombre_archivo(carpeta.ruta_web)
    ruta_personalizada = finished_pages / nombre_convertido

    if ruta_personalizada.exists():
        contenido = ruta_personalizada.read_text(encoding="utf-8")
        contenido = ensure_resource_in_html(contenido)
        index_path.write_text(contenido, encoding="utf-8")
        # registrar ruta base del directorio (como /es/java/)
        registrar_url_en_sitemap(carpeta.ruta_web, carpeta.ruta_web)
        return

    # si no hay personalizada, generar
    sidebar_html = generar_sidebar(carpeta)
    titulo = formatear_nombre_carpeta(carpeta.nombre) if carpeta.nombre else ""
    nav_links = nav_html
    page_content = (
        '<img src="/assets/construction-site.webp" width="280">\n'
        '<h2>Estamos trabajando en ello</h2>\n'
        f'<p>Sección <strong>{titulo}</strong> en construcción.</p>\n'
        f'<a href="{carpeta.ruta_web}" class="back-button">Volver atrás</a>\n'
    )
    html_final = HTML_TEMPLATE_SIMPLE.format(
        TITLE = titulo or "Sitio",
        LOGO_HREF = "/" + (obtener_idioma_de_ruta(carpeta.ruta_web) or "es") + "/",
        NAV_ENLACES = nav_links,
        CARPETA_TITULO = titulo,
        SIDEBAR_HTML = sidebar_html,
        PAGE_CONTENT = page_content
    )
    index_path.write_text(html_final, encoding="utf-8")
    registrar_url_en_sitemap(carpeta.ruta_web, carpeta.ruta_web)

def procesar_arbol(carpeta: CarpetaInfo, nav_html: str):
    # crear archivos
    for archivo in carpeta.archivos:
        crear_archivo_html(carpeta, archivo)
    # crear index
    crear_index(carpeta, nav_html)
    # recursión
    for sub in carpeta.subcarpetas:
        procesar_arbol(sub, nav_html)

# ============== PARSING datos.txt ==============
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
                crear_archivo_html(stack_info[-1], nombre_limpio)
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
                crear_archivo_html(stack_info[-1], nombre_limpio)
            else:
                nueva_ruta = stack_rutas[-1] / nombre_limpio
                nueva_ruta.mkdir(exist_ok=True)
                stack_info[-1].subcarpetas.append(CarpetaInfo(nueva_ruta, stack_info[-1].ruta_web + nombre_limpio + "/", nombre_limpio))
        nombre = ""
    else:
        nombre += c

# ================== GENERAR páginas para cada idioma (subcarpetas en primer nivel) ==================
if not stack_info[0].subcarpetas:
    print("Advertencia: no se encontraron subcarpetas de primer nivel en datos.txt (no hay idiomas).")
else:
    for idioma in stack_info[0].subcarpetas:
        nav_superior_html = generar_nav_superior(idioma.subcarpetas)
        procesar_arbol(idioma, nav_superior_html)

# ================== CREAR robots.txt ==================
rutas_disallow = []
def registrar_rutas(carpeta: CarpetaInfo):
    for archivo in carpeta.archivos:
        rutas_disallow.append(carpeta.ruta_web + archivo)
    for sub in carpeta.subcarpetas:
        rutas_disallow.append(sub.ruta_web)
        registrar_rutas(sub)

for idioma in stack_info[0].subcarpetas:
    registrar_rutas(idioma)

robots_path = ruta_base / "robots.txt"
with robots_path.open("w", encoding="utf-8") as robots:
    robots.write("User-agent: *\n")
    for ruta in sorted(set(rutas_disallow)):
        robots.write(f"Disallow: {ruta}\n")
    robots.write("Allow: /\n")
    robots.write(f"Sitemap: {DOMAIN}/{SITEMAPS_DIRNAME}/sitemap.xml\n")

# ================== ESCRIBIR SITEMAPS ==================
def escribir_sitemaps():
    sitemaps_dir = ruta_base / SITEMAPS_DIRNAME
    sitemaps_dir.mkdir(exist_ok=True)
    archivos_generados = []
    for idioma, urls in sitemaps_por_idioma.items():
        if not urls: continue
        sitemap_fname = f"sitemap-{idioma}.xml"
        sitemap_path = sitemaps_dir / sitemap_fname
        archivos_generados.append(sitemap_fname)
        with sitemap_path.open("w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n')
            for url in sorted(urls):
                f.write("  <url>\n")
                f.write(f"    <loc>{DOMAIN}{url}</loc>\n")
                f.write("  </url>\n\n")
            f.write('</urlset>\n')
    # index sitemap
    sitemap_index_path = ruta_base / "sitemap.xml"
    with sitemap_index_path.open("w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n')
        for fname in sorted(archivos_generados):
            f.write("  <sitemap>\n")
            f.write(f"    <loc>{DOMAIN}/{SITEMAPS_DIRNAME}/{fname}</loc>\n")
            f.write("  </sitemap>\n\n")
        f.write('</sitemapindex>\n')

escribir_sitemaps()

print("Generación finalizada: páginas, robots.txt y sitemaps creados.")
input("Press Enter to exit...")