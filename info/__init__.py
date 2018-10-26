# 创建web应用
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_migrate import Migrate

from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

from config import config_dict

#
db = None # type: SQLAlchemy
strict_redis = None  # type : StrictRedis


def setup_log():
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_application(config_type):
    config_class = config_dict.get(config_type)
    # 创建app对象
    app = Flask(__name__)

    # 从类对象a加载配置信息
    app.config.from_object(config_class)
    global db, strict_redis
    # 创建数据库连接对象
    db = SQLAlchemy(app)

    # 创建redis连接对象
    strict_redis = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT,decode_responses=True)

    # session对象
    Session(app)

    # 初始化migrate
    Migrate(app, db)

    # register blueprint
    from info.modules.home import home_bp

    app.register_blueprint(home_bp)
    # 注册passport对应蓝图
    from info.modules.passport import passport_bp
    app.register_blueprint(passport_bp)

    # 配置日志
    setup_log()

    # 导入创建表结构
    import info.models
    return app
