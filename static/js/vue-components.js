Vue.component('vue-return-home', {
    props: {
        url: {
            default: "/"
        },
        name: {
            default: "~"
        }
    },
    template: `<a v-bind:href="url"><vue-return-home-icon style="margin-right: 10px"></vue-return-home-icon>{{ name }}</a>`
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
    <a v-bind:href="tags_url"><vue-tag-icon v-if="is_first" style="margin-right: 8px"></vue-tag-icon></a><a v-bind:href="url"><vue-hashtag-icon style="margin-right: 3px"></vue-hashtag-icon>{{ name }}</a>
</div>`
});

Vue.component('vue-date', {
    props: ['date'],
    template: '<div class="date">{{ date }}</div>'
});

Vue.component('vue-home-li', {
    props: {
        url: String, name: String, is_highlight: {
            type: Boolean,
            default: false
        }
    },
    template: `<a v-bind:href="url" v-bind:class="{'article-hl': is_highlight}"><vue-star-icon style="margin-right: 8px;" v-if="is_highlight"></vue-star-icon>{{ name }}</a>`
});

Vue.component('vue-error', {
    props: ['title'],
    template: '<div class="center"><h1>{{ title }}</h1></div>'
});

Vue.component('vue-index-tab-button', {
    props: ['name', 'id'],
    template: `
<button class="tablinks" v-bind:id="id">
    <vue-folder-icon style="margin-right: 8px"></vue-folder-icon>{{ name }}
</button>`
});

Vue.component('vue-tag-icon', {
    template: '<i class="fas fa-tags fa-xs"></i>'
});

Vue.component('vue-hashtag-icon', {
    template: '<i class="fas fa-hashtag"></i>'
});

Vue.component('vue-home-li-icon', {
    template: '<i class="fas fa-angle-double-right"></i>'
});

Vue.component('vue-return-home-icon', {
    template: '<i class="fas fa-angle-double-left"></i>'
});

Vue.component('vue-star-icon', {
    template: '<i class="fas fa-star"></i>'
});

Vue.component('vue-folder-icon', {
    template: '<i class="far fa-folder"></i>'
});

Vue.component('vue-check-icon', {
    props: ['checked'],
    template: `<i v-bind:class="['fas', checked ? 'fa-check' : 'fa-times', 'check']"></i>`
});

new Vue({
    el: '#content',
    delimiters: ['{|', '|}']
});