
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
        this.innerHTML = "&#10004;";
        this.style.padding = "2px 6px";
        change_user_data = true;
        cancel_btn.style.display = "inline-block";
        hist.edit();
        tags.edit();
        age.edit();
        gender.edit();
        _name.edit();
        avatar.edit();
        image.edit();
    } else {
        hist.submit();
        tags.submit();
        age.submit();
        gender.submit();
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
