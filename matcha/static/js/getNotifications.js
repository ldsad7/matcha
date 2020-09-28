_intervalNotification = 5; // seconds

_idsNotifs = []

function clearNotifList() {
    document.querySelectorAll("#notif_list a").forEach(el => {
        el.remove();
    });
}

const appendNotif = (text, id, href) => {
    const newNotif = document.createElement("a");
    newNotif.setAttribute("href", href || "#");
    newNotif.id = id;
    newNotif.classList.add("animate__animated");
    newNotif.innerHTML = `<span class='notif_elem'>${text}</span>`
    newNotif.addEventListener("mouseenter", function(e) {
        setTimeout(() => {
            _idTimeout = setTimeout(
                () => {
                    const index = _idsNotifs.indexOf(this.id);
                    if (index > -1) {
                        _idsNotifs.splice(index, 1);
                        this.classList.add("animate__fadeOutTopRight");
                        $.ajax({
                            headers: {
                                'Accept' : 'application/json',
                                'Content-Type' : 'application/json',
                                'X-CSRFToken': csrftoken
                            },
                            url: "/api/v1/notifications/read/",
                            type: "PATCH",
                            data: JSON.stringify({
                                "ids": this.id
                            })
                        })
                        setTimeout(() => {this.remove()}, 500)
                    }
                }, 1500)
        }, 0);
    });
    newNotif.addEventListener("mouseleave", function(e) {clearInterval(_idTimeout)});
    document.getElementById("notif_list").appendChild(newNotif);
}

function changeNotifList() {
    SendRequest("get", "/api/v1/notifications", "created=0", function(e) {
        const result = JSON.parse(e.response);
        console.log(result);
        result.forEach(el => {
            const { type, id } = el;
            if (_idsNotifs.indexOf(id) === -1) {
                _idsNotifs.push(id);
                if (el.user_1) {
                    appendNotif(type, id, "/profiles/" + el.user_1);
                } else {
                    appendNotif(type, id);
                }
            }
        });
    });
}

function getNotifications(e) {
    setInterval(() => {
        changeNotifList();
    }, _intervalNotification * 1000);
}

changeNotifList();
getNotifications();

document.getElementById("read-all").addEventListener("click", function(e) {
    _idsNotifs.forEach(ind => {
        document.getElementById(ind).remove();
    });
    $.ajax({
        headers: {
            'Accept' : 'application/json',
            'Content-Type' : 'application/json',
            'X-CSRFToken': csrftoken
        },
        url: "/api/v1/notifications/read/",
        type: "PATCH",
        data: JSON.stringify({
            "ids": _idsNotifs.join(",")
        })
    })
    this.remove();
});
