$(function () {
    $("a").each((index, element) => {
        if (element.getAttribute("href").startsWith("http")) {
            element.setAttribute("target", "_blank")
        }
    });

    let keyInput = "";
    $(window).bind("keydown", (event) => {
        keyInput += event.key;
        for (let key in inputBind["common"]) {
            if (keyInput.endsWith(key)) {
                inputBind["common"][key]();
                break;
            }
        }
    });
});