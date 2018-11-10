import random
import re

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

    ccp = CCP()
    ret = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                constants.SMS_CODE_TEMPLATE_ID)

    if ret == -1:
        # 发送短信失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    # 7. 把短信验证吗保存redis中，再后面用户提交表单的时候，要验证短信验证码是否正确
    try:
        redis_store.set("sms_code_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    # 8. 响应结果给客户端
    return jsonify(errno=RET.OK, errmsg="发送成功")


# @passport_blu.route("/register",methods=["POST"])
# def register():
#     """注册信息"""
#     # 获取参数和判断是否有值
#     json_data = request.json
#     mobile = json_data.get("mobile")
#     sms_code = json_data.get("smscode")
#     password = json_data.get("password")
#
#     # 验证用户提交的数据
#     if not all([mobile,sms_code,password]):
#         return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
#
#     # 检验手机号是否正确
#     if not re.match("^1[345789][0-9]{9}$",mobile):
#         return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")
#
#     # 验证短信验证码
#     try:
#         real_sms_code = redis_store.get("SMS_%s" % mobile)
#         real_sms_code = real_sms_code.decode()
#         print(real_sms_code)
#         if not real_sms_code:
#             return jsonify(errno=RET.DATAERR, errmsg="短信验证码已过期")
#         # 如果可以获取到真实的图片验证码，则删除掉redis中的文本数据，
#         redis_store.delete("SMS_"+mobile)
#     except Exception as e:
#         current_app.logger.error(e)
#         # 获取短信验证码失败
#         return jsonify(errno=RET.DBERR, errmsg="获取短信验证码失败")
#
#         # 把用户提交过来的短信验证码和redis中真实短信验证码比较
#     if real_sms_code != sms_code:
#         return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
#
#     # 根据手机号到数据库中查询，当前手机是否已经被注册
#     num = User.query.filter(User.mobile == mobile).count()
#     if num > 0:
#         return jsonify(errno=RET.DATAERR, errmsg="手机号码已经被注册了")
#
#     # 3. 保存用户信息
#     user = User()
#     user.mobile = mobile
#     user.password = password
#     user.nick_name = mobile #使用手机号作为默认的昵称
#
#     try:
#         db.session.add(user)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DATAERR, errmsg="数据保存错误")
#
#     # 注册成功以后，自动保存登陆状态
#     session["user_id"] = user.id
#     session["nick_name"] = user.nick_name
#     session["mobile"] = user.mobile
#
#     # 返回注册结果
#     return jsonify(errno=RET.OK, errmsg="OK")
