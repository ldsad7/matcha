_intervalNotification = 5; // seconds

_idsNotifs = [];

csrftoken = getCookie('csrftoken');

if (document.getElementById("read-all")) {
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
        newNotif.innerHTML = `<span class='notif_elem'>${text.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</span>`;
        newNotif.addEventListener("click", function(e) {
            setTimeout(() => {
                _idTimeout = setTimeout(
                    () => {
                        let index = _idsNotifs.indexOf(+this.id);
                        if (index > -1) {
                            _idsNotifs.splice(index, 1);
                            if (_idsNotifs.length < 1) {
                                document.querySelector("span.circle").style.display = "none";
                                // }
                                // if (_idsNotifs.length < 2) {
                                document.getElementById("read-all").style.display = "none";
                            }
                            this.classList.add("animate__fadeOutTopRight");
                            $.ajax({
                                headers: {
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrftoken
                                },
                                url: "/api/v1/notifications/read/",
                                type: "PATCH",
                                data: JSON.stringify({
                                    "ids": this.id
                                })
                            });
                            setTimeout(() => {this.remove()}, 250)
                        }
                    })})
        });
        /*newNotif.addEventListener("mouseenter", function(e) {
            setTimeout(() => {
                _idTimeout = setTimeout(
                    () => {
                        const index = _idsNotifs.indexOf(+this.id);
                        if (index > -1) {
                            _idsNotifs.splice(index, 1);
                            console.log("_idsNotifs.length: " + _idsNotifs.length);
                            if (_idsNotifs.length < 1) {
                                document.querySelector("span.circle").style.display = "none";
                            // }
                            // if (_idsNotifs.length < 2) {
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
                            });
                            setTimeout(() => {this.remove()}, 500)
                        }
                    }, 1500)
            }, 0);
        });*/
        // newNotif.addEventListener("mouseleave", function(e) {clearInterval(_idTimeout)});
        let notif_list = document.getElementById("notif_list");
        notif_list.insertBefore(newNotif, notif_list.children[1]);
    };

    function changeNotifList() {
        SendRequest("get", "/api/v1/notifications", "", function(e) {
            const result = JSON.parse(e.response);
            result.forEach(el => {
                const { type, id } = el;
                if (_idsNotifs.indexOf(id) === -1) {
                    _idsNotifs.push(id);
                    if (el.user_1 && type === 'сообщение') {
                        appendNotif(type, id, "/chat/" + [user_id, el.user_1].sort().join('_'));
                    } else if (el.user_1) {
                        appendNotif(type, id, "/profiles/" + el.user_1);
                    } else {
                        appendNotif(type, id);
                    }
                }
            });
            if (_idsNotifs.length) {
                document.querySelector("span.circle").style.display = "block";
            // }
            // if (_idsNotifs.length > 1) {
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

    function deleteNotification(id_notif) {
        const index = _idsNotifs.indexOf(+id_notif);
        if (index > -1) {
            _idsNotifs.splice(index, 1);
            if (_idsNotifs.length < 1) {
                document.querySelector("span.circle").style.display = "none";
            // }
            // if (_idsNotifs.length < 2) {
                document.getElementById("read-all").style.display = "none";
            }
            document.getElementById(id_notif).remove();
            $.ajax({
                headers: {
                    'Accept' : 'application/json',
                    'Content-Type' : 'application/json',
                    'X-CSRFToken': csrftoken
                },
                url: "/api/v1/notifications/read/",
                type: "PATCH",
                data: JSON.stringify({
                    "ids": id_notif
                })
            })
        }
    }

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
            });
            this.style.display = "none";
            _idsNotifs = [];
            document.querySelector("span.circle").style.display = "none";
        });
}
