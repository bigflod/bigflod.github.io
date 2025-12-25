// Combined JS: app.js
// Sources (concatenated in this order): menu.js, scroll.js, settings.js, theme.js

// menu.js
const hamburger = document.getElementById("hamburger");
const sideMenu = document.getElementById("sideMenu");
const overlay = document.getElementById("overlay");

// Only wire up the full side-menu behavior when the required elements exist.
if (hamburger && sideMenu && overlay) {
    hamburger.onclick = () => {
        // compute willOpen before toggling
        const willOpen = !sideMenu.classList.contains('open');
        if (willOpen) {
            // ensure page is scrolled to top so headers are fully visible when menu opens
            try { window.scrollTo({ top: 0, left: 0, behavior: 'auto' }); } catch (e) { window.scrollTo(0,0); }
        }
        const isOpen = sideMenu.classList.toggle("open");
        hamburger.classList.toggle("open", isOpen);
        hamburger.setAttribute('aria-expanded', String(isOpen));
        // show full-screen overlay (dims whole page below headers)
        document.body.classList.toggle('side-open', isOpen);
        overlay.classList.toggle("show", isOpen);
        // forward scroll/keys to sideMenu when open; do NOT modify body overflow
        if (isOpen) {
            addSideScrollHandlers();
        } else {
            removeSideScrollHandlers();
            // reset internal scroll so reopening starts at top
            try { sideMenu.scrollTop = 0; } catch (e) { /* ignore */ }
        }
    };

    overlay.onclick = () => {
        hamburger.classList.remove("open");
        sideMenu.classList.remove("open");
        overlay.classList.remove("show");
        // remove event handlers and body state
        removeSideScrollHandlers();
        document.body.classList.remove('side-open');
        hamburger.setAttribute('aria-expanded', 'false');
        // reset side menu internal scroll when closed
        try { sideMenu.scrollTop = 0; } catch (e) { /* ignore */ }
    };

    // Allow closing the side menu with Escape
    // (Escape key handler moved inside guarded menu block)
} else if (hamburger) {
    // If hamburger exists but menu/overlay are missing, hide the hamburger to avoid errors
    hamburger.style.display = 'none';
}


// scroll.js (synchronized with actual scroll delta)
const topHeader = document.getElementById("topHeader");
const subHeader = document.getElementById("subHeader");
let topHeaderH = topHeader ? topHeader.offsetHeight : 0;

const searchContainerSub = document.getElementById("searchContainerSub");
const searchCloseBtn = searchContainerSub ? searchContainerSub.querySelector(".closeBtn") : null;
const searchIconEl = searchContainerSub ? searchContainerSub.querySelector('.search-icon') : null;

function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

window.addEventListener('resize', () => { topHeaderH = topHeader ? topHeader.offsetHeight : 0; });

// Map header translation directly to scroll position to avoid lag/jitter.
window.addEventListener("scroll", () => {
    if (!topHeader || !subHeader) return;

    const scrollY = window.scrollY || 0;
    const translate = clamp(scrollY, 0, topHeaderH);

    topHeader.style.transform = `translateY(-${translate}px)`;
    subHeader.style.transform = `translateY(-${translate}px)`;
    // Show the small lupa icon in subHeader when the top header is fully hidden
    if (searchContainerSub) {
        if (translate >= topHeaderH) {
            // show only collapsed icon (do not expand input automatically)
            if (!searchContainerSub.classList.contains('expanded')) {
                searchContainerSub.classList.add('collapsed');
            }
            // clear top header search when top header is hidden
            const topInput = document.querySelector('#searchContainerTop input');
            if (topInput) topInput.value = '';
        } else {
            // hide the collapsed icon if user hasn't expanded
            if (!searchContainerSub.classList.contains('expanded')) {
                searchContainerSub.classList.remove('collapsed');
            }
            // If the subheader search was expanded and the user scrolled back to top
            // (so the top header is visible), force-close the subheader search and clear it.
            if (searchContainerSub.classList.contains('expanded')) {
                searchContainerSub.classList.remove('expanded');
                searchContainerSub.classList.add('collapsed');
                searchContainerSub.setAttribute('aria-hidden', 'true');
                const input = searchContainerSub.querySelector('input');
                if (input) input.value = '';
            }
        }
        // nothing else here — theme button is in top header now
    }
});

