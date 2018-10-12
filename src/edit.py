from index import reindex
from util import update_config_ignore_file_list


def ignore(item_path):
    # 加入忽略列表
    update_config_ignore_file_list(item_path, True)
    # 重建索引
    reindex()
