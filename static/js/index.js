$(function () {
    let inputs = [$("#idS"), $("#titleS"), $("#tagS"), $("#dateS")];
    let flags = ["i", "n", "t", "d"];

    inputs.forEach(function (item) {
        item.keydown(function () {
            if (event.keyCode === 13) search.click()
        });
    });

    let request = function () {
        let url = location.search;
        let request = {};
        if (url.indexOf("?") !== -1) {
            let str = url.substr(1);
            let strList = str.split("&");
            for (let i = 0; i < strList.length; i++) {
                request[strList[i].split("=")[0]] = decodeURI(strList[i].split("=")[1]);
            }
        }
        return request;
    }();

    inputs.forEach(function (item, index) {
        item.val(request[flags[index]]);
    });

    $("#search").click(function () {
        let values = [];
        inputs.forEach(function (item) {
            values.push($.trim(item.val()))
        });

        let href = "";

        values.forEach(function (item, index) {
            if (item !== "") href += "&" + flags[index] + "=" + item
        });

        if (href !== "") href = "?" + href.substr(1);

        window.location.href = window.location.pathname + href
    });

    $("#clean").click(function () {
        inputs.forEach(function (item) {
            item.val("");
        });
    });

    for (let tab of $(".tablinks")) {
        $(tab).click(function (evt) {
            let clickElement = document.getElementById(this.innerText);
            let isDisplay = clickElement.style.display !== "block";

            let i, tabcontent, tablinks;

            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }

            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
                tablinks[i].children[0].className = tablinks[i].children[0].className.replace("-open", "");
            }

            if (isDisplay) {
                clickElement.style.display = "block";
                evt.currentTarget.className += " active";
                this.children[0].className = this.children[0].className + "-open"
            }
        })
    }

    let defaultOpen = document.getElementById("defaultOpen");
    if (defaultOpen !== null) defaultOpen.click()
});

function edit(_this, type) {
    let textDiv = _this.parentElement.previousElementSibling;
    textDiv.style.display = "none";
    let text = textDiv.innerText;

    let input = document.createElement("input");
    input.type = type;
    input.value = text;

    let editDiv = document.createElement("div");
    editDiv.appendChild(input);
    textDiv.parentElement.insertBefore(editDiv, textDiv);

    _this.style.display = "none";
    let next = _this.nextElementSibling;
    next.style.display = "inline";
    // noinspection JSUnresolvedVariable
    next.nextElementSibling.style.display = "inline";
}

function submit(_this, url) {
    let parent = _this.parentElement.parentElement;
    let data = parent.children[0].children[0].value;
    $.getJSON(url, {data}, (result) => {
        if (result) {
            parent.children[1].innerText = data;
        }
        cancel(_this.nextElementSibling)
    })
}

function cancel(_this) {
    let textDiv = _this.parentElement.previousElementSibling;
    textDiv.style.display = "inline";
    let editDiv = textDiv.previousElementSibling;
    editDiv.remove();

    _this.style.display = "none";
    let pre = _this.previousElementSibling;
    pre.style.display = "none";
    // noinspection JSUnresolvedVariable
    pre.previousElementSibling.style.display = "inline";
}