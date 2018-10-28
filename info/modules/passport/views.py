import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, Response, jsonify, session

from info import strict_redis, db
from info.lib.captcha.pic_captcha import captcha
from info.lib.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_bp
from info.utils.response_code import RET, error_map


@passport_bp.route('/get_img_code', methods=['GET', 'POST'])
def get_img_code():
    # 获取request中的参数: 图片id
    img_code_id = request.args.get('img_code_id')
    # 校验参数
    if not img_code_id:
        return abort(403)

    #  调用第三方接口生成验证码,保存id 和 验证文字
    img_name, img_text, img_bytes = captcha.generate_captcha()
    try:
        # strict_redis.setex( name, time, value)
        strict_redis.set('img_code_id' + img_code_id, img_text, ex=300)
        print(img_text)
    except Exception as e:
        current_app.logger.error(e)
        return abort(500)
    # return  img_bytes
    # 调用第三方接口生成他\验证图片,response 图片
    response = make_response(img_bytes)  # type: Response
    response.content_type = 'image/jpeg'
    return response


@passport_bp.route('/get_sms_code', methods=['GET', 'POST'])
def get_sms_code():
    # 获取参数: 图片id 输入的验证图片文本 手机号
    img_code_id = request.json.get('img_code_id')
    img_code = request.json.get('img_code')
    mobile = request.json.get('mobile')
    print(mobile, img_code, img_code_id)
    # 校验是否有参数
    if not all([img_code_id, img_code, mobile]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 校验手机格式 ,不要相信别人的任何数据
    if not re.match(r'1[35678]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 校验手机是否注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg=error_map[RET.DATAEXIST])

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # 根据id读取数据库文本,校验图片是否正确.
    try:
        real_img_code = strict_redis.get('img_code_id' + img_code_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if real_img_code != img_code.upper():
        print(real_img_code)
        print(img_code.upper())
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 正确后 调用第三方内容发送短信
    rand_num = '%04d' % random.randint(0, 9999)
    # 生成验证码,
    current_app.logger.info('短信验证码为:%s' % rand_num)

    # # 发送短信,用于测试使用,验证完毕后暂时关闭
    # response_code = CCP().send_template_sms(mobile, [rand_num, 5], 1)
    # print(response_code)
    # if response_code != 0:
    #     return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 保存短信验证码
    try:
        strict_redis.set('sms_code_id:' + mobile, rand_num, ex=60)
        print(rand_num)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errormsg=error_map[RET.DBERR])
    # return json
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 用户注册
@passport_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
     接口文档:
        /passport/register
        用户注册
        url

        格式:
        Json
        请求方法
        post
        请求参数:
        mobile
        sms_code
        password

    """

    """
        业务逻辑:
        1.获取参数
        2验证参数
        3校验数据库信息
        4保存用户信息
        5返回响应
    """
    # 获取参数
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    sms_code = request.json.get('sms_code')
    # 校验参数
    # 1.校验是否有值
    if not all([mobile, password, sms_code]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 2.校验短信验证码
    try:
        real_sms_code = strict_redis.get('sms_code_id:' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        # 获取本地验证码
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 校验数据库信息
    # 校验验证码

    if sms_code != real_sms_code:
        # 例如验证码错误, 短信验证码过期
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 保存用户信息
    try:
        user = User()
        user.mobile = mobile
        user.nick_name = mobile  # 默认昵称为mobile
        # 密码加密,用目前没有前端加密,故用后端代替

        # user.password_hash = password
        # 方法很多,使用property
        user.password = password

        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 状态保持
    session['user_id'] = user.id
    # response 5返回响应
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 用户登陆
@passport_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    接口文档:
     /passport/login
        用户登陆
        请求格式:
        Json
        请求方法
        post
        请求参数:
        mobile  手机号
        password 密码
        响应格式:
        json

    :return: response
    """
    """
    逻辑:
    1获取参数
    2校验参数
    3查询用户信息
    4验证密码
    5记录最后登陆时间
    6返回json
    """
    # 1获取参数

    mobile = request.json.get('mobile')
    password = request.json.get('password')
    # 2校验参数
    # 2.1校验参数是否有值
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 2.2校验手机格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    #
    user = None  # type:User
    # 3查询用户信息
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not user:  # 没有该用户
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 4验证密码

    if not user.check_password(password):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 5记录最后登陆时间
    user.last_login = datetime.now()
    # 状态保存
    session['user_id'] = user.id

    # 6返回json
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

@passport_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    #前端根据点击事件发送请求,访问/passport/logout
    # 删除session
    :return:
    """
    session.pop("user_id",None)
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

