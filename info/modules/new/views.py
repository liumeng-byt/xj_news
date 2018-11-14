from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import db
from info.models import News, User, Comment
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

    #查询当前用户是否已经收藏了当前新闻
    is_collected = False # 默认没有收藏，因为有可能用户是没有登陆的
    # 首先判断用户是否登陆，如果已登录,收藏记录存在，就到页面中把已收藏显示出来并隐藏收藏
    if user:
        if news in user.collection_news:
            is_collected = True

    return render_template("news/detail.html",
                           user=user,
                           news_list=news_list,
                           news=news,
                           is_collected=is_collected
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


@news_blu.route("/news_comment")
def news_comment():
    """用户评论的新闻/回复评论"""
    user = g.user
    # 判断是否已登录
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")

    # 获取参数
    data_dict = request.json
    news_id = data_dict.get("news_id") # 哪一条新闻
    comment_str = data_dict.get("comment") # 评论内容
    parent_id = data_dict.get("parent_id") # 被评论id（要知道回复谁）

    # 校验参数
    if not all([news_id,comment_str]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 如果参数存在,就到数据库查询
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据失败")

    # 判断有没有查询到数据
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="该新闻不存在")


    # 如果查到数据，在数据库操作记录（初始化 Comment 模型）
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        """如果是回复评论，则需要添加parent_id"""
        comment.parent_id = parent_id


    # 初始化完后，保存数据
    try:
        db,session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app .logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="保存评论数据失败")

    # 被评论后，评论次数 +1 ，在更新新闻的评论总数 comments_count
    news.comments_count += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e) # 无需返回页面


    # 返回结果，因为是局部刷新，所以需要把新增的评论一并返回
    return jsonify(errno=RET.OK,errmsg = "评论成功",data=comment.to_dict())




























