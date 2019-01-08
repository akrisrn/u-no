Pace.on("done", function () {
    document.getElementById("content").style.opacity = "1";
    $("iframe.steam-widget").each(function () {
        this.setAttribute("src", `https:\/\/store.steampowered.com/widget/${this.getAttribute("data-id")}/`);
        this.removeAttribute("data-id");
        this.setAttribute("frameborder", "0");
        this.style.width = "100%";
        this.style.height = "200px";
    });
    $("iframe.kindle-widget").each(function () {
        this.setAttribute("src", `https:\/\/read.amazon.cn/kp/card?asin=${this.getAttribute("data-id")}&preview=inline`);
        this.removeAttribute("data-id");
        this.setAttribute("frameborder", "0");
        this.setAttribute("allowfullscreen", "");
        this.style.maxWidth = "100%";
        this.style.width = "336px";
        this.style.height = "550px";
    });
    $("img").each(function () {
        const imgSrc = this.getAttribute("data-src");
        if (imgSrc !== null) {
            this.setAttribute("src", imgSrc);
            this.removeAttribute("data-src")
        }
    })
});