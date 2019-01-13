Pace.on("done", function () {
    document.getElementById("content").style.opacity = "1";
    const fillFrame = (e, src, width, height) => {
        e.setAttribute("src", src.replace("%s", e.getAttribute("data-id")));
        e.removeAttribute("data-id");
        e.setAttribute("frameborder", "0");
        e.style.maxWidth = "100%";
        e.style.width = width;
        e.style.height = height;
    };
    $("iframe.steam-widget").each(function () {
        fillFrame(this, "https:\/\/store.steampowered.com/widget/%s/", "100%", "200px");
    });
    $("iframe.kindle-widget").each(function () {
        fillFrame(this, "https:\/\/read.amazon.cn/kp/card?asin=%s&preview=inline", "336px", "550px");
        this.setAttribute("allowfullscreen", "");
    });
    $("iframe.music-widget").each(function () {
        fillFrame(this, "https:\/\/music.163.com/outchain/player?type=2&id=%s&auto=0&height=66", "100%", "86px");
        this.style.top = "12px";
        this.style.position = "relative";
    });
    $("img").each(function () {
        const imgSrc = this.getAttribute("data-src");
        if (imgSrc !== null) {
            this.setAttribute("src", imgSrc);
            this.removeAttribute("data-src")
        }
    })
});