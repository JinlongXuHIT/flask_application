from flask import session, render_template, request, jsonify
from flask import current_app

from info.constants import HOME_PAGE_MAX_NEWS
from info.models import User, News, Category
from info.modules.home import home_bp
import logging

from info.utils.response_code import RET, error_map


@home_bp.route('/demo1', methods=['GET', 'POST'])
def demo1():
    from info import strict_redis
    strict_redis.set('name', 'zs')
    logging.error('raise a error')
    current_app.logger.error('raise a error')

    return 'demo1'


@home_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    获取session值,判断是否登录

    查询用户信息
    数据库查询排名前10数据
    # add 查询新闻分类数据,渲染
    后端渲染
    :return:
    """
    user_id = session.get('user_id')
    user = None  # type:    User
    if user_id:
        # 数据库查询用户信息
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)
    # 查询排名前10的新闻
    news_list=[] #type:News
    try:
        news_list=News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
    news_list = [News.to_dict() for News in news_list]
    # 将模型转为字典
    user = user.to_dict() if user else None

    # 查询所有的新闻分类,将数据传入模板渲染
    categories = []
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    # TODO 将用户信息传入模板渲染
    return render_template('index.html', user=user,news_list= news_list,categories=categories)


@home_bp.route('/favicon.ico', methods=['GET', 'POST'])
def favicon():
    return current_app.send_static_file('./news/favicon.ico')

@home_bp.route('/get_news_list', methods=['GET', 'POST'])
def get_news_list():
    """
    #接口文档
    /get_news_list
    获取新闻列表
    request:
    get
    请求参数
    cid 分类id
    cur_page 当前页码
    per_count 每页条数
    响应格式
    json
    :return:
    """
    #获取参数
    cid = request.args.get('cid')
    cur_page = request.args.get('cur_page')
    #
    per_count = request.args.get('per_count', HOME_PAGE_MAX_NEWS)
    #校验参数
    if not all([cid,cur_page]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    #格式转换
    try:
        cid=int(cid)
        cur_page=int(cur_page)
        per_count=int(per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 根据参数查询新闻
    filter_list=[]
    if cid !=1:
        filter_list.append(News.category_id == cid)
    try:
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page,per_count)
        news_list = [news.to_dict() for news in pn.items]

        total_page = pn.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    data ={
        "news_list" :news_list,
        "total_page":total_page
    }
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK],data=data)

