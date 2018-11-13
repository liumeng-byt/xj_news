import logging
from logging.handlers import RotatingFileHandler

from flask import current_app
from flask import render_template
from flask import session
from flask.ext.wtf.csrf import generate_csrf
from redis import StrictRedis
from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session



redis_store = None
# 创建mysql操作对象的变量
db = SQLAlchemy()


def setup_log(log_level):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=log_level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    # 日志保存的目录需要手动创建
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """初始化函数"""
    # flask 实例对象的初始化,import_name指的是 __name__ 就是程序所在的包（模块）
    app = Flask(__name__)

    # 根据配置文件中的字典查找对应的配置类
    Config = config[config_name]

    # 加载配置类到flask项目中
    app.config.from_object(Config)

    # 加载配置信息到SQLAlchemy
    # global db
    # db = SQLAlchemy(app)
    db.init_app(app)  # 关联db和app

    # 实例化redis操作对象
    global redis_store
    redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DATA_DB)

    # 开启csrf的防范机制,csrf保护关联app
    CSRFProtect(app)
    # 在每次客户端请求成功以后，自动执行
    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token",csrf_token)
        return response

    # 开启session,把Session对象和app关联
    Session(app)

    # 启动日志功能
    setup_log(Config.LOG_LEVEL)

    # 把视图函数的蓝图注册到app
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    # 把验证蓝图（短信）注册到app
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    # 注册自定义的过滤器（用于点击排行的前三个序号颜色）
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, "index_class") #过滤器可直接在html中使用，不需要用return render_template("news/index.html",a=a)的形式

    # 注册新闻详情页蓝图
    from info.modules.new import news_blu
    app.register_blueprint(news_blu)

    # 捕获404异常，显示404页面
    from info.models import User
    @app.errorhandler(404)
    def page_not_found(_): # 如果某些变量或者参数表示没有意义的，可以用 _ 占位
        user_id = session.get("user_id")

        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        return render_template("news/404.html",
                               user=user,
                               )





    return app

# app=create_app("development") manage.py里 app接收的是上面的 return app