var navbar = document.querySelector(".navbar");
var toggle = document.querySelector(".toggle");
if (navbar) {
    document.addEventListener("click", function(e) {
        if (navbar.classList.contains("navbar-active")) {
            if (e.target !== navbar && !navbar.contains(e.target) && !toggle.contains(e.target) && toggle !== e.target) {
                navbar.classList.remove("navbar-active");
            }
        }
    });
    document.querySelector(".toggle").addEventListener("click", function(e) {
        navbar.classList.toggle("navbar-active");
    });
}