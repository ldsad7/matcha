var orientat = {
    edit: function() {
        this.changeOrientation = document.getElementById("selectOrientation");
        this.span = document.getElementById("orientation-data");
        this.changeOrientation.querySelectorAll("option").forEach(opt => {
            if (opt.value === this.span.innerHTML) {
                opt.setAttribute("selected", "");
            }
        });
        this.span.innerHTML = "";
        this.changeOrientation.style.display = "inline-block";
    },
    submit: function() {
        this.span.innerHTML = this.changeOrientation.value.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        this.changeOrientation.querySelectorAll("option").forEach(opt => {
            opt.removeAttribute("selected");
        });
        this.changeOrientation.style.display = "none";
    }
}
