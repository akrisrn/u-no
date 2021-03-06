$(function () {
    const textarea = $("#article-content")[0];
    textarea.setSelectionRange(0, 0);
    textarea.scrollTop = 0;

    const postData = (func) => {
        $.post(window.location.href, {data: textarea.value}, (result) => {
            if (result) {
                url = result;
                const message = $("#message");
                message.show();
                message.fadeOut(1000);
                if (func) func()
            }
        })
    };

    $("#save").click(() => {
        postData()
    });
    $("#view").click(() => {
        window.open(url)
    });
    $("#saveView").click(() => {
        postData(() => {
            window.location.href = url;
        });
    });

    $(window).bind("keydown", (event) => {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case "s":
                    event.preventDefault();
                    $("#save").click();
                    break;
                case "q":
                    event.preventDefault();
                    $("#view").click();
                    break;
                case "b":
                    event.preventDefault();
                    $("#saveView").click();
                    break;
            }
        }
    });
});