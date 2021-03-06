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
        this.history.innerHTML = replaceAllSymbols(this.textArea.value);
        this.textArea.remove();
    }
}

document.getElementById("change-profile-data").addEventListener("click", function(e) {
    if (change_user_data === false) {
        initial_images = [...$('.user-profile img')].filter(el => el.getAttribute('src')).map(el => { return el.getAttribute('src') });
        initial_main_image = [...$('figure img')].filter(el => el.getAttribute('src'));
        new_images = [];
        new_images_srcs = [];
        main_image_src = "";

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
        _email.edit();

        change_user_data = true;
        cancel_btn.style.display = "inline-block";
    } else {
        let main_image = [...$('figure img')].filter(el => el.getAttribute('src'));
        let initial_main_image_src = initial_main_image[0].getAttribute('src');
        let main_image_src = main_image[0].getAttribute('src');
        if (initial_main_image_src !== main_image_src) {
            $.ajax({
                headers: {
                    'Accept' : 'application/json',
                    'Content-Type' : 'application/json',
                    'X-CSRFToken': csrftoken
                },
                url: "/api/v1/user_photos/update_main/",
                type: "PATCH",
                data: JSON.stringify({
                    "image": initial_main_image_src,
                    "main": 0
                }),
                error: function (request, status, error) {
                    alert(request.responseText + ". Запрос не был сохранён.");
                }
            });
            if (!main_image_src.startsWith("blob:")) {
                $.ajax({
                    headers: {
                        'Accept' : 'application/json',
                        'Content-Type' : 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    url: "/api/v1/user_photos/update_main/",
                    type: "PATCH",
                    data: JSON.stringify({
                        "image": main_image_src,
                        "main": 1
                    }),
                    error: function (request, status, error) {
                        alert(request.responseText + ". Запрос не был сохранён.");
                    }
                });
            }
        }
        let images = [...$('.user-profile img')].filter(el => el.getAttribute('src')).map(el => { return el.getAttribute('src') });
        $.ajax({
            headers: {
                'Accept' : 'application/json',
                'Content-Type' : 'application/json',
                'X-CSRFToken': csrftoken
            },
            url: "/api/v1/user_photos/" + user_id + "/update/",
            type: "PATCH",
            data: JSON.stringify({
                "images": images,
                "initial_images": initial_images
            }),
            error: function (request, status, error) {
                alert(request.responseText + ". Запрос не был сохранён.");
            }
        });

        new_images.forEach(function (elem, i) {
            let { file } = elem;

            if (file) {
                let data = new FormData();

                data.append("image", file, "tmp.jpg");
                data.append("user_id", user_id - 0);
                if (new_images_srcs[i] === main_image_src) {
                    data.append("main", "True");
                } else {
                    data.append("main", "False");
                }

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

        const tag_names = [...$(".tag span")].map(el => { return replaceAllSymbols(el.textContent) });

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
                "first_name": replaceAllSymbols($("#first_name").val()),
                "last_name": replaceAllSymbols($("#last_name").val()),
                "date_of_birth": replaceAllSymbols($("#date-picker").val()),
                "gender": replaceAllSymbols($("#selectGender option:checked").val()),
                "orientation": replaceAllSymbols($("#selectOrientation option:checked").val()),
                "location": replaceAllSymbols($("#selectLocation").val()),
                "info": replaceAllSymbols($("#textArea").val()),
                "email": replaceAllSymbols($("#email_input").val()),
                "tags": tag_names
            }),
            error: function (request, status, error) {
                alert(request.responseText + ". Запрос не был сохранён.");
                wasError = true;
            }
        });

        avatar.submit();
        _name.submit();
        hist.submit();
        age.submit();
        tags.submit();
        gender.submit();
        orientat.submit();
        _location.submit();
        image.submit();
        _email.submit();
        this.innerHTML = "&#9998;";
        this.style.padding = "2px 5px";
        change_user_data = false;
        cancel_btn.style.display = "none";
    }
});
cancel_btn.addEventListener("click", function(e) {
    location.reload();
});