// Search toggle behavior: clicking lupa expands input (animated), close button collapses
if (searchIconEl) {
    searchIconEl.addEventListener('click', (e) => {
        const willExpand = !searchContainerSub.classList.contains('expanded');
        const themeBtn = document.getElementById('themeBtn');
        if (willExpand) {
            // opening: expand input, focus it, and shift theme icon left to match
            searchContainerSub.classList.add('expanded');
            searchContainerSub.classList.remove('collapsed');
            searchContainerSub.setAttribute('aria-hidden', 'false');
            const input = searchContainerSub.querySelector('input');
            if (input) setTimeout(() => { input.focus(); input.setSelectionRange(input.value.length, input.value.length); }, 180);
            // show close button in the same place as the icon (CSS handles visibility)
        } else {
            // closing: collapse and clear input
            searchContainerSub.classList.remove('expanded');
            searchContainerSub.classList.add('collapsed');
            searchContainerSub.setAttribute('aria-hidden', 'true');
            const input = searchContainerSub.querySelector('input');
            if (input) input.value = '';
            // no theme button animation required (it's in top header)
        }
    });
    // keyboard support (Enter / Space)
    searchIconEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
            e.preventDefault();
            searchIconEl.click();
        }
    });
}

if (searchCloseBtn) {
    searchCloseBtn.addEventListener('click', () => {
        searchContainerSub.classList.remove('expanded');
        searchContainerSub.classList.add('collapsed');
        const input = searchContainerSub.querySelector('input'); if (input) input.value = '';
    });
    searchCloseBtn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
            e.preventDefault();
            searchCloseBtn.click();
        }
    });
}

// NOTE: sub-hamburger removed — subheader only shows the lupa/search.


// THEME button moved to subHeader. Keep only theme toggle logic and remove settings/language code.
const themeBtn = document.getElementById("themeBtn");
const themeIcon = document.getElementById("themeIcon");
const prismLink = document.getElementById("prism-theme");

// Persisted theme preference key (shared with search.html)
const THEME_KEY = 'theme_pref_v1';

// Apply saved preference on load (default to light)
try {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme === 'dark') {
        document.body.classList.add('dark');
    } else if (savedTheme === 'light') {
        document.body.classList.remove('dark');
    }
} catch (e) { /* ignore localStorage errors */ }

// Initialize theme icon based on current state
if (themeIcon) {
    if (document.body.classList.contains('dark')) {
        themeIcon.src = '/assets/sun-icon.svg';
        themeBtn && themeBtn.setAttribute('data-tooltip', 'Cambiar a Modo Claro');
        prismLink.href = "https://cdn.jsdelivr.net/npm/prismjs@1.30.0/themes/prism-okaidia.css"; // tema oscuro
    } else {
        themeIcon.src = '/assets/moon-icon.svg';
        themeBtn && themeBtn.setAttribute('data-tooltip', 'Cambiar a Modo Oscuro');
        prismLink.href = "https://cdn.jsdelivr.net/npm/prismjs@1.30.0/themes/prism.css"; // tema claro
    }
}

if (themeBtn) {
    themeBtn.onclick = () => {
        const dark = document.body.classList.toggle('dark');
        if (dark) {
            themeIcon.src = '/assets/sun-icon.svg';
            themeBtn.setAttribute('data-tooltip', 'Cambiar a Modo Claro');
            prismLink.href = "https://cdn.jsdelivr.net/npm/prismjs@1.30.0/themes/prism-okaidia.css"; // tema oscuro
        } else {
            themeIcon.src = '/assets/moon-icon.svg';
            themeBtn.setAttribute('data-tooltip', 'Cambiar a Modo Oscuro');
            prismLink.href = "https://cdn.jsdelivr.net/npm/prismjs@1.30.0/themes/prism.css"; // tema claro
        }

        try { localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light'); } catch (e) {}

        // close side menu / overlay when toggling theme for a clean state
        hamburger.classList.remove('open');
        sideMenu.classList.remove('open');
        overlay.classList.remove('show');
        removeSideScrollHandlers();
        document.body.classList.remove('side-open');

        // update copy button icons to match theme
        const copyImgs = document.querySelectorAll('.copy-btn img');
        copyImgs.forEach(img => {
            if (!img.dataset.isTick) {
                img.src = document.body.classList.contains('dark') ? '/assets/copy-icon-modo-oscuro.svg' : '/assets/copy-icon-modo-claro.svg';
            }
        });
    };

    // keyboard support
    themeBtn.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); themeBtn.click(); } });
}

