from flask import current_app
from flask import render_template
from flask import session

from info.models import User
from . import index_blu

# 定义首页视图函数
@index_blu.route("/")
def index():
    # 查看当前已经登录的用户
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)


    title = "首页-新经资讯网"
    return render_template("news/index.html",title=title,user=user)


# 显示logo图标的视图函数
@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")