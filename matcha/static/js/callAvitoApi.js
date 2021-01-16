const avitoDatalist = document.getElementById("locat");

function clearDatalist() {
    document.querySelectorAll("#locat option").forEach(el => {
        el.remove();
    });
}

function callAvitoApi(value) {
    SendRequest("get", "/api/v1/location", "&value=" + encodeURI(value), function(e) {
        try {
            const result = JSON.parse(e.response);
            clearDatalist();
            if (result["result"]["locations"]) {
                result["result"]["locations"].forEach(obj => {
                    const name = obj["names"]["1"];
                    const newEl = document.createElement("option");
                    newEl.setAttribute("value", name);
                    avitoDatalist.appendChild(newEl);
                });
            }
        } catch (error) {
            alert("Значение в `location` слишком большое");
        }
    });
}

function changeAvitoDatalist(e) {
    var res = e.value;
    setTimeout((res) => {
        if (e.value === res)
            callAvitoApi(res);
    }, 300, res);
}
