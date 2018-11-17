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


# 修改个人基本信息
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


# 修改头像
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


# 我的关注
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
        p = 1

    # 获取当前用户的信息
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户为登录")

    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(p, constants.USER_FOLLOWED_MAX_COUNT, False)
        # 获取当前页数据
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

    data = {"user": user_dict_li, "total_page": total_page, "current_page": current_page}

    return render_template("news/user_follow.html", data=data, user=user)


# 修改密码
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


# 用户发布新闻的 列表页面
@profile_blu.route("/user_news_list",methods=["GET"])
@user_login_data
def user_news_list():
    """用户发布新闻列表页面"""
    # 根据当前用户的id查询对应的发布新闻
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    page = request.args.get("p",1) # 当前页码
    per_page = request.args.get("per_page",1) # 每页数据量

    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)

    # 总页码初始为1
    total_page = 1
    try:
        pagenation = News.query.filter(News.user_id == user.id).order_by(News.id.desc()).paginate(page,per_page,False)

        # 获取总页码
        total_page = pagenation.pages
    except Exception as e:
        current_app.logger.error(e)

    return render_template("news/user_news_list.html",total_page=total_page)



# ajax提供数据分页
@profile_blu.route("/user_get_news_list",methods=["GET"])
@user_login_data
def user_get_new_list():
    """ajax提供数据分页"""
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    # 接收参数
    # 从地址栏上面获取的数据，同意都是字符串，要进行分页，密码和每页数据量必须是int类型
    page = int(request.args.get("p",1)) # 当前页
    per_page = int(request.args.get("per_page",constants.OTHER_NEWS_PAGE_MAX_COUNT)) # 每页数据量

    # 初始化变量
    total_page = 1
    news_li = []
    current_page = 1

    # 根据当前用户的user_id查询所发布的新闻信息
    try:
        pagination = News.query.filter(News.user_id == user.id).order_by(News.id.desc()).paginate(page,per_page,False)

        # 获取当前页数据列表（是一个列表，成员是每一个数据模型的对象）
        news_li = pagination.items
        # 获取当前页
        current_page = pagination.page
        # 获取总页数
        total_page = pagination.pages
    except Exception as e:
        current_app.logger.error(e)

    # 因为接下来要返回数据给ajax,所以需要把对象转成字典
    news_dict_li = []
    for item in news_li:
        news_dict_li.append(item.to_basic_dict())

    return jsonify(errno =RET.OK,errmsg="操作成功",
                   news_dict_li=news_dict_li,
                   current_page=current_page,
                   total_page=total_page
                   )


# 发布新闻
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
    source = "个人发布" # 新闻来源
    digest = data_dict.get("digest") # 新闻摘要
    content = data_dict.get("content") # 新闻内容
    index_iamge = request.files.get("index_image") # 图片
    category_id = data_dict.get("category_id")


    # 2.校验数据
    if not all([title,digest,content,index_iamge,category_id]):
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



