// =============================
// Menú lateral hamburguesa
// =============================
const menuToggle = document.getElementById("menuToggle");
const body = document.body;

menuToggle.addEventListener("click", () => {
    menuToggle.classList.toggle("open");
    body.classList.toggle("sidebars-open");
});

// =============================
// Idiomas popup
// =============================
function toggleLanguageMenu() {
    const menu = document.getElementById("languageMenu");
    menu.style.display = menu.style.display === "flex" ? "none" : "flex";
}

function changeLanguage(lang) {
    const current = window.location.pathname.split("/");
    current[1] = lang;
    window.location.href = current.join("/");
}

// =============================
// Dark mode
// =============================
function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");

    const icon = document.getElementById("darkModeIcon");
    const button = document.getElementById("darkModeBtn");

    if (document.body.classList.contains("dark-mode")) {
        icon.src = "/assets/sun-icon.webp";
        icon.alt = "Light mode icon";
        button.title = "Use Light Mode";
    } else {
        icon.src = "/assets/moon-icon.webp";
        icon.alt = "Dark mode icon";
        button.title = "Use Dark Mode";
    }
}

// =============================
// Debug
// =============================
console.log("Sitio cargado correctamente");
