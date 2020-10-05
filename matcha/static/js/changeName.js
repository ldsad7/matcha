var _name = {
    edit: function() {
        this.first_name = document.getElementById("first_name");
        this.last_name = document.getElementById("last_name");
        this.firstname = document.getElementById("firstname");
        this.lastname = document.getElementById("lastname");
        
        this.first_name.style.display = "inline-block";
        this.last_name.style.display = "inline-block";
        this.first_name.value = this.firstname.textContent;
        this.last_name.value = this.lastname.textContent;

        this.firstname.innerHTML = "";
        this.lastname.innerHTML = "";
    },
    submit: function() {
        this.first_name.style.display = "none";
        this.last_name.style.display = "none";

        this.firstname.innerHTML = this.first_name.value + " ";
        this.lastname.innerHTML = this.last_name.value;
    }
}