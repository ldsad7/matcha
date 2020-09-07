var image = {
    loadFile: function(event) {
        var output = document.getElementById('output');

        if (document.querySelectorAll(".img-area div div img").length < 4) {
            let tmp = document.createElement("img");
            tmp.setAttribute("id", "output");
            tmp.style.display = "none";
            document.querySelector(".img-area").appendChild(tmp);
        } else {
            document.getElementById("image-input").style.display = "none";
        }
        output.style.display = "inline-block";
        output.src = URL.createObjectURL(event.target.files[0]);
        output.removeAttribute("id");
        avatar.edit();
    },
    edit: function() {
        this.input = document.getElementById("image-input");
        this.input.style.display = "inline-block";
    },
    submit: function() {
        this.input.style.display = "none";
    }
}