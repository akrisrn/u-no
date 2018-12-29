$(function () {
    const textarea = $("#article-content")[0];
    textarea.setSelectionRange(0, 0);
    textarea.scrollTop = 0;

    $("#save").click(() => {
        $.post(document.location.pathname, {data: $("#article-content").val()}, (result) => {
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