from flask import g
from flask import render_template

from info import user_login_data
from info.modules.profile import profile_blu


@profile_blu.route("/info")
@user_login_data
def user_info():
    """后台个人中心"""

    # 获取登陆信息
    user = g.user




    return render_template("news/user.html",
                            user=user
                           )