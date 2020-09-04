var avatar = {
    edit: function() {
        this.current = document.querySelector("figure img");
        this.del_btn = document.getElementById("del-avatar");
        this.images = document.querySelectorAll(".img-area div img");
        this.clicked = false;
        if (this.images.length > 1) {
            // this.del_btn.style.display = "inline-block";
            // this.del_btn.addEventListener("click", function(e) {
            //     this.style.display = "none";
            // });
            this.images.forEach(img => {
                // img.style.border = "2px solid green";
                img.addEventListener("click", function(e) {
                    // document.querySelectorAll(".img-area img").forEach(img => {
                    //     img.style.border = "none";
                    // });
                    let el = document.querySelector("figure img");
                    if (document.querySelector("#change-profile-data-cancel").style.display !== "none") {
                        let div = document.createElement("div");
                        // let hover = document.createElement("div");
                        // hover.classList.add("hover-info");
                        // div.appendChild(hover);
                        
                        div.appendChild(el);
                        document.querySelector(".img-area").appendChild(div);
                        document.querySelector("figure div").appendChild(e.target);
                        el.addEventListener("click", function(e) {
                            if (document.querySelector("#change-profile-data-cancel").style.display !== "none") {
                                let div = document.createElement("div");
                                
                                div.appendChild(document.querySelector("figure img"));
                                document.querySelector(".img-area").appendChild(div);
                                document.querySelector("figure div").appendChild(e.target);
                            }
                        });
                    }
                });
            });
        }
    },
    submit: function() {
        document.querySelectorAll(".img-area img").forEach(el => {
            el.removeEventListener("click", function(e) {
                document.querySelector(".img-area").appendChild(document.querySelector("figure img"));
                document.querySelector("figure div").appendChild(e.target);
            });
            // el.addEventListener("click", function(e) {});
        });
        // this.del_btn.style.display = "none";
        // this.images.forEach(img => {
        //     img.style.border = "none";
        // });
    }
}