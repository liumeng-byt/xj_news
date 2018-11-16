from flask import current_app
from flask import g, jsonify
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import user_login_data, db
from info.modules.profile import profile_blu
from info.utils.common import file_storage
from info.utils.response_code import RET


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
    # 获取当前登陆用户的信息
    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if request.method == "GET":
        return render_template("news/user_base_info.html",
                            user=user)
    else:

        """post提交数据"""
        # 1. 获取json数据
        data_dict = request.json
        signature = data_dict.get("signature")
        nick_name = data_dict.get("nick_name")
        gender = data_dict.get("gender")

        # 2. 校验数据
        if not all([nick_name, gender, signature]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

        if gender not in (['MAN', 'WOMAN']):
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

        # 3. 保存更改的数据
        user.nick_name = nick_name
        user.gender = gender
        user.signature = signature
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

        # 将 session 中保存的数据进行实时更新
        session["nick_name"] = nick_name

        # 4. 返回操作结果
        return jsonify(errno=RET.OK, errmsg="更新成功")


#修改头像
@profile_blu.route("/user_pic_info",methods=["POST","GET"])
@user_login_data
def user_pic_info():
    """修改头像"""
    # 获取当前登陆用户的信息
    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if request.method == "GET":
        return render_template("news/user_pic_info.html",
                               user=user)

    else:
        """post就要接收上传过来的文件，并把上传的文件保存到七牛云"""
        # 1.上传来的头像文件【read 读取】
        avatar = request.files.get("avatar").read()

        #存到七牛云
        try:
            # 上传文件名
            avatar_files_name = file_storage(avatar)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

        # 拼接完整的头像地址
        user.avatar_url = constants.QINIU_DOMIN_PREFIX + avatar_files_name

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存用户数据错误")

        # 4. 返回上传的结果<avatar_url>
        return jsonify(errno=RET.OK, errmsg="OK", data={"avatar_url": user.avatar_url})














