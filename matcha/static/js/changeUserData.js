
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
        avatar.edit();
        image.edit();
        change_user_data = true;
        cancel_btn.style.display = "inline-block";
    } else {
        var id = parseInt(jQuery("#id").text());
        var tag_names = [];
        var imgs = [];
        var tag_tags = jQuery(".tag span");
        for (var i = 0; i < tag_tags.length; i++)
            tag_names.push(tag_tags[i].textContent);
        document.querySelectorAll(".img-area div img").forEach(el => {
            const str = el.getAttribute("src").split("/");
            imgs.push(str[str.length - 1]);
        });
        console.log(imgs);
        const csrftoken = getCookie('csrftoken');
        jQuery.ajax({
            headers: {
                'Accept' : 'application/json',
                'Content-Type' : 'application/json',
                'X-CSRFToken': csrftoken
            },
            url: "/api/v1/users/" + id + "/",
            type: "PATCH",
            data: JSON.stringify({
                "first_name": jQuery("#first_name").val(),
                "last_name": jQuery("#last_name").val(),
                "date_of_birth": jQuery("#date-picker").val(),
                "gender": jQuery("#selectGender option:checked").val(),
                "orientation": jQuery("#selectOrientation option:checked").val(),
                "location": jQuery("#location").val(),
                "info": jQuery("#textArea").val(),
                "tags": tag_names,
                "photos": imgs
            })
        })

        hist.submit();
        tags.submit();
        age.submit();
        gender.submit();
        orientation.submit();
        _name.submit();
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
