var image = {
    loadFile: function(event) {
        var output = document.getElementById('output');

        if (document.querySelectorAll(".img-area img").length < 4) {
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
        output.onload = function() {
            URL.revokeObjectURL(output.src) // free memory
            avatar.edit();
            // var ajax = new XMLHttpRequest();
            $.ajax({
                url: '/api/v1/user_photos', // url where to submit the request
                type : "POST", // type of action POST || GET
                dataType : 'json', // data type
                data : $("#form").serialize(), // post data || get data
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
    },
    edit: function() {
        this.input = document.getElementById("image-input");
        this.input.style.display = "inline-block"; 
    },
    submit: function() {
        this.input.style.display = "none";
    }
}