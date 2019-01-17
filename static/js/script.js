$(function () {
    $("a").each((index, element) => {
        if (element.getAttribute("href").startsWith("http")) {
            element.setAttribute("target", "_blank")
        }
    });

    let keyInput = "";
    const inputBind = {
        "tags": () => {
            open(tags_url)
        }
    };
    $(window).bind("keydown", (event) => {
        keyInput += event.key;
        for (let key in inputBind) {
            if (keyInput.endsWith(key)) {
                inputBind[key]();
                break;
            }
        }
    });
});