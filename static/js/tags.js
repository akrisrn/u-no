$(function () {
    $($('ul').get().reverse()).each(function () {
        const parentText = $(this).parent().find(">.tag>a").text();
        $(this).find(">li").each(function () {
            const aTag = $(this).find(">.tag>a");
            if (parentText !== "") {
                aTag.html(aTag.html().replace(new RegExp(`</i>${parentText}/`), "</i>"))
            }
        });
    })
});