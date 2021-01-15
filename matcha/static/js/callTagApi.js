const tagDatalist = document.getElementById("tag");

function clearDatalist() {
    document.querySelectorAll("#tag option").forEach(el => {
        el.remove();
    });
}

function callTagApi(value) {
    SendRequest("get", "/api/v1/tag/", "&value=" + encodeURI(value), function(e) {
        const result = JSON.parse(e.response);
        clearDatalist();
        if (result["tags"]) {
            result["tags"].forEach(tag_name => {
                const newEl = document.createElement("option");
                newEl.setAttribute("value", tag_name);
                tagDatalist.appendChild(newEl);
            });
        }
    });
}

function changeTagDatalist(e) {
    var res = e.value;
    setTimeout((res) => {
        if (e.value === res)
            callTagApi(res);
    }, 300, res);
}
