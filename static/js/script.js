document.addEventListener("DOMContentLoaded", function(){
    document.querySelectorAll(".barra-energia").forEach(function(barra){
        barra.style.width = barra.getAttribute("data-energia") + "%";
    });
});