from datetime import timedelta

from redis import StrictRedis


class Config:
    # 定义与配置同名的类属性
    # 设置调试模式
    DEBUG = True
    # sql 配置
    # 1>数据库连接地址
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/flask_app_demo'
    # 2>设置sql数据库地址变化属性
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 3>设置sql数据库自动提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 每次请求结束后, 自动提交

    # redis 配置

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session config
    SESSION_TYPE = 'redis'
    # 设置session_redis连接对象,默认本地,
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # session加密
    SESSION_USE_SIGNER = True

    SECRET_KEY = "test"  # 生成机制 base64.b64encode(os.urandom(48))
    # 设置session过期时间
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductConfig(Config):
    DEBUG = False
    # 重写类属性
    # 还有SQLALCHEMY_DATABASE_URI中的数据库
    # REDIS_HOST and REDIS_PORT


# 定义字典记录配置的对应关系
config_dict = {'develop': DevelopmentConfig, 'product': ProductConfig}
