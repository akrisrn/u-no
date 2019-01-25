$(function () {
    const getScrollTop = () => {
        return document.documentElement.scrollTop + document.body.scrollTop;
    };
    const setScrollTop = (value) => {
        if (document.documentElement.scrollTop) {
            document.documentElement.scrollTop = value;
        } else {
            document.body.scrollTop = value;
        }
    };

    const toTopDiv = $("#to-top");
    $(window).scroll(() => {
        if (getScrollTop() > 0) {
            toTopDiv.css("opacity", "1")
        } else {
            toTopDiv.css("opacity", "");
        }
    });
    toTopDiv.click(() => {
        const goTop = setInterval(() => {
            setScrollTop(getScrollTop() / 1.1);
            if (getScrollTop() < 1) clearInterval(goTop);
        }, 10);
    });
});