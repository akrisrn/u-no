$(function () {
    $("a").each((index, element) => {
        if (element.getAttribute("href").startsWith("http")) {
            element.setAttribute("target", "_blank")
        }
    });
});