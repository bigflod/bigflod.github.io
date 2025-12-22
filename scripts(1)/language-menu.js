/*
// ============================================
// 1) Diccionario de slugs por idioma
// ============================================
const dictionary = {
    es: {
        "inicio": "home",
        "algoritmos": "algorithms",
        "estructuras": "data",
        "de-datos": "structures",
        "arbol-binario": "binary-tree",
        "ordenamiento": "sorting",
        "teoria": "theory",
        "grafos": "graphs",
        "consultas": "queries",
        "group-by": "group-by",
        "sql": "sql"
    },
    en: {
        "home": "inicio",
        "algorithms": "algoritmos",
        "data": "estructuras",
        "structures": "de-datos",
        "binary-tree": "arbol-binario",
        "sorting": "ordenamiento",
        "theory": "teoria",
        "graphs": "grafos",
        "queries": "consultas",
        "group-by": "group-by",
        "sql": "sql"
    },
    fr: {
        "accueil": "inicio",
        "algorithmes": "algoritmos",
        "structures": "estructuras",
        "de-donnees": "de-datos",
        "arbre-binaire": "arbol-binario",
        "tri": "ordenamiento",
        "theorie": "teoria",
        "graphes": "grafos",
        "requêtes": "consultas",
        "group-by": "group-by",
        "sql": "sql"
    },
    it: {
        "home": "inicio",
        "algoritmi": "algoritmos",
        "strutture": "estructuras",
        "dati": "de-datos",
        "albero-binario": "arbol-binario",
        "ordinamento": "ordenamiento",
        "teoria": "teoria",
        "grafi": "grafos",
        "query": "consultas",
        "group-by": "group-by",
        "sql": "sql"
    }
};

// ============================================
// 2) Popup: abrir/cerrar
// ============================================
function toggleLanguageMenu() {
    const menu = document.getElementById("languageMenu");
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

// Cerrar si se hace clic fuera
document.addEventListener("click", (e) => {
    const menu = document.getElementById("languageMenu");
    const icon = document.querySelector(".language-menu-icon");
    if (!menu.contains(e.target) && e.target !== icon) {
        menu.style.display = "none";
    }
});

// ============================================
// 3) Obtener idioma actual desde la URL
// ============================================
function getCurrentLanguage(path) {
    const parts = path.split("/").filter(p => p !== "");
    return parts[0]; // es, en, fr, it
}

// ============================================
// 4) Traducir slugs
// ============================================
function translatePathSegments(segments, langFrom, langTo) {
    return segments.map(seg => {
        const dict = dictionary[langFrom];
        if (!dict) return seg;
        return dict[seg] || seg;
    });
}

// ============================================
// 5) Cambiar idioma manteniendo la sección exacta
// ============================================
function changeLanguage(newLang) {
    const path = window.location.pathname;
    const parts = path.split("/").filter(p => p !== "");

    if (parts.length === 0) return;

    const currentLang = parts[0];
    const rest = parts.slice(1);

    const translated = translatePathSegments(rest, currentLang, newLang);

    const newPath = "/" + [newLang, ...translated].join("/");

    window.location.href = newPath;
}
*/

// ======================================================
// Alternar visibilidad del menú con animación
// ======================================================
function toggleLanguageMenu() {
    const menu = document.getElementById("languageMenu");

    if (menu.classList.contains("active")) {
        menu.classList.remove("active");
        setTimeout(() => menu.style.display = "none", 150);
    } else {
        menu.style.display = "block";
        setTimeout(() => menu.classList.add("active"), 10);
    }
}

// ======================================================
// Cerrar menú si se hace clic fuera
// ======================================================
document.addEventListener("click", (e) => {
    const menu = document.getElementById("languageMenu");
    const icon = document.querySelector(".language-menu-icon");

    if (!menu.contains(e.target) && e.target !== icon) {
        if (menu.classList.contains("active")) {
            toggleLanguageMenu();
        }
    }
});

// ======================================================
// Redirigir a la misma página en otro idioma
// ======================================================
function goToLanguage(newLang) {
    const path = window.location.pathname.split("/").filter(p => p !== "");
    const currentLang = path[0];

    // Si por alguna razón la URL no tiene /lang/, no hacemos nada
    if (!currentLang) return;

    const rest = path.slice(1);
    const newPath = "/" + newLang + "/" + rest.join("/");

    window.location.href = newPath;
}
