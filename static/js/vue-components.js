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
    <a href="{{ url }}">
        <i style="margin-right: 3px" class="fas fa-hashtag"></i>{{ name }}
    </a>
</div>`
});

new Vue({el: '#content'});