// Wrap top nav link letters in spans to create wave animation on hover
function wrapTopLinkLetters() {
    const links = document.querySelectorAll('.top-links a');
    links.forEach(link => {
        // skip if already wrapped
        if (link.dataset.wrapped) return;
        const text = link.textContent.trim();
        link.textContent = '';
        const fragment = document.createDocumentFragment();
        Array.from(text).forEach((ch, i) => {
            const span = document.createElement('span');
            span.className = 'char';
            span.textContent = ch === ' ' ? '\u00A0' : ch;
            span.style.display = 'inline-block';
            span.style.transition = 'transform .32s cubic-bezier(.2,.9,.3,1), color .28s';
            span.style.transitionDelay = `${i * 0.04}s`;
            fragment.appendChild(span);
        });
        link.appendChild(fragment);
        link.dataset.wrapped = '1';
    });
}

document.addEventListener('DOMContentLoaded', () => {
    wrapTopLinkLetters();
});

// initialize breadcrumb links in subheader
document.addEventListener('DOMContentLoaded', () => {
    const crumbs = Array.from(document.querySelectorAll('.sub-crumbs .crumb')).map(n => n.textContent.trim());
    const crumbEls = document.querySelectorAll('.sub-crumbs .crumb');
    function currentLang() { return document.documentElement.lang || 'es'; }
    crumbEls.forEach((el, idx) => {
        el.addEventListener('click', () => {
            const lang = currentLang();
            const parts = crumbs.slice(0, idx + 1).map(encodeURIComponent).join('/');
            const href = `/${lang}/${parts}`;
            window.location.href = href;
        });
    });
});

function setupCopyButtons() {
    const pres = document.querySelectorAll('.content pre');

    pres.forEach(pre => {
        if (pre.dataset.copyInit) return;
        pre.dataset.copyInit = '1';

        pre.style.position = pre.style.position || 'relative';

        const btn = document.createElement('button');
        btn.className = 'copy-btn';

        const img = document.createElement('img');
        img.alt = 'Copiar';

        // función para icono de copiar según tema
        const getCopyIcon = () =>
            document.body.classList.contains('dark')
                ? '/assets/copy-icon-modo-oscuro.svg'
                : '/assets/copy-icon-modo-claro.svg';

        const getTickIcon = () =>
            document.body.classList.contains('dark')
                ? '/assets/tick-icon-modo-oscuro.svg'
                : '/assets/tick-icon-modo-claro.svg';

        img.src = getCopyIcon();
        btn.appendChild(img);

        const feedback = document.createElement('div');
        feedback.className = 'copy-feedback';
        feedback.textContent = 'Copiado!';

        pre.appendChild(btn);
        pre.appendChild(feedback);

        btn.addEventListener('click', async () => {
            try {
                const clone = pre.cloneNode(true);
                clone.querySelectorAll('.copy-btn, .copy-feedback')
                    .forEach(n => n.remove());

                const codeText = clone.innerText.trim();
                await navigator.clipboard.writeText(codeText);

                // mostrar tick
                img.src = getTickIcon();
                feedback.classList.add('show');

                // cancelar timeout anterior
                if (img._copyTimeout) {
                    clearTimeout(img._copyTimeout);
                }

                // restaurar icono correcto según tema ACTUAL
                img._copyTimeout = setTimeout(() => {
                    img.src = getCopyIcon();
                    feedback.classList.remove('show');
                }, 1500);

            } catch (err) {
                console.error('copy failed', err);
            }
        });
    });
}


/*
// Add copy buttons to code blocks and handle copy action
function setupCopyButtons() {
    const pres = document.querySelectorAll('.content pre');

    pres.forEach(pre => {
        // evitar duplicados
        if (pre.dataset.copyInit) return;
        pre.dataset.copyInit = '1';

        // asegurar posición
        pre.style.position = pre.style.position || 'relative';

        // botón copiar
        const btn = document.createElement('button');
        btn.className = 'copy-btn';

        const img = document.createElement('img');
        img.src = document.body.classList.contains('dark')
            ? 'assets/copy-icon-modo-oscuro.svg'
            : 'assets/copy-icon-modo-claro.svg';
        img.alt = 'Copiar';

        // guardar icono original UNA VEZ
        img.dataset.originalSrc = img.src;

        btn.appendChild(img);

        // feedback
        const feedback = document.createElement('div');
        feedback.className = 'copy-feedback';
        feedback.textContent = 'Copiado!';

        pre.appendChild(btn);
        pre.appendChild(feedback);

        btn.addEventListener('click', async () => {
            try {
                // copiar texto sin botón ni feedback
                const clone = pre.cloneNode(true);
                clone.querySelectorAll('.copy-btn, .copy-feedback')
                    .forEach(n => n.remove());

                const codeText = clone.innerText.trim();
                await navigator.clipboard.writeText(codeText);

                // icono tick según tema
                const tick = document.body.classList.contains('dark')
                    ? 'assets/tick-icon-modo-oscuro.svg'
                    : 'assets/tick-icon-modo-claro.svg';

                // mostrar feedback
                img.src = tick;
                feedback.classList.add('show');

                // cancelar timeout anterior
                if (img._copyTimeout) {
                    clearTimeout(img._copyTimeout);
                }

                // restaurar estado
                img._copyTimeout = setTimeout(() => {
                    img.src = img.dataset.originalSrc;
                    feedback.classList.remove('show');
                }, 1500);

            } catch (err) {
                console.error('copy failed', err);
            }
        });
    });
}
*/
document.addEventListener('DOMContentLoaded', setupCopyButtons);

