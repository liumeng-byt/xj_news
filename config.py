from redis import StrictRedis
import base64, os


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
    # print(SECRECT_KEY)
    # flask_session 的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_SESSION_DB)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒
