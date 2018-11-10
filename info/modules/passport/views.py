from flask import current_app, jsonify
from flask import request
from info import constants, redis_store
from info.utils.response_code import RET

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
    # 判断是否存在UUID
    if not image_code_id:
        current_app.logger.error("图片验证码缺少uuid")  # 记录日志
        # return make_response("图片验证码缺少")  # 有时存在编码问题，需要返回json格式
        return make_response(jsonify(error=RET.PARAMERR, errmsg="缺少UUID"))

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

@passport_blu.route("/sms_code",method=["POST","GET"])
def sms_code():
    """发送短信功能"""