// The previous dynamic sub-links bounding logic has been removed because
// the subheader now uses normal centered links. No-op placeholder kept for
// backward compatibility if other code references it.
function updateSubLinksBounds() { /* removed - sub-links use normal flow */ }

// --- Side menu scroll forwarding when open ---
let _touchStartY = 0;
function onWheelForwardToSide(e) {
    if (!sideMenu.classList.contains('open')) return;
    e.preventDefault();
    sideMenu.scrollTop += e.deltaY;
}
function onTouchStart(e) { _touchStartY = e.touches ? e.touches[0].clientY : e.clientY; }
function onTouchMoveForward(e) {
    if (!sideMenu.classList.contains('open')) return;
    const y = e.touches ? e.touches[0].clientY : e.clientY;
    const delta = _touchStartY - y;
    if (Math.abs(delta) > 0) {
        e.preventDefault();
        sideMenu.scrollTop += delta;
        _touchStartY = y;
    }
}
function addSideScrollHandlers() {
    document.addEventListener('wheel', onWheelForwardToSide, { passive: false });
    document.addEventListener('touchstart', onTouchStart, { passive: false });
    document.addEventListener('touchmove', onTouchMoveForward, { passive: false });
    document.addEventListener('keydown', onKeyForwardToSide, { passive: false });
}
function removeSideScrollHandlers() {
    document.removeEventListener('wheel', onWheelForwardToSide, { passive: false });
    document.removeEventListener('touchstart', onTouchStart, { passive: false });
    document.removeEventListener('touchmove', onTouchMoveForward, { passive: false });
    document.removeEventListener('keydown', onKeyForwardToSide, { passive: false });
}

function onKeyForwardToSide(e) {
    if (!sideMenu.classList.contains('open')) return;
    const step = Math.max(40, Math.round(sideMenu.clientHeight * 0.6));
    switch (e.key) {
        case 'ArrowDown': sideMenu.scrollTop += 40; e.preventDefault(); break;
        case 'ArrowUp': sideMenu.scrollTop -= 40; e.preventDefault(); break;
        case 'PageDown': sideMenu.scrollTop += step; e.preventDefault(); break;
        case 'PageUp': sideMenu.scrollTop -= step; e.preventDefault(); break;
        case 'Home': sideMenu.scrollTop = 0; e.preventDefault(); break;
        case 'End': sideMenu.scrollTop = sideMenu.scrollHeight; e.preventDefault(); break;
    }
}

// --- Simple search redirect: both inputs with class .search-input navigate to search.html?q=... on Enter ---
function setupSearchBars() {
    const searchBars = document.querySelectorAll('.search-input');
    searchBars.forEach(bar => {
        // avoid double-binding
        if (bar.dataset.searchInit) return;
        bar.dataset.searchInit = '1';
        bar.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const q = this.value.trim();
                if (!q) return;
                const query = encodeURIComponent(q);
                // navigate to search page (absolute path)
                window.location.href = `/search.html?q=${query}`;
            }
        });
    });
}


//TODO: quitar? //Era para cambiar clase del subheader al abrir/cerrar búsqueda
/*
window.addEventListener("DOMContentLoaded", () => {
    const searchSub = document.getElementById('searchContainerSub');
    const subHeader = document.getElementById('subHeader');

    if (searchSub && subHeader) {
        const observer = new MutationObserver(() => {
            if (searchSub.classList.contains('expanded')) {
                subHeader.classList.add('search-open');
            } else {
                subHeader.classList.remove('search-open');
            }
        });

        observer.observe(searchSub, { attributes: true, attributeFilter: ['class'] });
    }
});
*/
//TODO: quitar?

document.addEventListener('DOMContentLoaded', setupSearchBars);

document.addEventListener('DOMContentLoaded', () => {
    if (!window.Prism) {
        console.error('Prism NO está cargado');
        return;
    }

    const blocks = document.querySelectorAll('pre code');
    console.log('Bloques encontrados:', blocks.length);

    Prism.highlightAll();
});