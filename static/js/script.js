let keyInput = "";
const bindInput = (binds) => {
    $(window).bind("keydown", (event) => {
        keyInput += event.key;
        for (let key in binds) {
            if (keyInput.endsWith(key)) {
                binds[key]();
                break;
            }
        }
    });
};

$(function () {
    $("a").each((index, element) => {
        if (element.getAttribute("href").startsWith("http")) {
            element.setAttribute("target", "_blank")
        }
    });
    bindInput(inputBinds["common"])
});