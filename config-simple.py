# 以下三项只在直接运行主文件时生效
# 主机名
uno_host = "127.0.0.1"
# 端口
uno_port = 5000
# 是否开启调试
uno_debug = False

# 是否开启维护模式
uno_maintenance = False
# 静态文件目录
uno_static_dir_name = "static"

# 站点名
uno_site_name = ""
# 版本号
uno_version = ""
# 是否使用CDN引入静态库
uno_use_cdn = True

# 主页展示文字
uno_index_show_text = ""
# 侧边栏展示文字
uno_sidebar_show_text = ""
# 版权信息展示文字
uno_copyright_show_text = ""

# 根目录下文章目录名
uno_articles_dir_name = ""
# 文章目录下附件目录名字
uno_attachments_dir_name = ""
# 索引文件名
uno_index_file_name = ""
# 重建索引的URL名
uno_reindex_url_name = ""
# 更新程序的URL名
uno_update_url_name = ""
# 更新时重启的systemd服务名
uno_update_service_name = ""
# 重建索引的冷却时间
uno_reindex_limit_time = 60 * 10
# 更新的冷却时间
uno_update_limit_time = 60 * 10

# 忽略索引的文件名列表
uno_ignore_file_list = [uno_index_file_name]
# 把文件加入忽略列表的URL参数名
uno_make_file_ignore_arg = ""
# 忽略索引的目录名
uno_ignore_dir_list = [".git"]

# 文件名展示时剔除的前缀（可正则）
uno_strip_prefix = ""

# 无标签时默认标签名
uno_default_tag = ""
