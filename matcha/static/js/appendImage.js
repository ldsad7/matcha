var image = {
    loadFile: function(event) {
<<<<<<< HEAD
        // var output = document.getElementById('output');

        // if (document.querySelectorAll(".img-area img").length < 4) {
        //     let tmp = document.createElement("img");
        //     tmp.setAttribute("id", "output");
        //     tmp.style.display = "none";
        //     document.querySelector(".img-area").appendChild(tmp);
        // } else {
        //     document.getElementById("image-input").style.display = "none";
        // }
        // output.style.display = "inline-block";
        // output.src = URL.createObjectURL(event.target.files[0]);
        // output.removeAttribute("id");
        // avatar.edit();
        output.onload = function() {
            const csrftoken = getCookie('csrftoken');

            URL.revokeObjectURL(output.src) // free memory
            avatar.edit();
            $.ajax({
                // headers: {
                //     'Accept' : 'application/json',
                //     'Content-Type' : 'application/json',
                //     'X-CSRFToken': csrftoken
                // },
                url: '/api/v1/test_upload', // url where to submit the request
                type : "POST", // type of action POST || GET
                dataType : 'json', // data type
                data : this.files[0], // post data || get data
                success : function(result) {
                    // you can see the result from the console
                    // tab of the developer tools
                    console.log(result);
                },
                error: function(xhr, resp, text) {
                    console.log(xhr, resp, text);
                }
            })
        }
=======
        var output = document.getElementById('output');
        const div = document.createElement("div");

        if (document.querySelectorAll(".img-area div div img").length < 3) {
            let tmp = document.createElement("img");
            tmp.setAttribute("id", "output");
            tmp.style.display = "none";
            div.appendChild(tmp);
            document.querySelector(".img-area").appendChild(tmp);
        } else {
            document.getElementById("image-input").style.display = "none";
        }
        output.style.display = "inline-block";
        output.src = URL.createObjectURL(event.target.files[0]);
        output.removeAttribute("id");
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
                        document.querySelector("figure div").appendChild(e.target);
                    }
                });
            }
        });
        // avatar.edit();
>>>>>>> 8efc225a6b6dcbc20cc0782eb59cbde0e3c8bf46
    },
    edit: function() {
        this.input = document.getElementById("image-input");
        if (document.querySelectorAll(".img-area div div img").length < 4)
            this.input.style.display = "inline-block";
    },
    submit: function() {
        this.input.style.display = "none";
    }
}
