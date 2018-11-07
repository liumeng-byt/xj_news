from flask import Flask

app = Flask(__name__)


class Config(object):
    DEBUG = True


app.config.from_object(Config)


@app.route("/index")
def index():
    return "ind"


if __name__ == '__main__':
    app.run()

