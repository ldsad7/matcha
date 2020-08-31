var _name = {
    edit: function() {
        this.first_name = document.getElementById("first_name");
        this.last_name = document.getElementById("last_name");
        this.span = document.getElementById("name").querySelector("span");
        this.first_name.style.display = "inline-block";
        this.last_name.style.display = "inline-block";
        this.first_name.value = this.span.innerHTML.split(" ")[0];
        this.last_name.value = this.span.innerHTML.split(" ")[1];

        this.span.innerHTML = "";
    },
    submit: function() {
        this.first_name.style.display = "none";
        this.last_name.style.display = "none";

        this.span.innerHTML = this.first_name.value + " " + this.last_name.value;
    }
}