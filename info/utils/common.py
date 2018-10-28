# 自定义过滤器
# 过滤器的本质为函数
import functools

from flask import session, current_app, g

from info.models import User,News

def func_index_convert(index):
    index_dict = {1: "first", 2: "second", 3: "third"}

    return index_dict.get(index, "")


# 获取用户登录信息
def user_login_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return func(*args, **kwargs)
    return wrapper

#
# def user_login_data():
#     user_id = session.get('user_id')
#     if user_id:
#         try:
#             user = User.query.get(user_id)
#         except Exception as e:
#             current_app.logger.error(e)
#
#     # 第一种方式
#     # return user
#     # 第二种方式
#     g.user = user

def query_top_news(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 查询排名前10的新闻
        news_list = []  # type:News
        try:
            news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
        except Exception as e:
            current_app.logger.error(e)
        g.news_list = [News.to_dict() for News in news_list]
        return func(*args, **kwargs)
    return wrapper