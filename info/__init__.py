from redis import StrictRedis
from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session

#创建保存redis操作对象的全局变量
redis=None
#创建mysql操作对象的变量
db=SQLAlchemy()


def create_app(config_name):
    """初始化函数"""
    # flask 实例对象的初始化
    app = Flask(__name__)

    #根据配置文件中的字典查找对应的配置类
    Config=config[config_name]

    # 加载配置类到flask项目中
    app.config.from_object(Config)

    # 加载配置信息到SQLAlchemy
    # global db
    # db = SQLAlchemy(app)
    db.init_app(app)

    # 实例化redis操作对象
    global redis
    redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DATA_DB)

    # 开启csrf的防范机制
    CSRFProtect(app)

    # 开启session,并加载session配置
    Session(app)

    return app