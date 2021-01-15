var _email = {
    edit: function() {
        this.email_value = document.getElementById("email_value");
        this.email_input = document.getElementById("email_input");

        this.email_input.style.display = "inline-block";
        this.email_input.value = this.email_value.textContent.trim();

        this.email_value.innerHTML = "";
    },
    submit: function() {
        this.email_input.style.display = "none";
        this.email_value.innerHTML = replaceAllSymbols(this.email_input.value.trim());
    }
}
