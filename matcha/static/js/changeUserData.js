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
        initial_images = [...$('.img-area img')].filter(el => el.getAttribute('src'));
        initial_main_image = [...$('figure img')].filter(el => el.getAttribute('src'));
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
        new_images.forEach(elem => {
            let { file } = elem;

            if (file) {
                let data = new FormData();

                data.append("image", file, "tmp.jpg");
                data.append("user_id", user_id - 0);
                data.append("main", "False");

                let settings = {
                    "url": "/api/v1/user_photos/",
                    "method": "POST",
                    "headers": {
                        "X-CSRFToken": getCookie('csrftoken'),
                    },
                    "processData": false,
                    "mimeType": "multipart/form-data",
                    "contentType": false,
                    "data": data
                };
                $.ajax(settings);
            }
        });

        let images = [...$('.img-area img')].filter(el => el.getAttribute('src'));
        console.log("images: " + images.map(el => { return el.getAttribute('src') }));
        console.log("initial_images: " + initial_images.map(el => { return el.getAttribute('src') }));
        let main_image = [...$('figure img')].filter(el => el.getAttribute('src'));

        if (initial_main_image && main_image) {
            initial_main_image[0].getAttribute('src');
        } else {
            //
        }

        console.log("main_image: " + main_image.map(el => { return el.getAttribute('src') }));
        console.log("initial_main_image: " + initial_main_image.map(el => { return el.getAttribute('src') }));

        const tag_names = [...$(".tag span")].map(el => { return el.textContent });

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
                "tags": tag_names
            })
        });

        avatar.submit();
        _name.submit();
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
