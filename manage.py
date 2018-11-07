from flask import Flask

# flask 实例对象的初始化
app = Flask(__name__)


class Config(object):
    DEBUG = True


app.config.from_object(Config)


# 定义视图函数
@app.route("/index")
def index():
    return "ind"


# 运行项目
if __name__ == '__main__':
    app.run()
