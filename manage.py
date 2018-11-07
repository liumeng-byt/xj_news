from flask_script import Manager
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
import base64, os
from  flask_migrate import Migrate, MigrateCommand

from redis import StrictRedis


class Config(object):
    # debug模式
    DEBUG = True
    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_SESSION_DB = 1
    REDIS_DATA_DB = 0

    SECRECT_KEY = base64.b64encode(os.urandom(48))  # 设置密钥

    # flask_session 的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_SESSION_DB)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒


# flask 实例对象的初始化
app = Flask(__name__)

# 加载配置类到flask项目中
app.config.from_object(Config)

# 加载配置信息到SQLAlchemy
db = SQLAlchemy(app)

# 实例化redis操作对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DATA_DB)

# 开启csrf的防范机制
CSRFProtect(app)

# 使用终端脚本工具启动启动和管理flask项目
manager = Manager(app)

# 初始化数据迁移模块
Migrate(app, db)

# 给终端脚本工具新增增加数据迁移的相关命令
manager.add_command("db", MigrateCommand)


# 定义视图函数
@app.route("/")
def index():
    return "hello news!"


# 运行项目
if __name__ == '__main__':
    # app.run()
    manager.run()
