Vue.component('vue-return-home', {
    template: `
<a href="/">
    <i style="margin-right: 10px" class="fas fa-angle-double-left"></i>~
</a>`
});

Vue.component('vue-tag', {
    props: ['url', 'name'],
    template: `
<div class="tag">
    <a v-bind:href="url"><i style="margin-right: 3px" class="fas fa-hashtag"></i>{{ name }}</a>
</div>`
});

Vue.component('vue-date', {
    props: ['date'],
    template: '<div class="date">{{ date }}</div>'
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

Vue.component('vue-home-li', {
    props: ['url', 'name', 'highlight'],
    template: `
<a v-bind:href="url" v-bind:class="{ 'article-hl': highlight }">
    <i class="fas fa-star" v-if="highlight"></i>
    {{ name }}
</a>`
});

Vue.component('vue-login-form', {
    props: ['error', 'referrer'],
    template: `
<div class="center">
    <h1 v-bind:class="{ 'pw-error': error }">* PASSWORD *</h1>
    <form method="post">
        <label>
            <input type="password" name="password" autofocus="autofocus"/>
        </label>
        <label>
            <input name="referrer" v-bind:value="referrer" style="display: none">
        </label>
        <button type="submit" style="display: none">Submit</button>
    </form>
</div>`
});

Vue.component('vue-error', {
    props: ['title'],
    template: '<div class="center"><h1>{{ title }}</h1></div>'
});

Vue.component('vue-index-tab-button', {
    props: ['name', 'id'],
    template: `
<button class="tablinks" v-bind:id="id">
    <i style="margin-right: 10px" class="far fa-folder"></i>{{ name }}
</button>`
});

Vue.component('vue-check', {
    props: ['checked'],
    template: `
<i v-bind:class="['fas', checked ? 'fa-check' : 'fa-times', 'check']"></i>`
});

new Vue({el: '#content'});