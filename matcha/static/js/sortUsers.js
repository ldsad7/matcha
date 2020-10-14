const sort_by_param = (param, flag) => {
    return (a, b) => {
        if (flag)
            return a.querySelector(`.${param}`) > b.querySelector(`.${param}`);
        else
            return b.querySelector(`.${param}`) > a.querySelector(`.${param}`);
    }
}
/*
**
** @param param: "rating, age"
**
*/

function sortUsers(param, flag) {
    let list = [...document.querySelectorAll(".user-profile")];
    let sort_func = sort_by_param(param, flag);

    list.sort(sort_func);

    for (let i = 0, len = list.length; i < len; i++) {
        list[i].parentNode.appendChild(list[i]);
    }
}
