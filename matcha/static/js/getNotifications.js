_intervalNotification = 5; // seconds

function getLocalNotifs() {
    window.localStorage.getItem("notif")
}

function clearNotifList() {
    document.querySelectorAll("#notif_list a").forEach(el => {
        el.remove();
    });
}

const appendNotif = (text, href) => {
    const newNotif = document.createElement("a");
    newNotif.setAttribute("href", href || "#");
    newNotif.classList.add("animate__animated");
    newNotif.innerHTML = `<span class='notif_elem'>${text}</span>`
    newNotif.addEventListener("mouseenter", function(e) {
        setTimeout(() => {
            _idTimeout = setTimeout(
                () => {
                    this.classList.add("animate__fadeOutTopRight");
                    setTimeout(() => {this.remove()}, 700)
                }, 1500)
        }, 0);
    });
    newNotif.addEventListener("mouseleave", function(e) {clearInterval(_idTimeout)});
    document.getElementById("notif_list").appendChild(newNotif);
}

function changeNotifList() {
    SendRequest("get", "/api/v1/notifications", "created=" + (Math.floor(+new Date() / 1000) - _intervalNotification), function(e) {
        const result = JSON.parse(e.response);
        console.log(result);
        result.forEach(el => {
            const { type } = el;
            if (el.user_1) {
                appendNotif(type, "/profiles/" + el.user_1.id);
            } else {
                appendNotif(type);
            }
        });
    });
}

function getNotifications(e) {
    setInterval(() => {
        changeNotifList();
    }, _intervalNotification * 1000);
}

getNotifications();
