# 函数中公用的代码，或者辅助代码


import functools

import qiniu
from flask import current_app
from flask import g
from flask import session


# 注册自定义的过滤器使用的函数（用于点击排行的前三个序号颜色）
def do_index_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


#获取当前登陆用户的信息的装饰器
def user_login_data(view_func):
    """获取当前登陆用户的信息的装饰器"""
    @functools.wraps(view_func) # 视图函数调用的时候会出现bug(比如在url_for()重定向到视图函数的时候)，需要私用@functools 进行还原
    def wrapper(*args,**kwargs):
        # 实现业务逻辑代码
        user_id = session.get("user_id")
        from info.models import User
        user = None
        if user_id:
            # 根据user_id到数据库中查询用户信息
            try:
                user = User.query.get(user_id) # 到数据库查询用户信息
            except Exception as e:
                current_app.logger.error(e)

        g.user = user # 把用户登陆信息保存到g变量，在本次请求结束之前提供数据的临时存储，给其他的方法使用
        return view_func(*args,**kwargs)
    return wrapper


# 上传到七牛云上面的文件数据
def file_storage(data):
    """
    :param data: 上传到七牛云上面的文件数据
    :return:
    """
    access_key = "UhYWJIgbXnIzPHiZdVCenSnWVksXLlOY4WBAYc91"
    secret_key = "kVIfTnGjvMU6U9f7l5n_0cTzG4rlGh_v-MXdcKlf"
    bucket_name = "gz-python7"

    # 上面的信息，需要手动加到配置中。

    q = qiniu.Auth(access_key, secret_key)  # 七牛云操作对象
    token = q.upload_token(bucket_name)  # bucket_name 存储空间名  gz-python7
    ret, info = qiniu.put_data(token, None, data)
    print(ret)
    return ret.get("key")