$(document).ready(function () {
    $("input[type=password]").keydown(function (e) {
        if (e.which === 13) {
            $("button[type=submit]").click();
            return false;
        }
    });
});