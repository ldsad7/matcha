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
    newNotif.innerHTML = `<span class='notif_elem'>${text}</span>`
    newNotif.addEventListener("mouseenter", function(e) {_idTimeout = setTimeout(() => this.remove(), 1500)});
    newNotif.addEventListener("mouseleave", function(e) {clearInterval(_idTimeout)});
    document.getElementById("notif_list").appendChild(newNotif);
}

function changeNotifList() {
    SendRequest("get", "/api/v1/notifications", "created=" + (Math.floor(+new Date() / 1000) - 10), function(e) {
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
    }, 10000);
}

getNotifications();
