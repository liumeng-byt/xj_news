from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import db
from info.models import News, User
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blu


@news_blu.route("/<int:news_id>")
@user_login_data
def detail(news_id):
    """新闻详情"""
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404) # 查询错误，抛出异常

    if not news:
        abort(404) # 查不到数据，跑出异常

    # 如果查到数据，则记录点击量,并提交到库里
    news.clicks += 1

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    # 查询点击排行的咨询列表
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 查询当前登陆的用户信息
    # 上面的视图函数已经被装饰器user_login_data 装饰了，所以直接从g.user提取即可
    user = g.user


    return render_template("news/detail.html",
                           user=user,
                           news_list=news_list,
                           news=news
                           )


@news_blu.route("/news_collect",methods=["POST"])
@user_login_data
def news_collect():
    """新闻收藏"""
    user = g.user
    json_data = request.json
    news_id = json_data.get("news_id")
    action = json_data.get("action")

    #判断是否已登录
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登陆")

    # 如果没有登陆
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 如果请求不属于collect，cancel_collect
    if action not in ("collect","cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 拿到参数后，到库里查询
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    # 如果没有查询到
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    # 收藏
    if action == "collect":
        user.collection_news.append(news) #添加一条收藏记录
    # 取消收藏
    else:
        user.collection_news.remove(news) # 删除一条收藏记录

    try:
        db.session.commit() # 提交
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback() # 提交失败时 回滚事物
        return jsonify(errno=RET.DBERR, errmsg="保存失败")

    # 最后返回结果
    return jsonify(errno=RET.OK, errmsg="操作成功")