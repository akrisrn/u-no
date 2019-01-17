let currentPageNum;

$(function () {
    function switchPage(num) {
        $("ul > li").hide();
        prevButton.hide();
        nextButton.hide();

        $(`li.page-${num}`).fadeIn();
        if (num > 1) {
            prevButton.show();
        }
        if (num < pageCount) {
            nextButton.show();
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
    }

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
        if (event.keyCode === 37) {
            if (prevButton.is(":visible")) {
                prevButton.click()
            }
        } else if (event.keyCode === 39) {
            if (nextButton.is(":visible")) {
                nextButton.click()
            }
        }
    });
});