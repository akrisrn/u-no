$(function () {
    $($('details').get().reverse()).each(function () {
        const parentText = $(this).parent().find(">summary>.tag>a").text();
        const summary = this.children[0];
        const aTag = $(summary).find(">.tag>a");
        if (parentText !== "") {
            aTag.html(aTag.html().replace(new RegExp(`</i>${parentText} /`), "</i>"))
        }
        let count = $(summary).find(">.date").text();
        count = count.substr(1, count.length - 2);
        aTag.css("font-size", `${12 + Math.round(Math.log(count)) * 3}px`);
        summary.style.paddingBottom = "6px";
        if (this.childElementCount === 1) {
            this.classList.add("readonly");
            summary.style.pointerEvents = "auto";
            summary.style.cursor = "default";
        }
        this.classList.add("tags");
    })
});