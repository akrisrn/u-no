function getTextCount() {
    const countStr = $(".markdown-body>*:not(.toc)").text().replace(/\s|·|~|@|%|-|\+|=|`|!|#|\$|\^|&|\*|\(|\)|_|\[|]|{|}|\\|\||;|:|"|'|,|\.|\/|<|>|\?|。|？|！|，|、|；|：|“|”|‘|’|（|）|《|》|〈|〉|【|】|『|』|「|」|﹃|﹄|〔|〕|…|—|～|﹏|￥/g, "").length.toString();
    const sep = parseInt(countStr.length / 3);
    const countList = [];
    let start = 0;
    for (let i = sep; i >= 0; i--) {
        const end = countStr.length - i * 3;
        if (end === 0) continue;
        countList.push(countStr.substring(start, end));
        start = end
    }
    return countList.join(",")
}

$(function () {
    const sortTd = $("table td.sort");
    sortTd.parent().parent().parent().tablesorter({sortList: [[0, 0]]});
    sortTd.parent().remove();
    const thead = $("thead");
    if (thead.text().trim() === "") {
        thead.remove()
    }

    $("p").each(function () {
        if (this.innerHTML === "") {
            this.remove()
        }
    });

    $('.star').raty({
        readOnly: true,
        starType: "i"
    });

    $("ul>li:first-child>details, ol>li:first-child>details").each(function () {
        this.innerHTML = this.innerHTML.replace(/<\/summary>\s/, "</summary><p>") + "</p>"
    });

    const toc = $(".toc");
    if (toc.length > 0) {
        if (toc.find("ul>li").length === 0) {
            toc.remove()
        } else {
            let tocDetails = $("<details>");
            tocDetails.addClass("toc");
            toc.wrap(tocDetails);
            const tocDetailsSummary = $("<summary>");
            tocDetailsSummary.append($("<strong>").text("TOC"));
            tocDetailsSummary.insertBefore(toc);
            $(toc.find('ul').get().reverse()).each(function () {
                $(this).replaceWith($('<ol class="number">' + $(this).html() + '</ol>'))
            });
            const changeTop = (tocDetails, scrollTop) => {
                const markdownBody = $(".markdown-body");
                const headerHeight = markdownBody.offset().top - 16;
                const bodyHeight = markdownBody.height() + markdownBody.offset().top;
                const isFixed = tocDetails.css("position") === "fixed";
                if (scrollTop + tocDetails.height() + 32 > bodyHeight) {
                    tocDetails.css("top", isFixed ? bodyHeight - tocDetails.height() - 32 - scrollTop :
                        bodyHeight - tocDetails.height() - 32)
                } else {
                    tocDetails.css("top", scrollTop > headerHeight ? (isFixed ? 0 : scrollTop) :
                        (isFixed ? headerHeight - scrollTop : headerHeight));
                }
            };
            const changeSth = (tocDetails) => {
                tocDetails.css("max-height", window.innerHeight - 50);
                if (window.innerWidth > 1520) {
                    tocDetails.attr("open", "");
                    $("#content").css("left", -100);
                } else {
                    tocDetails.removeAttr("open");
                    $("#content").css("left", 0);
                }
            };
            const setActive = (scrollTop) => {
                const tocA = $(".toc a,h1>a,h2>a,h3>a,h4>a,h5>a,h6>a");
                for (const h of $(".markdown-body").find("h1,h2,h3,h4,h5,h6").get().reverse()) {
                    if (scrollTop + 20 > h.offsetTop) {
                        tocA.each(function () {
                            if (this.getAttribute("href") === "#" + h.getAttribute("id")) {
                                this.classList.add("active")
                            } else {
                                this.classList.remove("active")
                            }
                        });
                        return
                    }
                }
                tocA.each(function () {
                    this.classList.remove("active")
                });
            };
            setTimeout(() => {
                const scrollTop = getScrollTop();
                tocDetails = $("details.toc");
                tocDetails.appendTo($(".markdown-body"));
                changeSth(tocDetails);
                changeTop(tocDetails, scrollTop);
                setActive(scrollTop)
            }, 1);
            $(window).resize(() => {
                const tocDetails = $("details.toc");
                changeSth(tocDetails);
                changeTop(tocDetails, getScrollTop());
            });
            $(window).scroll(() => {
                const scrollTop = getScrollTop();
                changeTop($("details.toc"), scrollTop);
                setActive(scrollTop)
            });
        }
    }

    $("summary").each(function () {
        if (this.innerHTML === "") {
            this.style.display = "none"
        }
    });

    $(".markdown-body").find("h1,h2,h3,h4,h5,h6").each(function () {
        $(this).html($("<a>").attr("href", "#" + $(this).attr("id")).html($(this).html()));
    });
});