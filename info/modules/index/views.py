from flask import current_app, jsonify
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blu


# 定义首页视图函数
@index_blu.route("/")
@user_login_data
def index():
    # 右上角登陆退出功能显示  通过session 查看当前已经登录的用户
    user = g.user

    # 点击排行
    news_clicks = None
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
        # print(news_list)
    except Exception as e:
        current_app.logger.error(e)

    # 获取新闻分类
    categorys = Category.query.all()


    title = "首页-新经资讯网"
    return render_template("news/index.html",
                           title=title,
                           user=user,
                           news_clicks=news_clicks,
                           categorys=categorys,
                           )


# 显示logo图标的视图函数
@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")



@index_blu.route("/news_list")
def news_list():
    """ajax请求新闻列表数据"""
    # 1. 接受参数，前段发送通过get参数发送
    data_dict = request.args
    page = data_dict.get("page",1) # 当前页码
    cid = data_dict.get("cid",1)   # 新闻分类ID
    per_page = data_dict.get("per_page",constants.HOME_PAGE_MAX_NEWS)  # 允许前端指定每一页的数据量，默认10
    try:
        page = int(page)
        per_page = int(per_page)
        cid = int(cid)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")


    # 2. 获取根据新闻分类获取新闻列表
    filters = []
    if cid != 1:
        # 根据指定的分类ID来查询新闻列表
        filters.append(News.category_id==cid)

    try:
        paginate = News.query.filter(*filters).order_by(News.id.desc()).paginate(page, per_page, False)
        # 获取查询出来的数据[items是一个列表，列表中的每一个成员都是模型对象]
        items = paginate.items
        # 获取到总页数
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    # 3. 返回数据之前需要把每一个模型对象转换成字典格式，因为js不识别python的模型对象
    news_dict_list = []
    for news in items:
        news_dict_list.append( news.to_basic_dict() )

    # ４. 返回结果
    return jsonify(errno=RET.OK, errmsg="OK",
                   totalPage=total_page,
                   currentPage=current_page,
                   newsList=news_dict_list,
                   cid=cid)






