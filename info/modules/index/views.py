from flask import current_app
from flask import render_template

from . import index_blu

# 定义视图函数
@index_blu.route("/")
def index():
    # logging.fatal("致命错误")
    # logging.error("普通错误！")
    # logging.warning("警告错误！")
    # logging.info("普通日志信息！")
    # logging.debug("调试信息")
    title = "首页-新经资讯网"
    return render_template("news/index.html",title=title)

@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")