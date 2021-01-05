var image = {
    swapImages: function(el) {
        if (document.querySelector("#change-profile-data-cancel").style.display !== "none") {
            let div = document.createElement("div");
            div.appendChild(document.querySelector("figure img"));
            div.appendChild(createDelBlock());
            document.querySelector(".img-area div").appendChild(div);
            el.parentNode.remove();
            el.classList.add("main");
            main_image_src = el.getAttribute("src");
            document.querySelector("figure div").appendChild(el);
        }
    },
    func: function(img, del=false) {
        let el = document.querySelector("figure img");
        if (document.querySelector("#change-profile-data-cancel").style.display !== "none") {
            let div = document.createElement("div");
            div.appendChild(el);
            if (!del) {
                el.classList.remove("main");
                div.appendChild(createDelBlock());
                document.querySelector(".img-area div").appendChild(div);
            }
            img.parentNode.remove();
            img.classList.add("main");
            main_image_src = img.getAttribute("src");
            document.querySelector("figure div").appendChild(img);
            if (!del)
                el.addEventListener("click", (e) => swapImages(img));
            else {
                el.remove();
            }
        }
    },
    loadFile: function(event) {
        var output = document.getElementById('output');
        const div = document.createElement("div");

        if (document.querySelectorAll(".img-area div div img").length < 4) {
            let tmp = document.createElement("img");
            tmp.setAttribute("id", "output");
            tmp.style.display = "none";
            div.appendChild(tmp);
            document.querySelector(".img-area").appendChild(tmp);
        }
        if (document.querySelectorAll(".img-area div div img").length > 3) {
            document.getElementById("image-input").style.display = "none";
        }
        output.style.display = "inline-block";

        _image = {};
        _image.file = event.target.files[0];
        new_images.push(_image);
           
        output.src = URL.createObjectURL(event.target.files[0]);
        new_images_srcs.push(output.src);

        output.removeAttribute("id");
        output.classList.add("for-push");
        avatar.edit();

        document.querySelector(".img-area div").appendChild(div);
        div.appendChild(output);
        div.appendChild(createDelBlock());

        if (!document.querySelector(".main")) {
            this.func(output, true);
        } else {
            output.addEventListener("click", (e) => this.func(e.target));
        }
    },
    edit: function() {
        this.input = document.getElementById("image-input");
        if (document.querySelectorAll(".img-area div div img").length < 4)
            this.input.style.display = "inline-block";
        document.querySelectorAll(".img-area div div").forEach(el => {
            el.appendChild(createDelBlock());
        });
    },
    submit: function() {
        this.input.style.display = "none";
    }
}
