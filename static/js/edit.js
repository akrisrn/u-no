$(function () {
    editormd({
        id: "editormd",
        path: lib_path,
        height: "700px",
        watch: false
    });

    $("#save").click(() => {
        $.post(document.location.pathname, {data: $("#data").val()}, (result) => {
            if (result) {
                const message = $("#message");
                message.show();
                message.fadeOut(1000);
            }
        })
    });
});