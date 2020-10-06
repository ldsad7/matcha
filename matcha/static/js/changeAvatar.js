function createDelBlock() {
    let del_block = document.createElement("div");
    del_block.classList.add("del-img-btn");
    del_block.style =   `padding: 2px 5px;
                        background-color: red;
                        position: absolute;
                        right: 15px;
                        top: 25px;
                        cursor: pointer;
                        text-align: center;
                        align-items: center;`
    del_block.innerHTML = "x";
    del_block.addEventListener("click", function(e) {
        const inp_btn = document.getElementById("image-input");
        avatar.deleted_imgs.push(e.target.parentNode.querySelector("img"));
        e.target.parentNode.remove();
        if (inp_btn.style.display == "none") {
            inp_btn.style.display = "block";
        }
    });
    return del_block;
}

var avatar = {
    deleted_imgs: [],
    edit: function() {
        this.current = document.querySelector("figure img");
        this.del_btn = document.getElementById("del-avatar");
        this.images = document.querySelectorAll(".img-area div img");
        this.clicked = false;
        document.querySelectorAll(".img-area div div").forEach(el => {
            el.appendChild(createDelBlock());
        });
        if (this.images.length > 1) {
            this.images.forEach(img => {
                img.addEventListener("click", function(e) {
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
                                document.querySelector("figure div").appendChild(e.target);
                            }
                        });
                    }
                });
            });
        }
    },
    submit: function() {
        document.querySelectorAll(".img-area div div .del-img-btn").forEach(el => {
            el.remove();
        });
        document.querySelectorAll(".img-area img").forEach(el => {
            el.removeEventListener("click", function(e) {
                document.querySelector(".img-area").appendChild(document.querySelector("figure img"));
                document.querySelector("figure div").appendChild(e.target);
            });
        });
        this.deleted_imgs.forEach(img => {
            csrftoken = getCookie('csrftoken');

            $.ajax({
                "url": "/api/v1/user_photos/" + img.id,
                "headers": {
                    'Accept' : 'application/json',
                    'Content-Type' : 'application/json',
                    "X-CSRFToken": csrftoken,
                },
                type: "DELETE",
            });
        })
    }
}