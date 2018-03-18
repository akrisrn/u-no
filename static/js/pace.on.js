Pace.on("done", function () {
    document.getElementById("content").style.opacity = "1";
    document.getElementById("content").style.top = "0";
});

window.onbeforeunload = function () {
    document.getElementById("content").style.opacity = "0";
    document.getElementById("content").style.top = "30px";
};