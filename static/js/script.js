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