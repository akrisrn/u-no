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
    $("a").each(function () {
        const href = this.getAttribute("href");
        if (href && href.startsWith("http")) {
            this.setAttribute("target", "_blank")
        }
    });
    bindInput(inputBinds)
});