
import random
import re
from datetime import datetime

from flask import current_app, jsonify
from flask import request
from flask import session

from info import constants, redis_store, db
from info.models import User
from info.utils.response_code import RET
from info.utils.yuntongxun.sms import CCP

from . import passport_blu
from info.utils.captcha.captcha import captcha
from flask import make_response


@passport_blu.route("/image_code")
def image_code():
    """图片验证功能"""
    name, text, image = captcha.generate_captcha()
    # 1.调用图片验证码模块生成的图片验证码
    # name表示验证码图片的文件名（这里不需要使用）
    # text 表示验证码图片中的文本信息
    # image 表示验证码图片的二进制内容

    # 2. 保存图片验证的文本到redis中，以uuid作为key，以文本作为value
    image_code_id = request.args.get("image_code_id")  # 把图片的UUID拿到
    # print(image_code_id)
    # 判断是否存在UUID
    if not image_code_id:
        current_app.logger.error("图片验证码缺少uuid")  # 记录日志
        # return make_response("图片验证码缺少")  # 有时存在编码问题，需要返回json格式
        return make_response(jsonify(error=RET.PARAMERR, errmsg="缺少UUID"))

    # 保存在redis
    try:
        redis_store.setex("image_code_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES,
                          text)  # 以第一个参数uuid作为key，以text作为value；把text内容保存300秒
    except Exception as e:
        current_app.logger.error("保存图片验证文本失败")
        return make_response(jsonify(errno=RET.DATAERR, errmsg="保存验证文本失败"))  # 错误码和错误信息

    # 3. 把图片返回给客户端浏览器
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpeg"  # 【设置响应头】告诉浏览器，返回内容的格式是图片
    return response


@passport_blu.route("/sms_code", methods=["POST"])
def sms_code():
    """发送短信功能"""
    # 接收客户端浏览器发送过来的参数并判断是否有值（json格式数据）
    data_dict = request.json
    mobile = data_dict.get("mobile")
    image_code = data_dict.get("image_code")
    image_code_id = data_dict.get("image_code_id")

    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.DATAERR, errmsg="参数不全")

    # 校验手机号
    if not re.match("^1[356789][0-9]{9}$", mobile):
        return jsonify(erro=RET.DATAERR, errmsg="手机号不符合规则")
    # 判断手机好是否已经被注册过
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="查询数据错误")
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")


        # 图片编码（image_code_id）和redis中的数据对比校验
    try:
        real_image_code = redis_store.get("image_code_" + image_code_id)
        if real_image_code:
            real_image_code = real_image_code.decode()
            # 保证一个图片验证码换一个短信验证码，所以提取出真是图片验证码以后，删除掉redis中的
            redis_store.delete("image_code_" + image_code_id)
    except Exception as e:
        current_app.logger.error("图片验证码不存在")
        return make_response(jsonify(errno=RET.DATAERR, errmsg="图片验证码不存在"))

        # 判断redis中的图片验证码是否过期了
    if not real_image_code:
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

        # 判断图片验证码是否正确
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg="图片验证码错误")

        # 5. 生成随机的短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # ccp = CCP()
    # ret = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
    #                             constants.SMS_CODE_TEMPLATE_ID)
    #
    # if ret == -1:
    #     # 发送短信失败
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    # 7. 把短信验证吗保存redis中，再后面用户提交表单的时候，要验证短信验证码是否正确
    try:
        redis_store.set("sms_code_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    # 8. 响应结果给客户端
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blu.route("/register",methods=["POST"])
def register():
    """用户注册，保存用户信息"""
    # 1. 获取参数和判断是否有值
    data_dict = request.json
    mobile = data_dict.get("mobile")
    sms_code = data_dict.get("sms_code")
    password = data_dict.get("password")
    # agree = data_dict.get("agree")  # 是否同意了注册条款
    print([mobile, sms_code, password])

    if not all([mobile, sms_code, password]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2. 从redis中获取指定手机号对应的短信验证码的
    try:
        real_sms_code = redis_store.get("sms_code_" + mobile)
        if real_sms_code:
            real_sms_code = real_sms_code.decode()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="获取短信验证码错误")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期了")

    # 3. 校验短信验证码
    if real_sms_code != sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="短信验证码错误")

    # 4. 初始化 user 模型，并设置数据并添加到数据库
    user = User()
    # 把用户提交过来的数据保存模型中
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # 回滚事务
        current_app.logger.error(e)
        # 数据保存错误
        return jsonify(errno=RET.DATAERR, errmsg="数据保存错误")

    # 5. 保存当前用户的登陆状态，保存session中
    session["mobile"] = mobile
    # session["nick_name"] = mobile #默认手机号是昵称
    session["nick_name"] = user.nick_name #默认手机号是昵称
    session["user_id"] = user.id

    # 6. 返回注册的结果
    return jsonify(errno=RET.OK, errmsg="OK")

@passport_blu.route("/login",methods=["POST"])
def login():
    """登陆"""
    #获取参数和判断是否有值,登陆只需要获取手机号和密码
    json_data = request.json
    mobile = json_data.get("mobile")
    password = json_data.get("password")

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据错误")

    if not user:
        return jsonify(errno=RET.USERERR,errmsg="用户不存在")

    #校验密码
    if not user.check_passowrd(password):
        print(password)
        print(user.check_passowrd(password))
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 保存登陆状态
    session["mobile"]=mobile
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name

    #修改用户的最后登陆时间
    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        #如果出错记录下来即可，没必要阻止用户登陆
        current_app.logger.error(e)

    #返回结果
    return jsonify(errno=RET.OK,errmsg="OK")


@passport_blu.route("/logout",methods=["GET","POST"])
def logout():
    """退出登录"""
    # 清除当前用户的登录状态，# pop 是字典中移除掉指定的键值对成员，第二个参数防止报错，设置默认值
    session.pop("user_id",None)
    session.pop("nick_name",None)
    session.pop("mobile",None)

    return jsonify(errno=RET.OK,errmsg="退出成功")
