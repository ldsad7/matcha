_intervalNotification = 5; // seconds

_idsNotifs = []

csrftoken = getCookie('csrftoken');

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
                    console.log(this.id);
                    console.log(_idsNotifs);
                    const index = _idsNotifs.indexOf(+this.id);
                    console.log(index);
                    if (index > -1) {
                        _idsNotifs.splice(index, 1);
                        if (_idsNotifs.length < 1) {
                            document.querySelector("span.circle").style.display = "none";
                        }
                        if (_idsNotifs.length < 2) {
                            document.getElementById("read-all").style.display = "none";
                        }
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
    SendRequest("get", "/api/v1/notifications", "", function(e) {
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
        if (_idsNotifs.length) {
            document.querySelector("span.circle").style.display = "block";
        }
        if (_idsNotifs.length > 1) {
            document.getElementById("read-all").style.display = "block";
        }
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
    this.style.display = "none";
    _idsNotifs = [];
    document.querySelector("span.circle").style.display = "none";
});
