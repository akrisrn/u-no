$(function () {
    $($('details').get().reverse()).each(function () {
        const parentText = $(this).parent().find(">summary>.tag>a").text();
        $(this).find(">summary").each(function () {
            const aTag = $(this).find(">.tag>a");
            if (parentText !== "") {
                aTag.html(aTag.html().replace(new RegExp(`</i>${parentText}/`), "</i>"))
            }
        });
        const summary = this.children[0];
        summary.style.paddingBottom = "6px";
        if (this.childElementCount === 1) {
            this.classList.add("readonly");
            summary.style.pointerEvents = "auto";
            summary.style.cursor = "default";
        }
    })
});