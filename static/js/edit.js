$(function () {
    $("#save").click(() => {
        $.post(document.location.pathname, {data: $("#data").val()}, (result) => {
            if (result) {
                url = result;
                const message = $("#message");
                message.show();
                message.fadeOut(1000);
            }
        })
    });
    $("#view").click(() => {
        open(url)
    });

    $(window).bind("keydown", (event) => {
        if (event.ctrlKey || event.metaKey) {
            if (String.fromCharCode(event.which).toLowerCase() === "s") {
                event.preventDefault();
                $("#save").click()
            }
        }
    });
});