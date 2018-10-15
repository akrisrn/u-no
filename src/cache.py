import os

from flask import current_app

cache_dict = {}


def build_cache(file_path, file_mtime=None):
    with open(file_path, "r" if file_mtime else "w", encoding='utf-8') as file:
        if file_mtime:
            file_data = file.read()
        else:
            file_data = "{}"
            file.write(file_data)
            file_mtime = os.path.getmtime(file_path)
    cache_dict[file_path] = []
    cache_dict[file_path].append(file_mtime)
    cache_dict[file_path].append(file_data)


def get_file_cache(file_path):
    if os.path.exists(file_path):
        file_mtime = os.path.getmtime(file_path)
        if file_path not in cache_dict:
            build_cache(file_path, file_mtime)
        else:
            if cache_dict[file_path][0] != file_mtime:
                build_cache(file_path, file_mtime)
    else:
        if file_path in cache_dict:
            del cache_dict[file_path]
        if file_path.endswith(current_app.config["INDEX_FILE_NAME"]):
            build_cache(file_path)
    return cache_dict[file_path][1]
