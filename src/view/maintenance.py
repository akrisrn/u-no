from flask import Blueprint, render_template

maintenance = Blueprint("maintenance", __name__)


# 维护页面，配置中开启维护模式后所有访问都会定向到这里
# noinspection PyUnusedLocal
@maintenance.route('/', defaults={'path': ''})
@maintenance.route('/<path:path>')
def catch_all(path):
    return render_template('maintenance.html')
