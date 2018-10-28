from flask import Blueprint

news_bp = Blueprint('news', __name__, url_prefix='/news')

# 将视图函数封装到单独文件中,故init文件需关联视图函数
from .views  import *
