var new_tag_edited = false;
var change_tag_btn = document.getElementById("change-tag");
var change_tag = false; 

function submitTag(el) {
    let input = el.querySelector("input");
    try {
        var data = input.value.trim();
    } catch (error) {
        return;
    }
    if (!data) {
        el.remove();
    }
    input.remove();
    el.classList.remove("active-tag");
    el.classList.remove("new-tag");
    if (new_tag_edited) {
        let del_btn = document.createElement("div");
        del_btn.classList.add("del_btn");
        el.appendChild(del_btn);
        tagListener(el);
        createNewTag();
        new_tag_edited = false;
    }
    el.querySelector("span").innerHTML = "#" + data;
    // ЗДЕСЬ НАДО ОТПРАВЛЯТЬ ЗАПРОС О СОЗДАНИИ/ИЗМЕНЕНИИ ТЕГА
}

function createNewTag() {
    let new_tag = document.createElement("div");
    let span = document.createElement("span");
    let tags_area = document.getElementById("tags");

    span.innerHTML = "# ";
    new_tag.classList.add("tag");
    new_tag.classList.add("new-tag");
    new_tag.appendChild(span);
    new_tag.appendChild(document.createElement("input"));
    tags_area.appendChild(new_tag);
    tagListener(new_tag);
}

function tagListener(el) {
    el.addEventListener("click", function(e) {
        if (!el.classList.contains("active-tag") && !el.classList.contains("new-tag")) {
            let active = document.querySelector(".active-tag");
            if (active) {
                submitTag(active);
            }
            el.classList.add("active-tag");
            let span = el.querySelector("span");
            let data = span.innerHTML.split("#")[1];
            span.innerHTML = "# ";
            let input = document.createElement("input");
            input.setAttribute("value", data);
            el.appendChild(input);
        }
    });
    el.addEventListener("input", function(e) {
        if (el.classList.contains("new-tag")) {
            new_tag_edited = true;
        }
        if (el.classList.contains("new-tag") && el.querySelector("input").value == "") {
            new_tag_edited = false;
        }
        if (e.data === " ") {
            submitTag(el);
        }
    });
    el.addEventListener("keypress", function(e) {
        let code = e.keyCode || e.which;
        if (code === 13) {
            if ((document.querySelector(".new-tag") && document.querySelector(".new-tag input").value) || el.classList.contains("active-tag"))
                submitTag(el);
        }
    });
    try {
        el.querySelector(".del_btn").addEventListener("click", function(e) {
            el.remove();
        });
    } catch {
        console.log("error here");
    }
}

function editTag() {
    document.addEventListener("click", function(e) {
        let active_tag = document.querySelector(".active-tag");
        if (active_tag) {
            if (!(e.target == active_tag || active_tag.contains(e.target))) {
                submitTag(active_tag);
            }
        }
    });
    document.querySelectorAll(".interests .tag").forEach(el => {
        tagListener(el);
    });
}

change_tag_btn.addEventListener("click", function(e) {
    if (change_tag === false) {
        document.querySelectorAll(".tag").forEach(el => {
            let del_btn = document.createElement("div");
            del_btn.classList.add("del_btn");
            el.appendChild(del_btn);
        });
        change_tag_btn.innerHTML = "&#10004;";
        createNewTag();
        editTag();
        change_tag = true;
    } else {
        document.querySelectorAll(".tag").forEach(el => {
            try {
                el.querySelector(".del_btn").remove();
            } catch (error) {
            }
        });
        document.querySelector(".new-tag").remove();
        change_tag = false;
        change_tag_btn.innerHTML = "&#9998;";
    }
});
