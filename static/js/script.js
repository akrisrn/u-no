let keyInput = "";

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

$(function () {
    $("a").each(function () {
        const href = this.getAttribute("href");
        if (href && href.startsWith("http")) {
            this.setAttribute("target", "_blank")
        }
    });

    Object.assign(inputBinds, {
        "home": () => {
            window.location.href = "/"
        },
        "tags": () => {
            window.location.href = tags_url
        },
        "gg": () => {
            $("#content")[0].scrollIntoView(true);
            keyInput += "_";
        },
        "G": () => {
            $("#content")[0].scrollIntoView(false);
        },
        "zen": () => {
            $("#main>h1~:not(.markdown-body), #content>:not(#main), .toc, #to-top").hide()
        },
        "#": () => {
            let i = 7;
            let str = "";
            let char;
            do {
                char = keyInput.substr(keyInput.length - i++, 1);
                if (char === "-" && i > 8) {
                    str = char + str;
                    break
                }
            } while (!isNaN(parseInt(char)) && (str = char + str));
            if (str) {
                const links = $(".home li:visible>a, .toc li>a");
                if (links.length > 0) {
                    let num = parseInt(str);
                    if (num < 0) {
                        num += links.length
                    }
                    if (num >= 0 && num < links.length) {
                        links[num].click()
                    }
                }
            }
        },
        "Backspace": () => {
            keyInput = keyInput.substr(0, keyInput.length - 10)
        }
    });
    $(window).bind("keydown", (event) => {
        if (!$("textarea, input").is(':focus')) {
            keyInput += event.key;
            for (let key in inputBinds) {
                if (keyInput.endsWith(key)) {
                    inputBinds[key]();
                    break;
                }
            }
        }
    });

    const toTopDiv = $("#to-top");
    const showToTop = () => {
        if (getScrollTop() > 0) {
            toTopDiv.css("opacity", "1");
            toTopDiv.css("cursor", "pointer")
        } else {
            toTopDiv.css("opacity", "");
            toTopDiv.css("cursor", "auto")
        }
    };
    showToTop();
    $(window).scroll(() => {
        showToTop()
    });
    toTopDiv.click(() => {
        const goTop = setInterval(() => {
            setScrollTop(getScrollTop() / 1.1);
            if (getScrollTop() < 1) clearInterval(goTop);
        }, 10);
    });

    Vue.component('vue-return-home', {
        props: {
            url: {
                default: "/"
            },
            name: {
                default: "~"
            }
        },
        template: `<a v-bind:href="url" style="margin-right: 8px"><i style="margin-right: 10px" class="fas fa-angle-double-left"></i>{{ name }}</a>`
    });
    Vue.component('vue-tag', {
        props: {
            tags_url: String, url: String, name: String, is_first: {
                type: Boolean,
                default: false
            }
        },
        template: `
<div class="tag">
    <a v-if="is_first" v-bind:href="tags_url"><vue-tag-icon style="margin-right: 8px"></vue-tag-icon></a><a v-bind:href="url"><vue-hashtag-icon style="margin-right: 3px"></vue-hashtag-icon>{{ name.split("/").join(" / ") }}</a>
</div>`
    });
    Vue.component('vue-date', {
        props: ['date', 'update', 'count'],
        template: '<div class="date" v-if="date">{{ date }}<div><div class="update" v-if="count">Words: {{ count }}</div><div class="update" v-if="update"><div style="display: inline; margin-right: 8px">|</div>Update: {{ update }}</div></div></div><div class="date" v-else-if="count">Words: {{ count }}</div>'
    });
    Vue.component('vue-home-li', {
        props: {
            url: String, name: String, is_highlight: {
                type: Boolean,
                default: false
            }
        },
        template: `<a v-bind:href="url" v-bind:class="{'article-hl': is_highlight}" style="margin: 0 8px"><i style="margin-right: 8px;" class="fas fa-star" v-if="is_highlight"></i>{{ name }}</a>`
    });
    Vue.component('vue-error', {
        props: ['title'],
        template: '<div class="center"><h1>{{ title }}</h1></div>'
    });
    Vue.component('vue-index-tab-button', {
        props: ['name', 'id'],
        template: `
<button class="tablinks" v-bind:id="id">
    <i style="width: 14px; margin-right: 8px" class="far fa-folder"></i>{{ name }}
</button>`
    });
    Vue.component('vue-tag-icon', {
        template: '<i class="fas fa-tags fa-xs"></i>'
    });
    Vue.component('vue-hashtag-icon', {
        template: '<i class="fas fa-hashtag"></i>'
    });
    Vue.component('vue-check-icon', {
        props: ['checked'],
        template: `<i v-bind:class="['fas', checked ? 'fa-check' : 'fa-times', 'check']"></i>`
    });
    new Vue({
        el: '#main',
        delimiters: ['{|', '|}']
    });
});