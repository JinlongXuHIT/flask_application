from flask import Blueprint

passport_bp = Blueprint('passport', __name__, url_prefix='/passport')

# 将视图函数封装到单独文件中,故init文件需关联视图函数
from .views  import *
