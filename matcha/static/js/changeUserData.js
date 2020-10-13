var change_user_data = false;
var cancel_btn = document.getElementById("change-profile-data-cancel");

var hist = {
    edit: function() {
        this.textArea = document.createElement("textarea"),
        this.history = document.getElementById("history"),
        this.textArea.setAttribute("id", "textArea");
        this.textArea.innerHTML = this.history.innerHTML;
        this.history.innerHTML = "";
        this.history.appendChild(this.textArea);
        autosize(this.textArea);
    },
    submit: function() {
        this.history.innerHTML = this.textArea.value;
        this.textArea.remove();
    }
}

document.getElementById("change-profile-data").addEventListener("click", function(e) {
    if (change_user_data === false) {
        new_images = [];

        this.innerHTML = "&#10004;";
        this.style.padding = "2px 6px";

        hist.edit();
        tags.edit();
        age.edit();
        gender.edit();
        orientat.edit();
        _name.edit();
        _location.edit();
        avatar.edit();
        image.edit();

        change_user_data = true;
        cancel_btn.style.display = "inline-block";
    } else {
        const tag_names = [...$(".tag span")].map(el => { return el.textContent });

        const images_src = [...$(".for-push")];

        csrftoken = getCookie('csrftoken');
        $.ajax({
            headers: {
                'Accept' : 'application/json',
                'Content-Type' : 'application/json',
                'X-CSRFToken': csrftoken
            },
            url: "/api/v1/users/" + user_id + "/",
            type: "PATCH",
            data: JSON.stringify({
                "first_name": $("#first_name").val(),
                "last_name": $("#last_name").val(),
                "date_of_birth": $("#date-picker").val(),
                "gender": $("#selectGender option:checked").val(),
                "orientation": $("#selectOrientation option:checked").val(),
                "location": $("#selectLocation").val(),
                "info": $("#textArea").val(),
                "tags": tag_names,
            })
        })

        avatar.submit();

        _name.submit();

        new_images.forEach(elem => {
        // images_src.forEach(elem => {
            let { file } = elem;
            // let { src } = elem;
            // let file = src;

            if (file) {
                // var FR = new FileReader();
                // var data = {};
                var data = new FormData();
                // var image = null;

                // console.log(new_images);

                // const imageToData = (e) => {
                    // data.image = e.target.result.split(',')[1];
                    // data.append("image", e.target.result.toString(), "tmp.jpg");
                // }
                // FR.addEventListener("load", imageToData);
                // FR.readAsDataURL( file );

                
                // data.user_id = user_id;
                data.append("image", file, "tmp.jpg");
                data.append("user_id", user_id - 0);
                data.append("main", false);

                let settings = {
                    "url": "/api/v1/user_photos/",
                    "method": "POST",
                    // "timeout": 0,
                    "headers": {
                        "Content-Type" : 'multipart/form-data',
                        "X-CSRFToken": getCookie('csrftoken'),
                    },
                    "processData": false,
                    "mimeType": "multipart/form-data",
                    "contentType": false,
                    "data": data
                };
                console.log(settings);
                $.ajax(settings);
            }
        });
        hist.submit();
        tags.submit();
        age.submit();
        gender.submit();
        orientat.submit();
        _location.submit();
        image.submit();
        this.innerHTML = "&#9998;";
        this.style.padding = "2px 5px";
        change_user_data = false;
        cancel_btn.style.display = "none";
    }
});
cancel_btn.addEventListener("click", function(e) {
    location.reload();
});
