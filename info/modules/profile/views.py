from flask import g
from flask import render_template
from flask import request

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

@profile_blu.route("/user_base_info",methods=["POST","GET"])
@user_login_data
def user_base_info():
    """修改个人基本信息"""
    # 获取登陆信息
    if request.method == "GET":
        user = g.user

        return render_template("news/user_base_info.html",
                           user=user
                           )
    else:
        """POST"""
        pass