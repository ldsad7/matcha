var _name = {
    edit: function() {
        this.firstname = document.getElementById("firstname");
        this.lastname = document.getElementById("lastname");
        this.span = document.getElementById("name").querySelector("span");
        this.firstname.style.display = "inline-block";
        this.lastname.style.display = "inline-block";
        this.firstname.value = this.span.innerHTML.split(" ")[0];
        this.lastname.value = this.span.innerHTML.split(" ")[1];
        this.span.innerHTML = "";
    },
    submit: function() {
        this.firstname.style.display = "none";
        this.lastname.style.display = "none";
        this.span.innerHTML = this.firstname.value + " " + this.lastname.value;
    }
}