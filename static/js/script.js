let keyInput = "";

$(function () {
    $("a").each(function () {
        const href = this.getAttribute("href");
        if (href && href.startsWith("http")) {
            this.setAttribute("target", "_blank")
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
    const random = (min, max, round) => {
        const result = Math.random() * (max - min) + min;
        return round === true ? Math.round(result) : result;
    };
    toTopDiv[0].addEventListener('click', function () {
        keyInput += "∨";
        if (keyInput.endsWith("∨∨∨∨∨∨∨")) {
            keyInput += "_";
            for (let i = 0; i < 100; i++) {
                const left = -100 - random(0, 200);
                const top = random(-20, window.innerHeight);
                const fontSize = random(12, 42);
                const color = `rgb(${random(0, 255, true)}, ${random(0, 255, true)}, ${random(0, 255, true)})`;
                const duration = random(1, 5);
                const versionDiv = $("<div>").css({
                    "left": left + `px`,
                    "top": top + "px",
                    "font-size": fontSize + "px",
                    "color": color,
                    "z-index": 100,
                    "position": "fixed", "transition": `all cubic-bezier(0.46, 1.47, 0.91,-0.46) ${duration}s`,
                    "-moz-transition": `all cubic-bezier(0.46, 1.47, 0.91,-0.46) ${duration}s`,
                    "-webkit-transition": `all cubic-bezier(0.46, 1.47, 0.91,-0.46) ${duration}s`,
                    "-o-transition": `all cubic-bezier(0.46, 1.47, 0.91,-0.46) ${duration}s`
                }).text(version);
                versionDiv[0].addEventListener("transitionend", function () {
                    this.remove()
                });
                $("body").append(versionDiv);
                setTimeout(() => {
                    versionDiv.css("left", window.innerWidth + "px")
                }, 1)
            }
        }
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
    <a v-if="is_first" v-bind:href="tags_url"><vue-tag-icon style="margin-right: 8px"></vue-tag-icon></a><a v-bind:href="url"><vue-hashtag-icon style="margin-right: 3px"></vue-hashtag-icon>{{ name }}</a>
</div>`
    });
    Vue.component('vue-date', {
        props: ['date'],
        template: '<div class="date" v-if="date">{{ date }}</div>'
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