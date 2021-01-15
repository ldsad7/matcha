var gender = {
    edit: function() {
        this.changeGender = document.getElementById("selectGender");
        this.span = document.getElementById("gender").querySelector("span");
        this.changeGender.querySelectorAll("option").forEach(opt => {
            if (opt.value === this.span.innerHTML) {
                opt.setAttribute("selected", "");
            }
        });
        this.span.innerHTML = "";
        this.changeGender.style.display = "inline-block";
    },
    submit: function() {
        this.span.innerHTML = this.changeGender.value.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        this.changeGender.querySelectorAll("option").forEach(opt => {
            opt.removeAttribute("selected");
        });
        this.changeGender.style.display = "none";
    }
}
