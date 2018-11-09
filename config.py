import logging
from redis import StrictRedis
import base64, os


class Config(object):
    # debug模式
    DEBUG = False
    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # LOG_LEVEL=logging.ERROR
    # LOG_LEVEL = logging.DEBUG

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_SESSION_DB = 1
    REDIS_DATA_DB = 0

    SECRET_KEY = base64.b64encode(os.urandom(48))  # 设置密钥
    # SECRET_KEY = "idsfhu8732g*&F^(%$#"
    
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_SESSION_DB)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒


class DevelopementConfig(Config):
    """开发模式下的配置"""
    # LOG_LEVEL = logging.DEBUG
    LOG_LEVEL = logging.INFO
    DEBUG = True


class ProductionConfig(Config):
    """生产模式下的配置"""
    pass

# 定义配置字典
config = {
    "development": DevelopementConfig,
    "production": ProductionConfig
}

