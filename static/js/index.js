$(document).ready(function () {
    function GetRequest() {
        const url = location.search;
        const request = {};
        if (url.indexOf("?") !== -1) {
            const str = url.substr(1);
            const strList = str.split("&");
            for (let i = 0; i < strList.length; i++) {
                request[strList[i].split("=")[0]] = decodeURI(strList[i].split("=")[1]);
            }
        }
        return request;
    }

    const id = $("#idS");
    const title = $("#titleS");
    const tag = $("#tagS");
    const date = $("#dateS");

    const request = GetRequest();
    id.val(request["i"]);
    title.val(request["n"]);
    tag.val(request["t"]);
    date.val(request["d"]);

    $("#search").click(function () {
        const idVal = $.trim(id.val());
        const nameVal = $.trim(title.val());
        const tagVal = $.trim(tag.val());
        const dateVal = $.trim(date.val());
        let href = "";
        if (idVal !== "") {
            href += "&i=" + idVal
        }
        if (nameVal !== "") {
            href += "&n=" + nameVal
        }
        if (tagVal !== "") {
            href += "&t=" + tagVal
        }
        if (dateVal !== "") {
            href += "&d=" + dateVal
        }
        if (href !== "") {
            href = "?" + href.substr(1)
        }
        window.location.href = window.location.pathname + href
    });

    $("#clean").click(function () {
        id.val("");
        title.val("");
        tag.val("");
        date.val("");
    });

    document.getElementById("defaultOpen").click();
});

function openCity(evt, cityName, t) {
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

    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
    t.children[0].className = t.children[0].className + "-open"
}