from pymdownx.magiclink import SOCIAL_PROVIDERS, PROVIDER_INFO, MagiclinkExtension

RE_WEIBO_USER = r'\w{1,15}'
RE_WEIBO_EXT_MENTIONS = r'weibo:%s' % RE_WEIBO_USER

SOCIAL_PROVIDERS.add('weibo')
SOCIAL_PROVIDERS.add('steam')

PROVIDER_INFO.update({
    "weibo": {
        "provider": "Weibo",
        "url": "https://weibo.com",
        "user_pattern": RE_WEIBO_USER
    }
})


class MyMagiclinkExtension(MagiclinkExtension):
    def setup_shorthand(self, md, int_mentions, ext_mentions, config):
        if self.social_short:
            ext_mentions.append(RE_WEIBO_EXT_MENTIONS)

        super().setup_shorthand(md, int_mentions, ext_mentions, config)


def makeExtension(*args, **kwargs):
    return MyMagiclinkExtension(*args, **kwargs)
