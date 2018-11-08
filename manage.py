import logging
from flask_script import Manager
from  flask_migrate import Migrate, MigrateCommand
# from info.__init__ import app,db
from info import create_app,db

app=create_app("development")


# 使用终端脚本工具启动启动和管理flask项目
manager = Manager(app)

# 初始化数据迁移模块
Migrate(app, db)

# 给终端脚本工具新增增加数据迁移的相关命令
manager.add_command("db", MigrateCommand)
# 定义视图函数
@app.route("/")
def index():
    logging.fatal("致命错误")
    logging.error("普通错误！")
    logging.warning("警告错误！")
    logging.info("普通日志信息！")
    logging.debug("调试信息")

    return "hello news!"


# 运行项目
if __name__ == '__main__':
    # app.run()
    manager.run()
