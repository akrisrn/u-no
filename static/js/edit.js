$(function () {
    const editor = editormd({
        id: "editormd",
        path: lib_path,
        height: "700px",
        watch: false
    });
    const fullscreen = editor.fullscreen;
    const fullscreenExit = editor.fullscreenExit;
    editor.fullscreen = function () {
        fullscreen.apply(editor);
        if (editor.state.fullscreen) {
            $(".button-group").hide();
        }
    };
    editor.fullscreenExit = function () {
        fullscreenExit.apply(editor);
        if (!editor.state.fullscreen) {
            $(".button-group").show();
        }
    };

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
    })
});