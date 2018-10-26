from flask import Blueprint

home_bp = Blueprint('home', __name__)


# 4.关联视图函数
from .views import *
