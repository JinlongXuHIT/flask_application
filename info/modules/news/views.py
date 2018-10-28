from flask import request, current_app, abort, render_template, session, g

from info import db
from info.models import News, User
from info.modules.news import news_bp
from info.utils.common import user_login_data


@news_bp.route('/<news_id>', methods=['GET', 'POST'])
# todo 装饰
@query_top_news
# @user_login_data   # 用户登陆状态查询

def demo1(news_id):
    """
    /news/动态url
    #seo 后端渲染
    # 参数
    id new_id
    # request 方式
    get
    #
    :return:
    """
    # 根据动态url获取新闻id,查询该新闻
    # 同时实现点击量加1
    try:
        news = News.query.get(news_id)
        news.clicks += 1
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        abort(500)
    # 排行渲染
    # # 查询排名前10的新闻
    # news_list = []  # type:News
    # try:
    #     news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    # except Exception as e:
    #     current_app.logger.error(e)
    # news_list = [News.to_dict() for News in news_list]

    # # 用户登录状态显示
    # user = user_login_data()
    # # .1将模型转化为字典
    # # user = user.to_dict() if user else None
    # # .1.2 方式
    # user = g.user.to_dict() if g.user else None
    # 装饰器方法
    # 将模型转化为字典
    user = g.user.to_dict() if g.user else None
    # 将数据传入模板渲染
    return render_template('detail.html', news=news.to_dict(), news_list=g.news_list, user=user)
