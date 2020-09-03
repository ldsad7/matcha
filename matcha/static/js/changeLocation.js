var _location = {
    edit: function() {
        this.changeLocation = document.getElementById("selectLocation");
        this.span = document.getElementById("location-data");

        this.changeLocation.style.display = "inline-block";
        this.changeLocation.value = this.span.innerHTML;

        this.span.innerHTML = "";
    },
    submit: function() {
        this.changeLocation.style.display = "none";

        this.span.innerHTML = this.changeLocation.value;
    }
}
