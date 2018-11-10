import logging
from logging.handlers import RotatingFileHandler

from redis import StrictRedis
from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session

# 创建保存redis操作对象的全局变量
redis = None
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
    global redis
    redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DATA_DB)

    # 开启csrf的防范机制,csrf保护关联app
    CSRFProtect(app)

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

    return app

# app=create_app("development") manage.py里 app接收的是上面的 return app