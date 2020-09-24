notif_data = [];

function clearNotifList() {
    document.querySelectorAll("#notif_list a").forEach(el => {
        el.remove();
    });
}

const appendNotif = (text) => {
    const newNotif = document.createElement("a");
    newNotif.setAttribute("href", "#");
    newNotif.innerHTML = `<span class='notif_elem'>${text}</span>`
    newNotif.addEventListener("mouseenter", function(e) {setTimeout(() => this.remove(), 5000)});
    document.getElementById("notif_list").appendChild(newNotif);
}

function changeNotifList() {
    SendRequest("get", "/api/v1/notifications", "created=" + (Math.floor(+new Date() / 1000) - 10), function(e) {
        const result = JSON.parse(e.response);
        result.forEach(el => {
            const { type } = el;
            appendNotif(type);
        });
    });
}

function getNotifications(e) {
    setInterval(() => {
        changeNotifList();
    }, 10000);
}

getNotifications();
