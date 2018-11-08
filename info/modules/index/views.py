from . import index_blu

# 定义视图函数
@index_blu.route("/")
def index():
    # logging.fatal("致命错误")
    # logging.error("普通错误！")
    # logging.warning("警告错误！")
    # logging.info("普通日志信息！")
    # logging.debug("调试信息")

    return "hello news!"