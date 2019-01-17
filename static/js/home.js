let currentPageNum;

$(function () {
    const showArrow = (button, is_left, is_disable) => {
        button.find(">i").removeClass().addClass(`fas fa-arrow-${is_left ? "left" : "right"}`);
        button.css("pointer-events", is_disable ? "none" : "auto");
    };
    const switchPage = (num) => {
        if (num < 1 || num > pageCount) {
            return;
        }
        $("ul > li").hide();
        showArrow(prevButton, false, true);
        showArrow(nextButton, true, true);

        $(`li.page-${num}`).fadeIn();
        if (num > 1) {
            showArrow(prevButton, true, false);
        }
        if (num < pageCount) {
            showArrow(nextButton, false, false);
        }
        for (let i = 0; i < pageCount; i++) {
            const pageButton = pageButtons[i];
            pageButton.classList.remove("hover");
            if (i === num - 1) {
                pageButton.classList.add("hover");
            }
        }
        scrollTo(0, 0);
        currentPageNum = num;

        $("ul > li:visible:first").css("margin-top", "0");
    };

    const buttonGroup = $(".button-group");
    const pageCount = buttonGroup.children().length - 2;
    const prevButton = buttonGroup.children().first();
    const nextButton = buttonGroup.children().last();
    const pageButtons = buttonGroup.children().slice(1, pageCount + 1);

    switchPage(1);

    for (let i = 0; i < pageCount; i++) {
        const pageButton = pageButtons[i];
        $(pageButton).click(() => {
            switchPage(i + 1);
        })
    }
    prevButton.click(() => {
        switchPage(currentPageNum - 1);
    });
    nextButton.click(() => {
        switchPage(currentPageNum + 1);
    });

    $(window).bind("keydown", (event) => {
        switch (event.key) {
            case "ArrowLeft":
                prevButton.click();
                break;
            case "ArrowRight" :
                nextButton.click();
                break;
        }
    });
});