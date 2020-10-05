var navbar = document.querySelector(".nav-bar");
var toggle = document.querySelector(".toggle");
if (toggle) {
    document.addEventListener("click", function(e) {
        if (navbar.classList.contains("nav-bar-active")) {
            if (e.target !== navbar && !navbar.contains(e.target) && !toggle.contains(e.target) && toggle !== e.target) {
                navbar.classList.remove("nav-bar-active");
            }
        }
    });
    document.querySelector(".toggle").addEventListener("click", function(e) {
        navbar.classList.toggle("nav-bar-active");
    });
}