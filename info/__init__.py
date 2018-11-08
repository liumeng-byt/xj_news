from redis import StrictRedis
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session



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

# 开启session,并加载session配置
Session(app)