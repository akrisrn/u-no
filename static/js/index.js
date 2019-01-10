$(function () {
    let inputs = [$("#idS"), $("#titleS"), $("#tagS"), $("#dateS")];
    let flags = ["i", "n", "t", "d"];

    inputs.forEach(function (item) {
        item.keydown(function () {
            if (event.keyCode === 13) $("#search").click()
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
    let parent = _this.parentElement.parentElement;
    let showDiv = _this.parentElement.previousElementSibling;
    showDiv.style.display = "none";
    let editDiv = document.createElement("div");
    editDiv.style.display = "inline";
    parent.insertBefore(editDiv, showDiv);

    if (type === "date") {
        let input = document.createElement("input");
        input.type = "date";
        input.classList.add("edit-input");
        input.classList.add("edit-date");
        input.value = showDiv.innerText;
        editDiv.appendChild(input);
    } else if (type === "tag") {
        for (let child of showDiv.children) {
            let input = document.createElement("input");
            input.classList.add("edit-input");
            input.classList.add("edit-tag");
            input.value = child.innerText;
            editDiv.appendChild(input);
        }
    }

    _this.style.display = "none";
    let next = _this.nextElementSibling;
    next.style.display = "inline";
    next.nextElementSibling.style.display = "inline";
}

function submit(_this, url, type) {
    let parent = _this.parentElement.parentElement;
    let editDiv = parent.children[0];
    let showDiv = parent.children[1];
    let data = "";
    if (type === "date") {
        data = editDiv.children[0].value;
    } else if (type === "tag") {
        for (let child of editDiv.children) {
            let inputData = child.value.trim().replace("，", ",");
            if (inputData === "" || inputData === default_tag) {
                continue;
            }
            let splitInputData = inputData.split(",");
            if (splitInputData.length > 1) {
                for (let split of splitInputData) {
                    let splitData = split.trim();
                    if (splitData === "" || splitData === default_tag) {
                        continue
                    }
                    data += splitData + ","
                }
            } else {
                data += inputData + ","
            }
        }
        data = data.substring(0, data.length - 1)
    }
    $.getJSON(url, {data}, (result) => {
        if (result) {
            if (type === "date") {
                showDiv.innerText = data;
            } else if (type === "tag") {
                let tagExmDiv = showDiv.children[0].cloneNode(true);
                showDiv.innerHTML = "";
                let splitData = data === "" ? [default_tag] : data.split(",");
                for (let split of splitData) {
                    let tagDiv = tagExmDiv.cloneNode(true);
                    tagDiv.children[0].childNodes[1].nodeValue = split;
                    showDiv.appendChild(tagDiv)
                }
            }
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
    pre.previousElementSibling.style.display = "inline";
}

flag_state = {};

function toggle(_this, urls, state) {
    if (flag_state[urls[0]] === undefined) {
        flag_state[urls[0]] = state;
    }
    $.getJSON(flag_state[urls[0]] ? urls[1] : urls[0], "", (result) => {
        if (result) {
            flag_state[urls[0]] = !flag_state[urls[0]];
            let classList = _this.children[0].classList;
            classList.toggle("fa-times");
            classList.toggle("fa-check")
        }
    })
}