from flask import current_app, jsonify
from flask import request
# from info import redis_store,constants
from info.utils.response_code import RET

from . import passport_blu
from info.utils.captcha.captcha import captcha
from flask import make_response

#
@passport_blu.route("/image_code")
def image_code():
    """图片验证"""
    name,text,image = captcha.generate_captcha()

    #把图片返回给浏览器
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpeg"
    return response

