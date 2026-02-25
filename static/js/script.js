document.addEventListener("DOMContentLoaded", function(){
    document.querySelectorAll(".barra-energia").forEach(function(barra){
        barra.style.width = barra.getAttribute("data-energia") + "%";
    });
});

// Evita múltiplos envios de formulários POST desabilitando o botão de submit
document.addEventListener("submit", function(e) {
    try {
        const form = e.target;
        if (form && form.method && form.method.toLowerCase() === 'post') {
            const btn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (btn && !btn.disabled) {
                // altera estado visual e desabilita para prevenir múltiplos cliques
                btn.disabled = true;
                if (btn.tagName.toLowerCase() === 'button') {
                    btn.dataset.__origText = btn.innerText;
                    btn.innerText = 'Enviando...';
                }
                // Caso algo dê errado, reabilita após 10s como fallback
                setTimeout(() => {
                    if (btn) {
                        btn.disabled = false;
                        if (btn.tagName.toLowerCase() === 'button' && btn.dataset.__origText) {
                            btn.innerText = btn.dataset.__origText;
                        }
                    }
                }, 10000);
            }
        }
    } catch (err) {
        // não propagar erro
        console.error('submit-handler error', err);
    }
}, true);

// Theme toggle: salva preferência em localStorage e aplica classe ao body
(function() {
    function applyTheme(theme) {
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(theme === 'light' ? 'theme-light' : 'theme-dark');
    }

    function initTheme() {
        const stored = localStorage.getItem('theme') || 'dark';
        applyTheme(stored);
        const btn = document.getElementById('themeToggle');
        if (btn) btn.textContent = stored === 'light' ? '🌙 Dark' : '🌞 Light';
    }

    function toggleTheme() {
        const current = document.body.classList.contains('theme-light') ? 'light' : 'dark';
        const next = current === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', next);
        applyTheme(next);
        const btn = document.getElementById('themeToggle');
        if (btn) btn.textContent = next === 'light' ? '🌙 Dark' : '🌞 Light';
    }

    document.addEventListener('DOMContentLoaded', initTheme);
    window.toggleTheme = toggleTheme; // função global para uso em templates
})();