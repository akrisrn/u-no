Vue.component('vue-return-home', {
    template: `
<a href="/">
    <i style="margin-right: 10px" class="fas fa-angle-double-left"></i>HOME
</a>`
});

Vue.component('vue-tag', {
    props: ['url', 'name'],
    template: `
<div class="tag">
    <a :href="url">
        <i style="margin-right: 3px" class="fas fa-hashtag"></i>{{ name }}
    </a>
</div>`
});

Vue.component('vue-date', {
    props: ['date'],
    template: '<div class="date">{{ date }}</div>'
});

Vue.component('vue-tag-icon', {
    template: '<i class="fas fa-tags fa-xs"></i>'
});

Vue.component('vue-home-li-icon', {
    template: '<i class="fas fa-angle-double-right"></i>'
});

Vue.component('vue-home-li', {
    props: ['url', 'name', 'highlight'],
    template: `
<a :href="url" :class="{ 'article-hl': highlight }">
    <i class="fas fa-star" v-if="highlight"></i>
    {{ name }}
</a>`
});

new Vue({el: '#content'});