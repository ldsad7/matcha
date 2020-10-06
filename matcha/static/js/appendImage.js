var image = {
    loadFile: function(event) {
        var output = document.getElementById('output');
        const div = document.createElement("div");

        if (document.querySelectorAll(".img-area div div img").length < 4) {
            let tmp = document.createElement("img");
            tmp.setAttribute("id", "output");
            tmp.style.display = "none";
            div.appendChild(tmp);
            document.querySelector(".img-area").appendChild(tmp);
        } else {
            document.getElementById("image-input").style.display = "none";
        }
        output.style.display = "inline-block";

        _image = {}
        _image.file = event.target.files[0];
        new_images.push(_image);
        
        output.src = URL.createObjectURL(event.target.files[0]);
        output.removeAttribute("id");
        output.classList.add("for-push");
        avatar.edit();

        document.querySelector(".img-area div").appendChild(div);
        div.appendChild(output);
        div.appendChild(createDelBlock());

        output.addEventListener("click", function(e) {
            let el = document.querySelector("figure img");
            if (document.querySelector("#change-profile-data-cancel").style.display !== "none") {
                let div = document.createElement("div");
                div.appendChild(el);
                div.appendChild(createDelBlock());
                document.querySelector(".img-area div").appendChild(div);
                e.target.parentNode.remove();
                document.querySelector("figure div").appendChild(e.target);
                el.addEventListener("click", function(e) {
                    if (document.querySelector("#change-profile-data-cancel").style.display !== "none") {
                        let div = document.createElement("div");
                        div.appendChild(document.querySelector("figure img"));
                        div.appendChild(createDelBlock());
                        document.querySelector(".img-area div").appendChild(div);
                        e.target.parentNode.remove();
                        e.target.classList.add("for-push");
                        document.querySelector("figure div").appendChild(e.target);
                    }
                });
            }
        });
    },
    edit: function() {
        this.input = document.getElementById("image-input");
        if (document.querySelectorAll(".img-area div div img").length < 4)
            this.input.style.display = "inline-block";
    },
    submit: function() {
        this.input.style.display = "none";
        // var form = new FormData();
        // form.append("image", );
        // form.append("user", user_id);

        // $.ajax({
        //     "url": "http://127.0.0.1:8000/api/v1/user_photos/",
        //     "method": "POST",
        //     "timeout": 0,
        //     "headers": {
        //         "Content-Type": "multipart/form-data",
        //         "sessionid": "e04s9c436u9xdnpjm84vruyj1g7ukkfa"
        //     },
        //     "processData": false,
        //     "mimeType": "multipart/form-data",
        //     "contentType": false,
        //     "data": form
        // });
    }
}
