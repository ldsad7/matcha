notif_data = [];

function clearNotifList() {
    document.querySelectorAll("#notif_list a").forEach(el => {
        el.remove();
    });
}

function changeNotifList() {
    SendRequest("get", "/api/v1/notifications", "&created=" + (Math.floor(+new Date() / 1000) - 10), function(e) {
        const result = JSON.parse(e.response);
        console.log(result);
        // if (result != notif_data)
        // {
        //     clearNotifList();
        //     if (result["result"]["locations"]) {
        //         result["result"]["locations"].forEach(obj => {
        //             const name = obj["names"]["1"];
        //             const newEl = document.createElement("option");
        //             newEl.setAttribute("value", name);
        //             datalist.appendChild(newEl);
        //         });
        //     }
        // }
    });
}

function getNotifications(e) {
    setInterval(() => {
        changeNotifList();
    }, 10000);
}

getNotifications();
