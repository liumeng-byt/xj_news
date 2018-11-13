from flask import abort
from flask import current_app
from flask import render_template
from flask import session

from info import constants
from info import db
from info.models import News, User
from . import news_blu


@news_blu.route("/<int:news_id>")
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
    print(news.clicks)
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
    user_id = session.get("user_id")

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)


    return render_template("news/detail.html",
                           user=user,
                           news_list=news_list,
                           news=news
                           )
