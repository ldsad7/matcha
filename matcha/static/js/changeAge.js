function get_current_age(date) {
    var d = date.split('-');
    if( typeof d[2] !== "undefined" ) {
        date = d[1]+'.'+d[2]+'.'+d[0];
        return ((new Date().getTime() - new Date(date)) / (24 * 3600 * 365.25 * 1000)) | 0;
    }
    return 0;
}

var ageArea = document.getElementById("age");
var datePicker = document.getElementById("date-picker");
ageArea.querySelector("span").innerHTML = get_current_age(datePicker.value);

var age = {
    edit: function() {
        this.ageArea = document.getElementById("age");
        this.datePicker = document.getElementById("date-picker");
        if (!this.datePicker.value) {
            this.datePicker.setAttribute("value", "2004-12-31");
        }
        this.datePicker.setAttribute("type", "date");
    },
    submit: function() {
        this.datePicker.setAttribute("type", "hidden");
        if (!this.datePicker.value) {
            this.datePicker.setAttribute("value", "2004-12-31");
        } else {
            this.datePicker.setAttribute("value", this.datePicker.value);
        }
        this.ageArea.querySelector("span").innerHTML = get_current_age(this.datePicker.value);
    }
};
