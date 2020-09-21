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

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById("change-profile-data").addEventListener("click", function(e) {
    if (change_user_data === false) {
        this.innerHTML = "&#10004;";
        this.style.padding = "2px 6px";
        hist.edit();
        tags.edit();
        age.edit();
        gender.edit();
        orientation.edit();
        _name.edit();
        _location.edit();
        avatar.edit();
        image.edit();
        change_user_data = true;
        cancel_btn.style.display = "inline-block";
    } else {
        const id = parseInt($("#id").text());
        const tag_names = [...$(".tag span")].map(el => { return el.textContent });

        const images_src = [...$(".for-push")];

        const csrftoken = getCookie('csrftoken');
        $.ajax({
            headers: {
                'Accept' : 'application/json',
                'Content-Type' : 'application/json',
                'X-CSRFToken': csrftoken
            },
            url: "/api/v1/users/" + id + "/",
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

        let data = new FormData();
        console.log($('#imageInput')[0].files.length);
        images_src.forEach(elem => {
            let imageInput = $('#imageInput').length ? $('#imageInput')[0].files[0] : null;
            if (imageInput) {
                data.append("image", imageInput, "tmp.jpg");
            }
        });
        data.append("user_id", id.toString());
        let settings = {
            "url": "/api/v1/user_photos/",
            "method": "POST",
            "timeout": 0,
            "headers": {
                // "Content-Type" : 'multipart/form-data',
                "X-CSRFToken": csrftoken,
            },
            "processData": false,
            "mimeType": "multipart/form-data",
            "contentType": false,
            "data": data
        };
        $.ajax(settings);

        hist.submit();
        tags.submit();
        age.submit();
        gender.submit();
        orientation.submit();
        _name.submit();
        _location.submit();
        avatar.submit();
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
