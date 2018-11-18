import datetime
import logging
import random

from info import models
from flask_script import Manager
from  flask_migrate import Migrate, MigrateCommand
# from info.__init__ import app,db
from info import create_app,db
from info.models import User

app=create_app("development")


# 使用终端脚本工具启动启动和管理flask项目
manager = Manager(app)

# 初始化数据迁移模块
Migrate(app, db)

# 给终端脚本工具新增增加数据迁移的相关命令
manager.add_command("db", MigrateCommand)


"""创建管理员用户"""
@manager.option('-n', '-name', dest='name')
@manager.option('-p', '-password', dest='password')
def createsuperuser(name, password):
    """创建管理员用户"""
    if not all([name, password]):
        print('参数不足')
        return

    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
        print("创建成功")
    except Exception as e:
        print(e)
        db.session.rollback()


"""批量生成测试用户"""
def add_test_users():
    """批量生成测试用户"""
    users = []
    now = datetime.datetime.now()
    for num in range(10010, 80000):
        try:
            user = User()
            user.nick_name = "%011d" % num
            user.mobile = "%011d" % num
            user.password_hash = "pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829"
            user.create_time = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            users.append(user)
            print(user.mobile)
        except Exception as e:
            print(e)
    with app.app_context():
        # add_all 批量添加用户，参数就是一个列表
        db.session.add_all(users)
        db.session.commit()
    print('OK')



# 运行项目
if __name__ == '__main__':

    # add_test_users() 批量生成测试用户函数
    # app.run()
    manager.run()

