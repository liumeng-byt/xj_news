from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from info import constants
from info import user_login_data, db
from info.models import News, Category
from info.modules.profile import profile_blu
from info.utils.common import file_storage
from info.utils.response_code import RET


# 后台个人中心
@profile_blu.route("/info")
@user_login_data
def user_info():
    """后台个人中心"""

    # 获取登陆信息
    user = g.user

    return render_template("news/user.html",
                           user=user
                           )


# 个人中心-修改个人基本信息
@profile_blu.route("/user_base_info", methods=["POST", "GET"])
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


# 个人中心-修改头像
@profile_blu.route("/user_pic_info", methods=["POST", "GET"])
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

        # 存到七牛云
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


# 个人中心-我的关注
@profile_blu.route("/user_follow")
@user_login_data
def user_follow():
    """个人中心显示我的关注"""
    # 获取页数

    p = request.args.get("p", 1)  # 当前页数
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)


    # 获取当前用户的信息
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户为登录")

    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(p, constants.USER_FOLLOWED_MAX_COUNT, False)
        # 获取所有数据数据（列表）
        follows = paginate.items

        # 获取当前页
        current_page = paginate.page

        # 获取总页数
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []
    for follow_user in follows:
        user_dict_li.append(follow_user.to_dict())  # to_dict 为转换成字典格式
    print(user_dict_li)

    data = {"user": user_dict_li, "total_page": total_page, "current_page": current_page}

    return render_template("news/user_follow.html", data=data, user=user)


# 个人中心-修改密码
@profile_blu.route("/pass_info", methods=["GET", "POST"])
@user_login_data
def pass_info():
    """修改密码"""
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    else:
        """post发送数据，修改密码"""
        # 1. 接收旧密码，新密码，确认密码
        data_dict = request.json
        old_password = data_dict.get("old_password")
        new_password = data_dict.get("new_password")
        new_password2 = data_dict.get("new_password2")

        # 2. 校验参数
        if not all([old_password, new_password, new_password2]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

        if new_password != new_password2:
            return jsonify(errno=RET.PARAMERR, errmsg="新密码和确认密码不一致")

        # 2.1 判断密码是否正确
        if not user.check_passowrd(old_password):
            return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

        # 3. 更新密码[ 新密码要加密 ]
        user.password = new_password

        # 3.1 保存更新
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

        # 4. 返回结果
        return jsonify(errno=RET.OK, errmsg="保存成功")


# 个人中心-新闻列表页面
@profile_blu.route("/news_list")
@user_login_data
def news_list():
    """
    1.获取页数
    2.获取user
    3.到数据库把数据查询出来（查询出来的每个成员都是个对象）
    4.【分页数据，总页，当前页】
    5.添加进列表，同时转换成字典
    6.传给前端
    :return:
    """
    # 获取当前页数1代表当前显示出来的是第一页
    p = request.args.get("p",1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
    # 获取用户
    user = g.user

    # 初始化变量
    news_list = []
    current_page = 1
    total_page = 1

    # 数据库获取数据
    try:
        # .paginate(当前页p，每页显示多少数据)
        paginate = News.query.filter(News.user_id == user.id).paginate(p,constants.USER_COLLECTION_MAX_NEWS2)

        # 获取所有数据（成员都是对象）
        news_list = paginate.items

        # 获取当前页
        current_page = paginate.page

        # 获取总页
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news_item in news_list:
        news_dict_list.append(news_item.to_basic_dict())
    data = {"news_list":news_dict_list,"total_page":total_page,"current_page": current_page}


    return render_template("news/user_news_list.html",
                           data=data
                           )



# 个人中心-发布新闻
@profile_blu.route("/user_news_release",methods=["GET","POST"])
@user_login_data
def user_news_release():
    """用户发布新闻"""
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    categories = 1
    if request.method == "GET": # get请求，则直接显示页面
        try:
            categories = Category.query.filter(Category.name != "最新").all() # 获取所有的分类数据
        except Exception as e:
            current_app.logger.error(e)
        return render_template("news/user_news_release.html",
                               categories=categories
                               )

    # 如果不是get请求，则需要接受表单提交的新增新闻内容
    # 1. 后端接收参数[ 标题、分类id、摘要、内容、上传图片 ]
    data_dict = request.form
    data_dict.get("")
    title = data_dict.get("title") # 新闻标题
    source = "刘小猛" # 新闻来源
    digest = data_dict.get("digest") # 新闻摘要
    content = data_dict.get("content") # 新闻内容
    index_iamge = request.files.get("index_image") # 图片
    category_id = data_dict.get("category_id")


    # 2.校验数据
    if not all([source,title,digest,content,index_iamge,category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 获取图片的内容，通过read()
    try:
        index_iamge = index_iamge.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 保存数据，图片上传到7牛云
    try:
        key = file_storage(index_iamge) # 上传到7牛云，获取图片的地址key
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.THIRDERR,errmsg = "上传图片出错")

    news = News()
    news.title = title
    news.source = source
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = user.id
    print(category_id)

    # 1代表带审核状态
    news.status = 1

    # 响应数据
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(err=RET.DBERR,errmsg="保存数据失败")

    # 返回结果（因为是表单提交数据，所以直接可以后端指定要跳转的页面）
    return redirect(url_for("user.user_news_list"))


# 个人中心-我的收藏
@profile_blu.route("/collection")
@user_login_data
def user_collection():
    """
    1.获取页数
    2.获取user
    3.到数据库把数据查询出来（查询出来的每个成员都是个对象）
    4.【分页数据，总页，当前页】
    5.添加进列表，同时转换成字典
    6.传给前端
    """
    # 获取当前页数
    p = request.args.get("p",1)
    try:
        p=int(p)
    except Exception as e:
        current_app.logger.error(e)

    # 获取用户
    user = g.user

    #初始化变量
    # collections = []
    # current_page = 1
    # total_page = 1

    try:
        # 进行分页查询数据
        paginate = user.collection_news.paginate(p,constants.USER_COLLECTION_MAX_NEWS2,False)

        # 获取所有分页数据【每一个成员都是对象，需要转化成字典】
        collections = paginate.items

        # 获取当前页
        current_page = paginate.page

        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取数据失败")

    #收藏列表
    collection_dict_li = []
    for news in collections:
        collection_dict_li.append(news.to_basic_dict())

    data = {"total_page":total_page,"current_page":current_page,"collections":collection_dict_li}


    return render_template("news/user_collection.html",
                           data=data)
