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
    $("img").each(function () {
        const imgSrc = this.getAttribute("data-src");
        if (imgSrc !== null) {
            this.setAttribute("src", imgSrc);
            this.removeAttribute("data-src")
        }
    })
});