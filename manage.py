from flask_script import Manager
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from  flask_migrate import Migrate, MigrateCommand
from redis import StrictRedis
from config import Config



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
