$(function () {
    const textarea = $("#article-content")[0];
    textarea.setSelectionRange(0, 0);
    textarea.scrollTop = 0;

    $("#save").click(() => {
        $.post(document.location.pathname, {data: textarea.value}, (result) => {
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
    $("#clean").click(() => {
        textarea.value = ""
    });
    $("#select").click(() => {
        textarea.select()
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